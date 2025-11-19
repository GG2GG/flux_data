"""
Simple test to show data provenance and full output
"""
from workflows.orchestrator import Orchestrator
from models.schemas import ProductInput

# Create orchestrator
orchestrator = Orchestrator()

# Test product
product = ProductInput(
    product_name="Premium Energy Drink",
    category="Beverages",
    price=3.99,
    budget=5000,
    target_sales=500,
    target_customers="Young adults 18-35",
    expected_roi=1.5
)

print("\n" + "="*80)
print("RETAIL PRODUCT PLACEMENT RECOMMENDATION")
print("="*80)
print(f"\nProduct: {product.product_name} (${product.price})")
print(f"Category: {product.category}")
print(f"Budget: ${product.budget}")
print(f"Target: {product.target_sales} units")

# Execute
result = orchestrator.execute(product)

print("\n" + "="*80)
print("TOP 5 RECOMMENDATIONS")
print("="*80)
for i, (loc, roi) in enumerate(list(result.recommendations.items())[:5], 1):
    print(f"{i}. {loc:45s} ROI: {roi:.2f}x")

if result.explanation:
    print("\n" + "="*80)
    print("FEATURE IMPORTANCE & DATA PROVENANCE")
    print("="*80)
    print(result.explanation.feature_importance)

    print("\n" + "="*80)
    print("CONFIDENCE ASSESSMENT")
    print("="*80)
    print(result.explanation.confidence_assessment[:600])

print("\n✅ Test completed successfully!\n")
