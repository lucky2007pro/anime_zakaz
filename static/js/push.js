const VAPID_PUBLIC_KEY = "BIV_qRywliALoRuqskqFzPIu-uhA6YPVMV0zo9PWAqt4SDiHvXIuAvcD6iO32Q5BJ0J-bSEX9eUeAU5jdy0RsnI";

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = atob(base64);
    return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

async function subscribeToPush(showPromptIfDefault = false) {
    if (!('serviceWorker' in navigator) || !('PushManager' in window) || !('Notification' in window)) {
        console.warn("Bu brauzer push bildirishnomalarni qo'llab-quvvatlamaydi");
        return { success: false, reason: 'unsupported' };
    }

    try {
        let perm = Notification.permission;
        if (perm === 'denied') {
            console.warn("Bildirishnomalarga brauzer sozlamalarida taqiq qo'yilgan");
            return { success: false, reason: 'denied' };
        }

        if (perm === 'default') {
            if (!showPromptIfDefault) {
                // Avtomatik ochilganda ruxsat so'ramaymiz, faqat UI tugmasi bosilganda
                return { success: false, reason: 'default' };
            }
            perm = await Notification.requestPermission();
            if (perm !== 'granted') {
                return { success: false, reason: 'denied' };
            }
        }

        const registration = await navigator.serviceWorker.ready;
        let subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
            });
        }

        const res = await fetch('/save-push-subscription/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(subscription)
        });

        if (res.ok) {
            console.log("Push obuna muvaffaqiyatli saqlandi ✅");
            window.dispatchEvent(new CustomEvent('push-subscription-changed', { detail: { state: 'granted' } }));
            return { success: true, reason: 'granted' };
        } else {
            console.warn("Obuna serverda saqlanmadi:", res.status);
            return { success: false, reason: 'server_error' };
        }
    } catch (err) {
        console.error("Push obuna xatosi:", err);
        return { success: false, reason: err.message };
    }
}

function checkPushStatus() {
    if (!('serviceWorker' in navigator) || !('Notification' in window)) {
        return 'unsupported';
    }
    return Notification.permission; // 'granted', 'denied', 'default'
}

window.subscribeToPush = subscribeToPush;
window.checkPushStatus = checkPushStatus;

document.addEventListener('DOMContentLoaded', () => {
    // Agar foydalanuvchi tizimga kirgan bo'lsa va oldin ruxsat bergan bo'lsa, obunani yangilab qo'yamiz
    if (window.USER_AUTHENTICATED === true) {
        if (checkPushStatus() === 'granted') {
            subscribeToPush(false);
        }
    }
});