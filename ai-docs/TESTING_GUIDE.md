# Testing Guide - Retail Product Placement System

## Quick Start Testing

### 1️⃣ **Test Data Loader (Polars Performance)**

```bash
cd /Users/raghul.ponnusamy/Research/hackathon/retail-product-placement-agent/flux_data

# Test Polars data loader
uv run python -c "
from utils.data_loader import SalesDataLoader
import time

start = time.time()
loader = SalesDataLoader('data/input/sales_history.csv')
summary = loader.get_data_summary()
elapsed = time.time() - start

print('=' * 60)
print('DATA LOADER TEST')
print('=' * 60)
print(f'Load time: {elapsed*1000:.2f}ms')
print(f'Total transactions: {summary[\"total_transactions\"]:,}')
print(f'Unique products: {summary[\"unique_products\"]}')
print(f'Unique locations: {summary[\"unique_locations\"]}')
print(f'Total revenue: \${summary[\"total_revenue\"]:,.2f}')
print(f'Has promotion data: {summary[\"has_promotion_data\"]}')
print('=' * 60)
"
```

**Expected Output:**
```
============================================================
DATA LOADER TEST
============================================================
Load time: 25.34ms
Total transactions: 3,600
Unique products: 30
Unique locations: 10
Total revenue: $4,234,567.89
Has promotion data: True
============================================================
```

---

### 2️⃣ **Test Adaptive Data Manager (Metric Computation)**

```bash
# Run the data manager directly
uv run python -m utils.adaptive_data_manager
```

**Expected Output:**
```
============================================================
COMPUTING METRICS WITH ADAPTIVE FALLBACKS
============================================================
✓ Sales data loaded successfully
✓ Computed lifts for 5 categories
✓ Beverages - endcap: 1.42 (computed, 287 samples)
✓ Snacks - checkout: 1.68 (computed, 312 samples)
⚠ Dairy - endcap: 1.3 (default, insufficient data)
✓ Computed performance for 10 locations
✓ Saved computed metrics to data/computed
============================================================
METRIC COMPUTATION COMPLETE
============================================================

============================================================
COMPUTATION SUMMARY
============================================================
Total metrics: 20
Computed from sales: 13
Using defaults: 7
Computation rate: 65.0%

Data Quality: GOOD
Confidence: 85.0%
Recommendation: Data quality is good. Recommendations are reliable.
============================================================
```

**Check Generated Files:**
```bash
# View computed metrics
cat data/computed/category_lifts.json | head -30
cat data/computed/location_performance.json
cat data/computed/metadata.json
```

---

### 3️⃣ **Test Cost Manager (YAML Configuration)**

```bash
uv run python -m utils.cost_manager
```

**Expected Output:**
```
============================================================
COST MANAGER TEST
============================================================
Config path: config/placement_costs.yaml
Config exists: True
Default duration: 4 weeks
Budget flexibility: 10%

Zone Costs (4 weeks):
  endcap               $8,000.00
  checkout             $6,000.00
  eye_level            $4,000.00
  regular_shelf        $3,200.00
  low_shelf            $2,000.00

Budget Feasibility Check:
  Budget: $5,000.00
  Required: $5,200.00
  Recommendation: acceptable

============================================================
VISIBILITY MANAGER TEST
============================================================

Visibility Factors:
  endcap               1.50x (90% visibility)
  checkout             1.60x (95% visibility)
  eye_level            1.20x (80% visibility)
  low_shelf            0.80x (30% visibility)
============================================================
```

---

### 4️⃣ **Test Complete Workflow (End-to-End)**

Create a test script:

