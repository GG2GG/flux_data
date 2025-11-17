"""
Input Agent - Validates product input and initializes session state.
"""

from .base_agent import BaseAgent
from models.schemas import PlacementState, ProductInput
from uuid import uuid4
from datetime import datetime


class InputAgent(BaseAgent):
    """
    Agent responsible for validating user input and initializing the placement state.

    Responsibilities:
    - Validate product details (price > 0, budget > 0, etc.)
    - Perform business rule checks
    - Initialize PlacementState with metadata
    - Log request for auditing
    """

    def __init__(self):
        super().__init__(
            name="InputAgent",
            description="Validates user input and initializes session state"
        )

    def execute(self, state: PlacementState) -> PlacementState:
        """
        Validate product input and initialize state.

        Args:
            state: PlacementState with product information

        Returns:
            Validated and initialized PlacementState
        """
        self.log_info(f"Processing placement request for '{state.product.product_name}'")

        # Validate product input
        self._validate_product(state)

        # Perform business rule checks
        self._check_business_rules(state)

        # Ensure session ID and timestamp are set
        if not state.session_id:
            state.session_id = str(uuid4())

        if not state.timestamp:
            state.timestamp = datetime.now()

        self.log_info(f"Session initialized: {state.session_id}")

        return state

    def _validate_product(self, state: PlacementState):
        """Validate product details."""
        product = state.product

        # Price validation
        if product.price <= 0:
            self.log_error("Product price must be positive", state)
            raise ValueError("Product price must be positive")

        # Budget validation
        if product.budget <= 0:
            self.log_error("Placement budget must be positive", state)
            raise ValueError("Placement budget must be positive")

        # Target sales validation
        if product.target_sales <= 0:
            self.log_error("Target sales must be positive", state)
            raise ValueError("Target sales must be positive")

        # Expected ROI validation
        if product.expected_roi <= 0:
            self.log_error("Expected ROI must be positive", state)
            raise ValueError("Expected ROI must be positive")

        # Product name validation
        if not product.product_name or len(product.product_name.strip()) == 0:
            self.log_error("Product name cannot be empty", state)
            raise ValueError("Product name cannot be empty")

        # Category validation
        if not product.category or len(product.category.strip()) == 0:
            self.log_error("Product category cannot be empty", state)
            raise ValueError("Product category cannot be empty")

        self.log_info("Product validation passed")

    def _check_business_rules(self, state: PlacementState):
        """Check business rules and add warnings if needed."""
        product = state.product

        # Check if expected ROI is unrealistic
        if product.expected_roi > 3.0:
            warning = f"Expected ROI of {product.expected_roi:.2f} is very ambitious. " \
                     f"Most retail placements achieve ROI between 1.0-2.5."
            self.log_warning(warning, state)

        # Check if budget seems low for target sales
        expected_revenue = product.price * product.target_sales
        if product.budget > expected_revenue:
            warning = f"Placement budget (${product.budget:.2f}) exceeds expected revenue " \
                     f"(${expected_revenue:.2f}). This would result in negative ROI."
            self.log_warning(warning, state)

        # Check if price seems unusual
        if product.price < 0.50:
            self.log_warning("Product price seems unusually low (<$0.50)", state)
        elif product.price > 50.0:
            self.log_warning("Product price seems unusually high (>$50)", state)

        # Validate target customer description
        if len(product.target_customers.strip()) < 5:
            self.log_warning("Target customer description is very brief. More detail would improve recommendations.", state)

    def validate_input_data(self, product_input: ProductInput) -> tuple[bool, str]:
        """
        Public method to validate product input before creating state.

        Args:
            product_input: ProductInput to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Create temporary state for validation
            temp_state = PlacementState(product=product_input)
            self._validate_product(temp_state)
            self._check_business_rules(temp_state)

            if temp_state.errors:
                return False, "; ".join(temp_state.errors)

            return True, ""

        except Exception as e:
            return False, str(e)
