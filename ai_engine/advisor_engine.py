from google import genai
import os
import json

class AdvisorEngine:
    def __init__(self):
        self.client = False
        
    def _configure_genai(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return False
        if not self.client:
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                print(f"GenAI Client Init Error: {e}")
                return False
        return True

    def generate_roadmap(self, subject, level, goal, time, user_name):
        """
        Generates a structured learning roadmap based on user inputs using Gemini.
        """
        if not self._configure_genai():
             return self._fallback_roadmap(subject, level, goal, time, user_name, "API Key Missing")

        try:
            prompt = f"""
            Act as an expert learning advisor. Create a learning roadmap for {user_name}.
            Subject: {subject}
            Current Level: {level}
            Goal: {goal}
            Time Commitment: {time}/day
            
            Output a JSON object with this EXACT structure:
            {{
                "intro": "<h3>...html greeting...</h3><p>...html explanation...</p>",
                "weeks": [
                    {{
                        "title": "Week 1: [Focus Area]",
                        "desc": "[Description]",
                        "tasks": ["Task 1", "Task 2", "Task 3", "Mini-Project"]
                    }}
                ]
            }}
            
            Generate 4-6 weeks content. Use HTML tags in 'intro' for rich text.
            Make it motivating and specific to the goal.
            """
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash', 
                config={'response_mime_type': 'application/json'},
                contents=prompt
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Advisor AI Error: {error_msg}")
            if "429" in error_msg:
                return self._fallback_roadmap(subject, level, goal, time, user_name, "Usage Limit Reached")
            return self._fallback_roadmap(subject, level, goal, time, user_name, "AI Unavailable")

    def _fallback_roadmap(self, subject, level, goal, time, user_name, reason):
        # ... (Existing Mock Logic as Fallback) ...
        intro = f"""
        <h3>Hello {user_name} (Offline Mode)</h3>
        <p>I couldn't contact the AI brain ({reason}), but here is a standard path for <strong>{subject}</strong>.</p>
        """
        
        weeks = [
            {
                "title": "Week 1: Fundamentals",
                "desc": f"Start with the basics of {subject}.",
                "tasks": ["Setup Environment", "Core Concepts", "First Program"]
            },
            {
                "title": "Week 2: Advanced Topics",
                "desc": "Move to intermediate concepts.",
                "tasks": ["Data Structures", "Algorithms", "Mini Project"]
            }
        ]
        
        return {"intro": intro, "weeks": weeks}

advisor_engine = AdvisorEngine()
