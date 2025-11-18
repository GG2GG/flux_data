# 🎮 Unity Implementation Guide
## Quick Start for Integrating "The Placement Gambit"

---

## 📋 Prerequisites

- Unity 2021.3 or newer
- The Placement Gambit project at: `/Users/gautham.ganesh/Downloads/The Placement Gambit`
- Backend API running at: `http://localhost:8000`
- Basic knowledge of C# async/await

---

## 🚀 Step 1: Add ApiClient Script

1. **Create the ApiClient.cs file**

   ```bash
   # Copy the ApiClient.cs from the integration plan into:
   /Users/gautham.ganesh/Downloads/The Placement Gambit/Assets/Scripts/ApiClient.cs
   ```

   The complete ApiClient code is in [UNITY_INTEGRATION_PLAN.md:252-469]

2. **Verify it compiles**
   - Open Unity project
   - Let Unity compile the script
   - Check Console for any errors

---

## 🔧 Step 2: Modify DialogueManager.cs

Add API integration to your existing DialogueManager:

### 2.1 Add Session Variables (Top of DialogueManager class)

```csharp
// Add these at the top of DialogueManager class
private string currentSessionId;
private RowAnalysisResponse currentRowData;
private string selectedCategory;

[Header("UI References")]
public GameObject webViewButton;
public GameObject feedbackPrefab;
```

### 2.2 Create Session on Start

```csharp
// Replace or add to your Start() method
private async void Start()
{
    // Hide buttons initially
    choice1Button.gameObject.SetActive(false);
    choice2Button.gameObject.SetActive(false);
    choice3Button.gameObject.SetActive(false);
    webViewButton.gameObject.SetActive(false);

    // Create game session with backend
    ProductData productData = new ProductData
    {
        product_name = "Premium Energy Drink",
        category = "Beverages",
        price = 3.49f,
        budget = 5000f,
        target_sales = 1000,
        expected_roi = 1.5f
    };

    GameSession session = await ApiClient.Instance.CreateGameSession(productData);

    if (session != null)
    {
        currentSessionId = session.session_id;
        Debug.Log($"✅ Game session created: {currentSessionId}");
        PlayerPrefs.SetString("WebPlanogramURL", session.web_url);
    }
    else
    {
        Debug.LogError("❌ Failed to create game session");
    }
}
```

### 2.3 Modify ShowGambitResponse Method

```csharp
// Replace your existing ShowGambitResponse method
private async void ShowGambitResponse(int rowNum)
{
    currentState = DialogueState.ShowingGambitResponse;

    // Fetch real ROI data from backend
    string locationId = GetLocationIdFromCategory(selectedCategory);
    currentRowData = await ApiClient.Instance.GetRowAnalysis(locationId);

    if (currentRowData != null && currentRowData.rows.Length >= rowNum)
    {
        RowData selectedRow = currentRowData.rows[rowNum - 1];

        // Display real dialogue from backend
        string dialogueText = selectedRow.unity_display.dialogue_text;
        dialogueText += $"\n\n<color=#10B981>ROI Score: {selectedRow.calculated_roi}x</color>";
        dialogueText += $"\n{selectedRow.sales_impact}";

        dialogueUI.text = dialogueText;

        // Record player's choice
        await RecordChoice(locationId, rowNum);
    }
    else
    {
        // Fallback to existing static dialogue
        ShowStaticResponse(rowNum);
    }

    gambitAgent.GoToRow(rowNum);
    ShowWebViewButton();
}

// Helper method for static fallback
private void ShowStaticResponse(int rowNum)
{
    string[] staticResponses = new string[]
    {
        "Row 1 (Eye Level) is the premium placement zone.",
        "Row 2 (Reach Level) offers good visibility.",
        "Row 3 (Touch Level) encourages interaction."
    };

    if (rowNum <= staticResponses.Length)
    {
        dialogueUI.text = staticResponses[rowNum - 1];
    }
}
```

### 2.4 Add RecordChoice Method

```csharp
private async Task RecordChoice(string locationId, int rowNum)
{
    var result = await ApiClient.Instance.RecordPlayerChoice(
        currentSessionId,
        locationId,
        rowNum
    );

    if (result != null && result.choice_recorded)
    {
        Debug.Log($"✅ Choice recorded! {result.success_message}");
        StartCoroutine(ShowSuccessFeedback(result.success_message, result.roi_result));
    }
}
```

### 2.5 Add ShowSuccessFeedback Coroutine

