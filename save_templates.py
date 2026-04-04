import os

base_html = """{% load static %}
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AniHub - Eksklyuziv Anime Platformasi{% endblock %}</title>
    
    <meta name="theme-color" content="#7c3aed">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <link href="https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css" rel="stylesheet">
    
    <style>
        :root {
            --bg-color: #0b0f19;
            --surface-color: #151a2a;
            --primary-color: #7c3aed;
            --primary-hover: #6d28d9;
            --secondary-color: #fca5a5;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --glass-bg: rgba(21, 26, 42, 0.7);
            --border-color: rgba(124, 58, 237, 0.2);
            --radius-lg: 16px;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-main); overflow-x: hidden; scroll-behavior: smooth; min-height: 100vh; display: flex; flex-direction: column; }
        
        .navbar { position: fixed; top: 0; width: 100%; padding: 20px 6%; display: flex; justify-content: space-between; align-items: center; background: linear-gradient(180deg, rgba(11, 15, 25, 0.95), transparent); backdrop-filter: blur(8px); z-index: 1000; transition: all 0.3s; }
        .navbar.scrolled { background: var(--bg-color); padding: 15px 6%; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .logo { font-size: 2rem; font-weight: 900; color: var(--text-main); text-decoration: none; display: flex; align-items: center; gap: 8px;}
        .logo i { color: var(--primary-color); font-size: 2.4rem; }
        .nav-links { display: flex; gap: 30px; }
        .nav-links a { color: var(--text-main); text-decoration: none; font-weight: 500; font-size: 1rem; transition: 0.3s; position: relative;}
        .nav-links a:hover { color: var(--primary-color); }
        .nav-icons { display: flex; gap: 20px; align-items: center; }
        .icon-btn { color: var(--text-main); font-size: 1.5rem; background: transparent; border: none; cursor: pointer; transition: 0.3s; }
        .icon-btn:hover { color: var(--primary-color); transform: scale(1.1); }
        .user-btn { width: 40px; height: 40px; background: var(--surface-color); border: 2px solid var(--border-color); border-radius: 50%; display: grid; place-items: center; font-size: 1.2rem; cursor: pointer; transition: 0.3s;}
        .mobile-menu-btn { display: none; font-size: 2rem; color: #fff; cursor: pointer; }
        
        .sidebar-modal { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(5px); z-index: 2000; opacity: 0; visibility: hidden; transition: 0.3s; }
        .sidebar { position: fixed; top: 0; right: -400px; width: 350px; height: 100vh; background: var(--surface-color); border-left: 2px solid var(--border-color); z-index: 2005; transition: 0.4s cubic-bezier(0.2, 0.8, 0.2, 1); padding: 30px 20px; display: flex; flex-direction: column; overflow-y:auto; }
        .sidebar-modal.active { opacity: 1; visibility: visible; }
        .sidebar.active { right: 0; }
        .close-sidebar { align-self: flex-end; font-size: 1.8rem; background: none; border: none; color: var(--text-muted); cursor: pointer; transition: 0.3s;}
        .user-widget { text-align: center; margin-bottom: 40px; }
        .user-av { width: 90px; height: 90px; border-radius: 50%; background: linear-gradient(45deg, var(--primary-color), #2dd4bf); margin: 0 auto 15px; display: grid; place-items: center; font-size: 2.5rem; font-weight: 900; box-shadow: 0 0 20px rgba(124,58,237,0.4); }
        .user-name { font-size: 1.4rem; font-weight: 700; }
        .ms-links { display: flex; flex-direction: column; gap: 15px; }
        .ms-link { padding: 15px; background: rgba(255,255,255,0.03); border-radius: 12px; display: flex; align-items: center; gap: 15px; text-decoration: none; color: var(--text-main); font-weight: 500; transition: 0.3s; border: 1px solid transparent; }
        .ms-link:hover { background: var(--glass-bg); border-color: var(--primary-color); transform: translateX(-5px); }
        .ms-link i { font-size: 1.4rem; color: var(--primary-color); }
        
        main.main-content { flex: 1; margin-top: 80px; padding: 40px 6%; }
        
        /* Auth forms mostly */
        .auth-container { max-width: 400px; margin: 50px auto; background: var(--surface-color); padding: 30px; border-radius: var(--radius-lg); border: 1px solid var(--border-color); }
        .auth-container h2 { margin-bottom: 20px; text-align: center; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: var(--text-muted); }
        .form-control { width: 100%; padding: 12px; background: rgba(0,0,0,0.2); border: 1px solid var(--border-color); color: #fff; border-radius: 8px; outline: none; transition: 0.3s; }
        .form-control:focus { border-color: var(--primary-color); box-shadow: 0 0 10px rgba(124,58,237,0.3); }
        .btn-submit { width: 100%; padding: 12px; background: var(--primary-color); color: #fff; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.3s; }
        .btn-submit:hover { background: var(--primary-hover); transform: translateY(-2px); }

        @media(max-width: 900px) {
            .navbar { padding: 15px 5%; }
            .nav-links { display: none; }
            .mobile-menu-btn { display: block; }
        }
        @media(max-width: 480px) {
            .sidebar { width: 100%; right: -100%; }
        }
        
        {% block extra_css %}{% endblock %}
    </style>
</head>
<body>
    <nav class="navbar" id="navbar">
        <a href="{% url 'home' %}" class="logo"><i class='bx bx-play-circle'></i> AniHub</a>
        <div class="nav-links">
            <a href="{% url 'home' %}">Bosh Sahifa</a>
            <a href="{% url 'search' %}">Qidiruv</a>
            <a href="{% url 'chat' %}">Chat</a>
        </div>
        <div class="nav-icons">
            <a href="{% url 'search' %}" class="icon-btn"><i class='bx bx-search'></i></a>
            <button class="user-btn" onclick="toggleSidebar()"><i class='bx bxs-user'></i></button>
            <i class='bx bx-menu mobile-menu-btn' onclick="toggleSidebar()"></i>
        </div>
    </nav>

    {% block content %}
    {% endblock %}

    <div class="sidebar-modal" id="sidebarModal" onclick="if(event.target==this) toggleSidebar()"></div>
    <div class="sidebar" id="sidebar">
        <button class="close-sidebar" onclick="toggleSidebar()"><i class='bx bx-x'></i></button>
        <div class="user-widget">
            {% if request.user.is_authenticated %}
                <div class="user-av">{{ request.user.username|make_list|first|upper }}</div>
                <h3 class="user-name">{{ request.user.username }}</h3>
                <p style="color:var(--text-muted); font-size:0.9rem;">@{{ request.user.username|lower }}</p>
            {% else %}
                <div class="user-av"><i class='bx bx-user-circle' style="color:var(--surface-color);"></i></div>
                <h3 class="user-name">Mehmon</h3>
            {% endif %}
        </div>
        <div class="ms-links">
            {% if request.user.is_authenticated %}
                <a href="{% url 'home' %}" class="ms-link"><i class='bx bx-home'></i> Bosh sahifa</a>
                <a href="{% url 'profile' %}" class="ms-link"><i class='bx bx-user'></i> Mening Profilim</a>
                <a href="{% url 'chat' %}" class="ms-link"><i class='bx bx-message-rounded-dots'></i> Umumiy Chat</a>
                {% if request.user.is_staff or request.user.is_superuser or request.user.is_admin_user %}
                <a href="/root/" class="ms-link" style="border-color:var(--secondary-color); color:var(--secondary-color);"><i class='bx bx-shield-quarter'></i> Boshqaruv Paneli (Admin)</a>
                {% endif %}
                <form action="{% url 'logout' %}" method="post" style="margin: 0;">
                    {% csrf_token %}
                    <button type="submit" class="ms-link" style="width: 100%; border:none; color:#ef4444; background:rgba(239, 68, 68, 0.05); cursor:pointer;">
                        <i class='bx bx-log-out-circle' style="color:#ef4444;"></i> CHIQISH
                    </button>
                </form>
            {% else %}
                <a href="{% url 'login' %}" class="ms-link" style="background:var(--primary-color); border:none; justify-content:center;"><i class='bx bx-log-in-circle' style="color:#fff;"></i> Tizimga kirish</a>
                <a href="{% url 'register' %}" class="ms-link" style="justify-content:center;"><i class='bx bx-user-plus'></i> Ro'yxatdan o'tish</a>
            {% endif %}
        </div>
    </div>
    
    {% if request.session.mp3_played == False and mp3_file and request.user.is_authenticated %}
    <audio preload="auto" autoplay>
        <source src="{{ mp3_file }}" type="audio/mpeg">
    </audio>
    {% endif %}

    <script>
        window.addEventListener('scroll', () => {
            const nav = document.getElementById('navbar');
            if (window.scrollY > 50) nav.classList.add('scrolled');
            else nav.classList.remove('scrolled');
        });
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('active');
            document.getElementById('sidebarModal').classList.toggle('active');
        }
    </script>
</body>
</html>"""

