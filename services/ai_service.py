from ai_engine.content_engine import ai_engine
from ai_engine.adaptive import adaptive_engine
from ai_engine.chatbot import chatbot_engine

class AIService:
    @staticmethod
    def generate_lesson(subject, topic, level, previous_score):
        return ai_engine.generate_lesson_module(subject, topic, level, previous_score)

    @staticmethod
    def generate_quiz(topic_title, distribution):
        return ai_engine.generate_quiz(topic_title, distribution)

    @staticmethod
    def get_chat_response(message, user_context):
        return chatbot_engine.process_message(message, user_context)

    @staticmethod
    def generate_custom_roadmap(user_goal):
        return ai_engine.generate_custom_roadmap(user_goal)