```csharp
private IEnumerator ShowSuccessFeedback(string message, float roi)
{
    // Create floating UI element
    GameObject feedbackObj = Instantiate(feedbackPrefab, canvas.transform);
    TextMeshProUGUI feedbackText = feedbackObj.GetComponentInChildren<TextMeshProUGUI>();

    feedbackText.text = $"✓ {message}\nROI: {roi}x";

    // Animate upward fade
    float duration = 3f;
    float elapsed = 0f;
    Vector3 startPos = feedbackObj.transform.position;
    Color startColor = feedbackText.color;

    while (elapsed < duration)
    {
        elapsed += Time.deltaTime;
        float alpha = 1f - (elapsed / duration);

        feedbackObj.transform.position = startPos + Vector3.up * (elapsed * 50f);
        feedbackText.color = new Color(startColor.r, startColor.g, startColor.b, alpha);

        yield return null;
    }

    Destroy(feedbackObj);
}
```

### 2.6 Add Web View Button Method

```csharp
private void ShowWebViewButton()
{
    webViewButton.gameObject.SetActive(true);
    webViewButton.GetComponent<Button>().onClick.RemoveAllListeners();
    webViewButton.GetComponent<Button>().onClick.AddListener(() =>
    {
        string url = $"http://localhost:8080/demo/planogram_final.html?session={currentSessionId}";
        Application.OpenURL(url);
    });
}
```

### 2.7 Add Category Mapping Helper

```csharp
private string GetLocationIdFromCategory(string category)
{
    switch (category.ToLower())
    {
        case "dry goods & packaged foods":
            return "loc_003";
        case "health & beauty":
            return "loc_009";
        case "general merchandise & electronics":
            return "loc_010";
        default:
            return "loc_001"; // Beverages
    }
}
```

### 2.8 Track Selected Category

Modify your existing choice button methods:

```csharp
public void OnChoice1Selected()
{
    selectedCategory = "Dry Goods & Packaged Foods";
    // ... rest of your existing code
}

public void OnChoice2Selected()
{
    selectedCategory = "Health & Beauty";
    // ... rest of your existing code
}

public void OnChoice3Selected()
{
    selectedCategory = "General Merchandise & Electronics";
    // ... rest of your existing code
}
```

---

## 🎨 Step 3: Create UI Elements

### 3.1 Create Feedback Prefab

1. **Create new GameObject**: `Right-click in Hierarchy → UI → Panel`
2. **Name it**: `FeedbackPanel`
3. **Add components**:
   - CanvasGroup (for fading)
   - TextMeshProUGUI child for the message
