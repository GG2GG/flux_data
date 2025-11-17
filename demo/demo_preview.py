#!/usr/bin/env python3
"""
Interactive Demo Preview - Retail Product Placement System
Shows a visual representation of the planogram and recommendations
"""

import json
import sys
from pathlib import Path

# Colors for terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_banner():
    """Print welcome banner"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("═" * 80)
    print("🏪  RETAIL PRODUCT PLACEMENT OPTIMIZER - DEMO PREVIEW  🏪")
    print("═" * 80)
    print(f"{Colors.ENDC}\n")


def print_store_planogram():
    """Print ASCII representation of store layout"""
    print(f"{Colors.BOLD}{Colors.OKBLUE}📍 STORE PLANOGRAM (2D Layout){Colors.ENDC}\n")

    planogram = """
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                          STORE ENTRANCE                                  │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                          │
    │  ┌──────────┐                    ┌──────────────┐    ┌─────────────┐  │
    │  │   🏆     │                    │              │    │   MAIN      │  │
    │  │ END CAP 1│                    │   BAKERY     │    │  ENTRANCE   │  │
    │  │BEVERAGES │                    │   DISPLAY    │    │   DISPLAY   │  │
    │  │ ROI: 1.85│                    │              │    │             │  │
    │  └──────────┘                    └──────────────┘    └─────────────┘  │
    │                                                                          │
    │  ┌──────────┐  ┌─────────────┐  ┌─────────────┐                       │
    │  │ END CAP 2│  │  BEVERAGE   │  │   SNACK     │                       │
    │  │  SNACKS  │  │AISLE - EYE  │  │ AISLE - EYE │                       │
    │  │          │  │   LEVEL     │  │    LEVEL    │                       │
    │  └──────────┘  └─────────────┘  └─────────────┘                       │
    │                                                                          │
    │                ┌─────────────┐  ┌─────────────┐  ┌──────────────┐    │
    │                │    DAIRY    │  │   BAKERY    │  │  PERSONAL    │    │
    │                │   SECTION   │  │   DISPLAY   │  │     CARE     │    │
    │                │   REGULAR   │  │             │  │    AISLE     │    │
    │                └─────────────┘  └─────────────┘  └──────────────┘    │
    │                                                                          │
    │                ┌─────────────┐                       ┌─────────────┐  │
    │                │  BEVERAGE   │                       │  CHECKOUT   │  │
    │                │AISLE-BOTTOM │                       │   LANE 1    │  │
    │                └─────────────┘                       └─────────────┘  │
    │                                                                          │
    └─────────────────────────────────────────────────────────────────────────┘

    Legend:
    🏆 = Top Recommendation (Highest ROI)
    ⭐ = Recommended (Top 5)
    📦 = Standard Location
    """

    print(planogram)


def load_sample_data():
    """Load sample product and location data"""
    data_dir = Path(__file__).parent.parent / "data"

    try:
        with open(data_dir / "products.json") as f:
            products = json.load(f)

        with open(data_dir / "locations.json") as f:
            locations = json.load(f)

        return products[:5], locations  # First 5 products
    except Exception as e:
        print(f"{Colors.FAIL}Error loading data: {e}{Colors.ENDC}")
        return [], []


def show_product_analysis(product_name="Premium Energy Drink"):
    """Show analysis for a sample product"""
    print(f"\n{Colors.BOLD}{Colors.OKGREEN}📊 ANALYSIS RESULTS{Colors.ENDC}")
    print(f"\n{Colors.BOLD}Product:{Colors.ENDC} {product_name}")
    print(f"{Colors.BOLD}Category:{Colors.ENDC} Beverages")
    print(f"{Colors.BOLD}Price:{Colors.ENDC} $2.99")
    print(f"{Colors.BOLD}Budget:{Colors.ENDC} $5,000\n")

    # Mock recommendations
    recommendations = [
        {"location": "End Cap 1 - Beverages", "roi": 1.85, "rank": 1},
        {"location": "Main Entrance Display", "roi": 1.62, "rank": 2},
        {"location": "Checkout Lane 1", "roi": 1.58, "rank": 3},
        {"location": "Beverage Aisle - Eye Level", "roi": 1.45, "rank": 4},
        {"location": "End Cap 2 - Snacks", "roi": 1.38, "rank": 5}
    ]

    print(f"{Colors.BOLD}{Colors.OKCYAN}🎯 TOP 5 RECOMMENDED LOCATIONS:{Colors.ENDC}\n")

    for rec in recommendations:
        if rec["rank"] == 1:
            icon = "🏆"
            color = Colors.WARNING
        elif rec["rank"] <= 3:
            icon = "⭐"
            color = Colors.OKGREEN
        else:
            icon = "📍"
            color = Colors.ENDC

        roi_display = f"{rec['roi']:.2f}x"
        return_pct = f"{(rec['roi'] - 1) * 100:.0f}%"

        print(f"{color}{icon} #{rec['rank']} {rec['location']:<30} "
              f"ROI: {roi_display:>6}  ({return_pct:>4} return){Colors.ENDC}")

    # Explanation
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}💡 WHY END CAP 1?{Colors.ENDC}\n")
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} Premium location with 2.0x visibility multiplier")
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} High foot traffic (250 daily visitors)")
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} Perfect category match (Beverages → Beverage section)")
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} Within your $5,000 budget (costs $4,800 for 4 weeks)")

    # Metrics
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}📈 KEY METRICS:{Colors.ENDC}\n")
    metrics = [
        ("Expected Daily Units", "145 units"),
        ("Expected Monthly Revenue", "$13,065"),
        ("Placement Cost (4 weeks)", "$4,800"),
        ("Profit Margin", "45%"),
        ("Confidence Level", "80% CI [1.65 - 2.05]")
    ]

    for label, value in metrics:
        print(f"  {label:<30} {Colors.BOLD}{value}{Colors.ENDC}")


def show_comparison():
    """Show comparison with alternatives"""
    print(f"\n{Colors.BOLD}{Colors.WARNING}📊 ALTERNATIVE ANALYSIS:{Colors.ENDC}\n")

    print("If you chose Main Entrance Display instead of End Cap 1:")
    print(f"  • ROI would be {Colors.BOLD}1.62{Colors.ENDC} vs {Colors.BOLD}1.85{Colors.ENDC}")
    print(f"  • {Colors.FAIL}0.23 lower ROI{Colors.ENDC} (12% decrease)")
    print(f"  • {Colors.WARNING}$2,990 less profit{Colors.ENDC} over 4 weeks\n")

    print("Main differences:")
    print(f"  {Colors.OKGREEN}+{Colors.ENDC} End Cap 1 has higher visibility (2.0x vs 1.3x)")
    print(f"  {Colors.OKGREEN}+{Colors.ENDC} Better category alignment")
    print(f"  {Colors.FAIL}-{Colors.ENDC} Main Entrance has more foot traffic but lower conversion")


def show_competitive_analysis():
    """Show competitor analysis"""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}🏆 COMPETITIVE ANALYSIS:{Colors.ENDC}\n")

    print("Competitors in End Cap 1 - Beverages:")
    competitors = [
        ("Red Bull Original", 2.49, 1.52),
        ("Monster Energy Green", 2.79, 1.48),
        ("5-hour Energy", 3.99, 1.35)
    ]

    for name, price, roi in competitors:
        print(f"  • {name:<25} ${price:.2f}  ROI: {roi:.2f}")

    print(f"\n  Average Competitor ROI: {Colors.BOLD}1.45{Colors.ENDC}")
    print(f"  Your Predicted ROI: {Colors.BOLD}{Colors.OKGREEN}1.85{Colors.ENDC}")
    print(f"\n  {Colors.OKGREEN}✓ Your product will outperform competitors by 28%{Colors.ENDC}")


def show_api_demo():
    """Show how to use the API"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}🔌 API USAGE:{Colors.ENDC}\n")

    curl_command = """curl -X POST http://localhost:8000/api/analyze \\
  -H "Content-Type: application/json" \\
  -d '{
    "product_name": "Premium Energy Drink",
    "category": "Beverages",
    "price": 2.99,
    "budget": 5000.00,
    "target_sales": 1000,
    "target_customers": "Young adults 18-35",
    "expected_roi": 1.5
  }'"""

    print(f"{Colors.OKCYAN}{curl_command}{Colors.ENDC}\n")

    print(f"{Colors.BOLD}Response:{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{{\n"
          f'  "recommendations": {{\n'
          f'    "End Cap 1 - Beverages": 1.85,\n'
          f'    "Main Entrance Display": 1.62,\n'
          f'    ...\n'
          f'  }},\n'
          f'  "explanation": {{ ... }},\n'
          f'  "session_id": "uuid-here"\n'
          f"}}{Colors.ENDC}\n")