home_html = """{% extends "base.html" %}
{% block extra_css %}
<style>
.hero { position: relative; width: 100%; height: 80vh; display: flex; align-items: flex-end; padding: 0 6% 8%; overflow: hidden;}
.hero-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; animation: zoom 20s infinite alternate; background-position: center!important; background-size: cover!important; }
@keyframes zoom { from { transform: scale(1); } to { transform: scale(1.1); } }
.hero-overlay { position: absolute; inset: 0; background: linear-gradient(to top, var(--bg-color) 0%, rgba(11, 15, 25, 0.4) 60%, transparent 100%); z-index: -1; }
.hero-content { max-width: 800px; z-index: 10;}
.hero-badges { display: flex; gap: 15px; margin-bottom: 20px;}
.badge { background: var(--glass-bg); border: 1px solid var(--border-color); padding: 6px 16px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; display: flex; align-items: center; gap: 5px; color: var(--secondary-color);}
.hero-title { font-size: 4.5rem; font-weight: 900; line-height: 1.1; margin-bottom: 20px; background: linear-gradient(to right, #fff, #cbd5e1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.btn-play { padding: 15px 35px; background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)); color: #fff; font-size: 1.1rem; font-weight: 700; border: none; border-radius: 30px; cursor: pointer; display: inline-flex; align-items: center; gap: 10px; text-decoration: none; }
.btn-play:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(124, 58, 237, 0.6); }
.grid-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 25px; padding: 40px 6%;}
.card { background: var(--surface-color); border-radius: var(--radius-lg); overflow: hidden; transition: 0.4s; border: 1px solid transparent; text-decoration: none; color: inherit; display: block; position: relative;}
.card:hover { transform: translateY(-10px); border-color: var(--primary-color); box-shadow: 0 10px 30px rgba(124, 58, 237, 0.2); }
.card-img { width: 100%; height: 300px; position: relative; overflow: hidden; }
.card-img img { width: 100%; height: 100%; object-fit: cover; transition: 0.5s; }
.card:hover .card-img img { transform: scale(1.1); }
.card-info { padding: 20px 15px; margin-top: -30px; z-index: 10; position: relative; background: linear-gradient(to top, var(--surface-color) 70%, transparent); }
.card-title { font-weight: 700; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
.sec-title { padding: 20px 6% 0; font-size: 1.8rem; }
@media(max-width: 900px) { .hero-title { font-size: 3rem; } .grid-cards { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); } .card-img { height: 220px; } }
@media(max-width: 480px) { .hero-title { font-size: 2.2rem; } .grid-cards { grid-template-columns: repeat(2, 1fr); gap: 15px; } .card-img { height: 200px; } }
</style>
{% endblock %}

{% block content %}
<section class="hero">
    {% if movies.0 %}
    <div class="hero-bg" style="background: url('{% if movies.0.image_url %}{{ movies.0.image_url }}{% else %}/static/images/default.jpg{% endif %}')"></div>
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <div class="hero-badges">
            <div class="badge"><i class='bx bxs-star'></i> {{ movies.0.rating|default:"9.5" }}</div>
            <div class="badge">YANGI</div>
        </div>
        <h1 class="hero-title">{{ movies.0.title }}</h1>
        <a href="{% url 'movie_detail' movies.0.id %}" class="btn-play"><i class='bx bx-play'></i> Tomosha qilish</a>
    </div>
    {% else %}
    <div class="hero-content"><h1 class="hero-title">AniHub ga xush kelibsiz</h1></div>
    {% endif %}
</section>

<h2 class="sec-title"><i class='bx bxs-flame' style="color:var(--primary-color)"></i> Yangi animelar</h2>
<div class="grid-cards">
    {% for anime in movies %}
    <a href="{% url 'movie_detail' anime.id %}" class="card">
        <div class="card-img"><img src="{{ anime.image_url }}" alt="{{ anime.title }}"></div>
        <div class="card-info">
            <div class="card-title">{{ anime.title }}</div>
            <div style="color:var(--text-muted); font-size:0.85rem;">{{ anime.release_year }}</div>
        </div>
    </a>
    {% empty %}
    Shu yerga animelar kiritiladi...
    {% endfor %}
</div>
{% endblock %}
"""

