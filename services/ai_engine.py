import os
import requests
import json
from new_models import Destination

class AIEngine:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyDcwojg2ngA1ZW0-votJyiPp1MhV7MI1u0')
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.api_key}"
    
    def generate_response(self, user_message, context=None):
        """Generate AI response using Gemini API with local database knowledge"""
        
        # 1. Try to find local information first
        local_info = ""
        msg_lower = user_message.lower()
        
        try:
            # Avoid circular import by accessing app context differently
            from flask import current_app
            with current_app.app_context():
                all_dest = Destination.query.all()
                for d in all_dest:
                    if d.name.lower() in msg_lower:
                        local_info += f"\n- We have a featured destination: {d.name}, {d.country}. {d.description} Starting from ${d.price}. Best time to visit: {d.best_time_to_visit or 'Contact us for details'}."
        except Exception as e:
            # Fallback for testing outside of flask context
            try:
                from db import db
                from app import app
                with app.app_context():
                    all_dest = Destination.query.all()
                    for d in all_dest:
                        if d.name.lower() in msg_lower:
                            local_info += f"\n- Featured destination: {d.name}. {d.description}"
            except:
                pass

        # Enhanced system prompt for natural conversation
        system_prompt = f"""You are a knowledgeable and friendly AI travel assistant for World Tour. 
        
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

Information about our currently featured destinations:
{local_info if local_info else "We have many world-class destinations in Kenya and beyond."}

Guidelines:
- If the user asks about a destination we have (listed above), emphasize it!
- Be conversational and engaging, not robotic
- Use emojis occasionally (✈️ 🏨 🌍 ⭐)
- Keep responses concise but informative
- Always end with a helpful follow-up question or suggestion"""

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
                    "maxOutputTokens": 800,
                }
            }
            
            response = requests.post(
                self.api_url,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and data['candidates']:
                    return data['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"Gemini API Error: {response.status_code} - {response.text}")
            
            # If API fails or is slow, return a smart local response
            if local_info:
                return f"I'd love to help you with that! Regarding your interest, here's what we have available: {local_info}\n\nWould you like me to book a flight or find a hotel for you there? ✈️"
            
            return "That's a great question! I'm seeing some exciting options for you. Most travelers love places like Paris or the Maasai Mara. What kind of vibe are you looking for? 🌍"

        except Exception as e:
            print(f"AI Engine Error: {e}")
            if local_info:
                return f"I'm experiencing some connectivity issues, but I can tell you that we have great deals for your destination! {local_info}\n\nWould you like more details? 🏨"
            return "I'm having a bit of trouble connecting to my travel database, but I'm here to help! Could you tell me more about where you'd like to go? ✈️"

ai_engine = AIEngine()
