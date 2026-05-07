from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from zoneinfo import ZoneInfo

# =======================
# CATEGORY
# =======================
class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =======================
# CUSTOM USER
# =======================
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_banned = models.BooleanField(default=False)
    is_admin_user = models.BooleanField(default=False)  # Admin panelga kirish
    avatar = models.ForeignKey('ProfileAvatar', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    def active_tier(self):
        if not hasattr(self, 'vip_data'):
            return 'basic'
        return self.vip_data.get_tier()

    def __str__(self):
        return self.username if self.username else f"User-{self.id}"


class VipUser(models.Model):
    TIER_CHOICES = [
        ('basic', 'Asosiy (Free)'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='vip_data'
    )
    is_vip = models.BooleanField(default=False)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='basic')
    vip_expire = models.DateTimeField(null=True, blank=True)

    def vip_active(self):
        return self.is_vip and self.vip_expire and self.vip_expire > timezone.now()

    def get_tier(self):
        if not self.vip_active():
            return 'basic'
        return self.tier

    def has_access(self, required_tier):
        current = self.get_tier()
        tiers = ['basic', 'premium', 'vip']
        return tiers.index(current) >= tiers.index(required_tier)

    def __str__(self):
        return f"{self.user.username} - VIP"if self.user.username else f"User-{self.user.id} - VIP"


# =======================
# MOVIE
# =======================
class Movie(models.Model):
    TIER_CHOICES = [
        ('basic', 'Asosiy (Free)'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='movies/')
    description = models.TextField(blank=True, null=True)
    is_premium = models.BooleanField(
        default=False, 
        help_text="Faqat premium obunachilar ko'ra oladi (Eski tizim)"
    )
    minimum_tier = models.CharField(
        max_length=10, 
        choices=TIER_CHOICES, 
        default='basic',
        help_text="Qaysi tarifdan boshlab ko'rish mumkin"
    )
    is_home_featured = models.BooleanField(
        default=False,
        help_text="Bosh sahifa hero fonida ko'rsatish uchun belgilang"
    )
    home_featured_order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Kichik raqam avval ko'rsatiladi"
    )
    hero_media = models.FileField(
        upload_to='movies/hero/',
        blank=True,
        null=True,
        help_text="Bosh sahifa slideri uchun maxsus rasm yoki video (Ixtiyoriy)"
    )

    views_count = models.PositiveIntegerField(default=0, help_text="Umumiy ko'rishlar soni")
    release_year = models.CharField(max_length=20, blank=True, null=True, help_text="Chiqarilgan yili, masalan: 2026")

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movies"
    )

    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="Asosiy video URL (mp4 yoki CDN linki)"
    )

    video_file = models.FileField(
        upload_to='movies/videos/',
        blank=True,
        null=True,
        help_text="Yoki video faylni yuklang (mp4, mkv va b.)"
    )

    telegram_link = models.URLField(
        blank=True,
        null=True,
        help_text="Telegram post linki (ixtiyoriy, agar mavjud bo'lsa saytda ko'rinadi)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =======================
# MOVIE EPISODES
# =======================
class MovieEpisode(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True, null=True, help_text="Bunny.net iframe yoki mp4 linkini yozing")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True, help_text="Yoki video faylni yuklang (mp4, mkv va b.)")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['episode_number']  # Episode raqam bo‘yicha tartiblanadi

    def __str__(self):
        return f"{self.movie.title} - {self.episode_number}-qism - {self.title}"


# =======================
# SITE SETTINGS
# =======================
class SiteSettings(models.Model):
    background_video = models.FileField(
        upload_to='backgrounds/',
        blank=True,
        null=True
    )
    background_image = models.ImageField(
        upload_to='backgrounds/',
        blank=True,
        null=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Sayt Sozlamalari"


# =======================
# MP3 FILES
# =======================
class MP3(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='mp3/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =======================
# CHAT MESSAGES
# =======================
class ChatMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )

    def local_created_at(self):
        """Vaqtni Tashkent timezone ga o‘giradi"""
        from django.utils.timezone import localtime
        uz_time = ZoneInfo('Asia/Tashkent')
        return localtime(self.created_at, uz_time)

    def can_delete(self, current_user):
        """Hozirgi foydalanuvchi o‘chirishi mumkinmi"""
        return self.user == current_user or current_user.is_admin_user

    def can_reply(self, current_user):
        """Hozirgi foydalanuvchi javob bera oladimi"""
        return not current_user.is_banned

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]}"


# =======================
# PROFILE AVATAR
# =======================
class ProfileAvatar(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='avatars/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avatar {self.id}"


# =======================
# SUBSCRIPTION RECEIPTS
# =======================
class SubscriptionReceipt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='receipts')
    plan = models.CharField(max_length=50) # masalan: '1_month', '1_year'
    image = models.ImageField(upload_to='receipts/%Y/%m/')
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan} ({'Tasdiqlangan' if self.is_approved else 'Rad etish' if self.is_rejected else 'Kutilmoqda'})"


# =======================
# FAVORITE & HISTORY
# =======================
class FavoriteAnime(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

class WatchHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watched_by')
    last_watched = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'movie')

# =======================
# MOVIE COMMENTS
# =======================
class MovieComment(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='movie_comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} - {self.text[:20]}"

# =======================
# ACTIVE SESSIONS (DEVICE LIMITS)
# =======================
class ActiveSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='active_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.session_key}"



# =======================
# ANIME NEWS
# =======================
class AnimeNews(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='news/')
    description = models.TextField()

    # 🎥 VIDEO (agar bo‘lsa oldingi qo‘shilgan)
    video = models.FileField(upload_to='news/videos/', null=True, blank=True)

    # 🔗 IXTIYORIY SILKA
    link = models.URLField(null=True, blank=True)

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='news_posts',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title



# =======================
# NEWS LIKE SYSTEM
# =======================
class NewsLike(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    news = models.ForeignKey(
        AnimeNews,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'news')
        verbose_name = "News Like"
        verbose_name_plural = "News Likes"

    def __str__(self):
        return f"{self.user.username} liked {self.news.title}"


