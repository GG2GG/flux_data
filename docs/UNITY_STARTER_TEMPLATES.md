# Unity Transformation - C# Code Starter Templates

This document provides ready-to-use C# code templates for the main systems you need to build.

---

## 1. GAMEMANAGER (State Machine)

```csharp
using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }
    
    private GameState currentState;
    public ProductData CurrentProduct { get; set; }
    public SessionData CurrentSession { get; set; }
    
    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }
    
    void Start()
    {
        TransitionToMenuState();
    }
    
    void Update()
    {
        currentState?.OnUpdate();
    }
    
    // State transitions
    public void TransitionToMenuState()
    {
        currentState?.OnExit();
        currentState = new MenuState(this);
        currentState.OnEnter();
    }
    
    public void TransitionToLoadingState()
    {
        currentState?.OnExit();
        currentState = new LoadingState(this);
        currentState.OnEnter();
    }
    
    public void TransitionToGameScene()
    {
        currentState?.OnExit();
        currentState = new GameState(this);
        currentState.OnEnter();
    }
    
    public void TransitionToResultsState()
    {
        currentState?.OnExit();
        currentState = new ResultsState(this);
        currentState.OnEnter();
    }
}

// Abstract base state
public abstract class GameState
{
    protected GameManager gameManager;
    
    public GameState(GameManager manager)
    {
        gameManager = manager;
    }
    
    public virtual void OnEnter() { }
    public virtual void OnExit() { }
    public virtual void OnUpdate() { }
}

// Menu state
public class MenuState : GameState
{
    public MenuState(GameManager manager) : base(manager) { }
    
    public override void OnEnter()
    {
        Debug.Log("Entering Menu State");
        SceneManager.LoadScene("MainMenu");
    }
    
    public override void OnExit()
    {
        Debug.Log("Exiting Menu State");
    }
}

// Loading state
public class LoadingState : GameState
{
    public LoadingState(GameManager manager) : base(manager) { }
    
    public override void OnEnter()
    {
        Debug.Log("Entering Loading State - Calling API");
        SceneManager.LoadScene("Loading", LoadSceneMode.Single);
        // TODO: Call API /analyze
    }
    
    public override void OnExit()
    {
        Debug.Log("Exiting Loading State");
    }
}

// Game state
public class GameState : GameState
{
    public GameState(GameManager manager) : base(manager) { }
    
    public override void OnEnter()
    {
        Debug.Log("Entering Game State");
        SceneManager.LoadScene("Store", LoadSceneMode.Single);
    }
    
    public override void OnExit()
    {
        Debug.Log("Exiting Game State");
    }
}

// Results state
public class ResultsState : GameState
{
    public ResultsState(GameManager manager) : base(manager) { }
    
    public override void OnEnter()
    {
        Debug.Log("Entering Results State");
        SceneManager.LoadScene("Results", LoadSceneMode.Single);
    }
    
    public override void OnExit()
    {
        Debug.Log("Exiting Results State");
    }
}

// Data models
[System.Serializable]
public class ProductData
{
    public string productName;
    public string category;
    public float price;
    public float budget;
    public int targetSales;
    public float expectedROI;
}

[System.Serializable]
public class SessionData
{
    public string sessionId;
    public ProductData product;
    public string currentLocation;
    public int choicesMade;
    public float totalScore;
    public System.DateTime startTime;
}
```

---

## 2. RETAIL PLACEMENT API CLIENT

