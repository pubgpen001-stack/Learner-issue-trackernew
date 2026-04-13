import os
import requests
import json
from flask import current_app

def check_content(text):
    """
    Checks the provided text for inappropriate content using the OpenRouter LLM moderation API.
    Returns True if flagged, False otherwise.
    """
    if not text or not text.strip():
        return False
        
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        if current_app:
            current_app.logger.warning("OPENROUTER_API_KEY is not set. Moderation skipped.")
        return False
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen/qwen-plus",
        "messages": [
            {
                "role": "system",
                "content": "You are a strict content moderator for a university educational platform. Analyze the user's text for profanity, slurs, offensive language, abuse, or highly inappropriate content. Respond ONLY with a standard JSON object containing exactly two keys: 'flagged' (boolean) and 'reason' (string category, or empty string if not flagged). Example: {\"flagged\": true, \"reason\": \"profanity\"} or {\"flagged\": false, \"reason\": \"\"}."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        result_text = data['choices'][0]['message']['content'].strip()
        
        # Try to parse markdown if the model wrapped it
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
            
        result_json = json.loads(result_text)
        return result_json.get('flagged', False)
    except Exception as e:
        if current_app:
            current_app.logger.warning(f"Moderation API check failed: {e}")
        return False
