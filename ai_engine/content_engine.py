# import google.generativeai as genai
# from huggingface_hub import InferenceClient
# import os
# import json
# import random
# import time
# import re

# class AIContentGenerator:
#     """
#     Generative AI Engine for CogniMentor using Official SDKs:
#     - Content: Gemini 1.5 Flash (google-generativeai)
#     - Quiz: Flan-T5 Base (huggingface_hub)
#     - Lesson: Zephyr 3B (huggingface_hub)
#     """
#     def __init__(self):
#         self.hf_client = None
#         self.genai_client = None
        
#         # Models
#         self.model_content = "gemini-flash-latest"
#         self.model_quiz = "google/flan-t5-base"
#         self.model_lesson = "stabilityai/stablelm-zephyr-3b"
        
#         self.gemini_configured = False

#     def _configure_clients(self):
#         """Configures both Google and HF clients"""
#         self.last_error = None  # Reset error
        
#         # Configure HF
#         hf_key = os.getenv('HUGGINGFACE_API_KEY')
#         if hf_key and not self.hf_client:
#             try:
#                 self.hf_client = InferenceClient(token=hf_key)
#             except Exception as e:
#                 print(f"HF Client Init Error: {e}")
#                 self.last_error = f"HF Error: {e}"

#         # Configure GenAI
#         genai_key = os.getenv('GEMINI_API_KEY')
#         if not genai_key:
#             self.last_error = "Missing GEMINI_API_KEY"
#         if genai_key and not self.gemini_configured:
#             try:
#                 genai.configure(api_key=genai_key) #type: ignore
#                 self.gemini_configured = True
#             except Exception as e:
#                 print(f"GenAI Config Error: {e}")
#                 self.last_error = f"GenAI Config Error: {e}"
        
#         return self.hf_client and self.gemini_configured

#     def generate_content(self, topic_title, mode='beginner'):
#         """
#         Generates content using Google Gemini 1.5 Flash.
#         """
#         self._configure_clients()
#         # Ensure fallback if Gemini isn't configured, but prioritize it
#         if not self.gemini_configured:
#             # Try one last time to init just in case env vars loaded late
#             self._configure_clients()
#             if not self.gemini_configured:
#                 # DEBUG: Use the error message
#                 error_msg = getattr(self, 'last_error', 'Unknown Error')
#                 return self._rule_based_generation(topic_title, mode, error_info=error_msg)

#         try:
#             prompts = {
#                 'beginner': f"Explain '{topic_title}' to a complete beginner. Use simple language, metaphors, and HTML formatting (<h3>, <p>, <ul>). Keep it under 200 words.",
#                 'concept': f"Deep dive into the technical concept of '{topic_title}'. Explain the 'How' and 'Why'. Use HTML formatting. Keep it under 250 words.",
#                 'analogy': f"Give a creative real-world analogy for '{topic_title}'. Format it nicely with HTML.",
#                 'visual': f"Describe a visual mental model or write pseudo-code to explain '{topic_title}'. Use HTML and <pre><code> for code.",
#                 'mistakes': f"What are common mistakes beginners make when learning '{topic_title}'? List them using HTML bullets."
#             }
            
#             user_prompt = prompts.get(mode, f"Explain {topic_title}")
            
#             model = genai.GenerativeModel( #type: ignore
#                 self.model_content,
#                 system_instruction="You are an expert technical educator. Output only clean HTML."
#             )
            
#             response = model.generate_content(user_prompt)
#             return response.text
            
#         except Exception as e:
#             print(f"GenAI Error (Content): {e}")
#             return self._rule_based_generation(topic_title, mode, error_info=str(e))

#     def _rule_based_generation(self, topic, mode, error_info=None):
#         """Fallback procedural generation"""
#         debug_msg = f" <br><small style='color:red'>Error: {error_info}</small>" if error_info else ""
#         return f"<p>AI Service Unavailable. Loaded static content for {topic} ({mode}).{debug_msg}</p>"

#     def generate_quiz(self, topic, difficulty_distribution=None):
#         """
#         Generates a quiz using Gemini 1.5 Flash in strict JSON mode.
#         """
#         self._configure_clients()
        
#         # Fallback if Gemini not configured
#         if not self.gemini_configured:
#             return self._fallback_quiz(topic)

