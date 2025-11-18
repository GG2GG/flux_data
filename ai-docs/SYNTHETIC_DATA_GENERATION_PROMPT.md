# Synthetic Data Generation Prompt for Retail Product Placement System

## Overview
Generate realistic synthetic retail sales data for a product placement recommendation system. The data should simulate a real grocery store with multiple product categories, shelf locations, and sales patterns.

---

## 📦 Data Files to Generate

You need to create **3 interconnected CSV/JSON files**:

1. **products.json** - Product catalog with metadata
2. **locations.json** - Store shelf locations with zone information
3. **sales_history.csv** - Sales transactions linking products to locations

---

## 1️⃣ Products Catalog (`products.json`)

**Format:** JSON array of product objects

**Requirements:**
- Generate **50-100 products** across 5 categories
- Each product must have realistic pricing and margins
- Include mix of price tiers (budget, standard, premium)

**Schema:**
```json
[
  {
    "product_id": "P001",
    "sku": "SKU-BEV-0001",
    "name": "Premium Energy Drink",
    "category": "Beverages",
    "subcategory": "Energy Drinks",
    "price": 3.50,
    "cost": 1.93,
    "margin": 1.57,
    "margin_pct": 45.0,
    "brand": "Brand A",
    "lifecycle_stage": "mature",
    "price_tier": "premium",
    "notes": "High-performance energy drink"
  }
]
```

**Field Guidelines:**

| Field | Type | Description | Valid Values |
|-------|------|-------------|--------------|
| `product_id` | string | Unique ID | P001, P002, ... P100 |
| `sku` | string | Stock keeping unit | SKU-CAT-#### |
| `name` | string | Product name | Descriptive, realistic |
| `category` | string | **REQUIRED** Product category | Beverages, Snacks, Dairy, Bakery, Personal Care |
| `subcategory` | string | More specific category | Energy Drinks, Chips, Milk, etc. |
| `price` | float | Retail price (USD) | $0.50 - $15.00 (realistic) |
| `cost` | float | Cost to retailer | 50-70% of price |
| `margin` | float | Profit per unit | price - cost |
| `margin_pct` | float | Margin percentage | 25-50% typical |
| `brand` | string | Brand name | Brand A, Brand B, etc. |
| `lifecycle_stage` | string | Product maturity | new, growth, mature, decline |
| `price_tier` | string | Price positioning | budget, standard, premium |
| `notes` | string | Optional description | Any relevant notes |

**Category Distribution (suggested):**
- Beverages: 25-30 products (soft drinks, energy drinks, juices, water)
- Snacks: 20-25 products (chips, candy, cookies, crackers)
- Dairy: 15-20 products (milk, yogurt, cheese)
- Bakery: 10-15 products (bread, pastries, muffins)
- Personal Care: 10-15 products (soap, shampoo, toothpaste)

**Price Tier Distribution:**
- Budget: 30% (price < $2.00)
- Standard: 50% (price $2.00-$5.00)
- Premium: 20% (price > $5.00)

---

## 2️⃣ Store Locations (`locations.json`)

**Format:** JSON array of location objects

**Requirements:**
- Generate **15-25 shelf locations** across different zone types
- Include high-traffic premium zones (endcaps, checkout) and regular shelving
- Zone types must match placement cost configuration

**Schema:**
```json
[
  {
    "location_id": "L001",
    "zone_name": "End Cap 1 - Beverages",
    "zone_type": "End Cap",
    "primary_category": "Beverages",
    "traffic_level": "high",
    "traffic_index": 250,
    "visibility_factor": 1.5,
    "square_footage": 100,
    "display_type": "endcap_display",
    "base_placement_cost": 2000,
    "notes": "Premium end-cap location in beverages section"
  }
]
```

**Field Guidelines:**

| Field | Type | Description | Valid Values |
|-------|------|-------------|--------------|
| `location_id` | string | Unique ID | L001, L002, ... L025 |
| `zone_name` | string | Descriptive location name | "End Cap 1 - Beverages" |
| `zone_type` | string | **REQUIRED** Zone category | See zone types below |
| `primary_category` | string | Main product category | Beverages, Snacks, Dairy, etc. |
| `traffic_level` | string | Foot traffic level | high, medium, low |
| `traffic_index` | integer | Traffic score | 50-300 (100 = average) |
| `visibility_factor` | float | Visibility multiplier | 0.7-1.8 |
| `square_footage` | integer | Display area (sq ft) | 50-200 |
| `display_type` | string | Display format | endcap, shelf, cooler, checkout |
| `base_placement_cost` | integer | Monthly cost (USD) | 500-2500 |
| `notes` | string | Optional description | Location details |

**Zone Types (MUST USE THESE EXACT VALUES):**
- **"End Cap"** - High visibility end-of-aisle displays (8-12% of locations)
- **"Checkout"** - Checkout lane impulse buy zones (8-12% of locations)
- **"Eye Level"** - Eye-level shelf space (25-35% of locations)
- **"Regular Shelf"** - Standard shelf space (30-40% of locations)
- **"Bottom Shelf"** - Lower shelf space (10-15% of locations)
- **"Top Shelf"** - Upper shelf space (5-10% of locations)

**Traffic Index Guidelines:**
- High traffic (200-300): End caps, checkout, main entrance
- Medium traffic (120-200): Eye level, main aisles
- Low traffic (50-120): Bottom/top shelves, back of store

