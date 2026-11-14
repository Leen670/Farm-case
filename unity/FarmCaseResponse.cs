// POST https://farm-case-api.onrender.com/api/case/simple
//
// Unity's JsonUtility reads public fields only. The JSON is one object,
// arrays of strings and cards, and no nulls. Field names match the JSON.
// demo_data is true when the climate numbers came from a saved response.

using System;
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Text;

[Serializable]
public class SimpleClue
{
    public string name;
    public string line;
    public string source;
    public string image_url;
}

[Serializable]
public class SimplePlan
{
    public string[] crops;
    public int score;
    public string[] why;
    public string[] risks;
}

[Serializable]
public class FarmCaseResponse
{
    public string title;
    public SimpleClue[] clues;
    public SimplePlan recommended;
    public SimplePlan[] alternatives;
    public bool demo_data;

    public static FarmCaseResponse FromJson(string json)
    {
        return JsonUtility.FromJson<FarmCaseResponse>(json);
    }
}

public class FarmCaseClient : MonoBehaviour
{
    const string Url = "https://farm-case-api.onrender.com/api/case/simple";

    public void RequestAmes()
    {
        const string body =
            "{\"farmer_name\":\"Ada\",\"lat\":42.03,\"lon\":-93.62," +
            "\"soil\":\"loamy\",\"water_level\":\"limited\",\"water_source\":\"rain\"}";
        StartCoroutine(Post(body));
    }

    IEnumerator Post(string json)
    {
        byte[] raw = Encoding.UTF8.GetBytes(json);
        using UnityWebRequest request = new UnityWebRequest(Url, "POST");
        request.uploadHandler = new UploadHandlerRaw(raw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError(request.error);
            yield break;
        }

        FarmCaseResponse result = FarmCaseResponse.FromJson(request.downloadHandler.text);
        Debug.Log(result.title + " " + result.recommended.score);
    }
}
