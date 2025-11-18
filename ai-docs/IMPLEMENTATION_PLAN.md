# Implementation Plan: Research-Backed Multi-Agent Retail Product Placement System

## Executive Summary

This document outlines the implementation plan for a multi-agent system that provides data-driven retail product placement recommendations. The system analyzes historical sales patterns, product affinities, and location performance to suggest optimal placements with ROI predictions, backed by explainable evidence and competitor benchmarks.

## Technology Stack

### Core Technologies
- **Agent Framework**: LangGraph or CrewAI for multi-agent orchestration
- **ML Stack**: XGBoost/LightGBM for ROI prediction, scikit-learn for preprocessing
- **Explainability**: SHAP (SHapley Additive exPlanations) for interpretable ML
- **Market Basket Analysis**: mlxtend (FP-Growth algorithm)
- **Data Generation**: Faker + custom retail pattern simulators
- **Database**: SQLite (MVP) or PostgreSQL (production-ready)
- **API Framework**: FastAPI for RESTful endpoints
- **Language**: Python 3.10+

### Key Libraries
```
langgraph>=0.0.40
xgboost>=2.0.0
shap>=0.44.0
mlxtend>=0.22.0  # FP-Growth
pandas>=2.0.0
scikit-learn>=1.3.0
fastapi>=0.104.0
```

## Research Foundation

### Key Academic Insights

**1. Retail Product Placement Optimization**
- Mixed Integer Linear Programming (MILP) for shelf allocation (Hubner & Kuhn, 2012)
- Genetic Algorithms for multi-objective optimization (Yang & Chen, 2009)
- Reinforcement Learning approaches (Q-Learning, DQN) for dynamic placement

**2. Multi-Agent Systems**
- BDI (Belief-Desire-Intention) architecture for goal-oriented agents
- Hierarchical Multi-Agent Systems with specialized sub-agents
- Contract Net Protocol (CNP) for task allocation
- Blackboard Systems for shared knowledge coordination

**3. ROI Prediction Models**
- Gradient Boosting (XGBoost, LightGBM) for tabular data - best balance of accuracy and interpretability
- LSTM/GRU for temporal dependencies in sales patterns
- Attention mechanisms to identify ROI-driving features
- Multi-task learning for joint sales, margin, and ROI prediction

**4. Collaborative Filtering & Recommendations**
- Neural Collaborative Filtering (NCF) for implicit feedback
- Graph Neural Networks (GNN) for user-item-context relationships
- Factorization Machines (FM) for high-dimensional sparse features
- Multi-armed bandits for explore/exploit trade-offs

**5. Market Basket Analysis**
- Apriori and FP-Growth algorithms for frequent itemset mining
- Association rule metrics: Support, Confidence, Lift, Conviction
- Graph-based affinity using product co-purchase networks
- Embedding-based approaches (Prod2Vec, Node2Vec)

