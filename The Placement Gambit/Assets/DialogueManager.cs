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

    private PlayerMovement bobMovement;
    private GambitAgent gambitAgent; 
    
    // <-- NEW STATES ADDED
    private enum DialogueState { Inactive, ShowingManagerLine, ShowingPlayerChoices, ShowingSingleLine, ShowingManagerResponse, 
                                 ShowingGambitIntro, ShowingGambitChoices, ShowingGambitResponse }
    private DialogueState currentState;
    
    private int chosenGambitRow; // <-- To remember the choice

    void Start()
    {
        bobMovement = bob.GetComponent<PlayerMovement>();
        gambitAgent = FindObjectOfType<GambitAgent>();
        StartManagerConversation();
    }

    void Update()
    {
        // Manager convo
        if (currentState == DialogueState.ShowingManagerLine && Input.GetKeyDown(KeyCode.X))
        {
            ShowPlayerChoices();
        }
        else if (currentState == DialogueState.ShowingManagerResponse && Input.GetKeyDown(KeyCode.X))
        {
            EndConversation(); 
            if (gambitAgent != null) gambitAgent.StartApproach(bob.transform);
        }
        // Shopper convo
        else if (currentState == DialogueState.ShowingSingleLine && Input.GetKeyDown(KeyCode.X))
        {
            EndConversation();
        }
        // --- NEW GAMBIT CONVO FLOW ---
        else if (currentState == DialogueState.ShowingGambitIntro && Input.GetKeyDown(KeyCode.X))
        {
            ShowGambitChoiceButtons(); // Move to the 3 choices
        }
        else if (currentState == DialogueState.ShowingGambitResponse && Input.GetKeyDown(KeyCode.X))
        {
            EndConversation();
            gambitAgent.GoToRow(chosenGambitRow); // Tell agent to move
        }
    }
    
    // --- NEW: Renamed from ShowGambitChoices ---
    public void ShowGambitIntro()
    {
        bobMovement.enabled = false;
        dialoguePanel.SetActive(true);
        currentState = DialogueState.ShowingGambitIntro;

        speakerNameText.text = "The Placement Gambit";
        dialogueText.text = "Don't listen to him. I am The Placement Gambit. Tell me which type of product do you want.";

        continuePrompt.SetActive(true); // Show "Press X"
        choice1Button.gameObject.SetActive(false);
        choice2Button.gameObject.SetActive(false);
        choice3Button.gameObject.SetActive(false);
    }

    // --- NEW: This function shows the 3 buttons ---
    void ShowGambitChoiceButtons()
    {
        currentState = DialogueState.ShowingGambitChoices;
        speakerNameText.text = "Bob";
        dialogueText.text = ""; // Bob is choosing

        continuePrompt.SetActive(false);
        choice1Button.gameObject.SetActive(true);
        choice2Button.gameObject.SetActive(true);
        choice3Button.gameObject.SetActive(true);

        // Set button text
        choice1Button.GetComponentInChildren<TextMeshProUGUI>().text = "Dry Goods & Packaged Foods";
        choice2Button.GetComponentInChildren<TextMeshProUGUI>().text = "Health & Beauty";
        choice3Button.GetComponentInChildren<TextMeshProUGUI>().text = "General Merchandise & Electronics";

        // Wire up buttons
        choice1Button.onClick.RemoveAllListeners();
        choice2Button.onClick.RemoveAllListeners();
        choice3Button.onClick.RemoveAllListeners(); 

        choice1Button.onClick.AddListener(OnGambitChoice1);
        choice2Button.onClick.AddListener(OnGambitChoice2);
        choice3Button.onClick.AddListener(OnGambitChoice3);
    }

    // --- NEW: These now lead to the "Follow me" line ---
    void OnGambitChoice1() { ShowGambitResponse(1); }
    void OnGambitChoice2() { ShowGambitResponse(2); }
    void OnGambitChoice3() { ShowGambitResponse(3); }

    // --- NEW: This function shows the "Follow me" line ---
    void ShowGambitResponse(int rowNum)
    {
        this.chosenGambitRow = rowNum; // Remember the choice
        currentState = DialogueState.ShowingGambitResponse;

        speakerNameText.text = "The Placement Gambit";
        dialogueText.text = "Follow me.";
        
        continuePrompt.SetActive(true); // Show "Press X"
        choice1Button.gameObject.SetActive(false);
        choice2Button.gameObject.SetActive(false);
        choice3Button.gameObject.SetActive(false);
    }

    // --- (The rest of the functions are mostly the same) ---

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

    void EndConversation()
    {
        dialoguePanel.SetActive(false);
        bobMovement.enabled = true;
        currentState = DialogueState.Inactive;
    }
}