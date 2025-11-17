# 24-HOUR HACKATHON EXECUTION PLAN
## Research-Backed Retail Product Placement Agent

---

## REALITY CHECK: What We're Actually Building

**Timeline**: 24 hours
**Team**: 4 people
**Goal**: Working demo that showcases research-backed multi-agent system

### What This Plan Changes from Original

| Original Research Plan | 24-Hour Hackathon Reality |
|------------------------|---------------------------|
| Train XGBoost model on synthetic data | **Use precomputed ROI scores** (simulate trained model) |
| 6 specialized agents | **3 core agents** (Input, Analyzer, Explainer) |
| Real SHAP calculations | **Precomputed SHAP-style explanations** |
| FP-Growth from scratch | **Precomputed affinity rules** |
| Full LangGraph orchestration | **Simple sequential workflow** |
| Comprehensive testing suite | **Demo scenarios + smoke tests** |
| FastAPI + Unity frontend | **FastAPI + CLI interface** (Unity if time permits) |

### What We Keep (Research Credibility)

✅ **Multi-agent architecture** - Still 3 distinct agents with clear roles
✅ **Research foundation** - Document all algorithms/papers in IMPLEMENTATION_PLAN.md
✅ **Explainability** - SHAP-style feature importance + historical evidence + counterfactuals
✅ **Synthetic data with patterns** - Realistic seasonality, location effects, affinity
✅ **Professional documentation** - CLAUDE.md, AGENT_PIPELINE.md, research references

### Success Criteria (Must-Have for Demo)

1. ✅ **Working end-to-end flow**: Input product → Get recommendations
2. ✅ **3 agents functioning**: Input validation, ROI analysis, explanation generation
3. ✅ **Explainable outputs**: Feature importance + historical examples + competitor benchmarks
4. ✅ **Synthetic data pipeline**: 10+ locations, 30+ products, realistic patterns
5. ✅ **CLI demo**: Interactive command-line interface
6. ✅ **Documentation**: Research foundation clearly documented

---

## TEAM STRUCTURE & RESPONSIBILITIES

### Team Member 1: Backend Lead - Agent Systems & Orchestration
**Core Focus**: Multi-agent architecture, workflow, agent logic

**Hours 0-6**:
- Project structure setup (agents/, models/, data/, api/)
- Implement 3 agent classes (InputAgent, AnalyzerAgent, ExplainerAgent)
- Create simple sequential orchestrator (no LangGraph initially)
- Basic agent communication via Python dict state

**Hours 6-12**:
- Integrate agents with precomputed data
- Implement agent decision logic
- Add agent personality/behavior (Analyzer = data-driven, Explainer = defensive)
- Test agent workflow end-to-end

**Hours 12-18**:
- Polish agent responses
- Add error handling
- Create 3 demo scenarios
- Integration testing with Team Member 3's API

**Hours 18-24**:
- Final agent testing
- Demo script preparation
- Documentation of agent behavior
- Bug fixes

**Key Deliverables**:
- 3 fully functional agent classes
- Sequential workflow orchestrator
- Demo scenario data

---

### Team Member 2: Data Engineer - Synthetic Data & "ML Models"
**Core Focus**: Realistic synthetic data generation, precomputed ROI/SHAP

**Hours 0-6**:
- Design data schema (products, locations, sales_history, competitors)
- Generate 30 products across 5 categories
- Create 10 locations with traffic/visibility attributes
- Generate 12 months of sales history with patterns

**Hours 6-12**:
- Implement realistic patterns:
  - Seasonality (holiday +40%, summer beverages +25%)
  - Location effects (end-cap +200%, checkout +40%)
  - Product affinity rules (chips+soda, beer+snacks)
- Precompute ROI scores for all product-location pairs
- Create SHAP-style feature importance explanations

**Hours 12-18**:
- Generate competitor benchmarks
- Create historical "similar product" examples
- Precompute counterfactual scenarios
- Export to JSON files for fast loading

