/**
 * Dashboard Common — Shared utilities across index.html, mobile.html, app.html
 * Extracted to reduce code duplication (audit item #14)
 */

// ===== Fetch Helpers =====

// Inflight request deduplication — if multiple widgets request the same URL
// simultaneously, only one fetch fires and all callers share the result
const _inflight = new Map();

/**
 * Fetch JSON with timeout, error handling, and request deduplication
 */
async function fetchWithTimeout(url, timeout = 8000) {
    // Return existing inflight request for same URL
    if (_inflight.has(url)) return _inflight.get(url);
    
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    const promise = (async () => {
        try {
            const response = await fetch(url, { signal: controller.signal });
            clearTimeout(timer);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (e) {
            clearTimeout(timer);
            if (e.name === 'AbortError') console.warn(`Fetch timeout: ${url}`);
            else console.error(`Fetch error (${url}):`, e.message);
            return null;
        } finally {
            _inflight.delete(url);
        }
    })();
    
    _inflight.set(url, promise);
    return promise;
}

// Alias used by mobile.html
const fetchJSON = fetchWithTimeout;

/**
 * Spin a button while a promise resolves (min 300ms animation)
 */
function spinButton(btn, promise) {
    if (!btn) return promise;
    btn.classList.add('spinning');
    const minSpinTime = new Promise(r => setTimeout(r, 800));
    return Promise.all([promise, minSpinTime]).finally(() => btn.classList.remove('spinning'));
}

// ===== Formatting Helpers =====

function fmtK(n) {
    if (n == null) return '--';
    if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
    return String(n);
}

function formatPrice(price) {
    if (price == null) return '--';
    if (price >= 1) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (price >= 0.01) return price.toFixed(4);
    return price.toFixed(6);
}

function esc(str) {
    if (!str) return '';
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

// ===== Market Helpers =====

function isStockMarketOpen() {
    const now = new Date();
    const day = now.getDay();
    if (day === 0 || day === 6) return false;
    const et = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));
    const hours = et.getHours();
    const mins = et.getMinutes();
    const totalMins = hours * 60 + mins;
    return totalMins >= 570 && totalMins <= 960; // 9:30 AM - 4:00 PM ET
}

// ===== Visibility API — Pause CSS Animations =====

/**
 * Pause all CSS animations when the tab is not visible.
 * Call once on page load. Targets elements with 'animation' in their computed style.
 */
function initAnimationPauseOnHidden() {
    // Use a class on <html> to control animation-play-state via CSS
    const style = document.createElement('style');
    style.textContent = `
        html.tab-hidden *, html.tab-hidden *::before, html.tab-hidden *::after {
            animation-play-state: paused !important;
        }
    `;
    document.head.appendChild(style);

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            document.documentElement.classList.add('tab-hidden');
        } else {
            document.documentElement.classList.remove('tab-hidden');
        }
    });
}

// ===== Smart Interval (pause when tab hidden) =====

function smartInterval(fn, ms) {
    return setInterval(() => { if (!document.hidden) fn(); }, ms);
}

// ===== Gateway API (proxied through server) =====

const JaneAPI = {
    async sendToJane(message, options = {}) {
        const response = await fetch('/api/gateway/hook', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, ...options })
        });
        if (!response.ok) throw new Error(`Failed to send message: ${response.status}`);
        return response.json();
    },

    async wakeJane(text, mode = 'now') {
        const response = await fetch('/api/gateway/wake', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, mode })
        });
        if (!response.ok) throw new Error(`Failed to wake: ${response.status}`);
        return response.json();
    },

    async getSessionHistory(sessionKey = 'agent:main:main', limit = 20) {
        const response = await fetch(`/api/gateway/sessions/${encodeURIComponent(sessionKey)}/history?limit=${limit}`);
        if (!response.ok) throw new Error(`Failed to get history: ${response.status}`);
        return response.json();
    },

    async getGatewayStatus() {
        const response = await fetch('/api/gateway/status');
        if (!response.ok) throw new Error(`Failed to get status: ${response.status}`);
        return response.json();
    }
};

// Legacy export for backward compatibility
if (typeof window !== 'undefined') {
    window.JaneAPI = JaneAPI;
    window.fetchWithTimeout = fetchWithTimeout;
    window.fetchJSON = fetchJSON;
    window.spinButton = spinButton;
    window.fmtK = fmtK;
    window.formatPrice = formatPrice;
    window.esc = esc;
    window.isStockMarketOpen = isStockMarketOpen;
    window.smartInterval = smartInterval;
    window.initAnimationPauseOnHidden = initAnimationPauseOnHidden;
}
