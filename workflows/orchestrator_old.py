"""
Orchestrator - Coordinates the multi-agent workflow.
"""

import logging
from typing import Dict, Any
from agents.input_agent import InputAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.explainer_agent import ExplainerAgent
from models.schemas import ProductInput, PlacementState, Recommendation

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

        try:
            # Step 1: Input validation
            logger.info("\n[STEP 1/3] Running InputAgent...")
            state = self.input_agent.execute(state)

            if state.errors:
                raise ValueError(f"Input validation failed: {'; '.join(state.errors)}")

            # Step 2: ROI analysis
            logger.info("\n[STEP 2/3] Running AnalyzerAgent...")
            state = self.analyzer_agent.execute(state)

            if state.errors:
                error_msg = f"ROI analysis failed: {'; '.join(state.errors)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            if not state.final_recommendations:
                raise ValueError("No recommendations generated")

            # Step 3: Generate explanations
            logger.info("\n[STEP 3/3] Running ExplainerAgent...")
            state = self.explainer_agent.execute(state)

            # Create final recommendation
            recommendation = Recommendation(
                recommendations=state.final_recommendations,
                explanation=state.explanation,
                session_id=state.session_id,
                timestamp=state.timestamp
            )

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
