import os
import requests
import json

class AIEngine:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyAQOFn1SVkbrQDJn7VeRMs5vAV1mYErImM')
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"
    
    def generate_response(self, user_message, context=None):
        """Generate AI response using Gemini API with enhanced travel intelligence"""
        
        # Enhanced system prompt for natural conversation
        system_prompt = """You are a knowledgeable and friendly AI travel assistant for World Tour. 
        
Your personality:
- Enthusiastic about travel and helping people explore the world
- Conversational and warm, like chatting with a well-traveled friend
- Provide specific, actionable recommendations
- Ask follow-up questions to better understand user needs
- Share interesting facts and insider tips about destinations

Your capabilities:
- Recommend destinations based on preferences (budget, climate, activities, culture)
- Suggest hotels, flights, and complete itineraries
- Provide travel tips, visa information, and local customs
- Help with trip planning (best times to visit, what to pack, etc.)
- Answer questions about specific cities, countries, and attractions

Guidelines:
- Be conversational and engaging, not robotic
- Use emojis occasionally to add warmth (✈️ 🏨 🌍 ⭐)
- Keep responses concise but informative (2-4 paragraphs max)
- Always end with a helpful follow-up question or suggestion
- If discussing specific destinations, mention approximate costs and best seasons
- Personalize responses based on user context when available"""

        # Build the full prompt
        if context:
            user_info = f"\n\nUser Context: {json.dumps(context)}"
            full_prompt = f"{system_prompt}{user_info}\n\nUser: {user_message}\n\nAssistant:"
        else:
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
        
        try:
            payload = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.9,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            response = requests.post(
                self.api_url,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Handle potential safety ratings blocking content
            if 'candidates' in data and data['candidates']:
                return data['candidates'][0]['content']['parts'][0]['text']
            return "I couldn't generate a response. Please try asking differently."
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}"

ai_engine = AIEngine()