**6. Location-Based Optimization**
- Heat map analysis for customer traffic patterns
- Spatial autocorrelation (Moran's I) for zone clustering
- Agent-Based Modeling (ABM) for customer movement simulation
- Markov Chain models for zone transition probabilities

**7. Explainable AI**
- SHAP for unified feature importance framework
- LIME for local interpretable explanations
- Counterfactual explanations ("what-if" scenarios)
- Attention weight visualization for neural models

### Key Research Findings
- End-cap displays show 30-400% sales lift (category-dependent)
- Eye-level shelves outperform by 15-35%
- Right-side placement outperforms left in Western markets
- Checkout proximity increases impulse purchases by 20-50%

## System Architecture

### Multi-Agent Architecture

The system implements a hierarchical multi-agent architecture with six specialized agents:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input Interface                      │
│              (Product, Budget, Price, Category)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent 1: Input Orchestrator                     │
│  - Validates business constraints                            │
│  - Routes to analysis agents                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│       Agent 2: Data Mining & Feature Engineering             │
│  - Extracts historical patterns                              │
│  - Computes location-specific features                       │
│  - Calculates product affinity scores                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
              ┌───────┴───────┐
              │               │
              ▼               ▼
┌──────────────────────┐  ┌──────────────────────────┐
│ Agent 3: ROI         │  │ Agent 4: Market Basket   │
│ Prediction Agent     │  │ Analysis Agent           │
│ - XGBoost model      │  │ - FP-Growth algorithm    │
│ - Confidence         │  │ - Product affinity       │
│   intervals          │  │ - Lift scores            │
└──────────┬───────────┘  └───────────┬──────────────┘
           │                          │
           └──────────┬───────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│        Agent 5: Recommendation Synthesizer                   │
│  - Aggregates ROI + MBA predictions                          │
│  - Applies budget constraints                                │
│  - Ranks locations by expected ROI                           │
│  - Output: {"Main Entrance": 1.4, "Beverage Isle": 1.2}     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         Agent 6: Explanation & Defense Agent                 │
│  - SHAP feature importance                                   │
│  - Historical evidence retrieval                             │
│  - Competitor benchmarks                                     │
│  - Counterfactual scenarios                                  │
└─────────────────────────────────────────────────────────────┘
```

### Agent Communication Pattern

**Workflow Type**: Sequential with parallel branches
- **Sequential Flow**: Input → Data Mining → Synthesizer → Explanation
- **Parallel Branch**: ROI Prediction || Market Basket Analysis (run concurrently)
- **State Management**: Shared context via LangGraph state
- **Coordination Protocol**: Event-driven with blackboard-style shared memory

### Data Architecture

#### Required Data Stores

**1. Historical Sales Database**
```sql
sales_history
├── product_id (FK)
├── location_id (FK)
├── week_date
├── units_sold
├── revenue
└── was_promoted (boolean)
```

**2. Product Catalog**
```sql
products
├── product_id (PK)
├── name
├── category
├── subcategory
├── price
├── cost
├── margin
├── brand
└── lifecycle_stage (new/growth/mature/decline)
```

**3. Store Layout & Zone Metadata**
```sql
locations
├── location_id (PK)
├── zone_name (Main Entrance, Beverage Isle, etc.)
├── zone_type (end_cap/eye_level/checkout/regular)
├── traffic_level (high/medium/low)
├── square_footage
└── display_type
```

**4. Competitor Products**
```sql
competitor_products
├── competitor_id (PK)
├── product_id (similar product in our catalog)
├── location_id
├── observed_roi
├── market_share
└── pricing
```

**5. Market Basket Transactions**
```sql
transactions
├── transaction_id (PK)
├── timestamp
├── products (JSON array of product_ids)
└── location_id
```

#### Feature Engineering Pipeline

**Location-Based Features:**
- Location velocity (average sales per SKU in zone)
- Historical ROI by product category in location
- Traffic density score
- Zone type encoding (one-hot)

**Product-Based Features:**
- Price tier (budget/mid/premium)
- Category and subcategory
- Margin percentage
- Product lifecycle stage
- Brand strength index

**Temporal Features:**
- Seasonality indicators (month, quarter)
- Day of week effects
- Holiday proximity
- Trend direction (growing/stable/declining)

**Affinity Features:**
- Basket lift scores from FP-Growth
- Complementary product count
- Cross-category affinity
- Competitor proximity effects

**Computed Features (~20 total):**
1. location_velocity
2. category_location_fit
3. price_tier_encoded
4. traffic_level_encoded
5. zone_type_encoded
6. seasonality_month
7. seasonality_quarter
8. is_holiday_season
9. product_lifecycle_encoded
10. margin_percentage
11. basket_lift_score
12. complementary_product_count
13. competitor_proximity_score
14. historical_category_roi
15. price_elasticity
16. inventory_turnover_rate
17. promotion_frequency
18. cross_sell_potential
19. brand_strength_index
20. trend_direction_encoded

## Implementation Phases

### Phase 1: Foundation & Synthetic Data (Week 1-2)

#### 1.1 Synthetic Data Generator

**Objective**: Create realistic retail sales data with research-backed patterns

**Components:**

**A. Base Data Generation**
```python
# Generate 50 products across 5 categories
categories = ['Beverages', 'Snacks', 'Dairy', 'Bakery', 'Personal Care']
num_products = 50
num_locations = 10
history_months = 24

# Location definitions with traffic modifiers
locations = {
    'Main Entrance': {'traffic': 1.0, 'impulse': 0.8},
    'Beverage Isle': {'traffic': 0.7, 'impulse': 0.3},
    'End Cap 1': {'traffic': 0.9, 'impulse': 0.9},
    'Checkout': {'traffic': 1.0, 'impulse': 1.0},
    'Eye Level Center': {'traffic': 0.8, 'impulse': 0.5},
    # ... 5 more locations
}
```

**B. Realistic Pattern Implementation**

**Seasonality (SARIMA-based)**
```python
# Holiday lift: +40% in Nov-Dec
# Summer boost for beverages: +25% June-Aug
# Back-to-school: +30% in August-September for snacks
seasonal_multipliers = generate_sarima_pattern(
    trend=0.05,  # 5% annual growth
    seasonal_periods=12,
    seasonal_strength=0.3
)
```

**Location Effects (Research-backed)**
```python
location_multipliers = {
    'End Cap': 2.0,      # +200% lift
    'Eye Level': 1.25,   # +25% lift
    'Checkout': 1.40,    # +40% impulse lift
    'Main Entrance': 1.15,
    'Regular Shelf': 1.0  # baseline
}
```

**Product Affinity (MBA patterns)**
```python
# Define natural affinities
affinity_rules = [
    ('Chips', 'Soda', lift=2.5),
    ('Beer', 'Chips', lift=2.2),
    ('Milk', 'Cereal', lift=3.0),
    ('Toothpaste', 'Toothbrush', lift=4.5),
    # ... generate 50+ affinity rules
]
```

**Price Elasticity**
```python
# Budget products: high elasticity (-2.0)
# Premium products: low elasticity (-0.5)
# Mid-tier: moderate elasticity (-1.2)
elasticity_by_tier = {
    'budget': -2.0,
    'mid': -1.2,
    'premium': -0.5
}
```

**C. Competitor Product Generation**
```python
# For each product, generate 2-3 competitors
# with slightly different pricing and performance
competitor_roi_distribution = {
    'better': 0.2,   # 20% competitors perform better
    'similar': 0.5,  # 50% similar performance
    'worse': 0.3     # 30% perform worse
}
```

**Output**:
- 50,000+ transaction records
- 12,000+ sales_history records (50 products × 10 locations × 24 months)
- 150+ competitor product records
- Affinity matrix (50×50) with lift scores

#### 1.2 Core Data Models

**File**: `data/data_models.py`

```python
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Product(BaseModel):
    product_id: str
    name: str
    category: str
    subcategory: str
    price: float
    cost: float
    margin: float
    brand: str
    lifecycle_stage: str

class Location(BaseModel):
    location_id: str
    zone_name: str
    zone_type: str
    traffic_level: str
    square_footage: float
    display_type: str

class SalesRecord(BaseModel):
    product_id: str
    location_id: str
    week_date: datetime
    units_sold: int
    revenue: float
    was_promoted: bool

class ProductInput(BaseModel):
    product_name: str
    category: str
    price: float
    budget: float
    target_sales: int
    target_customers: str
    expected_roi: float

class PlacementRecommendation(BaseModel):
    location: str
    roi_score: float
    confidence_interval: tuple[float, float]
    reasoning: str
```

#### 1.3 Feature Engineering Pipeline

**File**: `data/feature_engineering.py`

```python
class FeatureEngineer:
    def create_features(self, product, locations, historical_data):
        features = {}

        # Location features
        features['location_velocity'] = self._calc_velocity()
        features['category_location_fit'] = self._calc_category_fit()

        # Product features
        features['price_tier'] = self._encode_price_tier(product.price)
        features['lifecycle_stage'] = self._encode_lifecycle()

        # Temporal features
        features['seasonality'] = self._extract_seasonality()

        # Affinity features
        features['basket_lift'] = self._calc_basket_lift()

        return features
```

### Phase 2: ML Models & ROI Prediction Engine (Week 2-3)

#### 2.1 ROI Prediction Model

**File**: `models/roi_predictor.py`

**Algorithm Choice: XGBoost**
- **Why**: Research shows gradient boosting achieves best accuracy on tabular data while maintaining interpretability
- **Advantages**: Handles mixed feature types, robust to outliers, built-in regularization, fast training

**Model Architecture:**
```python
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit

class ROIPredictor:
    def __init__(self):
        self.model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='reg:squarederror',
            random_state=42
        )

    def train(self, X, y):
        # Time-series cross-validation (4 folds)
        tscv = TimeSeriesSplit(n_splits=4)

        scores = []
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            self.model.fit(X_train, y_train)
            score = self.model.score(X_val, y_val)
            scores.append(score)

        # Final training on all data
        self.model.fit(X, y)
        return np.mean(scores)

    def predict_with_confidence(self, X):
        # Point prediction
        roi_pred = self.model.predict(X)

        # Confidence intervals using quantile regression
        # Train separate models for 10th and 90th percentiles
        lower = self._predict_quantile(X, 0.1)
        upper = self._predict_quantile(X, 0.9)

        return roi_pred, (lower, upper)
