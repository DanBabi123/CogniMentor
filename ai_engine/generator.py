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
        self.model_content = "gemini-1.5-flash"
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

    def generate_quiz(self, topic, difficulty_distribution=None):
        """
        Generates a quiz using Gemini 1.5 Flash in strict JSON mode.
        """
        self._configure_clients()
        
        # Fallback if Gemini not configured
        if not self.gemini_configured:
            return self._fallback_quiz(topic)

        # Distribute based on simplified 'Easy', 'Medium', 'Hard' if distribution provided
        # Or simple 'adaptive' prompt if not. The user prompt uses score to decide difficulty.
        # But here we might be calling it directly. Let's assume 'Medium' if usage is generic.
        
        try:
            prompt = f"""
            You are an expert quiz generator for {topic}.
            Generate 10 multiple-choice questions.
            
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
            
            model = genai.GenerativeModel( #type: ignore
                self.model_content,
                system_instruction="Output valid JSON array of 10 questions.",
                generation_config={"response_mime_type": "application/json"}
            )
            
            response = model.generate_content(prompt)
            return json.loads(response.text)

        except Exception as e:
            print(f"GenAI Quiz Error: {e}")
            return self._fallback_quiz(topic)

    def _fallback_quiz(self, topic_title):
        """Return 10 static questions as fail-safe"""
        base_questions = [
            ("Core Concept", "What is the primary function of {}?", ["Optimization", "Execution", "Storage", "Processing"], 3, "Easy"),
            ("Application", "When should you use {}?", ["Never", "Always", "Specific cases", "Randomly"], 2, "Easy"),
            ("Syntax", "Which syntax is correct for {}?", ["Option A", "Option B", "Option C", "Option D"], 0, "Medium"),
            ("Debugging", "How do you debug {}?", ["Logs", "Guessing", "Ignoring", "Reboot"], 0, "Medium"),
            ("Performance", "Does {} affect performance?", ["Yes", "No", "Maybe", "Only on Tuesday"], 0, "Medium"),
            ("Security", "Is {} secure by default?", ["Yes", "No", "Depends on config", "Always"], 2, "Hard"),
            ("Advanced", "What is an advanced feature of {}?", ["Feature X", "Feature Y", "Feature Z", "None"], 0, "Hard"),
            ("History", "Who created {}?", ["Dev A", "Dev B", "Community", "Unknown"], 2, "Medium"),
            ("Comparison", "How does {} compare to alternatives?", ["Better", "Worse", "Different", "Same"], 2, "Hard"),
            ("Future", "What is the future of {}?", ["Growth", "Decline", "Stable", "Unknown"], 0, "Easy")
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
        """
        self._configure_clients()
        
        # Fallback if Gemini not configured
        if not self.gemini_configured:
            return self._fallback_lesson(subject, topic)

        try:
            system_prompt = f"""
            You are COGNIMENTOR, a world-class technical educator known for EXTREMELY DETAILED, DEEP-DIVE content (like a premium textbook or detailed documentation).

            Your goal:
            - Create comprehensive, long-form lessons (think 15-minute read time).
            - Go BEYOND basics -> explain "HOW it works under the hood".
            - Use a friendly but professional tone.

            ==================================================
            CONTENT STRUCTURE (STRICT)
            ==================================================
            For the subject "{subject}" and topic "{topic}":

            1. **Introduction & Real-World Context**
            - Define the concept clearly.
            - Explain WHY it exists and WHAT problem it solves.
            - Give a relatable real-world analogy (e.g., "Think of a Library...").

            2. **Deep Dive: The Mechanics (The "How")**
            - Don't just show syntax. Explain the internal logic.
            - If coding: Memory management, complexity, or interpreter steps.
            - If theory: proven theorems or historical context.
            - Use Diagrams (via ASCII/Mermaid if simple) or clear descriptors.

            3. **Step-by-Step Implementation / Solution**
            - Provide a COMPLETE code example or solved problem.
            - Comment EVERY line of code.
            - Show expected output.
            - "Walk through" the execution flow.

            4. **Advanced Edge Cases & Best Practices**
            - What happens if inputs are null? Large data?
            - How do pros use this in production?
            - Common "Gotchas" and how to debug them.

            5. **Interactive Challenge**
            - Pose a thought-provoking question to the student.
            - Provide a "hidden" answer (using <details><summary>Check Answer</summary>...).

            6. **Summary & Key Takeaways**
            - Bullet points of the most critical concepts.

            ==================================================
            FORMATTING RULES
            ==================================================
            - Use <h3>, <h4> for headers.
            - Use <div class="note"> for key notes.
            - Use <div class="warning"> for pitfalls.
            - Use <pre><code> for all code.
            - **LENGTH**: The content of 'topic_content' MUST be significant (at least 800 words). Do not be brief.

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

            user_msg = f"""
            Generate the lesson module for:
            - Subject: {subject}
            - Topic: {topic}
            - User Level: {user_level}
            - Previous Score: {previous_score}
            """
            
            model = genai.GenerativeModel( #type: ignore
                self.model_content,
                system_instruction=system_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            response = model.generate_content(user_msg)
            return json.loads(response.text)

        except Exception as e:
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

ai_engine = AIContentGenerator()
