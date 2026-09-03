from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .models import *
from django.db.models import F
from django.utils import timezone as tz_utils


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
        rating = request.POST.get('rating', '').strip()
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
        movie.rating = rating or None
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
        intro_time = request.POST.get('intro_time')
        video_file = request.FILES.get('video_file')


        if not episode:
            episode = MovieEpisode()
        
        episode.movie = Movie.objects.get(id=movie_id)
        episode.episode_number = ep_num
        episode.title = title
        episode.video_url = vid_url
        episode.description = description
        episode.intro_time = intro_time
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


@user_passes_test(is_admin, login_url='/')
def admin_comments(request):
    comments_qs = MovieComment.objects.select_related('movie', 'user').all().order_by('-created_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Animelarga izohlar',
        'items': comments_qs,
        'type': 'comment'
    })


@user_passes_test(is_admin, login_url='/')
def admin_comment_edit(request, pk):
    comment = get_object_or_404(MovieComment, pk=pk)
    if request.method == 'POST':
        new_text = request.POST.get('text')
        if new_text:
            comment.text = new_text
            comment.save()
            messages.success(request, "Izoh muvaffaqiyatli tahrirlandi!")
            return redirect('admin_comments')
    
    return render(request, 'custom_admin/comment_form.html', {'comment': comment})


@user_passes_test(is_admin, login_url='/')
def admin_comment_delete(request, pk):
    comment = get_object_or_404(MovieComment, pk=pk)
    comment.delete()
    messages.success(request, "Izoh o'chirildi!")
    return redirect('admin_comments')



# =======================
# ANIME SCHEDULE
# =======================
@user_passes_test(is_admin, login_url='/')
def admin_schedule(request):
    schedules = AnimeSchedule.objects.all().order_by('order', '-created_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Anime Jadvali',
        'items': schedules,
        'type': 'schedule'
    })


@user_passes_test(is_admin, login_url='/')
def admin_schedule_form(request, pk=None):
    schedule = get_object_or_404(AnimeSchedule, pk=pk) if pk else None
    if request.method == 'POST':
        if not schedule:
            schedule = AnimeSchedule()
        schedule.name           = request.POST.get('name', '').strip()
        schedule.subtitle       = request.POST.get('subtitle', '').strip()
        schedule.image_url      = request.POST.get('image_url', '').strip()
        schedule.day            = request.POST.get('day', '')
        schedule.fandub         = request.POST.get('fandub', 'AniBest').strip()
        schedule.watch_url      = request.POST.get('watch_url', '').strip()
        schedule.is_active      = request.POST.get('is_active') == 'on'
        try:
            schedule.episode_number = int(request.POST.get('episode_number', 1))
            schedule.order          = int(request.POST.get('order', 0))
        except (TypeError, ValueError):
            schedule.episode_number = 1
            schedule.order = 0
        schedule.save()
        messages.success(request, "Jadval muvaffaqiyatli saqlandi!")
        return redirect('admin_schedule')
    return render(request, 'custom_admin/schedule_form.html', {
        'schedule': schedule,
        'day_choices': AnimeSchedule.DAY_CHOICES,
    })


@user_passes_test(is_admin, login_url='/')
def admin_schedule_delete(request, pk):
    schedule = get_object_or_404(AnimeSchedule, pk=pk)
    schedule.delete()
    messages.success(request, "Jadval o'chirildi!")
    return redirect('admin_schedule')


# =======================
# STORY
# =======================
@user_passes_test(is_admin, login_url='/')
def admin_stories(request):
    stories = Story.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Storylar',
        'items': stories,
        'type': 'story'
    })


@user_passes_test(is_admin, login_url='/')
def admin_story_form(request, pk=None):
    story = get_object_or_404(Story, pk=pk) if pk else None
    if request.method == 'POST':
        if not story:
            story = Story()
        story.title       = request.POST.get('title', '').strip()
        story.description = request.POST.get('description', '').strip()
        story.link        = request.POST.get('link', '').strip() or None
        story.is_active   = request.POST.get('is_active') == 'on'

        expires_at = request.POST.get('expires_at', '').strip()
        if expires_at:
            from django.utils.dateparse import parse_datetime
            story.expires_at = parse_datetime(expires_at)
        else:
            story.expires_at = None

        if request.FILES.get('image'):
            story.image = request.FILES['image']
        if request.FILES.get('video'):
            story.video = request.FILES['video']

        story.save()
        messages.success(request, "Story muvaffaqiyatli saqlandi!")
        return redirect('admin_stories')
    return render(request, 'custom_admin/story_form.html', {'story': story})


