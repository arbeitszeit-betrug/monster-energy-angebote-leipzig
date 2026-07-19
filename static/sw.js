var CACHE = "angebote-le-v1";

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) { return c.addAll(["./", "./index.html"]); })
  );
  self.skipWaiting();
});

self.addEventListener("activate", function (e) {
  e.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  e.respondWith(
    fetch(e.request)
      .then(function (resp) {
        var copy = resp.clone();
        caches.open(CACHE).then(function (c) { c.put(e.request, copy); });
        return resp;
      })
      .catch(function () { return caches.match(e.request); })
  );
});
