"""
Base agent class that all specialized agents inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import time
from models.schemas import PlacementState
from utils.state_logger import get_state_logger

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.

    Each agent is responsible for a specific part of the product placement
    recommendation pipeline. Agents receive a PlacementState object, process it,
    and return an updated state.
    """

    def __init__(self, name: str, description: str, enable_state_logging: bool = True):
        """
        Initialize the base agent.

        Args:
            name: Human-readable name of the agent
            description: Brief description of agent's purpose
            enable_state_logging: Enable state transition logging
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"Agent.{name}")
        self.enable_state_logging = enable_state_logging
        self.state_logger = get_state_logger() if enable_state_logging else None
        self.step_number: Optional[int] = None

    def execute_with_logging(self, state: PlacementState) -> PlacementState:
        """
        Execute agent with automatic state logging.

        Args:
            state: Current placement state

        Returns:
            Updated placement state
        """
        start_time = time.time()

        # Log input state
        if self.state_logger:
            self.state_logger.log_agent_input(
                agent_name=self.name,
                state=state,
                step_number=self.step_number
            )

        try:
            # Execute agent logic
            output_state = self.execute(state)

            # Calculate execution time
            execution_time = time.time() - start_time

            # Log output state
            if self.state_logger:
                self.state_logger.log_agent_output(
                    agent_name=self.name,
                    state=output_state,
                    step_number=self.step_number,
                    metrics={
                        "execution_time_seconds": round(execution_time, 3),
                        "errors_count": len(output_state.errors),
                        "warnings_count": len(output_state.warnings)
                    }
                )

            return output_state

        except Exception as e:
            # Log error
            if self.state_logger:
                self.state_logger.log_error(
                    agent_name=self.name,
                    error=e,
                    state=state
                )
            raise

    @abstractmethod
    def execute(self, state: PlacementState) -> PlacementState:
        """
        Execute the agent's main logic.

        This method must be implemented by all subclasses.

        Args:
            state: Current placement state

        Returns:
            Updated placement state

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError(f"{self.name} must implement execute() method")

    def log_info(self, message: str):
        """Log informational message."""
        self.logger.info(f"[{self.name}] {message}")

    def log_warning(self, message: str, state: PlacementState):
        """Log warning and add to state warnings."""
        self.logger.warning(f"[{self.name}] {message}")
        state.warnings.append(f"{self.name}: {message}")

    def log_error(self, message: str, state: PlacementState):
        """Log error and add to state errors."""
        self.logger.error(f"[{self.name}] {message}")
        state.errors.append(f"{self.name}: {message}")

    def validate_state(self, state: PlacementState, required_fields: list) -> bool:
        """
        Validate that required fields exist in state.

        Args:
            state: Placement state to validate
            required_fields: List of field names that must exist

        Returns:
            True if all required fields are present, False otherwise
        """
        for field in required_fields:
            if not hasattr(state, field) or getattr(state, field) is None:
                self.log_error(f"Required field '{field}' missing from state", state)
                return False
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
