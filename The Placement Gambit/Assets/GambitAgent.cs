using UnityEngine;

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

    // --- Private State ---
    private Transform playerTarget;
    private Transform currentRowTarget;
    private DialogueManager dialogueManager;
    
    // <-- NEW STATE ADDED
    private enum AgentState { Idle, ApproachingPlayer, AwaitingPlayerChoice, MovingToRow, WaitingAtRow }
    private AgentState currentState = AgentState.Idle;

    void Start()
    {
        dialogueManager = FindObjectOfType<DialogueManager>();
    }

    void Update()
    {
        if (currentState == AgentState.ApproachingPlayer)
        {
            MoveToTarget(playerTarget.position);
            
            // Check if we've arrived at the player
            if (Vector2.Distance(transform.position, playerTarget.position) < 1.5f)
            {
                // <-- UPDATED: Tell manager to start the INTRO, not the choices
                dialogueManager.ShowGambitIntro(); 
                currentState = AgentState.AwaitingPlayerChoice; // <-- NEW: Wait for a choice
            }
        }
        else if (currentState == AgentState.MovingToRow)
        {
            MoveToTarget(currentRowTarget.position);

            if (Vector2.Distance(transform.position, currentRowTarget.position) < 0.1f)
            {
                currentState = AgentState.WaitingAtRow;
            }
        }
    }

    void MoveToTarget(Vector2 targetPosition)
    {
        float step = moveSpeed * Time.deltaTime;
        transform.position = Vector2.MoveTowards(transform.position, targetPosition, step);
    }

    public void StartApproach(Transform target)
    {
        this.playerTarget = target;
        this.currentState = AgentState.ApproachingPlayer;
    }

    // This function is the same, it just gets called later now
    public void GoToRow(int rowNum)
    {
        currentState = AgentState.MovingToRow;
        if (rowNum == 1) currentRowTarget = row1Target;
        if (rowNum == 2) currentRowTarget = row2Target;
        if (rowNum == 3) currentRowTarget = row3Target;
    }

    private void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player") && currentState == AgentState.WaitingAtRow)
        {
            string lineToSay = "";
            if (currentRowTarget == row1Target) lineToSay = row1Dialogue;
            if (currentRowTarget == row2Target) lineToSay = row2Dialogue;
            if (currentRowTarget == row3Target) lineToSay = row3Dialogue;

            dialogueManager.ShowSingleLineDialogue("The Placement Gambit", lineToSay);
            currentState = AgentState.Idle;
        }
    }
}