# 🎮 Unity-Web Integration Architecture Plan
## Flux Data Retail Placement Optimizer

---

## 📋 Executive Summary

This document outlines the complete integration architecture for connecting "The Placement Gambit" Unity game with the Flux Data web planogram system. The integration creates a seamless experience where business owners can interact with product placement recommendations through both a gamified Unity experience and a professional web interface.

---

## 🎯 Integration Goals

1. **Bidirectional Data Flow**: Unity game and web UI share product data, ROI calculations, and placement decisions
2. **Session Persistence**: User sessions work across both interfaces without data loss
3. **Real-Time Sync**: Changes in one system reflect immediately in the other
4. **Unified Analytics**: Combine gameplay metrics with business analytics
5. **Seamless UX**: Smooth transitions between web dashboard and Unity game

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Business Owner                           │
└─────────────┬───────────────────────────────┬───────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────┐    ┌─────────────────────────────┐
│   Web Planogram UI      │◄───┤   Unity WebGL Game         │
│  (planogram_final.html) │────►│ (The Placement Gambit)     │
└─────────────┬───────────┘    └─────────────┬───────────────┘
              │                               │
              │         Shared Session        │
              │         via API Bridge        │
              │                               │
              ▼                               ▼
┌──────────────────────────────────────────────────────────────┐
│              FastAPI Backend + Multi-Agent System            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Product  │  │   ROI    │  │  Recomm  │  │ Defense  │    │
│  │Architect │  │ Analysis │  │  Agent   │  │  Agent   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│              Knowledge Base + Historical Data                │
│  • retail_psychology_sources.json (57 sources)               │
│  • Historical sales data                                     │
│  • Competitor metrics                                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔌 API Bridge Design

### New Backend Endpoints

#### 1. Game Session Management

**POST /api/game/session/create**
```json
Request:
{
  "product_name": "Premium Energy Drink",
  "category": "Beverages",
  "price": 3.49,
  "budget": 5000.00,
  "target_sales": 1000,
  "expected_roi": 1.5
}

Response:
{
  "session_id": "game_abc123",
  "unity_data": {
    "product_sprite_url": "/assets/beverages/energy_drink.png",
    "product_color": "#FF6B35",
    "starting_budget": 5000.00,
    "target_revenue": 5235.00
  },
  "web_url": "http://localhost:8080/demo/planogram_final.html?session=game_abc123"
}
```

**GET /api/game/session/{session_id}**
```json
Response:
{
  "session_id": "game_abc123",
  "status": "active",
  "product_data": { /* full product details */ },
  "game_progress": {
    "choices_made": 2,
    "current_location": "Beverages Aisle",
    "total_playtime_seconds": 245
  },
  "web_interactions": {
    "locations_viewed": ["Main Entrance", "Checkout Lane 1"],
    "shelves_expanded": 5
  }
}
```

**POST /api/game/session/sync**
```json
Request:
{
  "session_id": "game_abc123",
  "sync_data": {
    "player_choice": "row_1_eye_level",
    "dialogue_state": "showing_gambit_response",
    "timestamp": "2025-11-18T14:32:15Z"
  }
}

Response:
{
  "synced": true,
  "web_state_updated": true
}
```

#### 2. Row Analysis for Unity

**GET /api/game/rows/{location_id}**
```json
Response:
{
  "location_id": "L005",
  "location_name": "Beverages Aisle - Eye Level",
  "rows": [
    {
      "row_id": 1,
      "row_name": "Eye Level (1.2m - 1.6m)",
      "calculated_roi": 1.3,
      "psychology_insight": "Eye level is buy level - Products here are seen 9x more",
      "sales_impact": "Boosts sales by 23% compared to other shelf positions",
      "customer_behavior": "70% of purchase decisions made at this level",
      "best_for": "Premium products, new launches, high-margin items",
      "research_backed": "Trax Retail 2024 study",
      "unity_display": {
        "short_description": "Premium placement zone - 23% sales boost",
        "dialogue_text": "Eye level placement is scientifically proven to increase visibility by 900%. For your Premium Energy Drink, this position will capture 70% of purchase decisions."
      }
    },
    {
      "row_id": 2,
      "row_name": "Reach Level (1.6m - 1.8m)",
      "calculated_roi": 1.15,
      "unity_display": {
        "short_description": "Good visibility but requires reaching",
        "dialogue_text": "This shelf requires customers to reach up. Works well for familiar brands but challenging for new products. Expected 15% return on placement."
      }
    }
  ]
}
```