**Hours 18-24**:
- Validate data quality
- Create data documentation
- Generate 5 demo product profiles
- Data visualization for presentation

**Key Deliverables**:
- products.json (30 products)
- locations.json (10 locations)
- precomputed_roi.json (300 product-location scores)
- feature_importance.json (SHAP-style explanations)
- competitors.json (60 competitor products)
- historical_examples.json (150 examples)

---

### Team Member 3: API Developer - FastAPI & Endpoints
**Core Focus**: REST API, session management, endpoint logic

**Hours 0-6**:
- FastAPI project setup with CORS
- Create data models (Pydantic schemas)
- Implement session management
- Build `/api/analyze` endpoint (calls agent orchestrator)

**Hours 6-12**:
- Build `/api/defend` endpoint (follow-up questions)
- Add `/api/competitors` endpoint
- Implement error handling
- Create API documentation (auto-generated Swagger)

**Hours 12-18**:
- Integration with Team Member 1's agents
- Load Team Member 2's precomputed data
- API testing with different inputs
- Performance optimization

**Hours 18-24**:
- Final API testing
- Deploy locally for demo
- API documentation polish
- Prepare Postman collection for demo

**Key Deliverables**:
- 5+ REST API endpoints
- Swagger documentation
- Session state management
- Integration with agents

---

### Team Member 4: Interface Developer - CLI & Testing
**Core Focus**: User interface, testing, demo preparation

**Hours 0-6**:
- Design CLI interface flow
- Create input validation
- Build basic CLI commands (analyze, defend)
- Setup testing framework (pytest)

**Hours 6-12**:
- Implement rich CLI with colors/tables
- Add interactive prompts
- Create data visualization (ASCII charts if needed)
- Write unit tests for key functions

**Hours 12-18**:
- End-to-end testing of full system
- Create 5 demo scenarios with scripts
- Bug tracking and reporting
- UI polish (colors, formatting)

**Hours 18-24**:
- Final demo rehearsal
- Record demo video (backup)
- Create presentation slides
- Prepare demo script

**Key Deliverables**:
- Interactive CLI interface
- 5 demo scenarios
- Test suite (10+ tests)
- Demo video + slides

---

## HOURLY BREAKDOWN (24 Hours)

### HOUR 0-1: Project Kickoff & Setup

**All Team Together** (30 min)
- [ ] Review plan and assign roles
- [ ] Define data formats (JSON schemas)
- [ ] Define agent communication protocol
- [ ] Git repo setup + branching strategy

**Individual Setup** (30 min)
- [ ] Clone repo and create branches
- [ ] Setup Python environments
- [ ] Install dependencies
- [ ] Create initial directory structure

**Output**: Everyone has working environment, clear responsibilities

---

### HOUR 1-3: Foundation Sprint

**Team Member 1** (Backend/Agents)
- [ ] Create `agents/base_agent.py` with BaseAgent class
- [ ] Implement `agents/input_agent.py` (validation)
- [ ] Implement `agents/analyzer_agent.py` (skeleton)
- [ ] Implement `agents/explainer_agent.py` (skeleton)
- [ ] Create `workflows/orchestrator.py` (simple sequential)

**Team Member 2** (Data)
- [ ] Design data schemas (products, locations, etc.)
- [ ] Generate 30 products with realistic attributes
- [ ] Generate 10 locations with traffic/visibility
- [ ] Start sales history generation (basic)

**Team Member 3** (API)
- [ ] FastAPI project structure
- [ ] Create Pydantic models for ProductInput, Recommendations
- [ ] Implement `/health` endpoint
- [ ] Implement `/api/analyze` skeleton

**Team Member 4** (CLI/Testing)
- [ ] Design CLI command structure
- [ ] Implement basic argument parsing
- [ ] Create `cli_demo.py` skeleton
- [ ] Setup pytest configuration

**Checkpoint**: Basic project structure exists, can run "Hello World"

---

### HOUR 3-6: Core Development Sprint 1