#         # Distribute based on simplified 'Easy', 'Medium', 'Hard' if distribution provided
#         # Or simple 'adaptive' prompt if not. The user prompt uses score to decide difficulty.
#         # But here we might be calling it directly. Let's assume 'Medium' if usage is generic.
        
#         max_retries = 5
#         retry_delay = 5 # Initial delay for standard 429s

#         for attempt in range(max_retries):
#             try:
#                 prompt = f"""
#                 You are an expert quiz generator for {topic}.
#                 Generate 5 multiple-choice questions strictly focused on the topic: "{topic}". This is an adaptive re-attempt, so you MUST generate completely unique, non-standard, fresh questions we haven't seen before.
#                 System Entropy Seed: {random.randint(1, 999999)}
                
#                 Format (JSON Array):
#                 [
#                     {{
#                     "id": 1,
#                     "question": "...",
#                     "options": ["A", "B", "C", "D"],
#                     "correct": 0,
#                     "difficulty": "Medium",
#                     "explanation": "..."
#                     }}
#                 ]
                
#                 Rules:
#                 - 4 Options per question.
#                 - Correct index 0-3.
#                 - Include short explanation.
#                 - Difficulty mix: Follow logical progression (Easy -> Hard).
#                 """
                
#                 model = genai.GenerativeModel("gemini-1.5-flash") #type: ignore
                
#                 # Legacy robust generation prepending system context
#                 full_prompt = "Output valid JSON array of 5 questions.\n" + prompt
#                 response = model.generate_content(full_prompt)
#                 text = response.text
#                 # Robust JSON array extraction
#                 json_match = re.search(r'\[.*\]', text, re.DOTALL)
#                 if json_match:
#                     text = json_match.group(0)
#                 return json.loads(text.strip())

#             except Exception as e:
#                 error_msg = str(e)
#                 # Check for 429 specifically
#                 if ("429" in error_msg or "ResourceExhausted" in error_msg) and attempt < max_retries - 1:
#                     print(f"Quota exceeded (429). Retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
#                     time.sleep(retry_delay)
#                     retry_delay = min(retry_delay * 2, 60) # Cap at 60s
#                     continue
                
#                 print(f"GenAI Quiz Error: {e}")
#                 return self._fallback_quiz(topic)

#     def _fallback_quiz(self, topic_title):
#         """Return 5 static questions as fail-safe"""
#         # Clean up the contextual topic string to just the title for the fallback display
#         display_topic = topic_title
#         if "Topic/Module: " in topic_title:
#             display_topic = topic_title.split("Topic/Module: ")[1].strip()
            
#         base_questions = [
#             ("Core Concept", "What is the primary function of {}?", ["Optimization", "Execution", "Storage", "Processing"], 3, "Easy"),
#             ("Application", "When should you use {}?", ["Never", "Always", "Specific cases", "Randomly"], 2, "Easy"),
#             ("Syntax", "Which syntax is correct for {}?", ["Option A", "Option B", "Option C", "Option D"], 0, "Medium"),
#             ("Debugging", "How do you debug {}?", ["Logs", "Guessing", "Ignoring", "Reboot"], 0, "Medium"),
#             ("Performance", "Does {} affect performance?", ["Yes", "No", "Maybe", "Only on Tuesday"], 0, "Medium")
#         ]
        
#         quiz = []
#         for i, (cat, q_structure, opts, corr, diff) in enumerate(base_questions, 1):
#             quiz.append({
#                 "id": i,
#                 "question": q_structure.format(display_topic),
#                 "options": opts,
#                 "correct": corr,
#                 "difficulty": diff
#             })
#         return quiz

#     def generate_feedback(self, score, max_score, topic_title):
#         percentage = (score / max_score) * 100
#         if percentage >= 100:
#             return f"Perfect! You have mastered {topic_title}. You are ready for advanced concepts."
#         elif percentage >= 60:
#             return f"Good job! You understand the basics of {topic_title}."
#         else:
#             return f"Don't worry. {topic_title} is tricky. I recommend reviewing the material."

#     def generate_lesson_module(self, subject, topic, user_level='beginner', previous_score=0):
#         """
#         Generates a complete lesson module using Google Gemini (via official SDK).
#         Follows the strict 'W3Schools + Adaptive AI' system prompt.
#         Includes robust retry logic for 429 Quota errors.
#         """
#         self._configure_clients()
        
#         # Fallback if Gemini not configured
#         if not self.gemini_configured:
#             return self._fallback_lesson(subject, topic)