```

**Features Used (20 features):**
1. location_velocity
2. category_location_fit
3. price_tier
4. traffic_level
5. zone_type
6. seasonality_month
7. product_lifecycle
8. margin_percentage
9. basket_lift_score
10. complementary_product_count
11. competitor_proximity
12. historical_category_roi
13. price_elasticity
14. inventory_turnover
15. promotion_frequency
16. cross_sell_potential
17. brand_strength
18. trend_direction
19. zone_square_footage
20. impulse_purchase_factor

**Target Variable**: ROI (calculated as (Revenue - Placement_Cost) / Placement_Cost)

**Validation Strategy**:
- Time-series cross-validation with 4 folds
- Target: R² > 0.75 on test set
- RMSE on ROI scale
- MAE for interpretability

#### 2.2 Market Basket Analysis

**File**: `models/affinity_analyzer.py`

**Algorithm: FP-Growth**
- **Why**: More efficient than Apriori for large datasets, no candidate generation needed
- **Research backing**: Standard algorithm in retail analytics since 2000

```python
from mlxtend.frequent_patterns import fpgrowth, association_rules

class AffinityAnalyzer:
    def __init__(self, min_support=0.01, min_confidence=0.3):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.rules = None

    def analyze_transactions(self, transactions_df):
        # Transform to one-hot encoded format
        basket = transactions_df.groupby(['transaction_id', 'product_id'])['product_id'].count().unstack().fillna(0)
        basket = basket.applymap(lambda x: 1 if x > 0 else 0)

        # Apply FP-Growth
        frequent_itemsets = fpgrowth(basket,
                                     min_support=self.min_support,
                                     use_colnames=True)

        # Generate association rules
        self.rules = association_rules(frequent_itemsets,
                                       metric='confidence',
                                       min_threshold=self.min_confidence)

        # Add lift calculation
        self.rules['lift'] = self.rules['lift']

        return self.rules

    def get_complementary_products(self, product_id):
        # Find products with high lift when purchased together
        relevant_rules = self.rules[
            self.rules['antecedents'].apply(lambda x: product_id in x)
        ]

        # Sort by lift (descending)
        top_complementary = relevant_rules.sort_values('lift', ascending=False)

        return top_complementary[['consequents', 'lift', 'confidence']].head(10)

    def calculate_affinity_score(self, product_id, location_products):
        # Score based on complementary products already in location
        score = 0
        for loc_product in location_products:
            lift = self._get_lift(product_id, loc_product)
            score += max(0, lift - 1)  # Only count positive affinity

        return score / len(location_products) if location_products else 0
```

**Association Rule Metrics:**
- **Support**: P(A ∩ B) - frequency of itemset
- **Confidence**: P(B|A) - conditional probability
- **Lift**: P(B|A) / P(B) - how much more likely B is purchased when A is purchased
  - Lift > 1: Positive association
  - Lift = 1: Independent
  - Lift < 1: Negative association
- **Conviction**: Measures dependency strength

#### 2.3 Explainability Layer

**File**: `models/explainer.py`

**SHAP (SHapley Additive exPlanations)**
- **Why**: Unified framework with game-theory foundation, model-agnostic, provides both global and local explanations
- **Research backing**: Lundberg & Lee (2017), widely adopted in industry

```python
import shap

