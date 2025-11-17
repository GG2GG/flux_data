# Agent Pipeline Documentation

## Overview

This document provides comprehensive documentation of the multi-agent pipeline for the Retail Product Placement system. It details the flow of data through six specialized agents, including complete input/output state specifications for each agent.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                 │
│  Product Details + Business Requirements                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  AGENT 1: INPUT ORCHESTRATOR                                         │
│  Role: Validate input, initialize session state                      │
│  Input: ProductInput                                                 │
│  Output: PlacementState (initialized)                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  AGENT 2: DATA MINING & FEATURE ENGINEERING                          │
│  Role: Extract historical patterns, engineer features                │
│  Input: PlacementState (with product info)                           │
│  Output: PlacementState + historical_patterns + features_by_location │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  AGENT 3: ROI PREDICTION     │  │  AGENT 4: MARKET BASKET      │
│  Role: Predict ROI scores    │  │  ANALYSIS                    │
│  with XGBoost                │  │  Role: Calculate product     │
│  Input: Features             │  │  affinity scores             │
│  Output: ROI predictions +   │  │  Input: Features + product   │
│  confidence intervals        │  │  Output: Affinity scores +   │
│                              │  │  complementary products      │
└──────────────┬───────────────┘  └───────────┬──────────────────┘
               │                              │
               │    (Parallel Execution)      │
               │                              │
               └──────────────┬───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  AGENT 5: RECOMMENDATION SYNTHESIZER                                 │
│  Role: Combine ROI + affinity, rank locations                        │
│  Input: ROI predictions + affinity analysis                          │
│  Output: Final ranked recommendations                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  AGENT 6: EXPLANATION & DEFENSE                                      │
│  Role: Generate SHAP explanations, retrieve evidence                 │
│  Input: Final recommendations + all context                          │
│  Output: Complete explanation package                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FINAL OUTPUT                                 │
│  Recommendations + Explanations + Session ID                         │
└─────────────────────────────────────────────────────────────────────┘
```

## Execution Flow

- **Sequential**: Input → Data Mining → Synthesizer → Explanation
- **Parallel**: Data Mining → (ROI Prediction || Market Basket) → Synthesizer
- **State Management**: LangGraph StateGraph with shared PlacementState
- **Error Handling**: Each agent appends errors to state.errors list

---

## State Schema

### PlacementState (Root State Object)

The complete state object that flows through all agents:

```python
from typing import TypedDict, Annotated, List, Dict, Any, Tuple
import operator
from datetime import datetime

class PlacementState(TypedDict):
    # Core product information
    product: ProductInput                      # Original user input

    # Session metadata
    timestamp: datetime                        # Request timestamp
    session_id: str                            # Unique session identifier

    # Agent 2 outputs
    historical_patterns: Dict[str, Any]        # Historical insights
    features_by_location: Dict[str, Dict]      # Engineered features per location

    # Agent 3 outputs
    roi_predictions: Dict[str, Dict]           # ROI scores by location
    roi_explanations: Dict[str, List]          # SHAP values by location

    # Agent 4 outputs
    affinity_analysis: Dict[str, Dict]         # Affinity scores by location

    # Agent 5 outputs
    final_recommendations: Dict[str, float]    # Location → ROI mapping
    detailed_scores: Dict[str, Dict]           # Full scoring breakdown

    # Agent 6 outputs
    explanation: Dict[str, Any]                # Complete explanation package

    # Error tracking
    errors: Annotated[List[str], operator.add] # Accumulated errors
```

---

## Agent 1: Input Orchestrator

### Purpose
Validates user input, initializes session state, and performs business rule checks before routing to analysis agents.

### Responsibilities
- Validate product details (price > 0, budget > 0, etc.)
- Initialize PlacementState with metadata
- Perform sanity checks on business requirements
- Log request for auditing

### Tools Used
- Pydantic validation
- UUID generation
- Logging framework

### Input Schema

```python
class ProductInput(BaseModel):
    product_name: str                # Name of the product
    category: str                    # Product category (Beverages, Snacks, etc.)
    price: float                     # Product price ($)
    budget: float                    # Available placement budget ($)
    target_sales: int                # Target units to sell
    target_customers: str            # Target customer segment description
    expected_roi: float              # Business owner's ROI expectation
```

### Input Example

```json
{
  "product_name": "Premium Energy Drink",
  "category": "Beverages",
  "price": 2.99,
  "budget": 5000.00,
  "target_sales": 1000,
  "target_customers": "Young adults 18-35, fitness enthusiasts",
  "expected_roi": 1.5
}
```

### Processing Logic

```python
def execute(self, product_input: ProductInput) -> PlacementState:
    # 1. Validation
    if product_input.budget <= 0:
        raise ValueError("Budget must be positive")

    if product_input.price <= 0:
        raise ValueError("Price must be positive")

    if product_input.target_sales <= 0:
        raise ValueError("Target sales must be positive")

    # 2. Business rule checks
    if product_input.expected_roi <= 0:
        raise ValueError("Expected ROI must be positive")

    # Warn if expectations seem unrealistic
    if product_input.expected_roi > 3.0:
        warnings.append("Expected ROI >3.0 is ambitious for most retail placements")

    # 3. Initialize state
    state = PlacementState(
        product=product_input,
        timestamp=datetime.now(),
        session_id=str(uuid.uuid4()),
        errors=[]
    )

    # 4. Log
    logger.info(f"Session {state['session_id']}: Processing {product_input.product_name}")

    return state
