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

from .models import (
    CustomUser, Category, Movie, MovieEpisode,
    SiteSettings, MP3, ChatMessage, VipUser
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

    if not hero_movies:
        hero_movies = list(
            movies.select_related('category').prefetch_related('episodes')[:7]
        )

    categories = Category.objects.all()

    mp3_to_play = None
    if request.user.is_authenticated:
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
        'categories': categories,
        'mp3_file': mp3_to_play,
        'total_users': User.objects.count(),
        'user_id': request.user.id if request.user.is_authenticated else None,
    }

    return render(request, 'home.html', context)


# =======================
# MOVIE DETAIL
# =======================
@login_required
def movie_detail(request, id):
    movie = get_object_or_404(Movie, id=id)
    episodes = movie.episodes.all().order_by('episode_number')

    return render(request, 'movie_detail.html', {
        'movie': movie,
        'episodes': episodes
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
@login_required
def profile(request):
    user = request.user
    uz_time = ZoneInfo('Asia/Tashkent')
    date_joined_uz = localtime(user.date_joined, uz_time).strftime("%d-%m-%Y %H:%M:%S")

    try:
        total_users = CustomUser.objects.latest('id').id
    except CustomUser.DoesNotExist:
        total_users = 0

    # ✅ VIP tekshiruv
    vip = getattr(user, 'vip_data', None)
    vip_active = vip.vip_active() if vip else False

    return render(request, 'profile.html', {
        'user': user,
        'date_joined_uz': date_joined_uz,
        'total_users': total_users,
        'vip_active': vip_active
    })


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

    return render(request, 'search.html', {
        'movies': movies,
        'query': query,
    })


# =======================
# CATALOG
# =======================
def anime_catalog(request):
    movies = Movie.objects.select_related('category').prefetch_related('episodes').order_by('-created_at')
    paginator = Paginator(movies, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'anime_catalog.html', {
        'page_obj': page_obj,
        'movies': page_obj.object_list,
    })


# =======================
# CHAT
# =======================
@login_required
def chat(request):
    tz = ZoneInfo('Asia/Tashkent')
    messages_list = ChatMessage.objects.select_related('user', 'reply_to').order_by('created_at')

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

    return render(request, 'chat.html', {'messages': messages_list})


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