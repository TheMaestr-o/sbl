/* SBL Edition 2.1 — cache once, then instant (and offline). */
const SHELL = "sbl-shell-v4";
const DATA  = "sbl-data-v1";
const SHELL_FILES = ["index.html"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(SHELL).then((c) => c.addAll(SHELL_FILES)).catch(()=>{}).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.map((k) => (k === SHELL || k === DATA) ? null : caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // SDARM data
  if (url.hostname === "app.sdarm.org") {
    if (url.pathname.indexOf("/bible/data/") !== -1) {
      // Bibles are large and static → cache-first (download once, forever after)
      e.respondWith(caches.open(DATA).then(async (c) => {
        const hit = await c.match(req);
        if (hit) return hit;
        const res = await fetch(req);
        if (res && res.ok) c.put(req, res.clone());
        return res;
      }));
    } else {
      // Lessons may update → serve from cache instantly, refresh in the background
      e.respondWith(caches.open(DATA).then(async (c) => {
        const hit = await c.match(req);
        const net = fetch(req).then((res) => { if (res && res.ok) c.put(req, res.clone()); return res; }).catch(() => hit);
        return hit || net;
      }));
    }
    return;
  }

  // Same-origin app shell → network-first (stay fresh), fall back to cache offline
  if (url.origin === self.location.origin) {
    /* ——— the page is never ten minutes old ———
       Pages serves the lesson with `cache-control: max-age=600`, so a browser
       that has been here today will keep showing yesterday's sheet for another
       ten minutes and nobody can tell whether a change was made or missed. The
       document is asked for with a revalidation every time: the server answers
       304 and almost nothing crosses the wire, but what is shown is what was
       published. Everything else — the recordings above all — keeps the plain
       cache, because a range request must reach the network with its Range
       header intact or seeking inside a part stops working. */
    const doc = req.mode === "navigate" || /\.html$/.test(url.pathname) || url.pathname.endsWith("/");
    e.respondWith(
      (doc ? fetch(url.href, { cache: "no-cache" }) : fetch(req))
        .then((res) => { if (res && res.ok) caches.open(SHELL).then((c) => c.put(req, res.clone())); return res; })
        .catch(() => caches.match(req))
    );
  }
});