login_html = """{% extends "base.html" %}
{% block content %}
<main class="main-content">
    <div class="auth-container">
        <h2>Tizimga kirish</h2>
        {% if messages %}
            {% for msg in messages %}
            <div style="padding:10px; background: rgba(239, 68, 68, 0.2); color: #fca5a5; margin-bottom: 15px; border-radius: 8px; text-align:center;">{{ msg }}</div>
            {% endfor %}
        {% endif %}
        <form method="POST">
            {% csrf_token %}
            <div class="form-group">
                <label>Foydalanuvchi nomi</label>
                <input type="text" name="username" class="form-control" required>
            </div>
            <div class="form-group">
                <label>Parol</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn-submit">Kirish</button>
        </form>
        <p style="text-align:center; margin-top:20px; color:var(--text-muted);">Akauntingiz yo'qmi? <a href="{% url 'register' %}" style="color:var(--primary-color);">Ro'yxatdan o'tish</a></p>
    </div>
</main>
{% endblock %}
"""

register_html = """{% extends "base.html" %}
{% block content %}
<main class="main-content">
    <div class="auth-container">
        <h2>Ro'yxatdan o'tish</h2>
        {% if messages %}
            {% for msg in messages %}
            <div style="padding:10px; background: rgba(239, 68, 68, 0.2); color: #fca5a5; margin-bottom: 15px; border-radius: 8px; text-align:center;">{{ msg }}</div>
            {% endfor %}
        {% endif %}
        <form method="POST">
            {% csrf_token %}
            <div class="form-group">
                <label>Foydalanuvchi nomi</label>
                <input type="text" name="username" class="form-control" required>
            </div>
            <div class="form-group">
                <label>Elektron pochta</label>
                <input type="email" name="email" class="form-control">
            </div>
            <div class="form-group">
                <label>Parol</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn-submit">Ro'yxatdan o'tish</button>
        </form>
        <p style="text-align:center; margin-top:20px; color:var(--text-muted);">Akauntingiz bormi? <a href="{% url 'login' %}" style="color:var(--primary-color);">Kirish</a></p>
    </div>
</main>
{% endblock %}
"""

