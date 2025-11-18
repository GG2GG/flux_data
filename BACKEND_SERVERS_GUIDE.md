# 🖥️ Backend Servers Guide
## Complete Overview of Required Servers

**Last Updated**: 2025-11-18
**Project**: The Placement Gambit - Retail Placement Optimization System

---

## 📋 Quick Summary

You need to run **1-2 servers** depending on what you're building:

| Server | Port | Required For | Status |
|--------|------|--------------|--------|
| **FastAPI Backend** | 8000 | Unity Game + Web UI | ✅ **REQUIRED** |
| **Web UI Server** | 8080 | Web Planogram Demo | ⚠️ Optional (Unity only needs Backend) |

---

## 🎯 Which Servers Do I Need?

### For Unity Game Development (Recommended)
✅ **Only FastAPI Backend (Port 8000)**

```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```

**Why?**
- Unity communicates directly with the FastAPI backend
- No web server needed
- All game endpoints available at `http://localhost:8000`

---

### For Web Planogram Demo
✅ **FastAPI Backend (Port 8000)** + ✅ **Web Server (Port 8080)**

**Terminal 1 - Backend API:**
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```

**Terminal 2 - Web Server:**
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m http.server 8080
```

**Why?**
- Web planogram needs both servers
- Backend provides data, web server serves HTML/CSS/JS
- Access at `http://localhost:8080/demo/planogram_final.html`

---

## 🔧 Server 1: FastAPI Backend (REQUIRED)

### What It Does
- **Primary backend API** for the entire system
- Handles all business logic and data processing
- Multi-agent orchestration system
- ROI calculations and recommendations
- Game session management
- Unity integration endpoints

