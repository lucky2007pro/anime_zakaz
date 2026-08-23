{% extends 'base.html' %}
{% load static %}

{% block title %}Kirish - BESTMEDIA{% endblock %}

{% block footer %}{% endblock %}

{% block extra_css %}
<style>
    html, body {
        height: 100%;
        overflow: hidden;
    }

    .bg-video,
    .bg-image {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: -1;
        opacity: 0.3;
    }

    .login-page-bg {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image: url('https://i.pinimg.com/1200x/24/cc/79/24cc79ebb34bf6124aae128865fde531.jpg');
        background-size: cover;
        background-position: center;
        z-index: -2;
    }

    .login-page-bg::after {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(180deg, rgba(5,8,12,0.45) 0%, rgba(5,8,12,0.3) 50%, rgba(5,8,12,0.55) 100%);
    }

    .auth-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100dvh;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 16px;
        box-sizing: border-box;
        overflow: hidden;
    }

    .auth-container {
        background: rgba(10, 14, 20, 0.25);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(0, 243, 255, 0.15);
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4);
        width: 100%;
        max-width: 420px;
        max-height: calc(100dvh - 32px);
        overflow-y: auto;
    }

    .auth-title-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-bottom: 10px;
        flex-wrap: wrap;
    }

    .auth-title-row .auth-icon {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid var(--accent);
        box-shadow: 0 0 12px rgba(0, 243, 255, 0.4);
    }

    .messages {
        list-style: none;
        margin-bottom: 20px;
    }

    .messages li {
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        text-align: center;
        font-weight: 600;
    }

    .messages li.success { background: rgba(40, 167, 69, 0.2); border: 1px solid #28a745; color: #28a745; }
    .messages li.error { background: rgba(220, 53, 69, 0.2); border: 1px solid #dc3545; color: #dc3545; }

    .input-box {
        position: relative;
        margin-bottom: 20px;
    }

    .input-box .form-control {
        background: rgba(255, 255, 255, 0.03);
    }

    .input-box i {
        position: absolute;
        right: 15px;
        top: 50%;
        transform: translateY(-50%);
        color: var(--text-dim);
        font-size: 1.2rem;
    }

    .input-box .toggle-password {
        right: 45px;
        cursor: pointer;
    }

    .input-box .toggle-password:hover {
        color: var(--accent);
    }

    /* =========================================================
       FOYDALANISH SHARTLARI — checkbox qatori
       ========================================================= */

    .terms-agree-row {
        display: flex;
        align-items: flex-start;
        gap: 9px;
        margin-bottom: 22px;
        font-size: 0.85rem;
        color: var(--text-dim);
        line-height: 1.4;
    }

    .terms-agree-row input[type="checkbox"] {
        margin-top: 3px;
        width: 16px;
        height: 16px;
        flex-shrink: 0;
        accent-color: var(--accent);
        cursor: pointer;
    }

    .terms-agree-row label {
        cursor: pointer;
    }

    .terms-warn-toast {
        position: fixed;
        top: 24px;
        left: 50%;
        transform: translateX(-50%) translateY(-20px);
        z-index: 1200;

        display: flex;
        align-items: center;
        gap: 8px;

        background: rgba(220, 53, 69, 0.15);
        border: 1px solid rgba(220, 53, 69, 0.45);
        color: #ff8a94;

        padding: 12px 18px;
        border-radius: 10px;

        font-weight: 700;
        font-size: 0.9rem;

        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);

        opacity: 0;
        pointer-events: none;
        transition: opacity 0.25s ease, transform 0.25s ease;
    }

    .terms-warn-toast i {
        font-size: 1.2rem;
        flex-shrink: 0;
    }

    .terms-warn-toast.show {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
    }

    .terms-link {
        color: var(--accent);
        text-decoration: underline;
        font-weight: 700;
        cursor: pointer;
        background: none;
        border: none;
        padding: 0;
        font-size: inherit;
        font-family: inherit;
    }

    .login-link {
        text-align: center;
        margin-top: 20px;
        font-size: 0.9rem;
        color: var(--text-dim);
    }

    .glow-underline-wrap {
        display: inline-block;
        position: relative;
        margin-top: 4px;
        margin-left: 4px;
    }

    .glow-underline-link {
        position: relative;
        display: inline-block;
        color: var(--accent);
        text-decoration: none;
        font-weight: 700;
        font-size: 0.95rem;
        padding-bottom: 4px;
    }

    /* Doimiy (statik) past chiziq — fon sifatida */
    .glow-underline-link::before {
        content: '';
        position: absolute;
        left: 0;
        bottom: 0;
        width: 100%;
        height: 1px;
        background: rgba(0, 243, 255, 0.2);
    }

    /* Harakatlanuvchi glow segment */
    .glow-underline-link::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 40%;
        height: 2px;
        border-radius: 2px;
        background: var(--accent);
        box-shadow:
            0 0 6px var(--accent),
            0 0 14px var(--accent),
            0 0 22px rgba(0, 243, 255, 0.6);
        animation: glowSweep 2.6s ease-in-out infinite;
    }

    @keyframes glowSweep {
        0%   { left: 0%;   transform: translateX(0); }
        50%  { left: 100%; transform: translateX(-100%); }
        100% { left: 0%;   transform: translateX(0); }
    }

    .telegram-link {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin-top: 14px;
        padding: 10px;
        border-radius: 10px;
        background: rgba(0, 136, 204, 0.12);
        border: 1px solid rgba(0, 136, 204, 0.3);
        color: #2aabee;
        font-weight: 700;
        font-size: 0.9rem;
        text-decoration: none;
        transition: 0.2s;
    }

    .telegram-link i {
        font-size: 1.3rem;
    }

    .telegram-link:hover {
        background: rgba(0, 136, 204, 0.22);
    }

    .login-link a {
        color: var(--accent);
        text-decoration: none;
        font-weight: 600;
    }

    .login-link a:hover {
        text-decoration: underline;
    }

    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0,0,0,0);
        border: 0;
    }

    @media (max-width: 768px) {
        .auth-wrapper { padding: 12px; }
        .auth-container { padding: 22px 18px; }
        .login-link { font-size: 0.85rem; }
        .messages li { font-size: 0.9rem; }
    }

    @media (max-width: 480px) {
        .auth-container { padding: 18px 14px; }
        .auth-container h2 { font-size: 1.35rem; }
    }

    @media (max-height: 640px) {
        .auth-title-row { margin-bottom: 6px; }
        .auth-title-row .auth-icon { width: 38px; height: 38px; }
        .auth-container p { margin-bottom: 16px !important; }
        .input-box { margin-bottom: 14px; }
        .terms-agree-row { margin-bottom: 16px; }
        .login-link { margin-top: 12px; }
    }

    /* =========================================================
       FOYDALANISH SHARTLARI — TO'LIQ EKRAN OYNASI
       ========================================================= */

    .terms-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100dvh;
        z-index: 999;
        background: #05070b;
        display: none;
        flex-direction: column;
        overflow: hidden;
    }

    .terms-overlay.active {
        display: flex;
    }

    .terms-back-bar {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 16px 18px;
        background: rgba(10, 14, 20, 0.9);
        border-bottom: 1px solid rgba(0, 243, 255, 0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    .terms-back-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 243, 255, 0.1);
        border: 1px solid rgba(0, 243, 255, 0.25);
        color: var(--accent);
        font-weight: 800;
        font-size: 0.95rem;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        transition: 0.2s;
    }

    .terms-back-btn:hover {
        background: rgba(0, 243, 255, 0.2);
    }

    .terms-back-bar h3 {
        margin: 0;
        color: #fff;
        font-size: 1.05rem;
        font-weight: 800;
    }

    .terms-body {
        flex: 1 1 auto;
        overflow-y: auto;
        padding: 24px 18px 60px;
        -webkit-overflow-scrolling: touch;
    }

    .terms-content {
        max-width: 720px;
        margin: 0 auto;
        color: rgba(255, 255, 255, 0.85);
        line-height: 1.7;
        font-size: 0.95rem;
    }

    .terms-content h1 {
        color: var(--accent);
        font-size: 1.5rem;
        margin: 0 0 6px;
        font-weight: 900;
    }

    .terms-content .terms-updated {
        color: var(--text-dim);
        font-size: 0.8rem;
        margin-bottom: 26px;
    }

    .terms-content h2 {
        color: #fff;
        font-size: 1.1rem;
        font-weight: 800;
        margin: 26px 0 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .terms-content h2 .num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: rgba(0, 243, 255, 0.12);
        border: 1px solid rgba(0, 243, 255, 0.3);
        color: var(--accent);
        font-size: 0.8rem;
        flex-shrink: 0;
    }

    .terms-content p {
        margin: 0 0 12px;
    }

    .terms-content ul {
        margin: 0 0 12px;
        padding-left: 20px;
    }

    .terms-content ul li {
        margin-bottom: 8px;
    }

    .terms-warning-box {
        background: rgba(220, 53, 69, 0.1);
        border: 1px solid rgba(220, 53, 69, 0.35);
        border-radius: 10px;
        padding: 14px 16px;
        margin: 16px 0;
    }

    .terms-warning-box strong {
        color: #ff6b7a;
        display: block;
        margin-bottom: 6px;
        font-size: 0.95rem;
    }

    .terms-warning-box p {
        margin: 0;
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.9rem;
    }

    .terms-final-note {
        margin-top: 28px;
        padding-top: 18px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        color: var(--text-dim);
        font-size: 0.85rem;
        font-style: italic;
    }