@user_passes_test(is_admin, login_url='/')
def admin_story_delete(request, pk):
    story = get_object_or_404(Story, pk=pk)
    story.delete()
    messages.success(request, "Story o'chirildi!")
    return redirect('admin_stories')


@user_passes_test(is_admin, login_url='/')
def admin_story_views(request, pk):
    story = get_object_or_404(Story, pk=pk)
    views = StoryView.objects.filter(story=story).select_related('user').order_by('-viewed_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': f'"{story.title}" — Ko\'rishlar',
        'items': views,
        'type': 'storyview'
    })


# =======================
# ANIME NEWS
# =======================
@user_passes_test(is_admin, login_url='/')
def admin_news(request):
    news_list = AnimeNews.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Yangiliklar',
        'items': news_list,
        'type': 'news'
    })


@user_passes_test(is_admin, login_url='/')
def admin_news_form(request, pk=None):
    news = get_object_or_404(AnimeNews, pk=pk) if pk else None
    if request.method == 'POST':
        if not news:
            news = AnimeNews()
        news.title       = request.POST.get('title', '').strip()
        news.description = request.POST.get('description', '').strip()
        news.link        = request.POST.get('link', '').strip() or None
        news.author      = request.user

        if request.FILES.get('image'):
            news.image = request.FILES['image']
        if request.FILES.get('video'):
            news.video = request.FILES['video']

        news.save()
        messages.success(request, "Yangilik muvaffaqiyatli saqlandi!")
        return redirect('admin_news')
    return render(request, 'custom_admin/news_form.html', {'news': news})


@user_passes_test(is_admin, login_url='/')
def admin_news_delete(request, pk):
    news = get_object_or_404(AnimeNews, pk=pk)
    news.delete()
    messages.success(request, "Yangilik o'chirildi!")
    return redirect('admin_news')


@user_passes_test(is_admin, login_url='/')
def admin_news_likes(request, pk):
    news = get_object_or_404(AnimeNews, pk=pk)
    likes = NewsLike.objects.filter(news=news).select_related('user').order_by('-created_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': f'"{news.title}" — Likelar ({likes.count()})',
        'items': likes,
        'type': 'newslike'
    })

# =======================
# ANIME SECTION ITEM (Kunlik anime / Anime film)
# =======================
@user_passes_test(is_admin, login_url='/')
def admin_sections(request):
    items = AnimeSectionItem.objects.select_related('movie').order_by('section', 'order')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': "Kategoriya bo'limlari (Kunlik/Film)",
        'items': items,
        'type': 'section'
    })


@user_passes_test(is_admin, login_url='/')
def admin_section_form(request, pk=None):
    item = get_object_or_404(AnimeSectionItem, pk=pk) if pk else None
    movies = Movie.objects.all().order_by('title')
    if request.method == 'POST':
        if not item:
            item = AnimeSectionItem()
        item.section = request.POST.get('section', 'daily')
        movie_id = request.POST.get('movie')
        try:
            item.order = int(request.POST.get('order', 0))
        except (TypeError, ValueError):
            item.order = 0

        if movie_id:
            item.movie = Movie.objects.get(id=movie_id)

        try:
            item.save()
        except Exception:
            messages.error(request, "Bu anime shu bo'limda allaqachon mavjud yoki xatolik yuz berdi.")
            return render(request, 'custom_admin/section_form.html', {
                'item': item,
                'movies': movies,
                'section_choices': AnimeSectionItem.SECTION_CHOICES,
            })

        messages.success(request, "Bo'lim muvaffaqiyatli saqlandi!")
        return redirect('admin_sections')

    return render(request, 'custom_admin/section_form.html', {
        'item': item,
        'movies': movies,
        'section_choices': AnimeSectionItem.SECTION_CHOICES,
    })


@user_passes_test(is_admin, login_url='/')
def admin_section_delete(request, pk):
    item = get_object_or_404(AnimeSectionItem, pk=pk)
    item.delete()
    messages.success(request, "Bo'lim elementi o'chirildi!")
    return redirect('admin_sections')