```

### Output Schema

```python
PlacementState {
    product: ProductInput,
    timestamp: datetime,
    session_id: str,
    errors: List[str]
}
```

### Output Example

```json
{
  "product": {
    "product_name": "Premium Energy Drink",
    "category": "Beverages",
    "price": 2.99,
    "budget": 5000.00,
    "target_sales": 1000,
    "target_customers": "Young adults 18-35, fitness enthusiasts",
    "expected_roi": 1.5
  },
  "timestamp": "2025-11-17T10:30:45.123456",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "errors": []
}
```

### Error Handling

```python
# Validation errors → raise ValueError immediately
# Business warnings → append to state.errors but continue
# System errors → append to state.errors and return partial state
```

---

## Agent 2: Data Mining & Feature Engineering

### Purpose
Queries historical sales data, extracts patterns, and engineers 20+ features for each location to feed ML models.

### Responsibilities
- Query historical sales for similar products
- Analyze seasonal patterns (SARIMA-based)
- Calculate location performance metrics
- Extract category insights
- Engineer features for each location
- Compute baseline statistics

### Tools Used
- Database queries (SQLAlchemy)
- Pandas for data aggregation
- Feature engineering pipeline
- Statistical analysis (seasonality decomposition)

### Input Schema

```python
PlacementState {
    product: ProductInput,
    timestamp: datetime,
    session_id: str,
    errors: List[str]
}
```

### Input Example

```json
{
  "product": {
    "product_name": "Premium Energy Drink",
    "category": "Beverages",
    "price": 2.99,
    "budget": 5000.00
  },
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Processing Logic

```python
def execute(self, state: PlacementState) -> PlacementState:
    product = state['product']

    # 1. Query historical sales
    historical_sales = self.db.query(
        """
        SELECT product_id, location_id, week_date, units_sold, revenue
        FROM sales_history
        WHERE category = ? AND price BETWEEN ? AND ?
        ORDER BY week_date DESC
        LIMIT 10000
        """,
        product.category,
        product.price * 0.8,
        product.price * 1.2
    )

    # 2. Extract patterns
    patterns = {
        'seasonal_trends': self._extract_seasonality(historical_sales),
        'location_performance': self._analyze_locations(historical_sales),
        'category_insights': self._analyze_category(product.category),
        'price_tier_stats': self._analyze_price_tier(product.price)
    }

    # 3. Engineer features for each location
    locations = self.db.query("SELECT * FROM locations")
    features_by_location = {}

    for location in locations:
        features = self.feature_engineer.create_features(
            product=product,
            location=location,
            historical_data=historical_sales,
            patterns=patterns
        )
        features_by_location[location.zone_name] = features

    # 4. Update state
    state['historical_patterns'] = patterns
    state['features_by_location'] = features_by_location

    return state
```

### Feature Engineering Details

**20 Features Generated per Location:**

1. **location_velocity**: Average units sold per week in this location
2. **category_location_fit**: Historical performance of this category in location
3. **price_tier**: Encoded (0=budget, 1=mid, 2=premium)
4. **traffic_level**: Encoded (0=low, 1=medium, 2=high)
5. **zone_type**: One-hot encoded (end_cap, eye_level, checkout, regular)
6. **seasonality_month**: Current month encoding (1-12)
7. **seasonality_quarter**: Current quarter (1-4)
8. **is_holiday_season**: Boolean (Nov-Dec = 1)
9. **product_lifecycle**: Encoded (0=new, 1=growth, 2=mature, 3=decline)
10. **margin_percentage**: (price - cost) / price
11. **basket_lift_score**: Affinity score from MBA (computed by Agent 4)
12. **complementary_product_count**: Number of high-affinity products in location
13. **competitor_proximity_score**: Weighted distance to competitors
14. **historical_category_roi**: Avg ROI for category in location (past 12 months)
15. **price_elasticity**: Category-specific elasticity coefficient
16. **inventory_turnover_rate**: How fast products sell in this location
17. **promotion_frequency**: Historical promotion rate in location
18. **cross_sell_potential**: Likelihood of driving additional purchases
19. **brand_strength_index**: Brand recognition score (0-1)
20. **trend_direction**: Encoded (-1=declining, 0=stable, 1=growing)

### Output Schema

```python
PlacementState {
    product: ProductInput,
    timestamp: datetime,
    session_id: str,

    # NEW FIELDS ADDED:
    historical_patterns: {
        seasonal_trends: Dict[str, float],
        location_performance: Dict[str, float],
        category_insights: Dict[str, Any],
        price_tier_stats: Dict[str, float]
    },

    features_by_location: {
        [location_name: str]: {
            location_velocity: float,
            category_location_fit: float,
            price_tier: int,
            traffic_level: int,
            zone_type_end_cap: int,
            zone_type_eye_level: int,
            zone_type_checkout: int,
            zone_type_regular: int,
            seasonality_month: int,
            seasonality_quarter: int,
            is_holiday_season: int,
            product_lifecycle: int,
            margin_percentage: float,
            basket_lift_score: float,
            complementary_product_count: int,
            competitor_proximity_score: float,
            historical_category_roi: float,
            price_elasticity: float,
            inventory_turnover_rate: float,
            promotion_frequency: float,
            cross_sell_potential: float,
            brand_strength_index: float,
            trend_direction: int
        }
    },

    errors: List[str]
}
```

### Output Example

```json
{
  "product": { "product_name": "Premium Energy Drink", "category": "Beverages" },
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",

  "historical_patterns": {
    "seasonal_trends": {
      "summer_boost": 1.25,
      "winter_decline": 0.85,
      "holiday_spike": 1.40
    },
    "location_performance": {
      "Main Entrance": 1.15,
      "Checkout": 1.40,
      "Beverage Isle": 1.10,
      "End Cap 1": 2.00
    },
    "category_insights": {
      "avg_roi": 1.32,
      "best_locations": ["End Cap 1", "Checkout", "Main Entrance"],
      "seasonality_strength": 0.35
    },
    "price_tier_stats": {
      "tier": "premium",
      "avg_velocity": 85.5,
      "elasticity": -0.5
    }
  },

  "features_by_location": {
    "Main Entrance": {
      "location_velocity": 120.5,
      "category_location_fit": 0.82,
      "price_tier": 2,
      "traffic_level": 2,
      "zone_type_end_cap": 0,
      "zone_type_eye_level": 0,
      "zone_type_checkout": 0,
      "zone_type_regular": 1,
      "seasonality_month": 11,
      "seasonality_quarter": 4,
      "is_holiday_season": 1,
      "product_lifecycle": 1,
      "margin_percentage": 0.45,
      "basket_lift_score": 0.0,
      "complementary_product_count": 8,
      "competitor_proximity_score": 0.65,
      "historical_category_roi": 1.35,
      "price_elasticity": -0.5,
      "inventory_turnover_rate": 12.5,
      "promotion_frequency": 0.15,
      "cross_sell_potential": 0.72,
      "brand_strength_index": 0.80,
      "trend_direction": 1
    },
    "Checkout": {
      "location_velocity": 95.2,
      "category_location_fit": 0.75,
      "price_tier": 2,
      "traffic_level": 2,
      "zone_type_end_cap": 0,
      "zone_type_eye_level": 0,
      "zone_type_checkout": 1,
      "zone_type_regular": 0,
      "seasonality_month": 11,
      "seasonality_quarter": 4,
      "is_holiday_season": 1,
      "product_lifecycle": 1,
      "margin_percentage": 0.45,
      "basket_lift_score": 0.0,
      "complementary_product_count": 12,
      "competitor_proximity_score": 0.45,
      "historical_category_roi": 1.42,
      "price_elasticity": -0.5,
      "inventory_turnover_rate": 15.8,
      "promotion_frequency": 0.05,
      "cross_sell_potential": 0.88,
      "brand_strength_index": 0.80,
      "trend_direction": 1
    }
    // ... 8 more locations
  },

  "errors": []
}
```

### Error Handling

```python
# Missing historical data → use category averages, add warning
# Database errors → append to errors, use cached/default features
# Feature calculation errors → log warning, use median imputation
```

---

## Agent 3: ROI Prediction Agent

### Purpose
Predicts ROI scores for each location using the XGBoost model and generates confidence intervals.

### Responsibilities
- Transform features to model input format
- Run XGBoost predictions for all locations
- Calculate confidence intervals (80% CI using quantile regression)
- Apply budget constraints
- Rank locations by predicted ROI
- Generate SHAP values for explainability

### Tools Used
- XGBoost model (pre-trained)
- SHAP TreeExplainer
- NumPy for numerical operations

### Input Schema

```python
PlacementState {
    product: ProductInput,
    features_by_location: Dict[str, Dict[str, float]],
    // ... other fields
}
```

### Input Example

```json
{
  "product": { "price": 2.99, "budget": 5000.00 },
  "features_by_location": {
    "Main Entrance": {
      "location_velocity": 120.5,
      "category_location_fit": 0.82,
      // ... 18 more features
    }
  }
}
```

### Processing Logic

```python
def execute(self, state: PlacementState) -> PlacementState:
    product = state['product']
    features_by_location = state['features_by_location']

    predictions = {}
    explanations = {}

    for location, features in features_by_location.items():
        # 1. Prepare feature vector (20 features in correct order)
        X = self._prepare_features(features)

        # 2. Predict ROI
        roi_pred = self.model.predict(X)[0]

        # 3. Calculate confidence intervals (quantile regression)
        lower = self._predict_quantile(X, 0.10)[0]  # 10th percentile
        upper = self._predict_quantile(X, 0.90)[0]  # 90th percentile

        # 4. Check budget constraint
        placement_cost = self._estimate_placement_cost(location)
        if placement_cost > product.budget:
            continue  # Skip locations over budget

        # 5. Generate SHAP values for this prediction
        shap_values = self.explainer.shap_values(X)

        # Store prediction
        predictions[location] = {
            'roi': float(roi_pred),
            'confidence_interval': (float(lower), float(upper)),
            'confidence_level': 0.80,
            'placement_cost': placement_cost
        }

        # Store SHAP explanation
        explanations[location] = [
            {
                'feature': feature_name,
                'shap_value': float(shap_val),
                'feature_value': float(features[feature_name])
            }
            for feature_name, shap_val in zip(self.feature_names, shap_values[0])
        ]

    # 6. Rank by ROI
    ranked = sorted(predictions.items(), key=lambda x: x[1]['roi'], reverse=True)

    # 7. Update state
    state['roi_predictions'] = dict(ranked)
    state['roi_explanations'] = explanations

    return state
```

### Budget Constraint Logic

```python
def _estimate_placement_cost(self, location: str) -> float:
    """Estimate cost based on location type and duration"""

    # Base costs by zone type
    base_costs = {
        'End Cap': 2000,     # Premium placement
        'Checkout': 1500,    # High impulse area
        'Eye Level': 1000,   # Optimal visibility
        'Main Entrance': 1200,
        'Regular Shelf': 500
    }

    zone_type = self._get_zone_type(location)
    base_cost = base_costs.get(zone_type, 800)

    # Assume 4-week placement period
    weeks = 4

    return base_cost * weeks
```

### Output Schema

```python
PlacementState {
    // ... previous fields

    # NEW FIELDS ADDED:
    roi_predictions: {
        [location_name: str]: {
            roi: float,                        # Predicted ROI (1.4 = 140% return)
            confidence_interval: Tuple[float, float],  # (lower, upper) 80% CI
            confidence_level: float,           # 0.80 for 80% confidence
            placement_cost: float              # Estimated cost ($)
        }
    },

    roi_explanations: {
        [location_name: str]: List[{
            feature: str,                      # Feature name
            shap_value: float,                 # SHAP contribution to prediction
            feature_value: float               # Actual feature value
        }]
    }
}
```

### Output Example

```json
{
  "product": { "product_name": "Premium Energy Drink" },
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",

  "roi_predictions": {
    "Main Entrance": {
      "roi": 1.42,
      "confidence_interval": [1.25, 1.58],
      "confidence_level": 0.80,
      "placement_cost": 4800
    },
    "Checkout": {
      "roi": 1.38,
      "confidence_interval": [1.22, 1.54],
      "confidence_level": 0.80,
      "placement_cost": 6000
    },
    "Beverage Isle": {
      "roi": 1.25,
      "confidence_interval": [1.10, 1.40],
      "confidence_level": 0.80,
      "placement_cost": 2000
    },
    "End Cap 1": {
      "roi": 1.65,
      "confidence_interval": [1.45, 1.85],
      "confidence_level": 0.80,
      "placement_cost": 8000
    }
  },

  "roi_explanations": {
    "Main Entrance": [
      { "feature": "location_velocity", "shap_value": 0.35, "feature_value": 120.5 },
      { "feature": "category_location_fit", "shap_value": 0.28, "feature_value": 0.82 },
      { "feature": "is_holiday_season", "shap_value": 0.22, "feature_value": 1.0 },
      { "feature": "traffic_level", "shap_value": 0.18, "feature_value": 2.0 },
      { "feature": "brand_strength_index", "shap_value": 0.15, "feature_value": 0.80 },
      // ... 15 more features with smaller SHAP values
    ]
  },

  "errors": []
}
```

### SHAP Value Interpretation

- **Positive SHAP value**: Feature increases predicted ROI
- **Negative SHAP value**: Feature decreases predicted ROI
- **Magnitude**: Larger absolute value = stronger influence

Example:
```
shap_value: 0.35 for location_velocity
→ This feature contributes +0.35 to the ROI prediction
→ High location velocity is boosting the ROI score
```

### Error Handling

```python
# Model prediction errors → use median ROI, add to errors
# SHAP calculation fails → use feature importance instead
# Budget exceeded for all locations → return error message
```

---

## Agent 4: Market Basket Analysis Agent

### Purpose
Analyzes product affinity patterns using FP-Growth algorithm and scores locations based on complementary product presence.

### Responsibilities
- Run FP-Growth on historical transaction data
- Identify complementary products (high lift scores)
- Calculate affinity scores for each location
- Provide cross-selling insights

### Tools Used
- mlxtend FP-Growth algorithm
- Pandas for transaction processing
- Association rule mining

### Input Schema

```python
PlacementState {
    product: ProductInput,
    features_by_location: Dict[str, Dict],
    // ... other fields
}
```

### Input Example

```json
{
  "product": {
    "product_name": "Premium Energy Drink",
    "category": "Beverages"
  },
  "features_by_location": {
    "Main Entrance": { /* features */ }
  }
}
```

### Processing Logic

```python
def execute(self, state: PlacementState) -> PlacementState:
    product = state['product']

    # 1. Find complementary products using FP-Growth
    # Run on pre-computed association rules (trained offline)
    complementary = self.affinity.get_complementary_products(
        product_category=product.category,
        price_range=(product.price * 0.8, product.price * 1.2)
    )

    # 2. Score each location based on complementary product presence
    affinity_scores = {}

    for location in state['features_by_location'].keys():
        # Get products currently in this location
        location_products = self.db.query(
            """
            SELECT product_id, category, price
            FROM current_placements
            WHERE location_id = ?
            """,
            location
        )

        # Calculate affinity score
        score = 0.0
        matching_products = []

        for comp_product in complementary:
            # Check if complementary product is in this location
            if comp_product['product_id'] in location_products:
                lift = comp_product['lift']
                score += max(0, lift - 1.0)  # Only positive affinity
                matching_products.append(comp_product)

        # Normalize by number of location products
        if len(location_products) > 0:
            score = score / len(location_products)

        affinity_scores[location] = {
            'affinity_score': score,
            'complementary_products': complementary[:5],  # Top 5
            'matching_products': matching_products,
            'cross_sell_potential': min(1.0, score * 0.5)  # Cap at 1.0
        }

    # 3. Update state
    state['affinity_analysis'] = affinity_scores

    return state
```

### FP-Growth Details

**Association Rule Metrics:**

- **Support**: P(A ∩ B) - How often items appear together
- **Confidence**: P(B|A) - When A is purchased, probability of B
- **Lift**: P(B|A) / P(B) - How much more likely B is purchased with A
  - Lift > 1: Positive association (complementary)
  - Lift = 1: Independent
  - Lift < 1: Negative association (substitutes)

**Example Rules:**
```
{Energy Drink, Chips} → Lift: 2.5 (250% more likely together)
{Energy Drink, Protein Bar} → Lift: 3.2
{Energy Drink, Coffee} → Lift: 0.4 (substitutes)
```

### Output Schema

```python
PlacementState {
    // ... previous fields

    # NEW FIELD ADDED:
    affinity_analysis: {
        [location_name: str]: {
            affinity_score: float,                    # Composite affinity score
            complementary_products: List[{            # Top 5 complementary items
                product_name: str,
                category: str,
                lift: float,
                confidence: float,
                support: float
            }],
            matching_products: List[{                 # Complementary items in location
                product_name: str,
                lift: float
            }],
            cross_sell_potential: float               # 0-1 score
        }
    }
}
```

### Output Example

```json
{
  "product": { "product_name": "Premium Energy Drink" },
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",

  "affinity_analysis": {
    "Main Entrance": {
      "affinity_score": 0.68,
      "complementary_products": [
        {
          "product_name": "Protein Bar - Chocolate",
          "category": "Snacks",
          "lift": 3.2,
          "confidence": 0.45,
          "support": 0.08
        },
        {
          "product_name": "Sports Drink - Lemon",
          "category": "Beverages",
          "lift": 2.8,
          "confidence": 0.38,
          "support": 0.12
        },
        {
          "product_name": "Trail Mix",
          "category": "Snacks",
          "lift": 2.5,
          "confidence": 0.35,
          "support": 0.06
        },
        {
          "product_name": "Granola Bar",
          "category": "Snacks",
          "lift": 2.3,
          "confidence": 0.40,
          "support": 0.09
        },
        {
          "product_name": "Bottled Water",
          "category": "Beverages",
          "lift": 1.8,
          "confidence": 0.55,
          "support": 0.20
        }
      ],
      "matching_products": [
        { "product_name": "Protein Bar - Chocolate", "lift": 3.2 },
        { "product_name": "Granola Bar", "lift": 2.3 }
      ],
      "cross_sell_potential": 0.34
    },

    "Checkout": {
      "affinity_score": 0.82,
      "complementary_products": [ /* same top 5 */ ],
      "matching_products": [
        { "product_name": "Protein Bar - Chocolate", "lift": 3.2 },
        { "product_name": "Trail Mix", "lift": 2.5 },
        { "product_name": "Granola Bar", "lift": 2.3 }
      ],
      "cross_sell_potential": 0.41
    },

    "Beverage Isle": {
      "affinity_score": 0.45,
      "complementary_products": [ /* same top 5 */ ],
      "matching_products": [
        { "product_name": "Sports Drink - Lemon", "lift": 2.8 }
      ],
      "cross_sell_potential": 0.23
    }
    // ... more locations
  },

  "errors": []
}
```

### Affinity Score Calculation

```python
def calculate_affinity_score(complementary_products, location_products):
    """
    Score = Σ(lift - 1) for matching products / total location products

    Higher score = more complementary products already in location
    → Better cross-selling opportunity
    """
    score = 0.0
    for comp in complementary_products:
        if comp['product_id'] in location_products:
            score += max(0, comp['lift'] - 1.0)

    return score / len(location_products) if location_products else 0.0
```

### Error Handling

```python
# FP-Growth fails → use pre-computed rules, add warning
# No complementary products found → affinity_score = 0, continue
# Database query errors → use empty location_products list
```

---

## Agent 5: Recommendation Synthesizer

### Purpose
Combines ROI predictions and affinity analysis to produce final ranked recommendations applying multi-objective optimization.

### Responsibilities
- Aggregate ROI and affinity scores
- Apply weighted combination (70% ROI, 30% affinity)
- Rank locations by combined score
- Select top 5 recommendations
- Format output per specification

### Tools Used
- NumPy for scoring calculations
- Sorting and ranking algorithms

### Input Schema

```python
PlacementState {
    product: ProductInput,
    roi_predictions: Dict[str, Dict],
    affinity_analysis: Dict[str, Dict],
    // ... other fields
}
```

### Input Example

```json
{
  "roi_predictions": {
    "Main Entrance": { "roi": 1.42 },
    "Checkout": { "roi": 1.38 }
  },
  "affinity_analysis": {
    "Main Entrance": { "affinity_score": 0.68 },
    "Checkout": { "affinity_score": 0.82 }
  }
}
```

### Processing Logic

```python
def execute(self, state: PlacementState) -> PlacementState:
    roi_predictions = state['roi_predictions']
    affinity_analysis = state['affinity_analysis']
    product = state['product']

    # Multi-objective scoring
    final_scores = {}

    for location in roi_predictions.keys():
        # Get ROI score
        roi_score = roi_predictions[location]['roi']

        # Get affinity score (default 0 if missing)
        affinity_score = affinity_analysis.get(location, {}).get('affinity_score', 0.0)

        # Weighted combination: 70% ROI, 30% affinity
        combined_score = 0.7 * roi_score + 0.3 * affinity_score

        final_scores[location] = {
            'combined_score': combined_score,
            'roi': roi_score,
            'affinity': affinity_score,
            'confidence_interval': roi_predictions[location]['confidence_interval'],
            'placement_cost': roi_predictions[location]['placement_cost']
        }

    # Rank by combined score
    ranked = sorted(
        final_scores.items(),
        key=lambda x: x[1]['combined_score'],
        reverse=True
    )

    # Select top 5
    top_5 = dict(ranked[:5])

    # Format output as {location: roi} per specification
    output_format = {
        location: scores['roi']
        for location, scores in top_5.items()
    }

    # Update state
    state['final_recommendations'] = output_format
    state['detailed_scores'] = top_5

    return state
```

### Multi-Objective Optimization

**Weighting Rationale:**
- **70% ROI**: Primary objective is financial return
- **30% Affinity**: Secondary objective is cross-selling potential

**Formula:**
```
Combined Score = 0.7 × ROI + 0.3 × Affinity Score

Example:
Location A: ROI=1.4, Affinity=0.8 → Combined = 0.7×1.4 + 0.3×0.8 = 0.98 + 0.24 = 1.22
Location B: ROI=1.5, Affinity=0.2 → Combined = 0.7×1.5 + 0.3×0.2 = 1.05 + 0.06 = 1.11

→ Location A wins despite lower ROI due to better cross-sell potential
```

### Output Schema

```python
PlacementState {
    // ... previous fields

    # NEW FIELDS ADDED:
    final_recommendations: {
        [location_name: str]: float              # ROI score (output format)
    },

    detailed_scores: {
        [location_name: str]: {
            combined_score: float,               # Multi-objective score
            roi: float,                          # ROI contribution
            affinity: float,                     # Affinity contribution
            confidence_interval: Tuple[float, float],
            placement_cost: float
        }
    }
}
```

### Output Example

```json
{
  "product": { "product_name": "Premium Energy Drink" },
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",

  "final_recommendations": {
    "Main Entrance": 1.42,
    "Checkout": 1.38,
    "End Cap 1": 1.65,
    "Beverage Isle": 1.25,
    "Eye Level Center": 1.18
  },

  "detailed_scores": {
    "Main Entrance": {
      "combined_score": 1.198,
      "roi": 1.42,
      "affinity": 0.68,
      "confidence_interval": [1.25, 1.58],
      "placement_cost": 4800
    },
    "Checkout": {
      "combined_score": 1.212,
      "roi": 1.38,
      "affinity": 0.82,
      "confidence_interval": [1.22, 1.54],
      "placement_cost": 6000
    },
    "End Cap 1": {
      "combined_score": 1.287,
      "roi": 1.65,
      "affinity": 0.45,
      "confidence_interval": [1.45, 1.85],
      "placement_cost": 8000
    },
    "Beverage Isle": {
      "combined_score": 1.010,
      "roi": 1.25,
      "affinity": 0.45,
      "confidence_interval": [1.10, 1.40],
      "placement_cost": 2000
    },
    "Eye Level Center": {
      "combined_score": 1.016,
      "roi": 1.18,
      "affinity": 0.72,
      "confidence_interval": [1.05, 1.30],
      "placement_cost": 4000
    }
  },

  "errors": []
}
```

### Ranking Logic

```python
# Sorted by combined_score (descending):
1. End Cap 1:         1.287 (highest combined score)
2. Checkout:          1.212
3. Main Entrance:     1.198
4. Eye Level Center:  1.016
5. Beverage Isle:     1.010

# But final_recommendations shows ROI scores (per spec):
{
  "End Cap 1": 1.65,
  "Checkout": 1.38,
  "Main Entrance": 1.42,
  // ...
}
```

### Error Handling

```python
# No locations within budget → return error message
# Missing affinity data → default affinity_score = 0
# Ties in combined_score → break by ROI (higher wins)
```

---

## Agent 6: Explanation & Defense Agent

### Purpose
Generates comprehensive explanations for recommendations using SHAP values, historical evidence, competitor benchmarks, and counterfactual scenarios.

### Responsibilities
- Generate SHAP-based feature importance explanations
- Retrieve similar historical products and their performance
- Query competitor benchmarks
- Generate counterfactual "what-if" scenarios
- Answer follow-up questions from users

### Tools Used
- SHAP explainer (from Agent 3)
- Historical database queries
- Competitor database
- Nearest neighbor search (scikit-learn)
- Natural language generation templates

### Input Schema

```python
PlacementState {
    product: ProductInput,
    final_recommendations: Dict[str, float],
    detailed_scores: Dict[str, Dict],
    roi_explanations: Dict[str, List],
    affinity_analysis: Dict[str, Dict],
    // ... all previous fields
}
```

### Input Example

```json
{
  "product": { "product_name": "Premium Energy Drink" },
  "final_recommendations": {
    "End Cap 1": 1.65,
    "Checkout": 1.38,
    "Main Entrance": 1.42
  },
  "roi_explanations": {
    "End Cap 1": [ /* SHAP values */ ]
  }
}
```

### Processing Logic

```python
def execute(self, state: PlacementState, user_question: str = None) -> PlacementState:
    if user_question is None:
        # Proactive: Explain top recommendation
        explanation = self._explain_top_recommendation(state)
    else:
        # Reactive: Answer specific question
        explanation = self._answer_question(state, user_question)

    state['explanation'] = explanation
    return state

def _explain_top_recommendation(self, state: PlacementState):
    recommendations = state['final_recommendations']
    top_location = list(recommendations.keys())[0]

    return {
        'location': top_location,
        'roi_score': recommendations[top_location],
        'feature_importance': self._get_feature_importance(state, top_location),
        'historical_evidence': self._get_historical_evidence(state, top_location),
        'competitor_benchmark': self._get_competitor_benchmark(state, top_location),
        'counterfactual': self._generate_counterfactual(state, top_location),
        'confidence_assessment': self._assess_confidence(state, top_location)
    }
```

### Explanation Components

#### 1. Feature Importance (SHAP-based)

```python
def _get_feature_importance(self, state, location):
    shap_values = state['roi_explanations'][location]

    # Sort by absolute SHAP value
    sorted_features = sorted(
        shap_values,
        key=lambda x: abs(x['shap_value']),
        reverse=True
    )[:5]

    explanation = "Key factors influencing this recommendation:\n\n"

    for i, feat in enumerate(sorted_features, 1):
        impact = "increased" if feat['shap_value'] > 0 else "decreased"
        explanation += f"{i}. **{feat['feature']}** ({feat['feature_value']:.2f}): "
        explanation += f"{impact} predicted ROI by {abs(feat['shap_value']):.2f}\n"

    return explanation
```

**Example Output:**
```
Key factors influencing this recommendation:

1. **location_velocity** (155.2): increased predicted ROI by 0.42
2. **zone_type_end_cap** (1.0): increased predicted ROI by 0.35
3. **category_location_fit** (0.88): increased predicted ROI by 0.28
4. **is_holiday_season** (1.0): increased predicted ROI by 0.22
5. **traffic_level** (2.0): increased predicted ROI by 0.18
```

#### 2. Historical Evidence

```python
def _get_historical_evidence(self, state, location):
    product = state['product']
    features = state['features_by_location'][location]

    # Query historical products with similar features
    similar_products = self.db.query(
        """
        SELECT product_name, category, actual_roi, placement_date
        FROM historical_placements
        WHERE location_id = ?
        AND category = ?
        AND price BETWEEN ? AND ?
        ORDER BY placement_date DESC
        LIMIT 5
        """,
        location,
        product.category,
        product.price * 0.8,
        product.price * 1.2
    )

    if not similar_products:
        return "No historical data available for similar products in this location."

    evidence = "Similar products that performed in this location:\n\n"
    for prod in similar_products:
        evidence += f"- **{prod['product_name']}** ({prod['category']}): "
        evidence += f"ROI {prod['actual_roi']:.2f} "
        evidence += f"(placed {prod['placement_date']})\n"

    avg_roi = np.mean([p['actual_roi'] for p in similar_products])
    evidence += f"\n**Average ROI for similar products**: {avg_roi:.2f}"

    return evidence
```

**Example Output:**
```
Similar products that performed in this location:

- **Monster Energy Ultra** (Beverages): ROI 1.58 (placed 2025-09-15)
- **Red Bull Sugar Free** (Beverages): ROI 1.72 (placed 2025-08-22)
- **Rockstar Xdurance** (Beverages): ROI 1.45 (placed 2025-07-10)
- **Bang Energy** (Beverages): ROI 1.68 (placed 2025-06-05)
- **Celsius Sparkling** (Beverages): ROI 1.55 (placed 2025-05-18)

**Average ROI for similar products**: 1.60
```

#### 3. Competitor Benchmark

```python
def _get_competitor_benchmark(self, state, location):
    product = state['product']

    # Query competitor products
    competitors = self.competitor_db.query(
        category=product.category,
        location=location,
        active=True
    )

    if not competitors:
        return "No competitor data available for this location."

    predicted_roi = state['roi_predictions'][location]['roi']

    benchmark = f"Competitor products currently in **{location}**:\n\n"

    for comp in competitors:
        benchmark += f"- **{comp['product_name']}** "
        benchmark += f"(${comp['price']:.2f}): ROI {comp['observed_roi']:.2f}\n"

    avg_comp_roi = np.mean([c['observed_roi'] for c in competitors])

    benchmark += f"\n**Average competitor ROI**: {avg_comp_roi:.2f}\n"
    benchmark += f"**Your predicted ROI**: {predicted_roi:.2f}\n\n"

    if predicted_roi > avg_comp_roi:
        diff_pct = ((predicted_roi / avg_comp_roi) - 1) * 100
        benchmark += f"✅ Your product is predicted to **outperform** competitors by **{diff_pct:.0f}%**"
    else:
        diff_pct = ((avg_comp_roi / predicted_roi) - 1) * 100
        benchmark += f"⚠️ Competitors currently outperform by **{diff_pct:.0f}%**"

    return benchmark
```

**Example Output:**
```
Competitor products currently in **End Cap 1**:

- **Red Bull Original** ($2.49): ROI 1.52
- **Monster Energy Green** ($2.79): ROI 1.48
- **5-hour Energy** ($3.99): ROI 1.35

**Average competitor ROI**: 1.45
**Your predicted ROI**: 1.65

✅ Your product is predicted to **outperform** competitors by **14%**
```

#### 4. Counterfactual Scenarios

```python
def _generate_counterfactual(self, state, top_location):
    recommendations = state['final_recommendations']
    detailed = state['detailed_scores']

    locations = list(recommendations.keys())

    if len(locations) < 2:
        return "No alternative locations to compare."

    alt_location = locations[1]  # Second-best

    top_roi = detailed[top_location]['roi']
    alt_roi = detailed[alt_location]['roi']
    roi_diff = top_roi - alt_roi

    counterfactual = f"**Alternative placement analysis:**\n\n"
    counterfactual += f"If you placed in **{alt_location}** instead of **{top_location}**:\n\n"
    counterfactual += f"- ROI would be **{alt_roi:.2f}** (vs. {top_roi:.2f})\n"
    counterfactual += f"- **{roi_diff:.2f} lower** ({(roi_diff/top_roi)*100:.0f}% decrease)\n\n"

    # Identify key feature differences
    top_shap = state['roi_explanations'][top_location]
    alt_shap = state['roi_explanations'][alt_location]

    # Find features with biggest SHAP difference
    shap_diffs = []
    for top_feat in top_shap:
        alt_feat = next((f for f in alt_shap if f['feature'] == top_feat['feature']), None)
        if alt_feat:
            diff = top_feat['shap_value'] - alt_feat['shap_value']
            if abs(diff) > 0.05:  # Significant difference
                shap_diffs.append({
                    'feature': top_feat['feature'],
                    'diff': diff
                })

    shap_diffs = sorted(shap_diffs, key=lambda x: abs(x['diff']), reverse=True)[:3]

    if shap_diffs:
        counterfactual += "**Main differences:**\n"
        for feat in shap_diffs:
            direction = "advantage" if feat['diff'] > 0 else "disadvantage"
            counterfactual += f"- {feat['feature']}: {abs(feat['diff']):.2f} {direction}\n"

    return counterfactual
```

**Example Output:**
```
**Alternative placement analysis:**

If you placed in **Checkout** instead of **End Cap 1**:

- ROI would be **1.38** (vs. 1.65)
- **0.27 lower** (16% decrease)

**Main differences:**
- zone_type_end_cap: 0.35 advantage (End Cap 1 has premium placement)
- location_velocity: 0.15 advantage (End Cap 1 has higher foot traffic)
- competitor_proximity_score: 0.08 disadvantage (Checkout has more competitors)
```

#### 5. Confidence Assessment

```python
def _assess_confidence(self, state, location):
    prediction = state['roi_predictions'][location]
    roi = prediction['roi']
    lower, upper = prediction['confidence_interval']

    ci_width = upper - lower
    relative_width = ci_width / roi

    assessment = f"**Confidence Assessment:**\n\n"
    assessment += f"- Predicted ROI: **{roi:.2f}**\n"
    assessment += f"- 80% Confidence Interval: **[{lower:.2f}, {upper:.2f}]**\n"
    assessment += f"- Interval width: {ci_width:.2f} ({relative_width*100:.0f}% of prediction)\n\n"

    if relative_width < 0.15:
        assessment += "✅ **High confidence**: Narrow interval indicates strong prediction certainty."
    elif relative_width < 0.30:
        assessment += "⚠️ **Moderate confidence**: Reasonable uncertainty, typical for retail predictions."
    else:
        assessment += "⚠️ **Lower confidence**: Wide interval suggests higher uncertainty. Consider gathering more data."

    return assessment
```

**Example Output:**
```
**Confidence Assessment:**

- Predicted ROI: **1.65**
- 80% Confidence Interval: **[1.45, 1.85]**
- Interval width: 0.40 (24% of prediction)

⚠️ **Moderate confidence**: Reasonable uncertainty, typical for retail predictions.
```

### Output Schema

```python
PlacementState {
    // ... all previous fields

    # NEW FIELD ADDED:
    explanation: {
        location: str,                         # Top recommended location
        roi_score: float,                      # ROI for that location
        feature_importance: str,               # SHAP-based explanation (markdown)
        historical_evidence: str,              # Similar products (markdown)
        competitor_benchmark: str,             # Competitor comparison (markdown)
        counterfactual: str,                   # What-if scenario (markdown)
        confidence_assessment: str             # Confidence interval analysis (markdown)
    }
}
```

### Output Example

```json
{
  "product": { "product_name": "Premium Energy Drink" },
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",

  "final_recommendations": {
    "End Cap 1": 1.65,
    "Checkout": 1.38,
    "Main Entrance": 1.42,
    "Beverage Isle": 1.25,
    "Eye Level Center": 1.18
  },

  "explanation": {
    "location": "End Cap 1",
    "roi_score": 1.65,

    "feature_importance": "Key factors influencing this recommendation:\n\n1. **location_velocity** (155.2): increased predicted ROI by 0.42\n2. **zone_type_end_cap** (1.0): increased predicted ROI by 0.35\n3. **category_location_fit** (0.88): increased predicted ROI by 0.28\n4. **is_holiday_season** (1.0): increased predicted ROI by 0.22\n5. **traffic_level** (2.0): increased predicted ROI by 0.18",

    "historical_evidence": "Similar products that performed in this location:\n\n- **Monster Energy Ultra** (Beverages): ROI 1.58 (placed 2025-09-15)\n- **Red Bull Sugar Free** (Beverages): ROI 1.72 (placed 2025-08-22)\n- **Rockstar Xdurance** (Beverages): ROI 1.45 (placed 2025-07-10)\n- **Bang Energy** (Beverages): ROI 1.68 (placed 2025-06-05)\n- **Celsius Sparkling** (Beverages): ROI 1.55 (placed 2025-05-18)\n\n**Average ROI for similar products**: 1.60",

    "competitor_benchmark": "Competitor products currently in **End Cap 1**:\n\n- **Red Bull Original** ($2.49): ROI 1.52\n- **Monster Energy Green** ($2.79): ROI 1.48\n- **5-hour Energy** ($3.99): ROI 1.35\n\n**Average competitor ROI**: 1.45\n**Your predicted ROI**: 1.65\n\n✅ Your product is predicted to **outperform** competitors by **14%**",

    "counterfactual": "**Alternative placement analysis:**\n\nIf you placed in **Checkout** instead of **End Cap 1**:\n\n- ROI would be **1.38** (vs. 1.65)\n- **0.27 lower** (16% decrease)\n\n**Main differences:**\n- zone_type_end_cap: 0.35 advantage\n- location_velocity: 0.15 advantage\n- competitor_proximity_score: 0.08 disadvantage",

    "confidence_assessment": "**Confidence Assessment:**\n\n- Predicted ROI: **1.65**\n- 80% Confidence Interval: **[1.45, 1.85]**\n- Interval width: 0.40 (24% of prediction)\n\n⚠️ **Moderate confidence**: Reasonable uncertainty, typical for retail predictions."
  },

  "errors": []
}
```

### Follow-Up Question Handling

```python
def _answer_question(self, state, question: str):
    """Handle user follow-up questions"""

    question_lower = question.lower()

    # Pattern matching for common questions
    if "why" in question_lower and any(loc in question_lower for loc in state['final_recommendations'].keys()):
        # Why was X recommended?
        location = self._extract_location(question, state['final_recommendations'].keys())
        return self._explain_specific_location(state, location)

    elif "competitor" in question_lower or "vs" in question_lower:
        # Competitor comparison
        location = self._extract_location(question, state['final_recommendations'].keys())
        return self._get_competitor_benchmark(state, location)

    elif "alternative" in question_lower or "instead" in question_lower:
        # Alternative scenarios
        return self._generate_counterfactual(state, list(state['final_recommendations'].keys())[0])

    elif "confidence" in question_lower or "sure" in question_lower:
        # Confidence/certainty questions
        location = self._extract_location(question, state['final_recommendations'].keys())
        return self._assess_confidence(state, location)

    else:
        # Use LLM to answer with context
        return self._llm_answer(state, question)
```

**Example Questions:**
- "Why did you recommend End Cap 1?"
- "How does this compare to competitors?"
- "What if I placed in Checkout instead?"
- "How confident are you in this prediction?"

### Error Handling

```python
# Missing SHAP values → use feature importance from model
# No historical data → skip historical_evidence section
# No competitor data → skip competitor_benchmark section
# Question parsing fails → fall back to LLM-based answer
```

---

## Complete State Evolution Example

### Initial Input
```json
{
  "product_name": "Premium Energy Drink",
  "category": "Beverages",
  "price": 2.99,
  "budget": 5000.00,
  "target_sales": 1000,
  "target_customers": "Young adults 18-35",
  "expected_roi": 1.5
}
```

### After Agent 1 (Input Orchestrator)
```json
{
  "product": { /* ProductInput */ },
  "timestamp": "2025-11-17T10:30:45.123456",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "errors": []
}
```

### After Agent 2 (Data Mining)
```json
{
  "product": { /* ProductInput */ },
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "historical_patterns": { /* seasonal trends, location performance */ },
  "features_by_location": {
    "Main Entrance": { /* 20 features */ },
    "Checkout": { /* 20 features */ },
    // ... 8 more locations
  },
  "errors": []
}
```

### After Agent 3 (ROI Prediction) - Parallel
```json
{
  // ... previous fields
  "roi_predictions": {
    "Main Entrance": { "roi": 1.42, "confidence_interval": [1.25, 1.58] },
    "Checkout": { "roi": 1.38, "confidence_interval": [1.22, 1.54] },
    // ... more locations
  },
  "roi_explanations": {
    "Main Entrance": [ /* SHAP values */ ],
    // ... more locations
  },
  "errors": []
}
```

### After Agent 4 (Market Basket) - Parallel
```json
{
  // ... previous fields
  "affinity_analysis": {
    "Main Entrance": {
      "affinity_score": 0.68,
      "complementary_products": [ /* top 5 */ ],
      "matching_products": [ /* items in location */ ]
    },
    // ... more locations
  },
  "errors": []
}
```

### After Agent 5 (Synthesizer)
```json
{
  // ... previous fields
  "final_recommendations": {
    "End Cap 1": 1.65,
    "Checkout": 1.38,
    "Main Entrance": 1.42,
    "Beverage Isle": 1.25,
    "Eye Level Center": 1.18
  },
  "detailed_scores": {
    "End Cap 1": {
      "combined_score": 1.287,
      "roi": 1.65,
      "affinity": 0.45,
      "confidence_interval": [1.45, 1.85]
    },
    // ... more locations
  },
  "errors": []
}
```

### After Agent 6 (Explanation) - Final State
```json
{
  "product": { "product_name": "Premium Energy Drink", "category": "Beverages" },
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2025-11-17T10:30:45.123456",

  "historical_patterns": { /* ... */ },
  "features_by_location": { /* ... */ },
  "roi_predictions": { /* ... */ },
  "roi_explanations": { /* ... */ },
  "affinity_analysis": { /* ... */ },

  "final_recommendations": {
    "End Cap 1": 1.65,
    "Checkout": 1.38,
    "Main Entrance": 1.42,
    "Beverage Isle": 1.25,
    "Eye Level Center": 1.18
  },

  "detailed_scores": { /* ... */ },

  "explanation": {
    "location": "End Cap 1",
    "roi_score": 1.65,
    "feature_importance": "Key factors influencing this recommendation:\n\n1. **location_velocity**...",
    "historical_evidence": "Similar products that performed in this location...",
    "competitor_benchmark": "Competitor products currently in **End Cap 1**...",
    "counterfactual": "**Alternative placement analysis:**...",
    "confidence_assessment": "**Confidence Assessment:**..."
  },

  "errors": []
}
```

### Final API Response (to User)
```json
{
  "recommendations": {
    "End Cap 1": 1.65,
    "Checkout": 1.38,
    "Main Entrance": 1.42,
    "Beverage Isle": 1.25,
    "Eye Level Center": 1.18
  },
  "explanation": {
    "location": "End Cap 1",
    "roi_score": 1.65,
    "feature_importance": "...",
    "historical_evidence": "...",
    "competitor_benchmark": "...",
    "counterfactual": "...",
    "confidence_assessment": "..."
  },
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## Workflow Orchestration (LangGraph)

### Graph Definition

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(PlacementState)

# Add agent nodes
workflow.add_node("input_orchestrator", agent1.execute)
workflow.add_node("data_mining", agent2.execute)
workflow.add_node("roi_prediction", agent3.execute)
workflow.add_node("market_basket", agent4.execute)
workflow.add_node("synthesizer", agent5.execute)
workflow.add_node("explanation", agent6.execute)

# Define edges (execution flow)
workflow.set_entry_point("input_orchestrator")
workflow.add_edge("input_orchestrator", "data_mining")

# Parallel execution: data_mining → (roi_prediction || market_basket)
workflow.add_edge("data_mining", "roi_prediction")
workflow.add_edge("data_mining", "market_basket")

# Both must complete before synthesizer
workflow.add_edge("roi_prediction", "synthesizer")
workflow.add_edge("market_basket", "synthesizer")

# Sequential after synthesis
workflow.add_edge("synthesizer", "explanation")
workflow.add_edge("explanation", END)

# Compile
app = workflow.compile()
```

### Execution Flow Diagram

```
                    START
                      │
                      ▼
            ┌─────────────────┐
            │ Input           │
            │ Orchestrator    │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Data Mining &   │
            │ Feature Eng.    │
            └────────┬────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ ROI Prediction  │    │ Market Basket   │
│ (Agent 3)       │    │ Analysis        │
│                 │    │ (Agent 4)       │
└────────┬────────┘    └────────┬────────┘
         │                      │
         │   (Wait for both)    │
         │                      │
         └───────────┬──────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Recommendation  │
            │ Synthesizer     │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Explanation &   │
            │ Defense         │
            └────────┬────────┘
                     │
                     ▼
                    END
```

### Parallel Execution

**Why ROI Prediction and Market Basket run in parallel?**
- They are **independent**: MBA doesn't need ROI predictions, and vice versa
- **Performance**: Reduces total latency by ~40%
- **State safety**: Both read from `features_by_location`, neither modifies it
- **Output isolation**: Write to different state keys (`roi_predictions` vs `affinity_analysis`)

**Sequential Barrier:**
- Synthesizer waits for **both** Agent 3 and Agent 4 to complete
- LangGraph manages synchronization automatically

### Error Propagation

```python
# Each agent appends errors to state.errors
# Workflow continues unless critical error occurs

if len(state['errors']) > 0:
    logger.warning(f"Workflow completed with {len(state['errors'])} warnings")
    # Return warnings in final response

if critical_error:
    # Stop workflow and return error response
    raise WorkflowError(state['errors'])
```

---

## Performance Characteristics

### Latency Breakdown (Target: <5 seconds)

| Agent                    | Latency  | Notes                                    |
|--------------------------|----------|------------------------------------------|
| Input Orchestrator       | <50ms    | Validation only                          |
| Data Mining & Features   | 1-2s     | Database queries, feature engineering    |
| ROI Prediction           | 200-500ms| XGBoost inference + SHAP (parallel)      |
| Market Basket Analysis   | 300-600ms| FP-Growth queries + scoring (parallel)   |
| Synthesizer              | <100ms   | Simple aggregation                       |
| Explanation              | 500ms-1s | Database queries, text generation        |
| **Total (end-to-end)**   | **3-5s** | Includes parallel execution optimization |

### Optimization Strategies

1. **Parallel Execution**: Agents 3 & 4 run concurrently (saves ~1-2s)
2. **Feature Caching**: Cache engineered features for similar products
3. **Model Optimization**: Use XGBoost's optimized predictor
4. **Database Indexing**: Index on category, price, location_id
5. **Pre-computed Rules**: FP-Growth runs offline, queries pre-computed associations

---

## Summary

This pipeline documentation provides:

✅ **Complete agent specifications** with input/output schemas
✅ **Detailed state evolution** showing data transformation at each step
✅ **Real-world examples** with actual data structures
✅ **SHAP-based explainability** integration
✅ **Parallel execution** optimization for performance
✅ **Error handling** strategies at each stage
✅ **Multi-objective optimization** combining ROI + affinity
✅ **Comprehensive explanations** (4 types: SHAP, historical, competitors, counterfactuals)

**Total Agents**: 6
**Total State Keys**: 11
**Execution Pattern**: Sequential with parallel branch
**End-to-End Latency**: 3-5 seconds
**Explainability**: 4 explanation types + SHAP values

This architecture ensures **transparency**, **performance**, and **defensibility** for all product placement recommendations.
