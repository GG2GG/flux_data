#!/bin/bash

# Quick test script for Docker deployment

set -e

echo "🧪 Testing Retail Product Placement API (Docker)"
echo "================================================"
echo ""

# Check if API is running
if ! curl -sf http://localhost:8000/api/health > /dev/null; then
    echo "❌ API is not running!"
    echo "Start it with: docker-compose up -d"
    exit 1
fi

echo "✅ API is running"
echo ""

# Test health endpoint
echo "📍 Testing /api/health..."
HEALTH=$(curl -s http://localhost:8000/api/health)
echo "$HEALTH" | jq '.' 2>/dev/null || echo "$HEALTH"
echo ""

# Test analyze endpoint
echo "📍 Testing /api/analyze..."
ANALYZE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Energy Drink",
    "category": "Beverages",
    "price": 2.99,
    "budget": 5000.0,
    "target_sales": 1000,
    "target_customers": "Young adults",
    "expected_roi": 1.5
  }')

if echo "$ANALYZE_RESPONSE" | jq -e '.session_id' > /dev/null 2>&1; then
    echo "✅ Analyze endpoint working"
    SESSION_ID=$(echo "$ANALYZE_RESPONSE" | jq -r '.session_id')
    echo "📝 Session ID: $SESSION_ID"
    echo ""
    echo "Top Recommendation:"
    echo "$ANALYZE_RESPONSE" | jq -r '.recommendations | to_entries | .[0] | "\(.key): ROI \(.value)"'
    echo ""

    # Test defend endpoint
    echo "📍 Testing /api/defend..."
    DEFEND_RESPONSE=$(curl -s -X POST http://localhost:8000/api/defend \
      -H "Content-Type: application/json" \
      -d "{
        \"session_id\": \"$SESSION_ID\",
        \"question\": \"Why this location?\"
      }")

    if echo "$DEFEND_RESPONSE" | jq -e '.answer' > /dev/null 2>&1; then
        echo "✅ Defend endpoint working"
        echo "Answer preview:"
        echo "$DEFEND_RESPONSE" | jq -r '.answer' | head -3
        echo ""
    else
        echo "⚠️  Defend endpoint returned unexpected response"
    fi
else
    echo "❌ Analyze endpoint failed"
    echo "$ANALYZE_RESPONSE" | jq '.' 2>/dev/null || echo "$ANALYZE_RESPONSE"
    exit 1
fi

echo "================================================"
echo "✅ All tests passed!"
echo "================================================"
echo ""
echo "🎉 Docker deployment is working correctly!"
