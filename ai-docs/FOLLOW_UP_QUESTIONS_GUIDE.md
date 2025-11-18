# 🤔 How to Ask Follow-Up Questions

After getting a product placement recommendation, you can ask follow-up questions to dig deeper into the analysis!

---

## **How It Works**

1. **First**, get a recommendation using `/api/analyze`
2. **Save** the `session_id` from the response
3. **Then**, ask follow-up questions using `/api/defend` with that `session_id`

---

## **Step-by-Step Example**

### **Step 1: Get Initial Recommendation**

**Endpoint:** `POST /api/analyze`

**Request:**
```json
{
  "product_name": "Premium Energy Drink",
  "category": "Beverages",
  "price": 3.99,
  "budget": 5000,
  "target_sales": 500,
  "target_customers": "Young adults",
  "expected_roi": 1.5
}
```

**Response (truncated):**
```json
{
  "recommendations": {
    "End Cap 1 - Beverages": 2.92,
    "Checkout Lane 1": 2.92,
    ...
  },
  "explanation": {...},
  "session_id": "9981b101-a2a8-41e1-bb15-64036eb50c2d",  ← SAVE THIS!
  "timestamp": "2025-11-17T20:17:00"
}
```

---

### **Step 2: Ask Follow-Up Questions**

**Endpoint:** `POST /api/defend`

**Request:**
```json
{
  "session_id": "9981b101-a2a8-41e1-bb15-64036eb50c2d",
  "question": "Why is End Cap better than Eye Level for this product?"
}
```

**Response:**
```json
{
  "answer": "End Cap 1 - Beverages outperforms Eye Level placement by 46%...[detailed analysis]",
  "session_id": "9981b101-a2a8-41e1-bb15-64036eb50c2d"
}
```

---

## **Example Follow-Up Questions**

### **1. Compare Locations**
```json
{
  "session_id": "YOUR_SESSION_ID",
  "question": "Why is End Cap better than Checkout for this product?"
}
```

### **2. Challenge the Recommendation**
```json
{
  "session_id": "YOUR_SESSION_ID",
  "question": "What if I chose Eye Level instead? What would happen?"
}
```

### **3. Ask About Budget**
```json
{
  "session_id": "YOUR_SESSION_ID",
  "question": "Can I afford a better location if I increase my budget to $7000?"
}
```

### **4. Ask About Competition**
```json
{
  "session_id": "YOUR_SESSION_ID",
  "question": "How do competing products perform in this location?"
}
```

### **5. Ask About Data Quality**
```json
{
  "session_id": "YOUR_SESSION_ID",
  "question": "How confident are you in this recommendation?"
}
```

### **6. Ask About Historical Performance**
```json
{
  "session_id": "YOUR_SESSION_ID",
  "question": "What similar products succeeded in End Cap locations?"
}
```

### **7. Ask About Risk**
```json
{
  "session_id": "YOUR_SESSION_ID",
  "question": "What are the risks of this placement?"
}
```

### **8. Ask About ROI Breakdown**
```json
{
  "session_id": "YOUR_SESSION_ID",
  "question": "What factors contribute most to the 2.92x ROI prediction?"
}
```

---

## **Using curl**

```bash
# Step 1: Get recommendation (save the session_id from response)
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
  }' | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['session_id'])"

# Step 2: Ask follow-up (replace SESSION_ID with actual value)
curl -X POST http://localhost:8000/api/defend \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID_HERE",
    "question": "Why is End Cap better than Eye Level?"
  }' | python3 -m json.tool
```

---

## **Using Postman**

### **Method 1: Manual Workflow**

1. **Run "Analyze Placement - Premium Energy Drink"**
2. **Copy `session_id`** from response
3. **Create new POST request:**
   - URL: `http://localhost:8000/api/defend`
   - Body (raw JSON):
   ```json
   {
     "session_id": "PASTE_SESSION_ID_HERE",
     "question": "Your question here"
   }
   ```
4. **Click Send**

### **Method 2: Use Environment Variable**

1. After getting recommendation, add this to **Tests** tab:
   ```javascript
   pm.environment.set("session_id", pm.response.json().session_id);
   ```

2. Create follow-up request with:
   ```json
   {
     "session_id": "{{session_id}}",
     "question": "Your question here"
   }
   ```

---

## **Using Swagger UI (Easiest!)**

1. **Open:** http://localhost:8000/docs

2. **First, run POST /api/analyze:**
   - Click "Try it out"
   - Fill in product details
   - Click "Execute"
   - **Copy the `session_id`** from response

3. **Then, run POST /api/defend:**
   - Scroll down to "POST /api/defend"
   - Click "Try it out"
   - Paste your `session_id`
   - Type your question
   - Click "Execute"

---

## **Session Management**

### **How Long Do Sessions Last?**
- Sessions are stored **in-memory** (lost on server restart)
- No expiration (stays until server restarts)
- Each analysis creates a new session

### **Can I Ask Multiple Questions?**
- ✅ Yes! Use the same `session_id` for multiple follow-ups
- The system remembers your product and recommendations

### **What Happens If Session Expires?**
- You'll get: `"Session not found. Please run /api/analyze first."`
- Solution: Run `/api/analyze` again to get a new `session_id`

---

## **Pro Tips**

1. **Save session_id immediately** after getting recommendations
2. **Ask specific questions** for better answers
3. **Compare locations** to understand trade-offs
4. **Ask "why" and "what if"** questions - the system is designed for this!
5. **Chain questions** - ask follow-ups to the answers

---

## **Complete Postman Workflow Example**

### **Request 1: GET /api/health**
Check server is ready ✅

### **Request 2: POST /api/analyze**
```json
{
  "product_name": "Organic Yogurt",
  "category": "Dairy",
  "price": 4.50,
  "budget": 3000,
  "target_sales": 400,
  "target_customers": "Health-conscious families",
  "expected_roi": 1.8
}
```
**→ Save session_id: `abc-123-def-456`**

### **Request 3: POST /api/defend**
```json
{
  "session_id": "abc-123-def-456",
  "question": "Why is this location better than others?"
}
```
**→ Get detailed answer ✅**

### **Request 4: POST /api/defend** (same session!)
```json
{
  "session_id": "abc-123-def-456",
  "question": "What if I chose Checkout instead?"
}
```
**→ Get comparison ✅**

---

## **Error Handling**

### **Error: "Session not found"**
```json
{
  "detail": "Session not found. Please run /api/analyze first."
}
```
**Solution:** Run `/api/analyze` again to create a new session

### **Error: "Field required"**
```json
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "field required"
    }
  ]
}
```
**Solution:** Make sure both `session_id` and `question` are in the request

---

## **Advanced: Automated Testing Script**

```bash
#!/bin/bash

# Get recommendation and extract session_id
SESSION_ID=$(curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "category": "Beverages",
    "price": 3.99,
    "budget": 5000,
    "target_sales": 500,
    "target_customers": "Test",
    "expected_roi": 1.5
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

echo "Session ID: $SESSION_ID"

# Ask multiple follow-up questions
QUESTIONS=(
  "Why is this the best location?"
  "What are the risks?"
  "How confident are you in this prediction?"
)

for Q in "${QUESTIONS[@]}"; do
  echo -e "\n\nQ: $Q"
  curl -s -X POST http://localhost:8000/api/defend \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"$SESSION_ID\", \"question\": \"$Q\"}" \
    | python3 -c "import sys, json; print(json.load(sys.stdin)['answer'][:200] + '...')"
done
```

---

**Ready to ask questions? Get a `session_id` first, then start asking!** 🚀
