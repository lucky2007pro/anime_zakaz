# Bo'limlar ro'yxati (kalit, nom)
SECTIONS = [
    ('genres', 'Janrlar'),
    ('avatars', 'Rasmlar'),
    ('movies', 'Animelar'),
    ('episodes', 'Qismlar'),
    ('subscriptions', 'Obunalar'),
    ('chat', 'Chat'),
    ('comments', 'Izohlar'),
    ('schedule', 'Jadval'),
    ('stories', 'Storylar'),
    ('news', 'Yangiliklar'),
    ('reelbest', 'ReelBest'),
    ('sections', "Kategoriya bo'limlari"),
    ('premium', 'Premium azolar'),
    ('vip_video', 'VIP Videolar'),
    ('polls', "So'rovnomalar"),
    ('notices', "E'lonlar"),
    ('hisob', 'Hisoblar'),
    ('qarz', "Qarz so'rovlari"),
    ('jackpot', 'Jackpot kodlar'),
]

SECTION_KEYS = [k for k, _ in SECTIONS]
SECTION_LABELS = dict(SECTIONS)

# url name ("admin_" dan keyin) qaysi prefiks bilan boshlansa, shu bo'limga tegishli
PREFIX_MAP = [
    ('movie', 'movies'),
    ('animehaqida', 'movies'),
    ('kadrlar', 'movies'),
    ('genre', 'genres'),
    ('episode', 'episodes'),
    ('subscription', 'subscriptions'),
    ('avatar', 'avatars'),
    ('comment', 'comments'),
    ('schedule', 'schedule'),
    ('stor', 'stories'),
    ('news', 'news'),
    ('reelbest', 'reelbest'),
    ('section', 'sections'),
    ('notice', 'notices'),
    ('jackpot', 'jackpot'),
    ('hisob', 'hisob'),
    ('qarz', 'qarz'),
    ('premium', 'premium'),
    ('vip_video', 'vip_video'),
    ('poll', 'polls'),
    ('chat', 'chat'),
    ('message', 'chat'),
]


def section_for_url(url_name):
    if not url_name or not url_name.startswith('admin_'):
        return None
    name = url_name[len('admin_'):]
    for prefix, key in PREFIX_MAP:
        if name.startswith(prefix):
            return key
    return None


def get_allowed_sections(user):
    """Foydalanuvchiga ochiq bo'limlar kalitlari ro'yxati"""
    if user.id == 1:
        return list(SECTION_KEYS)
    from .models import AdminProfile
    profile = AdminProfile.objects.filter(user=user).first()
    if profile is None or profile.all_access:
        return list(SECTION_KEYS)
    return profile.sections_list()