```bash
cat > test_workflow.py << 'EOF'
"""
Test the complete workflow with LangGraph orchestration
"""
import logging
from models.schemas import ProductInput
from workflows.orchestrator import Orchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_workflow():
    print("\n" + "=" * 80)
    print("TESTING COMPLETE WORKFLOW")
    print("=" * 80)

    # Initialize orchestrator
    orchestrator = Orchestrator(data_dir="data", config_dir="config")

    # Create test product input
    product_input = ProductInput(
        product_name="Premium Energy Drink",
        category="Beverages",
        price=3.99,
        budget=5000,
        target_sales=500,
        target_customers="Young adults 18-35, fitness enthusiasts",
        expected_roi=1.5
    )

    print(f"\nTest Product: {product_input.product_name}")
    print(f"Category: {product_input.category}")
    print(f"Price: ${product_input.price}")
    print(f"Budget: ${product_input.budget}")

    # Execute workflow
    try:
        recommendation = orchestrator.execute(product_input)

        print("\n" + "=" * 80)
        print("WORKFLOW RESULTS")
        print("=" * 80)

        print("\n📊 Top 5 Recommendations:")
        for i, (location, roi) in enumerate(recommendation.recommendations.items(), 1):
            print(f"{i}. {location:40s} ROI: {roi:.2f}x")

        if recommendation.explanation:
            print("\n📝 Explanation Preview:")
            print("-" * 80)
            print(recommendation.explanation.feature_importance[:500] + "...")

        print("\n" + "=" * 80)
        print("✅ WORKFLOW TEST PASSED")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ WORKFLOW TEST FAILED: {e}")
        raise

if __name__ == '__main__':
    test_workflow()
EOF

# Run the test
uv run python test_workflow.py
```

**Expected Output:**
```
============================================================
TESTING COMPLETE WORKFLOW
============================================================

Test Product: Premium Energy Drink
Category: Beverages
Price: $3.99
Budget: $5000

============================================================
STARTING LANGGRAPH WORKFLOW
============================================================
[STEP 1/4] Validating input...
✓ Input validation complete
[STEP 2/4] Checking data quality...
Data quality: good
Confidence: 85.0%
[STEP 3/4] Analyzing ROI...
✓ Generated 10 ROI predictions
✓ Top recommendation: End Cap 1 - Beverages (ROI: 1.85)
[STEP 4/4] Generating explanations...
✓ Explanation generated
============================================================
WORKFLOW COMPLETED SUCCESSFULLY
============================================================

============================================================
WORKFLOW RESULTS
============================================================

📊 Top 5 Recommendations:
1. End Cap 1 - Beverages                  ROI: 1.85x
2. Main Entrance Display                  ROI: 1.72x
3. Checkout Lane 1                        ROI: 1.65x
4. Beverage Aisle - Eye Level             ROI: 1.48x
5. Snack Aisle - Eye Level                ROI: 1.32x

📝 Explanation Preview:
-------------------------------------------------------------------
**Key factors influencing this recommendation:**

**Data Source Transparency:**
- Category Lift: ✓ **Computed** (287 samples, high confidence)
- Visibility Factor: ✓ **Research Default** (high confidence)
- Location Performance: ✓ **Computed From Sales**
...

============================================================
✅ WORKFLOW TEST PASSED
============================================================
```

---

### 5️⃣ **Test API Server (FastAPI)**

```bash
# Start the API server
uv run uvicorn api.main:app --reload --port 8000
```

**In another terminal, test the API:**

```bash
# Test health endpoint
curl http://localhost:8000/api/health | jq

# Test analyze endpoint
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Premium Energy Drink",
    "category": "Beverages",
    "price": 3.99,
    "budget": 5000,
    "target_sales": 500,
    "target_customers": "Young adults",
    "expected_roi": 1.5
  }' | jq
```

**Or open in browser:**
```
http://localhost:8000/docs  # Swagger UI
```

**Expected API Response:**
```json
{
  "recommendations": {
    "End Cap 1 - Beverages": 1.85,
    "Main Entrance Display": 1.72,
    "Checkout Lane 1": 1.65,
    "Beverage Aisle - Eye Level": 1.48,
    "Snack Aisle - Eye Level": 1.32
  },
  "explanation": {
    "location": "End Cap 1 - Beverages",
    "roi_score": 1.85,
    "feature_importance": "**Key factors influencing this recommendation:**\n\n**Data Source Transparency:**\n- Category Lift: ✓ **Computed** (287 samples, high confidence)...",
    "historical_evidence": "...",
    "competitor_benchmark": "...",
    "counterfactual": "...",
    "confidence_assessment": "..."
  },
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-11-17T18:30:00"
}
```

---

### 6️⃣ **Test Data Quality Scenarios**

#### Test with GOOD data (current):
```bash
# Already tested above - 3,600 transactions
uv run python test_workflow.py
```

