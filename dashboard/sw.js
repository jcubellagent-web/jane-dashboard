/**
 * Jane Dashboard Service Worker
 * Network-first for HTML, cache static assets only
 */

const CACHE_NAME = 'jane-dashboard-v6.0';

// Only cache truly static assets - NOT HTML files
const ASSETS_TO_CACHE = [
    '/manifest.json',
    '/icon-192.png',
    '/icon-512.png'
];

// Install - cache only static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(ASSETS_TO_CACHE))
            .then(() => self.skipWaiting())
    );
});

// Activate - clean old caches immediately
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME)
                    .map((name) => caches.delete(name))
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch - ALWAYS network for HTML, cache for static only
self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') return;

    const url = new URL(event.request.url);
    
    // HTML files - ALWAYS go to network, no caching
    if (url.pathname.endsWith('.html') || 
        url.pathname === '/' || 
        url.pathname.endsWith('/')) {
        event.respondWith(
            fetch(event.request, { cache: 'no-store' })
                .catch(() => new Response('Offline - please reconnect', { 
                    status: 503,
                    headers: { 'Content-Type': 'text/html' }
                }))
        );
        return;
    }

    // API calls - always network
    if (url.pathname.includes('/api/') || 
        url.pathname.endsWith('.json') ||
        url.hostname !== self.location.hostname) {
        return;
    }

    // Static assets - network first with cache fallback
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                const responseClone = response.clone();
                caches.open(CACHE_NAME)
                    .then((cache) => cache.put(event.request, responseClone));
                return response;
            })
            .catch(() => caches.match(event.request))
    );
});
