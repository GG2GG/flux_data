using UnityEngine;
using UnityEngine.InputSystem;

public class GambitAgent : MonoBehaviour
{
    [Header("Movement")]
    public float moveSpeed = 3f;

    [Header("Row Targets")]
    public Transform row1Target;
    public Transform row2Target;
    public Transform row3Target;

    [Header("Row Dialogue")]
    public string row1Dialogue = "This is the primary location for Dry Goods. The slotting fees are high, but so is the turnover.";
    public string row2Dialogue = "This is the Health & Beauty section. A bit lower traffic, but the profit margins per unit are excellent.";
    public string row3Dialogue = "This is General Merchandise. It's a high-velocity aisle, perfect for impulse buys and seasonal items.";

    [Header("State & Settings")]
    public bool hasIntroducedHimself = false; // Flag to skip intro

    // --- Private State ---
    private Transform playerTarget;
    private Transform currentRowTarget;
    private DialogueManager dialogueManager;
    private PlayerControls playerControls; 

    private bool playerIsNearby = false;
    
    private enum AgentState { Idle, ApproachingPlayer, MovingToRow, WaitingAtRow }
    private AgentState currentState = AgentState.Idle;

    void Awake()
    {
        playerControls = new PlayerControls();
        playerControls.Player.Interact.performed += OnInteract;
    }

    void Start()
    {
        dialogueManager = FindObjectOfType<DialogueManager>();
    }

    // --- Need to enable/disable the input listener ---
    private void OnEnable()
    {
        playerControls.Player.Interact.Enable();
    }
    private void OnDisable()
    {
        playerControls.Player.Interact.Disable();
    }

    void Update()
    {
        // --- Logic for approaching the player ---
        if (currentState == AgentState.ApproachingPlayer)
        {
            MoveToTarget(playerTarget.position);
            
            // Check if we've arrived
            if (Vector2.Distance(transform.position, playerTarget.position) < 1.5f)
            {
                dialogueManager.ShowGambitIntro(); // Start the intro
                currentState = AgentState.Idle; // Stop moving
            }
        }
        // --- Logic for moving to a shelf ---
        else if (currentState == AgentState.MovingToRow)
        {
            MoveToTarget(currentRowTarget.position);

            // Check if we've arrived
            if (Vector2.Distance(transform.position, currentRowTarget.position) < 0.1f)
            {
                currentState = AgentState.WaitingAtRow; // Stop and wait
            }
        }
    }

    // Helper function for movement
    void MoveToTarget(Vector2 targetPosition)
    {
        float step = moveSpeed * Time.deltaTime;
        transform.position = Vector2.MoveTowards(transform.position, targetPosition, step);
    }

    // --- Public Functions Called by DialogueManager ---

    public void StartApproach(Transform target)
    {
        this.playerTarget = target;
        this.currentState = AgentState.ApproachingPlayer;
    }

    public void GoToRow(int rowNum)
    {
        currentState = AgentState.MovingToRow;
        if (rowNum == 1) currentRowTarget = row1Target;
        if (rowNum == 2) currentRowTarget = row2Target;
        if (rowNum == 3) currentRowTarget = row3Target;
    }

    // --- Interaction Logic (This is the only trigger section) ---

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            playerIsNearby = true; 
            
            if (currentState == AgentState.WaitingAtRow)
            {
                string lineToSay = "";
                int rowNum = 0; // <-- Need to store the row number

                if (currentRowTarget == row1Target) 
                {
                    lineToSay = row1Dialogue;
                    rowNum = 1;
                }
                if (currentRowTarget == row2Target)
                {
                    lineToSay = row2Dialogue;
                    rowNum = 2;
                }
                if (currentRowTarget == row3Target)
                {
                    lineToSay = row3Dialogue;
                    rowNum = 3;
                }

                // --- THIS IS THE FIX ---
                // We are now calling the new function that knows about the dashboard
                dialogueManager.ShowGambitFinalLine(lineToSay, rowNum);
                // ---------------------

                currentState = AgentState.Idle;
            }
        }
    }
    // ------------------------------------

    private void OnTriggerExit2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            string lineToSay = "";
            int rowNum = 0;

            if (currentRowTarget == row1Target) 
            {
                lineToSay = row1Dialogue;
                rowNum = 1;
            }
            if (currentRowTarget == row2Target)
            {
                lineToSay = row2Dialogue;
                rowNum = 2;
            }
            if (currentRowTarget == row3Target)
            {
                lineToSay = row3Dialogue;
                rowNum = 3;
            }

            // --- THIS IS THE CHANGE ---
            // Instead of the generic ShowSingleLine, we call a new, specific function
            dialogueManager.ShowGambitFinalLine(lineToSay, rowNum);
            // --------------------------

            currentState = AgentState.Idle;
        }
    }

    private void OnTriggerExit2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            playerIsNearby = false;
        }
    }

    // This is called when the player presses "E"
    private void OnInteract(InputAction.CallbackContext context)
    {
        // Check if player is nearby, agent is idle, AND has done his intro
        if (playerIsNearby && currentState == AgentState.Idle && hasIntroducedHimself)
        {
            // Call the new "re-conversation" function
            dialogueManager.StartGambitReconvo(); 
        }
    }
}