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

from .models import (
    CustomUser, VipUser, Category, Movie, SiteSettings, MP3, ChatMessage, SubscriptionReceipt, ProfileAvatar, AnimeNews, NewsLike
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

    mp3_to_play = None
    fav_ids = []
    if request.user.is_authenticated:
        from .models import FavoriteAnime
        fav_ids = list(FavoriteAnime.objects.filter(user=request.user).values_list('movie_id', flat=True))
        try:
            mp3_obj = MP3.objects.latest('created_at')
            mp3_file = mp3_obj.file.url
        except MP3.DoesNotExist:
            mp3_file = None

        mp3_to_play = mp3_file if not request.session.get('mp3_played', False) else None
        request.session['mp3_played'] = True

    context = {
        'movies': movies,
        'hero_movies': hero_movies,
        'recommended_movies': recommended_movies,
        'categories': categories,
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

    # Qo'shimcha cheklovlar xususiyatlari (rasm/tariflardagi imkoniyatlarga qarab):
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
        'comments': comments
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
    
    messages_list = list(ChatMessage.objects.select_related('user', 'reply_to', 'user__avatar', 'user__vip_data').order_by('-created_at')[:40])
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

    qs = ChatMessage.objects.select_related('user', 'user__avatar', 'user__vip_data', 'reply_to').order_by('-created_at')
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

@login_required
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
        "title": "Aloqa"
    }
    return render(request, "reels.html", context)




