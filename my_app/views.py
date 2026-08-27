from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localtime
from datetime import timedelta
from zoneinfo import ZoneInfo
from django.db.models import Max
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import F
from django.db import models
from django.db.models import Q
from django.urls import reverse
import re
from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.template.loader import render_to_string
import json
from pywebpush import webpush, WebPushException
from django.conf import settings



from .models import (
    CustomUser, VipUser, Category, Movie, SiteSettings, MP3, ChatMessage, SubscriptionReceipt, ProfileAvatar, AnimeNews, NewsLike,
    Story, StoryView, Reel, ReelLike, ReelComment, ReelShare,
    UserSettings,AnimeSchedule,AnimeSectionItem, Notice, NoticeRead,WatchHistory, FavoriteAnime,NoResultsMedia,
    AccountHistory, DebtRequest, BalanceTopupRequest, JackpotCode, JackpotCodeUse,UserBalance,PushSubscription,

)

User = get_user_model()
NEWS_PAGE_SIZE = 9

# =======================
# REGISTER
# =======================
def register(request):
    site_settings = SiteSettings.objects.last()
    context = {'site_settings': site_settings}

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Bu username allaqachon ishlatilgan")
            return redirect('register')

        if email and CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Bu email allaqachon ishlatilgan")
            return redirect('register')

        user = CustomUser(username=username, email=email)
        user.set_password(password)
        user.save()

        messages.success(request, "Akaunt yaratildi")
        return redirect('login')

    return render(request, 'register.html', context)


# =======================
# LOGIN
# =======================
def login(request):
    site_settings = SiteSettings.objects.last()
    context = {'site_settings': site_settings}

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            request.session['mp3_played'] = False
            request.session['show_welcome'] = True   # <-- shu qator qo'shildi
            return redirect('home')
        else:
            messages.error(request, "Login yoki parol noto‘g‘ri")
            return redirect('login')

    return render(request, 'login.html', context)

# =======================
# LOGOUT
# =======================
def logout_view(request):
    auth_logout(request)
    return redirect('login')


# =======================
# HOME
# =======================
def home(request):
    movies = Movie.objects.prefetch_related('episodes').annotate(
        last_episode=Max('episodes__created_at')
    ).order_by('-last_episode')

    hero_movies = list(
        Movie.objects.select_related('category').prefetch_related('episodes')
        .filter(is_home_featured=True)
        .order_by('home_featured_order', '-created_at')[:7]
    )

    recommended_movies = list(
        Movie.objects.select_related('category').prefetch_related('episodes')
        .order_by('-views_count', '-created_at')[:10]
    )

    categories = Category.objects.all()

    # ================= STORY =================
    stories = Story.objects.filter(
        is_active=True
    ).filter(
        models.Q(expires_at__gt=timezone.now()) | models.Q(expires_at__isnull=True)
    ).order_by('-created_at')

    seen_stories = set()
    if request.user.is_authenticated:
        seen_stories = set(
            StoryView.objects.filter(user=request.user)
            .values_list('story_id', flat=True)
        )

    # ================= MP3 =================
    mp3_to_play = None
    fav_ids = []

    # ================= WELCOME TOAST =================
    show_welcome = False

    if request.user.is_authenticated:
        from .models import FavoriteAnime

        fav_ids = list(
            FavoriteAnime.objects.filter(user=request.user)
            .values_list('movie_id', flat=True)
        )

        try:
            mp3_obj = MP3.objects.latest('created_at')
            mp3_file = mp3_obj.file.url
        except MP3.DoesNotExist:
            mp3_file = None

        mp3_to_play = mp3_file if not request.session.get('mp3_played', False) else None
        request.session['mp3_played'] = True

        show_welcome = request.session.get('show_welcome', False)
        request.session['show_welcome'] = False

    # ================= SCHEDULE =================
    schedule_list = list(AnimeSchedule.objects.filter(is_active=True))

    # ================= CONTEXT =================
    context = {
        'movies': movies,
        'hero_movies': hero_movies,
        'recommended_movies': recommended_movies,
        'categories': categories,

        # STORY
        'stories': stories,
        'seen_stories': seen_stories,

        # OTHER
        'mp3_file': mp3_to_play,
        'total_users': User.objects.count(),
        'user_id': request.user.id if request.user.is_authenticated else None,
        'fav_ids': fav_ids,
        'schedule_list': schedule_list,
        'show_welcome': show_welcome,
    }

    return render(request, 'home.html', context)


# =======================
# MOVIE DETAIL
# =======================
@login_required
def movie_detail(request, id):
    movie = get_object_or_404(
        Movie.objects.prefetch_related('episodes', 'frames'),
        id=id
    )

    if request.method == "POST":
        text = request.POST.get("comment", "").strip()
        parent_id = request.POST.get("parent_id")
        if text:
            from .models import MovieComment, Notice
            parent_comment = None
            if parent_id:
                parent_comment = MovieComment.objects.filter(id=parent_id, movie=movie).first()
                # Agar javob berilayotgan izoh o'zi ham javob bo'lsa (2-daraja),
                # uni eng tepadagi asosiy izohga "yassilaymiz" — shu orqali
                # barcha javoblar bitta ro'yxatda va bitta hisoblagichda chiqadi.
                if parent_comment and parent_comment.parent_id:
                    parent_comment = parent_comment.parent

            new_comment = MovieComment.objects.create(
                movie=movie, user=request.user, text=text, parent=parent_comment
            )

            if parent_comment and parent_comment.user != request.user:
                Notice.objects.create(
                    notice_type='reply',
                    created_by=request.user,
                    target_user=parent_comment.user,
                    title=f"{request.user.username} sizning izohingizga javob berdi",
                    message=text,
                    related_movie_comment=new_comment,
                )
        return redirect('movie_detail', id=movie.id)

    episodes = movie.episodes.all().order_by('episode_number')

    # Increment views remotely safely
    Movie.objects.filter(id=id).update(views_count=F('views_count') + 1)
    movie.refresh_from_db()

    # Add to watch history
    from .models import WatchHistory, FavoriteAnime

    episode_id = request.GET.get('episode')
    selected_episode = None
    if episode_id:
        selected_episode = episodes.filter(id=episode_id).first()
    if not selected_episode:
        selected_episode = episodes.last()

    WatchHistory.objects.update_or_create(
        user=request.user, movie=movie,
        defaults={'last_watched': timezone.now(), 'last_episode': selected_episode}
    )

    # Check if favorited
    is_favorited = FavoriteAnime.objects.filter(user=request.user, movie=movie).exists()

    vip_data, _ = VipUser.objects.get_or_create(user=request.user)
    tier = vip_data.get_tier()

    # Old premium fallback + new tier logic
    is_staff_or_admin = request.user.is_staff or request.user.is_admin_user
    real_minimum_tier = movie.minimum_tier
    if movie.is_premium and real_minimum_tier == 'basic':
        real_minimum_tier = 'premium'

    has_access = is_staff_or_admin or vip_data.has_access(real_minimum_tier)

    tier_labels = dict(Movie.TIER_CHOICES)
    required_tier_label = tier_labels.get(real_minimum_tier, real_minimum_tier)

    # Qo'shimcha cheklovlar xususiyatlari
    show_ads = (tier == 'basic') and not is_staff_or_admin
    can_download = (tier in ['premium', 'vip']) or is_staff_or_admin
    max_quality = '480p'
    if tier == 'premium' or is_staff_or_admin:
        max_quality = '1080p'
    if tier == 'vip' or is_staff_or_admin:
        max_quality = '4K'

    # Faqat asosiy (parent yo'q) izohlarni olish, javoblarni ichida tayyorlab qo'yish
    tz = ZoneInfo('Asia/Tashkent')
    comments = (
        movie.comments
        .filter(parent__isnull=True)
        .select_related('user', 'user__avatar')
        .prefetch_related('replies__user', 'replies__user__avatar')
    )
    for c in comments:
        c.local_created_at = localtime(c.created_at, tz)
        for r in c.replies.all():
            r.local_created_at = localtime(r.created_at, tz)

    # Izohdan keyin ko'rsatiladigan 2 ta random anime
    import random
    random_pool = list(
        Movie.objects.exclude(id=movie.id).order_by('?')[:10]
    )
    random_movies = random.sample(random_pool, min(2, len(random_pool)))

    return render(request, 'movie_detail.html', {
        'movie': movie,
        'episodes': episodes,
        'has_access': has_access,
        'is_favorited': is_favorited,
        'required_tier_label': required_tier_label,
        'show_ads': show_ads,
        'can_download': can_download,
        'max_quality': max_quality,
        'user_tier': tier,
        'comments': comments,
        'random_movies': random_movies,
    })


