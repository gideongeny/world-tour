// World Tour Service Worker
const CACHE_NAME = 'world-tour-v2.0.0';
const STATIC_CACHE = 'static-v2.0.0';
const DYNAMIC_CACHE = 'dynamic-v2.0.0';
const API_CACHE = 'api-v2.0.0';

// Files to cache immediately
const STATIC_FILES = [
    '/',
    '/static/style.css',
    '/static/script.js',
    '/static/manifest.json',
    '/static/favicon.ico',
    '/static/icons/icon-144x144.png',
    '/static/icons/icon-180x180.png',
    '/static/icons/icon-512x512.png',
    '/templates/base.html',
    '/templates/index.html',
    '/templates/travel.html',
    '/templates/search.html',
    '/templates/flights.html',
    '/templates/hotels.html',
    '/templates/packages.html',
    '/templates/profile.html',
    '/templates/login.html',
    '/templates/register.html'
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/destinations',
    '/api/weather/',
    '/api/v1/destinations',
    '/search',
    '/flights',
    '/hotels',
    '/packages'
];

// Install event - cache static files
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('Static files cached successfully');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('Error caching static files:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && 
                            cacheName !== DYNAMIC_CACHE && 
                            cacheName !== API_CACHE) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Handle API requests
    if (url.pathname.startsWith('/api/') || 
        url.pathname.startsWith('/search') ||
        url.pathname.startsWith('/flights') ||
        url.pathname.startsWith('/hotels') ||
        url.pathname.startsWith('/packages')) {
        event.respondWith(handleApiRequest(request));
        return;
    }

    // Handle static files
    if (url.pathname.startsWith('/static/') || 
        url.pathname.startsWith('/templates/') ||
        url.pathname === '/') {
        event.respondWith(handleStaticRequest(request));
        return;
    }

    // Handle HTML pages
    if (request.headers.get('accept').includes('text/html')) {
        event.respondWith(handleHtmlRequest(request));
        return;
    }

    // Default: network first, fallback to cache
    event.respondWith(handleDefaultRequest(request));
});

// Handle API requests with cache-first strategy
async function handleApiRequest(request) {
    try {
        // Try cache first
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            // Check if cache is fresh (less than 5 minutes old)
            const cacheTime = new Date(cachedResponse.headers.get('sw-cache-time'));
            const now = new Date();
            if (now - cacheTime < 5 * 60 * 1000) { // 5 minutes
                return cachedResponse;
            }
        }

        // Fetch from network
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Clone response and add cache timestamp
            const responseToCache = networkResponse.clone();
            const headers = new Headers(responseToCache.headers);
            headers.append('sw-cache-time', new Date().toISOString());
            
            const responseWithTime = new Response(responseToCache.body, {
                status: responseToCache.status,
                statusText: responseToCache.statusText,
                headers: headers
            });

            // Cache the response
            const cache = await caches.open(API_CACHE);
            await cache.put(request, responseWithTime);
        }

        return networkResponse;
    } catch (error) {
        // Fallback to cached response if available
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline response
        return new Response(JSON.stringify({
            error: 'Network error',
            message: 'Please check your connection and try again'
        }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

// Handle static files with cache-first strategy
async function handleStaticRequest(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            await cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        return new Response('Static file not available offline', {
            status: 404,
            headers: { 'Content-Type': 'text/plain' }
        });
    }
}

// Handle HTML requests with network-first strategy
async function handleHtmlRequest(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            await cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page
        return caches.match('/templates/offline.html');
    }
}

// Handle default requests with network-first strategy
async function handleDefaultRequest(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            await cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        return new Response('Resource not available offline', {
            status: 404,
            headers: { 'Content-Type': 'text/plain' }
        });
    }
}

// Background sync for offline actions
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

async function doBackgroundSync() {
    try {
        // Sync offline bookings
        const offlineBookings = await getOfflineBookings();
        for (const booking of offlineBookings) {
            await syncBooking(booking);
        }
        
        // Sync offline reviews
        const offlineReviews = await getOfflineReviews();
        for (const review of offlineReviews) {
            await syncReview(review);
        }
        
        console.log('Background sync completed');
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

// Push notification handling
self.addEventListener('push', event => {
    const options = {
        body: event.data ? event.data.text() : 'New notification from World Tour',
        icon: '/static/icons/icon-144x144.png',
        badge: '/static/icons/icon-32x32.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Details',
                icon: '/static/icons/icon-32x32.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/icons/icon-32x32.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('World Tour', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    event.notification.close();

    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Helper functions for offline data
async function getOfflineBookings() {
    // Implementation for getting offline bookings from IndexedDB
    return [];
}

async function syncBooking(booking) {
    // Implementation for syncing offline booking to server
    console.log('Syncing booking:', booking);
}

async function getOfflineReviews() {
    // Implementation for getting offline reviews from IndexedDB
    return [];
}

async function syncReview(review) {
    // Implementation for syncing offline review to server
    console.log('Syncing review:', review);
}

// Message handling for communication with main thread
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(STATIC_CACHE)
                .then(cache => cache.addAll(event.data.urls))
        );
    }
});