**Team Member 1** (Backend/Agents)
- [ ] Complete InputAgent logic (validate product details)
- [ ] AnalyzerAgent: Load precomputed ROI data
- [ ] AnalyzerAgent: Rank locations by ROI
- [ ] AnalyzerAgent: Apply budget constraints
- [ ] Test agent workflow with mock data

**Team Member 2** (Data)
- [ ] Implement seasonality patterns (SARIMA-inspired)
- [ ] Implement location effects (end-cap, checkout, eye-level)
- [ ] Generate 12 months of sales history
- [ ] Start precomputing ROI scores (formula-based)

**Team Member 3** (API)
- [ ] Connect `/api/analyze` to orchestrator
- [ ] Implement request/response models
- [ ] Add CORS middleware
- [ ] Test endpoint with Postman

**Team Member 4** (CLI/Testing)
- [ ] Implement `analyze` command
- [ ] Add rich console formatting
- [ ] Create input prompts with validation
- [ ] Write first integration test

**Checkpoint**: Can input product via CLI → API → Agents → Returns something

---

### HOUR 6: FIRST MAJOR MILESTONE

**All Team Together** (30 min)
- [ ] Demo: Input product → Get ROI recommendations
- [ ] Identify blockers
- [ ] Adjust priorities if needed
- [ ] Quick sync on data formats

**Break**: 15 minutes

---

### HOUR 6-9: Core Development Sprint 2

**Team Member 1** (Backend/Agents)
- [ ] ExplainerAgent: Feature importance generation
- [ ] ExplainerAgent: Historical example retrieval
- [ ] ExplainerAgent: Competitor benchmark logic
- [ ] Add personality to agent responses

**Team Member 2** (Data)
- [ ] Precompute ROI for all 300 product-location pairs
- [ ] Generate SHAP-style feature importance (rule-based)
- [ ] Create 60 competitor products with benchmarks
- [ ] Generate 150 historical examples

**Team Member 3** (API)
- [ ] Implement `/api/defend` endpoint
- [ ] Add session state storage
- [ ] Implement `/api/competitors` endpoint
- [ ] Error handling and validation

**Team Member 4** (CLI/Testing)
- [ ] Implement `defend` command for follow-up questions
- [ ] Add table formatting for recommendations
- [ ] Create 3 demo scenarios
- [ ] Write unit tests for agents

**Checkpoint**: Full workflow works, explanations generated

---

### HOUR 9-12: Feature Completion Sprint

**Team Member 1** (Backend/Agents)
- [ ] Add counterfactual generation logic
- [ ] Improve agent response quality
- [ ] Add confidence interval display
- [ ] Test edge cases

**Team Member 2** (Data)
- [ ] Generate product affinity rules (complementary products)
- [ ] Create counterfactual scenarios
- [ ] Add confidence intervals to ROI scores
- [ ] Export all data to JSON files

**Team Member 3** (API)
- [ ] Complete all endpoints
- [ ] Add API documentation
- [ ] Implement proper error responses
- [ ] Load and cache precomputed data

**Team Member 4** (CLI/Testing)
- [ ] Polish CLI interface
- [ ] Add ASCII charts/visualizations
- [ ] Create 2 more demo scenarios (total 5)
- [ ] Integration testing

**Checkpoint**: All core features implemented

---

### HOUR 12: SECOND MAJOR MILESTONE

**All Team Together** (30 min)
- [ ] Full end-to-end test
- [ ] Test all 5 demo scenarios
- [ ] Bug tracking in shared doc
- [ ] Prioritize critical bugs

**Break**: 30 minutes (lunch/dinner)

---

### HOUR 12-15: Integration & Bug Fixes

**Team Member 1** (Backend/Agents)
- [ ] Fix agent integration bugs
- [ ] Improve explanation quality
- [ ] Add logging for debugging
- [ ] Test with Team Member 2's final data

**Team Member 2** (Data)
- [ ] Validate all generated data
- [ ] Fix data quality issues
- [ ] Create data documentation
- [ ] Generate visualizations for slides

