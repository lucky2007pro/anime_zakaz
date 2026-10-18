from django.contrib import messages
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone

from .models import ActiveSession, VipUser
from .admin_access import SECTION_LABELS, get_allowed_sections, section_for_url


# =====================================================
# 1. QURILMALAR LIMITI (sizniki, o'zgarmagan)
# =====================================================
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


# =====================================================
# 2. ADMIN PANEL: BO'LIMLARGA RUXSAT + HARAKATLAR TARIXI
# =====================================================
PANEL_PREFIX = '/control-panel/'
CHANGE_WORDS = ('delete', 'cancel', 'remove', 'tasdiqlash', 'subscription_action')


def _describe(name):
    if 'delete' in name:
        return "o'chirdi"
    if 'cancel' in name or 'remove' in name:
        return "bekor qildi"
    if 'tasdiqlash' in name:
        return "tasdiqladi"
    if name.endswith('_rad'):
        return "rad etdi"
    if 'subscription_action' in name:
        return "obuna so'rovini ko'rib chiqdi"
    return "saqlash tugmasini bosib o'zgartirish kiritdi"


class AdminPanelMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        is_panel = (
            request.path.startswith(PANEL_PREFIX)
            and user is not None
            and user.is_authenticated
        )
        if is_panel:
            request.allowed_sections = get_allowed_sections(user)

        response = self.get_response(request)

        if is_panel and not getattr(request, '_admin_denied', False):
            try:
                self._track(request, response)
            except Exception as e:
                print("AdminPanelMiddleware xatosi:", e)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        allowed = getattr(request, 'allowed_sections', None)
        if allowed is None:
            return None

        match = request.resolver_match
        section = section_for_url(match.url_name if match else None)
        if section and section not in allowed:
            request._admin_denied = True
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'error': "Bu bo'lim siz uchun yopiq."}, status=403)
            messages.error(request, "Bu bo'limga kirish huquqingiz yo'q.")
            return redirect('admin_dashboard')
        return None

    def _track(self, request, response):
        from .models import AdminProfile, AdminActionLog

        user = request.user
        if user.id == 1:
            return
        if not (user.is_staff or user.is_superuser or user.is_admin_user):
            return

        now = timezone.now()
        profile, _ = AdminProfile.objects.get_or_create(user=user)
        if not profile.last_seen or (now - profile.last_seen).total_seconds() > 60:
            AdminProfile.objects.filter(pk=profile.pk).update(last_seen=now)

        if response.status_code >= 400:
            return

        match = request.resolver_match
        name = match.url_name if match and match.url_name else ''
        is_change = (
            request.method == 'POST'
            or any(w in name for w in CHANGE_WORDS)
            or name.endswith('_rad')
        )
        if not is_change:
            return

        label = SECTION_LABELS.get(section_for_url(name), 'Boshqa')
        kw = match.kwargs if match else {}
        obj_id = kw.get('pk') or kw.get('user_id') or kw.get('movie_id')
        text = f"{label}: {_describe(name)}"
        if obj_id:
            text += f" (#{obj_id})"

        AdminActionLog.objects.create(
            user=user,
            action=text[:255],
            url_name=name[:100],
            method=request.method,
            path=request.path[:255],
        )
