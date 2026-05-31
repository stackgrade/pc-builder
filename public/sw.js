// PC Builder SE — Service Worker
// Cache-first for static assets, network-first for data
const CACHE = 'pcb-v1';
const STATIC_CACHE = 'pcb-static-v1';
const DATA_CACHE = 'pcb-data-v1';

const BASE = '/pc-builder';

const STATIC_ASSETS = [
  `${BASE}/`,
  `${BASE}/favicon.ico`,
  `${BASE}/favicon.svg`,
  `${BASE}/og-image.svg`,
];

// Install: pre-cache essential static assets
self.addEventListener('install', evt => {
  self.skipWaiting();
  evt.waitUntil(
    caches.open(STATIC_CACHE).then(cache => cache.addAll(STATIC_ASSETS))
  );
});

// Activate: clean old caches
self.addEventListener('activate', evt => {
  evt.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== STATIC_CACHE && k !== DATA_CACHE)
          .map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// Fetch: cache-first for static, network-first for data/HTML
self.addEventListener('fetch', evt => {
  const url = new URL(evt.request.url);
  const path = url.pathname;

  // Service worker scope check — only handle our base path
  if (!path.startsWith(BASE + '/') && path !== BASE && path !== BASE + '/') {
    return;
  }

  // Data files: network-first (always want fresh prices)
  if (path.endsWith('.json') || path.includes('/data/')) {
    evt.respondWith(networkFirst(evt.request));
    return;
  }

  // Static assets: cache-first
  if (
    path.endsWith('.css') ||
    path.endsWith('.js') ||
    path.endsWith('.svg') ||
    path.endsWith('.ico') ||
    path.endsWith('.png') ||
    path.endsWith('.jpg') ||
    path.endsWith('.webp') ||
    path.endsWith('.woff2') ||
    path.endsWith('.woff') ||
    path.endsWith('.ttf')
  ) {
    evt.respondWith(cacheFirst(evt.request));
    return;
  }

  // HTML / main page: network-first with cache fallback
  if (path === BASE || path === BASE + '/' || path.endsWith('.html')) {
    evt.respondWith(networkFirst(evt.request));
    return;
  }

  // Everything else: network-first
  evt.respondWith(networkFirst(evt.request));
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    return new Response('Offline', { status: 503 });
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(DATA_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response('Offline', { status: 503 });
  }
}