### Port
**8000** (http://localhost:8000)

### How to Start

**Method 1 - Recommended (with auto-reload):**
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```

**Method 2 - Using uvicorn directly:**
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data/api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### What Happens on Startup

You'll see initialization logs:
```
🚀 Starting Retail Placement API Server...
📖 API Documentation: http://localhost:8000/docs
🔍 Health Check: http://localhost:8000/api/health

✅ Loaded 30 products
✅ Loaded 10 locations
✅ Loaded 300 ROI scores
✅ Loaded 300 feature importance scores
✅ Loaded 55 competitor products
✅ Loaded 150 historical examples

🔧 INITIALIZING AI LANGUAGE MODEL
✅ Found GEMINI_API_KEY
✅ Using AI Provider: GEMINI
🎯 Selected Model: gemini-2.0-flash
✅ Gemini initialized successfully!

✅ Orchestrator initialized
🎉 API ready to serve requests!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Key Features Loaded

1. **Multi-Agent System**:
   - InputAgent - Validates product data
   - AnalyzerAgent - ROI calculations
   - ExplainerAgent - AI-powered explanations (Gemini)

2. **Data Loaded**:
   - 30 products
   - 10 store locations
   - 300 ROI scores
   - 55 competitor products
   - 150 historical examples

3. **AI Integration**:
   - Google Gemini API (gemini-2.0-flash)
   - Natural language explanations
   - Research-backed recommendations

### API Endpoints Available

#### **Core Endpoints** (Original)
- `POST /api/analyze` - Analyze product placement
- `GET /api/location/{location_id}/rows` - Get shelf rows
- `GET /api/health` - Health check
- `GET /docs` - Interactive API documentation

#### **Game Integration Endpoints** (New - for Unity)
- `POST /api/game/session/create` - Create game session
- `GET /api/game/session/{session_id}` - Get session data
- `POST /api/game/session/sync` - Sync Unity-Web state
- `GET /api/game/rows/{location_id}` - Get shelf ROI data
- `POST /api/game/choice` - Record player choice
- `GET /api/game/agent/dialogue/{category}/{row}` - Get NPC dialogue
- `GET /api/game/sessions/active` - List active sessions
- `DELETE /api/game/session/{session_id}` - Delete session

### Verify It's Running

**Terminal:**
```bash
curl http://localhost:8000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-18T11:08:43Z"
}
```

**Browser:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

### Dependencies Required

**Environment Variables (.env file):**
```bash
GEMINI_API_KEY=your_api_key_here
```

**Python Packages:**
```
fastapi
uvicorn
pydantic
google-generativeai
python-dotenv
```

Install all:
```bash
pip install fastapi uvicorn pydantic google-generativeai python-dotenv
```

---

## 🌐 Server 2: Web UI Server (OPTIONAL)

### What It Does
- Serves static HTML/CSS/JS files
- Provides web planogram interface
- Demo and testing interface
- **NOT needed for Unity game**

### Port
**8080** (http://localhost:8080)

### How to Start

**Using Python's built-in server:**
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m http.server 8080
```

### What Happens on Startup

```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

### Access Points

- **Main Planogram**: http://localhost:8080/demo/planogram_final.html
- **Simple Planogram**: http://localhost:8080/demo/simple_planogram.html
- **Professional Version**: http://localhost:8080/demo/professional_planogram.html

### When to Use

Use this server when:
- ✅ Testing web planogram UI
- ✅ Demoing to stakeholders
- ✅ Developing web features
- ❌ **NOT needed for Unity development**

---

## 📊 Current Server Status

Based on your system:

```bash
# Check what's running
lsof -i -P | grep LISTEN | grep -E "(8000|8080)"
```

**Currently Running:**
```
Python (PID 45637) - Port 8000 - FastAPI Backend
Python (PID 45726) - Port 8000 - FastAPI Backend (duplicate)
Python (PID 47039) - Port 8080 - Web Server
```

⚠️ **Note**: You have 2 instances of the backend running (PIDs 45637, 45726). Only one is needed.

---

## 🛑 How to Stop Servers

### Stop All Python Servers
```bash
# Kill all Python servers on ports 8000 and 8080
pkill -f "python.*8000"
pkill -f "python.*8080"
```

### Stop Specific Server by PID
```bash
# Check what's running
lsof -i :8000

# Kill specific process
kill 45726  # Replace with actual PID
```

### Graceful Shutdown
In the terminal where server is running:
- Press `Ctrl+C`

---

## 🚀 Quick Start Commands

### For Unity Development

**Single Terminal:**
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```

✅ That's it! Unity can now connect to http://localhost:8000

---

### For Web Demo

**Terminal 1 - Backend:**
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```

**Terminal 2 - Web Server:**
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m http.server 8080
```

**Browser:**
- Open: http://localhost:8080/demo/planogram_final.html

---

## 🔍 Troubleshooting

### "Address already in use"

**Problem**: Port 8000 or 8080 already in use

**Solution 1 - Find and kill process:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

**Solution 2 - Use different port:**
```bash
# Run on port 8001 instead
cd api
uvicorn main:app --port 8001
```

Then update Unity API client:
```csharp
private string apiBaseUrl = "http://localhost:8001/api";
```

---

### "Cannot connect to API"

**Problem**: Unity or web can't reach backend

**Checklist:**
1. ✅ Backend running? Check: `curl http://localhost:8000/api/health`
2. ✅ Correct port? Should be 8000
3. ✅ Firewall blocking? Try disabling temporarily
4. ✅ CORS enabled? Backend has CORS configured for all origins

**Debug:**
```bash
# Check if API responds
curl -v http://localhost:8000/api/health

# Check game endpoint
curl -X POST http://localhost:8000/api/game/session/create \
  -H "Content-Type: application/json" \
  -d '{"product_name":"Test","category":"Beverages","price":2.99,"budget":1000,"target_sales":500,"expected_roi":1.5}'
```

---

### "GEMINI_API_KEY not found"

**Problem**: Missing environment variable

**Solution:**
```bash
# Create .env file
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env

# Restart backend
python3 -m api.main
```

---

## 📦 What Runs Where

### Backend API (Port 8000)
**File**: `/Users/gautham.ganesh/Documents/GG_Scripts/flux_data/api/main.py`

**Components**:
- FastAPI application
- Multi-agent orchestrator
- Gemini AI integration
- ROI calculation engine
- Game session manager
- Data loaders (products, locations, scores)

**Connects To**:
- Google Gemini API (external)
- Local data files (CSV, JSON)
- Unity game client
- Web planogram UI

---

### Web Server (Port 8080)
**Directory**: `/Users/gautham.ganesh/Documents/GG_Scripts/flux_data/`

**Serves**:
- HTML files in `demo/`
- CSS stylesheets
- JavaScript files
- Static assets

**Connects To**:
- Backend API on port 8000
- Gemini API directly (for chat)

---

## 🎯 Recommended Setup

### Daily Development Workflow

**1. Start Backend (Required)**
```bash
# Terminal 1
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main

# Wait for: 🎉 API ready to serve requests!
```

**2. Start Unity (For Game Development)**
```bash
# Open Unity Hub
# Open project: /Users/gautham.ganesh/Downloads/The Placement Gambit
# Press Play
```

**3. Start Web Server (For Web Testing)**
```bash
# Terminal 2 (optional)
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m http.server 8080
```

---

## 🔗 Related Documentation

- [UNITY_MVP_SETUP.md](./UNITY_MVP_SETUP.md) - Unity integration guide
- [INTEGRATION_COMPLETE.md](./INTEGRATION_COMPLETE.md) - Web-backend integration
- [README_ANALYSIS.md](./README_ANALYSIS.md) - Project overview

---

## 📝 Summary

### Minimum Required (Unity Only)
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```
**That's it!** Unity connects to http://localhost:8000

### Full Stack (Web + Unity)
**Terminal 1:**
```bash
python3 -m api.main  # Port 8000
```

**Terminal 2:**
```bash
python3 -m http.server 8080  # Port 8080
```

**Browser**: http://localhost:8080/demo/planogram_final.html
**Unity**: Connects to http://localhost:8000

---

**Pro Tip**: Keep the backend running in a dedicated terminal tab. It auto-reloads on file changes during development! 🔄
