using UnityEngine;
using UnityEngine.InputSystem; // Import the New Input System

public class PlayerMovement : MonoBehaviour
{
    // Public variable for movement speed (you can change this in Unity)
    public float moveSpeed = 5f;

    // Private variables
    private Rigidbody2D rb;
    private PlayerControls playerControls;
    private Vector2 moveInput;

    // This is called when the script is first loaded
    void Awake()
    {
        // Get references to our components
        rb = GetComponent<Rigidbody2D>();
        playerControls = new PlayerControls();
    }

    // This is called when the object is enabled
    private void OnEnable()
    {
        // Tell the "Move" action to call our "OnMove" function
        playerControls.Player.Move.performed += OnMove;
        playerControls.Player.Move.canceled += OnMove;
        playerControls.Player.Move.Enable();
    }

    // This is called when the object is disabled
    private void OnDisable()
    {
        playerControls.Player.Move.Disable();
    }

    // This function is called by the Input System
    private void OnMove(InputAction.CallbackContext context)
    {
        // Read the "Vector2" value from the input (e.g., W,A,S,D)
        moveInput = context.ReadValue<Vector2>();
    }

    // FixedUpdate is called every physics step (best for Rigidbody)
    void FixedUpdate()
    {
        // Apply the movement to the Rigidbody
        rb.linearVelocity = moveInput * moveSpeed;
    }
}