"""
Test the strict LLM prompt with Coca Cola.
"""

import os
from dotenv import load_dotenv
from utils.llm_client import LLMClient

load_dotenv()

# Coca Cola test
product = {
    'product_name': 'Coca Cola',
    'category': 'Beverages',
    'price': 0.5,
    'target_customers': 'Young Adults 18-35'
}

locations = [
    {'name': 'End Cap 1 - Beverages', 'zone': 'End Cap', 'notes': 'End Cap in Beverages area'},
    {'name': 'Main Entrance Display', 'zone': 'Main Entrance', 'notes': 'Main Entrance display'},
    {'name': 'Checkout Lane 1', 'zone': 'Checkout', 'notes': 'Checkout area'},
    {'name': 'Beverage Aisle - Eye Level', 'zone': 'Eye Level', 'notes': 'Eye Level in Beverages area'},
    {'name': 'Snack Aisle - Eye Level', 'zone': 'Eye Level', 'notes': 'Eye Level in Snacks area'},
    {'name': 'Dairy Section - Regular', 'zone': 'Regular Shelf', 'notes': 'Regular Shelf in Dairy area'},
    {'name': 'Bakery Display', 'zone': 'Regular Shelf', 'notes': 'Regular Shelf in Bakery area'},
    {'name': 'End Cap 2 - Snacks', 'zone': 'End Cap', 'notes': 'End Cap in Snacks area'},
    {'name': 'Personal Care Aisle', 'zone': 'Regular Shelf', 'notes': 'Regular Shelf in Personal Care area'},
    {'name': 'Beverage Aisle - Bottom', 'zone': 'Bottom Shelf', 'notes': 'Bottom Shelf in Beverages area'}
]

system_prompt = """You are a STRICT retail placement expert. Your job is to REJECT any location that doesn't make perfect sense for the product.

GOLDEN RULE: Better to recommend 2 perfect locations than 5 with irrelevant ones. BE STRICT.

STRICT CATEGORY-LOCATION COMPATIBILITY:
✓ Beverages → ONLY: Beverage Aisles, Checkout (impulse), Main Entrance (impulse)
✓ Personal Care/Cosmetics → ONLY: Personal Care Aisles, Checkout (impulse), Main Entrance (impulse)
✓ Snacks → ONLY: Snack Aisles, Checkout (impulse), Main Entrance (impulse)
✓ Dairy → ONLY: Dairy Sections, Checkout (impulse), Main Entrance (impulse)
✓ Bakery → ONLY: Bakery Sections, Checkout (impulse), Main Entrance (impulse)

NEVER ALLOW - ZERO TOLERANCE:
✗ Beverages in: Personal Care, Bakery, Dairy, Snack-specific aisles
✗ Personal Care in: Beverage, Snack, Dairy, Bakery aisles
✗ Snacks in: Personal Care, Dairy, Bakery aisles (beverages OK for impulse)
✗ Dairy in: Personal Care, Beverage, Snack, Bakery aisles
✗ Cross-category placements UNLESS it's Checkout or Main Entrance

ENDCAP RULES:
- Only allow endcaps if they match the product category
- "End Cap 1 - Beverages" → ONLY for Beverages
- "End Cap 2 - Snacks" → ONLY for Snacks
- Generic endcaps → Allow for any category

When in doubt, REJECT. Quality over quantity.

Respond with ONLY a JSON array of location names that make sense. No explanation."""

location_list = [f"- {loc['name']} ({loc['zone']}): {loc['notes']}" for loc in locations]
user_prompt = f"""Product: {product['product_name']}
Category: {product['category']}
Price: ${product['price']}
Target Customers: {product['target_customers']}

Available Locations:
{chr(10).join(location_list)}

Return JSON array of location names that make logical sense for this product.
Example: ["Location 1", "Location 2", "Location 3"]"""

print("=" * 80)
print("TESTING STRICT LLM PROMPT WITH COCA COLA")
print("=" * 80)
print()
print(f"Product: {product['product_name']} ({product['category']})")
print(f"Input locations: {len(locations)}")
print()

# Call LLM
llm_client = LLMClient(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_API_BASE'),
    model="qwen2.5-coder:3b",
    temperature=0.1,  # Very low for maximum strictness
    max_tokens=300
)

print("Calling LLM with STRICT prompt...")
print()

response = llm_client.generate(
    prompt=user_prompt,
    system_prompt=system_prompt,
    temperature=0.1,
    max_tokens=300,
    json_mode=False
)

print("=" * 80)
print("LLM RESPONSE:")
print("=" * 80)
print(response)
print()

# Parse
import json
import re
match = re.search(r'\[([^\]]+)\]', response, re.DOTALL)
if match:
    try:
        json_str = '[' + match.group(1) + ']'
        valid_names = json.loads(json_str)

        print("=" * 80)
        print("FILTERED RESULTS:")
        print("=" * 80)
        print(f"Kept: {len(valid_names)}/{len(locations)} locations")
        print()

        for name in valid_names:
            # Check if appropriate
            name_lower = name.lower()
            is_appropriate = (
                'beverage' in name_lower or
                'checkout' in name_lower or
                'main entrance' in name_lower or
                'entrance' in name_lower
            )
            symbol = "✅" if is_appropriate else "❌"
            print(f"  {symbol} {name}")

        print()
        print("Filtered out:")
        for loc in locations:
            if loc['name'] not in valid_names:
                # Check if should be kept
                name_lower = loc['name'].lower()
                should_keep = (
                    'beverage' in name_lower or
                    'checkout' in name_lower or
                    'main entrance' in name_lower
                )
                symbol = "❌" if should_keep else "✅"
                print(f"  {symbol} {loc['name']}")

    except Exception as e:
        print(f"Parse error: {e}")
else:
    print("Could not find JSON array in response")