# =======================
# MOVIE COMMENT — DELETE
# =======================
@login_required
def delete_comment(request, comment_id):
    from .models import MovieComment
    comment = get_object_or_404(MovieComment, id=comment_id)

    is_owner = comment.user == request.user
    is_admin = request.user.is_staff or request.user.is_superuser or request.user.is_admin_user

    if not (is_owner or is_admin):
        messages.error(request, "Bu izohni o'chirishga ruxsatingiz yo'q")
        return redirect('movie_detail', id=comment.movie_id)

    movie_id = comment.movie_id
    comment.delete()
    return redirect('movie_detail', id=movie_id)


# =======================
# FAVORITE TOGGLE
# =======================
@login_required
def toggle_favorite(request, movie_id):
    from .models import FavoriteAnime
    movie = get_object_or_404(Movie, id=movie_id)
    fav, created = FavoriteAnime.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        fav.delete()
        is_favorited = False
    else:
        is_favorited = True
    return JsonResponse({'is_favorited': is_favorited})


# =======================
# FAVORITES PAGE
# =======================
@login_required
def favorites_page(request):
    from .models import FavoriteAnime
    favs = FavoriteAnime.objects.filter(user=request.user).select_related('movie').order_by('-created_at')
    # Use Paginator if needed, but for now just pass list
    movies = [f.movie for f in favs]
    fav_ids = [m.id for m in movies]
    return render(request, 'anime_catalog.html', {
        'movies': movies,
        'page_title': "Saqlangan Animelar",
        'fav_ids': fav_ids,
    })


# =======================
# WATCH HISTORY PAGE
# =======================
@login_required
def watch_history_page(request):
    from .models import WatchHistory, FavoriteAnime
    hist = WatchHistory.objects.filter(user=request.user).select_related('movie').order_by('-last_watched')
    movies = [h.movie for h in hist]
    fav_ids = list(FavoriteAnime.objects.filter(user=request.user).values_list('movie_id', flat=True))
    return render(request, 'anime_catalog.html', {
        'movies': movies,
        'page_title': "Ko'rishlar Tarixi",
        'fav_ids': fav_ids,
    })


# =======================
# USERNAME CHECK
# =======================
def check_username(request):
    username = request.GET.get('username', '').strip()
    exists = CustomUser.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

# =======================
# PUSH NOTIFICATION — OBUNA SAQLASH
# =======================
@login_required
def save_push_subscription(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)

    try:
        data = json.loads(request.body)
        endpoint = data['endpoint']
        keys = data['keys']

        PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'user': request.user,
                'p256dh': keys['p256dh'],
                'auth': keys['auth'],
            }
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# =======================
# PUSH NOTIFICATION — YUBORISH (ichki funksiya, boshqa view'lardan chaqiriladi)
# =======================
def send_push_notification(user, title, body, url='/'):
    subs = PushSubscription.objects.filter(user=user)
    for sub in subs:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
                },
                data=json.dumps({"title": title, "body": body, "url": url}),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}"}
            )
        except WebPushException as ex:
            # 410 = obuna eskirgan/bekor qilingan, bazadan o'chiramiz
            if ex.response is not None and ex.response.status_code == 410:
                sub.delete()
            else:
                print("Push xatosi:", ex)

# =======================
# PROFILE
# =======================
@login_required(login_url='login')
def profile(request):
    from .models import WatchHistory, UserBalance  # fayl boshida import bo'lsa kerak emas

    vip_data, _ = VipUser.objects.get_or_create(user=request.user)
    balance, _ = UserBalance.objects.get_or_create(user=request.user)
    avatars = ProfileAvatar.objects.all().order_by('-created_at')

    if request.method == 'POST':
        avatar_id = request.POST.get('avatar_id')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        user = request.user
        updated = False

        if avatar_id:
            try:
                selected_avatar = ProfileAvatar.objects.get(id=avatar_id)
                user.avatar = selected_avatar
                updated = True
            except ProfileAvatar.DoesNotExist:
                messages.error(request, "Maxsus profil rasmi topilmadi.")

        if first_name != user.first_name:
            user.first_name = first_name
            updated = True

        if last_name != user.last_name:
            user.last_name = last_name
            updated = True

        if updated:
            user.save()
            messages.success(request, "Profillingiz muvaffaqiyatli saqlandi!")

        return redirect('profile')

    # ===== Oxirgi ko'rilgan 3 ta anime (qism va vaqt bilan) =====
    tz = ZoneInfo('Asia/Tashkent')
    last_watched_history = (
        WatchHistory.objects
        .filter(user=request.user)
        .select_related('movie', 'last_episode')
        .order_by('-last_watched')[:3]
    )
    for w in last_watched_history:
        w.local_time = localtime(w.last_watched, tz)

    context = {
        'total_users': CustomUser.objects.count(),
        'vip_active': vip_data.vip_active(),
        'user_tier': vip_data.get_tier(),
        'avatars': avatars,
        'balance': balance,

        'last_watched_history': last_watched_history,
        'user_level': request.user.get_level(),
        'watched_count': request.user.watched_count(),
    }
    return render(request, 'profile.html', context)


