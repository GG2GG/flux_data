"""
Demo script to test the complete workflow with actual output
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
    print("TESTING COMPLETE WORKFLOW - RETAIL PRODUCT PLACEMENT")
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

    print(f"\n📦 Test Product Details:")
    print(f"  • Name: {product_input.product_name}")
    print(f"  • Category: {product_input.category}")
    print(f"  • Price: ${product_input.price}")
    print(f"  • Budget: ${product_input.budget}")
    print(f"  • Target Sales: {product_input.target_sales} units")
    print(f"  • Target Customers: {product_input.target_customers}")
    print(f"  • Expected ROI: {product_input.expected_roi}x")

    # Execute workflow
    try:
        print("\n" + "=" * 80)
        print("EXECUTING WORKFLOW...")
        print("=" * 80)

        recommendation = orchestrator.execute(product_input)

        print("\n" + "=" * 80)
        print("✅ WORKFLOW RESULTS")
        print("=" * 80)

        print("\n📊 Top 5 Placement Recommendations:")
        print("-" * 80)
        for i, (location, roi) in enumerate(list(recommendation.recommendations.items())[:5], 1):
            print(f"{i}. {location:45s} ROI: {roi:.2f}x")

        if recommendation.explanation:
            print("\n" + "=" * 80)
            print("📝 DETAILED EXPLANATION")
            print("=" * 80)

            print("\n🔍 Feature Importance:")
            print("-" * 80)
            print(recommendation.explanation.feature_importance[:800])
            print("\n... (truncated for brevity)")

            if recommendation.explanation.historical_evidence:
                print("\n📈 Historical Evidence:")
                print("-" * 80)
                print(recommendation.explanation.historical_evidence[:400])
                print("\n... (truncated for brevity)")

            if recommendation.explanation.confidence_assessment:
                print("\n🎯 Confidence Assessment:")
                print("-" * 80)
                print(recommendation.explanation.confidence_assessment[:400])
                print("\n... (truncated for brevity)")

        print("\n" + "=" * 80)
        print("✅ WORKFLOW TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ WORKFLOW TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    test_workflow()
