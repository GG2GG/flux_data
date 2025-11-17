"""
Synthetic Data Generator for Retail Product Placement System
Generates realistic retail data with research-backed patterns
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)


class SyntheticDataGenerator:
    """Generate realistic synthetic retail data"""

    def __init__(self):
        self.categories = ['Beverages', 'Snacks', 'Dairy', 'Bakery', 'Personal Care']
        self.subcategories = {
            'Beverages': ['Energy Drinks', 'Soft Drinks', 'Juices', 'Water', 'Sports Drinks'],
            'Snacks': ['Chips', 'Candy', 'Nuts', 'Crackers', 'Protein Bars'],
            'Dairy': ['Milk', 'Yogurt', 'Cheese', 'Butter', 'Ice Cream'],
            'Bakery': ['Bread', 'Cookies', 'Muffins', 'Bagels', 'Donuts'],
            'Personal Care': ['Toothpaste', 'Shampoo', 'Soap', 'Deodorant', 'Lotion']
        }

        self.zone_types = {
            'End Cap': {'base_cost': 2000, 'traffic_multiplier': 2.0, 'visibility': 1.5},
            'Checkout': {'base_cost': 1500, 'traffic_multiplier': 1.4, 'visibility': 1.6},
            'Eye Level': {'base_cost': 1000, 'traffic_multiplier': 1.25, 'visibility': 1.2},
            'Main Entrance': {'base_cost': 1200, 'traffic_multiplier': 1.15, 'visibility': 1.3},
            'Regular Shelf': {'base_cost': 500, 'traffic_multiplier': 1.0, 'visibility': 1.0},
            'Bottom Shelf': {'base_cost': 400, 'traffic_multiplier': 0.8, 'visibility': 0.8}
        }

        self.current_month = 11  # November (holiday season)

    def generate_products(self, num_products: int = 30) -> List[Dict[str, Any]]:
        """Generate product catalog"""
        products = []
        product_names = {
            'Beverages': ['Premium Energy', 'Fresh Cola', 'Organic Juice', 'Pure Water', 'Sport Fuel'],
            'Snacks': ['Crunchy Chips', 'Sweet Candy', 'Trail Mix', 'Cheese Crackers', 'Protein Bar'],
            'Dairy': ['Whole Milk', 'Greek Yogurt', 'Cheddar Cheese', 'Organic Butter', 'Premium Ice Cream'],
            'Bakery': ['Whole Wheat Bread', 'Chocolate Cookies', 'Blueberry Muffins', 'Sesame Bagels', 'Glazed Donuts'],
            'Personal Care': ['Mint Toothpaste', 'Herbal Shampoo', 'Moisturizing Soap', 'Sport Deodorant', 'Body Lotion']
        }

        price_tiers = {
            'budget': {'multiplier': 0.7, 'margin': 0.25},
            'mid': {'multiplier': 1.0, 'margin': 0.35},
            'premium': {'multiplier': 1.4, 'margin': 0.45}
        }

        base_prices = {
            'Beverages': 2.50, 'Snacks': 2.00, 'Dairy': 3.50,
            'Bakery': 3.00, 'Personal Care': 4.00
        }

        brands = ['Brand A', 'Brand B', 'Brand C', 'Store Brand', 'Premium Brand']
        lifecycle_stages = ['new', 'growth', 'mature', 'decline']

        product_id = 1
        for category in self.categories:
            # Generate 6 products per category
            for i in range(6):
                tier_name = random.choice(['budget', 'mid', 'premium'])
                tier = price_tiers[tier_name]

                base_price = base_prices[category]
                price = round(base_price * tier['multiplier'], 2)
                cost = round(price * (1 - tier['margin']), 2)
                margin = round(price - cost, 2)
                margin_pct = round(tier['margin'] * 100, 1)

                subcategory = random.choice(self.subcategories[category])
                name_base = product_names[category][i % len(product_names[category])]

                product = {
                    'product_id': f'P{product_id:03d}',
                    'sku': f'SKU-{category[:3].upper()}-{product_id:04d}',
                    'name': f'{name_base} {tier_name.capitalize()}',
                    'category': category,
                    'subcategory': subcategory,
                    'price': price,
                    'cost': cost,
                    'margin': margin,
                    'margin_pct': margin_pct,
                    'brand': random.choice(brands),
                    'lifecycle_stage': random.choice(lifecycle_stages),
                    'price_tier': tier_name,
                    'notes': f'{tier_name.capitalize()} tier {category.lower()} product'
                }

                products.append(product)
                product_id += 1

                if len(products) >= num_products:
                    return products

        return products

    def generate_locations(self, num_locations: int = 10) -> List[Dict[str, Any]]:
        """Generate store locations"""
        locations = []

        location_templates = [
            {'name': 'End Cap 1 - Beverages', 'zone_type': 'End Cap', 'primary_category': 'Beverages', 'traffic': 'high'},
            {'name': 'Main Entrance Display', 'zone_type': 'Main Entrance', 'primary_category': 'Snacks', 'traffic': 'high'},
            {'name': 'Checkout Lane 1', 'zone_type': 'Checkout', 'primary_category': 'Snacks', 'traffic': 'high'},
            {'name': 'Beverage Aisle - Eye Level', 'zone_type': 'Eye Level', 'primary_category': 'Beverages', 'traffic': 'medium'},
            {'name': 'Snack Aisle - Eye Level', 'zone_type': 'Eye Level', 'primary_category': 'Snacks', 'traffic': 'medium'},
            {'name': 'Dairy Section - Regular', 'zone_type': 'Regular Shelf', 'primary_category': 'Dairy', 'traffic': 'medium'},
            {'name': 'Bakery Display', 'zone_type': 'Regular Shelf', 'primary_category': 'Bakery', 'traffic': 'medium'},
            {'name': 'End Cap 2 - Snacks', 'zone_type': 'End Cap', 'primary_category': 'Snacks', 'traffic': 'high'},
            {'name': 'Personal Care Aisle', 'zone_type': 'Regular Shelf', 'primary_category': 'Personal Care', 'traffic': 'low'},
            {'name': 'Beverage Aisle - Bottom', 'zone_type': 'Bottom Shelf', 'primary_category': 'Beverages', 'traffic': 'medium'}
        ]

        traffic_indices = {'low': 120, 'medium': 180, 'high': 250}

        for i, template in enumerate(location_templates[:num_locations]):
            zone_config = self.zone_types[template['zone_type']]

            location = {
                'location_id': f'L{i+1:03d}',
                'zone_name': template['name'],
                'zone_type': template['zone_type'],
                'primary_category': template['primary_category'],
                'traffic_level': template['traffic'],
                'traffic_index': traffic_indices[template['traffic']],
                'visibility_factor': zone_config['visibility'],
                'square_footage': random.randint(20, 100),
                'display_type': 'shelf' if 'Shelf' in template['zone_type'] else 'display',
                'x': random.randint(0, 800),
                'y': random.randint(0, 600),
                'width': random.randint(100, 200),
                'height': random.randint(80, 150),
                'base_placement_cost': zone_config['base_cost'],
                'notes': f"{template['zone_type']} in {template['primary_category']} area"
            }

            locations.append(location)

        return locations

    def generate_sales_history(self, products: List[Dict], locations: List[Dict],
                               months: int = 12) -> List[Dict[str, Any]]:
        """Generate historical sales data with patterns"""
        sales_records = []

        start_date = datetime.now() - timedelta(days=30 * months)

        for month_offset in range(months):
            current_date = start_date + timedelta(days=30 * month_offset)
            month = current_date.month

            # Seasonality multipliers
            seasonal_multiplier = self._get_seasonal_multiplier(month)

            for product in products:
                for location in locations:
                    # Category-location fit
                    category_fit = 1.2 if product['category'] == location['primary_category'] else 1.0

                    # Location effects
                    location_mult = self.zone_types[location['zone_type']]['traffic_multiplier']

                    # Base velocity
                    base_units = random.randint(50, 200)

                    # Apply all multipliers
                    units_sold = int(base_units * seasonal_multiplier * category_fit * location_mult)
                    units_sold = max(10, units_sold + random.randint(-20, 20))

                    revenue = round(units_sold * product['price'], 2)

                    was_promoted = random.random() < 0.15  # 15% promotion rate
                    if was_promoted:
                        units_sold = int(units_sold * 1.3)
                        revenue = round(units_sold * product['price'] * 0.9, 2)  # 10% discount

                    record = {
                        'product_id': product['product_id'],
                        'location_id': location['location_id'],
                        'month': month,
                        'year': current_date.year,
                        'week_date': current_date.strftime('%Y-%m-%d'),
                        'units_sold': units_sold,
                        'revenue': revenue,
                        'was_promoted': was_promoted
                    }

                    sales_records.append(record)

        return sales_records

    def generate_transactions(self, products: List[Dict], num_transactions: int = 50000) -> List[Dict[str, Any]]:
        """Generate transaction data for market basket analysis"""
        transactions = []

        # Define affinity rules
        affinity_pairs = {
            'Beverages': ['Snacks', 'Snacks'],  # Strong affinity
            'Snacks': ['Beverages'],
            'Dairy': ['Bakery'],
            'Bakery': ['Dairy'],
            'Personal Care': ['Personal Care']  # Same category
        }

        for i in range(num_transactions):
            # Start with anchor product
            anchor_product = random.choice(products)
            basket = [anchor_product['product_id']]

            # Add complementary products based on affinity
            num_items = random.randint(2, 6)

            for _ in range(num_items - 1):
                # 70% chance of related product, 30% random
                if random.random() < 0.7 and anchor_product['category'] in affinity_pairs:
                    related_category = random.choice(affinity_pairs[anchor_product['category']])
                    related_products = [p for p in products if p['category'] == related_category]
                    if related_products:
                        basket.append(random.choice(related_products)['product_id'])
                else:
                    basket.append(random.choice(products)['product_id'])

            # Remove duplicates
            basket = list(set(basket))

            transaction = {
                'transaction_id': f'TXN{i+1:06d}',
                'timestamp': (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
                'products': basket,
                'num_items': len(basket)
            }

            transactions.append(transaction)

        return transactions

    def generate_precomputed_roi(self, products: List[Dict], locations: List[Dict]) -> Dict[str, Dict]:
        """Generate precomputed ROI scores for all product-location pairs"""
        roi_data = {}

        for product in products:
            for location in locations:
                key = f"{product['product_id']}_{location['location_id']}"

                # Calculate ROI based on research-backed formula
                roi = self._calculate_roi(product, location)

                # Add realistic noise
                roi += random.gauss(0, 0.1)
                roi = max(0.5, min(3.0, roi))  # Clamp to realistic range

                # Calculate confidence intervals
                ci_width = 0.15 * roi  # 15% width
                lower = round(roi - ci_width, 2)
                upper = round(roi + ci_width, 2)

                # Calculate expected metrics
                base_units = random.randint(100, 500)
                expected_daily_units = int(base_units * roi / 30)
                daily_profit = round(expected_daily_units * product['margin'], 2)
                monthly_profit = round(daily_profit * 30, 2)

                placement_cost = location['base_placement_cost'] * 4  # 4 weeks

                roi_data[key] = {
                    'product_id': product['product_id'],
                    'location_id': location['location_id'],
                    'product_name': product['name'],
                    'location_name': location['zone_name'],
                    'roi': round(roi, 2),
                    'confidence_interval': [lower, upper],
                    'confidence_level': 0.80,
                    'expected_daily_units': expected_daily_units,
                    'expected_daily_profit': daily_profit,
                    'expected_30d_profit': monthly_profit,
                    'placement_cost': placement_cost
                }

        return roi_data

    def generate_feature_importance(self, products: List[Dict], locations: List[Dict]) -> Dict[str, List]:
        """Generate SHAP-style feature importance for each product-location pair"""
        importance_data = {}

        feature_names = [
            'location_velocity', 'category_location_fit', 'zone_type_end_cap',
            'zone_type_checkout', 'traffic_level', 'is_holiday_season',
            'price_tier', 'margin_percentage', 'brand_strength_index',
            'competitor_proximity_score'
        ]

        for product in products:
            for location in locations:
                key = f"{product['product_id']}_{location['location_id']}"

                # Generate realistic SHAP-style values
                shap_values = self._generate_shap_values(product, location)

                importance_data[key] = shap_values

        return importance_data

    def generate_competitors(self, products: List[Dict], locations: List[Dict]) -> List[Dict]:
        """Generate competitor product data"""
        competitors = []
        competitor_id = 1

        # For each category, create 2-3 competitor products per location
        for category in self.categories:
            category_products = [p for p in products if p['category'] == category]
            if not category_products:
                continue

            reference_product = random.choice(category_products)

            for location in locations:
                # 50% chance of competitors in this location
                if random.random() > 0.5:
                    continue

                num_competitors = random.randint(1, 3)

                for i in range(num_competitors):
                    competitor_price = reference_product['price'] * random.uniform(0.85, 1.15)
                    observed_roi = random.uniform(0.8, 2.0)
                    market_share = random.uniform(0.05, 0.30)

                    competitor = {
                        'competitor_id': f'COMP{competitor_id:03d}',
                        'product_name': f'{category} Competitor {chr(65+i)}',
                        'category': category,
                        'location_id': location['location_id'],
                        'location_name': location['zone_name'],
                        'price': round(competitor_price, 2),
                        'observed_roi': round(observed_roi, 2),
                        'market_share': round(market_share, 2),
                        'placement_date': (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
                    }

                    competitors.append(competitor)
                    competitor_id += 1

        return competitors

    def generate_historical_examples(self, products: List[Dict], locations: List[Dict]) -> List[Dict]:
        """Generate historical placement examples"""
        examples = []
        example_id = 1

        for location in locations:
            # Generate 15 examples per location (150 total for 10 locations)
            for _ in range(15):
                product = random.choice(products)

                # Calculate realistic ROI
                roi = self._calculate_roi(product, location)
                roi += random.gauss(0, 0.15)  # More variation than predicted
                roi = max(0.3, min(3.5, roi))

                placement_date = datetime.now() - timedelta(days=random.randint(30, 730))
                duration_days = random.randint(14, 120)

                example = {
                    'example_id': f'EX{example_id:04d}',
                    'product_name': product['name'],
                    'category': product['category'],
                    'price': product['price'],
                    'location_id': location['location_id'],
                    'location_name': location['zone_name'],
                    'actual_roi': round(roi, 2),
                    'placement_date': placement_date.strftime('%Y-%m-%d'),
                    'duration_days': duration_days,
                    'success_level': 'high' if roi > 1.5 else 'medium' if roi > 1.0 else 'low'
                }

                examples.append(example)
                example_id += 1

        return examples

    def _calculate_roi(self, product: Dict, location: Dict) -> float:
        """Calculate ROI using research-backed formula"""
        base_roi = 1.0

        # Location multiplier
        location_mult = self.zone_types[location['zone_type']]['traffic_multiplier']

        # Traffic boost
        traffic_boost = location['traffic_index'] / 180 * 0.15

        # Category fit
        category_fit = 1.2 if product['category'] == location['primary_category'] else 1.0

        # Seasonality (holiday season boost)
        seasonal_boost = 1.4 if self.current_month in [11, 12] and product['category'] == 'Beverages' else 1.0

        # Price tier fit (premium products do better in premium locations)
        price_fit = 1.1 if product['price_tier'] == 'premium' and location['zone_type'] in ['End Cap', 'Main Entrance'] else 1.0

        # Margin impact
        margin_boost = 1.0 + (product['margin_pct'] / 100 * 0.3)

        roi = base_roi * location_mult * (1 + traffic_boost) * category_fit * seasonal_boost * price_fit * margin_boost

        return roi

    def _get_seasonal_multiplier(self, month: int) -> float:
        """Get seasonal multiplier based on month"""
        # Holiday season (Nov-Dec)
        if month in [11, 12]:
            return 1.4
        # Summer (Jun-Aug)
        elif month in [6, 7, 8]:
            return 1.25
        # Spring (Mar-May)
        elif month in [3, 4, 5]:
            return 1.1
        # Back-to-school (Sep)
        elif month == 9:
            return 1.3
        # Regular months
        else:
            return 1.0

    def _generate_shap_values(self, product: Dict, location: Dict) -> List[Dict]:
        """Generate SHAP-style feature importance values"""
        shap_values = []

        # Location velocity contribution
        velocity_impact = location['traffic_index'] / 180 * 0.35
        shap_values.append({
            'feature': 'location_velocity',
            'shap_value': round(velocity_impact, 3),
            'feature_value': location['traffic_index']
        })

        # Category fit contribution
        category_impact = 0.28 if product['category'] == location['primary_category'] else 0.05
        shap_values.append({
            'feature': 'category_location_fit',
            'shap_value': round(category_impact, 3),
            'feature_value': 1.0 if product['category'] == location['primary_category'] else 0.5
        })

        # Zone type contribution
        zone_impact = 0.35 if location['zone_type'] == 'End Cap' else 0.25 if location['zone_type'] == 'Checkout' else 0.15
        shap_values.append({
            'feature': f"zone_type_{location['zone_type'].replace(' ', '_').lower()}",
            'shap_value': round(zone_impact, 3),
            'feature_value': 1.0
        })

        # Seasonality contribution
        seasonal_impact = 0.22 if self.current_month in [11, 12] else 0.05
        shap_values.append({
            'feature': 'is_holiday_season',
            'shap_value': round(seasonal_impact, 3),
            'feature_value': 1.0 if self.current_month in [11, 12] else 0.0
        })

        # Traffic level contribution
        traffic_impact = 0.18 if location['traffic_level'] == 'high' else 0.10
        shap_values.append({
            'feature': 'traffic_level',
            'shap_value': round(traffic_impact, 3),
            'feature_value': 2.0 if location['traffic_level'] == 'high' else 1.0
        })

        # Margin contribution
        margin_impact = product['margin_pct'] / 100 * 0.15
        shap_values.append({
            'feature': 'margin_percentage',
            'shap_value': round(margin_impact, 3),
            'feature_value': product['margin_pct']
        })

        # Price tier contribution
        price_impact = 0.12 if product['price_tier'] == 'premium' else 0.05
        shap_values.append({
            'feature': 'price_tier',
            'shap_value': round(price_impact, 3),
            'feature_value': 2 if product['price_tier'] == 'premium' else 1 if product['price_tier'] == 'mid' else 0
        })

        # Sort by absolute impact
        shap_values.sort(key=lambda x: abs(x['shap_value']), reverse=True)

        return shap_values


def main():
    """Generate all synthetic data"""
    print("🏪 Generating Synthetic Retail Data...")
    print("=" * 60)

    generator = SyntheticDataGenerator()

    # Generate products
    print("\n📦 Generating products...")
    products = generator.generate_products(30)
    print(f"   ✅ Generated {len(products)} products across {len(generator.categories)} categories")

    # Generate locations
    print("\n📍 Generating locations...")
    locations = generator.generate_locations(10)
    print(f"   ✅ Generated {len(locations)} store locations")

    # Generate sales history
    print("\n📊 Generating sales history (12 months)...")
    sales_history = generator.generate_sales_history(products, locations, months=12)
    print(f"   ✅ Generated {len(sales_history)} sales records")

    # Generate transactions
    print("\n🛒 Generating transaction data...")
    transactions = generator.generate_transactions(products, num_transactions=50000)
    print(f"   ✅ Generated {len(transactions)} transactions")

    # Generate precomputed ROI
    print("\n💰 Computing ROI scores (300 combinations)...")
    precomputed_roi = generator.generate_precomputed_roi(products, locations)
    print(f"   ✅ Generated {len(precomputed_roi)} ROI scores")

    # Generate feature importance
    print("\n🎯 Generating SHAP-style feature importance...")
    feature_importance = generator.generate_feature_importance(products, locations)
    print(f"   ✅ Generated feature importance for {len(feature_importance)} combinations")

    # Generate competitors
    print("\n🏆 Generating competitor data...")
    competitors = generator.generate_competitors(products, locations)
    print(f"   ✅ Generated {len(competitors)} competitor products")

    # Generate historical examples
    print("\n📚 Generating historical placement examples...")
    historical_examples = generator.generate_historical_examples(products, locations)
    print(f"   ✅ Generated {len(historical_examples)} historical examples")

    # Save all data
    print("\n💾 Saving data to files...")

    with open('data/products.json', 'w') as f:
        json.dump(products, f, indent=2)
    print("   ✅ Saved products.json")

    with open('data/locations.json', 'w') as f:
        json.dump(locations, f, indent=2)
    print("   ✅ Saved locations.json")

    with open('data/sales_history.json', 'w') as f:
        json.dump(sales_history, f, indent=2)
    print("   ✅ Saved sales_history.json")

    with open('data/transactions.json', 'w') as f:
        json.dump(transactions, f, indent=2)
    print("   ✅ Saved transactions.json")

    with open('data/precomputed_roi.json', 'w') as f:
        json.dump(precomputed_roi, f, indent=2)
    print("   ✅ Saved precomputed_roi.json")

    with open('data/feature_importance.json', 'w') as f:
        json.dump(feature_importance, f, indent=2)
    print("   ✅ Saved feature_importance.json")

    with open('data/competitors.json', 'w') as f:
        json.dump(competitors, f, indent=2)
    print("   ✅ Saved competitors.json")

    with open('data/historical_examples.json', 'w') as f:
        json.dump(historical_examples, f, indent=2)
    print("   ✅ Saved historical_examples.json")

    # Print summary
    print("\n" + "=" * 60)
    print("✨ DATA GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   • Products: {len(products)}")
    print(f"   • Locations: {len(locations)}")
    print(f"   • Sales Records: {len(sales_history):,}")
    print(f"   • Transactions: {len(transactions):,}")
    print(f"   • ROI Combinations: {len(precomputed_roi)}")
    print(f"   • Competitor Products: {len(competitors)}")
    print(f"   • Historical Examples: {len(historical_examples)}")
    print(f"\n✅ All data files saved to data/ directory")


if __name__ == '__main__':
    main()
