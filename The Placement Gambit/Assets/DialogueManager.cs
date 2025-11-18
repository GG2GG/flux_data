using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class DialogueManager : MonoBehaviour
{
    [Header("Game Objects")]
    public GameObject dialoguePanel;
    public GameObject bob; 

    [Header("UI Elements")]
    public TextMeshProUGUI speakerNameText;
    public TextMeshProUGUI dialogueText;
    public Button choice1Button;
    public Button choice2Button;
    public Button choice3Button;
    public GameObject continuePrompt;

    // --- Private State ---
    private PlayerMovement bobMovement;
    private GambitAgent gambitAgent;
    private APIController apiController; 

    private enum DialogueState { Inactive, ShowingManagerLine, ShowingPlayerChoices, ShowingSingleLine, ShowingManagerResponse, 
                                 ShowingGambitIntro, ShowingGambitChoices, ShowingGambitResponse, ShowingGambitReconvo,
                                 AwaitingApiCall }
    private DialogueState currentState;
    
    private int chosenGambitRow;
    private string chosenGambitCategory; 

    void Start()
    {
        bobMovement = bob.GetComponent<PlayerMovement>();
        gambitAgent = FindObjectOfType<GambitAgent>();
        apiController = FindObjectOfType<APIController>(); 
        StartManagerConversation();
    }

    void Update()
    {
        if (currentState == DialogueState.ShowingManagerLine && Input.GetKeyDown(KeyCode.X))
            ShowPlayerChoices();
        else if (currentState == DialogueState.ShowingManagerResponse && Input.GetKeyDown(KeyCode.X))
        {
            EndConversation(); 
            if (gambitAgent != null) gambitAgent.StartApproach(bob.transform);
        }
        else if (currentState == DialogueState.ShowingSingleLine && Input.GetKeyDown(KeyCode.X))
            EndConversation();
        else if (currentState == DialogueState.ShowingGambitIntro && Input.GetKeyDown(KeyCode.X))
        {
            gambitAgent.hasIntroducedHimself = true; 
            ShowGambitChoiceButtons(); 
        }
        else if (currentState == DialogueState.ShowingGambitReconvo && Input.GetKeyDown(KeyCode.X))
            ShowGambitChoiceButtons();
        else if (currentState == DialogueState.ShowingGambitResponse && Input.GetKeyDown(KeyCode.X))
        {
            EndConversation();
            gambitAgent.GoToRow(chosenGambitRow);
        }
        else if (currentState == DialogueState.AwaitingApiCall && Input.GetKeyDown(KeyCode.X))
        {
            EndConversation();
            apiController.StartDemoApiCall(chosenGambitRow, chosenGambitCategory);
        }
        // --- THIS IS THE FINAL STEP ---
        else if (currentState == DialogueState.AwaitingDashboardLaunch && Input.GetKeyDown(KeyCode.X))
        {
            // We end the convo, AND launch the dashboard
            EndConversation();
            LaunchDashboard(); // <-- This is the new function
        }
    }

    // --- NEW FUNCTION to launch the browser ---
    // --- NEW FUNCTION to launch the browser ---
    void LaunchDashboard()
    {
        // This is the URL from your "Terminal 2" server
        string dashboardUrl = "http://127.0.0.1:8001/demo/planogram_final.html"; 
        
        Debug.Log("--- Launching Dashboard at " + dashboardUrl + " ---");
        
        // This command opens your default web browser (Chrome, Firefox, etc.)
        Application.OpenURL(dashboardUrl);

        // --- THIS IS THE NEW LINE ---
        // This will kick the game out of fullscreen mode
        Screen.fullScreen = false;
    }
    // ----------------------------------------
    // ----------------------------------------
    
    // --- This function now leads to the launch state ---
    public void ShowGambitFinalLine(string line, int rowNum)
    {
        if (currentState != DialogueState.Inactive) return; 

        bobMovement.enabled = false;
        dialoguePanel.SetActive(true);
        speakerNameText.text = "The Placement Gambit";
        dialogueText.text = line;
        
        continuePrompt.SetActive(true);
        choice1Button.gameObject.SetActive(false);
        choice2Button.gameObject.SetActive(false);
        choice3Button.gameObject.SetActive(false);
        
        currentState = DialogueState.AwaitingDashboardLaunch; // <-- Set the new state
        chosenGambitRow = rowNum; 
    }

    // (All other functions are identical to the version you provided)
    
    public void ShowGambitFinalLine(string line, int rowNum)
    {
        if (currentState != DialogueState.Inactive) return; 

        bobMovement.enabled = false;
        dialoguePanel.SetActive(true);
        speakerNameText.text = "The Placement Gambit";
        dialogueText.text = line;
        
        continuePrompt.SetActive(true);
        choice1Button.gameObject.SetActive(false);
        choice2Button.gameObject.SetActive(false);
        choice3Button.gameObject.SetActive(false);
        
        currentState = DialogueState.AwaitingApiCall; 
        chosenGambitRow = rowNum; 
        
        if(rowNum == 1) chosenGambitCategory = "Dry Goods & Packaged Foods";
        if(rowNum == 2) chosenGambitCategory = "Health & Beauty";
        if(rowNum == 3) chosenGambitCategory = "General Merchandise & Electronics";
    }

    public void StartGambitReconvo()
    {
        if (currentState != DialogueState.Inactive) return;
        currentState = DialogueState.ShowingGambitReconvo; 
        bobMovement.enabled = false;
        dialoguePanel.SetActive(true);
        speakerNameText.text = "The Placement Gambit";
        dialogueText.text = "Tell me, which product category are you targeting?";
        continuePrompt.SetActive(true);
        choice1Button.gameObject.SetActive(false);
        choice2Button.gameObject.SetActive(false);
        choice3Button.gameObject.SetActive(false);
    }

    public void ShowGambitIntro()
    {
        bobMovement.enabled = false;
        dialoguePanel.SetActive(true);
        currentState = DialogueState.ShowingGambitIntro;
        speakerNameText.text = "The Placement Gambit";
        dialogueText.text = "Don't listen to him. I am The Placement Gambit. Tell me which type of product do you want.";
        continuePrompt.SetActive(true);
        choice1Button.gameObject.SetActive(false);
        choice2Button.gameObject.SetActive(false);
        choice3Button.gameObject.SetActive(false);
    }

    void ShowGambitChoiceButtons()
    {
        currentState = DialogueState.ShowingGambitChoices;
        speakerNameText.text = "Bob";
        dialogueText.text = ""; 
        continuePrompt.SetActive(false);
        choice1Button.gameObject.SetActive(true);
        choice2Button.gameObject.SetActive(true);
        choice3Button.gameObject.SetActive(true);
        choice1Button.GetComponentInChildren<TextMeshProUGUI>().text = "Dry Goods & Packaged Foods";
        choice2Button.GetComponentInChildren<TextMeshProUGUI>().text = "Health & Beauty";
        choice3Button.GetComponentInChildren<TextMeshProUGUI>().text = "General Merchandise & Electronics";
        choice1Button.onClick.RemoveAllListeners();
        choice2Button.onClick.RemoveAllListeners();
        choice3Button.onClick.RemoveAllListeners(); 
        choice1Button.onClick.AddListener(OnGambitChoice1);
        choice2Button.onClick.AddListener(OnGambitChoice2);
        choice3Button.onClick.AddListener(OnGambitChoice3);
    }

    void OnGambitChoice1() { ShowGambitResponse(1); }
    void OnGambitChoice2() { ShowGambitResponse(2); }
    void OnGambitChoice3() { ShowGambitResponse(3); }

    void ShowGambitResponse(int rowNum)
    {
        this.chosenGambitRow = rowNum; 
        currentState = DialogueState.ShowingGambitResponse;
        speakerNameText.text = "The Placement Gambit";
        dialogueText.text = "Follow me.";
        continuePrompt.SetActive(true);
        choice1Button.gameObject.SetActive(false);
        choice2Button.gameObject.SetActive(false);
        choice3Button.gameObject.SetActive(false);
    }

    public void ShowSingleLineDialogue(string speaker, string line)
    {
        if (currentState != DialogueState.Inactive) return; 
        bobMovement.enabled = false;
        dialoguePanel.SetActive(true);
        speakerNameText.text = speaker;
        dialogueText.text = line;
        continuePrompt.SetActive(true);
        choice1Button.gameObject.SetActive(false);
        choice2Button.gameObject.SetActive(false);
        choice3Button.gameObject.SetActive(false);
        currentState = DialogueState.ShowingSingleLine;
    }

    public void StartManagerConversation()
    {
        if (currentState != DialogueState.Inactive) return; 
        currentState = DialogueState.ShowingManagerLine;
        bobMovement.enabled = false;
        dialoguePanel.SetActive(true);
        speakerNameText.text = "Store Manager";
        dialogueText.text = "How may I help?";
        continuePrompt.SetActive(true);
        choice1Button.gameObject.SetActive(false);
        choice2Button.gameObject.SetActive(false);
        choice3Button.gameObject.SetActive(false); 
        choice1Button.onClick.RemoveAllListeners();
        choice2Button.onClick.RemoveAllListeners();
        choice1Button.onClick.AddListener(OnChoice1Selected);
        choice2Button.onClick.AddListener(OnChoice2Selected);
    }

    void ShowPlayerChoices()
    {
        speakerNameText.text = "Bob";
        dialogueText.text = ""; 
        continuePrompt.SetActive(false);
        choice1Button.gameObject.SetActive(true);
        choice2Button.gameObject.SetActive(true);
        choice3Button.gameObject.SetActive(false);
        choice1Button.GetComponentInChildren<TextMeshProUGUI>().text = "I am here to shop.";
        choice2Button.GetComponentInChildren<TextMeshProUGUI>().text = "I am here to sell a new product.";
        currentState = DialogueState.ShowingPlayerChoices;
    }

    void OnChoice1Selected() { EndConversation(); }

    void OnChoice2Selected()
    {
        currentState = DialogueState.ShowingManagerResponse;
        speakerNameText.text = "Store Manager";
        dialogueText.text = "I understand. Unfortunately, our current shelf allocation is completely full. We *might* be able to make an exception for a promising product, but it would require a review and would likely involve a placement fee to cover the re-stocking.";
        choice1Button.gameObject.SetActive(false);
        choice2Button.gameObject.SetActive(false);
        continuePrompt.SetActive(true);
    }

    public void EndConversation() // <-- Made public so GambitAgent can call it
    {
        dialoguePanel.SetActive(false);
        bobMovement.enabled = true;
        currentState = DialogueState.Inactive;
    }
}