# =======================
# MAKE VIP
# =======================
@login_required
def make_vip(request, user_id):
    if not request.user.is_staff and not request.user.is_admin_user:
        return redirect('profile')

    user = get_object_or_404(CustomUser, id=user_id)

    vip_record, created = VipUser.objects.get_or_create(user=user)
    vip_record.is_vip = True
    vip_record.vip_expire = timezone.now() + timedelta(days=30)
    vip_record.save()

    return redirect('profile')


# =======================
# SEARCH
# =======================
def search(request):
    query = request.GET.get('q', '').strip()
    if query:
        movies = Movie.objects.filter(title__icontains=query)
    else:
        movies = Movie.objects.all()

    fav_ids = []
    if request.user.is_authenticated:
        from .models import FavoriteAnime
        fav_ids = list(FavoriteAnime.objects.filter(user=request.user).values_list('movie_id', flat=True))

    no_results_media = NoResultsMedia.objects.filter(is_active=True).first()

    return render(request, 'search.html', {
        'movies': movies,
        'query': query,
        'fav_ids': fav_ids,
        'no_results_media': no_results_media,
    })


# =======================
# CATALOG
# =======================
def anime_catalog(request):
    movies = Movie.objects.select_related('category').prefetch_related('episodes').order_by('-created_at')
    paginator = Paginator(movies, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    fav_ids = []
    if request.user.is_authenticated:
        from .models import FavoriteAnime
        fav_ids = list(FavoriteAnime.objects.filter(user=request.user).values_list('movie_id', flat=True))

    return render(request, 'anime_catalog.html', {
        'page_obj': page_obj,
        'movies': page_obj.object_list,
        'fav_ids': fav_ids,
    })


# =======================
# CHAT
# =======================
@login_required
def chat(request):
    tz = ZoneInfo('Asia/Tashkent')
    vip_data, _ = VipUser.objects.get_or_create(user=request.user)

    messages_count = ChatMessage.objects.count()
    has_more = messages_count > 40

    messages_list = list(
        ChatMessage.objects.select_related(
            'user', 'reply_to', 'reply_to_news', 'user__avatar', 'user__vip_data'
        ).order_by('-created_at')[:40])
    messages_list.reverse()

    for msg in messages_list:
        msg.local_created_at = localtime(msg.created_at, tz)

    # YANGI — yangilikdan "javob yozish" orqali kelingan bo'lsa
    reply_news_obj = None
    reply_news_id = request.GET.get('reply_news')
    if reply_news_id and reply_news_id.isdigit():
        reply_news_obj = AnimeNews.objects.filter(id=reply_news_id).first()

    if request.method == "POST":
        if request.user.is_banned:
            messages.error(request, "Siz yozolmaysiz")
            return redirect('chat')

        text = request.POST.get("message", "").strip()
        reply_to_id = request.POST.get("reply_to")
        reply_to_news_id = request.POST.get("reply_to_news")   # YANGI
        reply_to_msg = None
        reply_to_news = None                                    # YANGI

        if reply_to_id:
            try:
                reply_to_msg = ChatMessage.objects.get(id=int(reply_to_id))
            except:
                pass

        if reply_to_news_id and reply_to_news_id.isdigit():      # YANGI
            reply_to_news = AnimeNews.objects.filter(id=reply_to_news_id).first()

        if text:
            new_msg = ChatMessage.objects.create(
                user=request.user,
                message=text,
                created_at=timezone.now(),
                reply_to=reply_to_msg,
                reply_to_news=reply_to_news,                      # YANGI
            )
            if reply_to_msg and reply_to_msg.user != request.user:
                Notice.objects.create(
                    notice_type='reply',
                    created_by=request.user,
                    target_user=reply_to_msg.user,
                    title=f"{request.user.username} sizga javob berdi",
                    message=text,
                    related_chat_message=new_msg,
                )
                # YANGI — push notification yuborish
                send_push_notification(
                    user=reply_to_msg.user,
                    title=f"{request.user.username} sizga javob berdi",
                    body=text[:100],
                    url='/chat/'
                )
        return redirect('chat')

    return render(request, 'chat.html', {
        'messages': messages_list,
        'has_more': has_more,
        'user_tier': vip_data.get_tier(),
        'vip_active': vip_data.vip_active(),
        'reply_news_obj': reply_news_obj,   # YANGI
    })


# =======================
# CHAT API (Load older messages)
# =======================
@login_required
def chat_messages_api(request):
    tz = ZoneInfo('Asia/Tashkent')
    before_id = request.GET.get('before')
    try:
        limit = int(request.GET.get('limit', 20))
    except ValueError:
        limit = 20

    qs = ChatMessage.objects.select_related(
        'user', 'user__avatar', 'user__vip_data', 'reply_to', 'reply_to_news'   # reply_to_news qo'shildi
    ).order_by('-created_at')
    if before_id and before_id.isdigit():
        qs = qs.filter(id__lt=before_id)

    messages_list = list(qs[:limit])
    messages_list.reverse()

    data = []
    for msg in messages_list:
        reply_data = None
        if msg.reply_to:
            reply_data = {
                'id': msg.reply_to.id,
                'username': msg.reply_to.user.username,
                'message': msg.reply_to.message,
                'is_vip': hasattr(msg.reply_to.user, 'vip_data') and msg.reply_to.user.vip_data.vip_active(),
            }

        # YANGI
        reply_news_data = None
        if msg.reply_to_news:
            reply_news_data = {
                'id': msg.reply_to_news.id,
                'title': msg.reply_to_news.title,
                'image_url': msg.reply_to_news.image.url if msg.reply_to_news.image else None,
            }

        avatar_url = msg.user.avatar.image.url if getattr(msg.user, 'avatar', None) and msg.user.avatar.image else None

        data.append({
            'id': msg.id,
            'message': msg.message,
            'username': msg.user.username,
            'display_name': msg.user.display_name(),
            'avatar_url': avatar_url,
            'date': localtime(msg.created_at, tz).strftime('%d.%m.%Y'),   # eslatma: kodingizda buni tekshiring, agar yo'q bo'lsa qo'shing
            'time': localtime(msg.created_at, tz).strftime('%H:%M'),
            'edited': msg.edited,
            'is_own': msg.user == request.user,
            'is_admin': msg.user.is_admin_user,
            'is_vip': hasattr(msg.user, 'vip_data') and msg.user.vip_data.vip_active(),
            'reply_to': reply_data,
            'reply_to_news': reply_news_data,   # YANGI
            'can_edit': (msg.user == request.user) or request.user.is_admin_user,
            'can_ban': request.user.is_admin_user and not msg.user.is_admin_user,
            'user_id': msg.user.id
        })

    return JsonResponse({'messages': data})

# =======================
# CHAT: USER MINI PROFIL (avatar bosilganda)
# =======================
@login_required
def user_mini_profile_api(request, user_id):
    from .models import WatchHistory

    target_user = get_object_or_404(CustomUser, id=user_id)
    vip_data, _ = VipUser.objects.get_or_create(user=target_user)

    last_watched_qs = (
        WatchHistory.objects
        .filter(user=target_user)
        .select_related('movie')
        .order_by('-last_watched')[:2]
    )
    last_watched = []
    for w in last_watched_qs:
        m = w.movie
        last_watched.append({
            'id': m.id,
            'title': m.title,
            'image_url': m.image.url if m.image else None,
            'release_year': m.release_year,
        })

    avatar_url = None
    if getattr(target_user, 'avatar', None) and target_user.avatar.image:
        avatar_url = target_user.avatar.image.url

    return JsonResponse({
        'id': target_user.id,
        'username': target_user.username,
        'display_name': target_user.display_name(),
        'first_name': target_user.first_name or "Kiritilmagan",
        'last_name': target_user.last_name or "Kiritilmagan",
        'date_joined': localtime(target_user.date_joined, ZoneInfo('Asia/Tashkent')).strftime('%d.%m.%Y'),
        'avatar_url': avatar_url,
        'tier': vip_data.get_tier(),
        'is_admin': target_user.is_admin_user,
        'level': target_user.get_level(),
        'watched_count': target_user.watched_count(),
        'last_watched': last_watched,
    })


# =======================
# EDIT MESSAGE
# =======================
@login_required
def edit_message(request, message_id):
    msg = get_object_or_404(ChatMessage, id=message_id)

    if request.user != msg.user and not request.user.is_admin_user:
        messages.error(request, "Ruxsat yo‘q")
        return redirect('chat')

    if request.method == "POST":
        new_text = request.POST.get("message", "").strip()
        if new_text:
            msg.message = new_text
            msg.edited = True
            msg.save()

    return redirect('chat')


# =======================
# DELETE MESSAGE
# =======================
@login_required
def delete_message(request, message_id):
    msg = get_object_or_404(ChatMessage, id=message_id)

    if request.user != msg.user and not request.user.is_admin_user:
        messages.error(request, "Ruxsat yo‘q")
        return redirect('chat')

    msg.delete()
    return redirect('chat')


# =======================
# BAN USER
# =======================
@login_required
def ban_user(request, user_id):
    if not request.user.is_admin_user:
        return redirect('chat')

    user_to_ban = get_object_or_404(CustomUser, id=user_id)

    if not user_to_ban.is_admin_user:
        user_to_ban.is_banned = True
        user_to_ban.save()

    return redirect('chat')


# =======================
# PREMIUM PAGE
# =======================
@login_required(login_url='login')
def premium_page(request):
    if request.method == 'POST':
        plan = request.POST.get('plan')
        receipt_image = request.FILES.get('receipt_image')
        if not plan or not receipt_image:
            messages.error(request, "Iltimos, obuna turini va to'lov chekini yuklang.")
        else:
            if SubscriptionReceipt.objects.filter(user=request.user, is_approved=False, is_rejected=False).exists():
                messages.warning(request, "Sizda allaqon ko'rib chiqilayotgan so'rov bor. Iltimos kuting.")
            else:
                SubscriptionReceipt.objects.create(
                    user=request.user,
                    plan=plan,
                    image=receipt_image
                )
                messages.success(request, "So'rovingiz yuborildi! Admin tez orada tasdiqlaydi.")
        return redirect('premium_page')

    vip_data, _ = VipUser.objects.get_or_create(user=request.user)
    return render(request, 'premium.html', {'vip_data': vip_data})



def aloqa(request):
    context = {
        "title": "Aloqa"
    }
    return render(request, "aloqa.html", context)


# =======================
# NEWS FEED (HOME PAGE)
# =======================
def news_feed(request):
    news_qs = AnimeNews.objects.all().order_by('-created_at')
    paginator = Paginator(news_qs, NEWS_PAGE_SIZE)
    page_obj = paginator.get_page(1)

    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(
            NewsLike.objects.filter(user=request.user, news__in=page_obj.object_list)
            .values_list('news_id', flat=True)
        )

    return render(request, 'news.html', {
        'news_list': page_obj.object_list,
        'liked_ids': liked_ids,
        'has_more': page_obj.has_next(),
    })


# =======================
# NEWS — LOAD MORE (infinite scroll uchun AJAX)
# =======================
def news_load_more(request):
    page_number = request.GET.get('page', 2)
    news_qs = AnimeNews.objects.all().order_by('-created_at')
    paginator = Paginator(news_qs, NEWS_PAGE_SIZE)
    page_obj = paginator.get_page(page_number)

    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(
            NewsLike.objects.filter(user=request.user, news__in=page_obj.object_list)
            .values_list('news_id', flat=True)
        )

    html = render_to_string('news_cards.html', {
        'news_list': page_obj.object_list,
        'liked_ids': liked_ids,
    }, request=request)

    return JsonResponse({
        'html': html,
        'has_more': page_obj.has_next(),
    })
# =======================
# NEWS DETAIL PAGE
# =======================
def news_detail(request, pk):
    news = get_object_or_404(AnimeNews, pk=pk)

    is_liked = False
    if request.user.is_authenticated:
        is_liked = NewsLike.objects.filter(
            user=request.user,
            news_id=pk
        ).exists()

    # Rasm hajmi (bayt)
    image_size = None
    if news.image:
        try:
            image_size = news.image.size
        except Exception:
            image_size = None

    # Ulashish uchun to'liq havola: domain/news/<id>/
    share_url = request.build_absolute_uri(reverse('news_detail', args=[news.id]))

    return render(request, 'news_detail.html', {
        'news': news,
        'is_liked': is_liked,
        'total_likes': news.likes.count(),
        'image_size': image_size,
        'share_url': share_url,
    })

# =======================
# LIKE / UNLIKE (TOGGLE)
# =======================
@login_required
def toggle_like(request, pk):
    news = get_object_or_404(AnimeNews, pk=pk)

    like_obj, created = NewsLike.objects.get_or_create(
        user=request.user,
        news=news
    )

    if not created:
        like_obj.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        "liked": liked,
        "total_likes": NewsLike.objects.filter(news=news).count()
    })

