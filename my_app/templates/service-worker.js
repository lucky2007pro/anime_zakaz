/* ==========================================================================
   BESTMEDIA — Service Worker
   Vazifasi: home.html va base.html "qobig'ini" (dizayn, CSS, JS) offline
   ishlashi uchun keshlab qo'yish. Video, rasm, izohlar kabi og'ir/tez
   o'zgaruvchi narsalar BU YERDA KESHLANMAYDI — faqat sahifa qobig'i.

   MUHIM: Har safar base.html yoki home.html'ni jiddiy o'zgartirsangiz,
   CACHE_VERSION raqamini oshiring (v1 -> v2), aks holda foydalanuvchilar
   eski versiyani ko'rishda davom etadi.
========================================================================== */

const CACHE_VERSION   = 'v1';
const SHELL_CACHE      = 'bm-shell-' + CACHE_VERSION;
const RUNTIME_CACHE    = 'bm-runtime-' + CACHE_VERSION;
const OFFLINE_URL       = '/offline/';   // Django urls.py'da shu manzilga view qo'shing (pastda tushuntiraman)

/* Birinchi o'rnatishda oldindan keshlanadigan sahifalar/manbalar.
   '/' — home sahifa. Agar boshqa doim kerak bo'ladigan sahifa
   bo'lsa (masalan katalog), shu ro'yxatga qo'shing. */
const PRECACHE_URLS = [
    '/',
    OFFLINE_URL,
    'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&display=swap',
    'https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css',
];

/* ---------------------------------------------------------------
   INSTALL — dastlabki keshni tayyorlash
--------------------------------------------------------------- */
self.addEventListener('install', function (event) {
    event.waitUntil(
        caches.open(SHELL_CACHE).then(function (cache) {
            return cache.addAll(PRECACHE_URLS).catch(function (err) {
                // Ba'zi resurslar (masalan tashqi CDN) bloklansa ham
                // o'rnatish to'xtab qolmasin
                console.warn('SW precache xatosi:', err);
            });
        }).then(function () {
            return self.skipWaiting();
        })
    );
});


/* ==========================================================================
   PUSH NOTIFICATION
   Bu qism yuqoridagi offline-cache logikasidan MUSTAQIL ishlaydi —
   fetch bilan aralashmaydi, shuning uchun xavfsiz qo'shildi.
========================================================================== */

self.addEventListener('push', function (event) {
    let data = { title: "BESTMEDIA", body: "Yangi xabar bor!", url: "/" };

    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body: data.body,
        icon: '/static/images/favicon-192x192.png',
        badge: '/static/images/favicon-48x48.png',
        vibrate: [200, 100, 200],
        data: { url: data.url || '/' }
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();
    const url = event.notification.data.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function (clientList) {
            for (const client of clientList) {
                if (client.url === url && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(url);
            }
        })
    );
});

/* ---------------------------------------------------------------
   ACTIVATE — eski kesh versiyalarini tozalash
--------------------------------------------------------------- */
self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys().then(function (keys) {
            return Promise.all(
                keys
                    .filter(function (key) {
                        return key !== SHELL_CACHE && key !== RUNTIME_CACHE;
                    })
                    .map(function (key) {
                        return caches.delete(key);
                    })
            );
        }).then(function () {
            return self.clients.claim();
        })
    );
});

/* ---------------------------------------------------------------
   FETCH — so'rovlarni ushlab, strategiya bo'yicha javob berish
--------------------------------------------------------------- */
self.addEventListener('fetch', function (event) {
    const req = event.request;

    // Faqat GET so'rovlarni keshlaymiz. POST (izoh qoldirish,
    // like bosish, login va h.k.) hech qachon keshlanmasligi kerak.
    if (req.method !== 'GET') return;

    const url = new URL(req.url);

    // Admin panel va media fayllarni (video, rasm) keshga tegmaymiz —
    // ular alohida (kelajakdagi "offline yuklab olish" funksiyasi) orqali boshqariladi.
    if (url.pathname.startsWith('/admin') ||
        url.pathname.startsWith('/media/') ||
        url.pathname.includes('/toggle-favorite/')) {
        return;
    }

    // 1) SAHIFA NAVIGATSIYASI (HTML) — Network-First strategiyasi:
    //    Internet bo'lsa -> eng yangi versiyani ko'rsat va keshni yangila.
    //    Internet bo'lmasa -> keshdagi eski versiyani ko'rsat.
    //    Kesh ham bo'lmasa -> offline.html.
    if (req.mode === 'navigate') {
        event.respondWith(
            fetch(req)
                .then(function (response) {
                    const clone = response.clone();
                    caches.open(RUNTIME_CACHE).then(function (cache) {
                        cache.put(req, clone);
                    });
                    return response;
                })
                .catch(function () {
                    return caches.match(req).then(function (cached) {
                        return cached || caches.match(OFFLINE_URL);
                    });
                })
        );
        return;
    }

    // 2) STATIK RESURSLAR (shriftlar, ikonkalar, CSS/JS fayllar,
    //    rasm ikonlar) — Cache-First strategiyasi (tezroq va tejamkor):
    if (
        req.destination === 'style' ||
        req.destination === 'script' ||
        req.destination === 'font' ||
        url.origin === 'https://fonts.googleapis.com' ||
        url.origin === 'https://fonts.gstatic.com' ||
        url.origin === 'https://unpkg.com'
    ) {
        event.respondWith(
            caches.match(req).then(function (cached) {
                if (cached) return cached;
                return fetch(req).then(function (response) {
                    const clone = response.clone();
                    caches.open(RUNTIME_CACHE).then(function (cache) {
                        cache.put(req, clone);
                    });
                    return response;
                });
            })
        );
        return;
    }

    // 3) Qolgan hamma narsa uchun — oddiy tarmoq so'rovi (aralashmaymiz)
});