**Team Member 3** (API)
- [ ] Fix API bugs
- [ ] Optimize data loading
- [ ] Add request/response logging
- [ ] Test concurrent requests

**Team Member 4** (CLI/Testing)
- [ ] Fix UI bugs
- [ ] Add more visual polish
- [ ] Complete test suite (10+ tests)
- [ ] Start presentation slides

**Checkpoint**: Critical bugs fixed, system stable

---

### HOUR 15-18: Testing, Documentation & Polish

**Team Member 1** (Backend/Agents)
- [ ] Code cleanup and comments
- [ ] Document agent behavior
- [ ] Create agent architecture diagram
- [ ] Prepare agent demo talking points

**Team Member 2** (Data)
- [ ] Document data generation process
- [ ] Create data quality report
- [ ] Prepare data visualization slides
- [ ] Write research foundation section

**Team Member 3** (API)
- [ ] Finalize API documentation
- [ ] Create Postman collection
- [ ] Write deployment guide
- [ ] Test API stress scenarios

**Team Member 4** (CLI/Testing)
- [ ] Finalize demo scenarios
- [ ] Create demo script document
- [ ] Start recording demo video
- [ ] Create presentation slides (architecture, demo, results)

**Checkpoint**: Documentation complete, ready for demo prep

---

### HOUR 18: THIRD MAJOR MILESTONE

**All Team Together** (30 min)
- [ ] Full system test with fresh eyes
- [ ] Rehearse demo script
- [ ] Test on clean environment
- [ ] Assign presentation roles

**Break**: 30 minutes

---

### HOUR 18-21: Demo Preparation

**Team Member 1** (Backend/Agents)
- [ ] Prepare agent behavior explanation
- [ ] Create architecture slides
- [ ] Test demo scenarios 3x times
- [ ] Be ready for live demo

**Team Member 2** (Data)
- [ ] Create data generation slides
- [ ] Prepare research foundation slides
- [ ] Show data quality metrics
- [ ] Prepare technical Q&A answers

**Team Member 3** (API)
- [ ] Final API testing
- [ ] Prepare API demo
- [ ] Create architecture diagram
- [ ] Monitor system health

**Team Member 4** (CLI/Testing)
- [ ] Record final demo video
- [ ] Create backup demo screenshots
- [ ] Finalize presentation slides
- [ ] Test on presentation machine

**Checkpoint**: Demo ready, video recorded, slides complete

---

### HOUR 21-22: Final Rehearsal

**All Team Together**
- [ ] Run through complete demo 3x times
- [ ] Practice presentation (5 min version, 10 min version)
- [ ] Prepare Q&A answers
- [ ] Test on demo machine
- [ ] Create backup plan (if live demo fails)

---

### HOUR 22-23: Final Polish & Prep

**All Team Together**
- [ ] Final system check
- [ ] Load demo scenarios
- [ ] Test internet connection
- [ ] Prepare all windows/tabs
- [ ] Team pep talk!

---

### HOUR 23-24: DEMO TIME! 🚀

- [ ] Demo presentation
- [ ] Q&A
- [ ] Submission
- [ ] Celebration!

---

## TECHNICAL ARCHITECTURE (Simplified)

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                     CLI Interface                        │
│              (rich, click, interactive)                  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Server                        │
│  /api/analyze | /api/defend | /api/competitors          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Agent Orchestrator                          │
│           (Simple Sequential Flow)                       │
└─────┬───────────────┬───────────────┬───────────────────┘
      │               │               │
      ▼               ▼               ▼
┌──────────┐  ┌──────────────┐  ┌─────────────┐
│  Input   │  │   Analyzer   │  │  Explainer  │
│  Agent   │  │    Agent     │  │   Agent     │
│          │  │              │  │             │
│ Validate │  │ Load ROI     │  │ Generate    │
│ Product  │  │ Rank Locs    │  │ Explanations│
│ Details  │  │ Apply Budget │  │ SHAP-style  │
└──────────┘  └──────┬───────┘  └─────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│             Precomputed Data (JSON)                      │
│  - products.json                                         │
│  - locations.json                                        │
│  - precomputed_roi.json (300 scores)                    │
│  - feature_importance.json (SHAP-style)                 │
│  - competitors.json (60 products)                       │
│  - historical_examples.json (150 examples)              │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input (CLI)
    ↓
