import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API Key not found in .env file")
            
        genai.configure(api_key=api_key)
        

        self.model = genai.GenerativeModel(model_name='models/gemini-2.5-flash')
    async def suggest_recipe(self, ingredients: list):
        prompt = (
            f"I have these ingredients: {', '.join(ingredients)}. "
            "Suggest a quick, healthy, and easy recipe for a college student. "
            "Please respond in English."
        )
        # Remember the 'await' and '_async' for FastAPI performance
        response = await self.model.generate_content_async(prompt)
        return response.text