**Base Placement Cost Guidelines:**
- End Cap: $2000-2500/month
- Checkout: $1500-2000/month
- Eye Level: $1000-1500/month
- Regular Shelf: $800-1200/month
- Bottom/Top Shelf: $500-800/month

---

## 3️⃣ Sales History (`sales_history.csv`)

**Format:** CSV file

**Requirements:**
- Generate **5,000-10,000 transaction records** spanning 12 months
- Each product should appear in multiple locations
- Sales should reflect realistic patterns based on zone performance and promotions
- Include seasonal variations and promotional effects

**Schema:**
```csv
product_id,location_id,product_name,category,zone_type,month,year,week_date,units_sold,revenue,base_price,was_promoted,promotion_discount_pct
P001,L001,"Premium Energy Drink",Beverages,End Cap,11,2024,2024-11-22,388,1358.0,3.50,False,0
P001,L002,"Premium Energy Drink",Beverages,Checkout,11,2024,2024-11-22,125,437.5,3.50,False,0
P001,L003,"Premium Energy Drink",Beverages,Eye Level,11,2024,2024-11-22,457,1439.55,3.50,True,15
```

**Field Guidelines:**

| Field | Type | Description | Valid Values |
|-------|------|-------------|--------------|
| `product_id` | string | **REQUIRED** Product ID | Must match products.json |
| `location_id` | string | **REQUIRED** Location ID | Must match locations.json |
| `product_name` | string | **REQUIRED** Product name | From products.json |
| `category` | string | **REQUIRED** Product category | From products.json |
| `zone_type` | string | **REQUIRED** Shelf zone | From locations.json |
| `month` | integer | Month number | 1-12 |
| `year` | integer | Year | 2024 |
| `week_date` | string | Week starting date | YYYY-MM-DD format |
| `units_sold` | integer | Units sold that week | 10-500 (varies by zone) |
| `revenue` | float | Total revenue | units_sold × effective_price |
| `base_price` | float | Regular price | From products.json |
| `was_promoted` | boolean | Promotion flag | True/False |
| `promotion_discount_pct` | float | Discount percentage | 0-25% if promoted |

**Sales Pattern Guidelines:**

1. **Zone-Based Performance Multipliers:**
   ```
   End Cap: 1.8-2.5x baseline sales
   Checkout: 1.6-2.2x baseline sales (impulse buys)
   Eye Level: 1.2-1.5x baseline sales
   Regular Shelf: 1.0x baseline sales
   Bottom Shelf: 0.6-0.8x baseline sales
   Top Shelf: 0.7-0.9x baseline sales
   ```

2. **Promotional Lift:**
   - Promoted items: +50-100% units sold
   - Promotion rate: 15-25% of all records
   - Discount range: 10-25% off base price

3. **Baseline Sales by Category (units/week):**
   - Beverages: 50-300 units
   - Snacks: 40-250 units
   - Dairy: 30-200 units
   - Bakery: 20-150 units
   - Personal Care: 15-100 units

4. **Seasonal Patterns:**
   - Beverages: Higher in summer (Jun-Aug)
   - Snacks: Higher in winter holidays (Nov-Dec)
   - Dairy/Bakery: Steady year-round
   - Personal Care: Slight peaks in Jan, Jul

5. **Data Distribution:**
   - Each product should appear in 3-8 different locations
   - Each location should have 30-60 different products over the year
   - Weekly snapshots: Generate 1 record per product-location combo per week
   - Time range: 52 weeks (full year)

---

## 🎯 Realism Requirements

To ensure data quality for the ML system:

1. **Correlations:**
   - Higher-priced products → lower units but higher revenue
   - Premium zones (End Cap, Checkout) → consistently higher sales
   - Promoted products → significant lift in units sold
   - Category matching (e.g., Beverages perform best in beverage-focused locations)

2. **Variability:**
   - Add realistic noise: ±10-20% random variation in sales
   - Not all products succeed in premium zones (simulate some underperformers)
   - Some budget products can outsell premium in certain zones

3. **Business Logic:**
   - Revenue = units_sold × (base_price × (1 - promotion_discount_pct/100))
   - Promoted items: discount 10-25%, apply to 15-25% of records
   - No negative values for any numeric field

4. **Data Quality:**
   - No missing values in required fields
   - All IDs must be valid references
   - Dates should be realistic and sequential
   - Prices should be reasonable for retail

---

## 📊 Example Output Structure

```
data/input/
├── products.json          # 50-100 products
├── locations.json         # 15-25 locations
└── sales_history.csv      # 5,000-10,000 transactions
```

---

## ✅ Validation Checklist

After generation, verify:

- [ ] All product_ids in sales_history exist in products.json
- [ ] All location_ids in sales_history exist in locations.json
- [ ] All categories match between products and sales
- [ ] All zone_types use exact values from the list above
- [ ] Sales patterns show clear zone-based performance differences
- [ ] Promotional items show visible sales lift
- [ ] Revenue calculations are accurate (units × price)
- [ ] Date range covers 12 months of weekly data
- [ ] No duplicate product_id-location_id-week_date combinations
- [ ] Realistic value ranges (no $100 candy bars or 10,000 units/week for niche items)

---

## 💡 Output Format

Please generate:

1. **products.json** - Pretty-printed JSON with 2-space indentation
2. **locations.json** - Pretty-printed JSON with 2-space indentation
3. **sales_history.csv** - CSV with headers, no quotes unless necessary

Make the data realistic, statistically sound, and suitable for training a product placement recommendation system.