#         max_retries = 5
#         retry_delay = 5 # Initial delay for standard 429s

#         for attempt in range(max_retries):
#             try:
#                 # System prompt and user message construction...
#                 # (Same logic as before)
#                 full_system_prompt = f"""
#                 You are COGNIMENTOR, an expert technical educator. 
#                 Your goal is to generate content EXACTLY in the style of W3Schools and JavaTpoint.
#                 ... (Full prompt logic preserved) ...
#                 """
                
#                 # I'll use a slightly more compact representation for the tool call
#                 # but I must ensure the content matches.
                
#                 # RE-INSERTING FULL PROMPT FOR SAFETY
#                 full_system_prompt = f"""
#                 You are COGNIMENTOR, an expert technical educator. 
#                 Your goal is to generate content EXACTLY in the style of W3Schools and JavaTpoint.
                
#                 Key Style Rules (W3Schools & JavaTpoint style):
#                 - Be concise, simple, and direct. NO walls of text.
#                 - Use short sentences and simple vocabulary.
#                 - Provide LOTS of simple, clear code examples.
#                 - Focus on practical usage rather than deep academic theory.

#                 ==================================================
#                 CONTENT STRUCTURE (STRICT)
#                 ==================================================
#                 For the subject "{subject}" and topic "{topic}":

#                 1. **Introduction**
#                 - 1-2 very short paragraphs defining what it is.
#                 - Bullet points on why to use it.

#                 2. **Syntax / Basic Example (Crucial)**
#                 - Show the most basic copy-pasteable example immediately.
#                 - Use <pre><code> for the example.

#                 3. **Detailed Examples**
#                 - Provide 2-3 practical examples.
#                 - For each example, briefly explain what the code does step-by-step.
#                 - Use HTML tables if comparing things or listing properties.

#                 4. **Important Notes / Rules**
#                 - Short bullet points of rules to remember. Use <div class="note">.

#                 ==================================================
#                 FORMATTING RULES
#                 ==================================================
#                 - Use <h2> and <h3> for headers.
#                 - Use <div class="note"> for key notes or tips.
#                 - Use <div class="warning"> for pitfalls.
#                 - Use <pre><code> for all code blocks.
#                 - Keep the HTML clean and readable. Do NOT use inline styles like "color: white".


#                 ==================================================
#                 QUIZ GENERATION RULES (AUTO & RANDOM)
#                 ==================================================
#                 1. Decide difficulty automatically (User Level: {user_level}, Previous Score: {previous_score}).
#                 2. Generate 5 MULTIPLE-CHOICE questions strictly about the subject "{subject}" and topic "{topic}".
#                 3. Each question MUST include: Question, 4 options, Correct Answer, Explanation.

#                 ==================================================
#                 OUTPUT FORMAT (STRICT JSON ONLY)
#                 ==================================================
#                 {{
#                 "subject": "{subject}",
#                 "topic": "{topic}",
#                 "topic_content": "<html>FULL LESSON CONTENT...</html>",
#                 "quiz": [
#                     {{
#                     "id": 1,
#                     "question": "...",
#                     "options": ["...", "...", "...", "..."],
#                     "correct": 0,
#                     "difficulty": "Easy",
#                     "explanation": "..."
#                     }}
#                 ],
#                 "next_action": {{
#                     "unlock_next_topic": true | false,
#                     "recommended_level": "easy | medium | hard"
#                 }}
#                 }}
                
#                 IMPORTANT: Return ONLY valid JSON. No markdown formatting (```json).
#                 """

#                 user_msg = f"Generate lesson for: {subject} - {topic} (Level: {user_level}, Score: {previous_score})"
                
#                 model = genai.GenerativeModel(
#                     self.model_content,
#                     system_instruction=full_system_prompt
#                 )
                
#                 response = model.generate_content(user_msg)
#                 text = response.text
                
#                 # Robust JSON extraction
#                 json_match = re.search(r'\{.*\}', text, re.DOTALL)
#                 if json_match:
#                     text = json_match.group(0)
                
#                 return json.loads(text.strip())

#             except Exception as e:
#                 error_msg = str(e)
#                 # Check for 429 specifically
#                 if ("429" in error_msg or "ResourceExhausted" in error_msg) and attempt < max_retries - 1:
#                     # Longer wait for heavy quota exhaustion
#                     print(f"Quota exceeded (429). Retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
#                     time.sleep(retry_delay)
#                     retry_delay = min(retry_delay * 2, 60) # Cap at 60s
#                     continue
                
