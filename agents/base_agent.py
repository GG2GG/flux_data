"""
Base agent class that all specialized agents inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
from models.schemas import PlacementState

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

    def __init__(self, name: str, description: str):
        """
        Initialize the base agent.

        Args:
            name: Human-readable name of the agent
            description: Brief description of agent's purpose
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"Agent.{name}")

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
