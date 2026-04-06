from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
from .models import CustomUser, Movie, MovieEpisode, Category, ChatMessage

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.is_admin_user)


def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

@user_passes_test(is_admin, login_url='/')
def admin_dashboard(request):
    context = {
        'total_animes': Movie.objects.count(),
        'total_episodes': MovieEpisode.objects.count(),
        'total_genres': Category.objects.count(),
        'total_users': CustomUser.objects.count(),
        'latest_animes': Movie.objects.all().order_by('-created_at')[:5],
        'latest_users': CustomUser.objects.all().order_by('-date_joined')[:5],
    }
    return render(request, 'custom_admin/dashboard.html', context)

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
        image = request.FILES.get('image')
        video_file = request.FILES.get('video_file')

        if not movie:
            movie = Movie()
        
        movie.title = title
        movie.description = desc
        movie.video_url = vid_url
        movie.telegram_link = tg_link
        if cat_id:
            movie.category = Category.objects.get(id=cat_id)
        if image:
            movie.image = image
        if video_file:
            movie.video_file = video_file
            
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
        video_file = request.FILES.get('video_file')

        if not episode:
            episode = MovieEpisode()
        
        episode.movie = Movie.objects.get(id=movie_id)
        episode.episode_number = ep_num
        episode.title = title
        episode.video_url = vid_url
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
