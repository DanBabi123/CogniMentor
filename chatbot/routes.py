from flask import request, jsonify, render_template
from flask_login import current_user, login_required
from . import chatbot
from ai_engine.chatbot import chatbot_engine

@chatbot.route('/ask', methods=['POST'])
@login_required
def ask():
    from services.analytics_service import AnalyticsService
    data = request.json
    message = data.get('message')
    
    # Deep Context Gathering
    analytics = AnalyticsService.get_deep_analytics(current_user.id)
    
    # Synthesize persona-relevant context
    weak_subjects = [s['name'] for s in analytics.get('subject_performance', []) if s.get('is_weak')]
    recent_scores = [f"{a.topic.title if a.topic else 'Quiz'}: {int(a.score/a.max_score*100)}%" for a in analytics.get('attempts', [])[:3]]
    
    user_context = {
        'name': current_user.name,
        'subject': data.get('subject'),
        'topic': data.get('topic'),
        'accuracy': f"{analytics.get('accuracy_rate')}%",
        'focus_score': analytics.get('focus_score'),
        'weak_areas': ", ".join(weak_subjects) if weak_subjects else "None identified yet",
        'recent_history': " | ".join(recent_scores) if recent_scores else "No recent activity",
        'goal': current_user.selected_goal or "General Learning"
    }
    
    response = chatbot_engine.process_message(message, user_context)
    return jsonify({'response': response})

@chatbot.route('/chat')
@login_required
def chat_ui():
    from services.analytics_service import AnalyticsService
    analytics = AnalyticsService.get_deep_analytics(current_user.id)
    return render_template('chatbot/index.html', analytics=analytics)
