from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import title
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
    is_admin_user = models.BooleanField(default=False)
    avatar = models.ForeignKey('ProfileAvatar', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    def active_tier(self):
        if not hasattr(self, 'vip_data'):
            return 'basic'
        return self.vip_data.get_tier()

    # ============================================
    # DARAJA (LEVEL) TIZIMI
    # ============================================
    def days_since_joined(self):
        """Foydalanuvchi ro'yxatdan o'tganiga necha kun bo'ldi"""
        return (timezone.now() - self.date_joined).days

    def watched_count(self):
        """Nechta anime ko'rgan (WatchHistory bo'yicha)"""
        return self.watch_history.count()

    def _days_level(self):
        days = self.days_since_joined()
        if days >= 50:
            return 20
        elif days >= 31:
            return 10
        elif days >= 1:
            return 5
        return 0

    def _watched_level(self):
        count = self.watched_count()
        if count >= 50:
            return 20
        elif count >= 20:
            return 10
        elif count >= 5:
            return 5
        return 0

    def get_level(self):
        """Umumiy daraja = kunlik daraja + ko'rilgan anime darajasi"""
        return self._days_level() + self._watched_level()

    def display_name(self):
        """Profilda kiritilgan ismi bo'lsa o'shani, bo'lmasa username'ni qaytaradi"""
        return self.first_name.strip() if self.first_name and self.first_name.strip() else self.username

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
        return f"{self.user.username} - VIP" if self.user.username else f"User-{self.user.id} - VIP"


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
    about_info = models.TextField(
        blank=True, null=True,
        help_text="'Anime haqida' bo'limida chiqadigan matn (admin kiritadi)"
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
    rating = models.DecimalField(
        max_digits=3, decimal_places=1,
        blank=True, null=True,
        help_text="Anime reytingi, masalan: 8.5"
    )

    intro_time = models.CharField(
        max_length=30, blank=True, null=True,
        help_text="Intro oralig'i (faqat qismsiz film uchun), masalan: 2:55 | 3:17"
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
    video_file = models.FileField(upload_to='videos/', blank=True, null=True,
                                  help_text="Yoki video faylni yuklang (mp4, mkv va b.)")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    intro_time = models.CharField(
        max_length=30, blank=True, null=True,
        help_text="Intro oralig'i, masalan: 2:55 | 3:17"
    )

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
    # YANGI — yangilikka javob sifatida yozilgan xabar
    reply_to_news = models.ForeignKey(
        'AnimeNews',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_replies'
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
    plan = models.CharField(max_length=50)  # masalan: '1_month', '1_year'
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
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Agar bu boshqa izohga javob bo'lsa, o'sha izoh shu yerda"
    )
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


# =======================
# STORY
# =======================
class Story(models.Model):
    title = models.CharField(max_length=200)

    image = models.ImageField(upload_to='stories/', blank=True, null=True)
    video = models.FileField(upload_to='stories/videos/', blank=True, null=True)

    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # Admin panelda qo‘lda tanlanadi
    expires_at = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at

    def __str__(self):
        return self.title


# =======================
# STORY VIEW (KO'RILGANLAR)
# =======================
class StoryView(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='views')

    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'story')

    def __str__(self):
        return f"{self.user.username} -> {self.story.title}"



# =======================
# REELS
# =======================
class Reel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reels')
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to='reels/videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='reels/thumbnails/', blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def total_likes(self):
        return self.likes.count()

    def total_comments(self):
        return self.comments.count()

    def get_video_src(self):
        if self.video_file:
            return self.video_file.url
        return self.video_url or ''

    def __str__(self):
        return f"Reel #{self.id} - {self.user.username}"


class ReelLike(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reel_likes')
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'reel')

    def __str__(self):
        return f"{self.user.username} liked Reel#{self.reel.id}"


class ReelComment(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reel_comments')
    text = models.TextField()
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}"


class ReelShare(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reel#{self.reel.id} shared"





# ========================
# setting uchun confik lr
# ========================

class UserSettings(models.Model):
    THEME_CHOICES = [
        ('dark',    'Qorong\'i'),
        ('white',   'Oq'),
        ('rose',    'Qizil / Ro\'za'),
        ('premium', 'Premium (To\'q binafsha)'),
    ]

    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='settings'
    )

    # Mavzu
    theme = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='dark'
    )

    # Fon rangi (tayyor swatchlar uchun)
    bg_color = models.CharField(
        max_length=30,
        default='#0a0a0f',
        help_text="Hex yoki gradient kalit so'z"
    )

    # Custom color picker qiymati
    bg_color_custom = models.CharField(
        max_length=30,
        default='#0a0a0f',
        blank=True, null=True
    )

    # Tab bar (mobil pastki panel)
    tabbar_on = models.BooleanField(default=True)

    # PREMIUM IMKONIYATLAR
    premium_bg_on = models.BooleanField(default=False)
    premium_bg = models.ForeignKey(
        'PremiumBackground', on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )
    telegram_download_on = models.BooleanField(default=False)

    # Telegram sozlamalari
    telegram_username  = models.CharField(max_length=100, blank=True, null=True)
    telegram_chat_id   = models.CharField(max_length=50,  blank=True, null=True)
    telegram_bot_token = models.CharField(max_length=200, blank=True, null=True)
    telegram_notify_on = models.BooleanField(
        default=False,
        help_text="Yangi epizod yoki xabar bo'lganda Telegram orqali xabar yuborish"
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} – sozlamalar"


# =======================
# ACTIVE SESSIONS (DEVICE LIMITS)
# =======================
class ActiveSession(models.Model):
    DEVICE_CHOICES = [
        ('mobile', 'Mobil'),
        ('tablet', 'Planshet'),
        ('desktop', 'Kompyuter'),
        ('unknown', 'Noma\'lum'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='active_sessions')
    session_key = models.CharField(max_length=40, unique=True)

    # Qurilma ma'lumotlari
    device_type   = models.CharField(max_length=20, choices=DEVICE_CHOICES, default='unknown')
    device_name   = models.CharField(max_length=200, blank=True, null=True, help_text="Browser + OS")
    ip_address    = models.GenericIPAddressField(blank=True, null=True)
    user_agent    = models.TextField(blank=True, null=True)
    browser       = models.CharField(max_length=100, blank=True, null=True)
    os_name       = models.CharField(max_length=100, blank=True, null=True)
    location      = models.CharField(max_length=200, blank=True, null=True, help_text="Taxminiy joylashuv")

    created_at    = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.device_name or 'Noma\'lum qurilma'} ({self.ip_address})"



# =======================
# ANIME SCHEDULE (Chiqish kunlari)
# =======================
class AnimeSchedule(models.Model):
    DAY_CHOICES = [
        ('dushanba',  'Dushanba'),
        ('seshanba',  'Seshanba'),
        ('chorshanba','Chorshanba'),
        ('payshanba', 'Payshanba'),
        ('juma',      'Juma'),
        ('shanba',    'Shanba'),
        ('yakshanba', 'Yakshanba'),
    ]

    name        = models.CharField(max_length=200, help_text="Anime nomi")
    subtitle    = models.CharField(max_length=200, blank=True, null=True, help_text="Kichik sarlavha")
    image_url   = models.URLField(help_text="Poster rasmi URL (masalan: https://i.pinimg.com/...)")
    day         = models.CharField(max_length=20, choices=DAY_CHOICES, help_text="Chiqish kuni")
    episode_number = models.PositiveIntegerField(default=1, help_text="Chiqadigan qism raqami")
    fandub      = models.CharField(max_length=100, default='AniBest', help_text="Fandub nomi")
    watch_url   = models.URLField(help_text="Ko'rish havolasi (masalan: https://bestmedia-official.uz/movie/7/)")
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveSmallIntegerField(default=0, help_text="Kichik raqam avval chiqadi")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.name} — {self.get_day_display()} ({self.episode_number}-qism)"



