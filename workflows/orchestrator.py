"""
Orchestrator - Coordinates the multi-agent workflow.
"""

import logging
from typing import Dict, Any
from agents.input_agent import InputAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.explainer_agent import ExplainerAgent
from models.schemas import ProductInput, PlacementState, Recommendation
from utils.artifact_logger import ArtifactLogger

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Orchestrator")


class Orchestrator:
    """
    Orchestrates the multi-agent workflow for product placement recommendations.

    This is a simplified sequential orchestrator. In the full implementation,
    this would use LangGraph for more sophisticated agent coordination.

    Workflow:
    1. InputAgent: Validate product input
    2. AnalyzerAgent: Calculate ROI and rank locations
    3. ExplainerAgent: Generate comprehensive explanations
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the orchestrator with all agents.

        Args:
            data_dir: Directory containing data files
        """
        logger.info("Initializing Orchestrator")

        # Initialize agents
        self.input_agent = InputAgent()
        self.analyzer_agent = AnalyzerAgent(data_dir=data_dir)
        self.explainer_agent = ExplainerAgent(data_dir=data_dir)

        logger.info("All agents initialized")

    def execute(self, product_input: ProductInput) -> Recommendation:
        """
        Execute the complete workflow.

        Args:
            product_input: Validated product input

        Returns:
            Recommendation with ROI predictions and explanations

        Raises:
            Exception: If any agent fails
        """
        logger.info("=" * 80)
        logger.info("Starting new placement recommendation workflow")
        logger.info("=" * 80)

        # Create initial state
        state = PlacementState(product=product_input)

        # Initialize artifact logger
        artifact_logger = ArtifactLogger(state.session_id)

        # Log product information
        artifact_logger.add_step(
            step_name="Workflow Started",
            description=f"Beginning analysis for product: {product_input.product_name}",
            details={
                "product": {
                    "name": product_input.product_name,
                    "category": product_input.category,
                    "price": f"${product_input.price:.2f}",
                    "budget": f"${product_input.budget:.2f}",
                    "target_sales": product_input.target_sales,
                    "target_customers": product_input.target_customers
                }
            }
        )

        try:
            # Step 1: Input validation
            logger.info("\n[STEP 1/3] Running InputAgent...")
            artifact_logger.add_step(
                step_name="Input Validation",
                description="Checking that all product details are valid and complete",
                status="success"
            )
            state = self.input_agent.execute(state)

            if state.errors:
                artifact_logger.add_error(
                    message=f"Input validation failed: {'; '.join(state.errors)}",
                    error_details={"errors": state.errors}
                )
                raise ValueError(f"Input validation failed: {'; '.join(state.errors)}")

            # Log any warnings from input validation
            if state.warnings:
                for warning in state.warnings:
                    artifact_logger.add_warning(warning)

            # Step 2: ROI analysis
            logger.info("\n[STEP 2/3] Running AnalyzerAgent...")
            artifact_logger.add_step(
                step_name="ROI Analysis",
                description="Analyzing all available store locations and predicting ROI for each one",
                status="success"
            )
            state = self.analyzer_agent.execute(state)

            if state.errors:
                error_msg = f"ROI analysis failed: {'; '.join(state.errors)}"
                logger.error(error_msg)
                artifact_logger.add_error(error_msg, {"errors": state.errors})
                raise ValueError(error_msg)

            if not state.final_recommendations:
                artifact_logger.add_error("No suitable locations found within budget")
                raise ValueError("No recommendations generated")

            # Log ROI analysis results
            artifact_logger.add_step(
                step_name="ROI Rankings Generated",
                description=f"Successfully analyzed {len(state.final_recommendations)} locations within budget",
                details={
                    "total_locations_analyzed": len(state.final_recommendations),
                    "top_3_locations": [
                        {"location": loc, "roi": roi}
                        for loc, roi in list(state.final_recommendations.items())[:3]
                    ]
                }
            )

            # Step 3: Generate explanations
            logger.info("\n[STEP 3/3] Running ExplainerAgent...")

            # Check if AI is enabled
            if self.explainer_agent.llm_client and self.explainer_agent.llm_client.enabled:
                artifact_logger.enable_ai("gemini-2.0-flash")
                artifact_logger.add_step(
                    step_name="AI Explanation Generation",
                    description="Using Google Gemini AI to create natural language explanations",
                    status="success"
                )
            else:
                artifact_logger.add_step(
                    step_name="Template Explanation Generation",
                    description="Generating explanations using templates (AI not available)",
                    status="warning"
                )

            state = self.explainer_agent.execute(state)

            # Create final recommendation
            recommendation = Recommendation(
                recommendations=state.final_recommendations,
                explanation=state.explanation,
                session_id=state.session_id,
                timestamp=state.timestamp
            )

            # Set final results in artifact logger
            top_location = list(state.final_recommendations.keys())[0] if state.final_recommendations else None
            artifact_logger.set_final_results(
                product_info={
                    "name": product_input.product_name,
                    "category": product_input.category,
                    "price": product_input.price,
                    "budget": product_input.budget
                },
                recommendations=state.final_recommendations,
                top_recommendation={
                    "location": top_location,
                    "roi": state.final_recommendations[top_location] if top_location else None
                },
                explanation=state.explanation.model_dump() if hasattr(state.explanation, 'model_dump') else None
            )

            # Save artifact log
            artifact_logger.save()

            logger.info("=" * 80)
            logger.info("Workflow completed successfully")
            logger.info(f"Session ID: {state.session_id}")
            logger.info(f"Top recommendation: {list(state.final_recommendations.keys())[0]} (ROI: {list(state.final_recommendations.values())[0]:.2f})")
            logger.info("=" * 80)

            # Log warnings if any
            if state.warnings:
                logger.warning(f"\nWarnings generated: {len(state.warnings)}")
                for warning in state.warnings:
                    logger.warning(f"  - {warning}")

            return recommendation

        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            artifact_logger.add_error(f"Workflow failed: {str(e)}")
            artifact_logger.save()
            raise

    def answer_followup(self, session_id: str, question: str, state: PlacementState = None) -> str:
        """
        Answer follow-up questions about a recommendation.

        Args:
            session_id: Session ID from original recommendation
            question: User's follow-up question
            state: Original PlacementState (in production, would retrieve from cache/DB)

        Returns:
            Answer to the question
        """
        if state is None:
            return "Session not found. Please run a new analysis."

        logger.info(f"Answering follow-up question for session {session_id}")
        logger.info(f"Question: {question}")

        answer = self.explainer_agent.answer_followup_question(state, question)

        return answer

    def get_status(self) -> Dict[str, Any]:
        """
        Get orchestrator status.

        Returns:
            Status information
        """
        return {
            'status': 'ready',
            'agents': [
                {'name': self.input_agent.name, 'description': self.input_agent.description},
                {'name': self.analyzer_agent.name, 'description': self.analyzer_agent.description},
                {'name': self.explainer_agent.name, 'description': self.explainer_agent.description}
            ],
            'locations_loaded': len(self.analyzer_agent.locations),
            'categories_in_kb': len(self.analyzer_agent.retail_kb)
        }
