# import requests
# import os
# import json
# import re

# class GeminiREST:
#     """Helper class to call Gemini API via REST instead of gRPC SDK."""
#     def __init__(self, api_key, model_name="gemini-flash-latest", system_instruction=None):
#         self.api_key = api_key
#         self.model_name = model_name
#         self.system_instruction = system_instruction
#         # Handle model name aliases
#         #if self.model_name == "gemini-flash-latest":
#         #   self.model_name = "gemini-1.5-flash"
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

# class AdvisorEngine:
#     def __init__(self):
#         self.client_configured = False
        
#     def _configure_genai(self):
#         api_key = os.getenv('GEMINI_API_KEY')
#         if not api_key:
#             return False
#         if not self.client_configured:
#             # REST method doesn't need SDK config
#             self.client_configured = True
#         return True

#     def get_career_insight(self, subject, selected_goal=None):
#         """
#         Explains how a subject is useful across multiple domains using the career advisor persona.
#         Strictly follows the 4-domain breakdown: GATE, Placements, Gov Exams, Real-world.
#         Adds a 'Strategic Goal Focus' if a user's goal is provided.
#         """
#         if not self._configure_genai():
#              return self._fallback_career_insight(subject, "API Key Missing")

#         goal_context = f"The user's current goal is: {selected_goal}." if selected_goal else ""

#         try:
#             prompt = f"""
#             Act as an AI career advisor for an EdTech platform called Cognimentor.
#             Your task is to explain how the selected subject is useful across multiple domains.
            
#             Subject: {subject}
#             {goal_context}
            
#             Instructions:
#             1. Analyze the subject and identify where it is applicable.
#             2. Show how this subject helps in: GATE preparation, College placements, Government exams, Real-world skills, and building Related Technical Skills.
#             3. For each domain: Explain why this subject is important and give a practical use case. Especially focus on how this subject is useful for learning other recommended skills.
#             4. Provide a 'Strategic Goal Focus': Explain how this subject specifically aligns with the user's focus on '{selected_goal}'.
#             5. Provide a motivational insight: Explain how mastering this one skill can open multiple career opportunities.
#             6. Keep the explanation simple, clear, and impactful.
            
#             Output a JSON object with this EXACT structure:
#             {{
#                 "subject": "{subject}",
#                 "strategic_focus": "Specific advice for their {selected_goal} goal...",
#                 "domains": [
#                     {{
#                         "name": "GATE Preparation",
#                         "content": "...",
#                         "icon": "school"
#                     }},
#                     {{
#                         "name": "College Placements",
#                         "content": "...",
#                         "icon": "business_center"
#                     }},
#                     {{
#                         "name": "Government Exams",
#                         "content": "...",
#                         "icon": "account_balance"
#                     }},
#                     {{
#                         "name": "Real-world Applications",
#                         "content": "...",
#                         "icon": "psychology"
#                     }},
#                     {{
#                         "name": "Related Technical Skills",
#                         "content": "Explain exactly how learning this subject makes it easier to learn other specific recommended skills...",
#                         "icon": "account_tree"
#                     }}
#                 ],
#                 "motivation": "...",
#                 "conclusion": "..."
#             }}
            
#             IMPORTANT: Return ONLY valid JSON.
#             """
            
#             model = GeminiREST(os.getenv('GEMINI_API_KEY'), 'gemini-flash-latest')
#             response = model.generate_content(prompt)
            
#             return self._extract_json(response.text)
            
#         except Exception as e:
#             print(f"Career Advisor AI Error: {e}")
#             return self._fallback_career_insight(subject, str(e))

#     def _extract_json(self, text):
#         """Robustly extracts JSON from AI response."""
#         try:
#             # Try to find JSON in markdown code blocks
#             json_match = re.search(r'```json\s*(\{.*\}|\[.*\])\s*```', text, re.DOTALL)
#             if json_match:
#                 return json.loads(json_match.group(1))
            
#             # Try to find JSON in general code blocks
#             json_match = re.search(r'```\s*(\{.*\}|\[.*\])\s*```', text, re.DOTALL)
#             if json_match:
#                 return json.loads(json_match.group(1))

#             # Fallback to searching for start/end markers
#             start_brace = text.find('{')
#             start_bracket = text.find('[')
            