@login_required
def reels(request):
    context = {
        "title": "reels"
    }
    return render(request, "reels.html", context)




# =======================
# STORY OCHISH (VIEW PAGE)
# =======================
def story_view(request, story_id):
    story = get_object_or_404(Story, id=story_id, is_active=True)

    if story.expires_at and story.expires_at < timezone.now():
        return redirect('home')

    if request.user.is_authenticated:
        StoryView.objects.get_or_create(user=request.user, story=story)

    return render(request, 'story_view.html', {
        'story': story
    })


# =======================
# AJAX: STORY SEEN
# =======================
@login_required
def mark_story_seen(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    obj, created = StoryView.objects.get_or_create(
        user=request.user,
        story=story
    )

    return JsonResponse({
        'status': 'ok',
        'created': created,
        'views_count': story.views.count()
    })

def get_story_list():
    return list(
        Story.objects.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        ).order_by('created_at')
    )


def next_story_view(request, story_id):
    stories = get_story_list()

    for i, s in enumerate(stories):
        if s.id == story_id:
            if i + 1 < len(stories):
                return redirect('story_view', story_id=stories[i + 1].id)
            else:
                return redirect('home')

    return redirect('home')


def prev_story_view(request, story_id):
    stories = get_story_list()

    for i, s in enumerate(stories):
        if s.id == story_id:
            if i - 1 >= 0:
                return redirect('story_view', story_id=stories[i - 1].id)
            else:
                return redirect('home')

    return redirect('home')




