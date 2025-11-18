using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class APIController : MonoBehaviour
{
    // We'll call this from the DialogueManager
    public void StartDemoApiCall(int rowNumber, string category)
    {
        // Start the web request as a "coroutine"
        StartCoroutine(RunDemo(rowNumber, category));
    }

    IEnumerator RunDemo(int rowNumber, string category)
    {
        // 1. Define the Python server endpoint
        // This assumes your Python demo runs on localhost port 8000
        string url = "http://127.0.0.1:8000/run_demo";

        // 2. Create the data payload
        // We'll send a simple JSON object
        DemoRequestData data = new DemoRequestData();
        data.row = rowNumber;
        data.category = category;
        string jsonPayload = JsonUtility.ToJson(data);
        
        // 3. Create the UnityWebRequest
        // We use a "POST" request to send data
        using (UnityWebRequest www = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonPayload);
            www.uploadHandler = new UploadHandlerRaw(bodyRaw);
            www.downloadHandler = new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            // 4. Send the request and wait
            Debug.Log("--- Sending API request to Python demo ---");
            Debug.Log("Payload: " + jsonPayload);

            yield return www.SendWebRequest();

            // 5. Handle the response
            if (www.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Success! Python demo responded: " + www.downloadHandler.text);
            }
            else
            {
                Debug.LogError("API Call Failed: " + www.error);
            }
        }
    }
}

// A simple helper class to create the JSON object
[System.Serializable]
class DemoRequestData
{
    public int row;
    public string category;
}