FastAPI /api/analyze
    ↓
InputAgent: Validate
    ↓
AnalyzerAgent: Load precomputed ROI → Rank → Filter by budget
    ↓
ExplainerAgent: Load feature importance + historical + competitors
    ↓
FastAPI Response
    ↓
CLI Display (rich tables)
```

---

## PRECOMPUTED DATA STRATEGY

### Why Precompute?

**Time Constraint**: Training XGBoost + generating SHAP values = 4-6 hours
**Demo Priority**: Need working system > research implementation
**Research Credibility**: Document the **would-be** process thoroughly

### What to Precompute

#### 1. ROI Scores (products.json → locations.json)

**Formula** (research-backed):
```python
def calculate_roi(product, location):
    base_roi = 1.0

    # Location effects (research: end-caps +200%, checkout +40%)
    location_multiplier = {
        'end_cap': 2.0,
        'checkout': 1.4,
        'eye_level': 1.25,
        'main_entrance': 1.15,
        'regular': 1.0
    }[location.type]

    # Traffic factor
    traffic_boost = location.traffic_level * 0.15

    # Category fit (beverages in beverage aisle)
    category_fit = 1.2 if product.category == location.primary_category else 1.0

    # Seasonality
    seasonal_boost = 1.4 if is_holiday_season() and product.category == 'Beverages' else 1.0

    # Price tier fit
    price_fit = 1.1 if product.price_tier == 'premium' and location.type == 'end_cap' else 1.0

    roi = base_roi * location_multiplier * (1 + traffic_boost) * category_fit * seasonal_boost * price_fit

    # Add realistic noise
    roi += random.gauss(0, 0.1)

    return max(0.5, min(3.0, roi))  # Clamp to realistic range
```

#### 2. Feature Importance (SHAP-style)

**Approach**: Rule-based approximation of what SHAP would show

```python
def generate_feature_importance(product, location, roi):
    """Simulate SHAP values based on contribution to ROI"""

    importance = []

    # Location velocity (traffic)
    traffic_contribution = location.traffic_level * 0.3
    importance.append(('location_velocity', traffic_contribution))

    # Zone type
    zone_contribution = 0.25 if location.type == 'end_cap' else 0.1
    importance.append(('zone_type_end_cap', zone_contribution))

    # Category fit
    category_contribution = 0.2 if product.category == location.primary_category else 0.0
    importance.append(('category_location_fit', category_contribution))

    # Seasonality
    seasonal_contribution = 0.15 if is_holiday_season() else 0.0
    importance.append(('is_holiday_season', seasonal_contribution))

    # Sort by contribution
    importance.sort(key=lambda x: abs(x[1]), reverse=True)

    return importance[:5]  # Top 5
```

#### 3. Historical Examples

**Strategy**: Generate synthetic "past placements" that align with patterns

```python
def generate_historical_examples(product, location):
    """Create similar products that performed in this location"""

    examples = []

    # Find 3-5 similar products (same category, similar price)
    similar_products = filter_products(
        category=product.category,
        price_range=(product.price * 0.8, product.price * 1.2)
    )

    for prod in similar_products[:5]:
        # Calculate their "actual" ROI (slightly varied from predicted)
        actual_roi = calculate_roi(prod, location) + random.gauss(0, 0.05)

        examples.append({
            'product_name': prod.name,
            'category': prod.category,
            'actual_roi': round(actual_roi, 2),
            'placement_date': generate_past_date()
        })

    return examples
```

#### 4. Competitor Benchmarks

```python
def generate_competitors(product, location):
    """Create 2-4 competitor products in same location"""

    competitors = []

    # Generate competing products
    for i in range(random.randint(2, 4)):
        competitor = {
            'product_name': f"{product.category} Competitor {i+1}",
            'price': product.price * random.uniform(0.85, 1.15),
            'observed_roi': calculate_roi(product, location) * random.uniform(0.85, 1.10)
        }
        competitors.append(competitor)

    return competitors