# REELS — views.py ga qo'shing
@login_required
def reels_feed(request):
    latest = Reel.objects.order_by('-created_at').first()
    if latest:
        return redirect('reel_detail', reel_id=latest.id)
    return render(request, 'reels.html', {'reels': [], 'liked_ids': []})


@login_required
def toggle_reel_like(request, reel_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)

    reel = get_object_or_404(Reel, id=reel_id)
    like, created = ReelLike.objects.get_or_create(user=request.user, reel=reel)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'total_likes': reel.likes.count(),
    })


@login_required
def add_reel_comment(request, reel_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)

    reel = get_object_or_404(Reel, id=reel_id)
    text = request.POST.get('text', '').strip()
    reply_to_id = request.POST.get('reply_to')

    reply_obj = None
    if reply_to_id:
        try:
            reply_obj = ReelComment.objects.get(id=int(reply_to_id))
        except (ReelComment.DoesNotExist, ValueError):
            reply_obj = None

    if not text:
        return JsonResponse({'error': "Izoh bo'sh bo'lmasin"}, status=400)

    comment = ReelComment.objects.create(
        reel=reel,
        user=request.user,
        text=text,
        reply_to=reply_obj,
    )

    avatar_url = None
    if getattr(request.user, 'avatar', None) and request.user.avatar.image:
        avatar_url = request.user.avatar.image.url

    return JsonResponse({
        'status': 'ok',
        'comment': {
            'id': comment.id,
            'user': request.user.username,
            'text': comment.text,
            'time': comment.created_at.strftime('%H:%M'),
            'avatar': avatar_url,
            'reply_to': reply_obj.id if reply_obj else None,
            'reply_user': reply_obj.user.username if reply_obj else None,
        },
        'total_comments': reel.comments.count(),
    })


@login_required
def reel_comments_api(request, reel_id):
    comments = ReelComment.objects.select_related(
        'user', 'user__avatar', 'reply_to', 'reply_to__user'
    ).filter(reel_id=reel_id).order_by('created_at')

    data = []
    for c in comments:
        avatar_url = None
        if getattr(c.user, 'avatar', None) and c.user.avatar.image:
            avatar_url = c.user.avatar.image.url

        data.append({
            'id': c.id,
            'user': c.user.username,
            'text': c.text,
            'time': c.created_at.strftime('%H:%M'),
            'avatar': avatar_url,
            'reply_to': c.reply_to.id if c.reply_to else None,
            'reply_user': c.reply_to.user.username if c.reply_to else None,
            'reply_text': c.reply_to.text[:40] if c.reply_to else None,
        })

    return JsonResponse({'comments': data})


@login_required
def reel_share(request, reel_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)

    reel = get_object_or_404(Reel, id=reel_id)
    ReelShare.objects.create(reel=reel, user=request.user)
    Reel.objects.filter(id=reel_id).update(shares_count=models.F('shares_count') + 1)
    reel.refresh_from_db()

    return JsonResponse({
        'status': 'shared',
        'total_shares': reel.shares_count,
    })


def reel_detail(request, reel_id):
    reel = get_object_or_404(Reel, id=reel_id)
    Reel.objects.filter(id=reel_id).update(views_count=models.F('views_count') + 1)

    # Pastga scroll = eski reel (created_at kichikroq)
    next_reel = Reel.objects.filter(
        created_at__lt=reel.created_at
    ).order_by('-created_at').first()

    # Tepaga scroll = yangi reel (created_at kattaroq)
    prev_reel = Reel.objects.filter(
        created_at__gt=reel.created_at
    ).order_by('created_at').first()

    is_liked = False
    if request.user.is_authenticated:
        is_liked = ReelLike.objects.filter(user=request.user, reel=reel).exists()

    return render(request, 'reel_detail.html', {
        'reel': reel,
        'is_liked': is_liked,
        'total_likes': reel.likes.count(),
        'total_comments': reel.comments.count(),
        'next_reel': next_reel,
        'prev_reel': prev_reel,
    })



def sifat(request):
    return redirect('sifat.html')




# ========================
# views.py ga QO'SHING
# ========================
# Import qatoriga qo'shing:
#   from .models import UserSettings

BG_COLORS = [
    {'name': 'Qora',           'value': '#0a0a0f',   'css': '#0a0a0f'},
    {'name': 'Qoʻngʻir qora',  'value': '#0d0d0d',   'css': '#0d0d0d'},
    {'name': 'To\'q ko\'k',    'value': '#050d1a',   'css': '#050d1a'},
    {'name': 'Chuqur ko\'k',   'value': '#060b18',   'css': 'linear-gradient(135deg,#060b18,#0a0f22)'},
    {'name': 'Qoʻngʻir',       'value': '#120a06',   'css': '#120a06'},
    {'name': 'Qizil-qora',     'value': '#120a0f',   'css': '#120a0f'},
    {'name': 'Roʻza-qora',     'value': '#180810',   'css': 'linear-gradient(135deg,#180810,#0d0510)'},
    {'name': 'Binafsha-qora',  'value': '#0a0818',   'css': 'linear-gradient(135deg,#0a0818,#120a1f)'},
    {'name': 'Yashil-qora',    'value': '#060f0a',   'css': '#060f0a'},
    {'name': 'Kulrang',        'value': '#101014',   'css': '#101014'},
]


@login_required(login_url='login')
def settings_general(request):
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        settings_obj.theme         = request.POST.get('theme', 'dark')
        settings_obj.bg_color      = request.POST.get('bg_color', '#0a0a0f')
        settings_obj.bg_color_custom = request.POST.get('bg_color_custom', '#0a0a0f')
        settings_obj.tabbar_on     = request.POST.get('tabbar_on', '0') == '1'
        settings_obj.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        return redirect('settings_general')

    return render(request, 'boshqaruv/umumiynazorat.html', {
        'settings':   settings_obj,
        'bg_colors':  BG_COLORS,
        'active_section': 'general',
    })


@login_required(login_url='login')
def settings_telegram(request):
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        settings_obj.telegram_username  = request.POST.get('telegram_username', '').strip()
        settings_obj.telegram_chat_id   = request.POST.get('telegram_chat_id', '').strip()
        settings_obj.telegram_bot_token = request.POST.get('telegram_bot_token', '').strip()
        settings_obj.telegram_notify_on = request.POST.get('telegram_notify_on', '0') == '1'
        settings_obj.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        return redirect('settings_telegram')

    return render(request, 'boshqaruv/telegram.html', {
        'settings':       settings_obj,
        'active_section': 'telegram',
    })


@login_required(login_url='login')
def settings_premium(request):
    from .models import VipUser
    vip_data, _ = VipUser.objects.get_or_create(user=request.user)
    return render(request, 'boshqaruv/premium_settings.html', {
        'vip_data':       vip_data,
        'active_section': 'premium',
    })


