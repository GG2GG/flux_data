# How to Start the API Server

## Quick Start

```bash
cd /Users/raghul.ponnusamy/Research/hackathon/retail-product-placement-agent/flux_data

# Start the server
uv run uvicorn api.main:app --reload --port 8000
```

**Server will start on:** `http://localhost:8000`

**Wait for this message:**
```
INFO:     Application startup complete.
🎉 API ready to serve requests!
```

---

## Test It's Working

### 1. Health Check (in another terminal):
```bash
curl http://localhost:8000/api/health | python3 -m json.tool
```

**Expected output:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "data_quality": {
    "quality_level": "excellent",
    "confidence_score": 0.95,
    "total_transactions": 9360,
    "computed_metrics": 15,
    "default_metrics": 5
  },
  "data_loaded": {
    "products": 60,
    "locations": 20
  }
}
```

### 2. Test Recommendation:
```bash
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
  }'
```

**This will take ~90 seconds** (Deepseek-R1 generating explanation)

---

## Open in Browser

**Swagger UI (Interactive API Docs):**
```
http://localhost:8000/docs
```

**ReDoc (Alternative API Docs):**
```
http://localhost:8000/redoc
```

---

## Using Postman

1. **Import Collection:**
   - File: `Retail_Placement_API.postman_collection.json`
   - In Postman: Import → Upload Files

2. **Test Endpoints:**
   - Health Check → GET `http://localhost:8000/api/health`
   - Analyze Placement → POST `http://localhost:8000/api/analyze`

---

## Response Time

| Component | Time |
|-----------|------|
| Server startup | ~20 seconds (loads all data & computes metrics) |
| Health check | < 50ms |
| Recommendation (with LLM) | **~90 seconds** (Deepseek-R1 thinking) |
| Recommendation (without LLM) | < 1 second |

---

## Troubleshooting

### Port Already in Use:
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uv run uvicorn api.main:app --reload --port 8001
```

### Server Won't Start:
```bash
# Make sure you're in the right directory
cd /Users/raghul.ponnusamy/Research/hackathon/retail-product-placement-agent/flux_data

# Check dependencies
uv sync

# Check if .env file exists
ls -la .env

# Recompute metrics if needed
uv run python -m utils.adaptive_data_manager
```

### LLM Too Slow:
Disable LLM for instant responses (uses templates):
```bash
# Edit .env and comment out:
# OPENAI_API_KEY=ollama

# Then restart server
```

---

## Environment Variables

The server reads from `.env`:
```bash
# For Ollama/Deepseek-R1
OPENAI_API_KEY=ollama
OPENAI_API_BASE=http://localhost:11434/v1
LLM_MODEL=deepseek-r1:latest
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Check server status & data quality |
| `/api/analyze` | POST | Get placement recommendations |
| `/docs` | GET | Swagger UI (interactive docs) |
| `/redoc` | GET | ReDoc (alternative docs) |

---

## Ready to Start!

```bash
uv run uvicorn api.main:app --reload --port 8000
```

Then open: **http://localhost:8000/docs** 🚀