profile_html = """{% extends "base.html" %}
{% block content %}
<main class="main-content" style="max-width: 800px; margin: 80px auto; padding: 20px;">
    <div style="background: var(--surface-color); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 40px; text-align: center;">
        <div style="width: 100px; height: 100px; background: var(--primary-color); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 3rem; font-weight: 900; margin: 0 auto 20px;">
            {{ user.username|make_list|first|upper }}
        </div>
        <h2>{{ user.username }}</h2>
        <p style="color: var(--text-muted);">{{ user.email }}</p>
        
        <div style="margin-top: 30px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; text-align: left;">
            <div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="color: var(--text-muted); font-size: 0.9rem;">Ro'yxatdan o'tgan sana</div>
                <div style="font-size: 1.1rem; font-weight: 700; margin-top: 5px;">{{ date_joined_uz }}</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                 <div style="color: var(--text-muted); font-size: 0.9rem;">Profil Holati</div>
                 <div style="font-size: 1.1rem; font-weight: 700; margin-top: 5px; color: #34d399;">Faol (VIP yo'q)</div>
            </div>
        </div>
    </div>
</main>
{% endblock %}
"""

search_html = """{% extends "base.html" %}
{% block content %}
<main class="main-content">
    <div style="max-width: 600px; margin: 0 auto 40px;">
        <form method="GET" style="display: flex; gap: 10px;">
            <input type="text" name="q" value="{{ query }}" placeholder="Qidirish..." style="flex: 1; padding: 15px; background: var(--surface-color); border: 1px solid var(--border-color); color: #fff; border-radius: 12px; font-size: 1.1rem; outline:none;">
            <button type="submit" style="padding: 15px 30px; background: var(--primary-color); border: none; border-radius: 12px; color: #fff; font-weight: 700; font-size: 1.1rem; cursor: pointer;">Izlash</button>
        </form>
    </div>
    
    <h2>Natijalar:</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; margin-top:20px;">
        {% for anime in movies %}
        <a href="{% url 'movie_detail' anime.id %}" style="background: var(--surface-color); border-radius: var(--radius-lg); overflow: hidden; text-decoration:none; color:inherit; border: 1px solid transparent; transition: 0.3s; display:block;">
            <img src="{{ anime.image_url }}" alt="" style="width:100%; height:250px; object-fit:cover;">
            <div style="padding: 15px;">
                <div style="font-weight:700; white-space: nowrap; overflow:hidden; text-overflow:ellipsis;">{{ anime.title }}</div>
                <div style="color:var(--text-muted); font-size:0.85rem;">{{ anime.release_year }}</div>
            </div>
        </a>
        {% empty %}
        <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 50px;">Hech narsa topilmadi.</div>
        {% endfor %}
    </div>
</main>
{% endblock %}
"""