@login_required(login_url='login')
def settings_devices(request):
    from .models import ActiveSession
    sessions = ActiveSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'boshqaruv/devices.html', {
        'sessions':       sessions,
        'active_section': 'devices',
    })


@login_required(login_url='login')
def settings_privacy(request):
    return render(request, 'boshqaruv/privacy.html', {
        'active_section': 'privacy',
    })




def parse_user_agent(ua_string):
    """User-Agent stringidan browser va OS ni ajratib olish"""
    if not ua_string:
        return 'Noma\'lum', 'Noma\'lum', 'unknown'

    ua = ua_string.lower()

    # Browser aniqlash
    if 'edg/' in ua or 'edge/' in ua:
        browser = 'Microsoft Edge'
    elif 'opr/' in ua or 'opera' in ua:
        browser = 'Opera'
    elif 'chrome/' in ua and 'safari/' in ua:
        browser = 'Google Chrome'
    elif 'firefox/' in ua:
        browser = 'Mozilla Firefox'
    elif 'safari/' in ua and 'chrome/' not in ua:
        browser = 'Safari'
    elif 'samsungbrowser' in ua:
        browser = 'Samsung Browser'
    elif 'miuibrowser' in ua:
        browser = 'MIUI Browser'
    else:
        browser = 'Boshqa brauzer'

    # OS aniqlash
    if 'windows nt 10' in ua:
        os_name = 'Windows 10/11'
    elif 'windows nt 6.3' in ua:
        os_name = 'Windows 8.1'
    elif 'windows nt 6.1' in ua:
        os_name = 'Windows 7'
    elif 'windows' in ua:
        os_name = 'Windows'
    elif 'android' in ua:
        match = re.search(r'android\s([\d.]+)', ua)
        version = match.group(1) if match else ''
        os_name = f'Android {version}'.strip()
    elif 'iphone os' in ua or 'iphone' in ua:
        match = re.search(r'os\s([\d_]+)', ua)
        version = match.group(1).replace('_', '.') if match else ''
        os_name = f'iOS {version}'.strip()
    elif 'ipad' in ua:
        os_name = 'iPadOS'
    elif 'mac os x' in ua:
        os_name = 'macOS'
    elif 'linux' in ua:
        os_name = 'Linux'
    else:
        os_name = 'Noma\'lum OS'

    # Qurilma turi
    if any(x in ua for x in ['iphone', 'android', 'mobile', 'blackberry', 'windows phone']):
        device_type = 'mobile'
    elif any(x in ua for x in ['ipad', 'tablet']):
        device_type = 'tablet'
    elif any(x in ua for x in ['windows', 'macintosh', 'linux', 'x11']):
        device_type = 'desktop'
    else:
        device_type = 'unknown'

    return browser, os_name, device_type


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


@login_required(login_url='login')
def settings_devices(request):
    from .models import ActiveSession
    from django.contrib.sessions.models import Session

    # Joriy sessionni ro'yxatga olish / yangilash
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    ua_string  = request.META.get('HTTP_USER_AGENT', '')
    ip         = get_client_ip(request)
    browser, os_name, device_type = parse_user_agent(ua_string)
    device_name = f"{browser} / {os_name}"

    ActiveSession.objects.update_or_create(
        session_key=session_key,
        defaults={
            'user':        request.user,
            'ip_address':  ip,
            'user_agent':  ua_string,
            'browser':     browser,
            'os_name':     os_name,
            'device_type': device_type,
            'device_name': device_name,
        }
    )

    # Foydalanuvchining barcha sessionlari
    sessions = ActiveSession.objects.filter(user=request.user).order_by('-last_activity')

    if request.method == 'POST':
        action = request.POST.get('action')
        target_key = request.POST.get('session_key')

        if action == 'logout_single' and target_key:
            # Tanlangan qurilmani chiqarish
            if target_key != session_key:  # O'zini chiqarmasin
                try:
                    Session.objects.filter(session_key=target_key).delete()
                except Exception:
                    pass
                ActiveSession.objects.filter(
                    session_key=target_key,
                    user=request.user
                ).delete()

        elif action == 'logout_all':
            # Joriy qurilmadan tashqari hammasini chiqarish
            other_sessions = ActiveSession.objects.filter(
                user=request.user
            ).exclude(session_key=session_key)
            for s in other_sessions:
                try:
                    Session.objects.filter(session_key=s.session_key).delete()
                except Exception:
                    pass
            other_sessions.delete()

        return redirect('settings_devices')

    return render(request, 'boshqaruv/devices.html', {
        'sessions':          sessions,
        'current_session':   session_key,
        'active_section':    'devices',
    })

def anime_category(request):
    from .models import AnimeSectionItem

    # BARCHA ANIME — hamma card chiqadi
    all_movies = Movie.objects.select_related('category').prefetch_related('episodes').order_by('-created_at')

    # KUNLIK ANIME — faqat admin "daily" sifatida qo'shgan animelar
    daily_movies = Movie.objects.select_related('category').prefetch_related('episodes').filter(
        section_items__section='daily'
    ).order_by('section_items__order', '-section_items__created_at')

    # ANIME FILM — faqat admin "film" sifatida qo'shgan animelar
    movie_films = Movie.objects.select_related('category').prefetch_related('episodes').filter(
        section_items__section='film'
    ).order_by('section_items__order', '-section_items__created_at')

    context = {
        'daily_movies': daily_movies,
        'all_movies': all_movies,
        'movie_films': movie_films,
    }
    return render(request, 'category.html', context)


@login_required
def notice(request):
    base_qs = Notice.objects.filter(is_active=True).filter(
        Q(notice_type='admin', target_user__isnull=True) |
        Q(notice_type='reply', target_user=request.user)
    )

    # Barchasini o'qilgan qilish
    if request.GET.get('mark_all') == '1':
        unread_ids = base_qs.exclude(reads__user=request.user).values_list('id', flat=True)
        NoticeRead.objects.bulk_create(
            [NoticeRead(user=request.user, notice_id=nid) for nid in unread_ids],
            ignore_conflicts=True
        )
        return redirect('notice')

    # Bitta cardga bosilganda — o'qilgan qilish
    read_id = request.GET.get('read')
    if read_id and read_id.isdigit():
        notice_obj = base_qs.filter(id=read_id).first()
        if notice_obj:
            NoticeRead.objects.get_or_create(user=request.user, notice=notice_obj)
            if notice_obj.notice_type == 'reply':
                if notice_obj.related_movie_comment_id:
                    comment = notice_obj.related_movie_comment
                    url = reverse('movie_detail', args=[comment.movie_id])
                    return redirect(f"{url}#comment-{comment.id}")
                return redirect('chat')  # chat javobi bo'lsa — chatga olib boradi
        return redirect('notice')  # admin xabari bo'lsa — shu sahifada qoladi

    read_ids = set(
        NoticeRead.objects.filter(user=request.user).values_list('notice_id', flat=True)
    )

    notices = list(
        base_qs.select_related('created_by', 'related_chat_message', 'related_movie_comment')
        .order_by('-created_at')
    )
    for n in notices:
        n.is_read = n.id in read_ids
        # Chat javobimi yoki Anime izohiga javobmi — belgilab qo'yamiz (ixtiyoriy, UI uchun)
        n.source = 'movie' if n.related_movie_comment_id else ('chat' if n.related_chat_message_id else None)

    # ===== IKKI BO'LIMGA AJRATISH =====
    admin_notices = [n for n in notices if n.notice_type == 'admin']
    reply_notices = [n for n in notices if n.notice_type == 'reply']

    admin_unread_count = sum(1 for n in admin_notices if not n.is_read)
    reply_unread_count = sum(1 for n in reply_notices if not n.is_read)

    return render(request, 'notice.html', {
        'admin_notices': admin_notices,
        'reply_notices': reply_notices,
        'admin_unread_count': admin_unread_count,
        'reply_unread_count': reply_unread_count,
    })

