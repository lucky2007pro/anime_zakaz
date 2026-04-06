# urls.py
from django.urls import path
from .views import *
from .admin_views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('login/', login, name='login'),
    path('accounts/login/', login, name='login_legacy'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('movie/<int:id>/', movie_detail, name='movie_detail'),
    path('catalog/', anime_catalog, name='anime_catalog'),
    path('search/', search, name='search'),
    path('profile/', profile, name='profile'),
    path('check-username/', check_username, name='check_username'),

    path('chat/', chat, name='chat'),
    path('ban_user/<int:user_id>/', ban_user, name='ban_user'),
    path('edit_message/<int:message_id>/', edit_message, name='edit_message'),
    path('delete_message/<int:message_id>/', delete_message, name='delete_message'),
    path('make-vip/<int:user_id>/',make_vip, name='make_vip'),

    # Admin Panel
    path('control-panel/', admin_dashboard, name='admin_dashboard'),
    path('control-panel/movies/', admin_movies, name='admin_movies'),
    path('control-panel/movies/add/', admin_movie_form, name='admin_movie_form'),
    path('control-panel/movies/<int:pk>/edit/', admin_movie_form, name='admin_movie_form'),
    path('control-panel/movies/<int:pk>/delete/', admin_movie_delete, name='admin_movie_delete'),
    path('control-panel/genres/', admin_genres, name='admin_genres'),
    path('control-panel/genres/add/', admin_genre_form, name='admin_genre_form'),
    path('control-panel/genres/<int:pk>/edit/', admin_genre_form, name='admin_genre_form'),
    path('control-panel/genres/<int:pk>/delete/', admin_genre_delete, name='admin_genre_delete'),
    path('control-panel/episodes/', admin_episodes, name='admin_episodes'),
    path('control-panel/episodes/add/', admin_episode_form, name='admin_episode_form'),
    path('control-panel/episodes/<int:pk>/edit/', admin_episode_form, name='admin_episode_form'),
    path('control-panel/episodes/<int:pk>/delete/', admin_episode_delete, name='admin_episode_delete'),
    path('control-panel/chat/', admin_chat, name='admin_chat'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
