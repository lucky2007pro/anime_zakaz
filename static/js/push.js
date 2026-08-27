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

async function subscribeToPush() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn("Bu brauzer push notificationni qo'llab-quvvatlamaydi");
        return;
    }

    try {
        const registration = await navigator.serviceWorker.ready;
        let subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
            const permission = await Notification.requestPermission();
            if (permission !== 'granted') {
                console.log("Foydalanuvchi bildirishnomaga ruxsat bermadi");
                return;
            }
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
            });
        }

        await fetch('/save-push-subscription/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(subscription)
        });

        console.log("Push obuna muvaffaqiyatli saqlandi ✅");
    } catch (err) {
        console.error("Push obuna xatosi:", err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (window.USER_AUTHENTICATED === true) {
        subscribeToPush();
    }
});