#### 3. Player Choice Recording

**POST /api/game/choice**
```json
Request:
{
  "session_id": "game_abc123",
  "location_id": "L005",
  "row_number": 1,
  "choice_timestamp": "2025-11-18T14:35:22Z",
  "dialogue_path": "manager_greeting -> gambit_intro -> category_select_beverages -> row_1_choice"
}

Response:
{
  "choice_recorded": true,
  "roi_result": 1.3,
  "success_message": "Excellent choice! Eye level placement will give you 1.3x ROI.",
  "web_redirect": "http://localhost:8080/demo/planogram_final.html?session=game_abc123&highlight=L005&shelf=1",
  "next_recommendation": {
    "location_id": "L008",
    "location_name": "Beverages End Cap",
    "reason": "Consider end cap for even higher visibility (1.85x ROI)"
  }
}
```

#### 4. Gambit Agent Data

**GET /api/game/agent/dialogue/{product_category}/{row_number}**
```json
Response:
{
  "category": "Beverages",
  "row_number": 1,
  "dialogue_lines": [
    {
      "speaker": "gambit_agent",
      "text": "Let me show you something interesting about Row 1...",
      "emotion": "confident",
      "duration_seconds": 3
    },
    {
      "speaker": "gambit_agent",
      "text": "For beverages, eye-level placement increases impulse purchases by 23%. Your Premium Energy Drink will be seen 9 times more often here than on bottom shelves.",
      "emotion": "informative",
      "duration_seconds": 6,
      "data_source": "Trax Retail 2024"
    }
  ],
  "visual_cues": {
    "highlight_shelf": true,
    "show_roi_badge": true,
    "particle_effect": "gold_sparkle"
  }
}
```

---

## 🎮 Unity C# Implementation

### 1. API Client Manager

Create `Assets/Scripts/ApiClient.cs`:

