# Unity Transformation - Quick Reference Guide

## The Three-Sentence Summary
Your current Unity project has movement, dialogue, and NPC systems. You need to add: (1) a 2D store layout with 10 positioned shelves, (2) shelf click-to-select interactivity with ROI badges, and (3) a game loop connecting product input → store exploration → shelf choice → ROI feedback. **Total: ~200 hours, 4-8 weeks realistic timeline.**

---

## WHAT YOU HAVE (Existing Assets)

### Unity Project ✅
- 2D top-down movement system (PlayerMovement.cs)
- NEW Input System configured (WASD + E key)
- NPC interaction & dialogue system (DialogueManager.cs, GambitAgent.cs)
- TextMeshPro UI support
- Universal Render Pipeline (URP)
- Cinemachine for camera management
- Placeholder sprites for player, NPCs, shelves

### Backend API ✅
- FastAPI with ROI calculations
- Game session management endpoints
- Row-level shelf data with psychology insights
- Dialogue generation for Gambit Agent
- Choice recording system
- Everything needed for data flow

### Web Planogram ✅
- 10 store locations with layout
- 5 shelf rows per location with detailed data
- Psychology insights and research citations
- Color-coded ROI display system
- Recommendation algorithms

---

## WHAT YOU'RE MISSING (Main Gaps)

### Critical (Must Build) 🔴
1. **Store Layout Scene** - No store environment exists
   - 10 shelf positions in 2D space
   - Navigation areas with colliders
   - Visual representation of store zones

2. **Shelf Interactability** - Shelves are not clickable
   - Click detection on shelves
   - ROI badge display
   - Detail modal/panel system
   - Row selection interaction

3. **Game Loop** - No full flow from start to results
   - Main Menu with product form
   - Loading screen with API call
   - Store scene with free movement
   - Results/feedback scene
   - State machine to connect them

### Important (High Priority) 🟡
4. **API Integration Layer** - No C# HTTP client exists
   - Session management
   - Error handling & retries
   - Data caching
   - Network resilience

5. **Scoring & Feedback System** - No game mechanics
   - Calculate player choice quality
   - Compare to optimal ROI
   - Show success/failure feedback
   - Achievement system

6. **Visual Polish** - No game-like feedback
   - Particle effects for premium placements
   - Smooth animations
   - Color-coded visuals
   - Hover/selection states

---

## RECOMMENDED TECH STACK

```
Frontend (Unity):
├─ Unity 2022 LTS+ (or current stable)
├─ C# 10+
├─ TextMeshPro (UI text)
├─ DOTween (animations) - free
└─ Newtonsoft.Json (JSON parsing) - free

Backend (Keep existing):
├─ FastAPI (running at localhost:8000)
├─ Pydantic for validation
├─ JSON data files for store layout
└─ Optional: Redis for caching (future)

Development:
├─ Visual Studio Code or Rider
├─ Git for version control
└─ Unity Profiler for optimization
```

---

## ARCHITECTURE AT A GLANCE

### Scene Structure (3 scenes total)
```
MainMenu.unity
├─ Canvas with product input form
├─ Category selector, budget, ROI inputs
└─ "Play" button triggers loading

Loading.unity
├─ Shows spinner/tips
└─ Calls API /analyze endpoint

Store.unity (MAIN GAME)
├─ 2D store layout with 10 shelves
├─ Player character (top-down view)
├─ Gambit Agent NPC
├─ UI Canvas HUD (location, budget, prompt)
├─ Shelf detail modal (prefab)
└─ Choice dialog modal (prefab)

Results.unity
├─ ROI score comparison
├─ Achievement badges
└─ Continue/restart buttons
```

### Manager Classes (Singletons)
```
GameManager          → State machine (Menu → Loading → Playing → Results)
RetailPlacementAPI   → HTTP client for backend calls
ShelfManager         → Shelf state and interaction logic
UIManager            → All UI state transitions
PlayerManager        → Player progression data
DialogueManager      → (already exists, enhance)
AudioManager         → Sound effects & music
```

---

## IMPLEMENTATION PRIORITIES

### Phase 1: Foundation (Week 1-2) | 60 hours
```
Priority 1 (Setup):
- Create 3 scenes
- Implement GameManager state machine
- Build RetailPlacementAPI client

Priority 2 (Core):
- 2D store layout with 10 shelves
- Shelf prefab with visual feedback
- Shelf click-to-select system

Priority 3 (Polish):
- Main menu UI
- Loading screen
- Basic results display
```

