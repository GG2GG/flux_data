# 🎮 Unity MVP Setup Guide
## The Placement Gambit - Backend Integration

**Status**: ✅ All scripts created and ready for integration
**Time Estimate**: 30-45 minutes to set up in Unity Editor
**Prerequisites**: Unity 2021.3+, Backend API running on port 8000

---

## 📁 Files Created

All C# scripts have been created in `/Users/gautham.ganesh/Downloads/The Placement Gambit/Assets/`:

### Core Systems (✅ Complete)
1. **GameManager.cs** - State machine for game flow
2. **RetailPlacementAPI.cs** - API client for backend communication
3. **GameSetupManager.cs** - Initializes all systems on startup

### Data Models (✅ Complete)
4. **ProductData.cs** - Product information structure
5. **SessionData.cs** - Game session tracking
6. **ShelfData.cs** - Shelf and row data models

### Gameplay Scripts (✅ Complete)
7. **ShelfInteractable.cs** - Shelf click detection and interaction
8. **ShelfDetailUI.cs** - Modal showing shelf rows and ROI
9. **ShelfRowUI.cs** - Individual row display component
10. **ProductSetupUI.cs** - Product input form at game start

---

## 🚀 Quick Setup Steps

### Step 1: Start Backend API

```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```

Verify it's running:
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"healthy","version":"1.0.0"}
```

### Step 2: Open Unity Project

1. Open Unity Hub
2. Open project: `/Users/gautham.ganesh/Downloads/The Placement Gambit`
3. Wait for Unity to compile the new scripts (check Console for errors)

### Step 3: Create GameSystems GameObject

1. In Hierarchy, create empty GameObject: `Right-click → Create Empty`
2. Rename to `GameSystems`
3. Add component: `GameSetupManager`
4. **Important**: Check "Auto Create Game Manager" and "Auto Create API Client"

### Step 4: Setup Product Input Scene

#### Option A: Use Existing Scene
If you have a MainMenu scene:

1. Open your MainMenu scene
2. Create Canvas if not present: `Right-click → UI → Canvas`
3. Add `ProductSetupUI` to Canvas

#### Option B: Create New Scene

1. Create new scene: `File → New Scene → 2D`
2. Save as `MainMenu`
3. Create Canvas: `Right-click → UI → Canvas`
4. Create UI Panel for product input:
   - Add Panel to Canvas
   - Rename to `ProductSetupPanel`

5. **Add Input Fields** (Create these as children of ProductSetupPanel):
   - TMP Input Field: `ProductNameInput`
   - TMP Dropdown: `CategoryDropdown`
   - TMP Input Field: `PriceInput`
   - TMP Input Field: `BudgetInput`
   - TMP Input Field: `TargetSalesInput`
   - TMP Input Field: `ExpectedROIInput`

6. **Add Buttons**:
   - Button: `StartGameButton` (Text: "Start Game")
   - Button: `QuickStartButton` (Text: "Quick Start Demo")

7. **Add ProductSetupUI Script** to ProductSetupPanel:
   - Drag input fields to corresponding slots
   - Drag buttons to button slots

### Step 5: Create Store Scene with Shelves

1. Create new scene: `File → New Scene → 2D`
2. Save as `Store`

3. **Create Canvas for UI**:
   - `Right-click → UI → Canvas`
   - Set Canvas Scaler to "Scale with Screen Size" (1920x1080)

4. **Create ShelfDetailUI Modal**:
   - Add Panel to Canvas, rename to `ShelfDetailModal`
   - Add CanvasGroup component
   - Add these child objects:
     - Panel: `ModalBackground`
     - Text (TMP): `TitleText`
     - Text (TMP): `LocationInfoText`
     - Button: `CloseButton`
     - Scroll View: `RowsScrollView`
       - Inside Content: This is `rowsContainer`
     - Panel: `FeedbackPanel` (for success messages)

5. **Add ShelfDetailUI Script** to ShelfDetailModal:
   - Drag CanvasGroup to `canvasGroup` field
   - Drag TitleText to `titleText` field
   - Drag LocationInfoText to `locationInfoText` field
   - Drag RowsScrollView/Viewport/Content to `rowsContainer`
   - Drag CloseButton to `closeButton`

6. **Create Row Prefab**:
   - Create Panel in RowsScrollView Content
   - Rename to `ShelfRowPrefab`
   - Add these children:
     - Text (TMP): `RowNameText`
     - Text (TMP): `ROIText`
     - Text (TMP): `InsightText`
     - Text (TMP): `SalesImpactText`
   - Add `ShelfRowUI` component to prefab
   - Drag text fields to corresponding slots
   - Drag prefab to Project (Assets folder)
   - Delete from hierarchy
   - Drag prefab back to ShelfDetailUI's `rowPrefab` field

7. **Create Shelves**:
   - Create Sprite: `Right-click → 2D Object → Sprite → Square`
   - Rename to `Shelf_MainEntrance`
   - Position at (0, 0, 0)
   - Add `ShelfInteractable` component
   - Set Location ID: `loc_001`
   - Set Location Name: `Main Entrance Display`
   - Set Zone: `Entrance`
   - Add BoxCollider2D (set to Trigger)

8. **Create more shelves** (duplicate and modify):
   - `Shelf_Beverages` - loc_005, (5, 0, 0)
   - `Shelf_DryGoods` - loc_003, (10, 0, 0)
   - `Shelf_HealthBeauty` - loc_009, (15, 0, 0)

9. **Add Player** (if not present):
   - Your existing Player object should work
   - Make sure it has Tag: `Player`

### Step 6: Configure Build Settings

1. `File → Build Settings`
2. Add scenes in this order:
   - MainMenu (index 0)
   - Store (index 1)
3. Click `Add Open Scenes` or drag scenes from Project

### Step 7: Test the Game

1. **Press Play** in Unity Editor
2. **Check Console** for initialization messages:
   ```
   🚀 GameSetupManager: Initializing game systems...
   ✅ GameManager created
   ✅ API Client created
   🔌 Testing API connection...
   ✅ API Connection successful!
   ```

3. **Fill out product form** (or click Quick Start)
4. **Should see**:
   - Loading state
   - API session creation message: `✅ Game session created: game_abc123...`
   - Transition to Store scene

5. **Walk to a shelf** (or click on shelf sprite)
6. **Press E** (or click) to view shelf details
7. **Select a row** → Should see:
   - ROI data from backend
   - Success feedback
   - Choice recorded message

---

## 🐛 Troubleshooting

### Issue: Scripts not compiling

**Solution**: Check Console for errors. Common issues:
- Missing TextMeshPro package: `Window → TextMeshPro → Import TMP Essential Resources`
- API errors: Make sure backend is running

### Issue: "GameManager not found"

**Solution**:
- Make sure GameSetupManager is in your first scene
- Check "Auto Create Game Manager" is enabled
- Verify GameManager.cs has no compile errors

### Issue: "API Connection failed"

**Solution**:
```bash
# Check if API is running
curl http://localhost:8000/api/health