```

---

## AGENT IMPLEMENTATION (Simplified)

### Agent 1: InputAgent

**Purpose**: Validate product input

```python
class InputAgent:
    def execute(self, product_input: ProductInput) -> dict:
        # Validation
        if product_input.budget <= 0:
            raise ValueError("Budget must be positive")

        if product_input.price <= 0:
            raise ValueError("Price must be positive")

        # Initialize state
        return {
            'product': product_input,
            'session_id': str(uuid.uuid4()),
            'timestamp': datetime.now()
        }
```

### Agent 2: AnalyzerAgent

**Purpose**: Load precomputed ROI and rank locations

```python
class AnalyzerAgent:
    def __init__(self, precomputed_data):
        self.roi_data = precomputed_data['roi']
        self.locations = precomputed_data['locations']

    def execute(self, state: dict) -> dict:
        product = state['product']

        # Load precomputed ROI scores for this product category
        roi_predictions = {}

        for location in self.locations:
            # Find precomputed ROI
            roi_score = self._get_precomputed_roi(product, location)

            # Apply budget constraint
            placement_cost = self._estimate_cost(location)
            if placement_cost > product.budget:
                continue

            roi_predictions[location['name']] = {
                'roi': roi_score,
                'confidence_interval': (roi_score * 0.85, roi_score * 1.15),
                'placement_cost': placement_cost
            }

        # Rank by ROI
        ranked = sorted(roi_predictions.items(),
                       key=lambda x: x[1]['roi'],
                       reverse=True)

        state['roi_predictions'] = dict(ranked)
        return state
```

### Agent 3: ExplainerAgent

**Purpose**: Generate explanations using precomputed data

```python
class ExplainerAgent:
    def __init__(self, precomputed_data):
        self.feature_importance = precomputed_data['feature_importance']
        self.historical = precomputed_data['historical_examples']
        self.competitors = precomputed_data['competitors']

    def execute(self, state: dict) -> dict:
        top_location = list(state['roi_predictions'].keys())[0]

        # Load precomputed explanations
        explanation = {
            'location': top_location,
            'roi_score': state['roi_predictions'][top_location]['roi'],
            'feature_importance': self._get_feature_importance(top_location),
            'historical_evidence': self._get_historical_examples(top_location),
            'competitor_benchmark': self._get_competitors(top_location),
            'counterfactual': self._generate_counterfactual(state)
        }

        state['explanation'] = explanation
        return state
```

---

## CLI INTERFACE DESIGN

### Commands

```bash
# Start analysis
python demo/cli_demo.py analyze

# Interactive prompts:
Product name: Premium Energy Drink
Category: Beverages
Price: 2.99
Budget: 5000
Target sales: 1000
Target customers: Young adults 18-35
Expected ROI: 1.5

# Output:
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Location          ┃ ROI      ┃ Confidence (80% CI)┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ End Cap 1         │ 1.65     │ [1.40 - 1.90]      │
│ Main Entrance     │ 1.42     │ [1.21 - 1.63]      │
│ Checkout          │ 1.38     │ [1.17 - 1.59]      │
│ Beverage Isle     │ 1.25     │ [1.06 - 1.44]      │
│ Eye Level Center  │ 1.18     │ [1.00 - 1.36]      │
└───────────────────┴──────────┴────────────────────┘

Session ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
Use 'defend <session_id>' to ask follow-up questions

# Ask follow-up
python demo/cli_demo.py defend a1b2c3d4-e5f6-7890-abcd-ef1234567890 "Why End Cap 1?"

