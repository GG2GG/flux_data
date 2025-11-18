# 🎮 Unity Installation & Setup Guide
## Complete Guide to Run "The Placement Gambit" Unity Game

**Last Updated**: 2025-11-18
**Platform**: macOS
**Unity Project**: `/Users/gautham.ganesh/Downloads/The Placement Gambit`

---

## 📋 What You Need to Install

### 1. Unity Hub (Required)
**What**: Manages Unity Editor versions and projects
**Download**: https://unity.com/download
**Size**: ~150 MB
**Free**: Yes

### 2. Unity Editor (Required)
**Version Needed**: Unity 2021.3 LTS or newer
**Recommended**: Unity 2022.3 LTS (Long Term Support)
**Size**: ~3-4 GB
**Free**: Unity Personal (for learning/hobby projects)

### 3. Visual Studio for Mac or VS Code (Recommended)
**What**: Code editor for C# scripts
**VS Code**: https://code.visualstudio.com (Lighter, faster)
**Visual Studio**: https://visualstudio.microsoft.com/vs/mac/
**Free**: Yes

### 4. Backend API (You Already Have This)
**Status**: ✅ Already installed
**Python**: Already set up
**Just needs to be running**

---

## 🚀 Step-by-Step Installation

### Step 1: Install Unity Hub

**1. Download Unity Hub:**
- Go to: https://unity.com/download
- Click "Download Unity Hub"
- Save the DMG file

**2. Install:**
```bash
# Open the downloaded DMG
open ~/Downloads/UnityHubSetup.dmg

# Drag Unity Hub to Applications
# Then open it from Applications
```

**3. Create Unity Account:**
- Open Unity Hub
- Sign in or create free account
- Activate Unity Personal license (free)

**Time**: 5-10 minutes

---

### Step 2: Install Unity Editor

**1. Open Unity Hub**

**2. Go to "Installs" tab**

**3. Click "Install Editor"**

**4. Choose Version:**
- Recommended: **Unity 2022.3 LTS** (Long Term Support)
- Or any 2021.3+ version

**5. Select Modules:**
During installation, select these modules:
- ✅ **Mac Build Support (Mono)** - Required
- ✅ **Documentation** - Helpful
- ✅ **WebGL Build Support** - Optional (if you want web builds)
- ❌ iOS/Android - Skip unless you need mobile

**6. Accept Terms & Install**

**Download Size**: ~3-4 GB
**Installation Time**: 20-40 minutes (depends on internet speed)

```bash
# You can check installation progress in Unity Hub
```

---

### Step 3: Install Code Editor (Optional but Recommended)

**Option A: VS Code (Recommended - Lighter)**

```bash
# Download from https://code.visualstudio.com
# Or install via Homebrew:
brew install --cask visual-studio-code

# Install C# extension
code --install-extension ms-dotnettools.csharp
```

**Option B: Visual Studio for Mac**

Download from: https://visualstudio.microsoft.com/vs/mac/

---

### Step 4: Verify Your Unity Project Exists

Your Unity project is already here:

```bash
ls "/Users/gautham.ganesh/Downloads/The Placement Gambit"
```

**Should see:**
```
Assets/
Library/
Packages/
ProjectSettings/
UserSettings/
```

✅ **Project exists!**

---

## 🎮 Opening & Running the Unity Project

### Step 1: Start Backend API (REQUIRED)

**Terminal 1:**
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```

**Wait for:**
```
✅ API ready to serve requests!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify:**
```bash
curl http://localhost:8000/api/health
```

**Keep this terminal running!**

---

### Step 2: Open Unity Project

**1. Open Unity Hub**

**2. Click "Projects" tab**

**3. Click "Add" → "Add project from disk"**

**4. Navigate to:**
```
/Users/gautham.ganesh/Downloads/The Placement Gambit
```

**5. Click "Add Project"**

**6. Double-click the project to open it**

**First Open:**
- Unity will import all assets
- This takes 5-15 minutes first time
- Be patient! Don't close Unity