# =======================
# NOTICE (E'lonlar)
# =======================
@user_passes_test(is_admin, login_url='/')
def admin_notices(request):
    notices = Notice.objects.all().order_by('-created_at')
    push_subscribers_count = PushSubscription.objects.count()
    unique_push_users = PushSubscription.objects.values('user').distinct().count()
    total_users_count = CustomUser.objects.count()

    return render(request, 'custom_admin/list_base.html', {
        'page_title': "E'lonlar",
        'items': notices,
        'type': 'notice',
        'push_subscribers_count': push_subscribers_count,
        'unique_push_users': unique_push_users,
        'total_users_count': total_users_count,
    })


@user_passes_test(is_admin, login_url='/')
def admin_notice_form(request, pk=None):
    notice = get_object_or_404(Notice, pk=pk) if pk else None
    push_subscribers_count = PushSubscription.objects.count()
    unique_push_users = PushSubscription.objects.values('user').distinct().count()
    total_users_count = CustomUser.objects.count()

    if request.method == 'POST':
        is_new = notice is None
        if not notice:
            notice = Notice()
        notice.title = request.POST.get('title', '').strip()
        notice.message = request.POST.get('message', '').strip()
        notice.notice_type = 'admin'          # <-- doim 'admin', forma orqali o'zgartirilmaydi
        notice.target_user = None             # <-- hammaga ko'rinishi uchun bo'sh
        notice.created_by = request.user
        notice.is_active = request.POST.get('is_active') == 'on' or 'is_active' in request.POST
        notice.save()

        send_push = request.POST.get('send_push') == 'on' or 'send_push' in request.POST or is_new
        sent_count = 0
        if notice.is_active and send_push:
            try:
                from .views import send_broadcast_push_notification
                sent_count = send_broadcast_push_notification(
                    title=notice.title or "BESTMEDIA E'lon",
                    body=notice.message[:150],
                    url='/notice/'
                )
            except Exception as e:
                print("admin_notice_form push xatosi:", e)

        if sent_count > 0:
            messages.success(request, f"E'lon muvaffaqiyatli saqlandi va {sent_count} ta foydalanuvchi qurilmasiga Push bildirishnoma yuborildi!")
        else:
            messages.success(request, "E'lon muvaffaqiyatli saqlandi!")
        return redirect('admin_notices')

    return render(request, 'custom_admin/notice_form.html', {
        'notice': notice,
        'push_subscribers_count': push_subscribers_count,
        'unique_push_users': unique_push_users,
        'total_users_count': total_users_count,
    })

@user_passes_test(is_admin, login_url='/')
def admin_notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.delete()
    messages.success(request, "E'lon o'chirildi!")
    return redirect('admin_notices')

# =======================
# ANIME HAQIDA (about_info)
# =======================
@user_passes_test(is_admin, login_url='/')
def admin_animehaqida_form(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == 'POST':
        movie.about_info = request.POST.get('about_info', '').strip()
        movie.save(update_fields=['about_info'])
        messages.success(request, "Anime haqida ma'lumot saqlandi!")
        return redirect('admin_movies')

    return render(request, 'custom_admin/animehaqida_form.html', {'movie': movie})


# =======================
# ANIME KADRLAR (frames)
# =======================
@user_passes_test(is_admin, login_url='/')
def admin_kadrlar_form(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    frames = movie.frames.all().order_by('order', 'created_at')

    if request.method == 'POST':
        if frames.count() >= 5:
            messages.error(request, "Bitta anime uchun maksimal 5 ta kadr yuklash mumkin.")
            return redirect('admin_kadrlar_form', movie_id=movie.id)

        image = request.FILES.get('image')
        if not image:
            messages.error(request, "Rasm tanlanmadi!")
            return redirect('admin_kadrlar_form', movie_id=movie.id)

        try:
            order = int(request.POST.get('order', 0))
        except (TypeError, ValueError):
            order = 0

        MovieFrame.objects.create(movie=movie, image=image, order=order)
        messages.success(request, "Kadr muvaffaqiyatli qo'shildi!")
        return redirect('admin_kadrlar_form', movie_id=movie.id)

    return render(request, 'custom_admin/kadrlar_form.html', {
        'movie': movie,
        'frames': frames,
    })


@user_passes_test(is_admin, login_url='/')
def admin_kadrlar_delete(request, pk):
    frame = get_object_or_404(MovieFrame, pk=pk)
    movie_id = frame.movie_id
    frame.delete()
    messages.success(request, "Kadr o'chirildi!")
    return redirect('admin_kadrlar_form', movie_id=movie_id)


# =======================
# JACKPOT KODLAR (ADMIN)
# =======================
@user_passes_test(is_admin, login_url='/')
def admin_jackpot_list(request):
    codes = JackpotCode.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Jackpot kodlar',
        'items': codes,
        'type': 'jackpot'
    })