class ModelExplainer:
    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.TreeExplainer(model)

    def explain_prediction(self, X):
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X)

        # Get feature importance
        feature_importance = {
            name: float(shap_val)
            for name, shap_val in zip(self.feature_names, shap_values[0])
        }

        # Sort by absolute importance
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        return sorted_features[:5]  # Top 5 features

    def generate_counterfactuals(self, X, target_roi):
        # Find minimal feature changes to reach target ROI
        # Use optimization approach
        from scipy.optimize import minimize

        def objective(x_new):
            roi_diff = (self.model.predict([x_new])[0] - target_roi) ** 2
            feature_diff = np.sum((x_new - X[0]) ** 2)
            return roi_diff + 0.1 * feature_diff

        result = minimize(objective, X[0], method='L-BFGS-B')

        # Generate explanation
        changes = self._describe_changes(X[0], result.x)
        return changes

    def retrieve_historical_examples(self, X, historical_data, k=5):
        # Find k nearest neighbors in feature space
        from sklearn.neighbors import NearestNeighbors

        nn = NearestNeighbors(n_neighbors=k)
        nn.fit(historical_data['features'])

        distances, indices = nn.kneighbors(X)

        similar_examples = []
        for idx in indices[0]:
            example = {
                'product': historical_data['product_name'][idx],
                'location': historical_data['location'][idx],
                'actual_roi': historical_data['roi'][idx],
                'similarity': 1 / (1 + distances[0][idx])
            }
            similar_examples.append(example)

        return similar_examples
```

**Explanation Types Generated:**

1. **Feature Importance (SHAP)**
```
"Location traffic (0.35), category fit (0.28), seasonality (0.22)
were the key factors driving this prediction."
```

2. **Historical Evidence**
```
"Similar products that performed well in Main Entrance:
- Product A (Category: Snacks): ROI 1.45 (92% similar)
- Product B (Category: Beverages): ROI 1.38 (88% similar)"
```

3. **Counterfactual**
```
"Placing in Checkout instead would reduce ROI by 18% (from 1.4 to 1.15)
primarily due to lower category affinity (-0.15 impact) and reduced
complementary product lift (-0.10 impact)."
```

### Phase 3: Multi-Agent System (Week 3-4)

#### 3.1 Agent Implementations

**File**: `agents/base_agent.py`

```python
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

class BaseAgent:
    def __init__(self, name, description, tools):
        self.name = name
        self.description = description
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
        self.tools = tools

    def execute(self, input_data, context=None):
        raise NotImplementedError
```

**Agent 1: Input Orchestrator**

**File**: `agents/input_orchestrator.py`

```python
class InputOrchestrator(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Input Orchestrator",
            description="Validates and routes product placement requests",
            tools=[]
        )

    def execute(self, product_input: ProductInput, context=None):
        # Validate input
        if product_input.budget <= 0:
            raise ValueError("Budget must be positive")

        if product_input.price <= 0:
            raise ValueError("Price must be positive")

        # Create context for downstream agents
        context = {
            'product': product_input,
            'timestamp': datetime.now(),
            'session_id': str(uuid.uuid4())
        }

        # Log input
        logger.info(f"Processing placement request for {product_input.product_name}")

        return context
```

**Agent 2: Data Mining & Feature Engineering**

**File**: `agents/data_mining_agent.py`

```python
class DataMiningAgent(BaseAgent):
    def __init__(self, db_connection, feature_engineer):
        tools = [
            Tool(
                name="QueryHistoricalSales",
                func=self.query_sales,
                description="Query historical sales data"
            ),
            Tool(
                name="CalculateFeatures",
                func=self.calculate_features,
                description="Calculate features for ML model"
            )
        ]
        super().__init__(
            name="Data Mining Agent",
            description="Extracts patterns from historical data",
            tools=tools
        )
        self.db = db_connection
        self.feature_engineer = feature_engineer

    def execute(self, context):
        product = context['product']

        # Query relevant historical data
        historical_sales = self.query_sales(
            category=product.category,
            price_range=(product.price * 0.8, product.price * 1.2)
        )

        # Extract patterns
        patterns = {
            'seasonal_trends': self._extract_seasonality(historical_sales),
            'location_performance': self._analyze_location_performance(historical_sales),
            'category_insights': self._analyze_category(product.category)
        }

        # Engineer features for each location
        features_by_location = {}
        for location in self.get_all_locations():
            features = self.feature_engineer.create_features(
                product, location, historical_sales
            )
            features_by_location[location.zone_name] = features

        context['historical_patterns'] = patterns
        context['features_by_location'] = features_by_location

        return context
```

**Agent 3: ROI Prediction Agent**

**File**: `agents/roi_prediction_agent.py`

```python
class ROIPredictionAgent(BaseAgent):
    def __init__(self, roi_model, explainer):
        tools = [
            Tool(
                name="PredictROI",
                func=self.predict_roi,
                description="Predict ROI for given location"
            )
        ]
        super().__init__(
            name="ROI Prediction Agent",
            description="Predicts ROI using XGBoost model",
            tools=tools
        )
        self.model = roi_model
        self.explainer = explainer

    def execute(self, context):
        features_by_location = context['features_by_location']
        product = context['product']

        predictions = {}
        explanations = {}

        for location, features in features_by_location.items():
            # Convert to model input format
            X = self._prepare_features(features)

            # Predict ROI with confidence intervals
            roi, (lower, upper) = self.model.predict_with_confidence(X)

            # Generate SHAP explanation
            shap_values = self.explainer.explain_prediction(X)

            # Check budget constraint
            if self._estimate_placement_cost(location) > product.budget:
                continue

            predictions[location] = {
                'roi': float(roi[0]),
                'confidence_interval': (float(lower[0]), float(upper[0])),
                'confidence_level': 0.80  # 80% CI
            }

            explanations[location] = shap_values

        # Rank by ROI
        ranked_locations = sorted(
            predictions.items(),
            key=lambda x: x[1]['roi'],
            reverse=True
        )

        context['roi_predictions'] = dict(ranked_locations)
        context['roi_explanations'] = explanations

        return context