---

### Step 3: Set Up Game Systems in Unity Editor

**Once Unity opens, follow these steps:**

#### A. Create GameSystems GameObject

1. In **Hierarchy** window: `Right-click → Create Empty`
2. Rename to: `GameSystems`
3. Select `GameSystems` in Hierarchy
4. In **Inspector** window: `Add Component`
5. Search for: `GameSetupManager`
6. Click to add it
7. Check these boxes in Inspector:
   - ✅ Auto Create Game Manager
   - ✅ Auto Create API Client
   - ✅ Enable Debug Logs
   - ✅ Test API Connection

#### B. Check Console for Initialization

**Window → General → Console**

You should see:
```
🚀 GameSetupManager: Initializing game systems...
✅ GameManager created
✅ API Client created
🔌 Testing API connection...
✅ API Connection successful! Test session: game_abc123...
```

If you see errors, the backend isn't running. Go back to Step 1.

---

### Step 4: Test the Game

**1. Press the Play button** (▶️ at top center)

**2. Check Console** for:
```
✅ GameManager created
✅ API Client created
✅ API Connection successful!
```

**3. Game should start!**

If you see your existing game scene with the player, you're ready!

---

### Step 5: Add Shelves to Your Scene (If Not Present)

The Unity MVP scripts are already in your Assets folder. If your scene doesn't have shelves yet:

#### Create Store Scene

**1. Create New Scene:**
- `File → New Scene → 2D`
- Save as: `Store`

**2. Create Canvas:**
- `Right-click in Hierarchy → UI → Canvas`
- Set Canvas Scaler to "Scale with Screen Size"

**3. Create Shelves:**

For each shelf location you want:

```
Right-click in Hierarchy → 2D Object → Sprites → Square
```

Configure each shelf:
- Rename: `Shelf_Beverages`, `Shelf_DryGoods`, etc.
- Position: Space them out (e.g., 0,0), (5,0), (10,0)
- Add Component: `ShelfInteractable`
- Set in Inspector:
  - Location ID: `loc_001`, `loc_003`, etc.
  - Location Name: "Beverages Aisle", etc.
  - Zone: "Main Aisle"
- Add Component: `BoxCollider2D`
  - Set "Is Trigger" to ✅

**4. Create ShelfDetailUI Modal:**

Follow the detailed instructions in: [UNITY_MVP_SETUP.md](./UNITY_MVP_SETUP.md) Section "Step 5"

---

## 📦 What's Already Done

These files were created in your Unity project's Assets folder:

✅ **Core Systems:**
- GameManager.cs
- RetailPlacementAPI.cs
- GameSetupManager.cs

✅ **Data Models:**
- ProductData.cs
- SessionData.cs
- ShelfData.cs

✅ **Gameplay:**
- ShelfInteractable.cs
- ShelfDetailUI.cs
- ShelfRowUI.cs
- ProductSetupUI.cs

✅ **Existing Game Files:**
- DialogueManager.cs
- GambitAgent.cs
- PlayerMovement.cs
- NPCInteraction.cs

**All code is ready to use!**

---

## 🎯 Complete Workflow

### Daily Development:

**1. Start Backend:**
```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```

**2. Open Unity Hub**
- Click on "The Placement Gambit" project
- Wait for Unity to load

**3. Press Play** (▶️)

**4. Test:**
- Walk around (WASD)
- Approach shelves
- Press E to view shelf details
- Select rows to see ROI data

**5. Make Changes:**
- Edit C# scripts in VS Code
- Unity auto-reloads when you save
- Press Play again to test

---

## 🐛 Troubleshooting

### Issue: "Unity Hub won't open"

**macOS Security:**
```bash
# Allow Unity Hub in Security & Privacy
System Preferences → Security & Privacy → General
# Click "Open Anyway" for Unity Hub
```

---

### Issue: "Can't install Unity Editor"

**Check disk space:**
```bash
df -h
# Need at least 10 GB free
```

**Check internet:**
- Editor download is 3-4 GB
- Use stable connection

