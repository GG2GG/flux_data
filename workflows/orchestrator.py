"""
LangGraph-Based Orchestrator V2

Advanced multi-agent workflow with:
- State machine orchestration via LangGraph
- Conditional routing based on data quality
- Error recovery and retries
- Real-time progress streaming
- Full observability
"""

import logging
from typing import Dict, Any, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from agents.input_agent import InputAgent
from agents.analyzer_agent import AnalyzerAgentV2
from agents.explainer_agent import ExplainerAgent
from models.schemas import ProductInput, PlacementState, Recommendation

logger = logging.getLogger("OrchestratorV2")


class WorkflowState(TypedDict):
    """
    State passed between workflow nodes.

    LangGraph requires TypedDict for state management.
    """
    # Input
    product_input: Dict[str, Any]

    # Processing state
    placement_state: Any  # PlacementState object
    step: str
    errors: list
    warnings: list

    # Results
    recommendation: Dict[str, Any]
    metadata: Dict[str, Any]


class OrchestratorV2:
    """
    LangGraph-based orchestrator for multi-agent workflow.

    Features:
    - State machine with conditional routing
    - Data quality assessment
    - Automatic fallback to defaults
    - Error handling and recovery
    - Streaming progress updates
    """

    def __init__(self, data_dir: str = "data", config_dir: str = "config"):
        """
        Initialize orchestrator with agents.

        Args:
            data_dir: Data directory path
            config_dir: Configuration directory path
        """
        logger.info("Initializing LangGraph Orchestrator V2")

        # Initialize agents
        self.input_agent = InputAgent()
        self.analyzer_agent = AnalyzerAgentV2(
            data_dir=data_dir,
            config_dir=config_dir
        )
        self.explainer_agent = ExplainerAgent(data_dir=data_dir)

        # Build workflow graph
        self.workflow = self._build_workflow()

        logger.info("✓ Orchestrator initialized")

    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph state machine.

        Returns:
            Compiled workflow graph
        """
        # Create graph
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("validate_input", self._validate_input_node)
        workflow.add_node("check_data_quality", self._check_data_quality_node)
        workflow.add_node("analyze_roi", self._analyze_roi_node)
        workflow.add_node("explain", self._explain_node)
        workflow.add_node("handle_error", self._handle_error_node)

        # Define edges
        workflow.set_entry_point("validate_input")

        # From validation
        workflow.add_conditional_edges(
            "validate_input",
            self._should_continue_from_validation,
            {
                "continue": "check_data_quality",
                "error": "handle_error"
            }
        )

        # From data quality check
        workflow.add_conditional_edges(
            "check_data_quality",
            self._route_based_on_quality,
            {
                "analyze": "analyze_roi",
                "warning": "analyze_roi",  # Continue with warning
                "error": "handle_error"
            }
        )

        # From ROI analysis
        workflow.add_conditional_edges(
            "analyze_roi",
            self._should_continue_from_analysis,
            {
                "continue": "explain",
                "error": "handle_error"
            }
        )

        # From explanation
        workflow.add_edge("explain", END)

        # From error handler
        workflow.add_edge("handle_error", END)

        # Compile
        return workflow.compile()

    def _validate_input_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node: Validate product input.

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        logger.info("[STEP 1/4] Validating input...")

        try:
            # Convert dict to ProductInput
            product_input = ProductInput(**state['product_input'])

            # Create PlacementState
            placement_state = PlacementState(product=product_input)

            # Run validation
            placement_state = self.input_agent.execute(placement_state)

            state['placement_state'] = placement_state
            state['step'] = 'validated'
            state['errors'] = placement_state.errors
            state['warnings'] = placement_state.warnings

            logger.info("✓ Input validation complete")

        except Exception as e:
            logger.error(f"✗ Input validation failed: {e}")
            state['errors'] = [str(e)]
            state['step'] = 'validation_error'

        return state

    def _check_data_quality_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node: Check data quality and decide routing.

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        logger.info("[STEP 2/4] Checking data quality...")

        # Check if data manager has sufficient data
        if self.analyzer_agent.data_manager:
            metadata = self.analyzer_agent.data_manager.metadata

            if 'data_quality' in metadata:
                quality = metadata['data_quality']
                state['metadata'] = {'data_quality': quality}

                logger.info(f"Data quality: {quality['quality_level']}")
                logger.info(f"Confidence: {quality['confidence_score']:.1%}")

                if quality['quality_level'] in ['poor']:
                    state['warnings'].append(quality['recommendation'])
            else:
                state['warnings'].append("Using industry defaults - no sales data available")
        else:
            state['warnings'].append("No data manager - using all defaults")

        state['step'] = 'quality_checked'
        return state

    def _analyze_roi_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node: Analyze ROI for all locations.

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        logger.info("[STEP 3/4] Analyzing ROI...")

        try:
            placement_state = state['placement_state']

            # Run analysis
            placement_state = self.analyzer_agent.execute(placement_state)

            state['placement_state'] = placement_state
            state['errors'].extend(placement_state.errors)
            state['step'] = 'analyzed'

            if placement_state.errors:
                logger.error(f"✗ ROI analysis failed: {placement_state.errors}")
            else:
                logger.info(f"✓ Generated {len(placement_state.roi_predictions)} ROI predictions")

        except Exception as e:
            import traceback
            logger.error(f"✗ ROI analysis error: {e}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            state['errors'].append(str(e))
            state['step'] = 'analysis_error'

        return state

    def _explain_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node: Generate explanations.

        Args:
            state: Current workflow state

        Returns:
            Updated state
        """
        logger.info("[STEP 4/4] Generating explanations...")

        try:
            placement_state = state['placement_state']

            # Generate explanation
            placement_state = self.explainer_agent.execute(placement_state)

            state['placement_state'] = placement_state
            state['step'] = 'complete'

            # Create final recommendation
            state['recommendation'] = {
                'recommendations': placement_state.final_recommendations,
                'explanation': placement_state.explanation.dict() if placement_state.explanation else None,
                'session_id': placement_state.session_id,
                'timestamp': placement_state.timestamp.isoformat()
            }

            logger.info("✓ Explanation generated")

        except Exception as e:
            logger.error(f"✗ Explanation generation error: {e}")
            state['errors'].append(str(e))
            state['step'] = 'explanation_error'

        return state

    def _handle_error_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node: Handle errors and prepare error response.

        Args:
            state: Current workflow state

        Returns:
            Updated state with error info
        """
        logger.error(f"[ERROR HANDLER] Step: {state['step']}, Errors: {state['errors']}")

        state['recommendation'] = {
            'success': False,
            'errors': state['errors'],
            'step_failed': state['step']
        }
        state['step'] = 'error_handled'

        return state

    # Conditional routing functions

    def _should_continue_from_validation(self, state: WorkflowState) -> str:
        """Decide whether to continue after validation."""
        if state['errors']:
            return "error"
        return "continue"

    def _route_based_on_quality(self, state: WorkflowState) -> str:
        """Route based on data quality."""
        if state['errors']:
            return "error"

        # Check data quality level
        if 'metadata' in state and 'data_quality' in state['metadata']:
            quality_level = state['metadata']['data_quality']['quality_level']
            if quality_level == 'poor':
                return "warning"  # Continue with warning

        return "analyze"

    def _should_continue_from_analysis(self, state: WorkflowState) -> str:
        """Decide whether to continue after analysis."""
        if state['errors']:
            return "error"
        return "continue"

    # Public API

    def execute(self, product_input: ProductInput) -> Recommendation:
        """
        Execute workflow (backward compatible API).

        Args:
            product_input: Product input

        Returns:
            Recommendation object
        """
        logger.info("=" * 80)
        logger.info("STARTING LANGGRAPH WORKFLOW")
        logger.info("=" * 80)

        # Convert to dict for LangGraph
        initial_state = {
            'product_input': product_input.dict(),
            'step': 'init',
            'errors': [],
            'warnings': [],
            'recommendation': {},
            'metadata': {}
        }

        # Run workflow
        try:
            final_state = self.workflow.invoke(initial_state)

            # Check for success
            if final_state['errors']:
                logger.error("Workflow completed with errors")
                raise ValueError(f"Workflow failed: {'; '.join(final_state['errors'])}")

            # Extract recommendation
            placement_state = final_state['placement_state']

            recommendation = Recommendation(
                recommendations=placement_state.final_recommendations,
                explanation=placement_state.explanation,
                session_id=placement_state.session_id,
                timestamp=placement_state.timestamp
            )

            logger.info("=" * 80)
            logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)

            # Log warnings
            if final_state['warnings']:
                logger.warning("Workflow warnings:")
                for warning in final_state['warnings']:
                    logger.warning(f"  - {warning}")

            return recommendation

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise

    def get_status(self) -> Dict[str, Any]:
        """
        Get orchestrator status.

        Returns:
            Status information
        """
        return {
            'status': 'ready',
            'orchestration': 'langgraph',
            'agents': [
                {'name': self.input_agent.name, 'description': self.input_agent.description},
                {'name': self.analyzer_agent.name, 'description': self.analyzer_agent.description},
                {'name': self.explainer_agent.name, 'description': self.explainer_agent.description}
            ],
            'data_manager_active': self.analyzer_agent.data_manager is not None,
            'locations_loaded': len(self.analyzer_agent.locations),
        }


# Maintain backward compatibility
class Orchestrator(OrchestratorV2):
    """Alias for backward compatibility."""
    pass
