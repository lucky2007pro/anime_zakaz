from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import (
    Category, CustomUser, VipUser, Movie, MovieEpisode,
    SiteSettings, MP3, ChatMessage, ProfileAvatar, SubscriptionReceipt,NewsLike, AnimeNews, Story, StoryView,
    Reel, ReelLike, ReelComment, ReelShare,AnimeSchedule,AnimeSectionItem,Notice, NoticeRead,MovieFrame,NoResultsMedia,
    PremiumBackground, AnimeVoteRequest, AnimeVote, AnimeRequestSuggestion,
    AccountHistory, DebtRequest, JackpotCode, JackpotCodeUse,
    BalanceTopupRequest, UserBalance,
)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_admin_user', 'is_banned', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_admin_user', 'is_banned')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'phone', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'is_admin_user', 'is_banned', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2', 'is_staff', 'is_active', 'is_admin_user', 'is_banned')}
        ),
    )
    search_fields = ('username', 'email', 'phone')
    ordering = ('username',)


# class VipUserTanlashAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'is_vip', 'vip_expire')
#     fields = ('user', 'is_vip', 'vip_expire')
#     search_fields = ('user__username', 'user__email')  # Username bo‘yicha qidirish qulayroq


class MovieEpisodeInline(admin.TabularInline):
    model = MovieEpisode
    extra = 1
    fields = ('episode_number', 'title', 'video_url', 'video_file', 'description','intro_time')
    show_change_link = True


class MovieFrameInline(admin.TabularInline):
    model = MovieFrame
    extra = 1
    max_num = 5          # admin panelda ham 5 tadan ortiq qo'sha olmaydi
    fields = ('image', 'order')
    ordering = ('order',)


class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'rating', 'minimum_tier', 'created_at')
    search_fields = ('title',)
    inlines = [MovieFrameInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'image', 'description', 'category', 'release_year')
        }),
        ("Video", {
            'fields': ('video_url', 'video_file', 'telegram_link')
        }),
        ("Kirish huquqi", {
            'fields': ('is_premium', 'minimum_tier')
        }),
        ("Bosh sahifa", {
            'fields': ('is_home_featured', 'home_featured_order', 'hero_media')
        }),
        ("Qo'shimcha (Anime haqida / Intro / Reyting)", {
            'fields': ('about_info', 'intro_time', 'rating')
        }),
    )



class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'background_video', 'background_image', 'updated_at')


class MP3Admin(admin.ModelAdmin):
    list_display = ('title', 'file', 'created_at')
    search_fields = ('title',)


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message_preview', 'created_at', 'edited', 'reply_to')
    list_filter = ('edited', 'created_at')
    search_fields = ('message', 'user__username')
    ordering = ('-created_at',)

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

class AnimeNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'total_likes_count')
    search_fields = ('title', 'description', 'author__username')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def total_likes_count(self, obj):
        return obj.total_likes()
    total_likes_count.short_description = "Likes"

class NewsLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'news', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'news__title')

class StoryViewInline(admin.TabularInline):
    model = StoryView
    extra = 0
    readonly_fields = ('user', 'viewed_at')
    can_delete = False


class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at', 'expires_at', 'total_views')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')

    # expires_at ni olib tashlang
    readonly_fields = ('created_at',)

    inlines = [StoryViewInline]

    def total_views(self, obj):
        return obj.views.count()

    total_views.short_description = "Ko‘rishlar"

@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'views_count', 'shares_count', 'total_likes', 'total_comments', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'title', 'description')
    readonly_fields = ('views_count', 'shares_count', 'created_at')
    ordering = ('-created_at',)

    def total_likes(self, obj):
        return obj.likes.count()
    total_likes.short_description = 'Likelar'

    def total_comments(self, obj):
        return obj.comments.count()
    total_comments.short_description = 'Izohlar'


@admin.register(ReelLike)
class ReelLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reel', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    ordering = ('-created_at',)


@admin.register(ReelComment)
class ReelCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reel', 'text_short', 'reply_to', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'text')
    ordering = ('-created_at',)

    def text_short(self, obj):
        return obj.text[:50]
    text_short.short_description = 'Izoh'


@admin.register(ReelShare)
class ReelShareAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reel', 'shared_at')
    list_filter = ('shared_at',)
    search_fields = ('user__username',)
    ordering = ('-shared_at',)

@admin.register(AnimeSchedule)
class AnimeScheduleAdmin(admin.ModelAdmin):
    list_display  = ('name', 'day', 'episode_number', 'fandub', 'is_active', 'order')
    list_filter   = ('day', 'is_active')
    list_editable = ('is_active', 'order', 'episode_number')
    search_fields = ('name', 'fandub')
    ordering      = ('order',)


@admin.register(AnimeSectionItem)
class AnimeSectionItemAdmin(admin.ModelAdmin):
    list_display = ('movie', 'section', 'order', 'created_at')
    list_filter = ('section',)
    search_fields = ('movie__title',)
    autocomplete_fields = ('movie',)
    ordering = ('section', 'order')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'message')
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# =======================
# PREMIUM FON
# =======================
@admin.register(PremiumBackground)
class PremiumBackgroundAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order', 'created_at')
    list_editable = ('order',)
    ordering = ('order', '-created_at')
    search_fields = ('name',)