</style>
{% endblock %}

{% block content %}
<div class="login-page-bg"></div>
<main class="main-content" style="margin-top: 0;">
    <div class="auth-wrapper">
        <div class="auth-container">
            <div class="auth-title-row">
                <h2 style="color:var(--accent); font-size:2rem; margin:0;">Kirish</h2>
                <img src="https://i.pinimg.com/736x/21/6f/47/216f4718f7675003001a16e35585975e.jpg" alt="BESTMEDIA" class="auth-icon">
            </div>
            <p style="text-align:center; color:var(--text-dim); margin-bottom:30px; font-weight:600;">BESTMEDIA ga xush kelibsiz!</p>

            {% if messages %}
            <ul class="messages">
                {% for message in messages %}
                <li class="{{ message.tags }}">{{ message }}</li>
                {% endfor %}
            </ul>
            {% endif %}

            <form id="loginForm" action="{% url 'login' %}" method="post">
                {% csrf_token %}

                <div class="input-box form-group">
                    <label class="sr-only" for="username">Username</label>
                    <input type="text" id="username" name="username" class="form-control" placeholder="Username" required autocomplete="username">
                    <i class='bx bx-user-circle'></i>
                </div>

                <div class="input-box form-group">
                    <label class="sr-only" for="password">Parol</label>
                    <input type="password" id="password" name="password" class="form-control" placeholder="Parol" required autocomplete="current-password">
                    <i class='bx bxs-low-vision toggle-password' id="togglePassword1"></i>
                    <i class='bx bx-lock'></i>
                </div>

                <div class="terms-agree-row">
                    <input type="checkbox" id="agreeTerms">
                    <label for="agreeTerms">
                        Men <button type="button" class="terms-link" id="openTermsBtn">Foydalanish shartlari</button> bilan tanishdim va ularga to'liq roziman
                    </label>
                </div>

                <button type="submit" class="btn-submit">Kirish</button>

                <div class="login-link">
                    Akkountingiz yo'qmi?
                    <span class="glow-underline-wrap">
                        <a href="{% url 'register' %}" class="glow-underline-link">
                            Ro'yxatdan o'tish
                        </a>
                    </span>
                </div>

                <a href="https://t.me/ani_best_uzb_anime" target="_blank" rel="noopener" class="telegram-link">
                    <i class='bx bxl-telegram'></i>
                    <span>Telegram kanalimiz</span>
                </a>
            </form>
        </div>
    </div>