```

**Agent 4: Market Basket Analysis Agent**

**File**: `agents/market_basket_agent.py`

```python
class MarketBasketAgent(BaseAgent):
    def __init__(self, affinity_analyzer):
        tools = [
            Tool(
                name="AnalyzeAffinity",
                func=self.analyze_affinity,
                description="Analyze product affinity patterns"
            )
        ]
        super().__init__(
            name="Market Basket Agent",
            description="Analyzes product affinity using FP-Growth",
            tools=tools
        )
        self.affinity = affinity_analyzer

    def execute(self, context):
        product = context['product']

        # Find complementary products
        complementary = self.affinity.get_complementary_products(product.product_id)

        # Score each location based on complementary product presence
        affinity_scores = {}
        for location in context['features_by_location'].keys():
            # Get products currently in location
            location_products = self._get_location_products(location)

            # Calculate affinity score
            score = self.affinity.calculate_affinity_score(
                product.product_id,
                location_products
            )

            affinity_scores[location] = {
                'affinity_score': score,
                'complementary_products': complementary[:5].to_dict('records')
            }

        context['affinity_analysis'] = affinity_scores

        return context
```

**Agent 5: Recommendation Synthesizer**

**File**: `agents/recommendation_synthesizer.py`

```python
class RecommendationSynthesizer(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Recommendation Synthesizer",
            description="Synthesizes final recommendations",
            tools=[]
        )

    def execute(self, context):
        roi_predictions = context['roi_predictions']
        affinity_analysis = context['affinity_analysis']
        product = context['product']

        # Multi-objective scoring
        final_scores = {}
        for location in roi_predictions.keys():
            roi_score = roi_predictions[location]['roi']
            affinity_score = affinity_analysis[location]['affinity_score']

            # Weighted combination (70% ROI, 30% affinity)
            combined_score = 0.7 * roi_score + 0.3 * affinity_score

            final_scores[location] = {
                'combined_score': combined_score,
                'roi': roi_score,
                'affinity': affinity_score,
                'confidence_interval': roi_predictions[location]['confidence_interval']
            }

        # Rank and select top 5
        ranked = sorted(
            final_scores.items(),
            key=lambda x: x[1]['combined_score'],
            reverse=True
        )

        top_recommendations = dict(ranked[:5])

        # Format output as specified
        output = {
            location: scores['roi']
            for location, scores in top_recommendations.items()
        }

        context['final_recommendations'] = output
        context['detailed_scores'] = top_recommendations

        return context
```

**Agent 6: Explanation & Defense Agent**

**File**: `agents/explanation_agent.py`

```python
class ExplanationAgent(BaseAgent):
    def __init__(self, explainer, competitor_db):
        tools = [
            Tool(
                name="ExplainRecommendation",
                func=self.explain_recommendation,
                description="Generate explanation for recommendation"
            ),
            Tool(
                name="GetCompetitorData",
                func=self.get_competitor_benchmarks,
                description="Retrieve competitor performance data"
            ),
            Tool(
                name="GenerateCounterfactual",
                func=self.generate_counterfactual,
                description="Generate what-if scenarios"
            )
        ]
        super().__init__(
            name="Explanation Agent",
            description="Provides evidence-backed explanations",
            tools=tools
        )
        self.explainer = explainer
        self.competitor_db = competitor_db

    def execute(self, context, user_question=None):
        if user_question is None:
            # Proactive explanation for top recommendation
            return self._explain_top_recommendation(context)
        else:
            # Reactive: answer specific question
            return self._answer_question(context, user_question)

    def _explain_top_recommendation(self, context):
        recommendations = context['final_recommendations']
        top_location = list(recommendations.keys())[0]

        explanations = {
            'location': top_location,
            'roi_score': recommendations[top_location],
            'feature_importance': self._get_feature_importance(context, top_location),
            'historical_evidence': self._get_historical_evidence(context, top_location),
            'competitor_benchmark': self._get_competitor_benchmark(context, top_location),
            'counterfactual': self._generate_counterfactual_explanation(context, top_location)
        }

        return explanations

    def _get_feature_importance(self, context, location):
        shap_values = context['roi_explanations'][location]

        explanation = "Key factors influencing this recommendation:\n"
        for i, (feature, value) in enumerate(shap_values[:3], 1):
            impact = "increased" if value > 0 else "decreased"
            explanation += f"{i}. {feature}: {impact} ROI by {abs(value):.2f}\n"

        return explanation

    def _get_historical_evidence(self, context, location):
        product = context['product']

        # Retrieve similar products from history
        examples = self.explainer.retrieve_historical_examples(
            context['features_by_location'][location],
            self.historical_data,
            k=3
        )

        evidence = "Similar products that performed in this location:\n"
        for ex in examples:
            evidence += f"- {ex['product']}: ROI {ex['actual_roi']:.2f} ({ex['similarity']*100:.0f}% similar)\n"

        return evidence

    def _get_competitor_benchmark(self, context, location):
        product = context['product']

        # Find competitor products in same category
        competitors = self.competitor_db.query(
            category=product.category,
            location=location
        )

        if not competitors:
            return "No competitor data available for this location."

        avg_competitor_roi = np.mean([c['roi'] for c in competitors])
        predicted_roi = context['roi_predictions'][location]['roi']

        comparison = f"Competitor products in {location}:\n"
        comparison += f"- Average competitor ROI: {avg_competitor_roi:.2f}\n"
        comparison += f"- Your predicted ROI: {predicted_roi:.2f}\n"

        if predicted_roi > avg_competitor_roi:
            comparison += f"- Your product is predicted to outperform competitors by {(predicted_roi/avg_competitor_roi - 1)*100:.0f}%"
        else:
            comparison += f"- Competitors currently outperform by {(avg_competitor_roi/predicted_roi - 1)*100:.0f}%"

        return comparison

    def _generate_counterfactual_explanation(self, context, top_location):
        recommendations = context['final_recommendations']

        # Compare top location with second-best
        locations = list(recommendations.keys())
        if len(locations) < 2:
            return "No alternative locations to compare."

        alternative_location = locations[1]
        roi_diff = recommendations[top_location] - recommendations[alternative_location]

        explanation = f"Alternative placement analysis:\n"
        explanation += f"- Placing in {alternative_location} instead would reduce ROI by {roi_diff:.2f} "
        explanation += f"({roi_diff/recommendations[top_location]*100:.0f}%)\n"

        # Identify key feature differences
        top_features = context['features_by_location'][top_location]
        alt_features = context['features_by_location'][alternative_location]

        key_diffs = self._compare_features(top_features, alt_features)
        explanation += f"- Main differences: {', '.join(key_diffs)}"

        return explanation
