# urls.py
from django.urls import path
from .views import (
    register, login, home, movie_detail, check_username,
    profile, make_vip, search, anime_catalog,
    chat, chat_messages_api, edit_message, delete_message, ban_user,
    logout_view, premium_page, toggle_favorite, favorites_page, watch_history_page,reels, aloqa, news_feed, news_detail, toggle_like,next_story_view, prev_story_view, story_view, mark_story_seen,
    reels_feed, reel_detail, toggle_reel_like, add_reel_comment, reel_comments_api, reel_share,
    settings_privacy,settings_devices,settings_premium,settings_telegram,settings_general,user_mini_profile_api,
    anime_category,notice,delete_comment,service_worker_view,offline_view,manifest_view,
    hisobim_page, statistika_page, imkon_page, imkon_toggle_bg, imkon_select_bg, imkon_toggle_telegram_download,
    imkon_vote_request_add, imkon_vote, imkon_anime_request_add,check_username,
    news_load_more,vip_buy_balance, debt_request_add, balance_topup_add, jackpot_redeem,
)
from .admin_views import *
from django.conf import settings
from django.conf.urls.static import static
from .sitemaps import NewsSitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'news': NewsSitemap,
}


urlpatterns = [
    path('', home, name='home'),
    path('login/', login, name='login'),
    path('accounts/login/', login, name='login_legacy'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('movie/<int:id>/', movie_detail, name='movie_detail'),
    path('toggle-favorite/<int:movie_id>/', toggle_favorite, name='toggle_favorite'),
    path('favorites/', favorites_page, name='favorites_page'),
    path('history/', watch_history_page, name='watch_history_page'),
    path('catalog/', anime_catalog, name='anime_catalog'),
    path('search/', search, name='search'),
    path('profile/', profile, name='profile'),
    path('premium/', premium_page, name='premium_page'),
    path('news/', news_feed, name='news_feed'),
    path('news/<int:pk>/', news_detail, name='news_detail'),
    path('news/<int:pk>/like/', toggle_like, name='toggle_like'),
    path('reels/', reels, name='reels'),
    path('aloqa/', aloqa, name='aloqa'),

    path('chat/', chat, name='chat'),
    path('chat/messages/', chat_messages_api, name='chat_messages_api'),
    path('ban_user/<int:user_id>/', ban_user, name='ban_user'),
    path('edit_message/<int:message_id>/', edit_message, name='edit_message'),
    path('delete_message/<int:message_id>/', delete_message, name='delete_message'),
    path('make-vip/<int:user_id>/', make_vip, name='make_vip'),

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
    path('control-panel/subscriptions/<int:pk>/<str:action>/', admin_subscription_action,
         name='admin_subscription_action'),
    path('control-panel/avatars/', admin_avatars, name='admin_avatars'),
    path('control-panel/avatars/add/', admin_avatar_form, name='admin_avatar_form'),
    path('control-panel/avatars/<int:pk>/delete/', admin_avatar_delete, name='admin_avatar_delete'),

    path('control-panel/comments/', admin_comments, name='admin_comments'),
    path('control-panel/comments/<int:pk>/edit/', admin_comment_edit, name='admin_comment_edit'),
    path('control-panel/comments/<int:pk>/delete/', admin_comment_delete, name='admin_comment_delete'),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'
    ),
    # STORY VIEW
    path('story/<int:story_id>/', story_view, name='story_view'),
    path('story/seen/<int:story_id>/', mark_story_seen, name='mark_story_seen'),

    # NEXT / PREV
    path('story/<int:story_id>/next/', next_story_view, name='next_story'),
    path('story/<int:story_id>/prev/', prev_story_view, name='prev_story'),


    path('reels/', reels_feed, name='reels'),
    path('reels/<int:reel_id>/', reel_detail, name='reel_detail'),
    path('reels/<int:reel_id>/like/', toggle_reel_like, name='toggle_reel_like'),
    path('reels/<int:reel_id>/comment/', add_reel_comment, name='add_reel_comment'),
    path('reels/<int:reel_id>/comments/', reel_comments_api, name='reel_comments_api'),
    path('reels/<int:reel_id>/share/', reel_share, name='reel_share'),

    path('settings/', settings_general, name='settings_general'),
    path('settings/telegram/', settings_telegram, name='settings_telegram'),
    path('settings/premium/', settings_premium, name='settings_premium'),
    path('settings/devices/', settings_devices, name='settings_devices'),
    path('settings/privacy/', settings_privacy, name='settings_privacy'),



    # urlpatterns ga qo'shing:
    path('control-panel/schedule/', admin_schedule, name='admin_schedule'),
    path('control-panel/schedule/add/', admin_schedule_form, name='admin_schedule_form'),
    path('control-panel/schedule/<int:pk>/edit/', admin_schedule_form, name='admin_schedule_form'),
    path('control-panel/schedule/<int:pk>/delete/', admin_schedule_delete, name='admin_schedule_delete'),

    path('control-panel/stories/', admin_stories, name='admin_stories'),
    path('control-panel/stories/add/', admin_story_form, name='admin_story_form'),
    path('control-panel/stories/<int:pk>/edit/', admin_story_form, name='admin_story_form'),
    path('control-panel/stories/<int:pk>/delete/', admin_story_delete, name='admin_story_delete'),
    path('control-panel/stories/<int:pk>/views/', admin_story_views, name='admin_story_views'),

    path('control-panel/news/', admin_news, name='admin_news'),
    path('control-panel/news/add/', admin_news_form, name='admin_news_form'),
    path('control-panel/news/<int:pk>/edit/', admin_news_form, name='admin_news_form'),
    path('control-panel/news/<int:pk>/delete/', admin_news_delete, name='admin_news_delete'),
    path('control-panel/news/<int:pk>/likes/', admin_news_likes, name='admin_news_likes'),
    path('kategoriya/', anime_category, name='anime_category'),
    path('boshqaruv/sections/', admin_sections, name='admin_sections'),
    path('boshqaruv/sections/add/', admin_section_form, name='admin_section_form'),
    path('boshqaruv/sections/<int:pk>/edit/', admin_section_form, name='admin_section_form_edit'),
    path('boshqaruv/sections/<int:pk>/delete/', admin_section_delete, name='admin_section_delete'),

    path('notice/', notice, name='notice'),
    path('control-panel/notices/', admin_notices, name='admin_notices'),
    path('control-panel/notices/add/', admin_notice_form, name='admin_notice_form'),
    path('control-panel/notices/<int:pk>/edit/', admin_notice_form, name='admin_notice_form'),
    path('control-panel/notices/<int:pk>/delete/', admin_notice_delete, name='admin_notice_delete'),
    path('chat/user-profile/<int:user_id>/', user_mini_profile_api, name='user_mini_profile_api'),
    path('control-panel/movies/<int:movie_id>/haqida/', admin_animehaqida_form, name='admin_animehaqida_form'),
    path('control-panel/movies/<int:movie_id>/kadrlar/', admin_kadrlar_form, name='admin_kadrlar_form'),
    path('control-panel/movies/frame/<int:pk>/delete/', admin_kadrlar_delete, name='admin_kadrlar_delete'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    path('service-worker.js', service_worker_view, name='service_worker'),
    path('manifest.json', manifest_view, name='manifest'),
    path('offline/', offline_view, name='offline_page'),
    path('hisobim/', hisobim_page, name='hisobim_page'),
    path('statistika/', statistika_page, name='statistika_page'),
    path('imkon/', imkon_page, name='imkon_page'),

    path('imkon/premium-fon/toggle/', imkon_toggle_bg, name='imkon_toggle_bg'),
    path('imkon/premium-fon/<int:pk>/tanlash/', imkon_select_bg, name='imkon_select_bg'),
    path('imkon/telegram-yuklab-olish/toggle/', imkon_toggle_telegram_download, name='imkon_toggle_telegram_download'),
    path('imkon/sorovnoma/qoshish/', imkon_vote_request_add, name='imkon_vote_request_add'),
    path('imkon/sorovnoma/<int:pk>/ovoz/', imkon_vote, name='imkon_vote'),
    path('imkon/anime-sorash/qoshish/', imkon_anime_request_add, name='imkon_anime_request_add'),
    path('check-username/', check_username, name='check_username'),
    path('news/load-more/', news_load_more, name='news_load_more'),
    path('news/<int:pk>/', news_detail, name='news_detail'),
    path('news/<int:pk>/like/', toggle_like, name='toggle_like'),

    path('hisobim/vip-buy/<str:plan_key>/', vip_buy_balance, name='vip_buy_balance'),
    path('hisobim/qarz-sorash/', debt_request_add, name='debt_request_add'),
    path('hisobim/toldirish/', balance_topup_add, name='balance_topup_add'),
    path('hisobim/jackpot/', jackpot_redeem, name='jackpot_redeem'),

    # JACKPOT (admin)
    path('control-panel/jackpot/', admin_jackpot_list, name='admin_jackpot_list'),
    path('control-panel/jackpot/add/', admin_jackpot_form, name='admin_jackpot_form'),
    path('control-panel/jackpot/<int:pk>/edit/', admin_jackpot_form, name='admin_jackpot_form'),
    path('control-panel/jackpot/<int:pk>/delete/', admin_jackpot_delete, name='admin_jackpot_delete'),
    path('control-panel/jackpot/<int:pk>/cancel/', admin_jackpot_cancel_user, name='admin_jackpot_cancel_user'),

    # HISOB (admin)
    path('control-panel/hisob/', admin_hisob_list, name='admin_hisob_list'),
    path('control-panel/hisob/qidirish/', admin_hisob_form, name='admin_hisob_form_lookup'),
    path('control-panel/hisob/<int:user_id>/', admin_hisob_form, name='admin_hisob_form'),

    # QARZ (admin)
    path('control-panel/qarz/', admin_qarz_list, name='admin_qarz_list'),
    path('control-panel/qarz/<int:pk>/tasdiqlash/', admin_qarz_tasdiqlash, name='admin_qarz_tasdiqlash'),
    path('control-panel/qarz/<int:pk>/rad/', admin_qarz_rad, name='admin_qarz_rad'),

]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