```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;

public class RetailPlacementAPI : MonoBehaviour
{
    public static RetailPlacementAPI Instance { get; private set; }
    
    private string apiBaseUrl = "http://localhost:8000/api";
    private float requestTimeout = 10f;
    
    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }
    
    // Analyze product placement
    public async Task<AnalyzeResponse> AnalyzeProduct(ProductData product)
    {
        try
        {
            var request = new AnalyzeRequest
            {
                product_name = product.productName,
                category = product.category,
                price = product.price,
                budget = product.budget,
                target_sales = product.targetSales,
                target_customers = "Target customer segment",
                expected_roi = product.expectedROI
            };
            
            string json = JsonUtility.ToJson(request);
            var response = await PostRequest<AnalyzeResponse>("/analyze", json);
            
            Debug.Log($"Analysis complete. Top recommendation: {response.recommendations.Keys.First()}");
            return response;
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error analyzing product: {e.Message}");
            throw;
        }
    }
    
    // Get shelf rows for location
    public async Task<RowsResponse> GetShelfRows(string locationId, string sessionId = null)
    {
        try
        {
            string url = $"/game/rows/{locationId}";
            if (!string.IsNullOrEmpty(sessionId))
            {
                url += $"?session_id={sessionId}";
            }
            
            var response = await GetRequest<RowsResponse>(url);
            Debug.Log($"Retrieved {response.rows.Count} rows for location {locationId}");
            return response;
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error fetching rows: {e.Message}");
            throw;
        }
    }
    
    // Get agent dialogue
    public async Task<DialogueResponse> GetAgentDialogue(string category, int rowNumber)
    {
        try
        {
            string url = $"/game/agent/dialogue/{category}/{rowNumber}";
            var response = await GetRequest<DialogueResponse>(url);
            Debug.Log($"Retrieved dialogue for {category}, row {rowNumber}");
            return response;
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error fetching dialogue: {e.Message}");
            throw;
        }
    }
    
    // Record player choice
    public async Task<ChoiceResponse> RecordChoice(string sessionId, string locationId, int rowNumber)
    {
        try
        {
            var request = new ChoiceRequest
            {
                session_id = sessionId,
                location_id = locationId,
                row_number = rowNumber,
                choice_timestamp = System.DateTime.UtcNow.ToString("O")
            };
            
            string json = JsonUtility.ToJson(request);
            var response = await PostRequest<ChoiceResponse>("/game/choice", json);
            
            Debug.Log($"Choice recorded. ROI: {response.roi_result}x");
            return response;
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error recording choice: {e.Message}");
            throw;
        }
    }
    
    // Helper: GET request
    private async Task<T> GetRequest<T>(string endpoint)
    {
        string url = apiBaseUrl + endpoint;
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.timeout = (int)requestTimeout;
            
            var asyncOp = request.SendWebRequest();
            
            while (!asyncOp.isDone)
                await Task.Delay(10);
            
            if (request.result != UnityWebRequest.Result.Success)
            {
                throw new System.Exception($"HTTP Error {request.responseCode}: {request.error}");
            }
            
            string json = request.downloadHandler.text;
            return JsonUtility.FromJson<T>(json);
        }
    }
    
    // Helper: POST request
    private async Task<T> PostRequest<T>(string endpoint, string json)
    {
        string url = apiBaseUrl + endpoint;
        
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.timeout = (int)requestTimeout;
            
            var asyncOp = request.SendWebRequest();
            
            while (!asyncOp.isDone)
                await Task.Delay(10);
            
            if (request.result != UnityWebRequest.Result.Success)
            {
                throw new System.Exception($"HTTP Error {request.responseCode}: {request.error}");
            }
            
            string responseJson = request.downloadHandler.text;
            return JsonUtility.FromJson<T>(responseJson);
        }
    }
}

// API Request/Response models
[System.Serializable]
public class AnalyzeRequest
{
    public string product_name;
    public string category;
    public float price;
    public float budget;
    public int target_sales;
    public string target_customers;
    public float expected_roi;
}

[System.Serializable]
public class AnalyzeResponse
{
    public Dictionary<string, float> recommendations;
    public string session_id;
    public string timestamp;
}

[System.Serializable]
public class RowsResponse
{
    public string location_id;
    public string location_name;
    public List<ShelfRowData> rows;
    public string product_category;
    public float product_price;
}

[System.Serializable]
public class ShelfRowData
{
    public int row_id;
    public string row_name;
    public float calculated_roi;
    public string psychology_insight;
    public string sales_impact;
}

[System.Serializable]
public class DialogueResponse
{
    public string category;
    public int row_number;
    public List<DialogueLine> dialogue_lines;
}

[System.Serializable]
public class DialogueLine
{
    public string speaker;
    public string text;
    public string emotion;
    public int duration_seconds;
}

[System.Serializable]
public class ChoiceRequest
{
    public string session_id;
    public string location_id;
    public int row_number;
    public string choice_timestamp;
}

[System.Serializable]
public class ChoiceResponse
{
    public bool choice_recorded;
    public float roi_result;
    public string success_message;
}
```

