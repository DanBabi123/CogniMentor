# import os
# import time
# import requests
# from dotenv import load_dotenv

# load_dotenv()

# class GeminiREST:
#     """Helper class to call Gemini API via REST instead of gRPC SDK."""
#     def __init__(self, api_key, model_name="gemini-1.5-flash", system_instruction=None):
#         self.api_key = api_key
#         self.model_name = model_name
#         self.system_instruction = system_instruction
#         # Handle model name aliases
#         if self.model_name == "gemini-flash-latest":
#             self.model_name = "gemini-1.5-flash"
#         self.base_url = f"https://generativelanguage.googleapis.com/v1beta3/models/{self.model_name}:generateText?key={self.api_key}"

#     def generate_content(self, prompt):
#         prompt_text = prompt
#         if self.system_instruction:
#             prompt_text = f"{self.system_instruction}\n\n{prompt}"

#         payload = {
#             "prompt": {"text": prompt_text},
#             "temperature": 0.7,
#             "maxOutputTokens": 700
#         }

#         response = requests.post(self.base_url, json=payload, timeout=30)
#         response.raise_for_status()

#         data = response.json()

#         # Mocking the SDK response object structure
#         class MockResponse:
#             def __init__(self, text):
#                 self.text = text

#         try:
#             text = data['candidates'][0]['output']
#             return MockResponse(text)
#         except (KeyError, IndexError):
#             raise Exception("Invalid response from Gemini API")

# class ChatbotEngine:
#     def __init__(self):
#         self.persona = """You are CogniMentor Executive AI, a high-performance learning coach. 
#         You don't just answer questions; you optimize the student's learning journey.
#         - Be expert, concise, and strategically encouraging.
#         - Use data-driven insights: 'I noticed your accuracy in Data Structures is a bit low, let's fix that.'
#         - Provide structural explanations using bullet points.
#         - When asked for suggestions, look at the 'Weak Areas' provided in context.
#         - If 'Focus Score' is high, praise their consistency."""
        
#         # Using Gemini 1.5 Flash (via stable alias): Often has more reliable free-tier allocation
#         self.model_name = "gemini-flash-latest"
#         self.api_key = os.getenv('GEMINI_API_KEY')
#         self.client_configured = False

#     def _configure_genai(self):
#         if not self.api_key: return False
#         if not self.client_configured:
#             # REST method doesn't need SDK config
#             self.client_configured = True
#         return True

#     def process_message(self, message, user_context, retries=2):
#         if not self._configure_genai():
#              return "I'm having trouble connecting to my brain (API Key missing)."

#         for attempt in range(retries + 1):
#             try:
#                 # Construct Rich Context
#                 perf_context = [
#                     f"User Profile: {user_context.get('name') or 'Student'}",
#                     f"Learning Goal: {user_context.get('goal') or 'General Learning'}",
#                     f"Overall Accuracy: {user_context.get('accuracy') or 'N/A'}",
#                     f"Focus Consistency: {user_context.get('focus_score') or 'N/A'}/100",
#                     f"Weak Topics: {user_context.get('weak_areas') or 'None'}",
#                     f"Recent Performance: {user_context.get('recent_history') or 'None'}"
#                 ]
                
#                 if user_context.get('subject'):
#                     perf_context.append(f"Current Subject: {user_context.get('subject')}")
                
#                 context_summary = "\n".join(perf_context)
                
#                 model = GeminiREST(
#                     self.api_key,
#                     self.model_name,
#                     system_instruction=self.persona
#                 )
                
#                 full_prompt = f"STUDENT PROFILE:\n{context_summary}\n\nSTUDENT QUESTION: {message}"
                
#                 response = model.generate_content(full_prompt)
                
#                 if response and response.text:
#                     return response.text
#                 return "I thought of something, but it was blocked by my filters. Let's try rephrasing?"
                
#             except Exception as e:
#                 error_str = str(e)
#                 if "429" in error_str and attempt < retries:
#                     # Exponential backoff: Sleep and try again
#                     time.sleep(2 ** attempt)
#                     continue
                
#                 if "429" in error_str:
#                     return "I'm working too hard! Let's take a 30-second breather? (Rate limit reached)"
#                 return f"I apologize, let's try that again. (Error: {error_str})"

# chatbot_engine = ChatbotEngine()

import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class ChatbotEngine:
    def __init__(self):
        self.persona = """You are CogniMentor Executive AI, a high-performance learning coach. 
        You don't just answer questions; you optimize the student's learning journey.
        - Be expert, concise, and strategically encouraging.
        - Use data-driven insights: 'I noticed your accuracy in Data Structures is a bit low, let's fix that.'
        - Provide structural explanations using bullet points.
        - When asked for suggestions, look at the 'Weak Areas' provided in context.
        - If 'Focus Score' is high, praise their consistency."""
        
        # Using Gemini 1.5 Flash (via stable alias): Often has more reliable free-tier allocation
        self.model_name = "gemini-flash-latest"
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.client_configured = False

    def _configure_genai(self):
        if not self.api_key: return False
        if not self.client_configured:
            try:
                genai.configure(api_key=self.api_key)
                self.client_configured = True
            except: return False
        return True

    def process_message(self, message, user_context, retries=2):
        if not self._configure_genai():
            return "I'm having trouble connecting to my brain (API Key missing)."

        for attempt in range(retries + 1):
            try:
                # Construct Rich Context
                perf_context = [
                    f"User Profile: {user_context.get('name') or 'Student'}",
                    f"Learning Goal: {user_context.get('goal') or 'General Learning'}",
                    f"Overall Accuracy: {user_context.get('accuracy') or 'N/A'}",
                    f"Focus Consistency: {user_context.get('focus_score') or 'N/A'}/100",
                    f"Weak Topics: {user_context.get('weak_areas') or 'None'}",
                    f"Recent Performance: {user_context.get('recent_history') or 'None'}"
                ]
                
                if user_context.get('subject'):
                    perf_context.append(f"Current Subject: {user_context.get('subject')}")
                
                context_summary = "\n".join(perf_context)
                
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=self.persona
                )
                
                full_prompt = f"STUDENT PROFILE:\n{context_summary}\n\nSTUDENT QUESTION: {message}"
                
                response = model.generate_content(full_prompt)
                
                if response and response.text:
                    return response.text
                return "I thought of something, but it was blocked by my filters. Let's try rephrasing?"
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str and attempt < retries:
                    # Exponential backoff: Sleep and try again
                    time.sleep(2 ** attempt)
                    continue
                
                if "429" in error_str:
                    return "I'm working too hard! Let's take a 30-second breather? (Rate limit reached)"
                return f"I apologize, let's try that again. (Error: {error_str})"

chatbot_engine = ChatbotEngine()