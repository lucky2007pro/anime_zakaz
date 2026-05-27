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
import re
from django.contrib.sessions.models import Session


from .models import (
    CustomUser, VipUser, Category, Movie, SiteSettings, MP3, ChatMessage, SubscriptionReceipt, ProfileAvatar, AnimeNews, NewsLike,
    Story, StoryView, Reel, ReelLike, ReelComment, ReelShare,UserSettings
)

User = get_user_model()


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
    }

    return render(request, 'home.html', context)




# =======================
# MOVIE DETAIL
# =======================
@login_required
def movie_detail(request, id):
    movie = get_object_or_404(Movie, id=id)

    if request.method == "POST":
        text = request.POST.get("comment", "").strip()
        if text:
            from .models import MovieComment
            MovieComment.objects.create(movie=movie, user=request.user, text=text)
        return redirect('movie_detail', id=movie.id)

    episodes = movie.episodes.all().order_by('episode_number')

    # Increment views remotely safely
    Movie.objects.filter(id=id).update(views_count=F('views_count') + 1)
    movie.refresh_from_db()

    # Add to watch history
    from .models import WatchHistory, FavoriteAnime
    WatchHistory.objects.update_or_create(user=request.user, movie=movie, defaults={'last_watched': timezone.now()})

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

    comments = movie.comments.select_related('user', 'user__avatar').all()
    tz = ZoneInfo('Asia/Tashkent')
    for c in comments:
        c.local_created_at = localtime(c.created_at, tz)

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
# PROFILE
# =======================
@login_required(login_url='login')
def profile(request):
    vip_data, _ = VipUser.objects.get_or_create(user=request.user)
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

    context = {
        'total_users': CustomUser.objects.count(),
        'vip_active': vip_data.vip_active(),
        'avatars': avatars,
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

    return render(request, 'search.html', {
        'movies': movies,
        'query': query,
        'fav_ids': fav_ids,
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

    # fetch all messages up to limit
    messages_count = ChatMessage.objects.count()
    has_more = messages_count > 40

    messages_list = list(
        ChatMessage.objects.select_related('user', 'reply_to', 'user__avatar', 'user__vip_data').order_by(
            '-created_at')[:40])
    messages_list.reverse()

    for msg in messages_list:
        msg.local_created_at = localtime(msg.created_at, tz)

    if request.method == "POST":

        if request.user.is_banned:
            messages.error(request, "Siz yozolmaysiz")
            return redirect('chat')

        text = request.POST.get("message", "").strip()
        reply_to_id = request.POST.get("reply_to")
        reply_to_msg = None

        if reply_to_id:
            try:
                reply_to_msg = ChatMessage.objects.get(id=int(reply_to_id))
            except:
                pass

        if text:
            ChatMessage.objects.create(
                user=request.user,
                message=text,
                created_at=timezone.now(),
                reply_to=reply_to_msg
            )

        return redirect('chat')

    return render(request, 'chat.html', {
        'messages': messages_list,
        'has_more': has_more
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

    qs = ChatMessage.objects.select_related('user', 'user__avatar', 'user__vip_data', 'reply_to').order_by(
        '-created_at')
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
                'message': msg.reply_to.message
            }

        avatar_url = msg.user.avatar.image.url if getattr(msg.user, 'avatar', None) and msg.user.avatar.image else None

        data.append({
            'id': msg.id,
            'message': msg.message,
            'username': msg.user.username,
            'avatar_url': avatar_url,
            'time': localtime(msg.created_at, tz).strftime('%H:%M'),
            'edited': msg.edited,
            'is_own': msg.user == request.user,
            'is_admin': msg.user.is_admin_user,
            'is_vip': hasattr(msg.user, 'vip_data') and msg.user.vip_data.vip_active(),
            'reply_to': reply_data,
            'can_edit': (msg.user == request.user) or request.user.is_admin_user,
            'can_ban': request.user.is_admin_user and not msg.user.is_admin_user,
            'user_id': msg.user.id
        })

    return JsonResponse({'messages': data})


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
    news_list = AnimeNews.objects.all().order_by('-created_at')

    return render(request, 'news.html', {
        'news_list': news_list
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

    return render(request, 'news_detail.html', {
        'news': news,
        'is_liked': is_liked,
        'total_likes': news.likes.count()   # agar ManyToMany ishlatsang
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




# confikuchun viev qismi

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
