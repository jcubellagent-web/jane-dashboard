# Dashboard Code Audit — Feb 10, 2026

Prioritized list of the most impactful improvements for performance, reliability, and UX.

---

## 1. 🔴 `server.js` — Synchronous `execSync` blocks the event loop (Performance)

`getSystemStats()` calls `execSync("top -l 1 ...")` and `execSync("memory_pressure ...")` which **block the entire Node.js event loop** for 2-5 seconds each. Every request to `/api/system` stalls *all* other requests.

**Fix:** Replace with async `exec` (child_process.exec with callbacks/promises). Cache results for 5-10 seconds.

---

## 2. 🔴 `server.js` — SSH to Mini2 on every `/api/system` call (Performance)

The `/api/system` handler does both an HTTP fetch to Mini2:3001 AND an `execSync("ssh mini2 ...")` for CPU stats. The SSH call alone can take 2-5 seconds and blocks the event loop.

**Fix:** Fetch Mini2 stats asynchronously with a background poller (every 30s) and serve from cache. Remove the synchronous SSH entirely.

---

## 3. 🔴 `index.html` — Massive monolithic file at 4,300+ lines (Maintainability/Performance)

All CSS (~2,400 lines), HTML, and JS are in a single file. This means:
- No caching of CSS/JS separately
- Any tiny change invalidates the entire page
- Hard to maintain and debug

**Fix:** Extract CSS to `dashboard.css`, JS to `dashboard.js`. Enables browser caching and parallel downloads.

---

## 4. 🟠 All clients — No request deduplication or caching (Performance)

`index.html` and `mobile.html` call the same endpoints independently with `setInterval`. The desktop page has duplicate refresh functions (`refreshXStats` appears with nearly identical logic in both desktop tweet feed and X stats). `app.html` is the only one with proper request deduplication (`API.inflight` map).

**Fix:** Adopt `app.html`'s API pattern (with inflight deduplication and client-side TTL caching) across all pages.

---

## 5. 🟠 `server.js` — `/api/usage-today` reads entire session JSONL on every request (Performance)

This endpoint reads and parses **every line** of the main session transcript file on each request. These files can be megabytes in size.

**Fix:** Cache the result for 60 seconds. Or compute incrementally (track last-read offset).

---

## 6. 🟠 `server.js` — `/api/memecoins` triggers 12 parallel DexScreener searches per request (Reliability)

For each of the top 12 coins, the server makes a separate HTTP request to DexScreener's search API. This is slow (~3-5s total) and risks rate limiting.

**Fix:** Cache the memecoin data for 60 seconds. Batch or stagger the DexScreener calls. Consider using DexScreener's batch token endpoint instead of individual searches.

---

## 7. 🟠 `server.js` — `/api/predictions` fires 8+ parallel HTTP requests to external APIs (Reliability)

The predictions endpoint simultaneously calls Polymarket (5 URLs), Kalshi, Manifold, and Metaculus. Any single failure can cause partial data. No caching at all.

**Fix:** Add a server-side cache (like `aiNewsCache` pattern, 5-10 min TTL). Aggregate errors gracefully — return cached data when fresh fetch fails.

---

## 8. 🟠 `mobile.html` — Polling intervals overlap and cause redundant fetches (Performance)

Two separate `setInterval` loops:
- Every 30s: `refreshSystem`, `refreshMind`, `refreshNotifications`
- Every 60s: ALL 14 refresh functions (including the same 3 from above)

So `refreshSystem`/`refreshMind`/`refreshNotifications` are called **3 times per minute** instead of 2.

**Fix:** Remove the duplicates from the 60s interval, or unify into a single polling loop.

---

## 9. 🟠 `index.html` — No loading/skeleton states on desktop (UX)

Desktop widgets show static `--` or `Loading...` text while data fetches. `app.html` properly implements skeleton shimmer animations; `mobile.html` has none either.

**Fix:** Add skeleton states to desktop and mobile.html widgets (the pattern already exists in `app.html`).

---

## 10. 🟡 `server.js` — Static `/api/connections` returns hardcoded SVG data URIs (Performance)

The `/api/connections` handler returns ~15KB of hardcoded inline SVG icon data on every request. This data never changes.

**Fix:** Serve icons as static files or embed them client-side. Cache the response with `Cache-Control` headers. Or just hardcode on the client since it's static.

---

## 11. 🟡 `api.js` — Gateway tokens exposed in client-side JS (Security)

`api.js` contains `GATEWAY_TOKEN` and `HOOK_TOKEN` as plain constants, loaded by the browser. Anyone on the local network can extract these.

**Fix:** Proxy all gateway calls through `server.js` so tokens never reach the browser.

---

## 12. 🟡 `index.html` — Brain map SVG animations run continuously even when idle (Performance)

The brain visualization has ~20 CSS animations (orbits, pulses, glows, scans) running in perpetuity via `animation: ... infinite`. On the desktop page, this consumes GPU/CPU even when the tab is in the background.

**Fix:** Use `IntersectionObserver` or `document.visibilitychange` to pause animations when not visible. Consider `will-change: auto` (already on mobile) and reducing animation count.

---

## 13. 🟡 `server.js` — No rate limiting on expensive endpoints (Reliability)

Endpoints like `/api/system` (blocks event loop), `/api/memecoins` (12 outbound requests), `/api/predictions` (8 outbound requests) can be hammered by multiple clients or rapid refreshes.

**Fix:** Add simple in-memory throttling — if a request for the same endpoint is already in flight, return the pending result instead of starting a new one.

---

## 14. 🟡 Multiple HTML files — Code duplication across 4+ dashboard variants (Maintainability)

`index.html`, `mobile.html`, `app.html`, and `mobile-v2.html` all duplicate:
- Fetch/polling logic
- Data formatting helpers (`fmtK`, `formatPrice`, etc.)
- Ticker/X-stats/TikTok rendering

**Fix:** Extract shared logic into a `dashboard-common.js` module. Long-term, consider a lightweight framework or web components.

---

## 15. 🟡 `server.js` — `fetchCoinCap` fallback never caches properly (Bug)

The `fetchCoinCap` function receives `cacheTimestamp` from the caller but sets it as the cache key. If the caller passes `Date.now()`, the cache works. But the crypto endpoint code path that calls it uses `now` which was captured before the async fallback, potentially creating a stale timestamp.

**Fix:** Always use `Date.now()` at cache-write time, not a passed-in timestamp.

---

## Summary

| Priority | Count | Theme |
|----------|-------|-------|
| 🔴 Critical | 2 | Event loop blocking, SSH on every request |
| 🟠 High | 5 | Missing caches, redundant polling, no dedup |
| 🟡 Medium | 6 | Security, animation waste, code duplication |

**Biggest wins:** Fix #1 and #2 (async system stats + cached Mini2 data) would immediately make the dashboard feel 2-5x snappier since `/api/system` currently blocks the server for every connected client.
