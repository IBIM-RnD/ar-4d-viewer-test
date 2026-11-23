// 오프라인 사용: 통신이 되면 새 파일을 받아 저장해 두고, 안 되면 저장해 둔 파일을 쓴다.
const CACHE = 'ar4d-v4';
const FILES = ['./', 'index.html', 'drawing.html', 'detect-worker.js', 'vendor/cv.js', 'vendor/aruco.js', 'vendor/qrcode.js', 'vendor/three.module.min.js', 'vendor/GLTFLoader.js', 'vendor/BufferGeometryUtils.js',
  'data/tasks.csv', 'data/drawings.csv', 'data/model.glb', 'data/info.json', 'data/test_photo.jpg'];
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  const fresh = fetch(e.request).then(r => { if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); } return r; });
  e.respondWith(fresh.catch(() => caches.match(e.request, {ignoreSearch: true})));
});