# =======================
# KATEGORIYA BO'LIMLARI (Kunlik anime / Anime film)
# =======================
class AnimeSectionItem(models.Model):
    SECTION_CHOICES = [
        ('daily', 'Kunlik anime'),
        ('film', 'Anime film'),
    ]

    section = models.CharField(
        max_length=10,
        choices=SECTION_CHOICES,
        help_text="Qaysi bo'limga chiqishi kerak"
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='section_items',
        help_text="Nomi bo'yicha animani tanlang"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Kichik raqam avval chiqadi"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        unique_together = ('section', 'movie')
        verbose_name = "Kategoriya bo'limi (Kunlik/Film)"
        verbose_name_plural = "Kategoriya bo'limlari (Kunlik/Film)"

    def __str__(self):
        return f"{self.get_section_display()} — {self.movie.title}"








# =======================
# NOTICE (BILDIRISHNOMALAR)
# =======================
class Notice(models.Model):
    TYPE_CHOICES = [
        ('admin', 'Admin xabari'),
        ('reply', 'Chatda javob'),
    ]
    # YANGI — izohga (MovieComment) javob berilganda shu to'ldiriladi
    related_movie_comment = models.ForeignKey(
        'MovieComment', on_delete=models.CASCADE, null=True, blank=True, related_name='+'
    )

    notice_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='admin')

    title = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()

    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sent_notices', help_text="Yuborgan admin yoki javob yozgan foydalanuvchi"
    )

    # Faqat 'reply' turi uchun to'ldiriladi — kimga tegishli
    target_user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True,
        related_name='personal_notices',
        help_text="Faqat shaxsiy (reply) bildirishnoma uchun. Admin xabari hammaga bo'lsa bo'sh qoldiring."
    )

    related_chat_message = models.ForeignKey(
        'ChatMessage', on_delete=models.CASCADE, null=True, blank=True, related_name='+'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or self.message[:30]


class NoticeRead(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='read_notices')
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name='reads')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'notice')