# If not running, start it
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data
python3 -m api.main
```

### Issue: Shelf not interactable

**Solution**:
- Make sure Player has Tag: `Player`
- Check ShelfInteractable has BoxCollider2D set to Trigger
- Verify ShelfDetailUI exists in scene

### Issue: Row data not showing

**Solution**:
- Check Console for API errors
- Verify session was created (look for `✅ Game session created` message)
- Check location_id matches backend data (loc_001, loc_003, etc.)

---

## 📊 Expected Data Flow

```
1. Game Start
   ↓
2. GameSetupManager creates GameManager + API Client
   ↓
3. ProductSetupUI: User enters product details
   ↓
4. Click "Start Game" → GameManager.TransitionToLoadingState()
   ↓
5. LoadingState: API call to /api/game/session/create
   ↓
6. Session created: GameManager.CurrentSession populated
   ↓
7. Transition to Store scene
   ↓
8. Player walks to shelf → ShelfInteractable triggers
   ↓
9. Press E → API call to /api/game/rows/{location_id}
   ↓
10. ShelfDetailUI displays rows with ROI data
   ↓
11. Player selects row → API call to /api/game/choice
   ↓
12. Choice recorded → ROI result shown
   ↓
13. Session.AddChoice() updates session data
```

---

## 🎨 Visual Enhancements (Optional)

### Add Store Background
1. Import store background sprite
2. Add to Store scene as background layer
3. Set Sorting Layer: `Background`

### Add Shelf Sprites
1. Create/import shelf sprites (wood texture, shelves)
2. Replace square sprites on Shelf objects
3. Adjust BoxCollider2D to match sprite

### Add Player Movement Visuals
1. Add animation controller to Player
2. Create walk animations for WASD movement
3. Connect to existing PlayerMovement.cs

### Add Gambit Agent Integration
Your existing `GambitAgent.cs` can be enhanced:
- Add API dialogue fetching
- Show agent near shelves with high ROI
- Display hints based on backend recommendations

---

## 🔗 API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/game/session/create` | POST | Create game session |
| `/api/game/rows/{location_id}` | GET | Get shelf row ROI data |
| `/api/game/choice` | POST | Record player's shelf choice |
| `/api/game/agent/dialogue/{category}/{row}` | GET | Get NPC dialogue (optional) |

