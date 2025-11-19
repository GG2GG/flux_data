"""
Test script to debug why LocationFilterAgent isn't filtering properly.
"""

import json
from utils.llm_client import get_llm_client

# Test product data
product = {
    'product_name': 'Face Cream',
    'category': 'Personal Care',
    'price': 1.5,
    'target_customers': 'Women, Beauty conscious'
}

# Test locations
locations = [
    {'name': 'End Cap 1 - Beverages', 'zone': 'End Cap', 'notes': 'End Cap in Beverages area - Front left of store'},
    {'name': 'Main Entrance Display', 'zone': 'Main Entrance', 'notes': 'Main Entrance display - Front right of store'},
    {'name': 'Checkout Lane 1', 'zone': 'Checkout', 'notes': 'Checkout area - Bottom center of store'},
    {'name': 'Beverage Aisle - Eye Level', 'zone': 'Eye Level', 'notes': 'Eye Level in Beverages area - Left side middle'},
    {'name': 'Snack Aisle - Eye Level', 'zone': 'Eye Level', 'notes': 'Eye Level in Snacks area - Center left'},
    {'name': 'Dairy Section - Regular', 'zone': 'Regular Shelf', 'notes': 'Regular Shelf in Dairy area - Center right'},
    {'name': 'Bakery Display', 'zone': 'Regular Shelf', 'notes': 'Regular Shelf in Bakery area - Right side middle'},
    {'name': 'End Cap 2 - Snacks', 'zone': 'End Cap', 'notes': 'End Cap in Snacks area - Front center'},
    {'name': 'Personal Care Aisle', 'zone': 'Regular Shelf', 'notes': 'Regular Shelf in Personal Care area - Front center-right'},
    {'name': 'Beverage Aisle - Bottom', 'zone': 'Bottom Shelf', 'notes': 'Bottom Shelf in Beverages area - Left side bottom'}
]

# System prompt (from filter agent)
system_prompt = """You are a retail placement expert. Your job is to identify which store locations make logical sense for a product.

Guidelines:
- Products should be placed in relevant aisles/sections
- Cosmetics go in personal care, not snacks
- Beverages go in beverage sections or checkout, not bakery
- Dairy products go in dairy or refrigerated sections
- Snacks go in snack aisles or checkout, not personal care
- Be pragmatic: End caps and checkouts work for many product types
- Consider impulse buying patterns

Respond with ONLY a JSON array of location names that make sense. No explanation."""

# User prompt (from filter agent)
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
print("TESTING FILTER AGENT LLM")
print("=" * 80)
print(f"\nProduct: {product['product_name']} ({product['category']})")
print(f"\nInput Locations: {len(locations)}")
for loc in locations:
    print(f"  - {loc['name']}")

print("\n" + "=" * 80)
print("CALLING LLM...")
print("=" * 80)

# Get LLM client with qwen2.5-coder:3b (same as filter agent)
import os
from dotenv import load_dotenv
from utils.llm_client import LLMClient

load_dotenv()

llm_client = LLMClient(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_API_BASE'),
    model="qwen2.5-coder:3b",
    temperature=0.3,
    max_tokens=300
)

if not llm_client or not llm_client.enabled:
    print("ERROR: LLM client not available!")
    exit(1)

print(f"LLM enabled: {llm_client.enabled}")
print(f"Model: {llm_client.model}")

# Call LLM
try:
    response = llm_client.generate(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.3,
        max_tokens=300,
        json_mode=False  # Don't use json_mode with local models
    )

    print("\n" + "=" * 80)
    print("RAW LLM RESPONSE:")
    print("=" * 80)
    print(response)
    print()

    # Try to parse response (same logic as filter agent)
    print("=" * 80)
    print("PARSING RESPONSE...")
    print("=" * 80)

    if not response or response.strip() == "":
        print("✗ LLM returned empty response")
    else:
        # Try to extract JSON array from response
        import re
        match = re.search(r'\[([^\]]+)\]', response, re.DOTALL)
        if match:
            try:
                json_str = '[' + match.group(1) + ']'
                valid_names = json.loads(json_str)
                print(f"✓ Successfully extracted and parsed JSON array")
                print(f"✓ Filtered locations: {len(valid_names)}")
                for name in valid_names:
                    print(f"  - {name}")
            except json.JSONDecodeError as e:
                print(f"✗ JSON parse error: {e}")
                print(f"Attempting to parse full response...")
                try:
                    valid_names = json.loads(response.strip())
                    print(f"✓ Parsed full response as JSON")
                    print(f"✓ Filtered locations: {len(valid_names)}")
                    for name in valid_names:
                        print(f"  - {name}")
                except:
                    print(f"✗ Could not parse response")
        else:
            print(f"✗ No JSON array found in response")
            print(f"Response preview: {response[:200]}")

    # Check what was filtered out
    print("\n" + "=" * 80)
    print("FILTERING ANALYSIS:")
    print("=" * 80)

    input_names = set(loc['name'] for loc in locations)
    output_names = set(valid_names) if 'valid_names' in locals() else input_names

    kept = output_names
    removed = input_names - output_names

    print(f"\nKept ({len(kept)} locations):")
    for name in kept:
        print(f"  ✓ {name}")

    print(f"\nRemoved ({len(removed)} locations):")
    for name in removed:
        print(f"  ✗ {name}")

    if len(removed) == 0:
        print("\n⚠️  WARNING: No locations were filtered! LLM kept everything.")

except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
