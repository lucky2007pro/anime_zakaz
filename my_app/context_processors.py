from django.db.models import Q
from .models import Notice, ProfileAvatar, WatchHistory


def notices_context(request):
    if request.user.is_authenticated:
        count = Notice.objects.filter(is_active=True).filter(
            Q(notice_type='admin', target_user__isnull=True) |
            Q(notice_type='reply', target_user=request.user)
        ).exclude(reads__user=request.user).count()
    else:
        count = 0
    return {'unread_notices_count': count}


def premium_music_context(request):
    if request.user.is_authenticated:
        from .models import UserSettings
        s = UserSettings.objects.filter(user=request.user).select_related('premium_music').first()
        if s and s.premium_music_on and s.premium_music:
            return {
                'global_music_on': True,
                'global_music_url': s.premium_music.file.url,
                'global_music_volume': s.premium_music_volume,
            }
    return {'global_music_on': False, 'global_music_url': None, 'global_music_volume': 50}

def navbar_extra(request):
    """
    base.html (mobil navbar) uchun kerak bo'ladigan qo'shimcha ma'lumotlar:
    - avatars: admin yuklagan barcha profil rasmlari (avatar picker uchun)
    - last_watched_movies: foydalanuvchining oxirgi ko'rgan 2 ta animesi
    """
    if not request.user.is_authenticated:
        return {}

    avatars = ProfileAvatar.objects.all().order_by('-created_at')

    last_watched_movies = [
        w.movie for w in (
            WatchHistory.objects
            .filter(user=request.user)
            .select_related('movie')
            .order_by('-last_watched')[:2]
        )
    ]

    return {
        'avatars': avatars,
        'last_watched_movies': last_watched_movies,
    }
