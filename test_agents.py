"""
Test script for the agent system.
"""

from models.schemas import ProductInput
from workflows.orchestrator import Orchestrator


def test_basic_workflow():
    """Test the basic agent workflow."""

    print("\n" + "=" * 80)
    print("Testing Retail Product Placement Agent System")
    print("=" * 80 + "\n")

    # Create test product
    product = ProductInput(
        product_name="Premium Energy Drink",
        category="Beverages",
        price=2.99,
        budget=5000.0,
        target_sales=1000,
        target_customers="Young adults 18-35, fitness enthusiasts",
        expected_roi=1.5
    )

    print("Test Product:")
    print(f"  Name: {product.product_name}")
    print(f"  Category: {product.category}")
    print(f"  Price: ${product.price:.2f}")
    print(f"  Budget: ${product.budget:.2f}")
    print(f"  Expected ROI: {product.expected_roi:.2f}")
    print()

    # Initialize orchestrator
    orchestrator = Orchestrator(data_dir="data")

    # Check status
    status = orchestrator.get_status()
    print("Orchestrator Status:")
    print(f"  Status: {status['status']}")
    print(f"  Locations loaded: {status['locations_loaded']}")
    print(f"  Categories in KB: {status['categories_in_kb']}")
    print()

    # Execute workflow
    print("Executing workflow...\n")

    try:
        recommendation = orchestrator.execute(product)

        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80 + "\n")

        print("Top Recommendations:")
        for i, (location, roi) in enumerate(recommendation.recommendations.items(), 1):
            print(f"  {i}. {location}: ROI {roi:.2f}")

        print(f"\nSession ID: {recommendation.session_id}")

        print("\n" + "-" * 80)
        print("EXPLANATION")
        print("-" * 80 + "\n")

        print(f"Top Location: {recommendation.explanation.location}")
        print(f"ROI Score: {recommendation.explanation.roi_score:.2f}\n")

        print(recommendation.explanation.feature_importance)
        print()
        print(recommendation.explanation.historical_evidence)
        print()
        print(recommendation.explanation.competitor_benchmark)
        print()
        print(recommendation.explanation.counterfactual)
        print()
        print(recommendation.explanation.confidence_assessment)

        print("\n" + "=" * 80)
        print("TEST PASSED ✓")
        print("=" * 80 + "\n")

        return True

    except Exception as e:
        print("\n" + "=" * 80)
        print("TEST FAILED ✗")
        print("=" * 80)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_workflow()
    exit(0 if success else 1)