</main>

<div class="terms-warn-toast" id="termsWarnToast">
    <i class='bx bx-error-circle'></i>
    <span>Avval Foydalanish shartlariga rozilik bering!</span>
</div>

<!-- =====================================================
     FOYDALANISH SHARTLARI — TO'LIQ EKRAN OYNASI
     ===================================================== -->
<div class="terms-overlay" id="termsOverlay">
    <div class="terms-back-bar">
        <button type="button" class="terms-back-btn" id="closeTermsBtn">
            <i class='bx bx-arrow-back'></i> Orqaga
        </button>
        <h3>Foydalanish shartlari</h3>
    </div>

    <div class="terms-body">
        <div class="terms-content">
            <h1>ANIBEST — Foydalanish shartlari</h1>
            <p class="terms-updated">So'nggi yangilangan sana: 2026-yil</p>

            <p>
                Ushbu Foydalanish shartlari (keyingi o'rinlarda — "Shartlar") ANIBEST / BESTMEDIA
                platformasidan ("Sayt", "Xizmat") foydalanuvchi ("Foydalanuvchi", "Siz") o'rtasidagi
                huquq va majburiyatlarni belgilaydi. Saytda ro'yxatdan o'tish yoki undan foydalanish
                orqali Siz quyidagi barcha shartlarga to'liq va so'zsiz rozilik bildirasiz.
            </p>

            <h2><span class="num">1</span> Umumiy qoidalar</h2>
            <p>
                Sayt anime kontentini onlayn tomosha qilish uchun mo'ljallangan platforma hisoblanadi.
                Saytdan foydalanish uchun Foydalanuvchi 13 yoshdan katta bo'lishi va ushbu Shartlarni
                to'liq o'qib chiqqan bo'lishi shart. Agar Siz ushbu shartlarning biror qismiga rozi
                bo'lmasangiz, Saytdan foydalanishni to'xtatishingiz lozim.
            </p>

            <h2><span class="num">2</span> Kontentdan foydalanish tartibi</h2>
            <p>
                Saytdagi barcha anime, video, rasm, musiqa va matn materiallari mualliflik huquqi
                bilan himoyalangan bo'lib, faqat shaxsiy, notijorat maqsadlarda, faqat Sayt ichida
                tomosha qilish uchun taqdim etiladi. Kontentdan foydalanish quyidagi tartibda amalga
                oshiriladi:
            </p>
            <ul>
                <li>Kontentni faqat Saytning o'zida, tegishli obuna darajasiga (Oddiy / Premium / VIP) mos ravishda tomosha qilish mumkin;</li>
                <li>Kontentni ish yuritish, ta'lim yoki tijorat maqsadlarida ishlatish taqiqlanadi;</li>
                <li>Kontentga texnik himoya vositalarini (DRM, chegaralovchi kodlar va h.k.) chetlab o'tishga urinish taqiqlanadi.</li>
            </ul>

            <h2><span class="num">3</span> Ruxsatsiz olish va tarqatish taqiqi</h2>
            <p>
                Saytdagi anime kontentini <strong>mualliflik huquqi egasi yoki Sayt ma'muriyatining
                yozma ruxsatisiz</strong> quyidagi shakllarda foydalanish qat'iyan taqiqlanadi:
            </p>
            <ul>
                <li>Videoni yuklab olish, ekrandan yozib olish (screen recording) yoki boshqa usulda nusxa ko'chirish;</li>
                <li>Nusxa ko'chirilgan kontentni ijtimoiy tarmoqlarda, Telegram kanal/guruhlarda, boshqa saytlarda yoki messenjerlarda tarqatish, qayta yuklash yoki ulashish;</li>
                <li>Kontentni sotish, ijaraga berish, boshqa platformalarda joylashtirish yoki undan tijorat maqsadida foydalanish;</li>
                <li>Akkount ma'lumotlarini (login, parol, obuna huquqini) uchinchi shaxslarga sotish yoki bepul tarqatish.</li>
            </ul>

            <div class="terms-warning-box">
                <strong>⚠ Diqqat</strong>
                <p>
                    Yuqorida sanab o'tilgan har qanday harakat mualliflik huquqini buzish hisoblanadi
                    va O'zbekiston Respublikasi qonunchiligiga muvofiq javobgarlikka sabab bo'ladi.
                </p>
            </div>

            <h2><span class="num">4</span> Javobgarlik va jarimalar</h2>
            <p>
                O'zbekiston Respublikasining "Mualliflik huquqi va turdosh huquqlar to'g'risida"gi
                Qonuniga hamda amaldagi Ma'muriy javobgarlik to'g'risidagi va Jinoyat kodeksiga
                muvofiq, mualliflik huquqi bilan himoyalangan kontentni ruxsatsiz nusxalash,
                tarqatish yoki tijorat maqsadida foydalanish quyidagi javobgarlikka olib kelishi
                mumkin:
            </p>
            <ul>
                <li><strong>Ma'muriy javobgarlik</strong> — qonun hujjatlarida belgilangan miqdorda jarima solinishi;</li>
                <li><strong>Fuqarolik-huquqiy javobgarlik</strong> — mualliflik huquqi egasiga yetkazilgan zararni to'liq qoplash;</li>
                <li><strong>Jinoyiy javobgarlik</strong> — katta miqdorda zarar yetkazilgan yoki takroran sodir etilgan holatlarda, qonunda nazarda tutilgan tartibda.</li>
            </ul>
            <p>
                Bundan tashqari, Sayt ma'muriyati ushbu qoidalarni buzgan Foydalanuvchining
                akkountini ogohlantirishsiz bloklash, obunasini bekor qilish va kelgusida saytdan
                foydalanishini butunlay taqiqlash huquqini o'zida saqlab qoladi.
            </p>

            <h2><span class="num">5</span> Foydalanuvchi majburiyatlari</h2>
            <ul>
                <li>Ro'yxatdan o'tishda haqiqiy va aniq ma'lumotlar taqdim etish;</li>
                <li>O'z akkounti va parolining maxfiyligini ta'minlash, uni uchinchi shaxslarga bermaslik;</li>
                <li>Chat, izoh va boshqa interaktiv bo'limlarda boshqa foydalanuvchilarni haqorat qilmaslik, spam va reklama tarqatmaslik;</li>
                <li>Saytning ishlashiga zarar yetkazadigan (viruslar, avtomatlashtirilgan botlar, DDoS va h.k.) har qanday harakatlardan tiyilish.</li>
            </ul>

            <h2><span class="num">6</span> Obuna va to'lovlar</h2>
            <p>
                Premium va VIP obunalar to'lov asosida taqdim etiladi. To'lov cheki tasdiqlangandan
                so'ng tegishli tarif imkoniyatlari faollashtiriladi. Noto'g'ri yoki soxta to'lov
                cheki yuborilgan taqdirda, Sayt ma'muriyati so'rovni rad etish va akkountga nisbatan
                cheklov qo'llash huquqiga ega.
            </p>

            <h2><span class="num">7</span> Shartlarga o'zgartirish kiritish</h2>
            <p>
                Sayt ma'muriyati ushbu Shartlarga istalgan vaqtda o'zgartirish kiritish huquqiga
                ega. Yangilangan shartlar Saytda e'lon qilingan kundan boshlab kuchga kiradi.
                Saytdan foydalanishni davom ettirish yangilangan shartlarga rozilik sifatida talqin
                etiladi.
            </p>

            <h2><span class="num">8</span> Yakuniy qoida</h2>
            <p>
                Ro'yxatdan o'tish yoki tizimga kirish tugmasini bosish orqali Siz ushbu Foydalanish
                shartlarining barcha bandlari bilan tanishganingizni, ularni tushunganingizni va
                ularga <strong>to'liq va so'zsiz rozi</strong> ekanligingizni tasdiqlaysiz.
            </p>

            <p class="terms-final-note">
                Savollaringiz bo'lsa, "Aloqa" bo'limi orqali Sayt ma'muriyati bilan bog'lanishingiz mumkin.
            </p>
        </div>
    </div>
</div>

<script>
    const togglePassword1 = document.getElementById("togglePassword1");
    const password = document.getElementById("password");

    if (togglePassword1) {
        togglePassword1.addEventListener("click", function () {
            password.type = password.type === "password" ? "text" : "password";
            this.classList.toggle('active');
        });
    }

    const termsOverlay = document.getElementById('termsOverlay');
    const openTermsBtn = document.getElementById('openTermsBtn');
    const closeTermsBtn = document.getElementById('closeTermsBtn');

    if (openTermsBtn) {
        openTermsBtn.addEventListener('click', function () {
            termsOverlay.classList.add('active');
        });
    }

    if (closeTermsBtn) {
        closeTermsBtn.addEventListener('click', function () {
            termsOverlay.classList.remove('active');
        });
    }

    const form = document.getElementById('loginForm');
    const agreeTerms = document.getElementById('agreeTerms');
    const termsWarnToast = document.getElementById('termsWarnToast');
    let toastTimer = null;

    function showTermsWarn() {
        clearTimeout(toastTimer);
        termsWarnToast.classList.add('show');
        toastTimer = setTimeout(() => {
            termsWarnToast.classList.remove('show');
        }, 2000);
    }

    if (form) {
        form.addEventListener('submit', function (e) {
            if (!agreeTerms.checked) {
                e.preventDefault();
                showTermsWarn();
            }
        });
    }
</script>
{% endblock %}
