from rest_framework import serializers
from .models import (
    Movie, Category, MovieEpisode, ReelBest, CustomUser, AnimeNews, Story, 
    FavoriteAnime, WatchHistory, ReelBestComment, MovieComment, AnimeSchedule, 
    ChatMessage, SiteSettings, UserSettings
)

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['theme', 'bg_color', 'bg_color_custom', 'tabbar_on']

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class MovieEpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieEpisode
        fields = ['id', 'episode_number', 'title', 'video_url', 'video_file', 'description']

class MovieListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Movie
        fields = ['id', 'title', 'image', 'is_premium', 'minimum_tier', 'category_name', 'views_count']

class MovieDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    episodes = MovieEpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = '__all__'

class ReelSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    video_src = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = ReelBest
        fields = ['id', 'user_name', 'title', 'description', 'video_src', 'thumbnail', 'views_count', 'total_likes', 'total_comments', 'is_liked', 'created_at']
    def get_video_src(self, obj):
        return obj.get_video_src()

    def get_total_likes(self, obj):
        return obj.total_likes()

    def get_total_comments(self, obj):
        return obj.total_comments()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

class CustomUserSerializer(serializers.ModelSerializer):
    tier = serializers.CharField(source='active_tier', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'tier', 'avatar']

    def get_avatar(self, obj):
        if obj.avatar and obj.avatar.image:
            return obj.avatar.image.url
        return None

class AnimeNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimeNews
        fields = '__all__'

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id', 'image', 'video', 'link', 'expires_at', 'created_at']

class FavoriteAnimeSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)

    class Meta:
        model = FavoriteAnime
        fields = ['id', 'movie', 'created_at']

class WatchHistorySerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)

    class Meta:
        model = WatchHistory
        fields = ['id', 'movie', 'last_watched']

class ReelCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()

    class Meta:
        model = ReelBestComment
        fields = ['id', 'user_name', 'user_avatar', 'text', 'created_at', 'reply_to']
        
    def get_user_avatar(self, obj):
        if obj.user.avatar and obj.user.avatar.image:
            return obj.user.avatar.image.url
        return None

class MovieCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()

    class Meta:
        model = MovieComment
        fields = ['id', 'user_name', 'user_avatar', 'text', 'created_at']

    def get_user_avatar(self, obj):
        if obj.user.avatar and obj.user.avatar.image:
            return obj.user.avatar.image.url
        return None

class AnimeScheduleSerializer(serializers.ModelSerializer):
    anime_title = serializers.CharField(source='name', read_only=True)
    anime_image = serializers.URLField(source='image_url', read_only=True)
    day_of_week = serializers.CharField(source='day', read_only=True)

    class Meta:
        model = AnimeSchedule
        fields = ['id', 'anime_title', 'anime_image', 'day_of_week', 'episode_number', 'fandub']

class ChatMessageSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    is_vip = serializers.SerializerMethodField()
    is_premium = serializers.SerializerMethodField()
    is_admin = serializers.BooleanField(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'user_name', 'user_avatar', 'is_vip', 'is_premium', 'is_admin', 'message', 'created_at']

    def get_user_avatar(self, obj):
        if obj.user.avatar and obj.user.avatar.image:
            return obj.user.avatar.image.url
        return None

    def get_is_vip(self, obj):
        try:
            return obj.user.vip_data.tier == 'vip'
        except Exception:
            return False

    def get_is_premium(self, obj):
        try:
            return obj.user.vip_data.tier == 'premium'
        except Exception:
            return False
