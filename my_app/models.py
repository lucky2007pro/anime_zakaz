from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

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

    def __str__(self):
        return self.username if self.username else f"User-{self.id}"


class VipUser(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='vip_data'
    )
    is_vip = models.BooleanField(default=False)
    vip_expire = models.DateTimeField(null=True, blank=True)

    def vip_active(self):
        return self.is_vip and self.vip_expire and self.vip_expire > timezone.now()

    def __str__(self):
        return f"{self.user.username} - VIP"if self.user.username else f"User-{self.user.id} - VIP"


# =======================
# MOVIE
# =======================
class Movie(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='movies/')
    description = models.TextField(blank=True, null=True)

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
    video_url = models.URLField(help_text="Bunny.net iframe yoki mp4 linkini yozing")
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
        import pytz
        uz_time = pytz.timezone('Asia/Tashkent')
        return localtime(self.created_at, uz_time)

    def can_delete(self, current_user):
        """Hozirgi foydalanuvchi o‘chirishi mumkinmi"""
        return self.user == current_user or current_user.is_admin_user

    def can_reply(self, current_user):
        """Hozirgi foydalanuvchi javob bera oladimi"""
        return not current_user.is_banned

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]}"