"""
Polars-based Data Loader for High-Performance Data Processing
Provides 10-100x faster processing compared to Pandas for large datasets
"""

import polars as pl
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SalesDataLoader:
    """
    High-performance sales data loader using Polars.

    Handles validation, transformation, and metric computation
    from sales transaction data.
    """

    def __init__(self, csv_path: str):
        """
        Initialize loader with sales CSV path.

        Args:
            csv_path: Path to sales history CSV file
        """
        self.csv_path = Path(csv_path)
        self.df: Optional[pl.DataFrame] = None
        self._load_data()
        self._validate_schema()

    def _load_data(self):
        """Load CSV data using Polars lazy evaluation."""
        try:
            # Use lazy loading for better performance
            self.df = pl.read_csv(self.csv_path)
            logger.info(f"✓ Loaded {len(self.df)} sales records from {self.csv_path}")
        except Exception as e:
            logger.error(f"Failed to load sales data: {e}")
            raise ValueError(f"Cannot load sales data from {self.csv_path}: {e}")

    def _validate_schema(self):
        """Validate that required columns exist."""
        required_cols = {
            'product_id': pl.Utf8,
            'location_id': pl.Utf8,
            'units_sold': pl.Int64,
            'revenue': pl.Float64
        }

        optional_cols = {
            'was_promoted': pl.Boolean,
            'week_date': pl.Utf8,
            'month': pl.Int64,
            'year': pl.Int64
        }

        # Check required columns
        missing = set(required_cols.keys()) - set(self.df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Log optional missing columns
        missing_optional = set(optional_cols.keys()) - set(self.df.columns)
        if missing_optional:
            logger.warning(f"Missing optional columns: {missing_optional}")

        logger.info("✓ Schema validation passed")

    def get_data_summary(self) -> Dict:
        """
        Get summary statistics of the sales data.

        Returns:
            Dictionary with data quality metrics
        """
        return {
            'total_transactions': len(self.df),
            'unique_products': self.df['product_id'].n_unique(),
            'unique_locations': self.df['location_id'].n_unique(),
            'date_range': self._get_date_range(),
            'total_revenue': float(self.df['revenue'].sum()),
            'total_units': int(self.df['units_sold'].sum()),
            'has_promotion_data': 'was_promoted' in self.df.columns,
        }

    def _get_date_range(self) -> Optional[Tuple[str, str]]:
        """Get date range of sales data."""
        if 'week_date' in self.df.columns:
            dates = self.df['week_date'].unique().sort()
            return (str(dates[0]), str(dates[-1]))
        return None

    def compute_category_lifts(
        self,
        product_metadata: Dict[str, Dict] = None,
        location_metadata: Dict[str, Dict] = None,
        min_sample_size: int = 30
    ) -> Dict[str, Dict]:
        """
        Compute category-specific lift factors from sales data.

        Args:
            product_metadata: Dict mapping product_id to {category, price, etc} (optional if already in CSV)
            location_metadata: Dict mapping location_id to {zone_type, etc} (optional if already in CSV)
            min_sample_size: Minimum samples required for high confidence

        Returns:
            Dict with category lifts and confidence metrics
        """
        logger.info("Computing category lift factors from sales data...")

        # Check if category and zone_type are already in the dataframe
        has_category = 'category' in self.df.columns
        has_zone = 'zone_type' in self.df.columns

        if has_category and has_zone:
            logger.info("✓ Category and zone_type found in sales data, computing directly")
            enriched_df = self.df
        elif product_metadata and location_metadata:
            logger.info("✓ Using provided metadata to enrich sales data")
            # Add product metadata (category) to sales data
            product_df = pl.DataFrame({
                'product_id': list(product_metadata.keys()),
                'category': [p['category'] for p in product_metadata.values()]
            })

            # Add location metadata (zone_type) to sales data
            location_df = pl.DataFrame({
                'location_id': list(location_metadata.keys()),
                'zone_type': [loc['zone'] for loc in location_metadata.values()]
            })

            # Join metadata with sales
            enriched_df = (
                self.df
                .join(product_df, on='product_id', how='left')
                .join(location_df, on='location_id', how='left')
            )
        else:
            logger.warning("No category/zone_type in CSV and no metadata provided")
            return {}

        # Filter out promotional periods for cleaner signal
        if 'was_promoted' in enriched_df.columns:
            enriched_df = enriched_df.filter(pl.col('was_promoted') == False)

        # Compute baseline performance (regular shelf)
        # Normalize: "Regular Shelf" -> "regularshelf"
        baseline_zones = ['regular', 'regularshelf', 'midshelf']

        category_lifts = {}

        for category in enriched_df['category'].unique():
            cat_data = enriched_df.filter(pl.col('category') == category)

            # Compute baseline (avg sales in regular zones)
            # Normalize zone_type for comparison
            baseline = (
                cat_data
                .filter(pl.col('zone_type').str.to_lowercase().str.replace_all(' ', '').is_in(baseline_zones))
                .select(pl.col('units_sold').mean())
                .item()
            )

            if baseline is None or baseline == 0:
                # No baseline data, skip this category
                logger.warning(f"No baseline data for category: {category}")
                continue

            # Compute lift for each zone type
            zone_lifts = {}
            for zone in ['endcap', 'checkout', 'eye_level']:
                # Normalize zone names for comparison: "End Cap" -> "endcap", "Eye Level" -> "eyelevel"
                zone_normalized = zone.replace('_', '')
                zone_data = cat_data.filter(
                    pl.col('zone_type').str.to_lowercase().str.replace_all(' ', '') == zone_normalized
                )

                if len(zone_data) < min_sample_size:
                    # Insufficient data
                    zone_lifts[zone] = {
                        'lift': None,
                        'confidence': 'low',
                        'sample_size': len(zone_data),
                        'source': 'insufficient_data'
                    }
                    continue

                zone_avg = zone_data.select(pl.col('units_sold').mean()).item()
                lift = zone_avg / baseline if baseline > 0 else 1.0

                zone_lifts[zone] = {
                    'lift': round(lift, 2),
                    'confidence': 'high' if len(zone_data) >= 150 else 'medium',
                    'sample_size': len(zone_data),
                    'source': 'computed',
                    'baseline_sales': round(baseline, 1),
                    'zone_sales': round(zone_avg, 1)
                }

            category_lifts[category] = zone_lifts

        logger.info(f"✓ Computed lifts for {len(category_lifts)} categories")
        return category_lifts

    def compute_location_performance(self) -> Dict[str, float]:
        """
        Compute relative performance index for each location.

        Returns:
            Dict mapping location_id to performance index (100 = average)
        """
        logger.info("Computing location performance indices...")

        # Aggregate sales by location
        location_sales = (
            self.df
            .group_by('location_id')
            .agg(pl.col('units_sold').sum().alias('total_units'))
        )

        # Compute average
        avg_sales = location_sales['total_units'].mean()

        # Normalize to index (100 = average)
        performance = {}
        for row in location_sales.iter_rows(named=True):
            location_id = row['location_id']
            performance[location_id] = round((row['total_units'] / avg_sales) * 100, 1)

        logger.info(f"✓ Computed performance for {len(performance)} locations")
        return performance

    def get_product_sales_by_location(self, product_id: str) -> Dict[str, float]:
        """
        Get historical sales performance for a specific product across locations.

        Args:
            product_id: Product identifier

        Returns:
            Dict mapping location_id to average units sold
        """
        product_sales = (
            self.df
            .filter(pl.col('product_id') == product_id)
            .group_by('location_id')
            .agg([
                pl.col('units_sold').mean().alias('avg_units'),
                pl.col('revenue').mean().alias('avg_revenue')
            ])
        )

        return {
            row['location_id']: {
                'avg_units': round(row['avg_units'], 1),
                'avg_revenue': round(row['avg_revenue'], 2)
            }
            for row in product_sales.iter_rows(named=True)
        }

    def compute_seasonality_factors(self) -> Optional[Dict[int, float]]:
        """
        Compute monthly seasonality indices.

        Returns:
            Dict mapping month (1-12) to seasonality factor (1.0 = average)
        """
        if 'month' not in self.df.columns:
            logger.warning("No month column, cannot compute seasonality")
            return None

        monthly_sales = (
            self.df
            .group_by('month')
            .agg(pl.col('units_sold').sum().alias('total_units'))
        )

        avg_monthly = monthly_sales['total_units'].mean()

        return {
            row['month']: round(row['total_units'] / avg_monthly, 2)
            for row in monthly_sales.iter_rows(named=True)
        }


# Utility functions

def load_product_metadata(json_path: str) -> Dict[str, Dict]:
    """
    Load product metadata from JSON file.

    Args:
        json_path: Path to products.json

    Returns:
        Dict mapping product_id to metadata
    """
    import json

    with open(json_path, 'r') as f:
        products = json.load(f)

    return {
        p['product_id']: {
            'category': p['category'],
            'price': p['price'],
            'name': p['name']
        }
        for p in products
    }


def load_location_metadata(json_path: str) -> Dict[str, Dict]:
    """
    Load location metadata from JSON file.

    Args:
        json_path: Path to locations.json

    Returns:
        Dict mapping location_id to metadata
    """
    import json

    with open(json_path, 'r') as f:
        locations = json.load(f)

    return {
        loc['location_id']: {
            'zone': loc['zone_type'],
            'name': loc['zone_name'],
            'traffic_index': loc.get('traffic_index', 150)
        }
        for loc in locations
    }
