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
        Strictly follows the 4-domain breakdown: GATE, Placements, Gov Exams, Real-world.
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
            2. Show how this subject helps in: GATE preparation, College placements, Government exams, and Real-world skills.
            3. For each domain: Explain why this subject is important and give a practical use case.
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
                        "explanation": "...",
                        "icon": "school"
                    }},
                    {{
                        "name": "College Placements",
                        "explanation": "...",
                        "icon": "business_center"
                    }},
                    {{
                        "name": "Government Exams",
                        "explanation": "...",
                        "icon": "account_balance"
                    }},
                    {{
                        "name": "Real-world Applications",
                        "explanation": "...",
                        "icon": "psychology"
                    }}
                ],
                "motivation": "...",
                "conclusion": "..."
            }}
            
            IMPORTANT: Return ONLY valid JSON.
            """
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            return self._extract_json(response.text)
            
        except Exception as e:
            print(f"Career Advisor AI Error: {e}")
            return self._fallback_career_insight(subject, str(e))

    def _extract_json(self, text):
        """Robustly extracts JSON from AI response."""
        try:
            # Try to find JSON in markdown code blocks
            json_match = re.search(r'```json\s*(\{.*\}|\[.*\])\s*```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to find JSON in general code blocks
            json_match = re.search(r'```\s*(\{.*\}|\[.*\])\s*```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Fallback to searching for start/end markers
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

    def _fallback_career_insight(self, subject, reason):
        return {
            "subject": subject,
            "strategic_focus": "Focus on the core concepts to maximize your career potential.",
            "domains": [
                {"name": "GATE Preparation", "explanation": f"{subject} is crucial for securing a high rank in GATE.", "icon": "school"},
                {"name": "College Placements", "explanation": f"Top companies test your knowledge of {subject} in initial rounds.", "icon": "business_center"},
                {"name": "Government Exams", "explanation": f"{subject} is a core component of many competitive exams.", "icon": "account_balance"},
                {"name": "Real-world Applications", "explanation": f"Mastering {subject} improves your problem-solving capabilities.", "icon": "psychology"}
            ],
            "motivation": "This skill is a universal key to many career paths.",
            "conclusion": "Keep learning and mastering this subject to stay ahead!"
        }

advisor_engine = AdvisorEngine()
