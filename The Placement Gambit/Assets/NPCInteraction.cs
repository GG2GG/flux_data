using UnityEngine;
using UnityEngine.InputSystem;

public class NPCInteraction : MonoBehaviour
{
    // <-- NEW: We create a dropdown menu for the Inspector
    public enum ConversationType 
    { 
        SingleLine, 
        StoreManagerIntro 
    }
    public ConversationType conversationType;
    // ------------------------------------------------

    [Header("Dialogue (For SingleLine Only)")] // <-- Title changed
    public string dialogueLine = "It is so difficult to find anything in this store.";
    public string speakerName = "Shopper";

    private bool playerIsNearby = false;
    private PlayerControls playerControls;
    private DialogueManager dialogueManager;

    void Awake()
    {
        playerControls = new PlayerControls();
        playerControls.Player.Interact.performed += OnInteract;
        dialogueManager = FindObjectOfType<DialogueManager>();
    }
    
    private void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            playerIsNearby = true;
            playerControls.Player.Interact.Enable();
        }
    }

    private void OnTriggerExit2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            playerIsNearby = false;
            playerControls.Player.Interact.Disable();
        }
    }

    // <-- UPDATED to use the new dropdown
    private void OnInteract(InputAction.CallbackContext context)
    {
        if (playerIsNearby)
        {
            // Use a switch to decide which conversation to start
            switch (conversationType)
            {
                case ConversationType.SingleLine:
                    dialogueManager.ShowSingleLineDialogue(speakerName, dialogueLine);
                    break;
                
                case ConversationType.StoreManagerIntro:
                    dialogueManager.StartManagerConversation();
                    break;
            }
        }
    }
}