class MovieFrame(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='frames'
    )
    image = models.ImageField(upload_to='movies/frames/')
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Kichik raqam avval chiqadi"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Anime kadr"
        verbose_name_plural = "Anime kadrlar"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.movie_id:
            qs = MovieFrame.objects.filter(movie_id=self.movie_id)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.count() >= 5:
                raise ValidationError("Bitta anime uchun maksimal 5 ta kadr yuklash mumkin.")

    def __str__(self):
        return f"{self.movie.title} - kadr #{self.order}"






class WatchHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watched_by')
    last_watched = models.DateTimeField(auto_now=True)
    # YANGI — oxirgi ko'rilgan qism (profilda "9-qism" deb chiqarish uchun)
    last_episode = models.ForeignKey(
        'MovieEpisode', on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )

    class Meta:
        unique_together = ('user', 'movie')


# =======================
# HISOBIM (BALANS)
# =======================
class UserBalance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='balance')
    amount = models.PositiveIntegerField(default=0, help_text="Hisobdagi mablag' / ball")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.amount}"
# =======================
# PREMIUM FON
# =======================
class PremiumBackground(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='premium_backgrounds/')
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Premium fon"
        verbose_name_plural = "Premium fonlar"

    def __str__(self):
        return self.name or f"Fon #{self.id}"


# =======================
# ANIME SO'ROVNOMA (VIP OVOZ BERISH)
# =======================
class AnimeVoteRequest(models.Model):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='anime_vote_requests')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def total_votes(self):
        return self.votes.count()

    def __str__(self):
        return self.name


class AnimeVote(models.Model):
    request = models.ForeignKey(AnimeVoteRequest, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='anime_votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('request', 'user')


# =======================
# OLDINDAN ANIME SO'RASH
# =======================
class AnimeRequestSuggestion(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='anime_request_suggestion')
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"





# =======================
# QIDIRUV - NATIJA TOPILMADI MEDIA (yashil fon avtomatik olib tashlanadi)
# =======================
class NoResultsMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Rasm'),
        ('video', 'Video'),
    ]
    media_type = models.CharField(
        max_length=10, choices=MEDIA_TYPE_CHOICES, default='image',
        help_text="Rasmmi yoki videomi?"
    )
    image = models.ImageField(
        upload_to='no_results/', blank=True, null=True,
        help_text="Yashil (chroma-key) fonli rasm — fon avtomatik shaffof qilinadi"
    )
    video = models.FileField(
        upload_to='no_results/videos/', blank=True, null=True,
        help_text="Yashil (chroma-key) fonli video — fon avtomatik shaffof qilinadi"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Qidiruv - Natija topilmadi (media)"
        verbose_name_plural = "Qidiruv - Natija topilmadi (media)"

    def __str__(self):
        return f"NoResultsMedia #{self.id} ({self.get_media_type_display()})"