4. **Style it**:
   - Background: Semi-transparent green (#10B981 with 80% opacity)
   - Text: White, bold, size 24
   - Padding: 20px all sides
5. **Save as Prefab**: Drag to `Assets/Prefabs/FeedbackPanel.prefab`
6. **Delete from Hierarchy**

### 3.2 Create Web View Button

1. **Create Button**: `Right-click in Canvas → UI → Button`
2. **Name it**: `WebViewButton`
3. **Position**: Bottom-right of dialogue panel
4. **Text**: "📊 View Planogram"
5. **Style**:
   - Background: Gradient purple (#667eea to #764ba2)
   - Text: White, bold
   - Size: 200x50
6. **Reference in Inspector**: Drag to DialogueManager's `webViewButton` field

---

## 🧪 Step 4: Test the Integration

### 4.1 Start Backend API

```bash
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data/api
python main.py
```

Verify it's running:
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 4.2 Test in Unity

1. **Press Play** in Unity Editor
2. **Check Console** for: `✅ Game session created: game_abc123...`
3. **Talk to Store Manager** NPC
4. **Choose product category**
5. **Select a shelf row**
6. **Look for**:
   - Real ROI data displayed (not hardcoded)
   - Success feedback animation
   - "View Planogram" button appears

### 4.3 Test Web Integration

1. **Click "View Planogram" button**
2. **Browser should open** to planogram with:
   - Session ID in URL
   - Your product pre-filled
   - Location highlighted
   - Shelf row selected

---

## 🐛 Troubleshooting

### Issue: "ApiClient not found"

**Solution**: Ensure `ApiClient.cs` is in `Assets/Scripts/` and Unity has compiled it.

```bash
# Check file exists
ls "/Users/gautham.ganesh/Downloads/The Placement Gambit/Assets/Scripts/ApiClient.cs"
```

---

### Issue: "Connection refused" errors

**Solution**: Backend API not running.

```bash
# Check if API is running
curl http://localhost:8000/api/health

# If not running, start it
cd /Users/gautham.ganesh/Documents/GG_Scripts/flux_data/api
python main.py
```

---

### Issue: "Task.WhenAll not found"

**Solution**: Add using statement at top of DialogueManager:

```csharp
using System.Threading.Tasks;
```

---

### Issue: Dialogue not showing

**Solution**: Check Console for API errors:

1. Look for `❌ API Error:` messages
2. Verify API endpoint URL is correct
3. Check session was created successfully

---

### Issue: ROI always showing same values

**Solution**: Ensure location_id is correctly mapped:

```csharp
// Add debug logging
Debug.Log($"Category: {selectedCategory}, Location ID: {locationId}");
```

---

## 📊 Testing Checklist

- [ ] Backend API starts without errors
- [ ] Unity game creates session on start
- [ ] Console shows session ID
- [ ] Talking to NPCs works (no regression)
- [ ] Choosing category stores selectedCategory
- [ ] Shelf selection fetches real ROI data
- [ ] ROI values are different per shelf (not all 1.3x)
- [ ] Success feedback animates correctly
- [ ] "View Planogram" button appears
- [ ] Clicking button opens browser
- [ ] Web page loads with correct session
- [ ] Product data pre-filled on web page
- [ ] Chosen location highlighted on planogram
- [ ] Chosen shelf row selected in modal

---

## 🎯 Expected Data Flow

```
1. Unity Start()
   → POST /api/game/session/create
   → Store session_id

2. Player chooses category
   → Store selectedCategory variable
   → Gambit Agent activates

3. Player picks shelf row
   → GET /api/game/rows/{location_id}
   → Display real ROI data
   → POST /api/game/choice (record selection)

4. Show success feedback
   → Display ROI result
   → Show "View Planogram" button

5. Click "View Planogram"
   → Open browser: planogram_final.html?session={id}
   → Web loads session data
   → Highlights chosen location + shelf
```

---

## 🔗 API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/game/session/create` | POST | Create session on game start |
| `/api/game/rows/{location_id}` | GET | Fetch row ROI data |
| `/api/game/choice` | POST | Record player's choice |
| `/api/game/agent/dialogue/{category}/{row}` | GET | Get agent dialogue (optional) |

---

## 📝 Next Steps After Basic Integration

1. **Add Loading Indicators**: Show spinner while API calls in progress
2. **Error Handling**: Display user-friendly error messages
3. **Offline Mode**: Cache last known data for offline play
4. **Enhanced Dialogue**: Use `/api/game/agent/dialogue` for dynamic NPC speech
5. **Session Resume**: Allow players to continue previous sessions
6. **Analytics**: Track player behavior for optimization

---

## 📚 File Locations

- **Unity Project**: `/Users/gautham.ganesh/Downloads/The Placement Gambit`
- **Backend API**: `/Users/gautham.ganesh/Documents/GG_Scripts/flux_data/api/main.py`
- **Game Routes**: `/Users/gautham.ganesh/Documents/GG_Scripts/flux_data/api/game_routes.py`
- **Web UI**: `/Users/gautham.ganesh/Documents/GG_Scripts/flux_data/demo/planogram_final.html`
- **Integration Plan**: `/Users/gautham.ganesh/Documents/GG_Scripts/flux_data/UNITY_INTEGRATION_PLAN.md`

---

## 🎓 Learning Resources

### Understanding Async in Unity

```csharp
// ❌ DON'T: Blocking call (freezes game)
var result = ApiClient.GetData().Result;

// ✅ DO: Async/await (non-blocking)
var result = await ApiClient.GetData();
```

### Handling API Errors

```csharp
try
{
    var result = await ApiClient.Instance.GetRowAnalysis(locationId);
    if (result != null)
    {
        // Success
    }
    else
    {
        Debug.LogWarning("API returned null");
        ShowFallbackData();
    }
}
catch (Exception e)
{
    Debug.LogError($"API Error: {e.Message}");
    ShowErrorMessage("Connection failed. Using offline data.");
}
```

---

## ✅ Success Criteria

You'll know the integration is working when:

1. ✅ Unity Console shows: `✅ Game session created: game_abc123...`
2. ✅ Shelf dialogue shows different ROI values (1.05x, 1.23x, 1.30x, etc.)
3. ✅ Success feedback appears with calculated ROI
4. ✅ Browser opens to planogram with correct session
5. ✅ Web page highlights your chosen location and shelf
6. ✅ No errors in Unity Console or browser console

---

## 🆘 Get Help

If you're stuck:

1. **Check Console Logs**: Unity Console and browser DevTools
2. **Verify API Health**: `curl http://localhost:8000/api/health`
3. **Test Endpoints**: Use `curl` or Postman to test API directly
4. **Review Integration Plan**: See [UNITY_INTEGRATION_PLAN.md](./UNITY_INTEGRATION_PLAN.md)

---

**Ready to integrate? Start with Step 1! 🚀**
