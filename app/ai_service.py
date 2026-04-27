import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega a chave do arquivo .env
load_dotenv()

class AIService:
    def __init__(self):
        # Busca a chave no seu Mac (arquivo .env)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ ERRO: GEMINI_API_KEY não encontrada no arquivo .env")
            return
        
        # Configura o Gemini
        genai.configure(api_key=api_key)
        # Usamos o modelo flash que é mais rápido para testes
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

    def get_recipe_suggestion(self, ingredients: list):
        """
        Esta é a função que o main.py está procurando!
        """
        try:
            # Criamos uma instrução clara para a IA
            prompt = (
                f"I am a student using the SmartBite app. "
                f"I have these ingredients: {', '.join(ingredients)}. "
                f"Suggest a simple, healthy recipe I can make. "
                f"Keep it concise and professional."
            )
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating recipe: {str(e)}"