#             if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
#                 end_brace = text.rfind('}')
#                 if end_brace != -1:
#                     return json.loads(text[start_brace:end_brace+1])
#             elif start_bracket != -1:
#                 end_bracket = text.rfind(']')
#                 if end_bracket != -1:
#                     return json.loads(text[start_bracket:end_bracket+1])
            
#             return json.loads(text.strip())
#         except Exception as e:
#             print(f"JSON Parsing Error: {e}")
#             raise e

#     def generate_roadmap(self, subject, level, goal, time, username):
#         if not self._configure_genai():
#              return self._fallback_roadmap(subject, level)

#         try:
#             prompt = f"""
#             Act as an AI career advisor. Create a personalized learning roadmap for {username}.
#             Subject: {subject}
#             Current Level: {level}
#             Goal: {goal}
#             Time Commitment: {time} per day
            
#             Output a JSON object with this EXACT structure:
#             {{
#                 "intro": "A short customized intro paragraph...",
#                 "weeks": [
#                     {{
#                         "title": "Week 1: Fundamentals",
#                         "desc": "Focus on basics",
#                         "tasks": ["Task 1", "Task 2"]
#                     }}
#                 ]
#             }}
#             Create up to 4 weeks. ONLY return valid JSON.
#             """
#             model = GeminiREST(os.getenv('GEMINI_API_KEY'), 'gemini-flash-latest')
#             response = model.generate_content(prompt)
#             return self._extract_json(response.text)
#         except Exception as e:
#             print(f"Roadmap AI Error: {e}")
#             return self._fallback_roadmap(subject, level)

#     def _fallback_roadmap(self, subject, level):
#         return {
#             "intro": f"Welcome to your {subject} roadmap starting at the {level} level. Due to high AI traffic, here is your essential guide.",
#             "weeks": [
#                 {
#                     "title": "Week 1: Getting Started",
#                     "desc": "Familiarize yourself with the core concepts.",
#                     "tasks": ["Read introduction materials", "Practice basic problems", "Review syllabus"]
#                 }
#             ]
#         }

#     def _fallback_career_insight(self, subject, reason):
#         return {
#             "subject": subject,
#             "strategic_focus": "Focus on the core concepts to maximize your career potential.",
#             "domains": [
#                 {"name": "GATE Preparation", "content": f"{subject} is crucial for securing a high rank in GATE.", "icon": "school"},
#                 {"name": "College Placements", "content": f"Top companies test your knowledge of {subject} in initial rounds.", "icon": "business_center"},
#                 {"name": "Government Exams", "content": f"{subject} is a core component of many competitive exams.", "icon": "account_balance"},
#                 {"name": "Real-world Applications", "content": f"Mastering {subject} improves your problem-solving capabilities.", "icon": "psychology"},
#                 {"name": "Related Technical Skills", "content": f"{subject} lays the foundation for mastering advanced tech stacks smoothly.", "icon": "account_tree"}
#             ],
#             "motivation": "This skill is a universal key to many career paths.",
#             "conclusion": "Keep learning and mastering this subject to stay ahead!"
#         }

# advisor_engine = AdvisorEngine()

import google.generativeai as genai
import os
import json
import re

