"""
Location Filter Agent - Uses LLM to filter out illogical placements.

Prevents nonsensical recommendations like cosmetics in snack aisles or
beverages in personal care sections by using LLM reasoning about
product-location fit.
"""

import logging
from typing import List
from models.schemas import PlacementState, ShelfLocation
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class LocationFilterAgent(BaseAgent):
    """
    Agent that filters locations using LLM reasoning.

    Responsibilities:
    - Evaluate product-location logical fit
    - Filter out obviously wrong placements
    - Preserve locations that make sense
    - Explain filtering decisions
    """

    def __init__(self):
        super().__init__(
            name="LocationFilterAgent",
            description="Filters illogical product-location combinations using LLM reasoning"
        )

        # Initialize LLM client with qwen2.5-coder for fast classification
        self.llm_client = None
        try:
            from utils.llm_client import LLMClient
            import os
            from dotenv import load_dotenv

            load_dotenv()

            # Use lightweight qwen2.5-coder:3b for filtering (fast classification)
            # Falls back to environment config if qwen not available
            api_key = os.getenv('OPENAI_API_KEY')
            base_url = os.getenv('OPENAI_API_BASE')

            self.llm_client = LLMClient(
                api_key=api_key,
                base_url=base_url,
                model="qwen2.5-coder:3b",  # Lightweight model for classification
                temperature=0.3,  # Low temperature for consistent filtering
                max_tokens=200
            )

            if self.llm_client and self.llm_client.enabled:
                self.log_info(f"LLM-powered location filtering enabled (model: qwen2.5-coder:3b)")
            else:
                self.log_info("LLM not available, using rule-based filtering")
        except Exception as e:
            logger.warning(f"Could not initialize LLM client: {e}")
            self.llm_client = None

    def execute(self, state: PlacementState) -> PlacementState:
        """
        Filter locations that don't make sense for the product.

        Args:
            state: PlacementState with product and locations

        Returns:
            PlacementState with filtered locations
        """
        if not self.validate_state(state, ['product', 'locations']):
            return state

        self.log_info(f"Filtering {len(state.locations)} locations for {state.product.product_name}")

        # If LLM is available, use it for intelligent filtering
        if self.llm_client and self.llm_client.enabled:
            filtered_locations = self._filter_with_llm(state)
        else:
            # Fallback to rule-based filtering
            filtered_locations = self._filter_with_rules(state)

        # Log filtering results
        filtered_count = len(state.locations) - len(filtered_locations)
        if filtered_count > 0:
            filtered_names = [loc.name for loc in state.locations if loc not in filtered_locations]
            self.log_info(f"Filtered out {filtered_count} illogical locations: {', '.join(filtered_names)}")
            state.warnings.append(
                f"LocationFilterAgent: Removed {filtered_count} illogical placements"
            )

        # Update state with filtered locations
        state.locations = filtered_locations

        return state

    def _filter_with_llm(self, state: PlacementState) -> List[ShelfLocation]:
        """
        Use LLM to intelligently filter locations.

        Args:
            state: Current placement state

        Returns:
            List of valid locations
        """
        product = state.product
        locations = state.locations

        # Build location list for LLM
        location_list = []
        for loc in locations:
            location_list.append({
                'name': loc.name,
                'zone': loc.zone,
                'notes': loc.notes if hasattr(loc, 'notes') else ''
            })

        # Ask LLM to filter with STRICT rules
        system_prompt = """You are a STRICT retail placement expert. Your job is to REJECT any location that doesn't make perfect sense for the product.

GOLDEN RULE: Better to recommend 2 perfect locations than 5 with irrelevant ones. BE STRICT.

STRICT CATEGORY-LOCATION COMPATIBILITY:
✓ Beverages → ONLY: Beverage Aisles, Checkout (impulse), Main Entrance (impulse)
✓ Personal Care/Cosmetics → ONLY: Personal Care Aisles, Checkout (impulse), Main Entrance (impulse)
✓ Snacks → ONLY: Snack Aisles, Checkout (impulse), Main Entrance (impulse)
✓ Dairy → ONLY: Dairy Sections, Checkout (impulse), Main Entrance (impulse)
✓ Bakery → ONLY: Bakery Sections, Checkout (impulse), Main Entrance (impulse)

NEVER ALLOW - ZERO TOLERANCE:
✗ Beverages in: Personal Care, Bakery, Dairy, Snack-specific aisles
✗ Personal Care in: Beverage, Snack, Dairy, Bakery aisles
✗ Snacks in: Personal Care, Dairy, Bakery aisles (beverages OK for impulse)
✗ Dairy in: Personal Care, Beverage, Snack, Bakery aisles
✗ Cross-category placements UNLESS it's Checkout or Main Entrance

ENDCAP RULES:
- Only allow endcaps if they match the product category
- "End Cap 1 - Beverages" → ONLY for Beverages
- "End Cap 2 - Snacks" → ONLY for Snacks
- Generic endcaps → Allow for any category

When in doubt, REJECT. Quality over quantity.

Respond with ONLY a JSON array of location names that make sense. No explanation."""

        user_prompt = f"""Product: {product.product_name}
Category: {product.category}
Price: ${product.price}
Target Customers: {product.target_customers}

Available Locations:
{chr(10).join([f"- {loc['name']} ({loc['zone']}): {loc['notes']}" for loc in location_list])}

Return JSON array of location names that make logical sense for this product.
Example: ["Location 1", "Location 2", "Location 3"]"""

        try:
            response = self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Low temperature for consistent reasoning
                max_tokens=300,
                json_mode=False  # Don't use json_mode with local models
            )

            # Parse response - extract JSON array
            import json
            import re

            if not response or response.strip() == "":
                self.logger.warning("LLM returned empty response, using rule-based filtering")
                return self._filter_with_rules(state)

            # Try to extract JSON array from response
            # Match pattern like ["Location 1", "Location 2"]
            match = re.search(r'\[([^\]]+)\]', response, re.DOTALL)
            if match:
                try:
                    json_str = '[' + match.group(1) + ']'
                    valid_names = json.loads(json_str)
                    self.logger.info(f"LLM filtered to {len(valid_names)}/{len(locations)} locations")
                except json.JSONDecodeError as e:
                    self.logger.warning(f"JSON parse error: {e}, trying full match")
                    # Try parsing the whole response
                    try:
                        valid_names = json.loads(response.strip())
                    except:
                        self.logger.warning(f"Could not parse LLM response, using rule-based filtering")
                        return self._filter_with_rules(state)
            else:
                self.logger.warning(f"No JSON array found in response: {response[:200]}")
                return self._filter_with_rules(state)

            # Filter locations - use fuzzy matching since LLM might add zone info
            valid_locations = []
            for loc in locations:
                # Check exact match first
                if loc.name in valid_names:
                    valid_locations.append(loc)
                    continue

                # Check if LLM response contains location name (fuzzy match)
                # E.g., "Personal Care Aisle (Regular Shelf)" should match "Personal Care Aisle"
                for valid_name in valid_names:
                    if loc.name in valid_name or valid_name in loc.name:
                        valid_locations.append(loc)
                        break

            if len(valid_locations) == 0:
                self.logger.warning("LLM filtered out all locations, keeping all")
                return locations

            self.logger.info(f"Filtered {len(locations) - len(valid_locations)} locations")
            return valid_locations

        except Exception as e:
            self.logger.error(f"LLM filtering failed: {e}")
            # Fallback to rule-based if LLM fails
            return self._filter_with_rules(state)

    def _filter_with_rules(self, state: PlacementState) -> List[ShelfLocation]:
        """
        Rule-based fallback filtering.

        Args:
            state: Current placement state

        Returns:
            List of valid locations
        """
        product = state.product
        locations = state.locations

        # Category-based rules
        category_lower = product.category.lower()
        product_name_lower = product.product_name.lower()

        valid_locations = []

        for loc in locations:
            location_name_lower = loc.name.lower()
            should_allow = False

            # STRICT RULE: Only allow locations that make sense

            # Checkout and Main Entrance are universal (impulse buying)
            if 'checkout' in location_name_lower or 'main entrance' in location_name_lower:
                should_allow = True
            # End caps: Only if category-specific OR generic
            elif 'end cap' in location_name_lower:
                # Check if end cap is category-specific
                if category_lower in location_name_lower:
                    should_allow = True  # Category match
                elif not any(cat in location_name_lower for cat in ['beverage', 'snack', 'dairy', 'bakery', 'personal care']):
                    should_allow = True  # Generic end cap
                # Otherwise reject category-specific end caps for wrong category

            # Category-specific rules - STRICT matching only

            # Cosmetics / Personal Care - STRICT
            elif any(term in category_lower for term in ['cosmetic', 'personal care', 'beauty', 'hygiene']):
                if any(term in location_name_lower for term in ['personal care', 'cosmetic', 'beauty', 'hygiene']):
                    should_allow = True
                # Explicitly reject food/beverage aisles
                else:
                    should_allow = False

            # Beverages - STRICT
            elif any(term in category_lower for term in ['beverage', 'drink', 'juice', 'water', 'soda']):
                if any(term in location_name_lower for term in ['beverage', 'drink']):
                    should_allow = True
                # Explicitly reject all other categories
                else:
                    should_allow = False

            # Snacks - STRICT
            elif any(term in category_lower for term in ['snack', 'chip', 'candy', 'cookie']):
                if any(term in location_name_lower for term in ['snack', 'candy']):
                    should_allow = True
                # Explicitly reject all other categories
                else:
                    should_allow = False

            # Dairy - STRICT
            elif any(term in category_lower for term in ['dairy', 'milk', 'cheese', 'yogurt']):
                if any(term in location_name_lower for term in ['dairy', 'refrigerat']):
                    should_allow = True
                # Explicitly reject all other categories
                else:
                    should_allow = False

            # Bakery - STRICT
            elif any(term in category_lower for term in ['bakery', 'bread', 'pastry', 'cake']):
                if any(term in location_name_lower for term in ['bakery', 'bread']):
                    should_allow = True
                # Explicitly reject all other categories
                else:
                    should_allow = False

            # Default: REJECT (change from permissive to strict)
            # If we reach here, we don't have a rule for this category
            # Better to be safe and reject than allow irrelevant placements
            else:
                should_allow = False

            if should_allow:
                valid_locations.append(loc)

        # Ensure we have at least some locations
        if len(valid_locations) == 0:
            self.logger.warning("Rule-based filtering removed all locations, keeping all")
            return locations

        return valid_locations


# Export for use in orchestrator
__all__ = ['LocationFilterAgent']