```csharp
using UnityEngine;
using UnityEngine.Networking;
using System;
using System.Threading.Tasks;
using System.Text;

public class ApiClient : MonoBehaviour
{
    private const string API_BASE_URL = "http://localhost:8000/api";
    private static ApiClient _instance;

    public static ApiClient Instance
    {
        get
        {
            if (_instance == null)
            {
                GameObject go = new GameObject("ApiClient");
                _instance = go.AddComponent<ApiClient>();
                DontDestroyOnLoad(go);
            }
            return _instance;
        }
    }

    // Create game session on startup
    public async Task<GameSession> CreateGameSession(ProductData productData)
    {
        string url = $"{API_BASE_URL}/game/session/create";
        string jsonBody = JsonUtility.ToJson(productData);

        using (UnityWebRequest request = UnityWebRequest.Post(url, jsonBody, "application/json"))
        {
            await request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                return JsonUtility.FromJson<GameSession>(request.downloadHandler.text);
            }
            else
            {
                Debug.LogError($"API Error: {request.error}");
                return null;
            }
        }
    }

    // Fetch row analysis for specific location
    public async Task<RowAnalysisResponse> GetRowAnalysis(string locationId)
    {
        string url = $"{API_BASE_URL}/game/rows/{locationId}";

        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            await request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                return JsonUtility.FromJson<RowAnalysisResponse>(request.downloadHandler.text);
            }
            else
            {
                Debug.LogError($"Failed to fetch row analysis: {request.error}");
                return null;
            }
        }
    }

    // Record player's placement choice
    public async Task<ChoiceResult> RecordPlayerChoice(string sessionId, string locationId, int rowNumber)
    {
        string url = $"{API_BASE_URL}/game/choice";

        ChoiceData data = new ChoiceData
        {
            session_id = sessionId,
            location_id = locationId,
            row_number = rowNumber,
            choice_timestamp = DateTime.UtcNow.ToString("o")
        };

        string jsonBody = JsonUtility.ToJson(data);

        using (UnityWebRequest request = UnityWebRequest.Post(url, jsonBody, "application/json"))
        {
            await request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                return JsonUtility.FromJson<ChoiceResult>(request.downloadHandler.text);
            }
            else
            {
                Debug.LogError($"Failed to record choice: {request.error}");
                return null;
            }
        }
    }

    // Get dialogue data for Gambit Agent
    public async Task<DialogueResponse> GetAgentDialogue(string category, int rowNumber)
    {
        string url = $"{API_BASE_URL}/game/agent/dialogue/{category}/{rowNumber}";

        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            await request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                return JsonUtility.FromJson<DialogueResponse>(request.downloadHandler.text);
            }
            else
            {
                Debug.LogError($"Failed to fetch dialogue: {request.error}");
                return null;
            }
        }
    }

    // Sync session state with backend
    public async Task<bool> SyncSession(string sessionId, string dialogueState)
    {
        string url = $"{API_BASE_URL}/game/session/sync";

        SyncData data = new SyncData
        {
            session_id = sessionId,
            sync_data = new SyncDetails
            {
                dialogue_state = dialogueState,
                timestamp = DateTime.UtcNow.ToString("o")
            }
        };

        string jsonBody = JsonUtility.ToJson(data);

        using (UnityWebRequest request = UnityWebRequest.Post(url, jsonBody, "application/json"))
        {
            await request.SendWebRequest();
            return request.result == UnityWebRequest.Result.Success;
        }
    }
}

// Data Models
[Serializable]
public class ProductData
{
    public string product_name;
    public string category;
    public float price;
    public float budget;
    public int target_sales;
    public float expected_roi;
}

[Serializable]
public class GameSession
{
    public string session_id;
    public UnityDataConfig unity_data;
    public string web_url;
}

[Serializable]
public class UnityDataConfig
{
    public string product_sprite_url;
    public string product_color;
    public float starting_budget;
    public float target_revenue;
}

[Serializable]
public class RowAnalysisResponse
{
    public string location_id;
    public string location_name;
    public RowData[] rows;
}

[Serializable]
public class RowData
{
    public int row_id;
    public string row_name;
    public float calculated_roi;
    public string psychology_insight;
    public string sales_impact;
    public UnityDisplayData unity_display;
}

[Serializable]
public class UnityDisplayData
{
    public string short_description;
    public string dialogue_text;
}

[Serializable]
public class ChoiceData
{
    public string session_id;
    public string location_id;
    public int row_number;
    public string choice_timestamp;
}

[Serializable]
public class ChoiceResult
{
    public bool choice_recorded;
    public float roi_result;
    public string success_message;
    public string web_redirect;
}

[Serializable]
public class DialogueResponse
{
    public string category;
    public int row_number;
    public DialogueLine[] dialogue_lines;
}

[Serializable]
public class DialogueLine
{
    public string speaker;
    public string text;
    public string emotion;
    public int duration_seconds;
}

[Serializable]
public class SyncData
{
    public string session_id;
    public SyncDetails sync_data;
}

[Serializable]
public class SyncDetails
{
    public string dialogue_state;
    public string timestamp;
}

// Extension method for async/await with UnityWebRequest
public static class UnityWebRequestExtensions
{
    public static Task<UnityWebRequest> SendWebRequest(this UnityWebRequest request)
    {
        var tcs = new TaskCompletionSource<UnityWebRequest>();

        request.SendWebRequest().completed += (op) =>
        {
            tcs.SetResult(request);
        };

        return tcs.Task;
    }
}
```

### 2. Modified DialogueManager.cs Integration

Add to existing `DialogueManager.cs`:

