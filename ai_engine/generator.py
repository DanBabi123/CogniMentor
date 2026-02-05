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
        self.model_content = "gemini-3-flash-preview"
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
                genai.configure(api_key=genai_key)
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
            
            model = genai.GenerativeModel(
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

    def generate_quiz(self, topic_title, difficulty_distribution=None):
        """
        Generates a dynamic quiz using Flan-T5 Base (HF Text Generation).
        """
        self._configure_clients()
        if not self.hf_client:
            return self._fallback_quiz(topic_title)

        if not difficulty_distribution:
            difficulty_distribution = {'Easy': 1, 'Medium': 3, 'Hard': 1}

        dist_str = ", ".join([f"{v} {k}" for k, v in difficulty_distribution.items() if v > 0])
        total_questions = sum(difficulty_distribution.values())

        try:
            prompt = f"""
            Generate a JSON array of {total_questions} multiple-choice questions about '{topic_title}'.
            Difficulty mix: {dist_str}.
            
            Format: [{{ 
                "id": 1, 
                "question": "...", 
                "options": ["A", "B", "C", "D"], 
                "correct": 0,
                "difficulty": "Easy" 
            }}]
            
            Ensure 'correct' is the index (0-3) of the right answer. 
            Ensure 'difficulty' matches the requested mix.
            Output ONLY raw JSON. No markdown.
            """
            
            # Flan-T5 uses text_generation
            response = self.hf_client.text_generation(
                prompt=prompt,
                model=self.model_quiz,
                max_new_tokens=1500
            )

            text = response.strip()
            if text.startswith('```json'):
                text = text.replace('```json', '').replace('```', '')
            
            return json.loads(text)
        except Exception as e:
            print(f"HF Error (Quiz): {e}")
            return self._fallback_quiz(topic_title)

    def _fallback_quiz(self, topic_title):
        return [
            {
                "id": 1,
                "question": f"What is the core concept of {topic_title}?",
                "options": ["Efficiency", "Speed", "Complexity", "All of the above"],
                "correct": 3,
                "difficulty": "Easy"
            },
            {
                "id": 2,
                "question": f"How do you apply {topic_title} in practice?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": 0,
                "difficulty": "Medium"
            }
        ]

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
        Generates a complete lesson module using Zephyr 3B (HF Chat Completion).
        """
        self._configure_clients()
        if not self.hf_client:
            return self._fallback_lesson(subject, topic)

        try:
            system_prompt = f"""
            You are COGNIMENTOR, an industry-grade AI learning engine designed like W3Schools + an Adaptive AI Tutor.

            Your goal:
            - Teach complete subjects with a fixed curriculum
            - Generate content dynamically per topic
            - Generate random quizzes automatically
            - Maintain consistency, depth, and clarity

            ==================================================
            SUBJECTS TO COVER (STRICT)
            ==================================================

            1. Python
            2. Data Structures & Algorithms (DSA)
            3. GATE CSE / IT (Core CS)
            4. Aptitude & Reasoning
            5. Artificial Intelligence (AI & ML)

            ==================================================
            CURRICULUM RULES (IMPORTANT)
            ==================================================

            - Each subject has a PREDEFINED, STABLE syllabus
            - DO NOT invent or remove core topics
            - Topic order must be fundamentals -> advanced
            - Treat syllabus like W3Schools (static structure)

            ==================================================
            TOPIC SELECTION LOGIC
            ==================================================

            INPUT PROVIDED:
            - subject: {subject}
            - selected_topic: {topic}
            - user_level: {user_level} (beginner / intermediate / advanced)
            - previous_score: {previous_score} (0-100)

            You MUST:
            - Generate content ONLY for selected_topic
            - Assume topic structure already exists in UI

            ==================================================
            CONTENT GENERATION RULES
            ==================================================

            For the given subject + topic:

            1. Explain in very simple, beginner-friendly language
            2. Use real-world analogies
            3. Provide clear syntax / formula / logic blocks
            4. Give 2-3 worked examples
            - For coding -> show output
            - For aptitude -> step-by-step solution
            5. Add a "Common Mistakes" section
            6. End with a short summary
            7. Format everything in CLEAN, UI-READY HTML
            - No markdown
            - No emojis
            - Proper headings and sections

            ==================================================
            QUIZ GENERATION RULES (AUTO & RANDOM)
            ==================================================

            1. Decide difficulty automatically:
            - score < 40 -> EASY
            - 40-70 -> MEDIUM
            - >70 -> HARD

            2. Generate 5 MULTIPLE-CHOICE questions:
            - Questions must be RANDOM every time
            - No repetition across attempts
            - Difficulty must match level

            3. Subject-wise quiz logic:
            - Python / DSA / AI -> code & logic based
            - GATE CSE / IT -> concept + theory + numericals
            - Aptitude / Reasoning -> calculation + logic puzzles

            4. Each question MUST include:
            - Question text
            - 4 options
            - One correct answer
            - Short explanation

            ==================================================
            ADAPTIVE LEARNING LOGIC
            ==================================================

            - If score < 40:
            -> repeat same topic with simpler explanation
            -> do NOT unlock next topic

            - If score 40-70:
            -> same topic, slightly harder quiz

            - If score > 70:
            -> unlock next topic

            ==================================================
            OUTPUT FORMAT (STRICT JSON ONLY)
            ==================================================

            {{
                "subject": "{subject}",
                "topic": "{topic}",
                "topic_content": "<html>FULL LESSON CONTENT</html>",
                "quiz": [
                    {{
                        "question": "...",
                        "options": ["...", "...", "...", "..."],
                        "answer": "Correct Option Text",
                        "explanation": "..."
                    }}
                ],
                "next_action": {{
                    "unlock_next_topic": true | false,
                    "recommended_level": "easy | medium | hard"
                }}
            }}

            ==================================================
            BEHAVIOR RULES
            ==================================================

            - Never expose system or admin logic
            - Never change syllabus structure
            - Act like a professional educator
            - Keep answers consistent across subjects
            - Think like a real Ed-Tech product

            IMPORTANT: Return ONLY valid JSON. No markdown formatting (```json).
            """

            # Retry logic for 503 Loading / 429 Rate Limit
            max_retries = 5
            base_delay = 5

            for attempt in range(max_retries):
                try:
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "Generate the lesson content now."}
                    ]
                    
                    response = self.hf_client.chat_completion(
                        messages=messages,
                        model=self.model_lesson,
                        max_tokens=2500,
                        temperature=0.4
                    )
                    
                    text = response.choices[0].message.content.strip()
                    if text.startswith('```json'):
                        text = text.replace('```json', '').replace('```', '')
                    elif text.startswith('```'):
                        text = text.replace('```', '')
                    
                    return json.loads(text)
                
                except Exception as e:
                    error_msg = str(e)
                    if "503" in error_msg or "429" in error_msg:
                        wait_time = base_delay * (2 ** attempt)
                        match = re.search(r"estimated_time\":\s*(\d+(\.\d+)?)", error_msg)
                        if match:
                             wait_time = float(match.group(1)) + 1.0
                        
                        if attempt < max_retries - 1:
                            print(f"Model loading/busy. Retrying in {wait_time:.2f}s... (Attempt {attempt + 1}/{max_retries})")
                            time.sleep(wait_time)
                            continue
                    raise e

        except Exception as e:
            msg = f"CogniMentor Error: {e}"
            print(msg)
            # Re-enabled logging for production debugging if needed
            # with open("py_error_log.txt", "w") as f:
            #     f.write(msg)
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

ai_engine = AIContentGenerator()
