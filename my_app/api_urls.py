from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import api_views

urlpatterns = [
    # Auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', api_views.RegisterAPIView.as_view(), name='api_register'),
    path('user/', api_views.CurrentUserView.as_view(), name='api_user'),
    path('user-settings/', api_views.UserSettingsAPIView.as_view(), name='api_user_settings'),
    
    # Movies & Categories
    path('movies/', api_views.MovieListView.as_view(), name='api_movies'),
    path('movies/<int:pk>/', api_views.MovieDetailView.as_view(), name='api_movie_detail'),
    path('hero-movies/', api_views.HeroMovieListView.as_view(), name='api_hero_movies'),
    path('categories/', api_views.CategoryListView.as_view(), name='api_categories'),
    
    path('movies/<int:pk>/comments/', api_views.MovieCommentListView.as_view(), name='api_movie_comments'),
    path('movies/<int:pk>/comment/', api_views.AddMovieCommentView.as_view(), name='api_add_movie_comment'),

    # Reels
    path('reels/', api_views.ReelListView.as_view(), name='api_reels'),
    path('reels/<int:pk>/like/', api_views.ToggleReelLikeView.as_view(), name='api_reel_like'),
    path('reels/<int:pk>/comment/', api_views.AddReelCommentView.as_view(), name='api_add_reel_comment'),
    path('reels/<int:pk>/comments/', api_views.ReelCommentListView.as_view(), name='api_reel_comments'),

    # Other Content
    path('stories/', api_views.StoryListView.as_view(), name='api_stories'),
    path('news/', api_views.AnimeNewsListView.as_view(), name='api_news'),
    path('schedule/', api_views.AnimeScheduleListView.as_view(), name='api_schedule'),

    # User Interactions
    path('history/', api_views.WatchHistoryListView.as_view(), name='api_history'),
    path('history/<int:pk>/add/', api_views.AddWatchHistoryView.as_view(), name='api_add_history'),
    path('favorites/', api_views.FavoriteAnimeListView.as_view(), name='api_favorites'),
    path('favorites/<int:pk>/toggle/', api_views.ToggleFavoriteView.as_view(), name='api_toggle_favorite'),

    # Chat
    path('chat/', api_views.ChatListView.as_view(), name='api_chat_list'),
    path('chat/add/', api_views.AddChatView.as_view(), name='api_chat_add'),

    # Settings
    path('site-settings/', api_views.SiteSettingsAPIView.as_view(), name='api_site_settings'),
]