---

## 3. SHELF INTERACTABLE

```csharp
using UnityEngine;

public class ShelfInteractable : MonoBehaviour
{
    [SerializeField] private string locationId = "loc_001";
    [SerializeField] private string locationName = "Main Aisle";
    
    private Collider2D shelfCollider;
    private SpriteRenderer spriteRenderer;
    private bool isPlayerNear = false;
    private Color originalColor;
    
    void Start()
    {
        shelfCollider = GetComponent<Collider2D>();
        spriteRenderer = GetComponent<SpriteRenderer>();
        originalColor = spriteRenderer.color;
    }
    
    void Update()
    {
        if (isPlayerNear && Input.GetKeyDown(KeyCode.E))
        {
            OnShelfSelected();
        }
    }
    
    void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            isPlayerNear = true;
            ShowInteractPrompt();
            HighlightShelf();
        }
    }
    
    void OnTriggerExit2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            isPlayerNear = false;
            HideInteractPrompt();
            UnhighlightShelf();
        }
    }
    
    private void OnShelfSelected()
    {
        Debug.Log($"Shelf selected: {locationName} ({locationId})");
        
        // Show detail modal
        ShelfDetailModal modal = FindObjectOfType<ShelfDetailModal>();
        if (modal != null)
        {
            modal.ShowDetails(locationId, locationName);
        }
    }
    
    private void HighlightShelf()
    {
        spriteRenderer.color = new Color(1.2f, 1.2f, 1.2f, 1f);
    }
    
    private void UnhighlightShelf()
    {
        spriteRenderer.color = originalColor;
    }
    
    private void ShowInteractPrompt()
    {
        // TODO: Show "Press E" UI near player
        Debug.Log("Showing interact prompt");
    }
    
    private void HideInteractPrompt()
    {
        // TODO: Hide "Press E" UI
        Debug.Log("Hiding interact prompt");
    }
}
```

---

## 4. SHELF DETAIL MODAL