```

#### 3.2 LangGraph Orchestration

**File**: `workflows/placement_workflow.py`

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class PlacementState(TypedDict):
    product: ProductInput
    timestamp: datetime
    session_id: str
    historical_patterns: dict
    features_by_location: dict
    roi_predictions: dict
    roi_explanations: dict
    affinity_analysis: dict
    final_recommendations: dict
    detailed_scores: dict
    explanation: dict
    errors: Annotated[list, operator.add]

class PlacementWorkflow:
    def __init__(self, agents):
        self.input_orchestrator = agents['input_orchestrator']
        self.data_mining = agents['data_mining']
        self.roi_prediction = agents['roi_prediction']
        self.market_basket = agents['market_basket']
        self.synthesizer = agents['synthesizer']
        self.explanation = agents['explanation']

        self.workflow = self._build_workflow()

    def _build_workflow(self):
        workflow = StateGraph(PlacementState)

        # Add nodes
        workflow.add_node("input", self.input_orchestrator.execute)
        workflow.add_node("data_mining", self.data_mining.execute)
        workflow.add_node("roi_prediction", self.roi_prediction.execute)
        workflow.add_node("market_basket", self.market_basket.execute)
        workflow.add_node("synthesize", self.synthesizer.execute)
        workflow.add_node("explain", self.explanation.execute)

        # Define edges
        workflow.set_entry_point("input")
        workflow.add_edge("input", "data_mining")
        workflow.add_edge("data_mining", "roi_prediction")
        workflow.add_edge("data_mining", "market_basket")
        workflow.add_edge("roi_prediction", "synthesize")
        workflow.add_edge("market_basket", "synthesize")
        workflow.add_edge("synthesize", "explain")
        workflow.add_edge("explain", END)

        return workflow.compile()

    def execute(self, product_input: ProductInput):
        initial_state = {
            "product": product_input,
            "errors": []
        }

        result = self.workflow.invoke(initial_state)

        return {
            "recommendations": result['final_recommendations'],
            "explanation": result['explanation'],
            "session_id": result['session_id']
        }
```

### Phase 4: API & Demo Interface (Week 4)

#### 4.1 FastAPI Implementation

**File**: `api/main.py`

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Retail Product Placement Agent API",
    description="Multi-agent system for optimal product placement recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize workflow
workflow = PlacementWorkflow(agents)

@app.post("/api/analyze")
async def analyze_placement(product: ProductInput):
    """
    Analyze product and return placement recommendations with ROI scores.

    Example input:
    {
        "product_name": "Premium Energy Drink",
        "category": "Beverages",
        "price": 2.99,
        "budget": 5000,
        "target_sales": 1000,
        "target_customers": "Young adults 18-35",
        "expected_roi": 1.5
    }

    Example output:
    {
        "recommendations": {
            "Main Entrance": 1.4,
            "Checkout": 1.35,
            "Beverage Isle": 1.2
        },
        "explanation": {...},
        "session_id": "abc-123"
    }
    """
    try:
        result = workflow.execute(product)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/defend")
async def defend_recommendation(question: DefenseQuestion):
    """
    Answer follow-up questions about recommendations.

    Example input:
    {
        "session_id": "abc-123",
        "question": "Why did you recommend Main Entrance over Beverage Isle?"
    }
    """
    try:
        # Retrieve session context
        context = session_store.get(question.session_id)

        if not context:
            raise HTTPException(status_code=404, detail="Session not found")

        # Use explanation agent to answer
        answer = explanation_agent.execute(context, question.question)

        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/competitors/{product_id}")
async def get_competitor_data(product_id: str, location: str = None):
    """
    Retrieve competitor product performance data.
    """
    try:
        competitors = competitor_db.query(product_id=product_id, location=location)
        return {"competitors": competitors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}
```

#### 4.2 CLI Demo Interface

**File**: `demo/cli_demo.py`

```python
import click
import requests
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

@click.group()
def cli():
    """Retail Product Placement Agent CLI"""
    pass