def show_interactive_menu():
    """Show interactive menu"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}🎮 INTERACTIVE FEATURES:{Colors.ENDC}\n")

    features = [
        ("📊 Analyze Product", "Get placement recommendations with ROI scores"),
        ("❓ Ask Questions", "Why this location? How about alternatives?"),
        ("🏆 Compare Options", "See all 10 locations ranked by ROI"),
        ("💰 Budget Analysis", "Find best placements within budget"),
        ("📈 Competitor View", "Compare against existing products"),
        ("🗺️  Visual Planogram", "Interactive 2D store map (web UI)")
    ]

    for feature, description in features:
        print(f"  {feature:<25} {description}")


def main():
    """Main demo function"""
    print_banner()

    # Load data
    products, locations = load_sample_data()

    if products and locations:
        print(f"{Colors.OKGREEN}✓ Loaded {len(products)} products and {len(locations)} locations{Colors.ENDC}")

    # Show visualizations
    print_store_planogram()
    show_product_analysis()
    show_comparison()
    show_competitive_analysis()
    show_api_demo()
    show_interactive_menu()

    # Next steps
    print(f"\n{Colors.BOLD}{Colors.HEADER}🚀 NEXT STEPS:{Colors.ENDC}\n")
    print(f"  1. {Colors.BOLD}Web UI:{Colors.ENDC} Open demo/planogram_viewer.html in browser")
    print(f"  2. {Colors.BOLD}API Server:{Colors.ENDC} Already running at http://localhost:8000")
    print(f"  3. {Colors.BOLD}API Docs:{Colors.ENDC} Visit http://localhost:8000/docs")
    print(f"  4. {Colors.BOLD}Try API:{Colors.ENDC} Use curl commands above")

    print(f"\n{Colors.BOLD}{Colors.OKGREEN}✨ System is ready! Start analyzing placements now!{Colors.ENDC}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Demo interrupted. Goodbye!{Colors.ENDC}\n")
        sys.exit(0)