---

## ✅ Success Checklist

- [ ] Backend API running on port 8000
- [ ] All 10 C# scripts compile without errors
- [ ] GameSetupManager in scene with auto-create enabled
- [ ] ProductSetupUI form created with all input fields
- [ ] Store scene created with at least 1 shelf
- [ ] ShelfDetailUI modal created with row prefab
- [ ] Player tagged as "Player"
- [ ] Build settings configured with both scenes
- [ ] Test: Can start game and see API connection success
- [ ] Test: Can click shelf and see ROI data
- [ ] Test: Can select row and see success feedback
- [ ] Console shows: `✅ Choice recorded! ROI: X.XXx`

---

## 🎯 MVP Features Implemented

✅ **Core Systems**
- State machine game flow
- API integration with async/await
- Session management

✅ **Gameplay**
- Product setup at game start
- Store exploration (2D)
- Shelf interaction (click or proximity)
- Row selection with real ROI data

✅ **UI/UX**
- Product input form
- Shelf detail modal
- Row display with insights
- Success feedback

✅ **Data Integration**
- Real ROI calculations from backend
- Research-backed psychology insights
- Session tracking and scoring

---

## 🚀 Next Steps (After MVP Works)

### Phase 2: Enhanced Gameplay
- [ ] Add score tracking UI
- [ ] Add multiple product placements per session
- [ ] Add results screen with final score
- [ ] Add tutorial/onboarding

### Phase 3: Visual Polish
- [ ] Custom shelf sprites
- [ ] Animated ROI indicators
- [ ] Particle effects for success
- [ ] Background music and SFX

### Phase 4: Advanced Features
- [ ] Multiplayer comparison (leaderboard)
- [ ] Campaign mode with multiple stores
- [ ] Advanced analytics dashboard
- [ ] Export results to PDF

---

## 📚 Code Reference

### Quick Code Snippets

**Access current session from any script:**
```csharp
if (GameManager.Instance != null && GameManager.Instance.CurrentSession != null)
{
    string sessionId = GameManager.Instance.CurrentSession.sessionId;
    ProductData product = GameManager.Instance.CurrentProduct;
}
```

**Make API call:**
```csharp
var rowsData = await RetailPlacementAPI.Instance.GetShelfRows("loc_001");
```

**Record a choice:**
```csharp
var result = await RetailPlacementAPI.Instance.RecordChoice(sessionId, "loc_001", 1);
Debug.Log($"ROI: {result.roi_result}x");
```

---

## 💡 Tips

1. **Start Simple**: Get 1 shelf working before adding more
2. **Check Console**: All systems log their status with emoji prefixes
3. **Test API First**: Use curl or Postman to verify endpoints before Unity integration
4. **Prefab Everything**: Make shelves and UI elements into prefabs for reusability
5. **Scene Organization**: Use empty GameObjects as folders (Systems, UI, Shelves, etc.)

---

## 🆘 Get Help

If you're stuck:

1. **Check Unity Console**: Look for 🚀 ✅ ❌ prefixed messages
2. **Check API logs**: Terminal running `python3 -m api.main`
3. **Verify file locations**: All scripts should be in Assets folder
4. **Test API independently**: Use curl commands to verify endpoints
5. **Review docs**: See UNITY_TRANSFORMATION_ANALYSIS.md for detailed architecture

---

**You're ready to build! 🎮**

Start by completing the checklist above, then press Play in Unity Editor. The MVP should work end-to-end with real backend data!
