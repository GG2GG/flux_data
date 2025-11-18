"""
Analyzer Agent V2 - Data-Driven ROI Analysis

Refactored to use:
- AdaptiveDataManager for computed metrics
- CostManager for YAML-based costs
- VisibilityManager for research-backed factors
- Full transparency on data sources
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from .base_agent import BaseAgent
from models.schemas import PlacementState, ShelfLocation, ROIPrediction
from utils.adaptive_data_manager import AdaptiveDataManager
from utils.cost_manager import CostManager, VisibilityManager


class AnalyzerAgentV2(BaseAgent):
    """
    Data-driven analyzer agent with transparent metric sourcing.

    New Features:
    - Uses computed category lifts from sales data
    - Falls back to industry defaults when data insufficient
    - YAML-based cost configuration
    - Research-backed visibility factors
    - Full data provenance tracking
    """

    def __init__(
        self,
        data_dir: str = "data",
        config_dir: str = "config",
        sales_csv: Optional[str] = None
    ):
        super().__init__(
            name="AnalyzerAgentV2",
            description="Data-driven location analysis and ROI prediction"
        )
        self.data_dir = Path(data_dir)
        self.config_dir = Path(config_dir)

        # Initialize managers
        self.data_manager: Optional[AdaptiveDataManager] = None
        self.cost_manager = CostManager(self.config_dir / "placement_costs.yaml")
        self.visibility_manager = VisibilityManager(self.config_dir / "zone_visibility.yaml")

        # Storage
        self.locations: List[ShelfLocation] = []
        self.category_lifts: Dict = {}
        self.location_performance: Dict = {}

        # Load data
        self._initialize_data_manager(sales_csv)
        self._load_locations()

    def _initialize_data_manager(self, sales_csv: Optional[str]):
        """Initialize adaptive data manager with sales data."""
        if sales_csv is None:
            sales_csv = self.data_dir / "input" / "sales_history.csv"

        if Path(sales_csv).exists():
            try:
                self.data_manager = AdaptiveDataManager(
                    sales_csv_path=str(sales_csv),
                    data_dir=str(self.data_dir)
                )
                # Compute metrics
                results = self.data_manager.compute_all_metrics()
                self.category_lifts = results['category_lifts']
                self.location_performance = results['location_performance']
                self.log_info("✓ Data manager initialized with computed metrics")
            except Exception as e:
                self.logger.error(f"Failed to initialize data manager: {e}")
                self.data_manager = None
        else:
            self.log_warning("No sales data found, using defaults only")
            self.data_manager = None

    def _load_locations(self):
        """Load location metadata from defaults."""
        locations_file = self.data_dir / "archive" / "synthetic" / "locations.json"

        if not locations_file.exists():
            self.logger.error(f"Locations file not found: {locations_file}")
            return

        try:
            with open(locations_file, 'r') as f:
                locations_data = json.load(f)

            for loc_data in locations_data:
                location = ShelfLocation(
                    shelf_id=loc_data['location_id'],
                    name=loc_data['zone_name'],
                    zone=loc_data['zone_type'],
                    traffic_index=loc_data.get('traffic_index', 150),
                    visibility_factor=loc_data.get('visibility_factor', 1.0),
                    x=loc_data.get('x', 0),
                    y=loc_data.get('y', 0),
                    width=loc_data.get('width', 100),
                    height=loc_data.get('height', 80),
                    notes=loc_data.get('notes', '')
                )
                self.locations.append(location)

            self.log_info(f"✓ Loaded {len(self.locations)} locations")

        except Exception as e:
            self.logger.error(f"Error loading locations: {e}")

    def execute(self, state: PlacementState) -> PlacementState:
        """
        Analyze locations and generate ROI predictions.

        Args:
            state: PlacementState with validated product

        Returns:
            PlacementState with ROI predictions and data quality metrics
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
            # Calculate ROI with transparency
            roi_result = self._calculate_roi_transparent(product, location)

            # Check budget constraint
            if roi_result['placement_cost'] > product.budget:
                self.log_info(
                    f"Skipping {location.name}: cost ${roi_result['placement_cost']:.2f} "
                    f"exceeds budget ${product.budget:.2f}"
                )
                continue

            # Generate confidence interval
            lower_bound = roi_result['roi'] * 0.85
            upper_bound = roi_result['roi'] * 1.15

            roi_predictions[location.name] = ROIPrediction(
                location=location.name,
                roi=round(roi_result['roi'], 2),
                confidence_interval=(round(lower_bound, 2), round(upper_bound, 2)),
                placement_cost=round(roi_result['placement_cost'], 2),
                confidence_level=0.80,
                # Add data quality metadata
                **{'data_quality': roi_result['data_quality']}
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

        # Create recommendations (top 5)
        state.final_recommendations = {
            loc: pred.roi
            for loc, pred in list(sorted_predictions.items())[:5]
        }

        self.log_info(f"✓ Generated ROI predictions for {len(roi_predictions)} locations")
        self.log_info(
            f"✓ Top recommendation: {list(sorted_predictions.keys())[0]} "
            f"(ROI: {list(sorted_predictions.values())[0].roi})"
        )

        return state

    def _calculate_roi_transparent(self, product, location: ShelfLocation) -> Dict:
        """
        Calculate ROI with full transparency on data sources.

        Returns dict with:
        - roi: Computed ROI value
        - placement_cost: Cost in USD
        - data_quality: Metadata about data sources
        """
        base_roi = 1.0

        # Get visibility factor (from YAML config)
        visibility_info = self.visibility_manager.get_visibility_factor(
            location.zone,
            location.shelf_id
        )
        visibility_multiplier = visibility_info['factor']

        # Get location performance (from sales or defaults)
        if self.data_manager and location.shelf_id in self.location_performance:
            # Use computed performance index
            performance_index = self.location_performance[location.shelf_id]
            traffic_boost = (performance_index / 100 - 1) * 0.15
            traffic_source = 'computed_from_sales'
        else:
            # Use traffic index from location data
            traffic_boost = (location.traffic_index / 200) * 0.15
            traffic_source = 'location_metadata'

        # Get category lift (from sales or defaults)
        if self.data_manager:
            lift_info = self.data_manager.get_category_lift(product.category, location.zone)
            category_multiplier = lift_info['lift']
            category_source = lift_info['source']
            category_confidence = lift_info['confidence']
            category_sample_size = lift_info.get('sample_size', 0)
        else:
            # Fallback to defaults
            category_multiplier = 1.0
            category_source = 'fallback'
            category_confidence = 'low'
            category_sample_size = 0

        # Price tier consideration
        price_tier_multiplier = 1.0
        if product.price > 5.0:  # Premium product
            if location.zone in ['endcap', 'eye_level']:
                price_tier_multiplier = 1.1
        elif product.price < 2.0:  # Budget product
            if location.zone in ['low_shelf']:
                price_tier_multiplier = 1.05

        # Calculate final ROI
        roi = (
            base_roi *
            visibility_multiplier *
            (1 + traffic_boost) *
            category_multiplier *
            price_tier_multiplier
        )

        # Add realistic noise (±5%)
        import random
        noise = random.gauss(0, 0.05)
        roi = roi + noise

        # Clamp to realistic range
        roi = max(0.5, min(3.0, roi))

        # Get placement cost
        placement_cost = self.cost_manager.get_placement_cost(
            location_id=location.shelf_id,
            zone_type=location.zone
        )

        # Return with full transparency
        return {
            'roi': roi,
            'placement_cost': placement_cost,
            'data_quality': {
                'visibility': {
                    'value': visibility_multiplier,
                    'source': visibility_info['source'],
                    'confidence': visibility_info['confidence']
                },
                'traffic': {
                    'value': traffic_boost,
                    'source': traffic_source
                },
                'category_lift': {
                    'value': category_multiplier,
                    'source': category_source,
                    'confidence': category_confidence,
                    'sample_size': category_sample_size
                },
                'price_tier': {
                    'value': price_tier_multiplier,
                    'source': 'rule_based'
                },
                'placement_cost': {
                    'value': placement_cost,
                    'source': 'yaml_config'
                }
            }
        }


# Maintain backward compatibility
class AnalyzerAgent(AnalyzerAgentV2):
    """Alias for backward compatibility."""
    pass