@cli.command()
@click.option('--product', prompt='Product name', help='Product name')
@click.option('--category', prompt='Category', help='Product category')
@click.option('--price', prompt='Price', type=float, help='Product price')
@click.option('--budget', prompt='Budget', type=float, help='Placement budget')
@click.option('--target-sales', prompt='Target sales', type=int, help='Target sales units')
@click.option('--customers', prompt='Target customers', help='Target customer segment')
@click.option('--roi', prompt='Expected ROI', type=float, help='Expected ROI')
def analyze(product, category, price, budget, target_sales, customers, roi):
    """Analyze product and get placement recommendations"""

    payload = {
        "product_name": product,
        "category": category,
        "price": price,
        "budget": budget,
        "target_sales": target_sales,
        "target_customers": customers,
        "expected_roi": roi
    }

    console.print("\n[bold blue]Analyzing product placement...[/bold blue]")

    response = requests.post("http://localhost:8000/api/analyze", json=payload)

    if response.status_code == 200:
        result = response.json()

        # Display recommendations
        table = Table(title="Placement Recommendations")
        table.add_column("Location", style="cyan")
        table.add_column("ROI Score", style="magenta")

        for location, roi_score in result['recommendations'].items():
            table.add_row(location, f"{roi_score:.2f}")

        console.print(table)

        # Display explanation
        console.print("\n[bold green]Explanation:[/bold green]")
        console.print(Panel(result['explanation']['feature_importance']))
        console.print(Panel(result['explanation']['historical_evidence']))

        # Save session ID for follow-up questions
        with open('.last_session', 'w') as f:
            f.write(result['session_id'])

        console.print(f"\n[dim]Session ID: {result['session_id']}[/dim]")
        console.print("[dim]Use 'defend' command to ask follow-up questions[/dim]")
    else:
        console.print(f"[bold red]Error: {response.json()['detail']}[/bold red]")

@cli.command()
@click.argument('question')
def defend(question):
    """Ask follow-up questions about recommendations"""

    try:
        with open('.last_session', 'r') as f:
            session_id = f.read().strip()
    except FileNotFoundError:
        console.print("[bold red]No active session. Run 'analyze' first.[/bold red]")
        return

    payload = {
        "session_id": session_id,
        "question": question
    }

    response = requests.post("http://localhost:8000/api/defend", json=payload)

    if response.status_code == 200:
        result = response.json()
        console.print("\n[bold green]Answer:[/bold green]")
        console.print(Panel(result['answer']))
    else:
        console.print(f"[bold red]Error: {response.json()['detail']}[/bold red]")

if __name__ == '__main__':
    cli()
```

## Testing Strategy

### Unit Tests

**File**: `tests/test_roi_predictor.py`

```python
import pytest
import numpy as np
from models.roi_predictor import ROIPredictor

def test_roi_predictor_training():
    # Generate synthetic data
    X = np.random.rand(1000, 20)
    y = np.random.rand(1000)

    predictor = ROIPredictor()
    score = predictor.train(X, y)

    assert score > 0.5  # Reasonable R² score

def test_roi_predictor_confidence_intervals():
    predictor = ROIPredictor()
    # ... train model

    X_test = np.random.rand(1, 20)
    roi, (lower, upper) = predictor.predict_with_confidence(X_test)

    assert lower < roi[0] < upper  # Prediction within CI
    assert upper - lower > 0  # CI has positive width
```

### Integration Tests

**File**: `tests/test_workflow.py`

```python
import pytest
from workflows.placement_workflow import PlacementWorkflow
from data.data_models import ProductInput

def test_end_to_end_workflow():
    product = ProductInput(
        product_name="Test Product",
        category="Beverages",
        price=2.99,
        budget=5000,
        target_sales=1000,
        target_customers="Young adults",
        expected_roi=1.5
    )

    workflow = PlacementWorkflow(agents)
    result = workflow.execute(product)

    assert 'recommendations' in result
    assert 'explanation' in result
    assert len(result['recommendations']) > 0

    # Check recommendations format
    for location, roi in result['recommendations'].items():
        assert isinstance(location, str)
        assert isinstance(roi, float)
        assert roi > 0
```

### Performance Tests

**File**: `tests/test_performance.py`

```python
import time
import pytest

def test_workflow_latency():
    """Ensure end-to-end workflow completes in < 5 seconds"""

    start = time.time()
    result = workflow.execute(sample_product)
    end = time.time()

    latency = end - start
    assert latency < 5.0  # Success criteria: < 5 seconds
