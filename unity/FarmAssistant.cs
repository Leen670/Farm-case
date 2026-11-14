// POST https://farm-case-api.onrender.com/api/assistant
//
// Body: {"case": <the case JSON already on screen>, "question": "..."}
// Reply: {"answer": "..."}
//
// "case" is a C# keyword, so this builds the JSON from the case text
// the game already parsed. Twenty questions per minute.

using System;
using UnityEngine;

[Serializable]
public class AssistantReply
{
    public string answer;

    public static AssistantReply FromJson(string json)
    {
        return JsonUtility.FromJson<AssistantReply>(json);
    }
}

public static class FarmAssistant
{
    public static string Body(string caseJson, string question)
    {
        string encoded = JsonUtility.ToJson(new QuestionBox { question = question });
        return "{\"case\":" + caseJson + "," + encoded.TrimStart('{');
    }
}

[Serializable]
class QuestionBox
{
    public string question;
}
