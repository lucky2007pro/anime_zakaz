from django.contrib.sessions.models import Session
from .models import ActiveSession, VipUser

class DeviceLimitMiddleware:
    """
    Limits the number of active sessions (devices) a user can have
    based on their subscription tier: Basic=1, Premium=3, VIP=5.
    Older sessions are dropped if the limit is exceeded.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            session_key = request.session.session_key
            if not session_key:
                request.session.save()
                session_key = request.session.session_key

            # Get user tier limit
            user = request.user
            # Admin users can have parallel sessions freely to avoid lockouts
            if not (user.is_superuser or user.is_staff or user.is_admin_user):
                vip_data, _ = VipUser.objects.get_or_create(user=user)
                tier = vip_data.get_tier()
                
                limit = 1
                if tier == 'premium':
                    limit = 3
                elif tier == 'vip':
                    limit = 5

                # Track current session
                ActiveSession.objects.get_or_create(user=user, session_key=session_key)

                # Get all tracked sessions for user, ordered by oldest first
                active_sessions = ActiveSession.objects.filter(user=user).order_by('created_at')

                if active_sessions.count() > limit:
                    # Remove the oldest ones
                    to_remove = active_sessions.count() - limit
                    sessions_to_delete = active_sessions[:to_remove]
                    
                    for session_record in sessions_to_delete:
                        # delete from Django sessions so the device logs out
                        Session.objects.filter(session_key=session_record.session_key).delete()
                        session_record.delete()
        
        response = self.get_response(request)
        return response