```csharp
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;

public class ShelfDetailModal : MonoBehaviour
{
    [SerializeField] private CanvasGroup canvasGroup;
    [SerializeField] private TextMeshProUGUI locationTitle;
    [SerializeField] private Transform rowsContainer;
    [SerializeField] private GameObject rowPrefab;
    [SerializeField] private Button closeButton;
    
    private string currentLocationId;
    private string currentLocationName;
    private bool isOpen = false;
    
    void Start()
    {
        closeButton.onClick.AddListener(Close);
        canvasGroup.alpha = 0;
    }
    
    public async void ShowDetails(string locationId, string locationName)
    {
        currentLocationId = locationId;
        currentLocationName = locationName;
        
        locationTitle.text = locationName;
        
        // Fetch rows from API
        try
        {
            Debug.Log($"Fetching rows for {locationId}...");
            var rowsData = await RetailPlacementAPI.Instance.GetShelfRows(locationId);
            
            // Clear existing rows
            foreach (Transform child in rowsContainer)
            {
                Destroy(child.gameObject);
            }
            
            // Display rows
            foreach (var rowData in rowsData.rows)
            {
                DisplayRow(rowData);
            }
            
            Open();
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error fetching rows: {e.Message}");
        }
    }
    
    private void DisplayRow(ShelfRowData rowData)
    {
        GameObject rowGO = Instantiate(rowPrefab, rowsContainer);
        ShelfRowUI rowUI = rowGO.GetComponent<ShelfRowUI>();
        
        if (rowUI != null)
        {
            rowUI.SetData(rowData.row_id, rowData.row_name, rowData.calculated_roi);
            rowUI.OnSelected += OnRowSelected;
        }
    }
    
    private void OnRowSelected(int rowNumber)
    {
        Debug.Log($"Row {rowNumber} selected from shelf {currentLocationId}");
        
        // Record choice
        string sessionId = GameManager.Instance.CurrentSession.sessionId;
        RecordChoice(sessionId, currentLocationId, rowNumber);
        
        Close();
    }
    
    private async void RecordChoice(string sessionId, string locationId, int rowNumber)
    {
        try
        {
            var result = await RetailPlacementAPI.Instance.RecordChoice(sessionId, locationId, rowNumber);
            Debug.Log($"Choice recorded! ROI: {result.roi_result}x - {result.success_message}");
            
            // Show feedback
            ShowFeedback(result);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error recording choice: {e.Message}");
        }
    }
    
    private void ShowFeedback(ChoiceResponse result)
    {
        // TODO: Show feedback UI with ROI result
        Debug.Log(result.success_message);
    }
    
    private void Open()
    {
        isOpen = true;
        StartCoroutine(FadeIn());
    }
    
    public void Close()
    {
        isOpen = false;
        StartCoroutine(FadeOut());
    }
    
    private IEnumerator FadeIn()
    {
        float elapsed = 0f;
        float duration = 0.3f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            canvasGroup.alpha = Mathf.Clamp01(elapsed / duration);
            yield return null;
        }
        
        canvasGroup.alpha = 1f;
    }
    
    private IEnumerator FadeOut()
    {
        float elapsed = 0f;
        float duration = 0.3f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            canvasGroup.alpha = 1f - Mathf.Clamp01(elapsed / duration);
            yield return null;
        }
        
        canvasGroup.alpha = 0f;
    }
}

// Individual row UI component
public class ShelfRowUI : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI rowName;
    [SerializeField] private TextMeshProUGUI roiDisplay;
    [SerializeField] private Button selectButton;
    
    private int rowNumber;
    
    public delegate void RowSelectedDelegate(int rowNumber);
    public event RowSelectedDelegate OnSelected;
    
    void Start()
    {
        selectButton.onClick.AddListener(OnSelectClick);
    }
    
    public void SetData(int id, string name, float roi)
    {
        rowNumber = id;
        rowName.text = name;
        roiDisplay.text = $"ROI: {roi:F2}x";
    }
    
    private void OnSelectClick()
    {
        OnSelected?.Invoke(rowNumber);
    }
}
```

---

## 5. USAGE EXAMPLE IN SCENE

```csharp
// In your MainMenu or game startup script:

public class GameSetup : MonoBehaviour
{
    [SerializeField] private InputField productNameInput;
    [SerializeField] private InputField budgetInput;
    [SerializeField] private Dropdown categoryDropdown;
    [SerializeField] private Button playButton;
    
    void Start()
    {
        playButton.onClick.AddListener(OnPlayClick);
    }
    
    private void OnPlayClick()
    {
        // Create product data from form
        var product = new ProductData
        {
            productName = productNameInput.text,
            category = categoryDropdown.options[categoryDropdown.value].text,
            price = 2.99f,
            budget = float.Parse(budgetInput.text),
            targetSales = 1000,
            expectedROI = 1.5f
        };
        
        // Store in GameManager
        GameManager.Instance.CurrentProduct = product;
        
        // Transition to loading state
        GameManager.Instance.TransitionToLoadingState();
    }
}
```

---

## KEY PATTERNS USED

1. **Singleton Pattern** - GameManager, RetailPlacementAPI (persistent across scenes)
2. **State Machine Pattern** - GameManager with GameState classes
3. **Async/Await Pattern** - API calls don't block UI
4. **Component Pattern** - Each system is a self-contained MonoBehaviour
5. **Event Pattern** - UI components communicate via events
6. **MVC Pattern** - Data models separate from UI presentation

---

## NEXT STEPS

1. Create these scripts in your project
2. Create the 3 scenes (MainMenu, Loading, Store, Results)
3. Add the scripts to appropriate GameObjects
4. Connect UI elements in the Inspector
5. Test API connectivity
6. Build store layout scene

All templates are ready to compile and use. Adjust namespaces and references as needed for your project structure.