---

### Issue: "Unity project won't open"

**Check Unity version:**
- Project may require specific Unity version
- Check `ProjectSettings/ProjectVersion.txt` in project folder
- Install matching Unity version in Unity Hub

```bash
cat "/Users/gautham.ganesh/Downloads/The Placement Gambit/ProjectSettings/ProjectVersion.txt"
```

---

### Issue: "Scripts have errors"

**Common fixes:**

1. **Missing TextMeshPro:**
```
Window → TextMeshPro → Import TMP Essential Resources
```

2. **API not running:**
```bash
# Start backend
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```

3. **Reimport scripts:**
```
Right-click on Assets folder → Reimport All
```

---

### Issue: "API Connection failed"

**Check backend is running:**
```bash
curl http://localhost:8000/api/health
```

**Check Unity API URL:**
Open `RetailPlacementAPI.cs` and verify:
```csharp
private string apiBaseUrl = "http://localhost:8000/api";
```

---

## 📊 System Requirements

### Minimum:
- **OS**: macOS 10.14+
- **RAM**: 8 GB
- **Disk**: 10 GB free
- **CPU**: Intel Core i5 or M1
- **GPU**: Any Metal-compatible

### Recommended:
- **OS**: macOS 12.0+
- **RAM**: 16 GB
- **Disk**: 20 GB free
- **CPU**: M1/M2 or Intel i7
- **GPU**: Apple Silicon or dedicated GPU

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Download Unity Hub | 2-5 min |
| Install Unity Hub | 2-3 min |
| Download Unity Editor | 15-30 min |
| Install Unity Editor | 10-20 min |
| Open Unity project (first time) | 5-15 min |
| Setup GameSystems | 5 min |
| Test game | 2 min |
| **TOTAL** | **40-80 minutes** |

After first setup, opening Unity takes 1-2 minutes.

---

## 🎮 Quick Start Checklist

### Before You Start Unity:
- [ ] Download Unity Hub
- [ ] Install Unity Hub
- [ ] Create Unity account
- [ ] Install Unity Editor (2021.3 LTS or newer)
- [ ] Install VS Code (optional)
- [ ] Backend API running (`python3 -m api.main`)

### First Time Opening Project:
- [ ] Add project to Unity Hub
- [ ] Open project (wait for import)
- [ ] Create GameSystems GameObject
- [ ] Add GameSetupManager component
- [ ] Check console for successful API connection

### Every Time You Run:
- [ ] Start backend: `python3 -m api.main`
- [ ] Open Unity Hub
- [ ] Click "The Placement Gambit" project
- [ ] Press Play ▶️
- [ ] Test functionality

---

## 📚 Documentation References

**Unity Setup:**
- [UNITY_MVP_SETUP.md](./UNITY_MVP_SETUP.md) - Detailed Unity Editor setup
- [UNITY_MVP_COMPLETE.md](./UNITY_MVP_COMPLETE.md) - What was built

**Backend:**
- [BACKEND_SERVERS_GUIDE.md](./BACKEND_SERVERS_GUIDE.md) - Backend documentation
- [COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md) - Full setup for web demo

**Code:**
- [UNITY_STARTER_TEMPLATES.md](./UNITY_STARTER_TEMPLATES.md) - Code templates used
- [UNITY_TRANSFORMATION_ANALYSIS.md](./UNITY_TRANSFORMATION_ANALYSIS.md) - Architecture

---

## 🎯 Summary

**To run Unity version:**

1. **Install Unity** (40-60 min one-time setup)
   - Unity Hub: https://unity.com/download
   - Unity Editor 2022.3 LTS

2. **Start Backend** (every time)
   ```bash
   cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
   python3 -m api.main
   ```

3. **Open Unity** (every time)
   - Unity Hub → The Placement Gambit
   - Press Play ▶️

4. **Play!** 🎮

---

**First time setup takes 40-80 minutes. After that, starting takes 2 minutes!**

Download Unity now: **https://unity.com/download** 🚀
