"""
State Transition Logger - Logs agent state transitions as JSON files.

Provides comprehensive logging of:
- Agent inputs and outputs
- State transitions
- Data transformations
- Decision points
- Performance metrics
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class StateLogger:
    """
    Logs state transitions for debugging and analysis.

    Features:
    - JSON serialization of Pydantic models
    - Timestamped logs with session tracking
    - Automatic log rotation
    - Performance metrics
    """

    def __init__(self, log_dir: str = "logs/state_transitions"):
        """
        Initialize state logger.

        Args:
            log_dir: Directory to store state transition logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_log_dir: Optional[Path] = None
        logger.info(f"✓ State logger initialized: {self.log_dir}")

    def start_session(self, session_id: str):
        """
        Start a new logging session.

        Args:
            session_id: Unique session identifier
        """
        # Create session-specific directory
        self.session_log_dir = self.log_dir / session_id
        self.session_log_dir.mkdir(parents=True, exist_ok=True)

        # Log session metadata
        self.log_event(
            "session_start",
            {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "log_directory": str(self.session_log_dir)
            }
        )

        logger.info(f"✓ Started logging session: {session_id}")

    def log_agent_input(
        self,
        agent_name: str,
        state: Any,
        step_number: Optional[int] = None
    ):
        """
        Log agent input state.

        Args:
            agent_name: Name of the agent
            state: Input state (Pydantic model or dict)
            step_number: Optional step number in workflow
        """
        data = {
            "event": "agent_input",
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "step": step_number,
            "state": self._serialize(state)
        }

        filename = f"{self._get_step_prefix(step_number)}{agent_name.lower()}_input.json"
        self._write_log(filename, data)

    def log_agent_output(
        self,
        agent_name: str,
        state: Any,
        step_number: Optional[int] = None,
        metrics: Optional[Dict] = None
    ):
        """
        Log agent output state.

        Args:
            agent_name: Name of the agent
            state: Output state (Pydantic model or dict)
            step_number: Optional step number in workflow
            metrics: Optional performance metrics
        """
        data = {
            "event": "agent_output",
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "step": step_number,
            "state": self._serialize(state),
            "metrics": metrics or {}
        }

        filename = f"{self._get_step_prefix(step_number)}{agent_name.lower()}_output.json"
        self._write_log(filename, data)

    def log_state_transition(
        self,
        from_agent: str,
        to_agent: str,
        state: Any,
        decision: Optional[Dict] = None
    ):
        """
        Log state transition between agents.

        Args:
            from_agent: Source agent name
            to_agent: Destination agent name
            state: State being passed
            decision: Optional decision/routing information
        """
        data = {
            "event": "state_transition",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "timestamp": datetime.now().isoformat(),
            "state": self._serialize(state),
            "decision": decision or {}
        }

        filename = f"transition_{from_agent.lower()}_to_{to_agent.lower()}.json"
        self._write_log(filename, data)

    def log_decision_point(
        self,
        decision_name: str,
        condition: str,
        result: bool,
        context: Optional[Dict] = None
    ):
        """
        Log a decision/routing point in the workflow.

        Args:
            decision_name: Name of the decision point
            condition: Condition being evaluated
            result: Boolean result (True/False)
            context: Additional context about the decision
        """
        data = {
            "event": "decision_point",
            "decision": decision_name,
            "condition": condition,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }

        filename = f"decision_{decision_name.lower().replace(' ', '_')}.json"
        self._write_log(filename, data)

    def log_data_transformation(
        self,
        transformation: str,
        input_data: Any,
        output_data: Any,
        agent: Optional[str] = None
    ):
        """
        Log a data transformation.

        Args:
            transformation: Description of transformation
            input_data: Input data before transformation
            output_data: Output data after transformation
            agent: Optional agent performing transformation
        """
        data = {
            "event": "data_transformation",
            "transformation": transformation,
            "agent": agent,
            "timestamp": datetime.now().isoformat(),
            "input": self._serialize(input_data),
            "output": self._serialize(output_data)
        }

        filename = f"transform_{transformation.lower().replace(' ', '_')}.json"
        self._write_log(filename, data)

    def log_error(
        self,
        agent_name: str,
        error: Exception,
        state: Any,
        context: Optional[Dict] = None
    ):
        """
        Log an error that occurred during processing.

        Args:
            agent_name: Name of agent where error occurred
            error: Exception that was raised
            state: State at time of error
            context: Additional error context
        """
        data = {
            "event": "error",
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "state": self._serialize(state),
            "context": context or {}
        }

        filename = f"error_{agent_name.lower()}.json"
        self._write_log(filename, data)

    def log_event(self, event_name: str, data: Dict):
        """
        Log a generic event.

        Args:
            event_name: Name of the event
            data: Event data
        """
        log_data = {
            "event": event_name,
            "timestamp": datetime.now().isoformat(),
            **data
        }

        filename = f"event_{event_name.lower().replace(' ', '_')}.json"
        self._write_log(filename, data=log_data)

    def end_session(self, summary: Optional[Dict] = None):
        """
        End logging session and write summary.

        Args:
            summary: Optional session summary
        """
        data = {
            "event": "session_end",
            "timestamp": datetime.now().isoformat(),
            "summary": summary or {}
        }

        self.log_event("session_end", data)
        logger.info(f"✓ Ended logging session: {self.session_log_dir}")

    def _serialize(self, obj: Any) -> Any:
        """
        Serialize object to JSON-compatible format.

        Args:
            obj: Object to serialize (Pydantic model, dict, or primitive)

        Returns:
            JSON-serializable object
        """
        # Handle Pydantic models
        if isinstance(obj, BaseModel):
            return obj.model_dump()

        # Handle dicts (may contain Pydantic models)
        if isinstance(obj, dict):
            return {
                key: self._serialize(value)
                for key, value in obj.items()
            }

        # Handle lists
        if isinstance(obj, list):
            return [self._serialize(item) for item in obj]

        # Handle datetime
        if isinstance(obj, datetime):
            return obj.isoformat()

        # Handle other types that have __dict__
        if hasattr(obj, '__dict__'):
            try:
                return self._serialize(obj.__dict__)
            except:
                return str(obj)

        # Return as-is for primitives
        return obj

    def _get_step_prefix(self, step_number: Optional[int]) -> str:
        """
        Get filename prefix for step number.

        Args:
            step_number: Step number

        Returns:
            Prefix string (e.g., "step1_")
        """
        if step_number is not None:
            return f"step{step_number}_"
        return ""

    def _write_log(self, filename: str, data: Dict):
        """
        Write log data to file.

        Args:
            filename: Log filename
            data: Data to write
        """
        if not self.session_log_dir:
            logger.warning("No active session, skipping log write")
            return

        filepath = self.session_log_dir / filename

        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to write log {filename}: {e}")


# Global state logger instance
_global_logger: Optional[StateLogger] = None


def get_state_logger() -> StateLogger:
    """
    Get global state logger instance.

    Returns:
        StateLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = StateLogger()
    return _global_logger


def init_state_logger(log_dir: str = "logs/state_transitions") -> StateLogger:
    """
    Initialize global state logger.

    Args:
        log_dir: Log directory path

    Returns:
        StateLogger instance
    """
    global _global_logger
    _global_logger = StateLogger(log_dir=log_dir)
    return _global_logger
