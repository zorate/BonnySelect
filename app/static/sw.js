const CACHE_NAME = 'bonny-selects-v1';
const urlsToCache = [
  '/',
  '/manifest.json',
];

// Install event - cache files
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - Network First for HTML, Cache First for other assets
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  const url = new URL(event.request.url);

  // NEVER cache HTML pages - always fetch fresh from network
  if (event.request.destination === 'document' || 
      event.request.mode === 'navigate' ||
      url.pathname === '/' ||
      url.pathname.endsWith('.html')) {
    
    // Network first for HTML
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Don't cache if not successful
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }
          return response;
        })
        .catch(() => {
          // If offline, try cache
          return caches.match(event.request);
        })
    );
    return;
  }

  // Cache first for static assets (CSS, JS, images)
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response;
      }

      return fetch(event.request).then((response) => {
        // Don't cache if not successful
        if (!response || response.status !== 200 || response.type === 'error') {
          return response;
        }

        // Clone the response for caching
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });

        return response;
      }).catch(() => {
        // Return offline page if available
        return caches.match('/');
      });
    })
  );
});