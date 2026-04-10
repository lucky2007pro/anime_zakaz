# urls.py
from django.urls import path
from .views import (
    register, login, home, movie_detail, check_username,
    profile, make_vip, search, anime_catalog,
    chat, chat_messages_api, edit_message, delete_message, ban_user,
    logout_view, premium_page
)
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
    path('premium/', premium_page, name='premium_page'),

    path('chat/', chat, name='chat'),
    path('chat/messages/', chat_messages_api, name='chat_messages_api'),
    path('ban_user/<int:user_id>/', ban_user, name='ban_user'),
    path('edit_message/<int:message_id>/', edit_message, name='edit_message'),
    path('delete_message/<int:message_id>/', delete_message, name='delete_message'),
    path('make-vip/<int:user_id>/',make_vip, name='make_vip'),

    # Admin Panel
    path('control-panel/', admin_dashboard, name='admin_dashboard'),
    path('control-panel/users/', admin_users, name='admin_users'),
    path('control-panel/users/<int:user_id>/role/', admin_user_role, name='admin_user_role'),
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
    path('control-panel/chat/edit/<int:pk>/', admin_message_edit, name='admin_message_edit'),
    path('control-panel/chat/delete/<int:pk>/', admin_message_delete, name='admin_message_delete'),
    
    path('control-panel/subscriptions/', admin_subscriptions, name='admin_subscriptions'),
    path('control-panel/subscriptions/<int:pk>/<str:action>/', admin_subscription_action, name='admin_subscription_action'),
    path('control-panel/avatars/', admin_avatars, name='admin_avatars'),
    path('control-panel/avatars/add/', admin_avatar_form, name='admin_avatar_form'),
    path('control-panel/avatars/<int:pk>/delete/', admin_avatar_delete, name='admin_avatar_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