# =======================
# SERVICE WORKER / MANIFEST / OFFLINE
# =======================
def service_worker_view(request):
    content = render_to_string('service-worker.js')
    response = HttpResponse(content, content_type='application/javascript')
    # MUHIM: brauzer bu faylni keshlamasin — aks holda yangi versiya
    # chiqarganda foydalanuvchilarda eski SW ishlab qolaveradi
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Service-Worker-Allowed'] = '/'
    return response


def manifest_view(request):
    content = render_to_string('manifest.json')
    return HttpResponse(content, content_type='application/manifest+json')


def offline_view(request):
    return render(request, 'offline.html')

VIP_PLANS = [
    {'key': '1_5week', 'label': "1.5 haftalik", 'price': 5000, 'days': 11},
    {'key': '1_month', 'label': "1 oylik", 'price': 10000, 'days': 30},
    {'key': '3_month', 'label': "3 oylik", 'price': 28000, 'days': 90},
    {'key': '6_month', 'label': "6 oylik", 'price': 51000, 'days': 180},
]
VIP_PLANS_DICT = {p['key']: p for p in VIP_PLANS}

@login_required
def hisobim_page(request):
    from .models import UserBalance
    balance, _ = UserBalance.objects.get_or_create(user=request.user)
    vip_data, _ = VipUser.objects.get_or_create(user=request.user)

    tz = ZoneInfo('Asia/Tashkent')
    history = AccountHistory.objects.filter(user=request.user).order_by('-created_at')[:50]
    for h in history:
        h.local_time = localtime(h.created_at, tz)

    my_debt_pending = DebtRequest.objects.filter(user=request.user, status='pending').exists()

    vip_expire_local = None
    if vip_data.vip_active():
        vip_expire_local = localtime(vip_data.vip_expire, tz)

    return render(request, 'hisobim.html', {
        'balance': balance,
        'vip_data': vip_data,
        'vip_expire_local': vip_expire_local,
        'vip_plans': VIP_PLANS,
        'history': history,
        'my_debt_pending': my_debt_pending,
    })


@login_required
def vip_buy_balance(request, plan_key):
    if request.method == 'POST':
        plan = VIP_PLANS_DICT.get(plan_key)
        if not plan:
            messages.error(request, "Noto'g'ri reja tanlandi.")
            return redirect('hisobim_page')

        balance, _ = UserBalance.objects.get_or_create(user=request.user)
        if balance.amount < plan['price']:
            messages.error(request, "Hisobingizda mablag' yetarli emas.")
            return redirect('hisobim_page')

        UserBalance.objects.filter(user=request.user).update(amount=F('amount') - plan['price'])

        vip_data, _ = VipUser.objects.get_or_create(user=request.user)
        now = timezone.now()
        base = vip_data.vip_expire if (vip_data.vip_expire and vip_data.vip_expire > now) else now
        vip_data.is_vip = True
        vip_data.tier = 'vip'
        vip_data.vip_expire = base + timedelta(days=plan['days'])
        vip_data.save()

        AccountHistory.objects.create(
            user=request.user,
            text=f"{plan['price']:,} so'm — {plan['label']} VIP obuna aktivlashtirildi".replace(',', '.')
        )
        messages.success(request, f"{plan['label']} VIP obuna faollashtirildi!")
    return redirect('hisobim_page')


@login_required
def debt_request_add(request):
    if request.method == 'POST':
        if DebtRequest.objects.filter(user=request.user, status='pending').exists():
            messages.warning(request, "Sizda hali ko'rib chiqilayotgan qarz so'rovi bor.")
        else:
            try:
                amount = int(request.POST.get('amount', 0))
            except ValueError:
                amount = 0
            if amount <= 0:
                messages.error(request, "To'g'ri summa kiriting.")
            else:
                DebtRequest.objects.create(user=request.user, amount=amount)
                AccountHistory.objects.create(
                    user=request.user,
                    text=f"{amount:,} so'm qarz so'raldi — ko'rib chiqilmoqda".replace(',', '.')
                )
                messages.success(request, "Qarz so'rovingiz yuborildi.")
    return redirect('hisobim_page')


@login_required
def balance_topup_add(request):
    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount', 0))
        except ValueError:
            amount = 0
        image = request.FILES.get('receipt_image')

        if amount <= 0 or not image:
            messages.error(request, "Summa va chek rasmini to'g'ri kiriting.")
        else:
            BalanceTopupRequest.objects.create(user=request.user, amount=amount, image=image)
            AccountHistory.objects.create(
                user=request.user,
                text=f"{amount:,} so'm hisobni to'ldirish so'rovi yuborildi — ko'rib chiqilmoqda".replace(',', '.')
            )
            messages.success(request, "So'rovingiz yuborildi! Admin tez orada tasdiqlaydi.")
    return redirect('hisobim_page')