#                 print(f"GenAI Error (Lesson): {e}")
#                 return self._fallback_lesson(subject, topic)


#     def _fallback_lesson(self, subject, topic):
#         """Fallback for lesson generation"""
#         return {
#             "subject": subject,
#             "topic": topic,
#             "topic_content": f"<h3>{topic}</h3><p>Content temporarily unavailable. Please try again later.</p>",
#             "quiz": [],
#             "next_action": {
#                 "unlock_next_topic": False,
#                 "recommended_level": "easy"
#             }
#         }

#     def generate_custom_roadmap(self, user_goal):
#         """
#         Generates a 5-module fully personalized syllabus roadmap based on the user's specific goal.
#         """
#         self._configure_clients()
        
#         if not self.gemini_configured:
#             return [{"title": "Introduction to Concept", "difficulty": "Beginner"},
#                     {"title": "Core Syntax and Setup", "difficulty": "Beginner"},
#                     {"title": "Intermediate Application", "difficulty": "Medium"},
#                     {"title": "Advanced Logic", "difficulty": "Hard"},
#                     {"title": "Capstone Integration", "difficulty": "Hard"}]

#         try:
#             prompt = f"""
#             You are an expert curriculum architect.
#             The user has requested to learn: "{user_goal}".
            
#             Generate a highly structured, logical 5-module learning roadmap for them.
            
#             Format (Strict JSON Array):
#             [
#                 {{
#                     "title": "Module 1: ...",
#                     "difficulty": "Beginner"
#                 }},
#                 {{
#                     "title": "Module 2: ...",
#                     "difficulty": "Beginner"
#                 }},
#                 {{
#                     "title": "Module 3: ...",
#                     "difficulty": "Medium"
#                 }},
#                 {{
#                     "title": "Module 4: ...",
#                     "difficulty": "Hard"
#                 }},
#                 {{
#                     "title": "Module 5: ...",
#                     "difficulty": "Hard"
#                 }}
#             ]
            
#             IMPORTANT: Return ONLY the raw JSON array. Do not include markdown formatting like ```json.
#             """
            
#             model = genai.GenerativeModel(self.model_content) #type: ignore
#             response = model.generate_content(prompt)
            
#             text = response.text
#             # Robust JSON array extraction
#             json_match = re.search(r'\[.*\]', text, re.DOTALL)
#             if json_match:
#                 text = json_match.group(0)
                
#             return json.loads(text.strip())
            
#         except Exception as e:
#             print(f"GenAI Roadmap Error: {e}")
#             return [{"title": f"Intro to {user_goal}", "difficulty": "Beginner"},
#                     {"title": "Core Concepts", "difficulty": "Beginner"},
#                     {"title": "Practical Application", "difficulty": "Medium"},
#                     {"title": "Advanced Topics", "difficulty": "Hard"},
#                     {"title": "Final Integration", "difficulty": "Hard"}]

# ai_engine = AIContentGenerator()

import google.generativeai as genai
from huggingface_hub import InferenceClient
import os
import json
import random
import time
import re

