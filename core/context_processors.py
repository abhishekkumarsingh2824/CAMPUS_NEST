"""
CampusNest core context processor.
Injects the current session user into every template context.
"""
from db_utils import get_db
from bson import ObjectId


def user_context(request):
    """Add current user info to all template contexts."""
    context = {
        'session_user': None,
        'is_authenticated': False,
        'is_student': False,
        'is_owner': False,
        'is_admin': False,
    }
    user_id = request.session.get('user_id')
    if user_id:
        try:
            db = get_db()
            user = db.users.find_one({'_id': ObjectId(user_id)})
            if user:
                context['session_user'] = user
                context['is_authenticated'] = True
                context['is_student'] = user.get('role') == 'student'
                context['is_owner'] = user.get('role') == 'owner'
                context['is_admin'] = user.get('role') == 'admin'
        except Exception:
            pass
    return context