```

## Success Criteria

### Phase 1: Data Foundation
- ✅ Generate 50,000+ synthetic transactions
- ✅ Create 12,000+ sales history records
- ✅ Implement 20+ engineered features
- ✅ Validate synthetic data patterns match research (seasonality, location effects)

### Phase 2: ML Models
- ✅ ROI prediction model achieves R² > 0.75 on test set
- ✅ FP-Growth generates 100+ association rules with lift > 1.5
- ✅ SHAP explanations correctly identify top 5 features
- ✅ Confidence intervals calibrated (80% of actuals fall within 80% CI)

### Phase 3: Multi-Agent System
- ✅ All 6 agents execute without errors
- ✅ LangGraph workflow completes end-to-end
- ✅ Agent communication working (state passed correctly)
- ✅ Explanation agent provides 3+ justification types

### Phase 4: API & Demo
- ✅ FastAPI endpoints respond in < 5 seconds
- ✅ CLI demo executes full workflow
- ✅ Follow-up questions answered correctly
- ✅ API documentation auto-generated (FastAPI Swagger)

### Overall System
- ✅ End-to-end latency: Input → Recommendations < 5 seconds
- ✅ Recommendation accuracy: ROI predictions within 15% of actuals (on synthetic test set)
- ✅ Explainability: Users can understand why each recommendation was made
- ✅ Defensibility: System can answer "why?" questions with data evidence

## Project Structure

```
retail-product-placement-agent/
│
├── agents/                          # Multi-agent implementations
│   ├── __init__.py
│   ├── base_agent.py               # Base agent class
│   ├── input_orchestrator.py      # Agent 1: Input validation & routing
│   ├── data_mining_agent.py       # Agent 2: Data extraction & feature engineering
│   ├── roi_prediction_agent.py    # Agent 3: XGBoost ROI prediction
│   ├── market_basket_agent.py     # Agent 4: FP-Growth affinity analysis
│   ├── recommendation_synthesizer.py  # Agent 5: Multi-objective recommendation
│   └── explanation_agent.py       # Agent 6: SHAP + evidence + counterfactuals
│
├── models/                         # ML models & algorithms
│   ├── __init__.py
│   ├── roi_predictor.py           # XGBoost ROI prediction model
│   ├── affinity_analyzer.py       # FP-Growth market basket analysis
│   └── explainer.py               # SHAP explainability layer
│
├── data/                           # Data generation & management
│   ├── __init__.py
│   ├── synthetic_generator.py     # Synthetic retail data generator
│   ├── feature_engineering.py     # Feature engineering pipeline
│   ├── data_models.py             # Pydantic/SQLAlchemy models
│   └── database.py                # Database connection & queries
│
├── workflows/                      # Agent orchestration
│   ├── __init__.py
│   └── placement_workflow.py      # LangGraph workflow definition
│
├── api/                            # FastAPI interface
│   ├── __init__.py
│   ├── main.py                    # API endpoints
│   └── schemas.py                 # API request/response models
│
├── demo/                           # Demo interfaces
│   ├── cli_demo.py                # Command-line interface
│   └── web_demo.py                # Optional: Streamlit web interface
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── test_roi_predictor.py
│   ├── test_affinity_analyzer.py
│   ├── test_agents.py
│   ├── test_workflow.py
│   └── test_api.py
│
├── notebooks/                      # Research & validation notebooks
│   ├── research_validation.ipynb  # Validate research algorithms
│   └── data_exploration.ipynb     # Explore synthetic data
│
├── config/                         # Configuration files
│   ├── model_config.yaml
│   └── agent_config.yaml
│
├── scripts/                        # Utility scripts
│   ├── generate_data.py           # Run data generation
│   ├── train_models.py            # Train ML models
│   └── seed_database.py           # Populate database
│
├── docs/                           # Documentation
│   ├── api_documentation.md
│   ├── agent_architecture.md
│   └── research_references.md
│
├── .env.example                    # Environment variables template
├── .gitignore
├── requirements.txt                # Python dependencies
├── README.md                       # Project overview
├── CLAUDE.md                       # Claude Code guidance (to be updated)
└── IMPLEMENTATION_PLAN.md          # This file
```

## Commands Reference

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Data Generation
```bash
# Generate synthetic retail data
python scripts/generate_data.py --num-products 50 --num-locations 10 --months 24

# Seed database
python scripts/seed_database.py
```

### Model Training
```bash
# Train ROI prediction model
python scripts/train_models.py --model roi_predictor

# Train market basket analysis
python scripts/train_models.py --model affinity_analyzer
```

### Running the API
```bash
# Start FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Using the CLI Demo
```bash
# Analyze product placement
python demo/cli_demo.py analyze \
  --product "Premium Energy Drink" \
  --category "Beverages" \
  --price 2.99 \
  --budget 5000 \
  --target-sales 1000 \
  --customers "Young adults 18-35" \
  --roi 1.5

# Ask follow-up questions
python demo/cli_demo.py defend "Why did you recommend Main Entrance?"
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_workflow.py

# Run integration tests only
pytest tests/test_workflow.py -k integration
```

### Development
```bash
# Run single agent test
python -m agents.roi_prediction_agent

# Validate synthetic data
python scripts/validate_data.py

# Check model performance
python scripts/evaluate_models.py
```

## Next Steps After Implementation

### Phase 2 Enhancements (Post-MVP)
1. **LSTM Integration**: Add temporal patterns to ROI prediction
2. **Multi-Armed Bandit**: Implement Thompson Sampling for explore/exploit
3. **Real-time Feedback**: Log actual placements and outcomes for model retraining
4. **Graph Neural Networks**: Model complex product relationships
5. **Agent-Based Simulation**: Simulate customer movement through store

### Production Readiness
1. **Database Migration**: SQLite → PostgreSQL
2. **Caching**: Redis for feature caching and session management
3. **Load Balancing**: Deploy API with multiple workers
4. **Monitoring**: Prometheus + Grafana for system metrics
5. **CI/CD**: GitHub Actions for automated testing and deployment

### Research Extensions
1. Implement alternative algorithms (neural CF, contextual bandits)
2. Compare performance: XGBoost vs. LightGBM vs. Neural Networks
3. Experiment with different agent coordination protocols
4. Validate against real retail datasets (Dunnhumby, Instacart)

## Research References

### Foundational Papers
1. **Agrawal & Srikant (1994)**: "Fast Algorithms for Mining Association Rules" - Apriori algorithm
2. **Rao & Georgeff (1995)**: "BDI Agents: From Theory to Practice" - BDI agent architecture
3. **Hubner & Kuhn (2012)**: "Retail Category Management: Decision Support Systems for Assortment, Shelf Space, Inventory and Price Planning"
4. **Lundberg & Lee (2017)**: "A Unified Approach to Interpreting Model Predictions" - SHAP

### Recent Advances (2020-2025)
- Deep learning for retail forecasting (LSTM, Transformers for time-series)
- Graph neural networks for recommendations (LightGCN, PinSage)
- Multi-agent systems with deep reinforcement learning
- Explainable AI in recommendation systems
- Contextual bandits for dynamic optimization

### Key Conference Venues
- RecSys (ACM Conference on Recommender Systems)
- KDD (Knowledge Discovery and Data Mining)
- IJCAI (International Joint Conference on Artificial Intelligence)
- INFORMS (Institute for Operations Research and Management Sciences)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
**Status**: Ready for Implementation
