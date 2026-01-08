// Service Worker for World Tour PWA
const CACHE_NAME = 'world-tour-v1.0.0';
const STATIC_CACHE = 'static-v1';
const DYNAMIC_CACHE = 'dynamic-v1';
const API_CACHE = 'api-v1';

// Files to cache immediately
const STATIC_FILES = [
    '/',
    '/static/css/style.css',
    '/static/js/script.js',
    '/static/images/logo.png',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    '/offline.html',
    '/manifest.json'
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/destinations',
    '/api/flights',
    '/api/hotels',
    '/api/weather',
    '/api/pricing'
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

    // Handle different types of requests
    if (request.method === 'GET') {
        // Static files
        if (isStaticFile(url.pathname)) {
            event.respondWith(cacheFirst(request, STATIC_CACHE));
        }
        // API requests
        else if (isAPIRequest(url.pathname)) {
            event.respondWith(networkFirst(request, API_CACHE));
        }
        // HTML pages
        else if (request.headers.get('accept').includes('text/html')) {
            event.respondWith(networkFirst(request, DYNAMIC_CACHE));
        }
        // Images
        else if (request.destination === 'image') {
            event.respondWith(cacheFirst(request, DYNAMIC_CACHE));
        }
        // Other requests
        else {
            event.respondWith(networkFirst(request, DYNAMIC_CACHE));
        }
    }
});

// Cache first strategy
async function cacheFirst(request, cacheName) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.error('Cache first error:', error);
        return getOfflineResponse(request);
    }
}

// Network first strategy
async function networkFirst(request, cacheName) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.error('Network first error:', error);
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        return getOfflineResponse(request);
    }
}

// Check if request is for static file
function isStaticFile(pathname) {
    return pathname.startsWith('/static/') || 
           pathname === '/' || 
           pathname === '/manifest.json';
}

// Check if request is for API
function isAPIRequest(pathname) {
    return pathname.startsWith('/api/') || 
           pathname.includes('weather') || 
           pathname.includes('pricing');
}

// Get offline response
async function getOfflineResponse(request) {
    const url = new URL(request.url);
    
    // Return offline page for HTML requests
    if (request.headers.get('accept').includes('text/html')) {
        const offlineResponse = await caches.match('/offline.html');
        if (offlineResponse) {
            return offlineResponse;
        }
    }
    
    // Return offline image for image requests
    if (request.destination === 'image') {
        const offlineImage = await caches.match('/static/images/offline-image.png');
        if (offlineImage) {
            return offlineImage;
        }
    }
    
    // Return generic offline response
    return new Response(
        JSON.stringify({
            error: 'You are offline',
            message: 'Please check your internet connection and try again.',
            timestamp: new Date().toISOString()
        }),
        {
            status: 503,
            statusText: 'Service Unavailable',
            headers: {
                'Content-Type': 'application/json'
            }
        }
    );
}

// Background sync for offline actions
self.addEventListener('sync', event => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

// Handle background sync
async function doBackgroundSync() {
    try {
        // Get pending actions from IndexedDB
        const pendingActions = await getPendingActions();
        
        for (const action of pendingActions) {
            try {
                await processPendingAction(action);
                await removePendingAction(action.id);
            } catch (error) {
                console.error('Error processing pending action:', error);
            }
        }
    } catch (error) {
        console.error('Background sync error:', error);
    }
}

// Push notification event
self.addEventListener('push', event => {
    console.log('Push notification received');
    
    let notificationData = {
        title: 'World Tour',
        body: 'You have a new notification',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        data: {
            url: '/'
        }
    };
    
    if (event.data) {
        try {
            const data = event.data.json();
            notificationData = { ...notificationData, ...data };
        } catch (error) {
            console.error('Error parsing push data:', error);
        }
    }
    
    event.waitUntil(
        self.registration.showNotification(notificationData.title, notificationData)
    );
});

// Notification click event
self.addEventListener('notificationclick', event => {
    console.log('Notification clicked');
    
    event.notification.close();
    
    const urlToOpen = event.notification.data?.url || '/';
    
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(clientList => {
                // Check if there's already a window/tab open with the target URL
                for (const client of clientList) {
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                
                // If no window/tab is open, open a new one
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

// IndexedDB operations for offline functionality
async function getPendingActions() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('WorldTourDB', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['pendingActions'], 'readonly');
            const store = transaction.objectStore('pendingActions');
            const getAllRequest = store.getAll();
            
            getAllRequest.onsuccess = () => resolve(getAllRequest.result);
            getAllRequest.onerror = () => reject(getAllRequest.error);
        };
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('pendingActions')) {
                db.createObjectStore('pendingActions', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

async function addPendingAction(action) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('WorldTourDB', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['pendingActions'], 'readwrite');
            const store = transaction.objectStore('pendingActions');
            const addRequest = store.add(action);
            
            addRequest.onsuccess = () => resolve(addRequest.result);
            addRequest.onerror = () => reject(addRequest.error);
        };
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('pendingActions')) {
                db.createObjectStore('pendingActions', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

async function removePendingAction(id) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('WorldTourDB', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['pendingActions'], 'readwrite');
            const store = transaction.objectStore('pendingActions');
            const deleteRequest = store.delete(id);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
    });
}

async function processPendingAction(action) {
    switch (action.type) {
        case 'booking':
            return await processBookingAction(action);
        case 'review':
            return await processReviewAction(action);
        case 'search':
            return await processSearchAction(action);
        default:
            console.warn('Unknown action type:', action.type);
    }
}

async function processBookingAction(action) {
    const response = await fetch('/api/bookings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(action.data)
    });
    
    if (response.ok) {
        // Send notification to user
        self.registration.showNotification('Booking Confirmed', {
            body: `Your booking for ${action.data.destination} has been confirmed!`,
            icon: '/static/icons/icon-192x192.png',
            badge: '/static/icons/badge-72x72.png',
            data: { url: `/booking/${action.data.id}` }
        });
    }
    
    return response;
}

async function processReviewAction(action) {
    const response = await fetch('/api/reviews', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(action.data)
    });
    
    return response;
}

async function processSearchAction(action) {
    const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(action.data)
    });
    
    return response;
}

// Cache management utilities
async function clearOldCaches() {
    const cacheNames = await caches.keys();
    const currentCaches = [STATIC_CACHE, DYNAMIC_CACHE, API_CACHE];
    
    for (const cacheName of cacheNames) {
        if (!currentCaches.includes(cacheName)) {
            await caches.delete(cacheName);
        }
    }
}

async function updateCache() {
    const cache = await caches.open(STATIC_CACHE);
    const requests = await cache.keys();
    
    for (const request of requests) {
        try {
            const response = await fetch(request);
            if (response.ok) {
                await cache.put(request, response);
            }
        } catch (error) {
            console.error('Error updating cache for:', request.url, error);
        }
    }
}

// Periodic cache cleanup
setInterval(clearOldCaches, 24 * 60 * 60 * 1000); // Daily

// Export functions for use in main app
self.WorldTourSW = {
    addPendingAction,
    getPendingActions,
    removePendingAction,
    clearOldCaches,
    updateCache
}; 