from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Movie, MovieEpisode, SiteSettings, MP3, ChatMessage, Category


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
    fields = ('episode_number', 'title', 'video_url', 'video_file', 'description')
    show_change_link = True


class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_home_featured', 'home_featured_order', 'created_at')
    search_fields = ('title',)
    list_filter = ('created_at', 'is_home_featured')
    list_editable = ('is_home_featured', 'home_featured_order')
    inlines = [MovieEpisodeInline]


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


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Movie, MovieAdmin)
# admin.site.register(MovieEpisode)  # Alohida ko‘rish shart emas, inline orqali boshqariladi
admin.site.register(SiteSettings, SiteSettingsAdmin)
admin.site.register(MP3, MP3Admin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(Category)
# admin.site.register(VipUserTanlash, VipUserTanlashAdmin)