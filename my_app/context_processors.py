from django.db.models import Q
from .models import Notice


def notices_context(request):
    if request.user.is_authenticated:
        count = Notice.objects.filter(is_active=True).filter(
            Q(notice_type='admin', target_user__isnull=True) |
            Q(notice_type='reply', target_user=request.user)
        ).exclude(reads__user=request.user).count()
    else:
        count = 0
    return {'unread_notices_count': count}