```csharp
// Add at top of class
private string currentSessionId;
private RowAnalysisResponse currentRowData;

// Modify existing ShowGambitResponse method
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

    // Show button to view web planogram
    ShowWebViewButton();
}

private async Task RecordChoice(string locationId, int rowNum)
{
    var result = await ApiClient.Instance.RecordPlayerChoice(
        currentSessionId,
        locationId,
        rowNum
    );

    if (result != null && result.choice_recorded)
    {
        Debug.Log($"Choice recorded! {result.success_message}");

        // Show success feedback
        StartCoroutine(ShowSuccessFeedback(result.success_message, result.roi_result));
    }
}

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

    while (elapsed < duration)
    {
        elapsed += Time.deltaTime;
        float alpha = 1f - (elapsed / duration);

        feedbackObj.transform.position = startPos + Vector3.up * (elapsed * 50f);
        feedbackText.alpha = alpha;

        yield return null;
    }

    Destroy(feedbackObj);
}

private void ShowWebViewButton()
{
    // Create button to open web planogram
    webViewButton.gameObject.SetActive(true);
    webViewButton.onClick.RemoveAllListeners();
    webViewButton.onClick.AddListener(() =>
    {
        string url = $"http://localhost:8080/demo/planogram_final.html?session={currentSessionId}";
        Application.OpenURL(url);
    });
}

private string GetLocationIdFromCategory(string category)
{
    // Map category to location ID
    switch (category.ToLower())
    {
        case "dry goods & packaged foods":
            return "L003";
        case "health & beauty":
            return "L006";
        case "general merchandise & electronics":
            return "L010";
        default:
            return "L005"; // Beverages as default
    }
}

// Call on game start
private async void Start()
{
    // Create session with backend
    ProductData productData = new ProductData
    {
        product_name = "Test Product",
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
        Debug.Log($"Game session created: {currentSessionId}");

        // Store web URL for later
        PlayerPrefs.SetString("WebPlanogramURL", session.web_url);
    }
}
```

### 3. GambitAgent.cs Enhancement

Add to existing `GambitAgent.cs`:

```csharp
// Add method to fetch and speak dialogue from backend
public async void SpeakRowAnalysis(int rowNum, string locationId)
{
    var dialogueData = await ApiClient.Instance.GetAgentDialogue(
        GetCurrentCategory(),
        rowNum
    );

    if (dialogueData != null && dialogueData.dialogue_lines.Length > 0)
    {
        foreach (var line in dialogueData.dialogue_lines)
        {
            // Speak each line with timing
            SpeakLine(line.text, line.duration_seconds);

            // Wait for duration
            await Task.Delay(line.duration_seconds * 1000);
        }
    }
}

private void SpeakLine(string text, int duration)
{
    // Show speech bubble UI
    if (speechBubble != null)
    {
        speechBubble.SetActive(true);
        speechBubbleText.text = text;

        // Auto-hide after duration
        StartCoroutine(HideSpeechBubbleAfterDelay(duration));
    }
}

private IEnumerator HideSpeechBubbleAfterDelay(int seconds)
{
    yield return new WaitForSeconds(seconds);

    if (speechBubble != null)
    {
        speechBubble.SetActive(false);
    }
}

private string GetCurrentCategory()
{
    // Get from DialogueManager
    return FindObjectOfType<DialogueManager>().GetSelectedCategory();
}
```

---

## 🌐 Web Interface Integration

### Modified planogram_final.html

Add session management and Unity embedding:

```javascript
// Add at top of script section
let currentGameSession = null;
let unityInstance = null;

// Check for session parameter on page load
window.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session');

    if (sessionId) {
        // Load existing game session
        await loadGameSession(sessionId);

        // Highlight location and shelf if specified
        const highlightLocation = urlParams.get('highlight');
        const highlightShelf = urlParams.get('shelf');

        if (highlightLocation) {
            highlightLocationOnPlanogram(highlightLocation);

            if (highlightShelf) {
                await showLocationDetail(highlightLocation);
                highlightShelfRow(parseInt(highlightShelf));
            }
        }
    }

    // Add "Play Game" button
    addGameLaunchButton();
});

async function loadGameSession(sessionId) {
    try {
        const response = await fetch(`http://localhost:8000/api/game/session/${sessionId}`);
        const sessionData = await response.json();

        currentGameSession = sessionData;

        // Pre-fill form with session data
        document.getElementById('product-name').value = sessionData.product_data.product_name;
        document.getElementById('category').value = sessionData.product_data.category;
        document.getElementById('price').value = sessionData.product_data.price;
        document.getElementById('budget').value = sessionData.product_data.budget;
        document.getElementById('target-sales').value = sessionData.product_data.target_sales;
        document.getElementById('expected-roi').value = sessionData.product_data.expected_roi;

        // Show session indicator
        showSessionIndicator(sessionId);

        console.log('Game session loaded:', sessionData);
    } catch (error) {
        console.error('Failed to load game session:', error);
    }
}