@user_passes_test(is_admin, login_url='/')
def admin_jackpot_form(request, pk=None):
    jackpot = get_object_or_404(JackpotCode, pk=pk) if pk else None

    if request.method == 'POST':
        if not jackpot:
            jackpot = JackpotCode()

        jackpot.code = request.POST.get('code', '').strip()
        jackpot.reward_type = request.POST.get('reward_type', 'balance')

        def _to_int(name):
            try:
                return int(request.POST.get(name, 0) or 0)
            except (TypeError, ValueError):
                return 0

        jackpot.vip_hours = _to_int('vip_hours')
        jackpot.vip_days = _to_int('vip_days')
        jackpot.balance_amount = _to_int('balance_amount')
        jackpot.max_uses = _to_int('max_uses')

        expires_at = request.POST.get('expires_at', '').strip()
        if expires_at:
            from django.utils.dateparse import parse_datetime
            jackpot.expires_at = parse_datetime(expires_at)
        else:
            jackpot.expires_at = None

        jackpot.is_active = request.POST.get('is_active') == 'on'

        if not jackpot.created_by_id:
            jackpot.created_by = request.user

        try:
            jackpot.save()
        except Exception:
            messages.error(request, "Bu kod allaqachon mavjud yoki xatolik yuz berdi.")
            return render(request, 'custom_admin/jackpot_form.html', {
                'jackpot': jackpot,
                'reward_choices': JackpotCode.REWARD_CHOICES,
            })

        messages.success(request, "Jackpot kod muvaffaqiyatli saqlandi!")
        return redirect('admin_jackpot_form', pk=jackpot.pk)

    uses = jackpot.uses.select_related('user').order_by('-used_at') if jackpot else []

    return render(request, 'custom_admin/jackpot_form.html', {
        'jackpot': jackpot,
        'reward_choices': JackpotCode.REWARD_CHOICES,
        'uses': uses,
    })


@user_passes_test(is_admin, login_url='/')
def admin_jackpot_delete(request, pk):
    jackpot = get_object_or_404(JackpotCode, pk=pk)
    jackpot.delete()
    messages.success(request, "Jackpot kod o'chirildi!")
    return redirect('admin_jackpot_list')


@user_passes_test(is_admin, login_url='/')
def admin_jackpot_cancel_user(request, pk):
    """Bitta foydalanuvchining shu koddan foydalanishini ID orqali bekor qilish."""
    jackpot = get_object_or_404(JackpotCode, pk=pk)
    if request.method != 'POST':
        return redirect('admin_jackpot_form', pk=pk)

    user_id = request.POST.get('user_id', '').strip()
    if not user_id.isdigit():
        messages.error(request, "Foydalanuvchi ID noto'g'ri kiritildi.")
        return redirect('admin_jackpot_form', pk=jackpot.pk)

    use = JackpotCodeUse.objects.filter(code=jackpot, user_id=user_id).first()
    if use:
        use.delete()
        messages.success(request, f"#{user_id} ID li foydalanuvchi uchun jackpot bekor qilindi. U kodni qayta ishlata oladi.")
    else:
        messages.error(request, f"#{user_id} ID li foydalanuvchi bu koddan foydalanmagan.")
    return redirect('admin_jackpot_form', pk=jackpot.pk)


# =======================
# HISOBIM BOSHQARUVI (BALANS)
# =======================
@user_passes_test(is_admin, login_url='/')
def admin_hisob_list(request):
    balances = UserBalance.objects.select_related('user').order_by('-amount')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': "Foydalanuvchilar hisobi",
        'items': balances,
        'type': 'hisob'
    })


