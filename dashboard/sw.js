// Jane Dashboard — Service Worker for Push Notifications
const CACHE_NAME = 'jane-dash-v1';

// Install
self.addEventListener('install', (event) => {
    self.skipWaiting();
});

// Activate
self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});

// Push notification received
self.addEventListener('push', (event) => {
    let data = { title: 'Jane', body: 'New notification', icon: '/icon-192v2.png', badge: '/icon-192v2.png' };
    
    if (event.data) {
        try {
            const payload = event.data.json();
            data = {
                title: payload.title || 'Jane',
                body: payload.body || '',
                icon: payload.icon || '/icon-192v2.png',
                badge: '/icon-192v2.png',
                tag: payload.tag || 'jane-default',
                data: payload.data || {},
                actions: payload.actions || [],
                vibrate: [100, 50, 100],
                renotify: true
            };
        } catch (e) {
            data.body = event.data.text();
        }
    }

    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: data.icon,
            badge: data.badge,
            tag: data.tag,
            data: data.data,
            actions: data.actions,
            vibrate: data.vibrate,
            renotify: data.renotify
        })
    );
});

// Notification click — open dashboard
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    const url = event.notification.data?.url || '/mobile.html';
    
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
            // Focus existing tab if open
            for (const client of clientList) {
                if (client.url.includes('mobile.html') && 'focus' in client) {
                    return client.focus();
                }
            }
            // Otherwise open new tab
            return clients.openWindow(url);
        })
    );
});