function showSessionIndicator(sessionId) {
    const indicator = document.createElement('div');
    indicator.className = 'session-indicator';
    indicator.innerHTML = `
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 12px 20px; border-radius: 8px;
                    position: fixed; top: 20px; right: 20px; z-index: 9999;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15); font-size: 14px;">
            🎮 Game Session: <strong>${sessionId.substring(0, 8)}</strong>
            <button onclick="syncWithGame()" style="margin-left: 10px; padding: 4px 12px;
                    background: white; color: #667eea; border: none; border-radius: 4px;
                    cursor: pointer; font-weight: 600;">
                Sync
            </button>
        </div>
    `;
    document.body.appendChild(indicator);
}

async function syncWithGame() {
    if (!currentGameSession) return;

    try {
        const response = await fetch('http://localhost:8000/api/game/session/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentGameSession.session_id,
                sync_data: {
                    dialogue_state: 'web_interaction',
                    timestamp: new Date().toISOString()
                }
            })
        });

        const result = await response.json();

        if (result.synced) {
            showNotification('✓ Synced with game session', 'success');
        }
    } catch (error) {
        console.error('Sync failed:', error);
        showNotification('× Sync failed', 'error');
    }
}

function addGameLaunchButton() {
    const sidebar = document.querySelector('.input-panel');

    const gameButton = document.createElement('button');
    gameButton.textContent = '🎮 Launch Game Experience';
    gameButton.className = 'game-launch-btn';
    gameButton.style.cssText = `
        width: 100%;
        padding: 16px;
        margin-top: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    `;

    gameButton.addEventListener('mouseenter', () => {
        gameButton.style.transform = 'translateY(-2px)';
        gameButton.style.boxShadow = '0 6px 16px rgba(102, 126, 234, 0.4)';
    });

    gameButton.addEventListener('mouseleave', () => {
        gameButton.style.transform = 'translateY(0)';
        gameButton.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
    });

    gameButton.addEventListener('click', launchUnityGame);

    sidebar.appendChild(gameButton);
}

async function launchUnityGame() {
    // Get current form values
    const productData = {
        product_name: document.getElementById('product-name').value,
        category: document.getElementById('category').value,
        price: parseFloat(document.getElementById('price').value),
        budget: parseFloat(document.getElementById('budget').value),
        target_sales: parseInt(document.getElementById('target-sales').value),
        expected_roi: parseFloat(document.getElementById('expected-roi').value)
    };

    // Create game session if not exists
    if (!currentGameSession) {
        try {
            const response = await fetch('http://localhost:8000/api/game/session/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(productData)
            });

            currentGameSession = await response.json();
            showSessionIndicator(currentGameSession.session_id);
        } catch (error) {
            console.error('Failed to create game session:', error);
            alert('Failed to launch game. Please check API connection.');
            return;
        }
    }

    // Open Unity game in modal or new window
    showUnityGameModal();
}