# Output: Full explanation with SHAP-style feature importance, etc.
```

---

## DEMO SCENARIOS

### Scenario 1: Premium Energy Drink
- Category: Beverages
- Price: $2.99 (premium)
- Budget: $5,000
- Expected outcome: End Cap 1 (high traffic + impulse + premium fit)

### Scenario 2: Budget Chips
- Category: Snacks
- Price: $1.49 (budget)
- Budget: $2,000
- Expected outcome: Regular shelf (lower cost, still good ROI)

### Scenario 3: Organic Yogurt
- Category: Dairy
- Price: $4.99 (premium)
- Budget: $8,000
- Expected outcome: Eye Level in Dairy section (category fit)

### Scenario 4: Holiday Seasonal Product
- Category: Beverages (Hot Chocolate)
- Price: $3.49
- Budget: $6,000
- Time: November (holiday season)
- Expected outcome: Main Entrance (holiday traffic + seasonal boost)

### Scenario 5: Over-Budget Scenario
- Category: Snacks
- Price: $2.99
- Budget: $500 (very low)
- Expected outcome: Only 1-2 locations affordable, system handles gracefully

---

## RISK MITIGATION

### Risk 1: Integration Issues Between Team Members
**Probability**: High | **Impact**: Critical

**Mitigation**:
- Define data formats in Hour 0 (JSON schemas)
- Frequent check-ins every 3 hours
- Shared Google Doc for API contracts
- Mock data for independent development

### Risk 2: Precomputed Data Doesn't Look Realistic
**Probability**: Medium | **Impact**: Medium

**Mitigation**:
- Use research-backed formulas for ROI calculation
- Add realistic noise/variation
- Validate with domain knowledge
- Document assumptions clearly

### Risk 3: Not Enough Time for Demo Prep
**Probability**: Medium | **Impact**: High

**Mitigation**:
- Start demo prep at Hour 18 (6 hours before deadline)
- Record backup video at Hour 20
- Practice demo 3x times minimum
- Have slides ready by Hour 21

### Risk 4: Critical Bug in Final Hours
**Probability**: Medium | **Impact**: High

**Mitigation**:
- Feature freeze at Hour 20
- Only bug fixes after Hour 20
- Have backup demo video
- Focus on "what works" in demo

### Risk 5: Team Member Unavailable
**Probability**: Low | **Impact**: High

**Mitigation**:
- Clear documentation as you code
- Git commit frequently
- Pair programming for critical components
- Cross-train on basic tasks

---

## SUCCESS METRICS

### Must-Have (Demo Blockers)
- [ ] CLI can input product details
- [ ] System returns 5 location recommendations with ROI scores
- [ ] At least 1 explanation type works (feature importance OR historical)
- [ ] Can answer 1 follow-up question
- [ ] 3 demo scenarios work end-to-end
- [ ] Presentation slides complete

### Should-Have (Quality)
- [ ] All 3 agents functioning distinctly
- [ ] All 4 explanation types (SHAP, historical, competitors, counterfactual)
- [ ] 5 demo scenarios
- [ ] Clean CLI interface with tables
- [ ] API documentation (Swagger)
- [ ] Research foundation documented

### Nice-to-Have (Polish)
- [ ] ASCII charts/visualizations
- [ ] Unity frontend (if time permits)
- [ ] Deployed to cloud
- [ ] Advanced demo scenarios
- [ ] Beautiful presentation

---

## WHAT TO DOCUMENT (Research Credibility)

Even though we're precomputing, document the **research foundation**:

### In IMPLEMENTATION_PLAN.md
✅ Already complete - keep as-is
- Full research references
- Algorithm descriptions (XGBoost, FP-Growth, SHAP)
- What we **would** implement given more time

### In CLAUDE.md
✅ Already complete - update with:
- Note that this is a 24-hour prototype
- Precomputed data strategy
- Roadmap for full implementation

### In HACKATHON_24H_PLAN.md (this file)
✅ Execution strategy
✅ Team responsibilities
✅ What's simplified vs. research plan

### In Presentation
- Slide 1: Problem statement
- Slide 2: Research foundation (cite papers)
- Slide 3: System architecture (3 agents)
- Slide 4: Data generation (patterns used)
- Slide 5: Demo
- Slide 6: What's precomputed vs. what's real
- Slide 7: Future roadmap (full implementation)

---

## DEMO SCRIPT (5 Minutes)

### Minute 1: Problem & Research Foundation
"Retail product placement is a multi-billion dollar industry. Research shows end-cap displays can increase sales by 200-400%. We built a research-backed multi-agent system that recommends optimal placements using techniques from recent papers on retail optimization, explainable AI, and multi-agent systems."

### Minute 2: System Architecture
"Our system uses 3 specialized agents: Input Validator, ROI Analyzer (based on gradient boosting approaches), and Explainer (using SHAP-inspired feature importance). We generated synthetic data following research patterns - seasonality effects, location multipliers, product affinity rules."

### Minute 3: Live Demo
1. Run CLI: `python demo/cli_demo.py analyze`
2. Input: Premium Energy Drink, $2.99, $5k budget
3. Show recommendations table
4. Explain top recommendation (End Cap 1: ROI 1.65)
5. Ask follow-up: "Why End Cap 1?"
6. Show SHAP-style explanations, historical examples, competitor benchmarks

### Minute 4: Technical Highlights
"Key features:
- Multi-agent architecture with distinct roles
- Research-backed ROI calculations (location effects, seasonality)
- Explainable recommendations (4 explanation types)
- Precomputed data for demo speed (in production would train XGBoost)
- 300 product-location combinations analyzed"

### Minute 5: Q&A
Anticipated questions:
- "Is this using real ML?" → "For this 24h demo, we precomputed using research formulas. Full implementation would train XGBoost on real data."
- "How accurate are predictions?" → "Synthetic data follows research patterns. With real data, typical accuracy is R²>0.75 per literature."
- "Can it scale?" → "Architecture supports it - would need distributed agents + model serving for production."

---

## FINAL CHECKLIST

### Hour 22 (2 Hours Before Demo)
- [ ] All code committed to Git
- [ ] Demo scenarios tested 3x
- [ ] Backup video recorded
- [ ] Presentation slides finalized
- [ ] Demo machine setup complete
- [ ] Internet connection verified

### Hour 23 (1 Hour Before Demo)
- [ ] Team rehearsal complete
- [ ] Roles assigned (who presents what)
- [ ] Backup plan agreed
- [ ] Confidence boost huddle

### During Demo
- [ ] Stay calm if something breaks
- [ ] Use backup video if needed
- [ ] Focus on what works
- [ ] Show enthusiasm!
- [ ] Have fun - you built something in 24 hours! 🚀

---

## POST-HACKATHON: Full Implementation Roadmap

**Week 1**: Implement real XGBoost training on synthetic data
**Week 2**: Integrate real SHAP calculations
**Week 3**: Implement FP-Growth for affinity analysis
**Week 4**: Add LangGraph for proper agent orchestration
**Month 2**: Test with real retail datasets (Dunnhumby, Instacart)
**Month 3**: Production deployment with API scaling

---

## TEAM COMMUNICATION

### Check-in Schedule
- **Hour 0**: Kickoff (30 min)
- **Hour 3**: Quick standup (10 min)
- **Hour 6**: Milestone demo (30 min)
- **Hour 9**: Quick standup (10 min)
- **Hour 12**: Milestone demo (30 min)
- **Hour 15**: Quick standup (10 min)
- **Hour 18**: Milestone demo (30 min)
- **Hour 21**: Final rehearsal (30 min)

### Communication Channels
- Slack/Discord: Quick questions
- GitHub: Code + issues
- Google Doc: Shared data schemas, bug tracking
- Zoom: Milestone demos

### Escalation
1. Try yourself (15 min max)
2. Ask in chat
3. If blocked >10 min, call directly
4. If affects others, immediate huddle

---

**Remember**: Perfect is the enemy of done. Ship the prototype! Focus on the demo! Document the research! You've got this! 🚀💪

---

**Document Version**: 1.0
**Created**: 2025-11-17
**Team Size**: 4 people
**Timeline**: 24 hours
**Status**: Ready to Execute
