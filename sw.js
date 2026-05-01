// Cache-first service worker for the 111SB Change of Command program.
// Tiny, single page, ~250KB total — safe to precache everything.
const CACHE = "111sb-coc-v3";
const ASSETS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./assets/ssi.png",
  "./assets/prussian.jpg",
  "./assets/james.jpg",
  "./assets/armijo.jpg"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  e.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(()=>{});
          return res;
        })
        .catch(() => caches.match("./index.html"));
    })
  );
});
