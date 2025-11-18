"""
Adaptive Data Manager - Intelligent metric computation with automatic fallbacks.

Computes metrics from sales data when available, gracefully falls back to
industry defaults when data is insufficient. Maintains full transparency
about data sources and confidence levels.
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from utils.data_loader import SalesDataLoader

logger = logging.getLogger(__name__)


class AdaptiveDataManager:
    """
    Manages data loading, metric computation, and intelligent fallbacks.

    Automatically:
    - Computes category lifts from sales data
    - Computes location performance indices
    - Falls back to industry defaults when data is insufficient
    - Tracks data quality and confidence
    - Generates metadata about all computations
    """

    # Industry default category lifts (from retail research)
    INDUSTRY_DEFAULTS = {
        'Beverages': {
            'endcap': 1.4,
            'eye_level': 1.15,
            'checkout': 1.3,
            'low_shelf': 0.85
        },
        'Snacks': {
            'endcap': 1.5,
            'eye_level': 1.2,
            'checkout': 1.7,
            'low_shelf': 0.8
        },
        'Dairy': {
            'endcap': 1.3,
            'eye_level': 1.1,
            'checkout': 1.0,
            'low_shelf': 0.9
        },
        'Bakery': {
            'endcap': 1.4,
            'eye_level': 1.2,
            'checkout': 0.9,
            'low_shelf': 0.85
        },
        'Personal Care': {
            'endcap': 1.2,
            'eye_level': 1.15,
            'checkout': 0.8,
            'low_shelf': 0.9
        }
    }

    def __init__(
        self,
        sales_csv_path: Optional[str] = None,
        data_dir: str = "data",
        min_sample_size: int = 30
    ):
        """
        Initialize the adaptive data manager.

        Args:
            sales_csv_path: Path to sales history CSV (optional)
            data_dir: Base data directory
            min_sample_size: Minimum samples for high confidence metrics
        """
        self.data_dir = Path(data_dir)
        self.min_sample_size = min_sample_size
        self.sales_loader: Optional[SalesDataLoader] = None

        # Storage for computed metrics
        self.category_lifts: Dict[str, Dict] = {}
        self.location_performance: Dict[str, float] = {}
        self.metadata: Dict[str, Any] = {}

        # Load sales data if available
        if sales_csv_path and Path(sales_csv_path).exists():
            try:
                self.sales_loader = SalesDataLoader(sales_csv_path)
                logger.info("✓ Sales data loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load sales data: {e}")
                self.sales_loader = None
        else:
            logger.warning("No sales data provided, will use industry defaults")

    def compute_all_metrics(self) -> Dict[str, Any]:
        """
        Compute all metrics with automatic fallbacks.

        Returns:
            Dict containing all metrics and metadata
        """
        logger.info("=" * 60)
        logger.info("COMPUTING METRICS WITH ADAPTIVE FALLBACKS")
        logger.info("=" * 60)

        # Load product and location metadata
        product_metadata = self._load_product_metadata()
        location_metadata = self._load_location_metadata()

        # Compute category lifts
        self.category_lifts = self._compute_category_lifts_adaptive(
            product_metadata, location_metadata
        )

        # Compute location performance
        if self.sales_loader:
            self.location_performance = self.sales_loader.compute_location_performance()
            logger.info(f"✓ Computed performance for {len(self.location_performance)} locations")
        else:
            logger.warning("No sales data - using zone-type defaults for location performance")
            self.location_performance = self._get_default_location_performance(location_metadata)

        # Generate metadata
        self.metadata = self._generate_metadata()

        # Save computed metrics
        self._save_computed_metrics()

        logger.info("=" * 60)
        logger.info("METRIC COMPUTATION COMPLETE")
        logger.info("=" * 60)

        return {
            'category_lifts': self.category_lifts,
            'location_performance': self.location_performance,
            'metadata': self.metadata
        }

    def _compute_category_lifts_adaptive(
        self,
        product_metadata: Dict[str, Dict],
        location_metadata: Dict[str, Dict]
    ) -> Dict[str, Dict]:
        """
        Compute category lifts with intelligent fallback to defaults.

        Args:
            product_metadata: Product info (category, price, etc)
            location_metadata: Location info (zone_type, etc)

        Returns:
            Category lifts with confidence indicators
        """
        category_lifts = {}

        # Try to compute from sales data
        if self.sales_loader:
            computed_lifts = self.sales_loader.compute_category_lifts(
                product_metadata,
                location_metadata,
                min_sample_size=self.min_sample_size
            )

            # Merge computed with defaults
            for category in self.INDUSTRY_DEFAULTS.keys():
                if category in computed_lifts:
                    # Use computed values, fill gaps with defaults
                    category_lifts[category] = {}

                    for zone in ['endcap', 'eye_level', 'checkout', 'low_shelf']:
                        computed = computed_lifts[category].get(zone, {})

                        if computed.get('source') == 'computed' and computed.get('confidence') in ['high', 'medium']:
                            # Use computed value
                            category_lifts[category][zone] = {
                                'lift': computed['lift'],
                                'source': 'computed',
                                'confidence': computed['confidence'],
                                'sample_size': computed['sample_size']
                            }
                            logger.info(f"✓ {category} - {zone}: {computed['lift']:.2f} (computed, {computed['sample_size']} samples)")
                        else:
                            # Fall back to default
                            default_lift = self.INDUSTRY_DEFAULTS[category].get(zone, 1.0)
                            category_lifts[category][zone] = {
                                'lift': default_lift,
                                'source': 'industry_default',
                                'confidence': 'low',
                                'sample_size': computed.get('sample_size', 0)
                            }
                            logger.warning(f"⚠ {category} - {zone}: {default_lift:.2f} (default, insufficient data)")
                else:
                    # No computed data for this category, use all defaults
                    category_lifts[category] = {}
                    for zone, lift in self.INDUSTRY_DEFAULTS[category].items():
                        category_lifts[category][zone] = {
                            'lift': lift,
                            'source': 'industry_default',
                            'confidence': 'low',
                            'sample_size': 0
                        }
                    logger.warning(f"⚠ {category}: Using all defaults (no sales data)")
        else:
            # No sales data, use all defaults
            logger.warning("Using industry defaults for all categories (no sales data)")
            for category, zones in self.INDUSTRY_DEFAULTS.items():
                category_lifts[category] = {}
                for zone, lift in zones.items():
                    category_lifts[category][zone] = {
                        'lift': lift,
                        'source': 'industry_default',
                        'confidence': 'low',
                        'sample_size': 0
                    }

        return category_lifts

    def _get_default_location_performance(
        self,
        location_metadata: Dict[str, Dict]
    ) -> Dict[str, float]:
        """
        Generate default location performance based on zone types.

        Args:
            location_metadata: Location info with zone types

        Returns:
            Performance indices (100 = average)
        """
        zone_performance = {
            'endcap': 150,
            'checkout': 160,
            'eye_level': 120,
            'regular': 100,
            'regular_shelf': 100,
            'low_shelf': 70,
            'bottom_shelf': 60
        }

        performance = {}
        for loc_id, loc_info in location_metadata.items():
            zone = loc_info.get('zone', 'regular').lower()
            performance[loc_id] = zone_performance.get(zone, 100)

        return performance

    def _load_product_metadata(self) -> Dict[str, Dict]:
        """Load product metadata from input directory."""
        products_file = self.data_dir / 'input' / 'products.json'

        if not products_file.exists():
            logger.error(f"Products file not found: {products_file}")
            return {}

        with open(products_file, 'r') as f:
            products = json.load(f)

        return {
            p['product_id']: {
                'category': p['category'],
                'price': p['price'],
                'name': p['name']
            }
            for p in products
        }

    def _load_location_metadata(self) -> Dict[str, Dict]:
        """Load location metadata from input directory."""
        locations_file = self.data_dir / 'input' / 'locations.json'

        if not locations_file.exists():
            logger.error(f"Locations file not found: {locations_file}")
            return {}

        with open(locations_file, 'r') as f:
            locations = json.load(f)

        return {
            loc['location_id']: {
                'zone': loc['zone_type'],
                'name': loc['zone_name'],
                'traffic_index': loc.get('traffic_index', 150)
            }
            for loc in locations
        }

    def _generate_metadata(self) -> Dict[str, Any]:
        """Generate metadata about computation quality."""
        metadata = {
            'computation_timestamp': datetime.now().isoformat(),
            'data_sources': {
                'sales_data': self.sales_loader is not None,
                'sales_file': str(self.sales_loader.csv_path) if self.sales_loader else None
            }
        }

        if self.sales_loader:
            summary = self.sales_loader.get_data_summary()
            metadata.update({
                'sales_summary': summary,
                'data_quality': self._assess_data_quality(summary)
            })

        # Count computed vs defaulted metrics
        total_metrics = 0
        computed_metrics = 0
        high_confidence = 0

        for category, zones in self.category_lifts.items():
            for zone, info in zones.items():
                total_metrics += 1
                if info['source'] == 'computed':
                    computed_metrics += 1
                if info['confidence'] == 'high':
                    high_confidence += 1

        metadata['metrics_summary'] = {
            'total_metrics': total_metrics,
            'computed_from_sales': computed_metrics,
            'using_defaults': total_metrics - computed_metrics,
            'high_confidence': high_confidence,
            'computation_rate': round(computed_metrics / total_metrics * 100, 1) if total_metrics > 0 else 0
        }

        return metadata

    def _assess_data_quality(self, summary: Dict) -> Dict[str, Any]:
        """Assess overall data quality."""
        total_trans = summary.get('total_transactions', 0)

        if total_trans >= 3000:
            quality = 'excellent'
            confidence = 0.95
        elif total_trans >= 1000:
            quality = 'good'
            confidence = 0.85
        elif total_trans >= 500:
            quality = 'fair'
            confidence = 0.70
        else:
            quality = 'poor'
            confidence = 0.50

        return {
            'quality_level': quality,
            'confidence_score': confidence,
            'recommendation': self._get_quality_recommendation(quality)
        }

    def _get_quality_recommendation(self, quality: str) -> str:
        """Get recommendation based on data quality."""
        recommendations = {
            'excellent': 'Data quality is excellent. Recommendations are highly reliable.',
            'good': 'Data quality is good. Recommendations are reliable.',
            'fair': 'Data quality is fair. Consider collecting more data for better accuracy.',
            'poor': 'Data quality is poor. Using mostly industry defaults. Collect more sales data for better recommendations.'
        }
        return recommendations.get(quality, 'Unknown quality level')

    def _save_computed_metrics(self):
        """Save computed metrics to data/computed/."""
        computed_dir = self.data_dir / 'computed'
        computed_dir.mkdir(exist_ok=True)

        # Save category lifts
        with open(computed_dir / 'category_lifts.json', 'w') as f:
            json.dump(self.category_lifts, f, indent=2)

        # Save location performance
        with open(computed_dir / 'location_performance.json', 'w') as f:
            json.dump(self.location_performance, f, indent=2)

        # Save metadata
        with open(computed_dir / 'metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=2)

        logger.info(f"✓ Saved computed metrics to {computed_dir}")

    def get_category_lift(self, category: str, zone: str) -> Dict[str, Any]:
        """
        Get lift factor for a category-zone combination.

        Args:
            category: Product category
            zone: Zone type (endcap, eye_level, etc)

        Returns:
            Dict with lift value and metadata
        """
        if category not in self.category_lifts:
            # Unknown category, return neutral lift
            logger.warning(f"Unknown category: {category}, using neutral lift")
            return {
                'lift': 1.0,
                'source': 'fallback',
                'confidence': 'low',
                'sample_size': 0
            }

        # Normalize zone name: "End Cap" → "endcap", "Eye Level" → "eye_level"
        zone_normalized = zone.lower().replace(' ', '_')

        # Try both formats: with underscores and without
        # First try with underscores (e.g., "eye_level")
        result = self.category_lifts[category].get(zone_normalized)
        if result:
            return result

        # Try without underscores (e.g., "endcap")
        zone_no_underscore = zone_normalized.replace('_', '')
        result = self.category_lifts[category].get(zone_no_underscore)
        if result:
            return result

        # Default fallback
        return {
            'lift': 1.0,
            'source': 'fallback',
            'confidence': 'low',
            'sample_size': 0
        }

    def get_location_performance(self, location_id: str) -> float:
        """
        Get performance index for a location.

        Args:
            location_id: Location identifier

        Returns:
            Performance index (100 = average)
        """
        return self.location_performance.get(location_id, 100.0)


def main():
    """Test the adaptive data manager."""
    logging.basicConfig(level=logging.INFO)

    # Initialize manager
    manager = AdaptiveDataManager(
        sales_csv_path='data/input/sales_history.csv',
        data_dir='data'
    )

    # Compute all metrics
    results = manager.compute_all_metrics()

    # Print summary
    print("\n" + "=" * 60)
    print("COMPUTATION SUMMARY")
    print("=" * 60)
    print(f"Total metrics: {results['metadata']['metrics_summary']['total_metrics']}")
    print(f"Computed from sales: {results['metadata']['metrics_summary']['computed_from_sales']}")
    print(f"Using defaults: {results['metadata']['metrics_summary']['using_defaults']}")
    print(f"Computation rate: {results['metadata']['metrics_summary']['computation_rate']}%")

    if 'data_quality' in results['metadata']:
        quality = results['metadata']['data_quality']
        print(f"\nData Quality: {quality['quality_level'].upper()}")
        print(f"Confidence: {quality['confidence_score']:.1%}")
        print(f"Recommendation: {quality['recommendation']}")

    print("=" * 60)


if __name__ == '__main__':
    main()
