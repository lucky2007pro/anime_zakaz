from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .models import CustomUser, Movie, MovieEpisode, Category, ChatMessage, SubscriptionReceipt, ProfileAvatar, VipUser

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.is_admin_user)


def is_super_admin(user):
    return user.is_authenticated and user.is_superuser


def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

@user_passes_test(is_admin, login_url='/')
def admin_dashboard(request):
    context = {
        'total_animes': Movie.objects.count(),
        'total_episodes': MovieEpisode.objects.count(),
        'total_genres': Category.objects.count(),
        'total_users': CustomUser.objects.count(),
        'total_receipts': SubscriptionReceipt.objects.filter(is_approved=False, is_rejected=False).count(),
        'latest_animes': Movie.objects.all().order_by('-created_at')[:5],
        'latest_users': CustomUser.objects.all().order_by('-date_joined')[:5],
        'latest_messages': ChatMessage.objects.all().order_by('-created_at')[:10],
        'latest_topics': SubscriptionReceipt.objects.all().order_by('-created_at')[:5], # latest_receipts o'rniga latest_topics dan foydalansak
    }
    return render(request, 'custom_admin/dashboard.html', context)


@user_passes_test(is_super_admin, login_url='/')
def admin_users(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Foydalanuvchilar',
        'items': users,
        'type': 'user'
    })


@user_passes_test(is_super_admin, login_url='/')
def admin_user_role(request, user_id):
    if request.method != 'POST':
        return redirect('admin_users')

    user = get_object_or_404(CustomUser, id=user_id)
    role = request.POST.get('role', '')
    value = request.POST.get('value', '0') == '1'

    if user == request.user and not value and role in {'superuser', 'staff'}:
        messages.error(request, 'O‘zingizning asosiy admin vakolatingizni shu yerda olib tashlay olmaysiz.')
        return redirect('admin_users')

    if role == 'content_admin':
        user.is_admin_user = value
        if value:
            user.is_active = True
    elif role == 'staff':
        user.is_staff = value
        if value:
            user.is_active = True
    elif role == 'superuser':
        if request.user.is_superuser:
            user.is_superuser = value
            if value:
                user.is_staff = True
                user.is_admin_user = True
                user.is_active = True
        else:
            messages.error(request, 'Superadmin vakolati faqat superadmin tomonidan o‘zgartiriladi.')
            return redirect('admin_users')
    else:
        messages.error(request, 'Noto‘g‘ri rol turi.')
        return redirect('admin_users')

    if role != 'superuser':
        user.is_superuser = user.is_superuser and request.user.is_superuser

    user.save(update_fields=['is_admin_user', 'is_staff', 'is_superuser', 'is_active'])
    messages.success(request, f"{user.username} uchun vakolatlar yangilandi.")
    return redirect('admin_users')

@user_passes_test(is_admin, login_url='/')
def admin_movies(request):
    movies = Movie.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Animelar',
        'items': movies,
        'type': 'movie'
    })

@user_passes_test(is_admin, login_url='/')
def admin_genres(request):
    genres = Category.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Janrlar',
        'items': genres,
        'type': 'genre'
    })

@user_passes_test(is_admin, login_url='/')
def admin_chat(request):
    messages_qs = ChatMessage.objects.all().order_by('-created_at')[:50]
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Chat xabarlari',
        'items': messages_qs,
        'type': 'chat'
    })

