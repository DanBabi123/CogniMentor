from flask import request, jsonify
from flask_login import current_user
from . import chatbot
from ai_engine.chatbot import chatbot_engine

@chatbot.route('/ask', methods=['POST'])
def ask():
    data = request.json
    message = data.get('message')
    
    # Context gathering
    user_context = {
        'name': current_user.name if current_user.is_authenticated else 'Guest',
        'subject': data.get('subject'),
        'topic': data.get('topic'),
        'score': data.get('score')
    }
    
    response = chatbot_engine.process_message(message, user_context)
    
    return jsonify({'response': response})
