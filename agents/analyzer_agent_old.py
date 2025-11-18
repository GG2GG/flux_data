"""
Analyzer Agent - Loads precomputed ROI data and ranks locations.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List
from .base_agent import BaseAgent
from models.schemas import PlacementState, ShelfLocation, ROIPrediction


class AnalyzerAgent(BaseAgent):
    """
    Agent responsible for analyzing shelf locations and predicting ROI.

    In a full implementation, this would use XGBoost models. For the hackathon,
    it uses precomputed ROI scores based on research-backed formulas.

    Responsibilities:
    - Load shelf/location data
    - Calculate or load precomputed ROI scores
    - Apply budget constraints
    - Rank locations by predicted ROI
    - Generate confidence intervals
    """

    def __init__(self, data_dir: str = "data"):
        super().__init__(
            name="AnalyzerAgent",
            description="Analyzes locations and predicts ROI scores"
        )
        self.data_dir = Path(data_dir)
        self.locations: List[ShelfLocation] = []
        self.retail_kb: Dict = {}
        self.roi_cache: Dict = {}

        # Load data
        self._load_locations()
        self._load_retail_kb()

    def _load_locations(self):
        """Load shelf locations from CSV."""
        shelves_file = self.data_dir / "shelves.csv"

        if not shelves_file.exists():
            self.logger.warning(f"Shelves file not found: {shelves_file}")
            return

        try:
            with open(shelves_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    location = ShelfLocation(
                        shelf_id=row['shelf_id'],
                        name=row['name'],
                        zone=row['zone'],
                        traffic_index=float(row['traffic_index']),
                        visibility_factor=float(row['visibility_factor']),
                        x=float(row.get('x', 0)),
                        y=float(row.get('y', 0)),
                        width=float(row.get('width', 0)),
                        height=float(row.get('height', 0)),
                        notes=row.get('notes', '')
                    )
                    self.locations.append(location)

            self.log_info(f"Loaded {len(self.locations)} shelf locations")

        except Exception as e:
            self.logger.error(f"Error loading shelves: {e}")

    def _load_retail_kb(self):
        """Load retail knowledge base (category benchmarks)."""
        kb_file = self.data_dir / "retail_kb.csv"

        if not kb_file.exists():
            self.logger.warning(f"Retail KB file not found: {kb_file}")
            return

        try:
            with open(kb_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    category = row['category'].lower()
                    self.retail_kb[category] = {
                        'avg_conversion_rate': float(row['avg_conversion_rate']),
                        'avg_basket_value': float(row['avg_basket_value']),
                        'lift_eye_level_pct': float(row['lift_eye_level_pct']),
                        'lift_endcap_pct': float(row['lift_endcap_pct']),
                        'lift_checkout_pct': float(row['lift_checkout_pct']),
                        'baseline_daily_footfall': float(row['baseline_daily_footfall']),
                        'notes': row.get('notes', '')
                    }

            self.log_info(f"Loaded knowledge base for {len(self.retail_kb)} categories")

        except Exception as e:
            self.logger.error(f"Error loading retail KB: {e}")

    def execute(self, state: PlacementState) -> PlacementState:
        """
        Analyze locations and generate ROI predictions.

        Args:
            state: PlacementState with validated product

        Returns:
            PlacementState with ROI predictions and ranked locations
        """
        if not self.validate_state(state, ['product']):
            return state

        product = state.product
        self.log_info(f"Analyzing placement options for {product.product_name}")

        # Store locations in state
        state.locations = self.locations

        # Calculate ROI for each location
        roi_predictions: Dict[str, ROIPrediction] = {}

        for location in self.locations:
            # Calculate ROI
            roi_score = self._calculate_roi(product, location)

            # Estimate placement cost
            placement_cost = self._estimate_placement_cost(location)

            # Check budget constraint
            if placement_cost > product.budget:
                self.log_info(f"Skipping {location.name}: cost ${placement_cost:.2f} exceeds budget ${product.budget:.2f}")
                continue

            # Generate confidence interval (80% CI)
            # Simulate model uncertainty with ±15% variation
            lower_bound = roi_score * 0.85
            upper_bound = roi_score * 1.15

            roi_predictions[location.name] = ROIPrediction(
                location=location.name,
                roi=round(roi_score, 2),
                confidence_interval=(round(lower_bound, 2), round(upper_bound, 2)),
                placement_cost=round(placement_cost, 2),
                confidence_level=0.80
            )

        if not roi_predictions:
            self.log_error("No locations found within budget", state)
            state.errors.append("No shelf locations are affordable within the given budget")
            return state

        # Rank by ROI (descending)
        sorted_predictions = dict(
            sorted(roi_predictions.items(), key=lambda x: x[1].roi, reverse=True)
        )

        state.roi_predictions = sorted_predictions

        # Create simple recommendations (top 5)
        state.final_recommendations = {
            loc: pred.roi
            for loc, pred in list(sorted_predictions.items())[:5]
        }

        self.log_info(f"Generated ROI predictions for {len(roi_predictions)} locations")
        self.log_info(f"Top recommendation: {list(sorted_predictions.keys())[0]} (ROI: {list(sorted_predictions.values())[0].roi})")

        return state

    def _calculate_roi(self, product, location: ShelfLocation) -> float:
        """
        Calculate ROI using research-backed formula.

        Formula incorporates:
        - Location visibility factor (research: end-caps +200%, checkout +40%)
        - Traffic index
        - Category fit
        - Seasonality (simplified for demo)
        - Price tier considerations
        """
        base_roi = 1.0

        # Location visibility multiplier (research-backed)
        visibility_multiplier = location.visibility_factor

        # Traffic boost (normalized)
        traffic_boost = (location.traffic_index / 200) * 0.15  # Normalize to ~0.15 boost

        # Category fit (check if category benchmarks exist)
        category_lower = product.category.lower()
        category_multiplier = 1.0

        if category_lower in self.retail_kb:
            kb = self.retail_kb[category_lower]

            # Apply category-specific lift based on zone type
            if location.zone == 'endcap':
                category_multiplier = kb['lift_endcap_pct']
            elif location.zone == 'eye_level':
                category_multiplier = kb['lift_eye_level_pct']
            elif location.zone == 'checkout':
                category_multiplier = kb['lift_checkout_pct']

        # Price tier consideration
        price_tier_multiplier = 1.0
        if product.price > 5.0:  # Premium product
            if location.zone in ['endcap', 'eye_level']:
                price_tier_multiplier = 1.1  # Premium products do better in visible locations
        elif product.price < 2.0:  # Budget product
            if location.zone in ['low_shelf']:
                price_tier_multiplier = 1.05  # Budget products acceptable in lower shelves

        # Calculate final ROI
        roi = base_roi * visibility_multiplier * (1 + traffic_boost) * category_multiplier * price_tier_multiplier

        # Add small random variation to make it realistic (±5%)
        import random
        noise = random.gauss(0, 0.05)
        roi = roi + noise

        # Clamp to realistic range [0.5, 3.0]
        roi = max(0.5, min(3.0, roi))

        return roi

    def _estimate_placement_cost(self, location: ShelfLocation) -> float:
        """
        Estimate placement cost based on location type and visibility.

        Based on industry averages:
        - Endcap: $2000/month
        - Checkout: $1500/month
        - Eye level: $1000/month
        - Regular: $500/month

        Adjusted by traffic index.
        """
        base_costs = {
            'endcap': 2000,
            'checkout': 1500,
            'eye_level': 1000,
            'low_shelf': 500,
            'regular': 800
        }

        base_cost = base_costs.get(location.zone, 800)

        # Adjust by traffic (high traffic = more expensive)
        traffic_multiplier = location.traffic_index / 200  # Normalize

        # Assume 4-week placement period
        weeks = 4
        cost = base_cost * traffic_multiplier * weeks

        return max(500, cost)  # Minimum $500

    def get_location_by_name(self, location_name: str) -> ShelfLocation:
        """Helper method to get location by name."""
        for loc in self.locations:
            if loc.name == location_name:
                return loc
        return None
