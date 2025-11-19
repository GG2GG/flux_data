# 🚀 Complete Setup Guide
## Everything You Need to Run The Placement Gambit

**Last Updated**: 2025-11-18
**For**: Web Demo (No Unity Required)

---

## ✅ What You Already Have

Good news! I checked your system and you already have:

- ✅ Python 3.9.6 installed
- ✅ All required Python packages
- ✅ .env file with Gemini API key configured
- ✅ Backend code ready
- ✅ Web planogram ready

**You're ready to run!** 🎉

---

## 🚀 Quick Start (You Can Run This Now!)

**Single command to start everything:**

```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data && ./start_demo.sh
```

This will:
1. Start Backend API (port 8000)
2. Start Web Server (port 8080)
3. Open your browser to the planogram

**That's it!** You're done! 🎊

---

## 📋 Complete Installation Checklist

Just to be thorough, here's what you need:

### 1. Python ✅ (You have this)

**Required**: Python 3.9 or higher
**You have**: Python 3.9.6

```bash
# Check your version
python3 --version
# Output: Python 3.9.6
```

---

### 2. Python Packages ✅ (You have these)

**Required packages:**
- fastapi
- uvicorn
- pydantic
- google-generativeai
- python-dotenv
- pandas
- numpy

**Verify:**
```bash
python3 -c "import fastapi, uvicorn, pydantic, google.generativeai, dotenv; print('✅ All packages installed')"
```

If you ever need to reinstall:
```bash
pip install fastapi uvicorn pydantic google-generativeai python-dotenv pandas numpy
```

---

### 3. Environment Variables ✅ (You have this)

**Required**: `.env` file with Gemini API key
**Location**: `/Users/gautham.ganesh/Documents/GG_Scripts/flux_data/.env`

Your `.env` file exists and has:
```
GEMINI_API_KEY=AIzaSyDSV6...5t3E ✅
```

---

### 4. Web Browser ✅ (You have this)

Any modern browser works:
- ✅ Chrome
- ✅ Firefox
- ✅ Safari
- ✅ Edge

---

### 5. Project Files ✅ (You have these)

All required files are in place:
```
/Users/gautham.ganesh/Documents/GG_Scripts/flux_data/
├── api/
│   ├── main.py                    ✅
│   ├── game_routes.py             ✅
│   └── ...
├── demo/
│   ├── planogram_final.html       ✅
│   └── ...
├── .env                           ✅
├── start_demo.sh                  ✅
└── ...
```

---

## 🎯 What You DON'T Need

### For Web Demo:
- ❌ Unity (only needed for game version)
- ❌ Unity Hub
- ❌ Visual Studio (for Unity)
- ❌ Additional servers
- ❌ Docker
- ❌ Database (uses in-memory storage)

---

## 🚀 Running the Demo

### Method 1: One Command (Recommended)

```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data && ./start_demo.sh
```

**This handles everything automatically!**

---

### Method 2: Manual (If you want more control)

**Terminal 1 - Backend API:**
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```

Wait for:
```
✅ API ready to serve requests!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Web Server:**
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m http.server 8080
```

**Browser:**
Open: http://localhost:8080/demo/planogram_final.html

---

## 🧪 Testing the Setup

### Test 1: Backend API

```bash
curl http://localhost:8000/api/health
```

**Expected:**
```json
{"status": "healthy", "version": "1.0.0"}
```

### Test 2: Web Server

```bash
curl -I http://localhost:8080/demo/planogram_final.html
```

**Expected:**
```
HTTP/1.0 200 OK
```

### Test 3: Create Game Session

```bash
curl -X POST http://localhost:8000/api/game/session/create \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "category": "Beverages",
    "price": 2.99,
    "budget": 1000,
    "target_sales": 500,
    "expected_roi": 1.5
  }'
```

**Expected:**
```json
{
  "session_id": "game_abc123...",
  "status": "active",
  "web_url": "http://localhost:8080/demo/planogram_final.html?session=game_abc123..."
}
```

---

## 🎮 Using the Web Demo

Once running:

1. **Open Browser**: http://localhost:8080/demo/planogram_final.html

2. **See the Store Map**: 2D planogram with shelf locations

3. **Click a Shelf**: View detailed ROI data for 5 shelf rows

4. **Select a Row**: See psychology insights and sales impact

5. **Ask the AI**: Use the chat to ask questions about placement strategy

6. **View Results**: See recommendations and ROI calculations

---

## 🛑 Stopping the Demo

**If using start_demo.sh:**
```bash
pkill -f python
```

**If running manually:**
Press `Ctrl+C` in each terminal window

---

## 🐛 Troubleshooting

### Issue: "Address already in use"

**Problem**: Port 8000 or 8080 is taken

**Solution:**
```bash
# Kill existing processes
pkill -f "python.*api.main"
pkill -f "python.*http.server"

