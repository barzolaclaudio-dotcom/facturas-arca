// Service Worker para PWA instalable
const CACHE_NAME = 'facturas-arca-v3';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './static/manifest.json',
  './static/icon-192.png',
  './static/icon-512.png',
  './static/screenshot-1.png',
  './static/screenshot-2.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS).catch(() => {});
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
