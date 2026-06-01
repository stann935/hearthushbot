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
    if not config.GROQ_API_KEY:
        return "I'm not fully connected yet. Please check the API key setup."

    url = "https://api.groq.com/openai/v1/chat/completions"

    messages = [{"role": "system", "content": system_context}]

    if conversation_history:
        recent = conversation_history[-(config.MAX_CONTEXT_MESSAGES * 2):]
        for msg in recent:
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.75,
        "top_p": 0.9
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()
        elif "error" in data:
            return f"AI error: {data['error']['message']}"
        else:
            return "I couldn't generate a response. Please try again."

    except requests.exceptions.Timeout:
        return "I'm taking too long to respond. Please try again. 💙"
    except Exception as e:
        return f"Something went wrong: {str(e)}"
