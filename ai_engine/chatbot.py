import google.generativeai as genai
import os

class ChatbotEngine:
    def __init__(self):
        self.persona = """You are CogniMentor AI, an expert, friendly, and motivating AI tutor. 
        Your goal is to help students learn effectively. 
        Keep answers concise yet informative. 
        Use formatting like <b>bold</b> and lists to make content readable.
        Always be encouraging."""
        self.model_name = "gemini-3-flash-preview"
        self.client_configured = False
        
    def _configure_genai(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return False
            
        if not self.client_configured:
            try:
                genai.configure(api_key=api_key)
                self.client_configured = True
            except Exception as e:
                print(f"GenAI Config Error: {e}")
                return False
        return True

    def process_message(self, message, user_context):
        """
        Main entry point. Uses Gemini 3 Flash Preview to generate response.
        """
        if not self._configure_genai():
             return "I'm having trouble connecting to my brain (API Key missing). Please check settings."

        try:
            # Construct Prompt
            context_str = f"User Name: {user_context.get('name', 'Student')}. "
            if user_context.get('subject'):
                context_str += f"Current Subject: {user_context.get('subject')}. "
            if user_context.get('topic'):
                context_str += f"Current Topic: {user_context.get('topic')}. "
            
            # Using system_instruction for the persona
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=self.persona
            )
            
            chat_context = f"Context: {context_str}\n\nUser Message: {message}"
            
            response = model.generate_content(chat_context)
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            print(f"Chatbot AI Error: {error_msg}")
            
            if "429" in error_msg:
                 return "I'm a bit overwhelmed right now (Usage Limit). Please give me a minute to rest!"
            
            return f"I apologize, but I'm having trouble processing that right now. Error: {str(e)}"

chatbot_engine = ChatbotEngine()