class AIContentGenerator:
    """
    Generative AI Engine for CogniMentor using Official SDKs:
    - Content: Gemini 1.5 Flash (google-generativeai)
    - Quiz: Flan-T5 Base (huggingface_hub)
    - Lesson: Zephyr 3B (huggingface_hub)
    """
    def __init__(self):
        self.hf_client = None
        self.genai_client = None
        
        # Models
        self.model_content = "gemini-flash-latest"
        self.model_quiz = "google/flan-t5-base"
        self.model_lesson = "stabilityai/stablelm-zephyr-3b"
        
        self.gemini_configured = False

    def _configure_clients(self):
        """Configures both Google and HF clients"""
        self.last_error = None  # Reset error
        
        # Configure HF
        hf_key = os.getenv('HUGGINGFACE_API_KEY')
        if hf_key and not self.hf_client:
            try:
                self.hf_client = InferenceClient(token=hf_key)
            except Exception as e:
                print(f"HF Client Init Error: {e}")
                self.last_error = f"HF Error: {e}"

        # Configure GenAI
        genai_key = os.getenv('GEMINI_API_KEY')
        if not genai_key:
            self.last_error = "Missing GEMINI_API_KEY"
        if genai_key and not self.gemini_configured:
            try:
                genai.configure(api_key=genai_key) #type: ignore
                self.gemini_configured = True
            except Exception as e:
                print(f"GenAI Config Error: {e}")
                self.last_error = f"GenAI Config Error: {e}"
        
        return self.hf_client and self.gemini_configured

    def generate_content(self, topic_title, mode='beginner'):
        """
        Generates content using Google Gemini 1.5 Flash.
        """
        self._configure_clients()
        # Ensure fallback if Gemini isn't configured, but prioritize it
        if not self.gemini_configured:
            # Try one last time to init just in case env vars loaded late
            self._configure_clients()
            if not self.gemini_configured:
                # DEBUG: Use the error message
                error_msg = getattr(self, 'last_error', 'Unknown Error')
                return self._rule_based_generation(topic_title, mode, error_info=error_msg)

        try:
            prompts = {
                'beginner': f"Explain '{topic_title}' to a complete beginner. Use simple language, metaphors, and HTML formatting (<h3>, <p>, <ul>). Keep it under 200 words.",
                'concept': f"Deep dive into the technical concept of '{topic_title}'. Explain the 'How' and 'Why'. Use HTML formatting. Keep it under 250 words.",
                'analogy': f"Give a creative real-world analogy for '{topic_title}'. Format it nicely with HTML.",
                'visual': f"Describe a visual mental model or write pseudo-code to explain '{topic_title}'. Use HTML and <pre><code> for code.",
                'mistakes': f"What are common mistakes beginners make when learning '{topic_title}'? List them using HTML bullets."
            }
            
            user_prompt = prompts.get(mode, f"Explain {topic_title}")
            
            model = genai.GenerativeModel( #type: ignore
                self.model_content,
                system_instruction="You are an expert technical educator. Output only clean HTML."
            )
            
            response = model.generate_content(user_prompt)
            return response.text
            
        except Exception as e:
            print(f"GenAI Error (Content): {e}")
            return self._rule_based_generation(topic_title, mode, error_info=str(e))

    def _rule_based_generation(self, topic, mode, error_info=None):
        """Fallback procedural generation"""
        debug_msg = f" <br><small style='color:red'>Error: {error_info}</small>" if error_info else ""
        return f"<p>AI Service Unavailable. Loaded static content for {topic} ({mode}).{debug_msg}</p>"

    def generate_quiz(self, topic, difficulty_distribution=None, context=None):
        """
        Generates a quiz using Gemini 1.5 Flash in strict JSON mode.
        """
        self._configure_clients()
        
        # Fallback if Gemini not configured
        if not self.gemini_configured:
            return self._fallback_quiz(topic)

        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                base_prompt = f"""
                You are an expert strict quiz generator for the topic: {topic}.
                Generate 5 multiple-choice questions.
                """
                
                if context:
                    base_prompt += f"""
                CRITICAL INSTRUCTION: The student is at a specific learning level. You MUST ONLY test the student on concepts explicitly covered in the provided lesson content below! Do NOT ask advanced questions that are outside the scope of this exact content level. If the content is an "intro" level, the questions must be basic.
                
                --- PROVIDED LESSON CONTENT ---
                {context}
                -------------------------------
                """
                
                prompt = base_prompt + f"""
                This is an adaptive re-attempt, so you MUST generate completely unique, non-standard, fresh questions we haven't seen before.
                System Entropy Seed: {random.randint(1, 999999)}
                
                Format (JSON Array):
                [
                    {{
                    "id": 1,
                    "question": "...",
                    "options": ["A", "B", "C", "D"],
                    "correct": 0,
                    "difficulty": "Medium",
                    "explanation": "..."
                    }}
                ]
                
                Rules:
                - 4 Options per question.
                - Correct index 0-3.
                - Include short explanation.
                - Difficulty mix: Follow logical progression (Easy -> Hard).
                """
                
                model = genai.GenerativeModel(self.model_content) #type: ignore
                
                # Legacy robust generation prepending system context
                full_prompt = "Output valid JSON array of 5 questions.\n" + prompt
                response = model.generate_content(full_prompt)
                # Find JSON block using robust regex for arrays
                text = response.text
                import re
                json_match = re.search(r'\[.*\]', text, re.DOTALL)
                if json_match:
                    text = json_match.group(0)
                else:
                    # Fallback to backtick splits if regex fails
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0]
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0]
                        
                return json.loads(text.strip())
    
            except Exception as e:
                error_msg = str(e)
                # Check for 429 specifically
                if ("429" in error_msg or "ResourceExhausted" in error_msg) and attempt < max_retries - 1:
                    print(f"Quota exceeded (429). Retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 60) # Cap at 60s
                    continue
                
                print(f"GenAI Quiz Error: {e}")
                # Print exception traceback for debugging
                import traceback
                traceback.print_exc()
                return self._fallback_quiz(topic)

    def _fallback_quiz(self, topic_title):
        """Return 5 static questions as fail-safe"""
        base_questions = [
            ("Core Concept", "What is the primary function of {}?", ["Optimization", "Execution", "Storage", "Processing"], 3, "Easy"),
            ("Application", "When should you use {}?", ["Never", "Always", "Specific cases", "Randomly"], 2, "Easy"),
            ("Syntax", "Which syntax is correct for {}?", ["Option A", "Option B", "Option C", "Option D"], 0, "Medium"),
            ("Debugging", "How do you debug {}?", ["Logs", "Guessing", "Ignoring", "Reboot"], 0, "Medium"),
            ("Performance", "Does {} affect performance?", ["Yes", "No", "Maybe", "Only on Tuesday"], 0, "Medium")
        ]
        
        quiz = []
        for i, (cat, q_structure, opts, corr, diff) in enumerate(base_questions, 1):
            quiz.append({
                "id": i,
                "question": q_structure.format(topic_title),
                "options": opts,
                "correct": corr,
                "difficulty": diff
            })
        return quiz

    def generate_feedback(self, score, max_score, topic_title):
        percentage = (score / max_score) * 100
        if percentage >= 100:
            return f"Perfect! You have mastered {topic_title}. You are ready for advanced concepts."
        elif percentage >= 60:
            return f"Good job! You understand the basics of {topic_title}."
        else:
            return f"Don't worry. {topic_title} is tricky. I recommend reviewing the material."

    def generate_lesson_module(self, subject, topic, user_level='beginner', previous_score=0):
        """
        Generates a complete lesson module using Google Gemini (via official SDK).
        Follows the strict 'W3Schools + Adaptive AI' system prompt.
        Includes robust retry logic for 429 Quota errors.
        """
        self._configure_clients()
        
        # Fallback if Gemini not configured
        if not self.gemini_configured:
            return self._fallback_lesson(subject, topic)

        max_retries = 5
        retry_delay = 5 # Initial delay for standard 429s

        for attempt in range(max_retries):
            try:
                # System prompt and user message construction...
                # (Same logic as before)
                full_system_prompt = f"""
                You are COGNIMENTOR, an expert technical educator. 
                Your goal is to generate content EXACTLY in the style of W3Schools and JavaTpoint.
                ... (Full prompt logic preserved) ...
                """
                
                # I'll use a slightly more compact representation for the tool call
                # but I must ensure the content matches.
                
                # RE-INSERTING FULL PROMPT FOR SAFETY
                full_system_prompt = f"""
                You are COGNIMENTOR, an expert technical educator. 
                Your goal is to generate content EXACTLY in the style of W3Schools and JavaTpoint.
                
                Key Style Rules (W3Schools & JavaTpoint style):
                - Be concise, simple, and direct. NO walls of text.
                - Use short sentences and simple vocabulary.
                - Provide LOTS of simple, clear code examples.
                - Focus on practical usage rather than deep academic theory.

                ==================================================
                CONTENT STRUCTURE (STRICT)
                ==================================================
                For the subject "{subject}" and topic "{topic}":

                1. **Introduction**
                - 1-2 very short paragraphs defining what it is.
                - Bullet points on why to use it.

                2. **Syntax / Basic Example (Crucial)**
                - Show the most basic copy-pasteable example immediately.
                - Use <pre><code> for the example.

                3. **Detailed Examples**
                - Provide 2-3 practical examples.
                - For each example, briefly explain what the code does step-by-step.
                - Use HTML tables if comparing things or listing properties.

                4. **Important Notes / Rules**
                - Short bullet points of rules to remember. Use <div class="note">.

                ==================================================
                FORMATTING RULES
                ==================================================
                - Use <h2> and <h3> for headers.
                - Use <div class="note"> for key notes or tips.
                - Use <div class="warning"> for pitfalls.
                - Use <pre><code> for all code blocks.
                - Keep the HTML clean and readable. Do NOT use inline styles like "color: white".


                ==================================================
                QUIZ GENERATION RULES (AUTO & RANDOM)
                ==================================================
                1. Decide difficulty automatically (User Level: {user_level}, Previous Score: {previous_score}).
                2. Generate 5 MULTIPLE-CHOICE questions.
                3. Each question MUST include: Question, 4 options, Correct Answer, Explanation.

                ==================================================
                OUTPUT FORMAT (STRICT JSON ONLY)
                ==================================================
                {{
                "subject": "{subject}",
                "topic": "{topic}",
                "topic_content": "<html>FULL LESSON CONTENT...</html>",
                "quiz": [
                    {{
                    "id": 1,
                    "question": "...",
                    "options": ["...", "...", "...", "..."],
                    "correct": 0,
                    "difficulty": "Easy",
                    "explanation": "..."
                    }}
                ],
                "next_action": {{
                    "unlock_next_topic": true | false,
                    "recommended_level": "easy | medium | hard"
                }}
                }}
                
                IMPORTANT: Return ONLY valid JSON. No markdown formatting (```json).
                """

                user_msg = f"Generate lesson for: {subject} - {topic} (Level: {user_level}, Score: {previous_score})"
                
                model = genai.GenerativeModel(
                    self.model_content,
                    system_instruction=full_system_prompt
                )
                
                response = model.generate_content(user_msg)
                text = response.text
                
                # Robust JSON extraction
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    text = json_match.group(0)
                
                return json.loads(text.strip())

            except Exception as e:
                error_msg = str(e)
                # Check for 429 specifically
                if ("429" in error_msg or "ResourceExhausted" in error_msg) and attempt < max_retries - 1:
                    # Longer wait for heavy quota exhaustion
                    print(f"Quota exceeded (429). Retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 60) # Cap at 60s
                    continue
                
                print(f"GenAI Error (Lesson): {e}")
                return self._fallback_lesson(subject, topic)


    def _fallback_lesson(self, subject, topic):
        """Fallback for lesson generation"""
        return {
            "subject": subject,
            "topic": topic,
            "topic_content": f"<h3>{topic}</h3><p>Content temporarily unavailable. Please try again later.</p>",
            "quiz": [],
            "next_action": {
                "unlock_next_topic": False,
                "recommended_level": "easy"
            }
        }
    

    def generate_custom_roadmap(self, user_goal):
        """
        Generates a 5-module fully personalized syllabus roadmap based on the user's specific goal.
        """
        self._configure_clients()
        
        if not self.gemini_configured:
            return [{"title": "Introduction to Concept", "difficulty": "Beginner"},
                    {"title": "Core Syntax and Setup", "difficulty": "Beginner"},
                    {"title": "Intermediate Application", "difficulty": "Medium"},
                    {"title": "Advanced Logic", "difficulty": "Hard"},
                    {"title": "Capstone Integration", "difficulty": "Hard"}]

        try:
            prompt = f"""
            You are an expert curriculum architect.
            The user has requested to learn: "{user_goal}".
            
            Generate a highly structured, logical 5-module learning roadmap for them.
            
            Format (Strict JSON Array):
            [
                {{
                    "title": "Module 1: ...",
                    "difficulty": "Beginner"
                }},
                {{
                    "title": "Module 2: ...",
                    "difficulty": "Beginner"
                }},
                {{
                    "title": "Module 3: ...",
                    "difficulty": "Medium"
                }},
                {{
                    "title": "Module 4: ...",
                    "difficulty": "Hard"
                }},
                {{
                    "title": "Module 5: ...",
                    "difficulty": "Hard"
                }}
            ]
            
            IMPORTANT: Return ONLY the raw JSON array. Do not include markdown formatting like ```json.
            """
            
            model = genai.GenerativeModel(self.model_content) #type: ignore
            response = model.generate_content(prompt)
            
            text = response.text
            # Robust JSON array extraction
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                text = json_match.group(0)
                
            return json.loads(text.strip())
            
        except Exception as e:
            print(f"GenAI Roadmap Error: {e}")
            return [{"title": f"Intro to {user_goal}", "difficulty": "Beginner"},
                    {"title": "Core Concepts", "difficulty": "Beginner"},
                    {"title": "Practical Application", "difficulty": "Medium"},
                    {"title": "Advanced Topics", "difficulty": "Hard"},
                    {"title": "Final Integration", "difficulty": "Hard"}]


ai_engine = AIContentGenerator()