# =======================
# ANIME SO'ROVNOMA (VIP OVOZ BERISH)
# =======================
class AnimeVoteInline(admin.TabularInline):
    model = AnimeVote
    extra = 0
    readonly_fields = ('user', 'created_at')
    can_delete = True


@admin.register(AnimeVoteRequest)
class AnimeVoteRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'total_votes_display', 'created_at')
    search_fields = ('name', 'created_by__username')
    readonly_fields = ('created_by', 'created_at')
    inlines = [AnimeVoteInline]

    def total_votes_display(self, obj):
        return obj.total_votes()
    total_votes_display.short_description = "Ovozlar soni"


@admin.register(AnimeVote)
class AnimeVoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'user', 'created_at')
    search_fields = ('request__name', 'user__username')
    readonly_fields = ('created_at',)


# =======================
# OLDINDAN ANIME SO'RASH
# =======================
@admin.register(AnimeRequestSuggestion)
class AnimeRequestSuggestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'created_at')
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at',)

@admin.register(NoResultsMedia)
class NoResultsMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'media_type', 'is_active', 'created_at')
    list_filter = ('media_type', 'is_active')
    fields = ('media_type', 'image', 'video', 'is_active')

@admin.register(AccountHistory)
class AccountHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'text')
    readonly_fields = ('created_at',)


@admin.register(DebtRequest)
class DebtRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at', 'processed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    actions = ['approve_debt', 'reject_debt']

    def approve_debt(self, request, queryset):
        count = 0
        for debt in queryset.filter(status='pending'):
            balance, _ = UserBalance.objects.get_or_create(user=debt.user)
            balance.amount += debt.amount
            balance.save()
            debt.status = 'approved'
            debt.processed_at = timezone.now()
            debt.save()
            AccountHistory.objects.create(
                user=debt.user,
                text=f"{debt.amount:,} so'm qarz so'rovi tasdiqlandi, hisobingizga qo'shildi".replace(',', '.')
            )
            count += 1
        self.message_user(request, f"{count} ta qarz so'rovi tasdiqlandi")
    approve_debt.short_description = "Tanlangan qarz so'rovlarini tasdiqlash"

    def reject_debt(self, request, queryset):
        count = 0
        for debt in queryset.filter(status='pending'):
            debt.status = 'rejected'
            debt.processed_at = timezone.now()
            debt.save()
            AccountHistory.objects.create(
                user=debt.user,
                text=f"{debt.amount:,} so'm qarz so'rovi rad etildi".replace(',', '.')
            )
            count += 1
        self.message_user(request, f"{count} ta qarz so'rovi rad etildi")
    reject_debt.short_description = "Tanlangan qarz so'rovlarini rad etish"


@admin.register(BalanceTopupRequest)
class BalanceTopupRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'is_approved', 'is_rejected', 'created_at')
    list_filter = ('is_approved', 'is_rejected', 'created_at')
    search_fields = ('user__username',)
    actions = ['approve_topup', 'reject_topup']

    def approve_topup(self, request, queryset):
        count = 0
        for topup in queryset.filter(is_approved=False, is_rejected=False):
            balance, _ = UserBalance.objects.get_or_create(user=topup.user)
            balance.amount += topup.amount
            balance.save()
            topup.is_approved = True
            topup.save()
            AccountHistory.objects.create(
                user=topup.user,
                text=f"Hisobingiz {topup.amount:,} so'm ga to'ldirildi".replace(',', '.')
            )
            count += 1
        self.message_user(request, f"{count} ta to'lov tasdiqlandi")
    approve_topup.short_description = "Tanlangan to'lovlarni tasdiqlash"

    def reject_topup(self, request, queryset):
        count = 0
        for topup in queryset.filter(is_approved=False, is_rejected=False):
            topup.is_rejected = True
            topup.save()
            AccountHistory.objects.create(
                user=topup.user,
                text=f"{topup.amount:,} so'm to'lov cheki rad etildi".replace(',', '.')
            )
            count += 1
        self.message_user(request, f"{count} ta to'lov rad etildi")
    reject_topup.short_description = "Tanlangan to'lovlarni rad etish"


@admin.register(JackpotCode)
class JackpotCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'reward_type', 'vip_days', 'balance_amount', 'expires_at', 'is_active', 'created_at')
    list_filter = ('reward_type', 'is_active')
    search_fields = ('code',)

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(JackpotCodeUse)
class JackpotCodeUseAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'used_at')
    list_filter = ('used_at',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Movie, MovieAdmin)
# admin.site.register(MovieEpisode)  # Alohida ko‘rish shart emas, inline orqali boshqariladi
admin.site.register(SiteSettings, SiteSettingsAdmin)
admin.site.register(MP3, MP3Admin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(Category)
admin.site.register(ProfileAvatar)
admin.site.register(SubscriptionReceipt)
# admin.site.register(VipUserTanlash, VipUserTanlashAdmin)

admin.site.register(AnimeNews, AnimeNewsAdmin)
admin.site.register(NewsLike, NewsLikeAdmin)

admin.site.register(Story, StoryAdmin)
admin.site.register(StoryView)