#### Test with LIMITED data:
```bash
# Create smaller dataset
head -100 data/input/sales_history.csv > data/input/sales_history_small.csv

# Test with limited data
uv run python -c "
from utils.adaptive_data_manager import AdaptiveDataManager

manager = AdaptiveDataManager(
    sales_csv_path='data/input/sales_history_small.csv',
    data_dir='data'
)
results = manager.compute_all_metrics()

print('\\nData Quality with Limited Data:')
print(f'Quality Level: {results[\"metadata\"][\"data_quality\"][\"quality_level\"]}')
print(f'Confidence: {results[\"metadata\"][\"data_quality\"][\"confidence_score\"]:.1%}')
print(f'Metrics using defaults: {results[\"metadata\"][\"metrics_summary\"][\"using_defaults\"]}')
"

# Restore full dataset
rm data/input/sales_history_small.csv
```

#### Test with NO data (all defaults):
```bash
# Temporarily move sales data
mv data/input/sales_history.csv data/input/sales_history.backup

# Test without sales data
uv run python -c "
from workflows.orchestrator import Orchestrator
from models.schemas import ProductInput

orchestrator = Orchestrator(data_dir='data', config_dir='config')
product = ProductInput(
    product_name='Test Product',
    category='Beverages',
    price=3.99,
    budget=5000,
    target_sales=500,
    target_customers='General',
    expected_roi=1.5
)

recommendation = orchestrator.execute(product)
print('\\n✓ System works with NO sales data (all defaults)')
print(f'Top recommendation: {list(recommendation.recommendations.keys())[0]}')
"

# Restore sales data
mv data/input/sales_history.backup data/input/sales_history.csv
```

---

## 🧪 **Testing Checklist**

Run these tests in order:

- [ ] **Data Loader** - Verify Polars loads sales CSV quickly
- [ ] **Adaptive Data Manager** - Check metric computation and fallbacks
- [ ] **Cost Manager** - Validate YAML configuration loading
- [ ] **Complete Workflow** - End-to-end test with LangGraph
- [ ] **API Server** - Test FastAPI endpoints
- [ ] **Data Quality Scenarios** - Test with good/limited/no data

---

## 📊 **Performance Benchmarks**

Expected performance on standard laptop:

| Operation | Expected Time | Actual |
|-----------|--------------|--------|
| Load 3,600 records (Polars) | < 50ms | ___ms |
| Compute all metrics | < 200ms | ___ms |
| Complete workflow | < 500ms | ___ms |
| API response time | < 1s | ___ms |

---

## 🐛 **Troubleshooting**

### Issue: "Module not found"
```bash
# Ensure uv dependencies are installed
uv sync
```

### Issue: "File not found: sales_history.csv"
```bash
# Check if sales data exists
ls -la data/input/

# If missing, data should be in archive
ls -la data/archive/synthetic/

# You may need to re-run the conversion
uv run python -c "
import json, csv
with open('data/archive/synthetic/sales_history.json', 'r') as f:
    data = json.load(f)
with open('data/input/sales_history.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
print('✓ Converted sales_history.json to CSV')
"
```

### Issue: "Config file not found"
```bash
# Check configs exist
ls -la config/

# If missing, copy from examples
cp config/placement_costs.yaml.example config/placement_costs.yaml
cp config/zone_visibility.yaml.example config/zone_visibility.yaml
```

### Issue: Import errors
```bash
# Make sure you're in the right directory
cd /Users/raghul.ponnusamy/Research/hackathon/retail-product-placement-agent/flux_data

# Check Python path
uv run python -c "import sys; print('\\n'.join(sys.path))"
```

---

## 🎯 **What Success Looks Like**

✅ **All tests pass** without errors
✅ **Performance** meets benchmarks (< 1s total)
✅ **Data provenance** shows in explanations
✅ **Fallbacks work** when data is insufficient
✅ **API responds** correctly to requests
✅ **LangGraph orchestration** completes all steps

---

## 📝 **Next Steps After Testing**

Once all tests pass:
1. Review `data/computed/metadata.json` for data quality
2. Adjust `config/placement_costs.yaml` for your store
3. Customize `config/zone_visibility.yaml` if needed
4. Start using the API for real recommendations!

---

## 🔗 **Additional Resources**

- **API Docs**: http://localhost:8000/docs (when server running)
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Config Examples**: `config/*.yaml.example`