@user_passes_test(is_admin, login_url='/')
def admin_movie_form(request, pk=None):
    movie = get_object_or_404(Movie, pk=pk) if pk else None
    genres = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('description')
        cat_id = request.POST.get('category')
        vid_url = request.POST.get('video_url')
        tg_link = request.POST.get('telegram_link')
        is_home_featured = request.POST.get('is_home_featured') == 'on'
        minimum_tier = request.POST.get('minimum_tier', 'basic')
        release_year = request.POST.get('release_year', '').strip()
        try:
            home_featured_order = int(request.POST.get('home_featured_order', 0) or 0)
        except (TypeError, ValueError):
            home_featured_order = 0
        image = request.FILES.get('image')
        video_file = request.FILES.get('video_file')
        hero_media = request.FILES.get('hero_media')

        if not movie:
            movie = Movie()
        
        movie.title = title
        movie.description = desc
        movie.video_url = vid_url
        movie.telegram_link = tg_link
        movie.release_year = release_year
        movie.is_home_featured = is_home_featured
        movie.minimum_tier = minimum_tier
        if minimum_tier in ['premium', 'vip']:
            movie.is_premium = True
        else:
            movie.is_premium = False
        movie.home_featured_order = home_featured_order
        if cat_id:
            movie.category = Category.objects.get(id=cat_id)
        if image:
            movie.image = image
        if video_file:
            movie.video_file = video_file
        if hero_media:
            movie.hero_media = hero_media
            
        try:
            movie.save()
        except Exception:
            err_msg = "Fayl yuklanmadi. Rasm yoki video formatini tekshirib, qayta urinib ko'ring."
            if _is_ajax(request):
                return JsonResponse({'ok': False, 'error': err_msg}, status=400)
            messages.error(request, err_msg)
            return render(request, 'custom_admin/movie_form.html', {'movie': movie, 'genres': genres})

        if _is_ajax(request):
            return JsonResponse({'ok': True, 'redirect_url': reverse('admin_movies')})

        messages.success(request, "Anime muvaffaqiyatli saqlandi!")
        return redirect('admin_movies')
        
    return render(request, 'custom_admin/movie_form.html', {'movie': movie, 'genres': genres})

@user_passes_test(is_admin, login_url='/')
def admin_movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    messages.success(request, "Anime o'chirildi!")
    return redirect('admin_movies')

@user_passes_test(is_admin, login_url='/')
def admin_episodes(request):
    episodes_qs = MovieEpisode.objects.select_related('movie').order_by('-created_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Qismlar (Epizodlar)',
        'items': episodes_qs,
        'type': 'episode'
    })

@user_passes_test(is_admin, login_url='/')
def admin_episode_form(request, pk=None):
    episode = get_object_or_404(MovieEpisode, pk=pk) if pk else None
    movies = Movie.objects.all().order_by('-created_at')
    if request.method == 'POST':
        movie_id = request.POST.get('movie')
        ep_num = request.POST.get('episode_number')
        title = request.POST.get('title')
        vid_url = request.POST.get('video_url')
        description = request.POST.get('description')
        video_file = request.FILES.get('video_file')

        if not episode:
            episode = MovieEpisode()
        
        episode.movie = Movie.objects.get(id=movie_id)
        episode.episode_number = ep_num
        episode.title = title
        episode.video_url = vid_url
        episode.description = description
        if video_file:
            episode.video_file = video_file
        try:
            episode.save()
        except Exception:
            err_msg = "Video yuklanmadi. Video URL kiriting yoki to'g'ri video formatini yuklang."
            if _is_ajax(request):
                return JsonResponse({'ok': False, 'error': err_msg}, status=400)
            messages.error(request, err_msg)
            return render(request, 'custom_admin/episode_form.html', {'episode': episode, 'movies': movies})

        if _is_ajax(request):
            return JsonResponse({'ok': True, 'redirect_url': reverse('admin_episodes')})
        
        messages.success(request, "Qism muvaffaqiyatli saqlandi!")
        return redirect('admin_episodes')
        
    return render(request, 'custom_admin/episode_form.html', {'episode': episode, 'movies': movies})

@user_passes_test(is_admin, login_url='/')
def admin_episode_delete(request, pk):
    episode = get_object_or_404(MovieEpisode, pk=pk)
    episode.delete()
    messages.success(request, "Qism o'chirildi!")
    return redirect('admin_episodes')