function showUnityGameModal() {
    const modal = document.createElement('div');
    modal.className = 'unity-game-modal';
    modal.innerHTML = `
        <div class="unity-modal-overlay" onclick="closeUnityGame()"></div>
        <div class="unity-modal-content">
            <div class="unity-modal-header">
                <h2>🎮 The Placement Gambit</h2>
                <button onclick="closeUnityGame()" class="close-btn">×</button>
            </div>
            <div class="unity-game-container">
                <iframe src="unity_build/index.html?session=${currentGameSession.session_id}"
                        width="100%" height="100%" frameborder="0">
                </iframe>
            </div>
            <div class="unity-modal-footer">
                <div class="session-info">Session: ${currentGameSession.session_id}</div>
                <button onclick="syncWithGame()" class="sync-btn">🔄 Sync</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        .unity-game-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 10000;
        }

        .unity-modal-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
        }

        .unity-modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90%;
            max-width: 1200px;
            height: 80vh;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .unity-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .unity-game-container {
            flex: 1;
            background: #1a1a1a;
        }

        .unity-modal-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 24px;
            background: #f3f4f6;
            border-top: 1px solid #e5e7eb;
        }
    `;
    document.head.appendChild(style);
}

function closeUnityGame() {
    const modal = document.querySelector('.unity-game-modal');
    if (modal) {
        modal.remove();
    }
}

function highlightLocationOnPlanogram(locationId) {
    // Find and highlight location box
    const locationBox = document.querySelector(`[data-location-id="${locationId}"]`);
    if (locationBox) {
        locationBox.classList.add('game-selected');
        locationBox.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Add pulsing animation
        locationBox.style.animation = 'pulse 1.5s ease-in-out 3';
    }
}

function highlightShelfRow(rowNumber) {
    // Find and highlight shelf in modal
    const shelf = document.querySelector(`[data-row-index="${rowNumber}"]`);
    if (shelf) {
        shelf.classList.add('game-selected');
        shelf.click(); // Auto-click to show details
    }
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideInUp 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutDown 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const animationStyle = document.createElement('style');
animationStyle.textContent = `
    @keyframes pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
        50% { transform: scale(1.05); box-shadow: 0 0 0 20px rgba(102, 126, 234, 0); }
    }

    @keyframes slideInUp {
        from { transform: translateY(100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }

    @keyframes slideOutDown {
        from { transform: translateY(0); opacity: 1; }
        to { transform: translateY(100%); opacity: 0; }
    }

    .game-selected {
        border: 3px solid #667eea !important;
        box-shadow: 0 0 30px rgba(102, 126, 234, 0.6) !important;
    }
`;
document.head.appendChild(animationStyle);
```

---

## 📊 Data Flow Diagrams

### User Journey Flow

```
1. BUSINESS OWNER ENTRY
   ↓
2. WEB UI: Input product details
   ↓
3. BACKEND: Create session + analyze
   ↓
4. USER CHOICE:
   ├─→ A) View Web Planogram
   │   ├─→ See visual store map
   │   ├─→ Click locations
   │   ├─→ View shelf ROI details
   │   └─→ Launch Game (optional)
   │
   └─→ B) Play Unity Game
       ├─→ Meet Store Manager NPC
       ├─→ Choose product category
       ├─→ Gambit Agent guides to shelf
       ├─→ Select shelf row
       ├─→ See ROI feedback
       └─→ View Web Planogram
           (with highlighted choice)
```

### Session State Synchronization

```
┌─────────────────────────────────────────────┐
│           Shared Session State              │
├─────────────────────────────────────────────┤
│  session_id: "game_abc123"                  │
│  product_data: { name, category, price }    │
│  game_progress: { choices, location }       │
│  web_interactions: { views, clicks }        │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
        ▼                    ▼