@user_passes_test(is_admin, login_url='/')
def admin_hisob_form(request, user_id=None):
    target_user = None
    balance = None
    history = []

    lookup_id = user_id or request.GET.get('user_id', '').strip()
    if lookup_id:
        target_user = CustomUser.objects.filter(id=lookup_id).first()
        if target_user:
            balance, _ = UserBalance.objects.get_or_create(user=target_user)
            history = AccountHistory.objects.filter(user=target_user).order_by('-created_at')[:30]
        else:
            messages.error(request, f"#{lookup_id} ID li foydalanuvchi topilmadi.")

    if request.method == 'POST':
        uid = request.POST.get('user_id', '').strip()
        action = request.POST.get('action')
        try:
            amount = int(request.POST.get('amount', 0))
        except (TypeError, ValueError):
            amount = 0

        target_user = CustomUser.objects.filter(id=uid).first()
        if not target_user:
            messages.error(request, f"#{uid} ID li foydalanuvchi topilmadi.")
            return redirect('admin_hisob_form_lookup')

        balance, _ = UserBalance.objects.get_or_create(user=target_user)

        if amount <= 0:
            messages.error(request, "To'g'ri summa kiriting.")
            return redirect('admin_hisob_form', user_id=target_user.id)

        if action == 'toldirish':
            UserBalance.objects.filter(user=target_user).update(amount=F('amount') + amount)
            AccountHistory.objects.create(
                user=target_user,
                text=f"Admin tomonidan hisobingiz {amount:,} so'm ga to'ldirildi".replace(',', '.')
            )
            messages.success(request, f"{target_user.username} hisobiga {amount:,} so'm qo'shildi.".replace(',', '.'))
        elif action == 'yechish':
            balance.refresh_from_db()
            if balance.amount < amount:
                messages.error(request, "Foydalanuvchi hisobida yetarli mablag' yo'q.")
                return redirect('admin_hisob_form', user_id=target_user.id)
            UserBalance.objects.filter(user=target_user).update(amount=F('amount') - amount)
            AccountHistory.objects.create(
                user=target_user,
                text=f"Admin tomonidan hisobingizdan {amount:,} so'm yechib olindi".replace(',', '.')
            )
            messages.success(request, f"{target_user.username} hisobidan {amount:,} so'm yechildi.".replace(',', '.'))
        else:
            messages.error(request, "Noto'g'ri amal.")

        return redirect('admin_hisob_form', user_id=target_user.id)

    return render(request, 'custom_admin/hisob_form.html', {
        'target_user': target_user,
        'balance': balance,
        'history': history,
    })


# =======================
# QARZ SO'ROVLARI (ADMIN)
# =======================
@user_passes_test(is_admin, login_url='/')
def admin_qarz_list(request):
    debts = DebtRequest.objects.select_related('user').order_by('-created_at')
    return render(request, 'custom_admin/qarz_tastiq_form.html', {
        'page_title': "Qarz so'rovlari",
        'debts': debts,
    })


@user_passes_test(is_admin, login_url='/')
def admin_qarz_tasdiqlash(request, pk):
    debt = get_object_or_404(DebtRequest, pk=pk)
    if debt.status != 'pending':
        messages.error(request, "Bu so'rov allaqachon ko'rib chiqilgan.")
        return redirect('admin_qarz_list')

    UserBalance.objects.get_or_create(user=debt.user)
    UserBalance.objects.filter(user=debt.user).update(amount=F('amount') + debt.amount)
    debt.status = 'approved'
    debt.processed_at = tz_utils.now()
    debt.save()
    AccountHistory.objects.create(
        user=debt.user,
        text=f"{debt.amount:,} so'm qarz so'rovi tasdiqlandi, hisobingizga qo'shildi".replace(',', '.')
    )
    messages.success(request, f"{debt.user.username} uchun qarz so'rovi tasdiqlandi.")
    return redirect('admin_qarz_list')