movie_detail = """{% extends "base.html" %}
{% block content %}
<main class="main-content">
    <div style="display: flex; gap: 40px; background: var(--surface-color); padding: 40px; border-radius: var(--radius-lg); border: 1px solid var(--border-color); flex-wrap: wrap;">
        <div style="flex: 0 0 300px; width: 300px;">
            <img src="{{ movie.image_url }}" alt="{{ movie.title }}" style="width: 100%; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <a href="{{ movie.telegram_link|default:'#' }}" style="display:block; text-align:center; padding: 15px; background: #0088cc; color: white; border-radius: 8px; text-decoration:none; font-weight:700; margin-top:20px;"><i class='bx bxl-telegram'></i> Telegram orqali yuklash</a>
        </div>
        <div style="flex: 1; min-width: 300px;">
            <div style="display:flex; gap:10px; margin-bottom:15px;">
                <span style="background:var(--primary-color); padding:5px 15px; border-radius:20px; font-size:0.85rem; font-weight:700; color:#fff;">★ {{ movie.rating }}</span>
                <span style="background:var(--secondary-color); padding:5px 15px; border-radius:20px; font-size:0.85rem; font-weight:700; color:#000;">{{ movie.release_year }}</span>
            </div>
            <h1 style="font-size: 2.5rem; margin-bottom: 20px;">{{ movie.title }}</h1>
            <p style="color: var(--text-muted); line-height: 1.8; margin-bottom: 30px; font-size: 1.1rem;">{{ movie.description }}</p>
            
            <h3>Qismlar ({{ episodes.count }})</h3>
            <div style="display:flex; flex-wrap:wrap; gap:10px; margin-top:15px;">
                {% for ep in episodes %}
                <a href="#" style="background: rgba(0,0,0,0.3); padding: 15px; border: 1px solid var(--border-color); border-radius: 8px; color: #fff; text-decoration: none; font-weight: 700; transition: 0.3s; min-width: 60px; text-align: center;">{{ ep.episode_number }}</a>
                {% empty %}
                <p style="color: var(--text-muted);">Qismlar hozircha mavjud emas.</p>
                {% endfor %}
            </div>
        </div>
    </div>
</main>
{% endblock %}
"""

chat_html = """{% extends "base.html" %}
{% block content %}
<main class="main-content" style="max-width: 800px; margin: 80px auto; display: flex; flex-direction: column; height: 75vh;">
    <div style="background: var(--surface-color); border: 1px solid var(--border-color); border-radius: var(--radius-lg) var(--radius-lg) 0 0; padding: 20px; border-bottom: none;">
        <h2>Umumiy Chat</h2>
    </div>
    <div style="flex: 1; background: rgba(0,0,0,0.2); border-left: 1px solid var(--border-color); border-right: 1px solid var(--border-color); padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px;">
        {% for msg in messages %}
        <div style="background: var(--surface-color); padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; margin-bottom: 8px;">
                <span style="font-weight:700; color:var(--primary-color);">{{ msg.user.username }}</span>
                <span style="color:var(--text-muted); font-size:0.8rem;">{{ msg.local_created_at }}</span>
            </div>
            <div>{{ msg.message }}</div>
        </div>
        {% empty %}
        <div style="text-align:center; color:var(--text-muted); margin-top:50px;">Hech qanday xabar yo'q. Birinchi bo'lib yozing!</div>
        {% endfor %}
    </div>
    
    <div style="background: var(--surface-color); border: 1px solid var(--border-color); border-radius: 0 0 var(--radius-lg) var(--radius-lg); padding: 20px;">
        <form method="POST" style="display:flex; gap:15px;">
            {% csrf_token %}
            <input type="text" name="message" placeholder="Xabar yozing..." required style="flex:1; padding:15px; border-radius:12px; background:rgba(0,0,0,0.3); border:1px solid var(--border-color); color:#fff; outline:none;">
            <button type="submit" style="padding:15px 30px; background:var(--primary-color); border:none; border-radius:12px; color:#fff; font-weight:700; cursor:pointer;"><i class='bx bx-send'></i> Yuborish</button>
        </form>
    </div>
</main>
{% endblock %}
"""


with open('my_app/templates/base.html', 'w', encoding='utf-8') as f: f.write(base_html)
with open('my_app/templates/home.html', 'w', encoding='utf-8') as f: f.write(home_html)
with open('my_app/templates/login.html', 'w', encoding='utf-8') as f: f.write(login_html)
with open('my_app/templates/register.html', 'w', encoding='utf-8') as f: f.write(register_html)
with open('my_app/templates/profile.html', 'w', encoding='utf-8') as f: f.write(profile_html)
with open('my_app/templates/search.html', 'w', encoding='utf-8') as f: f.write(search_html)
with open('my_app/templates/movie_detail.html', 'w', encoding='utf-8') as f: f.write(movie_detail)
with open('my_app/templates/chat.html', 'w', encoding='utf-8') as f: f.write(chat_html)

