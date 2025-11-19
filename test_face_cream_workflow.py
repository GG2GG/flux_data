"""
Test the complete workflow with Face Cream to verify filtering works end-to-end.
"""

from models.schemas import ProductInput
from workflows.orchestrator import OrchestratorV2
import json

# Test product: Face Cream (Personal Care)
product = ProductInput(
    product_name="Face Cream",
    category="Personal Care",
    price=1.5,
    budget=1500.0,
    target_sales=2000,
    target_customers="Women, Beauty conscious",
    expected_roi=1.5
)

print("=" * 80)
print("TESTING COMPLETE WORKFLOW WITH FACE CREAM")
print("=" * 80)
print(f"\nProduct: {product.product_name}")
print(f"Category: {product.category}")
print(f"Price: ${product.price}")
print(f"Budget: ${product.budget}")
print()

# Initialize orchestrator
print("Initializing orchestrator...")
orchestrator = OrchestratorV2(enable_state_logging=False)
print()

# Execute workflow
print("=" * 80)
print("EXECUTING WORKFLOW")
print("=" * 80)
print()

try:
    recommendation = orchestrator.execute(product)

    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    print("Final Recommendations (Top 5):")
    for i, (location, roi) in enumerate(recommendation.recommendations.items(), 1):
        print(f"{i}. {location}: ROI {roi:.2f}")

    # Check if inappropriate locations are in top 5
    inappropriate_keywords = ['beverage', 'snack', 'dairy', 'bakery']
    inappropriate_found = []

    for location in recommendation.recommendations.keys():
        location_lower = location.lower()
        for keyword in inappropriate_keywords:
            if keyword in location_lower:
                inappropriate_found.append((location, keyword))

    print()
    if inappropriate_found:
        print("⚠️  WARNING: Found inappropriate locations in recommendations:")
        for loc, keyword in inappropriate_found:
            print(f"  ✗ {loc} (contains '{keyword}')")
    else:
        print("✓ SUCCESS: No inappropriate locations found!")
        print("  All recommendations make sense for Personal Care products")

    # Check if Personal Care Aisle is in top 3
    top_3_locations = list(recommendation.recommendations.keys())[:3]
    personal_care_in_top_3 = any('personal care' in loc.lower() for loc in top_3_locations)

    print()
    if personal_care_in_top_3:
        print("✓ SUCCESS: Personal Care Aisle is in top 3 recommendations")
    else:
        print("⚠️  WARNING: Personal Care Aisle not in top 3")

    print()
    print("=" * 80)
    print("FILTER AGENT EFFECTIVENESS")
    print("=" * 80)

    # We expect these locations to be filtered OUT:
    expected_filtered = [
        "Beverage Aisle - Eye Level",
        "Beverage Aisle - Bottom",
        "Snack Aisle - Eye Level",
        "End Cap 1 - Beverages",  # Beverage-specific endcap
        "End Cap 2 - Snacks",     # Snack-specific endcap
        "Dairy Section - Regular",
        "Bakery Display"
    ]

    # We expect these locations to be KEPT:
    expected_kept = [
        "Personal Care Aisle",
        "Checkout Lane 1",       # Acceptable for impulse
        "Main Entrance Display"  # Acceptable for high traffic
    ]

    print("\nExpected to be filtered out:")
    for loc in expected_filtered:
        if loc not in recommendation.recommendations:
            print(f"  ✓ {loc} - correctly filtered")
        else:
            print(f"  ✗ {loc} - NOT filtered (ROI: {recommendation.recommendations.get(loc, 'N/A')})")

    print("\nExpected to be kept:")
    for loc in expected_kept:
        if loc in recommendation.recommendations:
            print(f"  ✓ {loc} - correctly kept (ROI: {recommendation.recommendations[loc]:.2f})")
        else:
            print(f"  ✗ {loc} - incorrectly filtered out")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