┌───────────────┐    ┌───────────────┐
│   Unity Game  │    │    Web UI     │
├───────────────┤    ├───────────────┤
│ • Player at   │◄──►│ • Highlight   │
│   Row 1       │sync│   Row 1       │
│ • ROI: 1.3x   │    │ • Show 1.3x   │
│ • Choice made │    │ • Details     │
└───────────────┘    └───────────────┘
```

---

## 🛠️ Implementation Phases

### Phase 1: Backend API Development (Week 1)
- [ ] Create new FastAPI endpoints for game session management
- [ ] Implement `/api/game/session/create` endpoint
- [ ] Implement `/api/game/rows/{location_id}` endpoint
- [ ] Implement `/api/game/choice` endpoint
- [ ] Implement `/api/game/agent/dialogue/{category}/{rowNum}` endpoint
- [ ] Add session storage (Redis or PostgreSQL)
- [ ] Create session sync logic
- [ ] Write API tests

### Phase 2: Unity Integration (Week 2)
- [ ] Create `ApiClient.cs` with all endpoint methods
- [ ] Add async/await support for Unity
- [ ] Modify `DialogueManager.cs` to fetch real data
- [ ] Enhance `GambitAgent.cs` with API dialogue
- [ ] Add session initialization on game start
- [ ] Implement choice recording
- [ ] Add success feedback UI
- [ ] Create "View Web Planogram" button

### Phase 3: Web UI Enhancement (Week 3)
- [ ] Add session parameter detection
- [ ] Implement session loading from URL
- [ ] Add game launch button
- [ ] Create Unity game modal
- [ ] Implement location/shelf highlighting
- [ ] Add sync functionality
- [ ] Create notification system
- [ ] Test bidirectional flow

### Phase 4: Unity WebGL Build (Week 4)
- [ ] Configure Unity for WebGL export
- [ ] Optimize build size (compression, asset bundles)
- [ ] Create build pipeline
- [ ] Set up hosting for Unity build
- [ ] Test WebGL build in iframe
- [ ] Add loading screen
- [ ] Handle mobile/touch controls
- [ ] Performance optimization

### Phase 5: Integration Testing (Week 5)
- [ ] Test session creation flow
- [ ] Test data sync between systems
- [ ] Test game-to-web transitions
- [ ] Test web-to-game transitions
- [ ] Load testing (multiple concurrent sessions)
- [ ] Cross-browser testing
- [ ] Mobile responsiveness testing
- [ ] Error handling and edge cases

### Phase 6: Polish & Deployment (Week 6)
- [ ] Add analytics tracking
- [ ] Implement error logging
- [ ] Add user feedback mechanism
- [ ] Create documentation
- [ ] Set up CI/CD pipeline
- [ ] Deploy to staging environment
- [ ] User acceptance testing
- [ ] Production deployment

---

## 🔐 Security Considerations

### 1. Session Security
- Generate cryptographically secure session IDs
- Implement session expiration (24 hours)
- Add rate limiting to API endpoints
- Validate all input data

### 2. CORS Configuration
```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Data Validation
- Validate all product data before session creation
- Sanitize user inputs
- Prevent SQL injection
- Implement request size limits

---

## 📈 Analytics & Metrics

### Track User Behavior

```python
# Add to backend
class SessionAnalytics:
    def log_game_launch(session_id: str):
        # Track when users launch Unity game
        pass

    def log_location_view(session_id: str, location_id: str):
        # Track which locations users view
        pass

    def log_shelf_interaction(session_id: str, shelf_row: int):
        # Track shelf row clicks
        pass

    def calculate_engagement_score(session_id: str):
        # Score based on interactions
        pass
```

### Metrics to Collect
- Session duration
- Game playtime vs web interaction time
- Most viewed locations
- Most selected shelf rows
- Conversion from game to web (and vice versa)
- User journey paths

---

## 🚀 Performance Optimization

### Unity Build Optimization
- Enable compression (Brotli or Gzip)
- Use asset bundles for large assets
- Minimize texture sizes
- Reduce code stripping level
- Enable WebGL2 support

### API Response Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_row_analysis(location_id: str):
    # Cache frequently accessed location data
    return generate_row_analysis(location_id)
```

### WebGL Loading Screen
```html
<div id="unity-loading-screen">
    <div class="loading-bar-container">
        <div class="loading-bar" id="loading-bar"></div>
    </div>
    <div class="loading-text">Loading The Placement Gambit...</div>
</div>

