import requests
import config

CRISIS_KEYWORDS = [
    "suicid", "kill myself", "end it all",
    "don't want to live", "hurt myself",
    "self harm", "worthless", "nobody cares"
]

CRISIS_RESPONSE = """I hear you, and I want you to know you matter deeply. 💙

What you're feeling right now is real — but it's not permanent.

Please reach out right now:
🆘 International: https://findahelpline.com
🇺🇸 US Crisis Line: 988 (call or text)
🌍 Crisis Text: Text HOME to 741741

You don't have to go through this alone.
I'm here too — tell me what's going on. 💙"""

def check_for_crisis(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in CRISIS_KEYWORDS)

def get_ai_response(user_message, system_context, conversation_history=None):
    if not config.GEMINI_API_KEY:
        return "I'm not fully connected yet. Please check the API key setup."

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{config.GEMINI_MODEL}:generateContent"
        f"?key={config.GEMINI_API_KEY}"
    )

    history_text = ""
    if conversation_history:
        recent = conversation_history[-(config.MAX_CONTEXT_MESSAGES * 2):]
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Coach"
            history_text += f"{role}: {msg['content']}\n"

    full_prompt = f"""{system_context}

{('Conversation so far:\n' + history_text) if history_text else ''}

User: {user_message}

Coach (respond now):"""

    payload = {
        "contents": [
            {
                "parts": [{"text": full_prompt}]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 1024,
            "temperature": 0.75,
            "topP": 0.9
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()

        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        elif "error" in data:
            return f"AI error: {data['error']['message']}"
        else:
            return "I couldn't generate a response. Please try again."

    except requests.exceptions.Timeout:
        return "I'm taking too long to respond. Please try again. 💙"
    except Exception as e:
        return f"Something went wrong: {str(e)}"
