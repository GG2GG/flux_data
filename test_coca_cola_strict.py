"""
Test strict filtering with Coca Cola (Beverages).
"""

from models.schemas import ProductInput
from workflows.orchestrator import OrchestratorV2
import json

# Test product: Coca Cola (Beverages)
product = ProductInput(
    product_name="Coca Cola",
    category="Beverages",
    price=0.5,
    budget=1000.0,
    target_sales=10000,
    target_customers="Young Adults 18-35",
    expected_roi=1.5
)

print("=" * 80)
print("TESTING STRICT FILTERING WITH COCA COLA")
print("=" * 80)
print(f"\nProduct: {product.product_name}")
print(f"Category: {product.category}")
print(f"Budget: ${product.budget}")
print()

# Initialize orchestrator
print("Initializing orchestrator...")
orchestrator = OrchestratorV2(enable_state_logging=False)
print()

# Execute workflow
print("=" * 80)
print("EXECUTING WORKFLOW WITH STRICT FILTERING")
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

    # Check for inappropriate locations
    inappropriate_keywords = ['personal care', 'cosmetic', 'dairy', 'bakery', 'snack']
    inappropriate_found = []

    for location in recommendation.recommendations.keys():
        location_lower = location.lower()
        for keyword in inappropriate_keywords:
            if keyword in location_lower:
                inappropriate_found.append((location, keyword))

    print()
    if inappropriate_found:
        print("❌ FAILURE: Found inappropriate locations in recommendations:")
        for loc, keyword in inappropriate_found:
            print(f"  ✗ {loc} (contains '{keyword}' - NOT for beverages!)")
    else:
        print("✅ SUCCESS: No inappropriate locations found!")
        print("  All recommendations are beverage-appropriate")

    # Check if beverage-specific locations are in top 3
    top_3_locations = list(recommendation.recommendations.keys())[:3]
    beverage_in_top_3 = any('beverage' in loc.lower() for loc in top_3_locations)

    print()
    if beverage_in_top_3:
        print("✅ SUCCESS: Beverage-specific locations in top 3")
    else:
        print("⚠️  Note: No Beverage-specific locations in top 3 (may be due to budget)")

    print()
    print("=" * 80)
    print("EXPECTED RESULTS FOR COCA COLA (BEVERAGES)")
    print("=" * 80)

    # Expected allowed locations
    expected_allowed = [
        "Beverage Aisle - Eye Level",
        "Beverage Aisle - Bottom",
        "Checkout Lane 1",       # Impulse
        "Main Entrance Display"  # Impulse
    ]

    # Expected filtered out
    expected_filtered = [
        "Personal Care Aisle",
        "Dairy Section - Regular",
        "Bakery Display",
        "Snack Aisle - Eye Level",
        "End Cap 2 - Snacks"  # Snack-specific endcap, not beverage
    ]

    print("\nExpected ALLOWED for Beverages:")
    for loc in expected_allowed:
        if loc in recommendation.recommendations:
            print(f"  ✅ {loc} - correctly kept (ROI: {recommendation.recommendations[loc]:.2f})")
        else:
            print(f"  ⚠️  {loc} - missing (may be over budget)")

    print("\nExpected FILTERED OUT for Beverages:")
    for loc in expected_filtered:
        if loc not in recommendation.recommendations:
            print(f"  ✅ {loc} - correctly filtered")
        else:
            print(f"  ❌ {loc} - NOT filtered (ROI: {recommendation.recommendations[loc]:.2f}) - FAILURE!")

    # Count successes
    correct_filtered = sum(1 for loc in expected_filtered if loc not in recommendation.recommendations)
    total_filtered = len(expected_filtered)

    print()
    print(f"Filtering effectiveness: {correct_filtered}/{total_filtered} ({correct_filtered/total_filtered*100:.0f}%)")

    if correct_filtered == total_filtered:
        print("🎉 PERFECT FILTERING - All irrelevant locations removed!")
    elif correct_filtered >= total_filtered * 0.8:
        print("✅ Good filtering - Most irrelevant locations removed")
    else:
        print("❌ Poor filtering - Too many irrelevant locations kept")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