class AdvisorEngine:
    def __init__(self):
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

    def get_career_insight(self, subject, selected_goal=None):
        """
        Explains how a subject is useful across multiple domains using the career advisor persona.
        Strictly follows the 5-domain breakdown: GATE, Placements, Gov Exams, Real-world, Related Technical Skills.
        Adds a 'Strategic Goal Focus' if a user's goal is provided.
        """
        if not self._configure_genai():
             return self._fallback_career_insight(subject, "API Key Missing")

        goal_context = f"The user's current goal is: {selected_goal}." if selected_goal else ""

        try:
            prompt = f"""
            Act as an AI career advisor for an EdTech platform called Cognimentor.
            Your task is to explain how the selected subject is useful across multiple domains.
            
            Subject: {subject}
            {goal_context}
            
            Instructions:
            1. Analyze the subject and identify where it is applicable.
            2. Show how this subject helps in: GATE preparation, College placements, Government exams, Real-world skills, and building Related Technical Skills.
            3. For each domain: Explain why this subject is important and give a practical use case. Especially focus on how this subject is useful for learning other recommended skills.
            4. Provide a 'Strategic Goal Focus': Explain how this subject specifically aligns with the user's focus on '{selected_goal}'.
            5. Provide a motivational insight: Explain how mastering this one skill can open multiple career opportunities.
            6. Keep the explanation simple, clear, and impactful.
            
            Output a JSON object with this EXACT structure:
            {{
                "subject": "{subject}",
                "strategic_focus": "Specific advice for their {selected_goal} goal...",
                "domains": [
                    {{
                        "name": "GATE Preparation",
                        "content": "...",
                        "icon": "school"
                    }},
                    {{
                        "name": "College Placements",
                        "content": "...",
                        "icon": "business_center"
                    }},
                    {{
                        "name": "Government Exams",
                        "content": "...",
                        "icon": "account_balance"
                    }},
                    {{
                        "name": "Real-world Applications",
                        "content": "...",
                        "icon": "psychology"
                    }},
                    {{
                        "name": "Related Technical Skills",
                        "content": "Explain exactly how learning this subject makes it easier to learn other specific recommended skills...",
                        "icon": "account_tree"
                    }}
                ],
                "motivation": "...",
                "conclusion": "..."
            }}
            
            IMPORTANT: Return ONLY valid JSON.
            """
            
            # Using the correct, working model
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt)
            
            return self._extract_json(response.text)
            
        except Exception as e:
            print(f"Career Advisor AI Error: {e}")
            return self._fallback_career_insight(subject, str(e))

    def generate_roadmap(self, subject, level, goal, time, username):
        """Merged from friend's code to generate a custom roadmap"""
        if not self._configure_genai():
             return self._fallback_roadmap(subject, level)

        try:
            prompt = f"""
            Act as an AI career advisor. Create a personalized learning roadmap for {username}.
            Subject: {subject}
            Current Level: {level}
            Goal: {goal}
            Time Commitment: {time} per day
            
            Output a JSON object with this EXACT structure:
            {{
                "intro": "A short customized intro paragraph...",
                "weeks": [
                    {{
                        "title": "Week 1: Fundamentals",
                        "desc": "Focus on basics",
                        "tasks": ["Task 1", "Task 2"]
                    }}
                ]
            }}
            Create up to 4 weeks. ONLY return valid JSON.
            """
            
            # Using the correct, working model
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt)
            return self._extract_json(response.text)
            
        except Exception as e:
            print(f"Roadmap AI Error: {e}")
            return self._fallback_roadmap(subject, level)

    def _extract_json(self, text):
        """Robustly extracts JSON from AI response."""
        try:
            json_match = re.search(r'```json\s*(\{.*\}|\[.*\])\s*```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            json_match = re.search(r'```\s*(\{.*\}|\[.*\])\s*```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            start_brace = text.find('{')
            start_bracket = text.find('[')
            
            if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
                end_brace = text.rfind('}')
                if end_brace != -1:
                    return json.loads(text[start_brace:end_brace+1])
            elif start_bracket != -1:
                end_bracket = text.rfind(']')
                if end_bracket != -1:
                    return json.loads(text[start_bracket:end_bracket+1])
            
            return json.loads(text.strip())
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
            raise e

    def _fallback_roadmap(self, subject, level):
        """Merged from friend's code"""
        return {
            "intro": f"Welcome to your {subject} roadmap starting at the {level} level. Due to high AI traffic, here is your essential guide.",
            "weeks": [
                {
                    "title": "Week 1: Getting Started",
                    "desc": "Familiarize yourself with the core concepts.",
                    "tasks": ["Read introduction materials", "Practice basic problems", "Review syllabus"]
                }
            ]
        }

    def _fallback_career_insight(self, subject, reason):
        """Merged from friend's code"""
        return {
            "subject": subject,
            "strategic_focus": "Focus on the core concepts to maximize your career potential.",
            "domains": [
                {"name": "GATE Preparation", "content": f"{subject} is crucial for securing a high rank in GATE.", "icon": "school"},
                {"name": "College Placements", "content": f"Top companies test your knowledge of {subject} in initial rounds.", "icon": "business_center"},
                {"name": "Government Exams", "content": f"{subject} is a core component of many competitive exams.", "icon": "account_balance"},
                {"name": "Real-world Applications", "content": f"Mastering {subject} improves your problem-solving capabilities.", "icon": "psychology"},
                {"name": "Related Technical Skills", "content": f"{subject} lays the foundation for mastering advanced tech stacks smoothly.", "icon": "account_tree"}
            ],
            "motivation": "This skill is a universal key to many career paths.",
            "conclusion": "Keep learning and mastering this subject to stay ahead!"
        }

advisor_engine = AdvisorEngine()