# Wait 2 seconds
sleep 2

# Try again
./start_demo.sh
```

---

### Issue: "GEMINI_API_KEY not found"

**Problem**: Environment variable not loaded

**Check:**
```bash
cat /Users/gautham.ganesh/Documents/GG_Scripts/flux_data/.env | grep GEMINI
```

**Should see:**
```
GEMINI_API_KEY=AIzaSyDSV6...
```

If missing, create `.env` file:
```bash
echo "GEMINI_API_KEY=your_actual_key_here" > .env
```

---

### Issue: "Module not found"

**Problem**: Missing Python package

**Solution:**
```bash
# Install all dependencies
pip install fastapi uvicorn pydantic google-generativeai python-dotenv pandas numpy

# Or use requirements file if it exists
pip install -r requirements.txt
```

---

### Issue: "Browser doesn't open"

**Problem**: `open` command not working

**Solution:**
Manually open: http://localhost:8080/demo/planogram_final.html

---

### Issue: "Nothing happens when I click shelves"

**Problem**: Backend not running or not connected

**Check:**
```bash
curl http://localhost:8000/api/health
```

If fails, restart backend:
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```

---

## 📊 What Each Component Does

### Backend API (Port 8000)
**File**: `api/main.py`

**Features**:
- Multi-agent orchestration
- ROI calculations
- AI-powered explanations (Gemini)
- Game session management
- Historical data analysis

**Endpoints**:
- `/api/health` - Health check
- `/api/analyze` - Analyze product placement
- `/api/game/session/create` - Create game session
- `/api/game/rows/{location_id}` - Get shelf ROI data
- `/api/game/choice` - Record player choice
- `/docs` - Interactive API documentation

---

### Web Server (Port 8080)
**Directory**: `demo/`

**Serves**:
- `planogram_final.html` - Main planogram UI
- `simple_planogram.html` - Simple version
- `professional_planogram.html` - Professional version
- CSS and JavaScript files

**Features**:
- Interactive 2D store map
- Shelf detail modals
- AI chat consultant (Gemini)
- Real-time ROI display
- Visual feedback

---

## 🎯 System Architecture

```
┌─────────────────┐
│  Your Browser   │
│   Port: N/A     │
└────────┬────────┘
         │
         │ HTTP Requests
         │
    ┌────▼──────────────────────────┐
    │                                │
    │   Web Server (Port 8080)       │
    │   Serves: planogram_final.html │
    │                                │
    └────────┬───────────────────────┘
             │
             │ API Calls
             │
    ┌────────▼─────────────────────┐
    │                              │
    │  Backend API (Port 8000)     │
    │  - Multi-agent system        │
    │  - ROI calculations          │
    │  - Gemini AI integration     │
    │                              │
    └──────────────────────────────┘
             │
             │ External API
             │
    ┌────────▼─────────────────────┐
    │                              │
    │  Google Gemini API           │
    │  (External Service)          │
    │                              │
    └──────────────────────────────┘
```

---

## 📝 Quick Reference Commands

### Start Everything
```bash
./start_demo.sh
```

### Stop Everything
```bash
pkill -f python
```

### Check Status
```bash
# Backend
curl http://localhost:8000/api/health

# Web Server
curl -I http://localhost:8080/demo/planogram_final.html

# View backend logs (if using start_demo.sh)
tail -f /tmp/backend.log
```

### View API Documentation
```bash
open http://localhost:8000/docs
```

---

## 🎊 You're Ready!

**Everything is already installed and configured!**

Just run:
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data && ./start_demo.sh
```

And your web demo will start! 🚀

---

## 📚 Additional Resources

- **BACKEND_SERVERS_GUIDE.md** - Detailed server documentation
- **UNITY_MVP_SETUP.md** - Unity game setup (if you want to try later)
- **README_ANALYSIS.md** - Project overview
- **api/main.py** - Backend code
- **demo/planogram_final.html** - Web UI code

---

## 🆘 Still Need Help?

If something doesn't work:

1. **Check logs**: `/tmp/backend.log` and `/tmp/webserver.log`
2. **Verify Python version**: `python3 --version` (should be 3.9+)
3. **Check API key**: `cat .env | grep GEMINI`
4. **Test backend**: `curl http://localhost:8000/api/health`
5. **Kill all and restart**: `pkill -f python && sleep 2 && ./start_demo.sh`

---

**Happy demoing!** 🎉