<script>
unityInstance = createUnityInstance(canvas, config, (progress) => {
    document.getElementById('loading-bar').style.width = `${progress * 100}%`;
    if (progress === 1) {
        document.getElementById('unity-loading-screen').style.display = 'none';
    }
});
</script>
```

---

## 🧪 Testing Strategy

### Unit Tests
- API endpoint tests (pytest)
- Unity script tests (Unity Test Framework)
- JavaScript function tests (Jest)

### Integration Tests
- Session creation and loading
- Data sync between Unity and web
- API error handling
- WebGL build loading

### User Acceptance Tests
- Complete user journey
- Game-to-web transitions
- Web-to-game transitions
- Multiple concurrent sessions
- Mobile device testing

---

## 📚 Documentation Requirements

### For Developers
- API endpoint documentation (Swagger/OpenAPI)
- Unity script documentation (XML comments)
- JavaScript function documentation (JSDoc)
- Architecture diagrams
- Database schema

### For Users
- How to use the integrated system
- Game controls and interactions
- Web UI guide
- Troubleshooting common issues

---

## 🎯 Success Metrics

### Technical KPIs
- API response time < 200ms
- Unity WebGL load time < 5 seconds
- Session sync latency < 100ms
- 99.9% uptime

### User Experience KPIs
- 80%+ users try both game and web
- Average session duration > 5 minutes
- <5% error rate
- 90%+ mobile compatibility

---

## 📝 Next Immediate Steps

1. **Create Backend API Endpoints** (Days 1-3)
   - Set up `/api/game/*` routes
   - Implement session management
   - Add database models for sessions

2. **Build ApiClient.cs** (Days 4-5)
   - Implement all API methods
   - Add error handling
   - Test API calls from Unity

3. **Integrate DialogueManager** (Days 6-7)
   - Fetch real ROI data
   - Display backend dialogue
   - Record player choices

4. **Enhance Web UI** (Days 8-9)
   - Add session detection
   - Create game launch button
   - Implement highlighting

5. **Test Integration** (Day 10)
   - End-to-end testing
   - Fix bugs and edge cases
   - Prepare for WebGL build

---

## 🔗 File References

- **Backend**: `/Users/gautham.ganesh/Documents/GG_Scripts/flux_data/backend/main.py`
- **Web UI**: `/Users/gautham.ganesh/Documents/GG_Scripts/flux_data/demo/planogram_final.html`
- **Unity Scripts**: `/Users/gautham.ganesh/Downloads/The Placement Gambit/Assets/`
  - `DialogueManager.cs`
  - `GambitAgent.cs`
  - `PlayerMovement.cs`
  - `NPCInteraction.cs`
- **Knowledge Base**: `/Users/gautham.ganesh/Documents/GG_Scripts/flux_data/knowledge_base/retail_psychology_sources.json`

---

## ✅ Integration Checklist

- [ ] Backend API endpoints created
- [ ] Unity ApiClient.cs implemented
- [ ] DialogueManager modified for API calls
- [ ] GambitAgent enhanced with real dialogue
- [ ] Web UI session management added
- [ ] Game launch button added to web
- [ ] Unity WebGL build configured
- [ ] Session sync working bidirectionally
- [ ] Location highlighting functional
- [ ] Shelf row highlighting functional
- [ ] Analytics tracking implemented
- [ ] Error handling complete
- [ ] Documentation written
- [ ] Tests passing
- [ ] Performance optimized
- [ ] Security review done
- [ ] User acceptance testing complete
- [ ] Production deployment ready

---

**Document Version**: 1.0
**Last Updated**: 2025-11-18
**Author**: Claude Code
**Status**: Ready for Implementation

---

## 💬 Questions for Stakeholders

Before starting implementation, clarify:

1. **Hosting**: Where will Unity WebGL build be hosted? Same domain or CDN?
2. **Session Duration**: How long should game sessions persist? (Recommended: 24 hours)
3. **Analytics**: Which analytics platform to integrate? (Google Analytics, Mixpanel, custom)
4. **Authentication**: Should we add user login? Or keep anonymous sessions?
5. **Mobile Priority**: Is mobile experience critical? (Will determine WebGL optimization level)
6. **Deployment**: Staging and production environments already set up?
7. **Budget**: Any budget constraints for hosting Unity builds? (WebGL files can be large)

---

**🚀 Ready to Begin Implementation!**
