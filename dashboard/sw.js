/**
 * Jane Dashboard Service Worker
 * Enables offline access and caching
 */

const CACHE_NAME = 'jane-dashboard-v4.2';
const ASSETS_TO_CACHE = [
    '/',
    '/index.html',
    '/manifest.json',
    '/icon-192.png',
    '/icon-512.png',
    '/kanban/',
    '/kanban/index.html',
    '/notes/',
    '/notes/index.html',
    '/links/',
    '/links/index.html',
    '/settings/',
    '/settings/index.html',
    '/timer/',
    '/timer/index.html',
    '/api.js'
];

// Install - cache assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(ASSETS_TO_CACHE))
            .then(() => self.skipWaiting())
    );
});

// Activate - clean old caches
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

// Fetch - network first, fall back to cache
self.addEventListener('fetch', (event) => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') return;

    // Skip API calls and JSON files (they should always go to network)
    const url = new URL(event.request.url);
    if (url.pathname.includes('/hooks/') || 
        url.pathname.endsWith('.json') ||
        url.pathname.includes('/api/') ||
        url.hostname === 'api.coingecko.com' ||
        url.hostname === 'wttr.in') {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Clone the response for caching
                const responseClone = response.clone();
                caches.open(CACHE_NAME)
                    .then((cache) => cache.put(event.request, responseClone));
                return response;
            })
            .catch(() => {
                // Fall back to cache
                return caches.match(event.request)
                    .then((response) => response || new Response('Offline', { status: 503 }));
            })
    );
});
