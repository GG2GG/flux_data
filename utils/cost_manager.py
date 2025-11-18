"""
Cost Manager - YAML-based placement cost configuration.

Manages placement costs with zone defaults and store-specific overrides.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class CostManager:
    """
    Manages placement costs from YAML configuration.

    Features:
    - Zone-based default costs
    - Store-specific overrides
    - Traffic-based adjustments
    - Seasonal pricing
    - Duration-based calculations
    """

    def __init__(self, config_path: str = "config/placement_costs.yaml"):
        """
        Initialize cost manager from YAML config.

        Args:
            config_path: Path to placement costs YAML file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            self._use_fallback_config()
            return

        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"✓ Loaded cost configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._use_fallback_config()

    def _use_fallback_config(self):
        """Use hardcoded fallback configuration."""
        self.config = {
            'zone_defaults': {
                'endcap': 2000,
                'checkout': 1500,
                'eye_level': 1000,
                'regular_shelf': 800,
                'low_shelf': 500,
                'top_shelf': 600
            },
            'placement': {
                'default_duration_weeks': 4,
                'budget_flexibility_pct': 10,
                'min_budget_usd': 500
            }
        }
        logger.info("Using fallback cost configuration")

    def get_placement_cost(
        self,
        location_id: str,
        zone_type: str,
        store_id: str = 'default',
        duration_weeks: Optional[int] = None
    ) -> float:
        """
        Get placement cost for a location.

        Args:
            location_id: Location identifier (e.g., 'A001')
            zone_type: Zone type (e.g., 'endcap', 'eye_level')
            store_id: Store identifier for overrides
            duration_weeks: Placement duration (uses default if None)

        Returns:
            Placement cost in USD
        """
        # Get duration
        if duration_weeks is None:
            duration_weeks = self.config.get('placement', {}).get('default_duration_weeks', 4)

        # Try store-specific aisle cost
        if store_id != 'default':
            stores = self.config.get('stores', {})
            if store_id in stores:
                store_config = stores[store_id]
                aisles = store_config.get('aisles', {})
                if location_id in aisles:
                    monthly_cost = aisles[location_id]['monthly_cost']
                    cost = monthly_cost * (duration_weeks / 4)
                    logger.debug(f"Using store-specific cost for {store_id}/{location_id}: ${cost:.2f}")
                    return cost

        # Fall back to zone default
        zone_defaults = self.config.get('zone_defaults', {})
        # Normalize zone name: "End Cap" → "endcap", "Eye Level" → "eye_level"
        zone_normalized = zone_type.lower().replace(' ', '_')

        # Try both formats: with underscores and without
        monthly_cost = zone_defaults.get(zone_normalized)
        if monthly_cost is None:
            # Try without underscores
            zone_no_underscore = zone_normalized.replace('_', '')
            monthly_cost = zone_defaults.get(zone_no_underscore, 800)  # Default $800 if zone not found

        cost = monthly_cost * (duration_weeks / 4)

        logger.debug(f"Using zone default cost for {zone_type}: ${cost:.2f}")
        return cost

    def get_zone_default_cost(self, zone_type: str) -> float:
        """
        Get default monthly cost for a zone type.

        Args:
            zone_type: Zone type (e.g., 'endcap')

        Returns:
            Monthly cost in USD
        """
        zone_defaults = self.config.get('zone_defaults', {})
        zone_key = zone_type.lower().replace(' ', '_')
        return zone_defaults.get(zone_key, 800)

    def check_budget_feasibility(
        self,
        budget: float,
        required_cost: float
    ) -> Dict[str, Any]:
        """
        Check if budget allows for placement.

        Args:
            budget: Available budget
            required_cost: Required placement cost

        Returns:
            Dict with feasibility assessment
        """
        flexibility_pct = self.config.get('placement', {}).get('budget_flexibility_pct', 10)
        max_allowed = budget * (1 + flexibility_pct / 100)

        return {
            'feasible': required_cost <= max_allowed,
            'budget': budget,
            'required_cost': required_cost,
            'flexibility_pct': flexibility_pct,
            'max_allowed': max_allowed,
            'over_budget_amount': max(0, required_cost - max_allowed),
            'recommendation': 'approved' if required_cost <= budget else
                            'acceptable' if required_cost <= max_allowed else
                            'rejected'
        }

    def get_all_zone_costs(self, duration_weeks: Optional[int] = None) -> Dict[str, float]:
        """
        Get costs for all zone types.

        Args:
            duration_weeks: Placement duration (uses default if None)

        Returns:
            Dict mapping zone types to costs
        """
        if duration_weeks is None:
            duration_weeks = self.config.get('placement', {}).get('default_duration_weeks', 4)

        zone_defaults = self.config.get('zone_defaults', {})

        return {
            zone: monthly_cost * (duration_weeks / 4)
            for zone, monthly_cost in zone_defaults.items()
        }

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get summary of current configuration.

        Returns:
            Configuration summary
        """
        return {
            'config_path': str(self.config_path),
            'config_exists': self.config_path.exists(),
            'zone_defaults': self.config.get('zone_defaults', {}),
            'default_duration_weeks': self.config.get('placement', {}).get('default_duration_weeks'),
            'budget_flexibility_pct': self.config.get('placement', {}).get('budget_flexibility_pct'),
            'num_stores_configured': len(self.config.get('stores', {})),
            'seasonal_adjustments_enabled': self.config.get('seasonal_adjustments', {}).get('enabled', False)
        }


class VisibilityManager:
    """
    Manages visibility factors from YAML configuration.

    Loads research-backed visibility factors and allows custom overrides.
    """

    def __init__(self, config_path: str = "config/zone_visibility.yaml"):
        """
        Initialize visibility manager from YAML config.

        Args:
            config_path: Path to zone visibility YAML file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            self._use_fallback_config()
            return

        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"✓ Loaded visibility configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._use_fallback_config()

    def _use_fallback_config(self):
        """Use hardcoded fallback configuration."""
        self.config = {
            'zone_visibility': {
                'endcap': {'factor': 1.5, 'confidence': 'high'},
                'checkout': {'factor': 1.6, 'confidence': 'high'},
                'eye_level': {'factor': 1.2, 'confidence': 'high'},
                'mid_shelf': {'factor': 1.0, 'confidence': 'high'},
                'low_shelf': {'factor': 0.8, 'confidence': 'high'},
                'top_shelf': {'factor': 0.85, 'confidence': 'medium'},
                'regular_shelf': {'factor': 1.0, 'confidence': 'high'}
            }
        }
        logger.info("Using fallback visibility configuration")

    def get_visibility_factor(
        self,
        zone_type: str,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get visibility factor for a zone type.

        Args:
            zone_type: Zone type (e.g., 'endcap', 'eye_level')
            location_id: Optional location ID for custom overrides

        Returns:
            Dict with visibility factor and metadata
        """
        # Check for custom location override
        if location_id:
            custom_locations = self.config.get('custom_locations', {}) or {}
            if custom_locations and location_id in custom_locations:
                custom = custom_locations[location_id]
                logger.debug(f"Using custom visibility for {location_id}: {custom['visibility_override']}")
                return {
                    'factor': custom['visibility_override'],
                    'source': 'custom_override',
                    'confidence': 'medium',
                    'reason': custom.get('reason', 'Custom override')
                }

        # Get zone default
        zone_visibility = self.config.get('zone_visibility', {})
        # Normalize zone name: "End Cap" → "endcap", "Eye Level" → "eye_level"
        zone_normalized = zone_type.lower().replace(' ', '_')

        # Try both formats: with underscores and without
        if zone_normalized in zone_visibility:
            zone_key = zone_normalized
        else:
            zone_no_underscore = zone_normalized.replace('_', '')
            if zone_no_underscore in zone_visibility:
                zone_key = zone_no_underscore
            else:
                zone_key = None

        if zone_key is None or zone_key not in zone_visibility:
            logger.warning(f"Unknown zone type: {zone_type}, using baseline 1.0")
            return {
                'factor': 1.0,
                'source': 'fallback',
                'confidence': 'low'
            }

        zone_config = zone_visibility[zone_key]

        return {
            'factor': zone_config['factor'],
            'source': 'research_default',
            'confidence': zone_config.get('confidence', 'medium'),
            'visibility_pct': zone_config.get('visibility_pct'),
            'description': zone_config.get('description')
        }

    def get_all_visibility_factors(self) -> Dict[str, Dict[str, Any]]:
        """
        Get visibility factors for all zone types.

        Returns:
            Dict mapping zone types to visibility info
        """
        zone_visibility = self.config.get('zone_visibility', {})

        return {
            zone: {
                'factor': info['factor'],
                'visibility_pct': info.get('visibility_pct'),
                'confidence': info.get('confidence'),
                'description': info.get('description')
            }
            for zone, info in zone_visibility.items()
        }


def main():
    """Test cost and visibility managers."""
    logging.basicConfig(level=logging.INFO)

    # Test Cost Manager
    print("\n" + "=" * 60)
    print("COST MANAGER TEST")
    print("=" * 60)

    cost_mgr = CostManager()
    summary = cost_mgr.get_config_summary()

    print(f"Config path: {summary['config_path']}")
    print(f"Config exists: {summary['config_exists']}")
    print(f"Default duration: {summary['default_duration_weeks']} weeks")
    print(f"Budget flexibility: {summary['budget_flexibility_pct']}%")

    print("\nZone Costs (4 weeks):")
    zone_costs = cost_mgr.get_all_zone_costs()
    for zone, cost in zone_costs.items():
        print(f"  {zone:20s} ${cost:,.2f}")

    # Test budget feasibility
    print("\nBudget Feasibility Check:")
    check = cost_mgr.check_budget_feasibility(budget=5000, required_cost=5200)
    print(f"  Budget: ${check['budget']:,.2f}")
    print(f"  Required: ${check['required_cost']:,.2f}")
    print(f"  Recommendation: {check['recommendation']}")

    # Test Visibility Manager
    print("\n" + "=" * 60)
    print("VISIBILITY MANAGER TEST")
    print("=" * 60)

    vis_mgr = VisibilityManager()

    print("\nVisibility Factors:")
    factors = vis_mgr.get_all_visibility_factors()
    for zone, info in factors.items():
        print(f"  {zone:20s} {info['factor']:.2f}x ({info['visibility_pct']}% visibility)")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