@user_passes_test(is_admin, login_url='/')
def admin_genre_form(request, pk=None):
    genre = get_object_or_404(Category, pk=pk) if pk else None
    if request.method == 'POST':
        name = request.POST.get('name')
        if not genre:
            genre = Category()
        genre.name = name
        genre.save()
        messages.success(request, "Janr muvaffaqiyatli saqlandi!")
        return redirect('admin_genres')
    return render(request, 'custom_admin/genre_form.html', {'genre': genre})

@user_passes_test(is_admin, login_url='/')
def admin_genre_delete(request, pk):
    genre = get_object_or_404(Category, pk=pk)
    genre.delete()
    messages.success(request, "Janr o'chirildi!")
    return redirect('admin_genres')


@user_passes_test(is_admin, login_url='/')
def admin_message_edit(request, pk):
    msg = get_object_or_404(ChatMessage, pk=pk)
    if request.method == 'POST':
        new_message = request.POST.get('message')
        if new_message:
            msg.message = new_message
            msg.edited = True
            msg.save()
            messages.success(request, "Xabar muvaffaqiyatli tahrirlandi!")
            return redirect('admin_chat')
    
    return render(request, 'custom_admin/message_form.html', {'message': msg})


@user_passes_test(is_admin, login_url='/')
def admin_message_delete(request, pk):
    msg = get_object_or_404(ChatMessage, pk=pk)
    msg.delete()
    messages.success(request, "Xabar o'chirildi!")
    return redirect('admin_chat')


@user_passes_test(is_super_admin, login_url='/')
def admin_subscriptions(request):
    receipts = SubscriptionReceipt.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Obuna So\'rovlari',
        'items': receipts,
        'type': 'receipt',
    })


@user_passes_test(is_super_admin, login_url='/')
def admin_subscription_action(request, pk, action):
    from datetime import timedelta
    from django.utils import timezone
    receipt = get_object_or_404(SubscriptionReceipt, pk=pk)
    if action == 'approve':
        receipt.is_approved = True
        receipt.is_rejected = False
        
        vip_user, created = VipUser.objects.get_or_create(user=receipt.user)
        if not vip_user.is_vip or not vip_user.vip_expire:
            vip_user.vip_expire = timezone.now()
        
        # current time is less than expire then add to it, else add to now
        start_time = max(timezone.now(), vip_user.vip_expire) if vip_user.is_vip else timezone.now()
        
        if receipt.plan == '1_month':
            vip_user.vip_expire = start_time + timedelta(days=30)
            if vip_user.tier == 'basic':
                vip_user.tier = 'premium'
        else:
            vip_user.vip_expire = start_time + timedelta(days=365)
            vip_user.tier = 'vip'
        
        vip_user.is_vip = True
        vip_user.save()
        receipt.save()
        messages.success(request, f"{receipt.user.username} ga VIP vaqti qo'shildi! ({receipt.plan})")
        
    elif action == 'reject':
        receipt.is_approved = False
        receipt.is_rejected = True
        receipt.save()
        messages.error(request, f"{receipt.user.username} obunasi rad etildi!")
        
    return redirect('admin_subscriptions')


@user_passes_test(is_admin, login_url='/')
def admin_avatars(request):
    avatars = ProfileAvatar.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Profil Rasmlari (Avatarlar)',
        'items': avatars,
        'type': 'avatar',
    })

@user_passes_test(is_admin, login_url='/')
def admin_avatar_form(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        if image:
            ProfileAvatar.objects.create(name=name, image=image)
            messages.success(request, "Avatar muvaffaqiyatli saqlandi!")
        else:
            messages.error(request, "Rasm kiritilmadi!")
        return redirect('admin_avatars')

    return render(request, 'custom_admin/avatar_form.html')

@user_passes_test(is_admin, login_url='/')
def admin_avatar_delete(request, pk):
    avatar = get_object_or_404(ProfileAvatar, pk=pk)
    avatar.delete()
    messages.success(request, "Avatar o'chirildi!")
    return redirect('admin_avatars')
