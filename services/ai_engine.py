import os
import requests
import json

class AIEngine:
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.model = "gemini-1.5-flash"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def get_travel_recommendation(self, user_query, user_context=None):
        if not self.api_key:
            return "AI features are currently in demo mode. Please set GOOGLE_API_KEY to enable full intelligence."

        prompt = f"You are a world-class travel assistant. User Query: {user_query}. "
        if user_context:
            prompt += f"User context: {json.dumps(user_context)}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}"

ai_engine = AIEngine()