### Phase 2: Gameplay (Week 3-4) | 55 hours
```
Priority 1:
- Choice dialog UI
- Record player choice to API
- ROI feedback system

Priority 2:
- NPC dialogue integration
- Particle effects
- Smooth animations

Priority 3:
- Audio (SFX, music)
- Player scoring
```

### Phase 3: Final (Week 5-6) | 40 hours
```
- Game balance & tuning
- Mobile support
- Cross-platform testing
- Performance optimization
- Bug fixes & polish
```

---

## EFFORT BREAKDOWN

| Component | Hours | Difficulty | Priority |
|-----------|-------|-----------|----------|
| Store Environment (2D) | 25 | HARD | HIGH |
| Shelf System | 20 | HARD | HIGH |
| API Integration | 15 | MEDIUM | HIGH |
| UI Systems | 18 | MEDIUM | HIGH |
| Gamification & Scoring | 22 | MEDIUM | MEDIUM |
| Dialogue/NPC | 12 | MEDIUM | MEDIUM |
| Visual Effects | 15 | MEDIUM | MEDIUM |
| Audio | 8 | EASY | MEDIUM |
| Testing & QA | 20 | MEDIUM | MEDIUM |
| Buffer/Unforeseen | 25 | - | - |
| **TOTAL** | **200** | - | - |

**Timeline for solo dev (8h/day): 5-6 weeks full-time**
**Timeline for solo dev (4h/day): 10-12 weeks part-time**

---

## BIGGEST TIME SINKS (Often Underestimated)

⏱️ **Polishing UI animations** → +5-8 hours
⏱️ **API timeout/error handling** → +4-6 hours
⏱️ **Mobile screen adaptation** → +6-8 hours
⏱️ **Cross-platform testing** → +8-10 hours
⏱️ **Save/load system** → +5-8 hours

---

## MVP vs FULL VERSION

### Minimum Viable Product (1 week | 35 hours)
✅ Store scene with 10 shelf zones
✅ Click shelf → see rows → select row
✅ Record choice to API
✅ Show simple ROI feedback
❌ No animations, no audio, no mobile, no polish

### Full Production Version (6-8 weeks | 200 hours)
✅ Everything above PLUS:
✅ Smooth animations & transitions
✅ Particle effects & visual feedback
✅ Audio (SFX + music)
✅ Mobile support
✅ Advanced UI polish
✅ Scoring system & achievements
✅ Tutorial/onboarding
✅ Performance optimization

---

## API ENDPOINTS YOU'LL USE

```
POST   /api/analyze                          → Get placement recommendations
POST   /api/game/session/create              → Create game session
GET    /api/game/session/{session_id}        → Retrieve session
POST   /api/game/session/sync                → Sync progress
GET    /api/game/rows/{location_id}          → Get shelf rows for location
GET    /api/game/agent/dialogue/{cat}/{row}  → Get Gambit dialogue
POST   /api/game/choice                      → Record player's shelf choice
```

**Key response data:**
- ROI multiplier per row (1.3x eye-level, 0.7x bottom, etc.)
- Psychology insights per row
- Visual cues (particle effects, colors, animations)
- Dialogue text with emotional state

---

## DATA MODELS YOU'LL CREATE

```csharp
// Player product input
ProductData {
  productName: string
  category: string
  price: float
  budget: float
  targetSales: int
  expectedROI: float
}

// Shelf row info
ShelfRow {
  rowId: int
  rowName: string          // "Eye Level", "Bottom", etc.
  roi: float
  psychologyInsight: string
  salesImpact: string
  visibility: float
  accessibility: float
  typicalProducts: string[]
}

// Player's choice
PlacementChoice {
  locationId: string
  rowNumber: int
  timestamp: DateTime
  roiResult: float
  quality: string          // "excellent", "good", "poor"
}

// Session state
SessionData {
  sessionId: string
  productData: ProductData
  currentLocation: string
  choicesMade: int
  totalScore: float
  startTime: DateTime
}
```

---

## QUICK WINS (Do These First!)

✅ **Day 1-2:** Create 3 scenes + GameManager state machine (10 hours)
✅ **Day 3-4:** Build API client + test connectivity (8 hours)
✅ **Day 5-7:** Create 2D store layout with shelf positions (12 hours)
✅ **Day 8:** Implement shelf click detection (4 hours)
✅ **Day 9:** Add detail modal to show rows (6 hours)
✅ **Day 10:** Record choice to API + show feedback (6 hours)