@user_passes_test(is_admin, login_url='/')
def admin_qarz_rad(request, pk):
    debt = get_object_or_404(DebtRequest, pk=pk)
    if debt.status != 'pending':
        messages.error(request, "Bu so'rov allaqachon ko'rib chiqilgan.")
        return redirect('admin_qarz_list')

    debt.status = 'rejected'
    debt.processed_at = tz_utils.now()
    debt.save()
    AccountHistory.objects.create(
        user=debt.user,
        text=f"{debt.amount:,} so'm qarz so'rovi rad etildi".replace(',', '.')
    )
    messages.success(request, f"{debt.user.username} uchun qarz so'rovi rad etildi.")
    return redirect('admin_qarz_list')



# =======================
# REELBEST (ADMIN)
# =======================
@user_passes_test(is_admin, login_url='/')
def admin_reelbest_list(request):
    reels = ReelBest.objects.select_related('user', 'movie').order_by('-created_at')
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'ReelBest',
        'items': reels,
        'type': 'reelbest'
    })


@user_passes_test(is_admin, login_url='/')
def admin_reelbest_form(request, pk=None):
    reel = get_object_or_404(ReelBest, pk=pk) if pk else None
    movies = Movie.objects.all().order_by('title')

    if request.method == 'POST':
        if not reel:
            reel = ReelBest()

        reel.title = request.POST.get('title', '').strip() or None
        reel.description = request.POST.get('description', '').strip() or None

        movie_id = request.POST.get('movie')
        reel.movie = Movie.objects.get(id=movie_id) if movie_id else None

        video_url = request.POST.get('video_url', '').strip()
        reel.video_url = video_url or None

        if not reel.user_id:
            reel.user = request.user

        video_file = request.FILES.get('video_file')
        thumbnail = request.FILES.get('thumbnail')
        if video_file:
            reel.video_file = video_file
        if thumbnail:
            reel.thumbnail = thumbnail

        try:
            reel.save()
        except Exception:
            err_msg = "Video yuklanmadi. Video URL kiriting yoki to'g'ri video formatini yuklang."
            if _is_ajax(request):
                return JsonResponse({'ok': False, 'error': err_msg}, status=400)
            messages.error(request, err_msg)
            return render(request, 'custom_admin/reelbest_form.html', {'reel': reel, 'movies': movies})

        if _is_ajax(request):
            return JsonResponse({'ok': True, 'redirect_url': reverse('admin_reelbest_list')})

        messages.success(request, "ReelBest muvaffaqiyatli saqlandi!")
        return redirect('admin_reelbest_list')

    return render(request, 'custom_admin/reelbest_form.html', {'reel': reel, 'movies': movies})


@user_passes_test(is_admin, login_url='/')
def admin_reelbest_delete(request, pk):
    reel = get_object_or_404(ReelBest, pk=pk)
    reel.delete()
    messages.success(request, "ReelBest o'chirildi!")
    return redirect('admin_reelbest_list')


# =======================
# PREMIUM AZOLAR (VIP RO'YXATI)
# =======================
@user_passes_test(is_admin, login_url='/')
def admin_premium_list(request):
    vip_users = VipUser.objects.filter(is_vip=True).select_related('user').order_by('-vip_expire')
    total_vip = vip_users.count()
    return render(request, 'custom_admin/list_base.html', {
        'page_title': 'Premium azolar',
        'items': vip_users,
        'type': 'premium',
        'total_vip': total_vip,
    })


@user_passes_test(is_admin, login_url='/')
def admin_premium_form(request, pk):
    vip = get_object_or_404(VipUser, pk=pk)

    if request.method == 'POST':
        vip.tier = request.POST.get('tier', vip.tier)
        vip.is_vip = request.POST.get('is_vip') == 'on'

        expires_at = request.POST.get('vip_expire', '').strip()
        if expires_at:
            from django.utils.dateparse import parse_datetime
            vip.vip_expire = parse_datetime(expires_at)
        else:
            vip.vip_expire = None

        vip.save()
        messages.success(request, f"{vip.user.username} uchun obuna ma'lumotlari yangilandi!")
        return redirect('admin_premium_list')

    return render(request, 'custom_admin/premium_form.html', {'vip': vip})


@user_passes_test(is_admin, login_url='/')
def admin_premium_cancel(request, pk):
    vip = get_object_or_404(VipUser, pk=pk)
    vip.is_vip = False
    vip.tier = 'basic'
    vip.vip_expire = None
    vip.save()
    messages.success(request, f"{vip.user.username} obunasi bekor qilindi!")
    return redirect('admin_premium_list')