@login_required
def jackpot_redeem(request):
    if request.method == 'POST':
        code_str = request.POST.get('code', '').strip()
        jackpot = JackpotCode.objects.filter(code__iexact=code_str).first() if code_str else None

        if not jackpot:
            messages.error(request, "Bunday jackpot kod topilmadi.")
        elif JackpotCodeUse.objects.filter(user=request.user, code=jackpot).exists():
            messages.error(request, "Siz bu koddan avval foydalangansiz.")
        elif not jackpot.is_valid():
            if jackpot.expires_at and jackpot.expires_at < timezone.now():
                reason = "muddati tugagan"
            elif jackpot.max_uses and jackpot.used_count() >= jackpot.max_uses:
                reason = "foydalanuvchilar soni to'lgan"
            else:
                reason = "faol emas"
            AccountHistory.objects.create(
                user=request.user,
                text=f"Jackpot: \"{jackpot.code}\" — ulgurmadingiz, {reason}"
            )
            messages.error(request, "Kod muddati tugagan, limitga yetgan yoki faol emas.")
        else:
            JackpotCodeUse.objects.create(user=request.user, code=jackpot)

            if jackpot.reward_type == 'vip_hour':
                vip_data, _ = VipUser.objects.get_or_create(user=request.user)
                now = timezone.now()
                base = vip_data.vip_expire if (vip_data.vip_expire and vip_data.vip_expire > now) else now
                vip_data.is_vip = True
                vip_data.tier = 'vip'
                vip_data.vip_expire = base + timedelta(hours=jackpot.vip_hours)
                vip_data.save()
                AccountHistory.objects.create(
                    user=request.user,
                    text=f"Jackpot: {jackpot.vip_hours} soatlik VIP obuna aktivlashtirildi 🎉"
                )
                messages.success(request, f"Tabriklaymiz! {jackpot.vip_hours} soatlik VIP obuna aktivlashtirildi.")

            elif jackpot.reward_type == 'vip_day':
                vip_data, _ = VipUser.objects.get_or_create(user=request.user)
                now = timezone.now()
                base = vip_data.vip_expire if (vip_data.vip_expire and vip_data.vip_expire > now) else now
                vip_data.is_vip = True
                vip_data.tier = 'vip'
                vip_data.vip_expire = base + timedelta(days=jackpot.vip_days)
                vip_data.save()
                AccountHistory.objects.create(
                    user=request.user,
                    text=f"Jackpot: {jackpot.vip_days} kunlik VIP obuna aktivlashtirildi 🎉"
                )
                messages.success(request, f"Tabriklaymiz! {jackpot.vip_days} kunlik VIP obuna aktivlashtirildi.")

            else:  # balance
                UserBalance.objects.filter(user=request.user).update(amount=F('amount') + jackpot.balance_amount)
                AccountHistory.objects.create(
                    user=request.user,
                    text=f"Jackpot: hisobingizga {jackpot.balance_amount:,} so'm tushdi 🎉".replace(',', '.')
                )
                messages.success(request, f"Tabriklaymiz! Hisobingizga {jackpot.balance_amount:,} so'm tushdi.".replace(',', '.'))
    return redirect('hisobim_page')

@login_required
def statistika_page(request):
    return render(request, 'statistika.html', {})

@login_required
def imkon_page(request):
    from .models import (
        UserSettings, PremiumBackground, AnimeVoteRequest, AnimeVote,
        AnimeRequestSuggestion, VipUser
    )

    vip_data, _ = VipUser.objects.get_or_create(user=request.user)
    tier = vip_data.get_tier()
    is_premium = tier in ['premium', 'vip'] or request.user.is_staff or request.user.is_admin_user

    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
    backgrounds = PremiumBackground.objects.all()

    vote_requests = (
        AnimeVoteRequest.objects
        .annotate(votes_count=models.Count('votes'))
        .order_by('-votes_count', '-created_at')
    )
    voted_ids = set(
        AnimeVote.objects.filter(user=request.user).values_list('request_id', flat=True)
    )

    premium_count = VipUser.objects.filter(is_vip=True).count()

    my_vote_request = AnimeVoteRequest.objects.filter(created_by=request.user).first()
    my_request = AnimeRequestSuggestion.objects.filter(user=request.user).first()

    requested_names = (
        AnimeRequestSuggestion.objects
        .values('name')
        .annotate(total=models.Count('id'))
        .order_by('-total')
    )

    context = {
        'is_premium': is_premium,
        'user_tier': tier,
        'settings': settings_obj,
        'backgrounds': backgrounds,
        'vote_requests': vote_requests,
        'voted_ids': voted_ids,
        'premium_count': premium_count,
        'my_vote_request': my_vote_request,
        'my_request': my_request,
        'requested_names': requested_names,
    }
    return render(request, 'imkon.html', context)


@login_required
def imkon_toggle_bg(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)
    from .models import UserSettings, VipUser
    vip_data, _ = VipUser.objects.get_or_create(user=request.user)
    if vip_data.get_tier() not in ['premium', 'vip'] and not (request.user.is_staff or request.user.is_admin_user):
        return JsonResponse({'error': 'Faqat premium/VIP azolar uchun'}, status=403)

    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
    settings_obj.premium_bg_on = not settings_obj.premium_bg_on
    settings_obj.save()
    return JsonResponse({'premium_bg_on': settings_obj.premium_bg_on})


@login_required
def imkon_select_bg(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)
    from .models import UserSettings, PremiumBackground
    bg = get_object_or_404(PremiumBackground, pk=pk)
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
    settings_obj.premium_bg = bg
    settings_obj.premium_bg_on = True
    settings_obj.save()
    return JsonResponse({'ok': True, 'bg_id': bg.id, 'bg_url': bg.image.url})


@login_required
def imkon_toggle_telegram_download(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)
    from .models import UserSettings
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
    settings_obj.telegram_download_on = not settings_obj.telegram_download_on
    settings_obj.save()
    return JsonResponse({'telegram_download_on': settings_obj.telegram_download_on})


@login_required
def imkon_vote_request_add(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)
    from .models import VipUser, AnimeVoteRequest
    vip_data, _ = VipUser.objects.get_or_create(user=request.user)
    if vip_data.get_tier() not in ['premium', 'vip']:
        return JsonResponse({'error': "Faqat VIP azolar anime taklif qila oladi"}, status=403)

    if AnimeVoteRequest.objects.filter(created_by=request.user).exists():
        return JsonResponse({'error': "Siz allaqachon 1 ta anime taklif qilgansiz"}, status=400)

    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'error': "Anime nomini kiriting"}, status=400)

    req = AnimeVoteRequest.objects.create(name=name, created_by=request.user)
    return JsonResponse({'ok': True, 'id': req.id, 'name': req.name})


@login_required
def imkon_vote(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)
    from .models import VipUser, AnimeVoteRequest, AnimeVote
    vip_data, _ = VipUser.objects.get_or_create(user=request.user)
    if vip_data.get_tier() not in ['premium', 'vip']:
        return JsonResponse({'need_vip': True, 'error': "Ovoz berish uchun Premium/VIP obuna kerak"}, status=403)

    req = get_object_or_404(AnimeVoteRequest, pk=pk)
    vote, created = AnimeVote.objects.get_or_create(request=req, user=request.user)
    if not created:
        vote.delete()
        voted = False
    else:
        voted = True

    return JsonResponse({
        'voted': voted,
        'total_votes': req.total_votes(),
        'approved': req.total_votes() >= 10,
    })


@login_required
def imkon_anime_request_add(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST talab qilinadi'}, status=405)
    from .models import VipUser, AnimeRequestSuggestion
    vip_data, _ = VipUser.objects.get_or_create(user=request.user)
    if vip_data.get_tier() not in ['premium', 'vip']:
        return JsonResponse({'error': 'Faqat premium/VIP azolar uchun'}, status=403)

    if AnimeRequestSuggestion.objects.filter(user=request.user).exists():
        return JsonResponse({'error': "Siz allaqachon so'rov yuborgansiz"}, status=400)

    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'error': "Anime nomini kiriting"}, status=400)

    AnimeRequestSuggestion.objects.create(user=request.user, name=name)
    return JsonResponse({'ok': True, 'name': name})