**Result:** Playable prototype in ~50 hours (10 days intensive)

---

## RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|-----------|
| API latency blocks UI | High | Async/await + caching + offline mode |
| Mobile performance lag | Medium | Sprite atlasing + LOD system + profiling |
| Session expiration = data loss | High | Local save system + recovery UI |
| Cross-platform input issues | Medium | Abstract input layer + testing early |
| Boring after 2-3 playthroughs | Low | Vary dialogue + randomize store layout |

---

## ASSET CHECKLIST

### Visual Assets Needed
- [ ] Store floor tile (128×128, seamless)
- [ ] Shelf sprites (various widths)
- [ ] Product icons (64×64, various colors)
- [ ] ROI badges with animation frames
- [ ] NPC character sprite
- [ ] UI buttons (default, hover, pressed states)
- [ ] Panel backgrounds
- [ ] Loading spinner sprite

**Where to get:**
- Kenney.nl (clean 2D sprites)
- OpenGameArt.org (free, CC-licensed)
- Sketchfab.com (free 3D models if going 3D)

### Audio Assets Needed
- [ ] Click sound (0.1s)
- [ ] Success chime (0.5s)
- [ ] Fail tone (0.3s)
- [ ] Background music loop (2-3 min)
- [ ] Ambient retail sounds (optional)

**Where to get:**
- Freesound.org (free, CC-licensed)
- Zapsplat.com (free)
- OpenGameArt.org

---

## DECISION POINT: 2D vs 3D Store

### 2D Top-Down View (RECOMMENDED) ✅
- **Time:** 20 hours
- **Complexity:** Low
- **Visual Quality:** Good (like Zelda)
- **Performance:** Excellent
- **Mobile Ready:** Yes
- **Best for:** Quick iteration & MVP

### 3D Isometric/Perspective ❌
- **Time:** 40+ hours
- **Complexity:** High
- **Visual Quality:** Premium
- **Performance:** Moderate
- **Mobile Ready:** Challenging
- **Best for:** Later enhancement

**Recommendation:** Start with 2D. Upgrade to 3D later if needed.

---

## SUCCESS INDICATORS

✅ Game runs at 60 FPS
✅ API calls complete in <500ms
✅ Load time <3 seconds
✅ Player can complete full loop in <5 minutes
✅ Mobile version runs smoothly
✅ Players replay 3+ times per session
✅ Code is organized in managers/components
✅ No memory leaks after 30 min play

---

## COMMON MISTAKES TO AVOID

❌ Building 3D store environment first (do 2D MVP)
❌ Trying to support mobile from day 1 (add later)
❌ Implementing voice acting (scope creep)
❌ Complex procedural generation (not needed)
❌ Complicated state management (use state pattern)
❌ Synchronous API calls (always async)
❌ Tight coupling between systems (use events)
❌ No error handling for network issues (add early)

---

## RECOMMENDED DEVELOPMENT WORKFLOW

```
Day 1:  Project setup + scene structure + GameManager
Day 2:  API client implementation + test connectivity
Day 3:  Store layout (2D grid with 10 shelves)
Day 4:  Shelf prefab + click detection
Day 5:  Detail modal + row display
Day 6:  Choice system + feedback
Day 7:  NPC dialogue integration
Day 8:  Visual effects + animations
Day 9:  Audio + sound effects
Day 10: Polish + bug fixes + mobile testing

(Repeat with increasing complexity in Phase 2-3)
```

---

## RESOURCES & DOCUMENTATION

📚 Full analysis: `UNITY_TRANSFORMATION_ANALYSIS.md` (35KB - comprehensive)
📋 This guide: `UNITY_QUICK_REFERENCE.md` (this file)
🔗 API docs: Available at http://localhost:8000/docs (when API running)
💾 Data files: Located in `/api/data/` folder
🎮 Sample scene: `/Assets/Scenes/SampleScene.unity` (reference)

---

## CONTACT & SUPPORT

For architecture questions, refer to:
- **State Machine**: See GameManager pattern in full analysis
- **API Integration**: See RetailPlacementAPI pattern in full analysis
- **Scene Structure**: See recommended scene layout in full analysis
- **Data Models**: See C# architecture section in full analysis

Good luck! This is a significant but achievable transformation. Start with Phase 1, get a playable prototype in 10 days, then iterate from there. 🚀
