#!/usr/bin/env node
/**
 * Jane Dashboard Server
 * Simple static file server for the dashboard
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const ROOT = __dirname;

const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.webp': 'image/webp',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
};

const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
const os = require('os');
const https = require('https');

// ===== Rate Limiting (audit item #13) =====
const rateLimitBuckets = {};
const RATE_LIMIT = 60; // requests per minute per endpoint
const RATE_WINDOW = 60000; // 1 minute

function checkRateLimit(endpoint) {
    const now = Date.now();
    if (!rateLimitBuckets[endpoint]) rateLimitBuckets[endpoint] = [];
    const bucket = rateLimitBuckets[endpoint];
    while (bucket.length > 0 && bucket[0] < now - RATE_WINDOW) bucket.shift();
    if (bucket.length >= RATE_LIMIT) return false;
    bucket.push(now);
    return true;
}

// ===== Gateway proxy config (audit item #11 — tokens stay server-side) =====
const GATEWAY_URL = 'http://127.0.0.1:18789';
const GATEWAY_TOKEN = '47cf46ba8962b26d18a3d690d80a3e109f57e2525b8f6941';
const HOOK_TOKEN = '5c8d56dd45438059dddecbedb8a7123abaf72721153dc95d';

// Caches (to avoid rate limits and reduce external API calls)
let cryptoCache = { data: null, timestamp: 0 };
let aiNewsCache = { data: null, timestamp: 0 };
let tickerCache = { data: null, timestamp: 0 };
let systemStatsCache = { data: null, timestamp: 0 };
const SYSTEM_CACHE_TTL = 30000; // 30 seconds

// TTL caches for expensive endpoints
let dgenCache = { data: null, timestamp: 0 };
let predictionsCache = { data: null, timestamp: 0 };
let memecoinsCache = { data: null, timestamp: 0 };
let kalshiCache = { data: null, timestamp: 0 };
let walletCache = { data: null, timestamp: 0 };
let buttcoinCache = { data: null, timestamp: 0 };
let nbaLiveCache = { data: null, timestamp: 0 };
let marketCache = { data: null, timestamp: 0 };
let notificationsCache = { data: null, timestamp: 0 };
let usageTodayCache = { data: null, timestamp: 0 };
let arxivCache = { data: null, timestamp: 0 };
let secEdgarCache = { data: null, timestamp: 0 };
let defiLlamaCache = { data: null, timestamp: 0 };
let techCrunchCache = { data: null, timestamp: 0 };
const CACHE_TTL_30S = 30000;
const CACHE_TTL_60S = 60000;
const CACHE_TTL_5MIN = 300000;
const CACHE_TTL_30MIN = 1800000;

// Paths for dynamic data
const WORKSPACE = path.join(os.homedir(), '.openclaw', 'workspace');
const SECOND_BRAIN = path.join(os.homedir(), 'Desktop', 'Second Brain');
const MEMORY_DIR = path.join(WORKSPACE, 'memory');

// Fetch AI news from RSS feeds
async function fetchAINewsFromFeeds() {
    const feeds = [
        { url: 'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml', source: 'The Verge' },
        { url: 'https://techcrunch.com/category/artificial-intelligence/feed/', source: 'TechCrunch' },
        { url: 'https://www.wired.com/feed/tag/ai/latest/rss', source: 'Wired' }
    ];
    
    const fetchFeed = (url) => new Promise((resolve) => {
        const protocol = url.startsWith('https') ? https : require('http');
        const req = protocol.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' }, timeout: 5000 }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        });
        req.on('error', () => resolve(''));
        req.on('timeout', () => { req.destroy(); resolve(''); });
    });
    
    const parseRSS = (xml, source) => {
        const items = [];
        const itemRegex = /<item>([\s\S]*?)<\/item>/gi;
        let match;
        while ((match = itemRegex.exec(xml)) !== null && items.length < 8) {
            const item = match[1];
            const title = item.match(/<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?<\/title>/)?.[1] || '';
            const desc = item.match(/<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?<\/description>/)?.[1] || '';
            const pubDate = item.match(/<pubDate>(.*?)<\/pubDate>/)?.[1] || '';
            const link = item.match(/<link>(.*?)<\/link>/)?.[1] || '';
            if (title) {
                const date = new Date(pubDate);
                items.push({
                    title: title.replace(/<[^>]*>/g, '').substring(0, 80),
                    desc: desc.replace(/<[^>]*>/g, '').substring(0, 120),
                    source,
                    date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                    timestamp: date.getTime(),
                    link
                });
            }
        }
        return items;
    };
    
    try {
        const results = await Promise.all(feeds.map(async f => {
            const xml = await fetchFeed(f.url);
            return parseRSS(xml, f.source);
        }));
        
        const allItems = results.flat().sort((a, b) => b.timestamp - a.timestamp);
        const featured = allItems[0] || { title: 'No news available', desc: '', source: '-', date: '-' };
        
        return {
            lastUpdated: new Date().toISOString(),
            featured: { tag: '🔥 Breaking', ...featured },
            agenticRetail: allItems.slice(1, 6),
            agenticEnterprise: allItems.slice(6, 11),
            general: allItems.slice(11, 14).map(item => ({ tag: '📰 News', ...item }))
        };
    } catch (error) {
        console.error('AI News fetch error:', error.message);
        return null;
    }
}

// Get bubble cluster data from Second Brain items
function getBubbleData() {
    const bubbles = {
        lastUpdated: new Date().toISOString(),
        clusters: [],
        totalItems: 0
    };
    
    // Category definitions for Second Brain
    const CATEGORIES = {
        articles: { name: 'Articles', icon: '📚', color: '#60a5fa', desc: 'Reads & insights' },
        ideas: { name: 'Ideas', icon: '💡', color: '#facc15', desc: 'Thoughts & concepts' },
        links: { name: 'Links', icon: '🔗', color: '#a78bfa', desc: 'Sites & resources' },
        quotes: { name: 'Quotes', icon: '💬', color: '#f472b6', desc: 'Words to remember' },
        videos: { name: 'Videos', icon: '🎬', color: '#ff0050', desc: 'Content to watch' },
        people: { name: 'People', icon: '👥', color: '#fb923c', desc: 'Accounts & contacts' },
        tools: { name: 'Tools', icon: '🛠️', color: '#4ade80', desc: 'Apps & products' },
        random: { name: 'Random', icon: '🎲', color: '#38bdf8', desc: 'Cool stuff' }
    };
    
    // Helper to format relative time
    const relativeTime = (dateStr) => {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;
        const mins = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        if (mins < 60) return mins <= 1 ? 'just now' : `${mins}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days === 1) return 'yesterday';
        if (days < 7) return `${days}d ago`;
        if (days < 30) return `${Math.floor(days/7)}w ago`;
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    };
    
    // Load Second Brain items
    const itemsFile = path.join(WORKSPACE, 'second-brain', 'items.json');
    let items = [];
    
    if (fs.existsSync(itemsFile)) {
        try {
            const data = JSON.parse(fs.readFileSync(itemsFile, 'utf8'));
            items = data.items || [];
        } catch (e) {
            console.error('Error loading second-brain items:', e);
        }
    }
    
    bubbles.totalItems = items.length;
    
    // Group items by category
    const grouped = {};
    for (const cat of Object.keys(CATEGORIES)) {
        grouped[cat] = items.filter(item => item.category === cat);
    }
    
    // Build clusters - only show categories with items OR core categories
    const coreCats = ['articles', 'ideas', 'links', 'videos', 'random'];
    
    for (const [catId, catInfo] of Object.entries(CATEGORIES)) {
        const catItems = grouped[catId] || [];
        
        // Skip empty non-core categories
        if (catItems.length === 0 && !coreCats.includes(catId)) continue;
        
        // Calculate size based on item count (min 50, max 95)
        const baseSize = 50;
        const sizePerItem = 8;
        const size = Math.min(95, baseSize + catItems.length * sizePerItem);
        
        // Build artifacts from items (most recent first)
        const artifacts = catItems
            .sort((a, b) => new Date(b.savedAt) - new Date(a.savedAt))
            .slice(0, 5)
            .map(item => ({
                title: item.title,
                detail: item.note || item.tags?.join(', ') || catInfo.desc,
                time: relativeTime(item.savedAt),
                id: item.id
            }));
        
        bubbles.clusters.push({
            id: catId,
            name: catInfo.name,
            icon: catInfo.icon,
            color: catInfo.color,
            size: size,
            count: catItems.length,
            artifacts: artifacts
        });
    }
    
    // Sort clusters: items with content first, then by count
    bubbles.clusters.sort((a, b) => {
        if (a.count > 0 && b.count === 0) return -1;
        if (b.count > 0 && a.count === 0) return 1;
        return b.count - a.count;
    });
    
    return bubbles;
}

// Scan Second Brain folder for mindmap stats
function getMindmapStats() {
    const stats = { topics: {}, lastUpdated: new Date().toISOString() };
    
    try {
        if (!fs.existsSync(SECOND_BRAIN)) {
            return { topics: { 'No Second Brain folder': 0 }, lastUpdated: stats.lastUpdated };
        }
        
        const countFiles = (dir, depth = 0) => {
            if (depth > 3) return 0;
            let count = 0;
            const items = fs.readdirSync(dir, { withFileTypes: true });
            for (const item of items) {
                if (item.name.startsWith('.')) continue;
                if (item.isDirectory()) {
                    count += countFiles(path.join(dir, item.name), depth + 1);
                } else if (item.name.endsWith('.md') || item.name.endsWith('.txt')) {
                    count++;
                }
            }
            return count;
        };
        
        const topDirs = fs.readdirSync(SECOND_BRAIN, { withFileTypes: true })
            .filter(d => d.isDirectory() && !d.name.startsWith('.'));
        
        for (const dir of topDirs) {
            const dirPath = path.join(SECOND_BRAIN, dir.name);
            const fileCount = countFiles(dirPath);
            if (fileCount > 0) {
                stats.topics[dir.name] = fileCount;
            }
        }
        
        // Calculate percentages (relative to highest)
        const maxCount = Math.max(...Object.values(stats.topics), 1);
        const topicsWithPercent = {};
        for (const [topic, count] of Object.entries(stats.topics)) {
            topicsWithPercent[topic] = Math.round((count / maxCount) * 100);
        }
        stats.topics = topicsWithPercent;
        
    } catch (error) {
        console.error('Mindmap stats error:', error.message);
    }
    
    return stats;
}

// Get Jane's tasks from memory files
function getJaneTasks() {
    const tasks = { inProgress: [], completed: [], lastUpdated: new Date().toISOString() };
    
    try {
        // Read today's memory file
        const today = new Date().toISOString().split('T')[0];
        const todayFile = path.join(MEMORY_DIR, `${today}.md`);
        
        if (fs.existsSync(todayFile)) {
            const content = fs.readFileSync(todayFile, 'utf8');
            
            // Find "In Progress" items (lines with - [ ])
            const inProgressRegex = /^[-*]\s*\[\s*\]\s*(.+)$/gm;
            let match;
            while ((match = inProgressRegex.exec(content)) !== null) {
                tasks.inProgress.push({ task: match[1].trim(), status: 'in-progress', icon: '📌' });
            }
            
            // Find completed items (lines with - [x])
            const completedRegex = /^[-*]\s*\[x\]\s*(.+)$/gim;
            while ((match = completedRegex.exec(content)) !== null) {
                tasks.completed.push({ task: match[1].trim(), status: 'done', icon: '✓' });
            }
        }
        
        // Also check for a dedicated tasks file (in dashboard folder)
        const tasksFile = path.join(ROOT, 'tasks.json');
        if (fs.existsSync(tasksFile)) {
            const taskData = JSON.parse(fs.readFileSync(tasksFile, 'utf8'));
            if (taskData.inProgress) tasks.inProgress = taskData.inProgress;
            if (taskData.completed) tasks.completed = taskData.completed;
        }
        
    } catch (error) {
        console.error('Jane tasks error:', error.message);
    }
    
    // Fallback defaults if nothing found
    if (tasks.inProgress.length === 0) {
        tasks.inProgress = [
            { task: 'Monitor memecoin positions', status: 'in-progress', icon: '📈', detail: 'WOJAK, COPPERINU, pippin' },
            { task: 'TikTok stats monitoring', status: 'in-progress', icon: '🎵', detail: 'Auto-refresh 2-3x daily' }
        ];
    }
    
    return tasks;
}

// Fallback to CoinCap API
function fetchCoinCap(res, cacheTimestamp) {
    const coins = ['bitcoin', 'ethereum', 'solana'];
    const results = {};
    let completed = 0;
    
    coins.forEach(coin => {
        https.get(`https://api.coincap.io/v2/assets/${coin}`, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (proxyRes) => {
            let data = '';
            proxyRes.on('data', chunk => data += chunk);
            proxyRes.on('end', () => {
                try {
                    const parsed = JSON.parse(data);
                    results[coin] = {
                        usd: parseFloat(parsed.data.priceUsd),
                        usd_24h_change: parseFloat(parsed.data.changePercent24Hr)
                    };
                } catch (e) {
                    results[coin] = { usd: 0, usd_24h_change: 0 };
                }
                completed++;
                if (completed === coins.length) {
                    const formatted = {
                        bitcoin: results.bitcoin,
                        ethereum: results.ethereum,
                        solana: results.solana
                    };
                    // Cache the result
                    cryptoCache = { data: formatted, timestamp: cacheTimestamp };
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify(formatted));
                }
            });
        }).on('error', () => {
            completed++;
            results[coin] = { usd: 0, usd_24h_change: 0 };
            if (completed === coins.length) {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(results));
            }
        });
    });
}

// Get system stats (async, cached)
async function getSystemStats() {
    const now = Date.now();
    if (systemStatsCache.data && (now - systemStatsCache.timestamp) < SYSTEM_CACHE_TTL) {
        return systemStatsCache.data;
    }
    try {
        // Run all shell commands in parallel (async, non-blocking)
        const [cpuResult, mpResult, diskResult] = await Promise.allSettled([
            execAsync("top -l 1 | grep 'CPU usage' | awk '{print $3}' | tr -d '%'", { timeout: 5000 }),
            execAsync("memory_pressure | grep 'System-wide memory free percentage'", { timeout: 5000 }),
            execAsync("df -h / | tail -1 | awk '{print $5}' | tr -d '%'", { timeout: 5000 })
        ]);
        
        const cpu = cpuResult.status === 'fulfilled' ? Math.round(parseFloat(cpuResult.value.stdout) || 0) : 0;
        
        let memory = 0;
        if (mpResult.status === 'fulfilled') {
            const freeMatch = mpResult.value.stdout.match(/(\d+)%/);
            memory = freeMatch ? (100 - parseInt(freeMatch[1])) : 0;
        } else {
            const totalMem = os.totalmem();
            const freeMem = os.freemem();
            memory = Math.round(((totalMem - freeMem) / totalMem) * 100);
        }
        
        const disk = diskResult.status === 'fulfilled' ? parseInt(diskResult.value.stdout) || 0 : 0;
        
        // System uptime (no shell needed)
        const uptimeSeconds = os.uptime();
        const days = Math.floor(uptimeSeconds / 86400);
        const hours = Math.floor((uptimeSeconds % 86400) / 3600);
        const minutes = Math.floor((uptimeSeconds % 3600) / 60);
        let uptime = '';
        if (days > 0) uptime += `${days}d `;
        if (hours > 0) uptime += `${hours}h `;
        uptime += `${minutes}m`;
        
        const stats = { cpu, memory, disk, uptime };
        systemStatsCache = { data: stats, timestamp: Date.now() };
        return stats;
    } catch (error) {
        console.error('System stats error:', error.message);
        return { cpu: 0, memory: 0, disk: 0, uptime: 'unknown' };
    }
}

// Fetch market data server-side (bypasses CORS)
async function fetchMarketData() {
    const https = require('https');
    
    const fetchJSON = (url) => new Promise((resolve, reject) => {
        https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(data)); } 
                catch (e) { reject(e); }
            });
        }).on('error', reject);
    });
    
    try {
        const [ndaq, ixic, gspc] = await Promise.all([
            fetchJSON('https://query1.finance.yahoo.com/v8/finance/chart/NDAQ?interval=1d&range=1d').catch(() => null),
            fetchJSON('https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC?interval=1d&range=1d').catch(() => null),
            fetchJSON('https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d&range=1d').catch(() => null)
        ]);
        
        const extract = (data) => {
            if (!data?.chart?.result?.[0]) return null;
            const meta = data.chart.result[0].meta;
            const price = meta.regularMarketPrice;
            const prev = meta.chartPreviousClose || meta.previousClose;
            return { price, change: price - prev, changePercent: ((price - prev) / prev) * 100 };
        };
        
        return {
            ndaq: extract(ndaq),
            ixic: extract(ixic),
            gspc: extract(gspc),
            timestamp: new Date().toISOString()
        };
    } catch (error) {
        console.error('Market data error:', error.message);
        return { error: 'Failed to fetch market data' };
    }
}

function handleRequest(req, res) {
    // CORS headers for local development
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    // Rate limiting for API endpoints
    if (req.url.startsWith('/api/')) {
        const endpoint = req.url.split('?')[0];
        if (!checkRateLimit(endpoint)) {
            res.writeHead(429, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Too many requests. Max 60/min per endpoint.' }));
            return;
        }
    }

    // ===== Gateway Proxy Endpoints (audit item #11 — tokens never reach browser) =====
    if (req.url === '/api/gateway/hook' && req.method === 'POST') {
        let body = '';
        req.on('data', c => body += c);
        req.on('end', () => {
            const opts = {
                method: 'POST', hostname: '127.0.0.1', port: 18789, path: '/hooks/agent',
                headers: { 'Authorization': `Bearer ${HOOK_TOKEN}`, 'Content-Type': 'application/json' }
            };
            const proxy = require('http').request(opts, (pRes) => {
                let d = '';
                pRes.on('data', c => d += c);
                pRes.on('end', () => { res.writeHead(pRes.statusCode, { 'Content-Type': 'application/json' }); res.end(d); });
            });
            proxy.on('error', () => { res.writeHead(502); res.end('{"error":"Gateway unavailable"}'); });
            const parsed = JSON.parse(body || '{}');
            proxy.write(JSON.stringify({
                message: parsed.message, name: parsed.name || 'Dashboard',
                sessionKey: parsed.sessionKey || 'dashboard:main', deliver: parsed.deliver !== false,
                channel: parsed.channel || 'whatsapp', ...parsed
            }));
            proxy.end();
        });
        return;
    }

    if (req.url === '/api/gateway/wake' && req.method === 'POST') {
        let body = '';
        req.on('data', c => body += c);
        req.on('end', () => {
            const opts = {
                method: 'POST', hostname: '127.0.0.1', port: 18789, path: '/hooks/wake',
                headers: { 'Authorization': `Bearer ${HOOK_TOKEN}`, 'Content-Type': 'application/json' }
            };
            const proxy = require('http').request(opts, (pRes) => {
                let d = '';
                pRes.on('data', c => d += c);
                pRes.on('end', () => { res.writeHead(pRes.statusCode, { 'Content-Type': 'application/json' }); res.end(d); });
            });
            proxy.on('error', () => { res.writeHead(502); res.end('{"error":"Gateway unavailable"}'); });
            proxy.write(body);
            proxy.end();
        });
        return;
    }

    if (req.url === '/api/gateway/status') {
        const opts = {
            hostname: '127.0.0.1', port: 18789, path: '/api/status',
            headers: { 'Authorization': `Bearer ${GATEWAY_TOKEN}` }
        };
        require('http').get(opts, (pRes) => {
            let d = '';
            pRes.on('data', c => d += c);
            pRes.on('end', () => { res.writeHead(pRes.statusCode, { 'Content-Type': 'application/json' }); res.end(d); });
        }).on('error', () => { res.writeHead(502); res.end('{"error":"Gateway unavailable"}'); });
        return;
    }

    const gwSessionMatch = req.url.match(/^\/api\/gateway\/sessions\/(.+)\/history/);
    if (gwSessionMatch) {
        const sessionKey = decodeURIComponent(gwSessionMatch[1]);
        const limit = new URL(req.url, 'http://x').searchParams.get('limit') || 20;
        const opts = {
            hostname: '127.0.0.1', port: 18789,
            path: `/api/sessions/${encodeURIComponent(sessionKey)}/history?limit=${limit}`,
            headers: { 'Authorization': `Bearer ${GATEWAY_TOKEN}` }
        };
        require('http').get(opts, (pRes) => {
            let d = '';
            pRes.on('data', c => d += c);
            pRes.on('end', () => { res.writeHead(pRes.statusCode, { 'Content-Type': 'application/json' }); res.end(d); });
        }).on('error', () => { res.writeHead(502); res.end('{"error":"Gateway unavailable"}'); });
        return;
    }

    // API endpoint for connected accounts & data sources
    if (req.url === '/api/connections') {
        // White/light SVG icons for dark background
        const icons = {
            whatsapp: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2325D366'%3E%3Cpath d='M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z'/%3E%3C/svg%3E",
            gmail: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23EA4335'%3E%3Cpath d='M20 18h-2V9.25L12 13 6 9.25V18H4V6h1.2l6.8 4.25L18.8 6H20m0-2H4c-1.11 0-2 .89-2 2v12a2 2 0 002 2h16a2 2 0 002-2V6a2 2 0 00-2-2z'/%3E%3C/svg%3E",
            twitter: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z'/%3E%3C/svg%3E",
            tiktok: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1v-3.5a6.37 6.37 0 00-.79-.05A6.34 6.34 0 003.15 15.2a6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.34-6.34V8.72a8.19 8.19 0 004.76 1.52V6.79a4.85 4.85 0 01-1-.1z'/%3E%3C/svg%3E",
            reddit: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23FF4500'%3E%3Cpath d='M12 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 01-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 01.042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 014.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 01.14-.197.35.35 0 01.238-.042l2.906.617a1.214 1.214 0 011.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 00-.231.094.33.33 0 000 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 00.029-.463.33.33 0 00-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 00-.232-.095z'/%3E%3C/svg%3E",
            github: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12'/%3E%3C/svg%3E",
            sorare: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2300DC96'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Ctext x='12' y='16' text-anchor='middle' fill='black' font-size='12' font-weight='bold'%3ES%3C/text%3E%3C/svg%3E",
            phantom: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23AB9FF2'%3E%3Crect width='24' height='24' rx='6'/%3E%3Ccircle cx='9' cy='12' r='2' fill='white'/%3E%3Ccircle cx='15' cy='12' r='2' fill='white'/%3E%3C/svg%3E",
            polymarket: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/%3E%3C/svg%3E",
            kalshi: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%234A90D9'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='16' text-anchor='middle' fill='white' font-size='14' font-weight='bold'%3EK%3C/text%3E%3C/svg%3E",
            manifold: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%234337c9'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='16' text-anchor='middle' fill='white' font-size='14' font-weight='bold'%3EM%3C/text%3E%3C/svg%3E",
            metaculus: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23006C67'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='16' text-anchor='middle' fill='white' font-size='12' font-weight='bold'%3EMC%3C/text%3E%3C/svg%3E",
            coingecko: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%238BC53F'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Ccircle cx='9' cy='10' r='2' fill='white'/%3E%3Ccircle cx='9' cy='10' r='1' fill='black'/%3E%3C/svg%3E",
            yahoo: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%237B1FA2'%3E%3Cpath d='M2 4l5.5 8.5V20h3v-7.5L16 4h-3.5L9.25 9.5 6 4H2zm14 0l3 8h3l-3-8h-3zm2 10a2 2 0 100 4 2 2 0 000-4z'/%3E%3C/svg%3E",
            dexscreener: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2300E676'%3E%3Cpath d='M3 17l6-6 4 4 8-8v3h2V3h-7v2h3l-6 6-4-4-8 8z'/%3E%3C/svg%3E",
            brave: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23FB542B'%3E%3Cpath d='M12 2L4 5.5v5c0 5.25 3.4 10.15 8 11.5 4.6-1.35 8-6.25 8-11.5v-5L12 2zm0 2.18l6 2.63v4.19c0 4.35-2.76 8.43-6 9.68-3.24-1.25-6-5.33-6-9.68V6.81l6-2.63z'/%3E%3Cpath d='M12 6l-4 1.8v3.2c0 3.13 1.7 6.08 4 7.2 2.3-1.12 4-4.07 4-7.2V7.8L12 6z'/%3E%3C/svg%3E",
            substack: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23FF6719'%3E%3Cpath d='M22.539 8.242H1.46V5.406h21.08v2.836zM1.46 10.812V24L12 18.11 22.54 24V10.812H1.46zM22.54 0H1.46v2.836h21.08V0z'/%3E%3C/svg%3E",
            twilio: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23F22F46'%3E%3Cpath d='M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 20.25c-4.556 0-8.25-3.694-8.25-8.25S7.444 3.75 12 3.75s8.25 3.694 8.25 8.25-3.694 8.25-8.25 8.25zm3.11-11.36a1.89 1.89 0 110 3.78 1.89 1.89 0 010-3.78zm0 4.44a1.89 1.89 0 110 3.78 1.89 1.89 0 010-3.78zm-6.22-4.44a1.89 1.89 0 110 3.78 1.89 1.89 0 010-3.78zm0 4.44a1.89 1.89 0 110 3.78 1.89 1.89 0 010-3.78z'/%3E%3C/svg%3E",
            huggingface: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23FFD21E'%3E%3Cpath d='M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm-2.5 7a1.5 1.5 0 110 3 1.5 1.5 0 010-3zm5 0a1.5 1.5 0 110 3 1.5 1.5 0 010-3zM8 15.5c0-.276.5-.5.5-.5h7c0 0 .5.224.5.5S15.052 18 12 18s-4-.224-4-2.5z'/%3E%3C/svg%3E",
            finnhub: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2300C9A7'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='16' text-anchor='middle' fill='white' font-size='12' font-weight='bold'%3EFH%3C/text%3E%3C/svg%3E",
            alphavantage: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23F7931A'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='16' text-anchor='middle' fill='white' font-size='12' font-weight='bold'%3EAV%3C/text%3E%3C/svg%3E",
            arxiv: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23B31B1B'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='16' text-anchor='middle' fill='white' font-size='10' font-weight='bold'%3EarXiv%3C/text%3E%3C/svg%3E",
            hackernews: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23FF6600'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='17' text-anchor='middle' fill='white' font-size='16' font-weight='bold'%3EY%3C/text%3E%3C/svg%3E",
            secedgar: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%230A3161'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='16' text-anchor='middle' fill='white' font-size='9' font-weight='bold'%3ESEC%3C/text%3E%3C/svg%3E",
            techcrunch: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2300A562'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='16' text-anchor='middle' fill='white' font-size='11' font-weight='bold'%3ETC%3C/text%3E%3C/svg%3E",
            fred: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23000080'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='17' text-anchor='middle' fill='white' font-size='9' font-weight='bold'%3EFRED%3C/text%3E%3C/svg%3E",
            newsapi: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23FF6B00'%3E%3Cpath d='M6 3h12a3 3 0 013 3v12a3 3 0 01-3 3H6a3 3 0 01-3-3V6a3 3 0 013-3zm2 3v2h8V6H8zm0 4v2h8v-2H8zm0 4v2h5v-2H8z'/%3E%3C/svg%3E",
            openalex: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%236B46C1'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='17' text-anchor='middle' fill='white' font-size='9' font-weight='bold'%3EOAlex%3C/text%3E%3C/svg%3E",
            lobsters: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23DC2626'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='17' text-anchor='middle' fill='white' font-size='12' font-weight='bold'%3E🦞%3C/text%3E%3C/svg%3E",
            grokipedia: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%231DA1F2'%3E%3Crect width='24' height='24' rx='4'/%3E%3Ctext x='12' y='17' text-anchor='middle' fill='white' font-size='9' font-weight='bold'%3EGrok%3C/text%3E%3C/svg%3E",
        };
        const connections = {
            accounts: [
                { name: 'WhatsApp', detail: 'communication channel', icon: icons.whatsapp, active: true },
                { name: 'Gmail', detail: 'jcubellagent@gmail.com', icon: icons.gmail, active: true },
                { name: 'X / Twitter', detail: '@AgentJc11443', icon: icons.twitter, active: true },
                { name: 'TikTok', detail: '@degencollector', icon: icons.tiktok, active: true },
                { name: 'Reddit', detail: 'u/JaneAgentAI', icon: icons.reddit, active: true },
                { name: 'GitHub', detail: 'jcubellagent-web', icon: icons.github, active: true },
                { name: 'Sorare', detail: 'jcubnft', icon: icons.sorare, active: true },
                { name: 'Phantom Wallet', detail: 'Solana', icon: icons.phantom, active: true },
                { name: 'Substack', detail: '@agentjc11443', icon: icons.substack, active: true },
                { name: 'Twilio', detail: 'Phone number provider', icon: icons.twilio, active: true },
                { name: 'HuggingFace', detail: 'JaneAgentAI', icon: icons.huggingface, active: true }
            ],
            dataSources: [
                { name: '@DeItaone', detail: 'breaking financial news', icon: icons.twitter, active: true },
                { name: '@_akhaliq', detail: 'AI papers & research', icon: icons.twitter, active: true },
                { name: 'Finnhub', detail: 'stocks + economic calendar', icon: icons.finnhub, active: true },
                { name: 'Alpha Vantage', detail: 'NASDAQ movers, sentiment', icon: icons.alphavantage, active: true },
                { name: 'CoinGecko', detail: 'crypto prices, 10k/mo', icon: icons.coingecko, active: true },
                { name: 'Kalshi', detail: 'prediction markets', icon: icons.kalshi, active: true },
                { name: 'Polymarket', detail: 'prediction markets', icon: icons.polymarket, active: true },
                { name: 'Brave Search', detail: 'web search, 2k/mo', icon: icons.brave, active: true },
                { name: 'GitHub API', detail: 'AI provider releases', icon: icons.github, active: true },
                { name: 'HuggingFace API', detail: 'trending models', icon: icons.huggingface, active: true },
                { name: 'DeFi Llama', detail: 'TVL, yields, DEX vol', icon: icons.dexscreener, active: true },
                { name: 'Yahoo Finance', detail: 'stock prices', icon: icons.yahoo, active: true },
                { name: 'DexScreener', detail: 'memecoin data', icon: icons.dexscreener, active: true },
                { name: 'Sorare GraphQL', detail: 'fantasy sports', icon: icons.sorare, active: true },
                { name: 'Manifold', detail: 'prediction markets', icon: icons.manifold, active: true },
                { name: 'Metaculus', detail: 'prediction markets', icon: icons.metaculus, active: true },
                { name: 'SEC EDGAR', detail: '8-K filings, real-time', icon: icons.secedgar, active: true },
                { name: 'TechCrunch RSS', detail: 'startup funding & launches', icon: icons.techcrunch, active: true },
                { name: 'arXiv RSS', detail: 'cs.AI + cs.CL papers', icon: icons.arxiv, active: true },
                { name: 'Hacker News', detail: 'tech news', icon: icons.hackernews, active: true },
                { name: 'Fear & Greed Index', detail: 'crypto sentiment', icon: icons.coingecko, active: true },
                { name: 'Crunchbase News', detail: 'VC deal flow & rounds', icon: icons.techcrunch, active: true },
                { name: 'PitchBook News', detail: 'PE deals, exits, fund raises', icon: icons.finnhub, active: true },
                { name: 'Fortune Term Sheet', detail: 'daily PE/VC deals recap', icon: icons.hackernews, active: true },
                { name: 'DealBook (NYT)', detail: 'M&A, PE, VC scoops', icon: icons.hackernews, active: true },
                { name: 'DeFi Llama Raises', detail: 'crypto/web3 funding rounds', icon: icons.dexscreener, active: true },
                { name: 'CB Insights', detail: 'AI deal tracking & data', icon: icons.techcrunch, active: true },
                { name: 'Carta Blog', detail: 'private market valuations', icon: icons.finnhub, active: true },
                { name: 'Axios Pro Rata', detail: 'VC/PE deals roundup', icon: icons.hackernews, active: true },
                { name: 'PE Hub', detail: 'PE transactions', icon: icons.finnhub, active: true },
                { name: 'Reuters M&A', detail: 'strategic acquisitions', icon: icons.hackernews, active: true },
                { name: 'FRED API', detail: 'Fed economic data (GDP, CPI, etc)', icon: icons.fred, active: true },
                { name: 'NewsAPI', detail: 'AI/tech headlines, 100/day', icon: icons.newsapi, active: true },
                { name: 'OpenAlex', detail: 'recent AI research papers', icon: icons.openalex, active: true },
                { name: 'Reddit AI', detail: 'r/MachineLearning + r/artificial', icon: icons.reddit, active: true },
                { name: 'Lobste.rs', detail: 'tech community news', icon: icons.lobsters, active: true },
                { name: 'GitHub Trending', detail: 'daily trending AI/ML repos', icon: icons.github, active: true },
                { name: 'Product Hunt', detail: 'top AI/tech products (pending)', icon: icons.hackernews, active: false },
                { name: 'Reuters World', detail: 'geopolitics & trade policy', icon: icons.hackernews, active: true },
                { name: 'AP News World', detail: 'global breaking news', icon: icons.hackernews, active: true },
                { name: 'GDELT Project', detail: 'global conflict & trade events', icon: icons.finnhub, active: true },
                { name: 'Grokipedia', detail: 'AI-curated encyclopedia (xAI)', icon: icons.grokipedia, active: true }
            ],
            podcasts: [
                { name: 'All-In Podcast', detail: 'tech, VC, geopolitics (weekly)', active: true },
                { name: 'Anthony Pompliano', detail: 'crypto & macro (daily)', active: true },
                { name: 'Unchained', detail: 'crypto deep dives (weekly)', active: true },
                { name: 'This Week in Startups', detail: 'startup news (2-3x/week)', active: true },
                { name: 'The Daily (NYT)', detail: 'news of the day (daily)', active: true },
                { name: 'Acquired', detail: 'tech M&A deep dives', active: true },
                { name: 'BG2 Pod', detail: 'venture & public markets', active: true },
                { name: '20VC', detail: 'VC insights & funding scoops', active: true },
                { name: 'Bankless', detail: 'crypto & DeFi', active: true },
                { name: 'Hard Fork (NYT)', detail: 'tech & AI policy', active: true },
                { name: 'Turpentine VC', detail: 'AI-native podcast network', active: true },
                { name: 'Prof G Pod', detail: 'markets & big tech (Galloway)', active: true },
                { name: "Lenny's Podcast", detail: 'product, growth & SaaS', active: true },
                { name: 'Odd Lots (Bloomberg)', detail: 'macro & markets', active: true }
            ],
            newsletters: [
                { name: 'TLDR AI', detail: 'daily AI digest', active: true },
                { name: 'TLDR Tech', detail: 'daily tech news', active: true },
                { name: 'TLDR Crypto', detail: 'daily crypto', active: true },
                { name: 'The Rundown AI', detail: 'daily, 2M readers', active: true },
                { name: 'Alpha Signal', detail: 'models & papers', active: true },
                { name: 'Morning Brew', detail: 'markets & biz', active: true },
                { name: 'The Crypto Advisor', detail: 'Substack', active: true },
                { name: 'Doomberg', detail: 'Substack', active: true },
                { name: 'The Batch', detail: 'deeplearning.ai / Andrew Ng', active: true },
                { name: 'Import AI', detail: 'AI policy & research', active: true },
                { name: "Ben's Bites", detail: 'daily AI products & startups', active: true },
                { name: 'Stratechery', detail: 'tech strategy analysis', active: true },
                { name: 'The Daily Upside', detail: 'Wall Street & deal flow', active: true },
                { name: 'Chartr', detail: 'data-driven market charts', active: true },
                { name: 'Bankless', detail: 'DeFi & crypto analysis', active: true },
                { name: 'The Defiant', detail: 'DeFi news & on-chain data', active: true },
                { name: 'Milk Road', detail: 'quick-hit crypto news', active: true },
                { name: 'SaaStr', detail: 'enterprise SaaS metrics', active: true },
                { name: 'The Neuron', detail: 'daily AI trends & tools', active: true },
                { name: 'Superhuman AI', detail: 'weekly AI digest', active: false },
                { name: 'AI Breakfast', detail: 'daily AI news roundup', active: false },
                { name: 'Meritech Capital', detail: 'public SaaS comps', active: false }
            ]
        };
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(connections));
        return;
    }

    // API endpoint for system stats
    // DGEN Watch List - DexScreener API
    if (req.url === '/api/dgen') {
        const now = Date.now();
        if (dgenCache.data && (now - dgenCache.timestamp) < CACHE_TTL_60S) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(dgenCache.data));
            return;
        }
        const DGEN_TOKENS = [
            { address: 'Cm6fNnMk7NfzStP9CZpsQA2v3jjzbcYGAxdJySmHpump', name: 'Buttcoin', symbol: 'BUTT' },
            { address: '8Jx8AAHj86wbQgUTjGuj6GTTL5Ps3cqxKRTvpaJApump', name: 'Nietzschean Penguin', symbol: 'PENGUIN' },
            { address: 'FzLMPzqz9Ybn26qRzPKDKwsLV6Kpvugh31jF7T7npump', name: 'The Black Swan', symbol: 'BlackSwan' },
            { address: '561XxnuBCvPdoJC1a7zJDuBqqcQwZ2rEsaAd1eM1pump', name: 'Subway Queen', symbol: 'SUBWAY' },
            { address: '9AvytnUKsLxPxFHFqS6VLxaxt5p6BhYNr53SD2Chpump', name: 'The Official 67 Coin', symbol: '67' }
        ];
        const addresses = DGEN_TOKENS.map(t => t.address).join(',');
        https.get(`https://api.dexscreener.com/latest/dex/tokens/${addresses}`, (apiRes) => {
            let body = '';
            apiRes.on('data', chunk => body += chunk);
            apiRes.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    const results = DGEN_TOKENS.map(token => {
                        const pair = (data.pairs || []).find(p => p.baseToken && p.baseToken.address === token.address);
                        return {
                            name: token.name,
                            symbol: token.symbol,
                            address: token.address,
                            marketCap: pair ? (pair.marketCap || pair.fdv || null) : null,
                            volume24h: pair ? (pair.volume && pair.volume.h24 || null) : null,
                            priceChange24h: pair ? (pair.priceChange && pair.priceChange.h24 || null) : null,
                            priceUsd: pair ? pair.priceUsd : null,
                            url: pair ? pair.url : null,
                            imageUrl: (pair && pair.info && pair.info.imageUrl) ? pair.info.imageUrl : null
                        };
                    });
                    const result = { tokens: results, lastUpdated: new Date().toISOString() };
                    dgenCache = { data: result, timestamp: Date.now() };
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify(result));
                } catch (err) {
                    res.writeHead(500, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: err.message }));
                }
            });
        }).on('error', (err) => {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
        });
        return;
    }

    if (req.url === '/api/usage') {
        const usageFile = path.join(ROOT, 'usage.json');
        if (fs.existsSync(usageFile)) {
            const data = fs.readFileSync(usageFile, 'utf8');
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(data);
        } else {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ contextPercent: null }));
        }
        return;
    }

    if (req.url === '/api/system') {
        // Background poller for Mini2 stats (cached, refreshed every 30s)
        if (!global._mini2Cache) global._mini2Cache = { data: { online: false }, timestamp: 0 };
        
        const refreshMini2 = async () => {
            const now = Date.now();
            if ((now - global._mini2Cache.timestamp) < SYSTEM_CACHE_TTL) return;
            try {
                const r = await fetch('http://100.66.132.34:3001/status', { signal: AbortSignal.timeout(2000) });
                const mini2Data = await r.json();
                const mini2Mem = mini2Data?.checks?.memory;
                const mini2Disk = mini2Data?.checks?.disk;
                let mini2MemPercent = 0;
                if (mini2Mem?.raw) {
                    const free = (mini2Mem.raw.match(/Pages free:\s+(\d+)/) || [])[1] || 0;
                    const active = (mini2Mem.raw.match(/Pages active:\s+(\d+)/) || [])[1] || 0;
                    const inactive = (mini2Mem.raw.match(/Pages inactive:\s+(\d+)/) || [])[1] || 0;
                    const spec = (mini2Mem.raw.match(/Pages speculative:\s+(\d+)/) || [])[1] || 0;
                    const total = parseInt(free) + parseInt(active) + parseInt(inactive) + parseInt(spec);
                    if (total > 0) mini2MemPercent = Math.round(((parseInt(active) + parseInt(spec)) / total) * 100);
                }
                let mini2Cpu = 0;
                try {
                    const cpuOut = await execAsync("ssh -o ConnectTimeout=2 mini2 \"top -l 1 | grep 'CPU usage' | awk '{print \\$3}' | tr -d '%'\" 2>/dev/null", { timeout: 5000 });
                    mini2Cpu = Math.round(parseFloat(cpuOut.stdout) || 0);
                } catch(e) {}
                global._mini2Cache = {
                    data: {
                        online: true,
                        cpu: mini2Cpu,
                        memory: mini2MemPercent,
                        disk: parseInt((mini2Disk?.usedPercent || '0').replace('%', '')),
                        ollamaModels: mini2Data?.checks?.ollama?.models || []
                    },
                    timestamp: Date.now()
                };
            } catch {
                global._mini2Cache = { data: { online: false }, timestamp: Date.now() };
            }
        };

        // Fetch local stats and mini2 in parallel (all async)
        Promise.all([getSystemStats(), refreshMini2()]).then(([stats]) => {
            stats.mini2 = global._mini2Cache.data;
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(stats));
        }).catch(() => {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Failed to get system stats' }));
        });
        return;
    }
    
    // API endpoint for usage stats (tokens, cost, messages today)
    if (req.url === '/api/usage-today') {
        const now = Date.now();
        if (usageTodayCache.data && (now - usageTodayCache.timestamp) < CACHE_TTL_60S) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(usageTodayCache.data));
            return;
        }
        try {
            const sessionsDir = path.join(os.homedir(), '.openclaw', 'agents', 'main', 'sessions');
            const files = fs.readdirSync(sessionsDir).filter(f => f.endsWith('.jsonl') && !f.endsWith('.lock'));
            let totalTokens = 0, totalCost = 0, messagesToday = 0;
            const todayStr = new Date().toISOString().slice(0, 10);
            // Read main session transcript only (most recent by mtime)
            let newest = null, newestMtime = 0;
            for (const f of files) {
                const fp = path.join(sessionsDir, f);
                const stat = fs.statSync(fp);
                if (stat.mtimeMs > newestMtime) { newestMtime = stat.mtimeMs; newest = fp; }
            }
            if (newest) {
                const lines = fs.readFileSync(newest, 'utf8').split('\n').filter(Boolean);
                for (const line of lines) {
                    try {
                        const entry = JSON.parse(line);
                        const ts = entry.timestamp ? new Date(entry.timestamp).toISOString().slice(0, 10) : '';
                        if (ts === todayStr) {
                            const msg = entry.message || entry;
                            if (msg.role === 'user') messagesToday++;
                            const usage = msg.usage || {};
                            if (usage.input || usage.output || usage.cacheRead) {
                                totalTokens += (usage.input || 0) + (usage.output || 0) + (usage.cacheRead || 0);
                            }
                            if (usage.cost && usage.cost.total) totalCost += usage.cost.total;
                        }
                    } catch {}
                }
            }
            const tokenStr = totalTokens > 1000000 ? (totalTokens / 1000000).toFixed(1) + 'M' : totalTokens > 1000 ? (totalTokens / 1000).toFixed(0) + 'K' : totalTokens.toString();
            const result = { tokensToday: tokenStr, costToday: '$' + totalCost.toFixed(2), messagesToday };
            usageTodayCache = { data: result, timestamp: Date.now() };
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(result));
        } catch (err) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ tokensToday: '--', costToday: '--', messagesToday: 0 }));
        }
        return;
    }

    // API endpoint for Jane's Mind state (reasoning/task tracking)
    const mindStateFile = path.join(ROOT, 'mind-state.json');
    if (req.url === '/api/mind' && req.method === 'GET') {
        try {
            if (fs.existsSync(mindStateFile)) {
                const data = fs.readFileSync(mindStateFile, 'utf8');
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(data);
            } else {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ task: null, steps: [], thought: 'Ready for your next request.' }));
            }
        } catch (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
        }
        return;
    }
    
    if (req.url === '/api/mind' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                fs.writeFileSync(mindStateFile, JSON.stringify(data, null, 2));
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true }));
            } catch (err) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: err.message }));
            }
        });
        return;
    }
    
    // API endpoint for AI news (fetches from RSS feeds)
    if (req.url === '/api/ai-news') {
        // Cache for 10 minutes
        const now = Date.now();
        if (aiNewsCache.data && (now - aiNewsCache.timestamp) < 600000) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(aiNewsCache.data));
            return;
        }
        
        fetchAINewsFromFeeds().then(data => {
            if (data) {
                aiNewsCache = { data, timestamp: now };
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(data));
            } else {
                // Fallback to static file
                const staticFile = path.join(ROOT, 'ai-news.json');
                if (fs.existsSync(staticFile)) {
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(fs.readFileSync(staticFile));
                } else {
                    res.writeHead(500, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Failed to fetch AI news' }));
                }
            }
        });
        return;
    }
    
    // API endpoint for mindmap/Second Brain stats
    // Smart Notifications from Mini #2
    if (req.url === '/api/notifications') {
        const now = Date.now();
        if (notificationsCache.data && (now - notificationsCache.timestamp) < CACHE_TTL_30S) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(notificationsCache.data));
            return;
        }
        const fetchNotifications = () => new Promise((resolve) => {
            const r = require('http').get('http://100.66.132.34:3002/alerts', { timeout: 5000 }, (resp) => {
                let d = '';
                resp.on('data', c => d += c);
                resp.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve([]); } });
            });
            r.on('error', () => resolve([]));
            r.on('timeout', () => { r.destroy(); resolve([]); });
        });
        fetchNotifications().then(alerts => {
            notificationsCache = { data: alerts, timestamp: Date.now() };
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(alerts));
        });
        return;
    }

    if (req.url === '/api/notifications/dismiss' && req.method === 'POST') {
        let body = '';
        req.on('data', c => body += c);
        req.on('end', () => {
            const opts = { method: 'POST', hostname: '100.66.132.34', port: 3002, path: '/alerts/dismiss', headers: { 'Content-Type': 'application/json' } };
            const r = require('http').request(opts, (resp) => {
                let d = '';
                resp.on('data', c => d += c);
                resp.on('end', () => { res.writeHead(200, { 'Content-Type': 'application/json' }); res.end(d); });
            });
            r.on('error', () => { res.writeHead(500); res.end('{"error":"failed"}'); });
            r.write(body);
            r.end();
        });
        return;
    }

    if (req.url === '/api/notifications/read' && req.method === 'POST') {
        const opts = { method: 'POST', hostname: '100.66.132.34', port: 3002, path: '/alerts/read' };
        const r = require('http').request(opts, (resp) => {
            let d = '';
            resp.on('data', c => d += c);
            resp.on('end', () => { res.writeHead(200, { 'Content-Type': 'application/json' }); res.end(d); });
        });
        r.on('error', () => { res.writeHead(500); res.end('{"error":"failed"}'); });
        r.end();
        return;
    }

    if (req.url === '/api/mindmap') {
        const stats = getMindmapStats();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(stats));
        return;
    }
    
    // API endpoint for Jane's tasks
    if (req.url === '/api/tasks') {
        const tasks = getJaneTasks();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(tasks));
        return;
    }
    
    // API endpoint for active sessions/sub-agents
    // Returns session data from OpenClaw's sessions list
    if (req.url === '/api/sessions') {
        const sessionsFile = path.join(ROOT, 'sessions.json');
        if (fs.existsSync(sessionsFile)) {
            const data = JSON.parse(fs.readFileSync(sessionsFile, 'utf8'));
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(data));
        } else {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ 
                sessions: [], 
                lastUpdated: null,
                note: 'Session data updated by Jane during heartbeats'
            }));
        }
        return;
    }
    
    // API endpoint for cron jobs
    if (req.url === '/api/cron') {
        const cronFile = path.join(ROOT, 'cron-jobs.json');
        if (fs.existsSync(cronFile)) {
            const data = JSON.parse(fs.readFileSync(cronFile, 'utf8'));
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(data));
        } else {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ jobs: [], lastUpdated: null }));
        }
        return;
    }
    
    // API endpoint for TikTok stats (reads from JSON, updated by Jane's heartbeat)
    if (req.url === '/api/tiktok') {
        const statsFile = path.join(ROOT, 'tiktok-stats.json');
        const midnightFile = path.join(ROOT, 'tiktok-midnight.json');
        
        if (fs.existsSync(statsFile)) {
            const stats = JSON.parse(fs.readFileSync(statsFile, 'utf8'));
            stats.note = 'Updated via heartbeat browser scraping (TikTok has no public API)';
            
            // Add top-level fields for backwards compatibility
            if (stats.profile) {
                stats.followers = stats.profile.followers;
                stats.likes = stats.profile.likes;
            }
            
            // Normalize videos array (may be 'videos' or 'recentVideos')
            if (!stats.recentVideos && stats.videos) {
                stats.recentVideos = stats.videos.map(v => ({
                    title: v.title || v.url?.split('/').pop() || 'Video',
                    views: v.views,
                    url: v.url
                }));
            }
            
            // Calculate total views from all videos
            let totalViews = 0;
            if (stats.recentVideos) {
                totalViews += stats.recentVideos.reduce((sum, v) => sum + (typeof v.views === 'number' ? v.views : parseInt(v.views) || 0), 0);
            }
            if (stats.topVideos) {
                stats.topVideos.forEach(v => {
                    const views = typeof v.views === 'string' ? parseFloat(v.views.replace('K', '')) * (v.views.includes('K') ? 1000 : 1) : v.views;
                    totalViews += views || 0;
                });
            }
            stats.totalViews = Math.round(totalViews);
            
            // Calculate "since midnight" changes
            const now = new Date();
            const todayMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate()).toISOString().split('T')[0];
            
            let midnight = {};
            if (fs.existsSync(midnightFile)) {
                midnight = JSON.parse(fs.readFileSync(midnightFile, 'utf8'));
            }
            
            // If we don't have today's midnight baseline, or it's a new day, save current as baseline
            if (!midnight.date || midnight.date !== todayMidnight) {
                midnight = {
                    date: todayMidnight,
                    followers: stats.profile?.followers || stats.followers || 0,
                    likes: stats.profile?.likes || stats.likes || 0,
                    views: stats.totalViews || 0,
                    savedAt: now.toISOString()
                };
                fs.writeFileSync(midnightFile, JSON.stringify(midnight, null, 2));
            }
            
            // Calculate changes since midnight
            const currentFollowers = stats.profile?.followers || stats.followers || 0;
            const currentLikes = stats.profile?.likes || stats.likes || 0;
            const currentViews = stats.totalViews || 0;
            
            stats.changes24h = {
                followers: currentFollowers - (midnight.followers || currentFollowers),
                likes: currentLikes - (midnight.likes || currentLikes),
                views: currentViews - (midnight.views || currentViews),
                since: midnight.date,
                note: 'Changes since midnight EST'
            };
            
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(stats));
        } else {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'No TikTok stats available yet' }));
        }
        return;
    }
    
    // API endpoint for Panini collection (scraped from profile, updated periodically)
    if (req.url === '/api/panini') {
        const collectionFile = path.join(ROOT, 'panini-collection.json');
        if (fs.existsSync(collectionFile)) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(fs.readFileSync(collectionFile));
        } else {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'No Panini collection data available' }));
        }
        return;
    }
    
    // API endpoint for trading positions (with computed summary)
    if (req.url === '/api/trading') {
        const positionsFile = path.join(WORKSPACE, 'trading', 'positions.json');
        if (fs.existsSync(positionsFile)) {
            try {
                const data = JSON.parse(fs.readFileSync(positionsFile, 'utf8'));
                // Compute summary from realized trades
                if (data.realizedTrades && data.realizedTrades.length > 0) {
                    const totalRealized = data.realizedTrades.reduce((sum, t) => sum + (t.realizedPnL || 0), 0);
                    const totalCost = data.realizedTrades.reduce((sum, t) => sum + (t.costBasis || 0), 0);
                    data.summary = {
                        totalRealizedPnL: totalRealized,
                        totalRealizedPercent: totalCost > 0 ? (totalRealized / totalCost * 100) : 0,
                        tradeCount: data.realizedTrades.length
                    };
                }
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(data));
            } catch (e) {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(fs.readFileSync(positionsFile));
            }
        } else {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ positions: [], error: 'No positions file' }));
        }
        return;
    }
    
    // API endpoint for Kalshi positions
    if (req.url === '/api/kalshi/positions') {
        const now = Date.now();
        if (kalshiCache.data && (now - kalshiCache.timestamp) < CACHE_TTL_60S) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(kalshiCache.data));
            return;
        }
        (async () => {
        const crypto = require('crypto');
        try {
            const API_KEY = fs.readFileSync(path.join(WORKSPACE, '.secrets', 'kalshi_api_key.txt'), 'utf8').trim();
            const PRIVATE_KEY = fs.readFileSync(path.join(WORKSPACE, '.secrets', 'kalshi_private_key.pem'), 'utf8');
            const KALSHI_BASE = 'https://api.elections.kalshi.com';

            const TICKER_NAMES = {
                'KXNFLSBMVP-26-DMAYE10': 'Drake Maye Super Bowl MVP',
                'KXSB-26-NE': 'Patriots Win Super Bowl',
                'KXSUPERBOWLAD-SB2026-TEMU': 'Temu Super Bowl Ad',
                'KXSUPERBOWLAD-SB2026-ANTHROPIC': 'Anthropic Super Bowl Ad',
                'KXNFLMENTION-SB26-SCHE': "'Schedule' Mentioned in Super Bowl"
            };

            function kalshiSign(method, apiPath) {
                const timestamp = Date.now().toString();
                const msgString = timestamp + method + apiPath;
                const sign = crypto.createSign('RSA-SHA256');
                sign.update(msgString);
                sign.end();
                const signature = sign.sign({
                    key: PRIVATE_KEY,
                    padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
                    saltLength: crypto.constants.RSA_PSS_SALTLEN_DIGEST,
                });
                return { timestamp, signature: signature.toString('base64') };
            }

            function kalshiGet(apiPath) {
                return new Promise((resolve, reject) => {
                    const { timestamp, signature } = kalshiSign('GET', apiPath);
                    const url = new URL(KALSHI_BASE + apiPath);
                    const options = {
                        hostname: url.hostname,
                        path: url.pathname + url.search,
                        method: 'GET',
                        headers: {
                            'KALSHI-ACCESS-KEY': API_KEY,
                            'KALSHI-ACCESS-SIGNATURE': signature,
                            'KALSHI-ACCESS-TIMESTAMP': timestamp,
                            'Content-Type': 'application/json'
                        }
                    };
                    const r = https.request(options, (resp) => {
                        let data = '';
                        resp.on('data', chunk => data += chunk);
                        resp.on('end', () => {
                            try { resolve(JSON.parse(data)); }
                            catch(e) { resolve(data); }
                        });
                    });
                    r.on('error', reject);
                    r.end();
                });
            }

            const [positionsData, settlementsData, balanceData] = await Promise.all([
                kalshiGet('/trade-api/v2/portfolio/positions'),
                kalshiGet('/trade-api/v2/portfolio/settlements'),
                kalshiGet('/trade-api/v2/portfolio/balance')
            ]);

            // Fetch market data for each active position
            const positions = positionsData?.market_positions || [];
            const marketTickers = [...new Set(positions.map(p => p.ticker))];
            const marketDataMap = {};
            await Promise.all(marketTickers.map(async t => {
                try {
                    const md = await kalshiGet(`/trade-api/v2/markets/${t}`);
                    marketDataMap[t] = md?.market || md;
                } catch(e) {}
            }));

            const active = positions.filter(p => (p.total_traded || 0) > 0).map(p => {
                const market = marketDataMap[p.ticker] || {};
                const side = (p.position || 0) > 0 ? 'YES' : (p.position || 0) < 0 ? 'NO' : 'NONE';
                const shares = Math.abs(p.position || 0);
                const totalCost = p.market_exposure || p.total_traded || 0;
                const avgEntry = shares > 0 ? (totalCost / shares) : 0;
                const currentPrice = side === 'YES' ? (market.yes_bid || market.last_price || 0) : (market.no_bid || (100 - (market.last_price || 0)));
                const pnl = shares > 0 ? ((currentPrice - avgEntry) * shares / 100) : 0;
                return {
                    ticker: p.ticker,
                    name: TICKER_NAMES[p.ticker] || market.title || p.ticker,
                    side,
                    shares,
                    avgEntry: avgEntry / 100,
                    currentPrice: currentPrice / 100,
                    pnl: pnl,
                    expiration: market.expiration_time || market.close_time || null,
                    status: market.status || 'unknown'
                };
            }).filter(p => p.shares > 0);

            const settlements = (settlementsData?.settlements || []).map(s => {
                const tk = s.ticker;
                const yesCount = s.yes_count || 0;
                const noCount = s.no_count || 0;
                const result = s.market_result;
                // Determine primary side (net position)
                const side = (noCount > yesCount) ? 'NO' : 'YES';
                const shares = Math.max(yesCount, noCount);
                const totalCost = (s.yes_total_cost || 0) + (s.no_total_cost || 0);
                // Payout: winning side gets 100 per share
                const payout = result === 'yes' ? (yesCount * 100) : result === 'no' ? (noCount * 100) : 0;
                const pnl = (payout - totalCost) / 100;
                const won = pnl >= 0;
                return {
                    ticker: tk,
                    name: TICKER_NAMES[tk] || tk,
                    side,
                    shares,
                    totalCost: totalCost / 100,
                    result,
                    won,
                    pnl,
                    settledAt: s.settled_time || null
                };
            }).sort((a, b) => new Date(b.settledAt || 0) - new Date(a.settledAt || 0));

            const result = {
                active,
                settled: settlements,
                balance: balanceData?.balance || balanceData || {},
                timestamp: Date.now()
            };
            kalshiCache = { data: result, timestamp: Date.now() };
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(result));
        } catch(e) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: e.message }));
        }
        })();
        return;
    }

    // API endpoint for wallet balances (live from Solana RPC)
    if (req.url === '/api/wallet') {
        const now = Date.now();
        if (walletCache.data && (now - walletCache.timestamp) < CACHE_TTL_30S) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(walletCache.data));
            return;
        }
        const walletAddresses = {
            jane: { address: 'ExgSrepdc3DHTJ3xRzyMofXwTofvmRu6iSqm66oaYK6L', label: "Jane's Wallet" },
            josh: { address: '6EYvnXTGFj5HQzLAJMYs4EpYnzQ6A4gUVrG5vncP96h8', label: "Josh's Wallet" }
        };
        
        const fetchBalance = (address) => new Promise((resolve) => {
            const postData = JSON.stringify({
                jsonrpc: '2.0', id: 1, method: 'getBalance', params: [address]
            });
            const req = https.request({
                hostname: 'api.mainnet-beta.solana.com',
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        const result = JSON.parse(data);
                        resolve(result.result?.value / 1e9 || 0);
                    } catch { resolve(0); }
                });
            });
            req.on('error', () => resolve(0));
            req.write(postData);
            req.end();
        });
        
        const fetchSolPrice = () => new Promise((resolve) => {
            https.get('https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd', 
                { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        const result = JSON.parse(data);
                        resolve(result.solana?.usd || 200);
                    } catch { resolve(200); }
                });
            }).on('error', () => resolve(200));
        });
        
        Promise.all([
            fetchBalance(walletAddresses.jane.address),
            fetchBalance(walletAddresses.josh.address),
            fetchSolPrice()
        ]).then(([janeBal, joshBal, solPrice]) => {
            const wallets = {
                jane: {
                    address: walletAddresses.jane.address,
                    balance: janeBal,
                    usd: janeBal * solPrice,
                    label: walletAddresses.jane.label
                },
                josh: {
                    address: walletAddresses.josh.address,
                    balance: joshBal,
                    usd: joshBal * solPrice,
                    label: walletAddresses.josh.label
                },
                solPrice,
                total: {
                    balance: janeBal + joshBal,
                    usd: (janeBal + joshBal) * solPrice
                },
                lastUpdated: new Date().toISOString()
            };
            walletCache = { data: wallets, timestamp: Date.now() };
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(wallets));
        }).catch(() => {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Failed to fetch wallet data' }));
        });
        return;
    }
    
    // API endpoint for Buttcoin balance in Josh's wallet
    if (req.url === '/api/buttcoin') {
        const now = Date.now();
        if (buttcoinCache.data && (now - buttcoinCache.timestamp) < CACHE_TTL_30S) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(buttcoinCache.data));
            return;
        }
        const BUTTCOIN_MINT = 'Cm6fNnMk7NfzStP9CZpsQA2v3jjzbcYGAxdJySmHpump';
        const JOSH_WALLET = '6EYvnXTGFj5HQzLAJMYs4EpYnzQ6A4gUVrG5vncP96h8';
        
        // Fetch token balance from Solana RPC
        const fetchTokenBalance = () => new Promise((resolve) => {
            const postData = JSON.stringify({
                jsonrpc: '2.0', id: 1,
                method: 'getTokenAccountsByOwner',
                params: [JOSH_WALLET, { mint: BUTTCOIN_MINT }, { encoding: 'jsonParsed' }]
            });
            const req = https.request({
                hostname: 'api.mainnet-beta.solana.com',
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        const result = JSON.parse(data);
                        const tokenInfo = result.result?.value?.[0]?.account?.data?.parsed?.info;
                        resolve(tokenInfo?.tokenAmount?.uiAmount || 0);
                    } catch { resolve(20490.24); } // fallback
                });
            });
            req.on('error', () => resolve(20490.24));
            req.write(postData);
            req.end();
        });
        
        // Fetch price from DexScreener
        const fetchPrice = () => new Promise((resolve) => {
            https.get('https://api.dexscreener.com/latest/dex/tokens/' + BUTTCOIN_MINT,
                { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        const result = JSON.parse(data);
                        const price = parseFloat(result.pairs?.[0]?.priceUsd || '0.0247');
                        resolve(price);
                    } catch { resolve(0.0247); }
                });
            }).on('error', () => resolve(0.0247));
        });
        
        Promise.all([fetchTokenBalance(), fetchPrice()]).then(([balance, price]) => {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                token: 'Buttcoin',
                symbol: 'BUTT',
                mint: BUTTCOIN_MINT,
                balance,
                price,
                usd: balance * price,
                lastUpdated: new Date().toISOString()
            }));
        });
        return;
    }
    
    // API endpoint for bubble cluster mindmap with artifacts
    if (req.url === '/api/bubbles') {
        const bubbles = getBubbleData();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(bubbles));
        return;
    }
    
    // API endpoint for meme coin tracker - LIVE Solana memecoins via GeckoTerminal
    if (req.url === '/api/memecoins') {
        const now = Date.now();
        if (memecoinsCache.data && (now - memecoinsCache.timestamp) < CACHE_TTL_60S) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(memecoinsCache.data));
            return;
        }
        const MIN_MCAP = 100000;    // $100K minimum
        const MAX_MCAP = 100000000; // $100M maximum
        
        // Fetch trending pools from GeckoTerminal (no search terms needed!)
        const fetchPage = (page) => new Promise((resolve) => {
            const url = `https://api.geckoterminal.com/api/v2/networks/solana/trending_pools?page=${page}`;
            https.get(url, { headers: { 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0' }, timeout: 10000 }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        const result = JSON.parse(data);
                        resolve(result.data || []);
                    } catch { resolve([]); }
                });
            }).on('error', () => resolve([]));
        });
        
        // Fetch multiple pages to get more results
        Promise.all([fetchPage(1), fetchPage(2), fetchPage(3)]).then((pages) => {
            const allPools = pages.flat();
            
            // Filter by market cap and deduplicate
            const seen = new Set();
            const filtered = allPools.filter(pool => {
                if (!pool || !pool.attributes) return false;
                
                const attrs = pool.attributes;
                const mcap = parseFloat(attrs.fdv_usd || 0);
                const vol = parseFloat(attrs.volume_usd?.h24 || 0);
                
                // Check market cap range
                if (mcap < MIN_MCAP || mcap > MAX_MCAP) return false;
                
                // Must have meaningful volume
                if (vol < 10000) return false;
                
                // Get token name (first part of pair name)
                const name = (attrs.name || '').split(' / ')[0];
                if (!name || seen.has(name)) return false;
                
                // Skip stablecoins and major tokens
                const skipTokens = ['SOL', 'USDC', 'USDT', 'WETH', 'USD1', 'WSOL'];
                if (skipTokens.includes(name.toUpperCase())) return false;
                
                seen.add(name);
                return true;
            });
            
            // Sort by 24h volume descending
            filtered.sort((a, b) => {
                const volA = parseFloat(a.attributes.volume_usd?.h24 || 0);
                const volB = parseFloat(b.attributes.volume_usd?.h24 || 0);
                return volB - volA;
            });
            
            // Format response - top 12
            const top12 = filtered.slice(0, 12);
            
            // Fetch age from DEX Screener for each coin (parallel)
            // Fetch age and image from DEX Screener (single call for both)
            const fetchTokenDetails = (tokenName) => new Promise((resolve) => {
                const searchUrl = `https://api.dexscreener.com/latest/dex/search?q=${encodeURIComponent(tokenName)}`;
                https.get(searchUrl, { headers: { 'User-Agent': 'Mozilla/5.0' }, timeout: 5000 }, (res) => {
                    let data = '';
                    res.on('data', chunk => data += chunk);
                    res.on('end', () => {
                        try {
                            const result = JSON.parse(data);
                            const solanaPair = (result.pairs || []).find(p => p.chainId === 'solana');
                            resolve({
                                createdAt: solanaPair?.pairCreatedAt || null,
                                imageUrl: solanaPair?.info?.imageUrl || null
                            });
                        } catch { resolve({ createdAt: null, imageUrl: null }); }
                    });
                }).on('error', () => resolve({ createdAt: null, imageUrl: null }));
            });
            
            // Helper to format age
            const formatAge = (createdAt) => {
                if (!createdAt) return null;
                const now = Date.now();
                const created = typeof createdAt === 'number' ? createdAt : new Date(createdAt).getTime();
                const diffMs = now - created;
                const diffMins = Math.floor(diffMs / 60000);
                const diffHours = Math.floor(diffMs / 3600000);
                const diffDays = Math.floor(diffMs / 86400000);
                
                if (diffMins < 60) return `${diffMins}m`;
                if (diffHours < 24) return `${diffHours}h`;
                if (diffDays < 30) return `${diffDays}d`;
                if (diffDays < 365) return `${Math.floor(diffDays / 30)}mo`;
                return `${Math.floor(diffDays / 365)}y`;
            };
            
            // Get token details (age + image) for all tokens
            const tokenNames = top12.map(pool => (pool.attributes.name || '').split(' / ')[0]);
            const tokenAddresses = top12.map(pool => {
                const tokenId = pool.relationships?.base_token?.data?.id || '';
                return tokenId.replace('solana_', '');
            });
            
            Promise.all(tokenNames.map(fetchTokenDetails)).then((tokenDetails) => {
                const memecoins = top12.map((pool, i) => {
                    const attrs = pool.attributes;
                    const name = (attrs.name || '').split(' / ')[0];
                    const priceChange = parseFloat(attrs.price_change_percentage?.h24 || 0);
                    const details = tokenDetails[i] || {};
                    
                    return {
                        name: name,
                        symbol: name,
                        chain: 'solana',
                        chainIcon: '◎',
                        price: parseFloat(attrs.base_token_price_usd || 0),
                        priceChange24h: priceChange,
                        volume24h: parseFloat(attrs.volume_usd?.h24 || 0),
                        marketCap: parseFloat(attrs.fdv_usd || 0),
                        liquidity: parseFloat(attrs.reserve_in_usd || 0),
                        dexUrl: `https://www.geckoterminal.com/solana/pools/${pool.id?.split('_')[1] || ''}`,
                        poolAddress: pool.id?.split('_')[1] || '',
                        tokenAddress: tokenAddresses[i] || '',
                        imageUrl: details.imageUrl || null,
                        age: formatAge(details.createdAt),
                        createdAt: details.createdAt
                    };
                });
                
                const result = {
                    memecoins,
                    lastUpdated: new Date().toISOString(),
                    source: 'GeckoTerminal',
                    filters: { minMcap: MIN_MCAP, maxMcap: MAX_MCAP }
                };
                memecoinsCache = { data: result, timestamp: Date.now() };
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(result));
            });
        }).catch(err => {
            console.error('Memecoin fetch error:', err);
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Failed to fetch memecoins' }));
        });
        
        return;
    }
    
    // API endpoint for Sorare lineup (reads from JSON, triggers background refresh if stale)
    // NBA live games — returns teams currently playing
    if (req.url === '/api/nba-live') {
        const now = Date.now();
        if (nbaLiveCache.data && (now - nbaLiveCache.timestamp) < CACHE_TTL_30S) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(nbaLiveCache.data));
            return;
        }
        const nbaUrl = 'https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json';
        https.get(nbaUrl, { headers: { 'User-Agent': 'JaneDashboard/1.0' } }, (nbaRes) => {
            let body = '';
            nbaRes.on('data', c => body += c);
            nbaRes.on('end', () => {
                try {
                    const d = JSON.parse(body);
                    const games = (d.scoreboard || {}).games || [];
                    const liveTeams = [];
                    games.forEach(g => {
                        const status = (g.gameStatusText || '').toLowerCase();
                        // Live if contains Q1-Q4, OT, or "half"
                        const isLive = /q[1-4]|ot|half/i.test(status);
                        if (isLive) {
                            liveTeams.push(g.homeTeam?.teamName || '');
                            liveTeams.push(g.awayTeam?.teamName || '');
                        }
                    });
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    const result = { liveTeams, games: games.map(g => ({ home: g.homeTeam?.teamName, away: g.awayTeam?.teamName, status: g.gameStatusText })) };
                    nbaLiveCache = { data: result, timestamp: Date.now() };
                    res.end(JSON.stringify(result));
                } catch(e) {
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ liveTeams: [], games: [] }));
                }
            });
        }).on('error', () => {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ liveTeams: [], games: [] }));
        });
        return;
    }

    if (req.url === '/api/cron-schedule') {
        const cronFile = path.join(ROOT, 'cron-schedule.json');
        if (fs.existsSync(cronFile)) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(fs.readFileSync(cronFile, 'utf8'));
        } else {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end('{"error":"not found"}');
        }
        return;
    }

    if (req.url === '/api/sorare') {
        const statsFile = path.join(ROOT, 'sorare-stats.json');
        // Trigger background refresh if file is >5 min old
        if (fs.existsSync(statsFile)) {
            const age = Date.now() - fs.statSync(statsFile).mtimeMs;
            if (age > 5 * 60 * 1000 && !global._sorareRefreshing) {
                global._sorareRefreshing = true;
                const { exec: execChild } = require('child_process');
                execChild(`bash "${path.join(ROOT, 'fetch-sorare.sh')}"`, { timeout: 60000 }, (err) => {
                    global._sorareRefreshing = false;
                    if (err) console.error('Sorare refresh error:', err.message);
                    else console.log('Sorare data refreshed');
                });
            }
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(fs.readFileSync(statsFile));
        } else {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'No Sorare stats available' }));
        }
        return;
    }
    
    // API endpoint for Polymarket prediction markets (competitive markets with 20-80% odds)
    if (req.url === '/api/predictions') {
        const now = Date.now();
        if (predictionsCache.data && (now - predictionsCache.timestamp) < 300000) { // 5 min TTL
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(predictionsCache.data));
            return;
        }
        const mainUrl = 'https://gamma-api.polymarket.com/markets?closed=false&order=volume24hr&ascending=false&limit=100';
        const superBowlUrl = 'https://gamma-api.polymarket.com/markets?closed=false&limit=50&tag=nfl';
        // Business & Finance specific tags
        const cryptoUrl = 'https://gamma-api.polymarket.com/markets?closed=false&order=volume24hr&ascending=false&limit=30&tag=crypto';
        const businessUrl = 'https://gamma-api.polymarket.com/markets?closed=false&order=volume24hr&ascending=false&limit=30&tag=business';
        const economyUrl = 'https://gamma-api.polymarket.com/markets?closed=false&order=volume24hr&ascending=false&limit=30&tag=economy';
        const techUrl = 'https://gamma-api.polymarket.com/markets?closed=false&order=volume24hr&ascending=false&limit=30&tag=tech';
        // Kalshi markets (events with nested markets)
        const kalshiUrl = 'https://api.elections.kalshi.com/trade-api/v2/events?limit=50&status=open&with_nested_markets=true';
        // Manifold Markets - high liquidity markets
        const manifoldUrl = 'https://api.manifold.markets/v0/search-markets?sort=liquidity&limit=50&filter=open';
        // Metaculus - top questions
        const metaculusUrl = 'https://www.metaculus.com/api2/questions/?status=open&type=forecast&order_by=-activity&limit=30';
        
        const fetchUrl = (url) => new Promise((resolve, reject) => {
            https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try { resolve(JSON.parse(data)); } 
                    catch (e) { resolve([]); }
                });
            }).on('error', () => resolve([]));
        });
        
        Promise.all([
            fetchUrl(mainUrl), 
            fetchUrl(superBowlUrl),
            fetchUrl(cryptoUrl),
            fetchUrl(businessUrl),
            fetchUrl(economyUrl),
            fetchUrl(techUrl),
            fetchUrl(kalshiUrl),
            fetchUrl(manifoldUrl),
            fetchUrl(metaculusUrl)
        ]).then(([mainMarkets, nflMarkets, cryptoMarkets, businessMarkets, economyMarkets, techMarkets, kalshiData, manifoldData, metaculusData]) => {
            // Combine all finance/business markets
            const financeMarkets = [...cryptoMarkets, ...businessMarkets, ...economyMarkets, ...techMarkets];
            
            // Parse Kalshi markets from events
            const kalshiMarkets = [];
            const kalshiEvents = kalshiData.events || [];
            kalshiEvents.forEach(event => {
                const markets = event.markets || [];
                markets.forEach(m => {
                    if (m.volume_24h > 50 && m.title && !m.title.includes(',') && m.yes_bid > 0) {
                        kalshiMarkets.push({
                            question: m.title,
                            yesOdds: Math.round(m.yes_bid || 50),
                            noOdds: Math.round(100 - (m.yes_bid || 50)),
                            volume24h: m.volume_24h || 0,
                            totalVolume: m.volume || 0,
                            slug: m.ticker,
                            endDate: m.close_time,
                            source: 'Kalshi'
                        });
                    }
                });
            });
            
            // Parse Manifold Markets
            const manifoldMarkets = [];
            const manifoldList = Array.isArray(manifoldData) ? manifoldData : [];
            manifoldList.forEach(m => {
                if (m.probability && m.totalLiquidity > 100) {
                    manifoldMarkets.push({
                        question: m.question,
                        yesOdds: Math.round((m.probability || 0.5) * 100),
                        noOdds: Math.round((1 - (m.probability || 0.5)) * 100),
                        volume24h: m.volume24Hours || 0,
                        totalVolume: m.totalLiquidity || 0,
                        slug: m.slug || m.id,
                        endDate: m.closeTime,
                        source: 'Manifold'
                    });
                }
            });
            
            // Parse Metaculus questions
            const metaculusMarkets = [];
            const metaculusResults = metaculusData?.results || [];
            metaculusResults.forEach(q => {
                if (q.community_prediction && q.community_prediction.full) {
                    const prob = q.community_prediction.full.q2 || 0.5;
                    metaculusMarkets.push({
                        question: q.title,
                        yesOdds: Math.round(prob * 100),
                        noOdds: Math.round((1 - prob) * 100),
                        volume24h: q.activity || 1000, // Metaculus uses activity instead of volume
                        totalVolume: q.number_of_forecasters || 0,
                        slug: `metaculus-${q.id}`,
                        endDate: q.resolve_time,
                        source: 'Metaculus'
                    });
                }
            });
            
            const parseMarket = m => {
                const prices = JSON.parse(m.outcomePrices || '["0.5","0.5"]');
                const yesPrice = parseFloat(prices[0]) * 100;
                const noPrice = parseFloat(prices[1]) * 100;
                
                const market = {
                    question: m.question,
                    yesOdds: Math.round(yesPrice),
                    noOdds: Math.round(noPrice),
                    volume24h: m.volume24hr || 0,
                    totalVolume: m.volumeNum || 0,
                    slug: m.slug,
                    image: m.icon || m.image,
                    endDate: m.endDate,
                    source: 'Polymarket'
                };
                
                // Parse team names for sports matchups (e.g., "Bruins vs. Lightning")
                const vsMatch = (m.question || '').match(/^(.+?)\s+vs\.?\s+(.+?)$/i);
                if (vsMatch) {
                    market.isSportsMatch = true;
                    market.teams = {
                        team1: { name: vsMatch[1].trim(), odds: Math.round(yesPrice) },
                        team2: { name: vsMatch[2].trim(), odds: Math.round(noPrice) }
                    };
                }
                
                return market;
            };
            
            const simplified = mainMarkets.map(parseMarket);
            const nflSimplified = nflMarkets.map(parseMarket);
            const financeSimplified = financeMarkets.map(parseMarket);
            
            // Super Bowl LX - pin until Feb 10, 2026 (day after game)
            const superBowlDate = new Date('2026-02-10T00:00:00');
            const now = new Date();
            let pinnedMarket = null;
            
            if (now < superBowlDate) {
                // Search both lists for Super Bowl markets
                const allMarkets = [...simplified, ...nflSimplified];
                const seahawks = allMarkets.find(m => m.question && m.question.toLowerCase().includes('seahawks') && m.question.toLowerCase().includes('super bowl'));
                const patriots = allMarkets.find(m => m.question && m.question.toLowerCase().includes('patriots') && m.question.toLowerCase().includes('super bowl'));
                
                if (seahawks && patriots) {
                    pinnedMarket = {
                        question: 'Super Bowl LX: Seahawks vs Patriots',
                        yesOdds: seahawks.yesOdds,
                        noOdds: patriots.yesOdds,
                        volume24h: (seahawks.volume24h || 0) + (patriots.volume24h || 0),
                        slug: 'will-the-seattle-seahawks-win-super-bowl-2026',
                        isPinned: true,
                        source: 'Polymarket',
                        teams: {
                            favorite: { name: 'Seahawks', odds: seahawks.yesOdds },
                            underdog: { name: 'Patriots', odds: patriots.yesOdds }
                        }
                    };
                }
            }
            
            // Combine all markets, removing duplicates by slug
            const allMarketsRaw = [...simplified, ...financeSimplified, ...kalshiMarkets, ...manifoldMarkets, ...metaculusMarkets];
            const seenSlugs = new Set();
            const allMarketsDeduped = allMarketsRaw.filter(m => {
                if (seenSlugs.has(m.slug)) return false;
                seenSlugs.add(m.slug);
                return true;
            });
            
            // Filter for competitive markets (odds between 10% and 90%, min volume by source)
            const competitive = allMarketsDeduped.filter(m => {
                if (m.question && m.question.toLowerCase().includes('super bowl')) return false;
                // Different volume thresholds per source (Kalshi uses contracts, not $)
                const minVolume = m.source === 'Kalshi' ? 50 : 
                                  m.source === 'Manifold' ? 100 : 
                                  m.source === 'Metaculus' ? 0 : 10000;
                if ((m.volume24h || 0) < minVolume) return false;
                return m.yesOdds >= 10 && m.yesOdds <= 90;
            });
            
            competitive.sort((a, b) => b.volume24h - a.volume24h);
            
            // Detect sports markets (typically have "vs." or sports-related slugs)
            const isSportsMarket = (m) => {
                const q = (m.question || '').toLowerCase();
                const s = (m.slug || '').toLowerCase();
                // "vs." pattern or sports league prefixes in slug
                return q.includes(' vs. ') || q.includes(' vs ') ||
                       s.startsWith('nba-') || s.startsWith('nfl-') || 
                       s.startsWith('nhl-') || s.startsWith('mlb-') ||
                       s.startsWith('ncaa-') || s.startsWith('ufc-');
            };
            
            // Detect M&A (Mergers & Acquisitions) markets
            const isMandAMarket = (m) => {
                const q = (m.question || '').toLowerCase();
                return q.includes('acquire') || q.includes('acquisition') || q.includes('merger') ||
                       q.includes('merge') || q.includes('buyout') || q.includes('buy out') ||
                       q.includes('takeover') || q.includes('take over') || q.includes('purchased by') ||
                       q.includes('will buy') || q.includes('buying') || q.includes('deal to buy');
            };
            
            // Detect finance/business markets (excluding M&A which has its own category)
            const isFinanceMarket = (m) => {
                if (isMandAMarket(m)) return false;
                const q = (m.question || '').toLowerCase();
                return q.includes('bitcoin') || q.includes('crypto') || q.includes('btc') ||
                       q.includes('eth') || q.includes('solana') || q.includes('price') ||
                       q.includes('stock') || q.includes('market') || q.includes('fed') ||
                       q.includes('recession') || q.includes('rate') || q.includes('inflation') ||
                       q.includes('gdp') || q.includes('ipo') ||
                       q.includes('company') || q.includes('ceo') || q.includes('layoff') ||
                       q.includes('apple') || q.includes('google') || q.includes('meta') ||
                       q.includes('amazon') || q.includes('microsoft') || q.includes('nvidia') ||
                       q.includes('tesla') || q.includes('openai') || q.includes('ai ') ||
                       q.includes('earnings') || q.includes('revenue') || q.includes('s&p') ||
                       q.includes('dow') || q.includes('nasdaq');
            };
            
            // Build balanced list with M&A priority
            const sports = competitive.filter(isSportsMarket);
            const manda = competitive.filter(m => isMandAMarket(m)); // Already filtered to >$50k
            const finance = competitive.filter(m => !isSportsMarket(m) && !isMandAMarket(m) && isFinanceMarket(m));
            const others = competitive.filter(m => !isSportsMarket(m) && !isMandAMarket(m) && !isFinanceMarket(m));
            
            let balanced = [];
            let sportsCount = 0;
            let financeCount = 0;
            let mandaCount = 0;
            
            // First, add up to 5 M&A markets (priority)
            for (let i = 0; i < manda.length && mandaCount < 5; i++) {
                balanced.push(manda[i]);
                mandaCount++;
            }
            
            // Then add top finance markets (6 minimum)
            for (let i = 0; i < finance.length && financeCount < 6; i++) {
                balanced.push(finance[i]);
                financeCount++;
            }
            
            // Skip sports entirely - filter them all out on frontend anyway
            
            // Fill rest with remaining finance, then others up to 30
            let financeIdx = 6, otherIdx = 0;
            while (balanced.length < 30) {
                const nextF = finance[financeIdx];
                const nextO = others[otherIdx];
                
                if (!nextF && !nextO) break;
                
                if (nextF && financeCount < 12) {
                    balanced.push(finance[financeIdx++]);
                    financeCount++;
                } else if (nextO) {
                    balanced.push(others[otherIdx++]);
                } else if (nextF) {
                    balanced.push(finance[financeIdx++]);
                } else {
                    break;
                }
            }
            
            const finalMarkets = pinnedMarket 
                ? [pinnedMarket, ...balanced.slice(0, 29)]
                : balanced.slice(0, 30);
            
            const result = { 
                markets: finalMarkets, 
                lastUpdated: new Date().toISOString(),
                filter: 'competitive (15-85% odds)',
                hasPinned: !!pinnedMarket
            };
            predictionsCache = { data: result, timestamp: Date.now() };
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(result));
        }).catch(err => {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
        });
        return;
    }
    
    // API endpoint for market data
    if (req.url === '/api/market') {
        const now = Date.now();
        if (marketCache.data && (now - marketCache.timestamp) < CACHE_TTL_60S) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(marketCache.data));
            return;
        }
        fetchMarketData().then(data => {
            marketCache = { data, timestamp: Date.now() };
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(data));
        }).catch(err => {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
        });
        return;
    }
    
    // API endpoint to request TikTok stats refresh
    // Creates a flag file that a cron job checks every 5 minutes
    if (req.url === '/api/tiktok-request-update') {
        const flagFile = path.join(ROOT, '.tiktok-refresh-requested');
        fs.writeFileSync(flagFile, new Date().toISOString());
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
            success: true, 
            message: 'Refresh requested! Stats will update within 5 minutes.',
            requestedAt: new Date().toISOString(),
            estimatedUpdate: new Date(Date.now() + 5 * 60 * 1000).toISOString()
        }));
        return;
    }
    
    // ==================== CHAT API ====================
    // POST /api/chat/send - Queue message for Jane
    if (req.url.startsWith('/api/chat/send') && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                const message = data.message || data.text;
                
                if (!message) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Message required' }));
                    return;
                }
                
                // Add to chat queue for Jane to process
                const queueFile = path.join(ROOT, 'chat-queue.json');
                const queue = fs.existsSync(queueFile) ? JSON.parse(fs.readFileSync(queueFile, 'utf8')) : [];
                queue.push({ 
                    message, 
                    timestamp: Date.now(), 
                    from: 'mobile-app',
                    id: Date.now().toString(36) + Math.random().toString(36).substr(2, 5)
                });
                fs.writeFileSync(queueFile, JSON.stringify(queue, null, 2));
                
                // Also add to chat history as user message
                const historyFile = path.join(ROOT, 'chat-history.json');
                const history = fs.existsSync(historyFile) ? JSON.parse(fs.readFileSync(historyFile, 'utf8')) : { messages: [] };
                history.messages.push({
                    role: 'user',
                    content: message,
                    timestamp: Date.now()
                });
                history.lastUpdated = new Date().toISOString();
                fs.writeFileSync(historyFile, JSON.stringify(history, null, 2));
                
                console.log(`💬 Chat message queued: "${message.substring(0, 50)}..."`);
                
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ 
                    success: true, 
                    message: 'Message sent! Jane will respond shortly.',
                    sent: message 
                }));
                
            } catch (e) {
                console.error('Chat send error:', e);
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Invalid request' }));
            }
        });
        return;
    }
    
    // GET /api/chat/history - Get chat history
    if (req.url === '/api/chat/history' || req.url.startsWith('/api/chat/history?')) {
        const historyFile = path.join(ROOT, 'chat-history.json');
        if (fs.existsSync(historyFile)) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(fs.readFileSync(historyFile));
        } else {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ messages: [], note: 'No chat history yet' }));
        }
        return;
    }
    
    // GET /api/chat/queue - Check pending messages (for Jane)
    if (req.url.startsWith('/api/chat/queue') && req.method === 'GET') {
        const queueFile = path.join(ROOT, 'chat-queue.json');
        if (fs.existsSync(queueFile)) {
            const queue = JSON.parse(fs.readFileSync(queueFile, 'utf8'));
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ messages: queue, count: queue.length }));
        } else {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ messages: [], count: 0 }));
        }
        return;
    }
    
    // DELETE /api/chat/queue - Clear message queue (after processing)
    if (req.url === '/api/chat/queue' && req.method === 'DELETE') {
        const queueFile = path.join(ROOT, 'chat-queue.json');
        if (fs.existsSync(queueFile)) fs.unlinkSync(queueFile);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, cleared: true }));
        return;
    }
    
    // API endpoint for market ticker (crypto, metals, indices)
    if (req.url === '/api/ticker') {
        const https = require('https');
        const now = Date.now();
        
        // Cache for 60 seconds
        if (tickerCache && tickerCache.data && (now - tickerCache.timestamp) < 60000) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(tickerCache.data));
            return;
        }
        
        const fetchJson = (url) => new Promise((resolve) => {
            https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' }, timeout: 8000 }, (r) => {
                let data = '';
                r.on('data', c => data += c);
                r.on('end', () => {
                    try { resolve(JSON.parse(data)); } 
                    catch { resolve(null); }
                });
            }).on('error', () => resolve(null)).on('timeout', function() { this.destroy(); resolve(null); });
        });
        
        // Fetch crypto from CoinGecko
        const cryptoUrl = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true';
        
        // Fetch IBIT (BlackRock Bitcoin ETF) from Yahoo Finance
        const ibitUrl = 'https://query1.finance.yahoo.com/v8/finance/chart/IBIT?interval=1d&range=2d';
        
        // Fetch NDAQ (Nasdaq Inc. stock) from Yahoo Finance
        const nasdaqUrl = 'https://query1.finance.yahoo.com/v8/finance/chart/NDAQ?interval=1d&range=2d';
        
        Promise.all([
            fetchJson(cryptoUrl),
            fetchJson(ibitUrl),
            fetchJson(nasdaqUrl)
        ]).then(([crypto, ibitData, nasdaqData]) => {
            const ticker = {};
            
            // Crypto
            if (crypto) {
                if (crypto.bitcoin) ticker.btc = { price: crypto.bitcoin.usd, change24h: crypto.bitcoin.usd_24h_change };
                if (crypto.ethereum) ticker.eth = { price: crypto.ethereum.usd, change24h: crypto.ethereum.usd_24h_change };
                if (crypto.solana) ticker.sol = { price: crypto.solana.usd, change24h: crypto.solana.usd_24h_change };
            }
            
            // NASDAQ Composite from Yahoo Finance
            if (nasdaqData && nasdaqData.chart && nasdaqData.chart.result && nasdaqData.chart.result[0]) {
                const result = nasdaqData.chart.result[0];
                const meta = result.meta;
                const price = meta.regularMarketPrice;
                const prevClose = meta.chartPreviousClose || meta.previousClose;
                const change = prevClose ? ((price - prevClose) / prevClose) * 100 : null;
                ticker.nasdaq = { price: price, change24h: change };
            } else {
                ticker.nasdaq = { price: null, change24h: null };
            }
            
            // IBIT (BlackRock Bitcoin ETF) from Yahoo Finance
            if (ibitData && ibitData.chart && ibitData.chart.result && ibitData.chart.result[0]) {
                const result = ibitData.chart.result[0];
                const meta = result.meta;
                const price = meta.regularMarketPrice;
                const prevClose = meta.chartPreviousClose || meta.previousClose;
                const change = prevClose ? ((price - prevClose) / prevClose) * 100 : null;
                ticker.ibit = { price: price, change24h: change };
            } else {
                // Fallback
                ticker.ibit = { price: 52.50, change24h: null };
            }
            
            tickerCache = { data: ticker, timestamp: now };
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(ticker));
        }).catch(() => {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Failed to fetch ticker data' }));
        });
        
        return;
    }
    
    // API endpoint for crypto prices (proxy to avoid CORS)
    // Uses CoinGecko with CoinCap fallback, plus caching to avoid rate limits
    if (req.url === '/api/crypto') {
        const https = require('https');
        
        // Check cache first (valid for 30 seconds)
        const now = Date.now();
        if (cryptoCache.data && (now - cryptoCache.timestamp) < 30000) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(cryptoCache.data));
            return;
        }
        
        const coingeckoUrl = 'https://api.coingecko.com/api/v3/simple/price?ids=solana,bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true';
        
        // Try CoinGecko first
        https.get(coingeckoUrl, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (proxyRes) => {
            let data = '';
            proxyRes.on('data', chunk => data += chunk);
            proxyRes.on('end', () => {
                try {
                    const parsed = JSON.parse(data);
                    // Check if it's a rate limit error
                    if (parsed.status?.error_code === 429 || !parsed.solana) {
                        throw new Error('Rate limited or invalid response');
                    }
                    // Cache the result
                    cryptoCache = { data: parsed, timestamp: now };
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(data);
                } catch (e) {
                    // Fallback to CoinCap
                    fetchCoinCap(res, now);
                }
            });
        }).on('error', () => {
            // Fallback to CoinCap
            fetchCoinCap(res, now);
        });
        return;
    }

    // ===== X/Twitter Growth Endpoints =====
    if (req.url === '/api/x-stats' && req.method === 'GET') {
        const statsFile = path.join(ROOT, 'x-stats.json');
        if (fs.existsSync(statsFile)) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(fs.readFileSync(statsFile));
        } else {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ followers: 0, following: 0, tweets: 0, impressions: 0 }));
        }
        return;
    }
    
    if (req.url === '/api/x-refresh' && req.method === 'POST') {
        // Write flag file that heartbeat/agent picks up for immediate scrape
        fs.writeFileSync(path.join(ROOT, '.x-refresh-requested'), new Date().toISOString());
        res.writeHead(200, {'Content-Type':'application/json'});
        res.end('{"ok":true,"message":"X stats refresh requested"}');
        return;
    }

    if (req.url === '/api/desktop-night-mode' && req.method === 'POST') {
        let body = '';
        req.on('data', c => body += c);
        req.on('end', () => {
            try {
                const { enabled } = JSON.parse(body);
                // Write night mode state so desktop can pick it up
                const nmFile = path.join(ROOT, '.night-mode');
                if (enabled) {
                    fs.writeFileSync(nmFile, '1');
                } else {
                    if (fs.existsSync(nmFile)) fs.unlinkSync(nmFile);
                }
                // Broadcast to desktop via WebSocket
                if (typeof wss !== 'undefined') {
                    wss.clients.forEach(c => {
                        if (c.readyState === 1) c.send(JSON.stringify({type:'nightMode', enabled}));
                    });
                }
                res.writeHead(200, {'Content-Type':'application/json'});
                res.end(JSON.stringify({ok:true, enabled}));
            } catch(e) {
                res.writeHead(400, {'Content-Type':'application/json'});
                res.end(JSON.stringify({ok:false, error: e.message}));
            }
        });
        return;
    }

    if (req.url === '/api/refresh-desktop' && req.method === 'POST') {
        // Force-refresh the desktop Chrome browser via AppleScript
        const { exec: execCmd } = require('child_process');
        execCmd("osascript -e 'tell application \"Google Chrome\" to reload active tab of first window'", (err) => {
            res.writeHead(200, {'Content-Type':'application/json'});
            if (err) {
                res.end(JSON.stringify({ok:false, error: err.message}));
            } else {
                res.end('{"ok":true,"message":"Desktop browser refreshed"}');
            }
        });
        return;
    }

    if (req.url === '/api/x-plan' && req.method === 'GET') {
        const planFile = path.join(ROOT, 'x-plan.json');
        if (fs.existsSync(planFile)) {
            try {
                const plan = JSON.parse(fs.readFileSync(planFile, 'utf8'));
                const today = new Date().toISOString().split('T')[0];
                // Auto-reset if plan is from a previous day
                if (plan.date && plan.date !== today) {
                    const fresh = { date: today, tasks: [] };
                    fs.writeFileSync(planFile, JSON.stringify(fresh, null, 2));
                    res.writeHead(200, {'Content-Type':'application/json'});
                    res.end(JSON.stringify(fresh));
                } else {
                    res.writeHead(200, {'Content-Type':'application/json'});
                    res.end(JSON.stringify(plan));
                }
            } catch(e) { res.writeHead(200, {'Content-Type':'application/json'}); res.end(fs.readFileSync(planFile)); }
        } else { res.writeHead(404); res.end('{}'); }
        return;
    }

    if (req.url === '/api/x-queue' && req.method === 'GET') {
        const queueFile = path.join(ROOT, 'x-queue.json');
        if (fs.existsSync(queueFile)) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(fs.readFileSync(queueFile));
        } else {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ pending: [], recent: [] }));
        }
        return;
    }
    
    const xApproveMatch = req.url.match(/^\/api\/x-queue\/approve\/(.+)$/);
    if (xApproveMatch && req.method === 'POST') {
        const id = xApproveMatch[1];
        const queueFile = path.join(ROOT, 'x-queue.json');
        try {
            const data = fs.existsSync(queueFile) ? JSON.parse(fs.readFileSync(queueFile, 'utf8')) : { pending: [], recent: [] };
            const idx = data.pending.findIndex(item => item.id === id);
            if (idx === -1) {
                res.writeHead(404, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Item not found' }));
                return;
            }
            const item = data.pending.splice(idx, 1)[0];
            item.status = 'approved';
            item.approvedAt = new Date().toISOString();
            data.recent.unshift(item);
            if (data.recent.length > 10) data.recent = data.recent.slice(0, 10);
            fs.writeFileSync(queueFile, JSON.stringify(data, null, 2));
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(data));
        } catch (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
        }
        return;
    }
    
    // POST /api/x-queue/add - Add draft tweet/reply to queue
    if (req.url === '/api/x-queue/add' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const item = JSON.parse(body);
                const queueFile = path.join(ROOT, 'x-queue.json');
                const data = fs.existsSync(queueFile) ? JSON.parse(fs.readFileSync(queueFile, 'utf8')) : { pending: [], recent: [] };
                const newItem = {
                    id: item.id || ('draft-' + Date.now().toString(36)),
                    type: item.type || 'tweet',
                    text: item.text || item.content || item.draft || '',
                    target: item.target || null,
                    theme: item.theme || null,
                    status: 'pending',
                    createdAt: new Date().toISOString()
                };
                if (item.scheduledFor) newItem.scheduledFor = item.scheduledFor;
                data.pending.push(newItem);
                fs.writeFileSync(queueFile, JSON.stringify(data, null, 2));
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, item: newItem, queue: data }));
            } catch (err) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: err.message }));
            }
        });
        return;
    }
    
    // POST /api/x-queue/schedule - Set scheduled post time for a queued item
    if (req.url === '/api/x-queue/schedule' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const { id, scheduledFor } = JSON.parse(body);
                const queueFile = path.join(ROOT, 'x-queue.json');
                const data = fs.existsSync(queueFile) ? JSON.parse(fs.readFileSync(queueFile, 'utf8')) : { pending: [], recent: [] };
                const item = data.pending.find(i => i.id === id);
                if (!item) {
                    res.writeHead(404, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Item not found in pending queue' }));
                    return;
                }
                item.scheduledFor = scheduledFor;
                item.status = 'scheduled';
                fs.writeFileSync(queueFile, JSON.stringify(data, null, 2));
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, item, queue: data }));
            } catch (err) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: err.message }));
            }
        });
        return;
    }
    
    const xRejectMatch = req.url.match(/^\/api\/x-queue\/reject\/(.+)$/);
    if (xRejectMatch && req.method === 'POST') {
        const id = xRejectMatch[1];
        const queueFile = path.join(ROOT, 'x-queue.json');
        try {
            const data = fs.existsSync(queueFile) ? JSON.parse(fs.readFileSync(queueFile, 'utf8')) : { pending: [], recent: [] };
            const idx = data.pending.findIndex(item => item.id === id);
            if (idx === -1) {
                res.writeHead(404, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Item not found' }));
                return;
            }
            data.pending.splice(idx, 1);
            fs.writeFileSync(queueFile, JSON.stringify(data, null, 2));
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(data));
        } catch (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
        }
        return;
    }
    
    // POST /api/x-plan/approve/:id - Approve a content idea
    const xPlanApproveMatch = req.url.match(/^\/api\/x-plan\/approve\/(.+)$/);
    if (xPlanApproveMatch && req.method === 'POST') {
        const id = decodeURIComponent(xPlanApproveMatch[1]);
        const planFile = path.join(ROOT, 'x-plan.json');
        try {
            const data = fs.existsSync(planFile) ? JSON.parse(fs.readFileSync(planFile, 'utf8')) : {};
            const idx = (data.contentIdeas || []).findIndex(i => i.id === id);
            if (idx === -1) {
                res.writeHead(404, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Content idea not found' }));
                return;
            }
            data.contentIdeas[idx].status = 'approved';
            fs.writeFileSync(planFile, JSON.stringify(data, null, 2));
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true, idea: data.contentIdeas[idx] }));
        } catch (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
        }
        return;
    }

    // POST /api/x-plan/reject/:id - Reject a content idea
    const xPlanRejectMatch = req.url.match(/^\/api\/x-plan\/reject\/(.+)$/);
    if (xPlanRejectMatch && req.method === 'POST') {
        const id = decodeURIComponent(xPlanRejectMatch[1]);
        const planFile = path.join(ROOT, 'x-plan.json');
        try {
            const data = fs.existsSync(planFile) ? JSON.parse(fs.readFileSync(planFile, 'utf8')) : {};
            const idx = (data.contentIdeas || []).findIndex(i => i.id === id);
            if (idx === -1) {
                res.writeHead(404, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Content idea not found' }));
                return;
            }
            data.contentIdeas[idx].status = 'rejected';
            fs.writeFileSync(planFile, JSON.stringify(data, null, 2));
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true, idea: data.contentIdeas[idx] }));
        } catch (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
        }
        return;
    }

    // API endpoint to request briefing refresh
    if (req.url === '/api/briefing/refresh' && req.method === 'POST') {
        const flagFile = path.join(ROOT, '.briefing-refresh-requested');
        fs.writeFileSync(flagFile, new Date().toISOString());
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: true, message: 'Briefing refresh requested' }));
        return;
    }
    // API endpoint for daily briefing
    // Push Notification API
    if (req.url === '/api/push/vapid-key' && req.method === 'GET') {
        const vapidPath = path.join(WORKSPACE, '.secrets', 'vapid-keys.json');
        try {
            const keys = JSON.parse(fs.readFileSync(vapidPath, 'utf8'));
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ publicKey: keys.publicKey }));
        } catch (e) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'VAPID keys not configured' }));
        }
        return;
    }

    if (req.url === '/api/push/subscribe' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const subscription = JSON.parse(body);
                const subsFile = path.join(ROOT, 'push-subscriptions.json');
                let subs = [];
                if (fs.existsSync(subsFile)) {
                    subs = JSON.parse(fs.readFileSync(subsFile, 'utf8'));
                }
                // Deduplicate by endpoint
                subs = subs.filter(s => s.endpoint !== subscription.endpoint);
                subs.push(subscription);
                fs.writeFileSync(subsFile, JSON.stringify(subs, null, 2));
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ ok: true, total: subs.length }));
            } catch (e) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    if (req.url === '/api/push/send' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                const { title, body: msgBody, tag, url: notifUrl } = JSON.parse(body);
                const vapidPath = path.join(WORKSPACE, '.secrets', 'vapid-keys.json');
                const keys = JSON.parse(fs.readFileSync(vapidPath, 'utf8'));
                const subsFile = path.join(ROOT, 'push-subscriptions.json');
                if (!fs.existsSync(subsFile)) {
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ ok: true, sent: 0, message: 'No subscribers' }));
                    return;
                }
                const webpush = require('web-push');
                webpush.setVapidDetails('mailto:jcubellagent@gmail.com', keys.publicKey, keys.privateKey);
                const subs = JSON.parse(fs.readFileSync(subsFile, 'utf8'));
                const payload = JSON.stringify({ title: title || 'Jane', body: msgBody || '', tag: tag || 'jane', data: { url: notifUrl || '/mobile.html' } });
                let sent = 0, failed = 0;
                const validSubs = [];
                for (const sub of subs) {
                    try {
                        await webpush.sendNotification(sub, payload);
                        validSubs.push(sub);
                        sent++;
                    } catch (e) {
                        if (e.statusCode === 410 || e.statusCode === 404) {
                            failed++; // Subscription expired, remove it
                        } else {
                            validSubs.push(sub);
                            failed++;
                        }
                    }
                }
                // Clean up expired subscriptions
                fs.writeFileSync(subsFile, JSON.stringify(validSubs, null, 2));
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ ok: true, sent, failed }));
            } catch (e) {
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    if (req.url === '/api/push/test' && req.method === 'POST') {
        (async () => {
            try {
                const vapidPath = path.join(WORKSPACE, '.secrets', 'vapid-keys.json');
                const keys = JSON.parse(fs.readFileSync(vapidPath, 'utf8'));
                const subsFile = path.join(ROOT, 'push-subscriptions.json');
                if (!fs.existsSync(subsFile)) {
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ ok: true, sent: 0, message: 'No subscribers' }));
                    return;
                }
                const webpush = require('web-push');
                webpush.setVapidDetails('mailto:jcubellagent@gmail.com', keys.publicKey, keys.privateKey);
                const subs = JSON.parse(fs.readFileSync(subsFile, 'utf8'));
                const payload = JSON.stringify({ title: '\ud83e\uddea Test from Jane', body: 'Push notifications are working!', tag: 'test' });
                let sent = 0;
                for (const sub of subs) {
                    try { await webpush.sendNotification(sub, payload); sent++; } catch(e) {}
                }
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ ok: true, sent }));
            } catch(e) {
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: e.message }));
            }
        })();
        return;
    }

    if (req.url === '/api/briefing') {
        const briefingFile = path.join(ROOT, 'briefing.json');
        if (fs.existsSync(briefingFile)) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(fs.readFileSync(briefingFile));
        } else {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'No briefing available yet' }));
        }
        return;
    }
    
    // Parse URL and strip query string
    const urlPath = new URL(req.url, `http://${req.headers.host}`).pathname;
    
    // ===== arXiv RSS (cs.AI + cs.CL) — cached 30 min =====
    if (req.url === '/api/arxiv') {
        const now = Date.now();
        if (arxivCache.data && (now - arxivCache.timestamp) < CACHE_TTL_30MIN) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(arxivCache.data));
            return;
        }
        const fetchFeed = (url) => new Promise((resolve) => {
            https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' }, timeout: 10000 }, (r) => {
                let d = '';
                r.on('data', c => d += c);
                r.on('end', () => resolve(d));
            }).on('error', () => resolve('')).on('timeout', function() { this.destroy(); resolve(''); });
        });
        Promise.all([
            fetchFeed('https://export.arxiv.org/rss/cs.AI'),
            fetchFeed('https://export.arxiv.org/rss/cs.CL')
        ]).then(([aiXml, clXml]) => {
            const parse = (xml, category) => {
                const items = [];
                const re = /<item[^>]*>([\s\S]*?)<\/item>/gi;
                let m;
                while ((m = re.exec(xml)) !== null && items.length < 15) {
                    const block = m[1];
                    const title = (block.match(/<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?<\/title>/s) || [])[1] || '';
                    const desc = (block.match(/<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?<\/description>/s) || [])[1] || '';
                    const link = (block.match(/<link>(.*?)<\/link>/) || [])[1] || '';
                    if (title) items.push({
                        title: title.replace(/<[^>]*>/g, '').trim().substring(0, 120),
                        description: desc.replace(/<[^>]*>/g, '').trim().substring(0, 300),
                        link, category
                    });
                }
                return items;
            };
            const result = {
                papers: [...parse(aiXml, 'cs.AI'), ...parse(clXml, 'cs.CL')],
                lastUpdated: new Date().toISOString()
            };
            arxivCache = { data: result, timestamp: Date.now() };
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(result));
        });
        return;
    }

    // ===== SEC EDGAR 8-K filings — cached 5 min =====
    if (req.url === '/api/sec-edgar') {
        const now = Date.now();
        if (secEdgarCache.data && (now - secEdgarCache.timestamp) < CACHE_TTL_5MIN) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(secEdgarCache.data));
            return;
        }
        const today = new Date().toISOString().split('T')[0];
        const edgarUrl = `https://efts.sec.gov/LATEST/search-index?q=*&dateRange=custom&startdt=${today}&enddt=${today}&forms=8-K`;
        https.get(edgarUrl, { headers: { 'User-Agent': 'Jane-Dashboard/1.0 jcubellagent@gmail.com', 'Accept': 'application/json' }, timeout: 10000 }, (apiRes) => {
            let body = '';
            apiRes.on('data', c => body += c);
            apiRes.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    const hits = (data.hits && data.hits.hits) || [];
                    const total = (data.hits && data.hits.total && data.hits.total.value) || 0;
                    const result = { filings: hits.slice(0, 20), total, lastUpdated: new Date().toISOString() };
                    secEdgarCache = { data: result, timestamp: Date.now() };
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify(result));
                } catch (e) {
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ filings: [], error: e.message, lastUpdated: new Date().toISOString() }));
                }
            });
        }).on('error', (e) => {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ filings: [], error: e.message }));
        });
        return;
    }

    // ===== DeFi Llama protocols TVL — cached 5 min =====
    if (req.url === '/api/defi-llama') {
        const now = Date.now();
        if (defiLlamaCache.data && (now - defiLlamaCache.timestamp) < CACHE_TTL_5MIN) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(defiLlamaCache.data));
            return;
        }
        https.get('https://api.llama.fi/protocols', { headers: { 'User-Agent': 'Mozilla/5.0' }, timeout: 10000 }, (apiRes) => {
            let body = '';
            apiRes.on('data', c => body += c);
            apiRes.on('end', () => {
                try {
                    const protocols = JSON.parse(body);
                    const top20 = protocols.slice(0, 20).map(p => ({
                        name: p.name, symbol: p.symbol, tvl: p.tvl,
                        change_1d: p.change_1d, change_7d: p.change_7d,
                        category: p.category, chain: p.chain, logo: p.logo
                    }));
                    const totalTvl = protocols.reduce((s, p) => s + (p.tvl || 0), 0);
                    const result = { protocols: top20, totalTvl, totalProtocols: protocols.length, lastUpdated: new Date().toISOString() };
                    defiLlamaCache = { data: result, timestamp: Date.now() };
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify(result));
                } catch (e) {
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ protocols: [], error: e.message }));
                }
            });
        }).on('error', (e) => {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ protocols: [], error: e.message }));
        });
        return;
    }

    // ===== TechCrunch RSS — cached 30 min =====
    if (req.url === '/api/techcrunch') {
        const now = Date.now();
        if (techCrunchCache.data && (now - techCrunchCache.timestamp) < CACHE_TTL_30MIN) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(techCrunchCache.data));
            return;
        }
        https.get('https://techcrunch.com/feed/', { headers: { 'User-Agent': 'Mozilla/5.0' }, timeout: 10000 }, (apiRes) => {
            let body = '';
            apiRes.on('data', c => body += c);
            apiRes.on('end', () => {
                const items = [];
                const re = /<item>([\s\S]*?)<\/item>/gi;
                let m;
                while ((m = re.exec(body)) !== null && items.length < 15) {
                    const block = m[1];
                    const title = (block.match(/<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?<\/title>/s) || [])[1] || '';
                    const link = (block.match(/<link>(.*?)<\/link>/) || [])[1] || '';
                    const pubDate = (block.match(/<pubDate>(.*?)<\/pubDate>/) || [])[1] || '';
                    const desc = (block.match(/<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?<\/description>/s) || [])[1] || '';
                    if (title) items.push({
                        title: title.replace(/<[^>]*>/g, '').trim().substring(0, 120),
                        link, pubDate,
                        description: desc.replace(/<[^>]*>/g, '').trim().substring(0, 200)
                    });
                }
                const result = { articles: items, lastUpdated: new Date().toISOString() };
                techCrunchCache = { data: result, timestamp: Date.now() };
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(result));
            });
        }).on('error', (e) => {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ articles: [], error: e.message }));
        });
        return;
    }

    // Serve x-headers images from tiktok/x-headers directory
    if (req.url.startsWith('/x-headers/')) {
        const imageName = req.url.replace('/x-headers/', '');
        const xHeadersPath = path.join(WORKSPACE, 'tiktok', 'x-headers', imageName);
        if (fs.existsSync(xHeadersPath)) {
            const ext = path.extname(xHeadersPath).toLowerCase();
            const contentType = MIME_TYPES[ext] || 'image/png';
            fs.readFile(xHeadersPath, (err, content) => {
                if (err) {
                    res.writeHead(500);
                    res.end('Error reading image');
                    return;
                }
                res.writeHead(200, { 'Content-Type': contentType });
                res.end(content);
            });
        } else {
            res.writeHead(404);
            res.end('Image not found');
        }
        return;
    }

    // Auto-detect mobile devices and serve mobile.html
    const userAgent = req.headers['user-agent'] || '';
    const isMobile = /iPhone|iPad|iPod|Android|webOS|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
    
    let filePath;
    if (urlPath === '/' && isMobile) {
        filePath = path.join(ROOT, 'mobile.html');
    } else {
        filePath = path.join(ROOT, urlPath === '/' ? 'index.html' : urlPath);
    }
    
    // Security: prevent directory traversal
    if (!filePath.startsWith(ROOT)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }

    // Handle directory requests
    if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
        filePath = path.join(filePath, 'index.html');
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    fs.readFile(filePath, (err, content) => {
        if (err) {
            if (err.code === 'ENOENT') {
                res.writeHead(404);
                res.end('Not Found');
            } else {
                res.writeHead(500);
                res.end('Server Error');
            }
            return;
        }

        // Add no-cache headers for HTML to prevent stale content
        const headers = { 'Content-Type': contentType };
        if (ext === '.html') {
            headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
            headers['Pragma'] = 'no-cache';
            headers['Expires'] = '0';
        }
        res.writeHead(200, headers);
        res.end(content);
    });
}

const server = http.createServer(handleRequest);

// HTTPS server for push notifications (service workers require HTTPS)
const HTTPS_PORT = 3443;
let httpsServer;
try {
    const tlsDir = path.join(WORKSPACE, '.secrets', 'tls');
    const tlsKey = path.join(tlsDir, 'selfsigned.key');
    const tlsCert = path.join(tlsDir, 'selfsigned.crt');
    if (fs.existsSync(tlsKey) && fs.existsSync(tlsCert)) {
        httpsServer = https.createServer({
            key: fs.readFileSync(tlsKey),
            cert: fs.readFileSync(tlsCert)
        }, handleRequest);
    }
} catch (e) {
    console.warn('HTTPS setup skipped:', e.message);
}

// ============================================
// WebSocket Server for Real-Time Push Updates
// ============================================
const WebSocket = require('ws');
const wss = new WebSocket.Server({ server });
// Also attach WebSocket to HTTPS server if available
let wssSecure;
if (httpsServer) {
    wssSecure = new WebSocket.Server({ server: httpsServer });
    wssSecure.on('connection', (ws) => {
        clients.add(ws);
        ws.send(JSON.stringify({ type: 'connected', timestamp: Date.now() }));
        ws.on('close', () => clients.delete(ws));
        ws.on('error', () => clients.delete(ws));
    });
}

// Track connected clients
let clients = new Set();

wss.on('connection', (ws) => {
    clients.add(ws);
    console.log(`📡 WebSocket client connected (${clients.size} total)`);
    
    // Send initial connection confirmation
    ws.send(JSON.stringify({ type: 'connected', timestamp: Date.now() }));
    
    ws.on('close', () => {
        clients.delete(ws);
        console.log(`📡 WebSocket client disconnected (${clients.size} total)`);
    });
    
    ws.on('error', (err) => {
        console.error('WebSocket error:', err.message);
        clients.delete(ws);
    });
});

// Broadcast to all connected clients
function broadcast(data) {
    const message = JSON.stringify(data);
    clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
}

// File watchers for real-time updates
const WATCHED_FILES = {
    'tasks': path.join(WORKSPACE, 'tasks.json'),
    'sessions': path.join(ROOT, 'sessions.json'),
    'tiktok': path.join(ROOT, 'tiktok-stats.json'),
    'trading': path.join(ROOT, 'trading-positions.json'),
    'sorare': path.join(ROOT, 'sorare-stats.json'),
    'sorare-mobile': path.join(ROOT, 'sorare-mobile.json'),
    'panini': path.join(ROOT, 'panini-collection.json'),
    'mind': path.join(ROOT, 'mind-state.json'),
    'x-queue': path.join(ROOT, 'x-queue.json'),
    'x-stats': path.join(ROOT, 'x-stats.json'),
    'x-plan': path.join(ROOT, 'x-plan.json'),
    'briefing': path.join(ROOT, 'briefing.json'),
    'x-tweets': path.join(ROOT, 'x-latest-tweets.json'),
    'x-thread-history': path.join(ROOT, 'x-thread-history.json'),
    'cron-schedule': path.join(ROOT, 'cron-schedule.json')
};

// Batched WebSocket updates — collect rapid file changes and send as one broadcast
const pendingUpdates = {};
let batchTimer = null;
const BATCH_DELAY = 300; // ms to wait before flushing batch

function flushBatch() {
    batchTimer = null;
    const keys = Object.keys(pendingUpdates);
    if (keys.length === 0) return;
    
    if (keys.length === 1) {
        // Single update — send as before for backwards compat
        const key = keys[0];
        console.log(`📤 Broadcasting ${key} update to ${clients.size} clients`);
        broadcast({ type: 'update', widget: key, data: pendingUpdates[key], timestamp: Date.now() });
    } else {
        // Batch multiple updates into one message
        console.log(`📤 Broadcasting batch update (${keys.join(', ')}) to ${clients.size} clients`);
        broadcast({ type: 'batch', updates: Object.entries(pendingUpdates).map(([widget, data]) => ({ widget, data })), timestamp: Date.now() });
    }
    
    // Clear
    for (const k of keys) delete pendingUpdates[k];
}

function queueUpdate(key, data) {
    pendingUpdates[key] = data;
    if (!batchTimer) {
        batchTimer = setTimeout(flushBatch, BATCH_DELAY);
    }
}

// Debounce file change events
const fileChangeTimers = {};
function debounceFileChange(key, callback, delay = 500) {
    if (fileChangeTimers[key]) clearTimeout(fileChangeTimers[key]);
    fileChangeTimers[key] = setTimeout(callback, delay);
}

// Set up file watchers
Object.entries(WATCHED_FILES).forEach(([key, filePath]) => {
    if (fs.existsSync(filePath)) {
        fs.watch(filePath, (eventType) => {
            if (eventType === 'change') {
                const debounceMs = key === 'mind' ? 50 : 500;
                debounceFileChange(key, () => {
                    try {
                        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                        queueUpdate(key, data);
                    } catch (err) {
                        console.error(`Failed to read ${key}:`, err.message);
                    }
                }, debounceMs);
            }
        });
        console.log(`👁️  Watching: ${key}`);
    }
});

// Also watch workspace tasks.json directory (in case file is created later)
const tasksDir = WORKSPACE;
fs.watch(tasksDir, (eventType, filename) => {
    if (filename === 'tasks.json' && eventType === 'change') {
        debounceFileChange('tasks', () => {
            try {
                const data = JSON.parse(fs.readFileSync(WATCHED_FILES.tasks, 'utf8'));
                queueUpdate('tasks', data);
            } catch (err) {
                // File might not exist yet
            }
        });
    }
});

// === Instant Mind Activation on Incoming Message ===
// Watch the main session transcript — when a new user message arrives,
// immediately flip mind-state to "Active" so the widget lights up before Jane starts processing.
(function setupTranscriptWatcher() {
    const sessionsDir = path.join(os.homedir(), '.openclaw', 'agents', 'main', 'sessions');
    const mindFile = path.join(ROOT, 'mind-state.json');
    let lastSize = 0;
    let mainTranscript = null;
    let idleProtectedUntil = 0; // Debounce: protect idle state for 2s after setting

    // Find the main session transcript (NOT sub-agents or crons)
    function findMainTranscript() {
        try {
            // Try to find the main session via the sessions index
            const indexFile = path.join(sessionsDir, '..', 'sessions.json');
            if (fs.existsSync(indexFile)) {
                const idx = JSON.parse(fs.readFileSync(indexFile, 'utf8'));
                // Look for the main session entry
                for (const [key, val] of Object.entries(idx)) {
                    if (key === 'agent:main:main' || (val && val.key === 'agent:main:main')) {
                        const sid = val?.sessionId || val?.id;
                        if (sid) {
                            const fp = path.join(sessionsDir, sid + '.jsonl');
                            if (fs.existsSync(fp)) return fp;
                        }
                        const tp = val?.transcriptPath;
                        if (tp) {
                            const fp = path.join(sessionsDir, tp);
                            if (fs.existsSync(fp)) return fp;
                        }
                    }
                }
            }
            // Fallback: pick the largest .jsonl (main session is usually the biggest)
            const files = fs.readdirSync(sessionsDir).filter(f => f.endsWith('.jsonl') && !f.endsWith('.lock'));
            if (files.length === 0) return null;
            let biggest = null, biggestSize = 0;
            for (const f of files) {
                const fp = path.join(sessionsDir, f);
                const stat = fs.statSync(fp);
                if (stat.size > biggestSize) { biggestSize = stat.size; biggest = fp; }
            }
            return biggest;
        } catch { return null; }
    }

    function checkForNewMessage() {
        if (!mainTranscript) mainTranscript = findMainTranscript();
        if (!mainTranscript) return;
        try {
            const stat = fs.statSync(mainTranscript);
            if (lastSize === 0) { lastSize = stat.size; return; }
            if (stat.size > lastSize) {
                // Read only the new bytes
                const fd = fs.openSync(mainTranscript, 'r');
                const buf = Buffer.alloc(stat.size - lastSize);
                fs.readSync(fd, buf, 0, buf.length, lastSize);
                fs.closeSync(fd);
                lastSize = stat.size;
                const newContent = buf.toString('utf8');
                // Parse new JSONL entries and update mind widget
                const newLines = newContent.split('\n').filter(Boolean);
                for (const line of newLines) {
                    try {
                        const entry = JSON.parse(line);
                        const msg = entry.message || entry;
                        const role = msg.role;
                        const current = JSON.parse(fs.readFileSync(mindFile, 'utf8'));

                        // Skip updates during idle protection window (prevents overwriting idle with stale tool calls)
                        if (Date.now() < idleProtectedUntil && role !== 'user') continue;

                        if (role === 'user') {
                            // Check if this is a system/heartbeat message (not a real user message)
                            const content = Array.isArray(msg.content) ? msg.content : (typeof msg.content === 'string' ? [{ type: 'text', text: msg.content }] : []);
                            const textContent = content.map(c => c.text || '').join('').trim();
                            const isSystem = textContent.startsWith('Read HEARTBEAT') || 
                                            textContent.includes('MIND WIDGET CHECK') ||
                                            textContent.includes('Exec completed') ||
                                            textContent.startsWith('System:') ||
                                            textContent.startsWith('[2') && textContent.includes('EST]');
                            if (isSystem) {
                                // System message — just update timestamp, don't activate
                                current.lastUpdated = Date.now();
                                fs.writeFileSync(mindFile, JSON.stringify(current, null, 2));
                                continue;
                            }
                            // Real user message — activate mind
                            idleProtectedUntil = 0;
                            current.task = 'Processing incoming message...';
                            current.steps = [{ label: 'Receiving and analyzing message', status: 'active', tool: 'opus' }];
                            current.thought = 'New message received — processing...';
                            current.lastUpdated = Date.now();
                            fs.writeFileSync(mindFile, JSON.stringify(current, null, 2));
                            console.log('⚡ Mind activated: user message');
                        } else if (role === 'assistant' && msg.content) {
                            // Assistant response — detect tool calls and text
                            const content = Array.isArray(msg.content) ? msg.content : [msg.content];
                            const toolCalls = content.filter(c => c.type === 'toolCall' || c.type === 'tool_use');
                            const textParts = content.filter(c => c.type === 'text' && c.text && !c.text.startsWith('NO_REPLY') && !c.text.startsWith('HEARTBEAT'));

                            // Extract assistant's own narration as thought context
                            const narration = textParts.length > 0 ? textParts[0].text.split('\n')[0].substring(0, 200) : null;

                            if (toolCalls.length > 0) {
                                // Map tool names to human-readable labels
                                const toolLabels = {
                                    'exec': 'Running shell command', 'read': 'Reading file', 'write': 'Writing file',
                                    'edit': 'Editing file', 'web_search': 'Searching the web', 'web_fetch': 'Fetching webpage',
                                    'browser': 'Browser automation', 'message': 'Sending message', 'cron': 'Managing cron jobs',
                                    'sessions_spawn': 'Spawning sub-agent', 'memory_search': 'Searching memory',
                                    'image': 'Analyzing image', 'tts': 'Generating speech', 'gateway': 'Gateway config',
                                    'session_status': 'Checking session status', 'sessions_list': 'Listing sessions',
                                    'process': 'Managing background process', 'memory_get': 'Reading memory'
                                };
                                const toolModels = {
                                    'exec': 'opus', 'read': 'opus', 'write': 'opus', 'edit': 'opus',
                                    'web_search': 'opus', 'web_fetch': 'opus', 'browser': 'opus',
                                    'sessions_spawn': 'sonnet', 'memory_search': 'ollama', 'memory_get': 'ollama'
                                };
                                const steps = toolCalls.map(tc => {
                                    const name = (tc.name || 'unknown').toLowerCase();
                                    const args = tc.arguments || {};
                                    // Smart labeling: detect specific tools from arguments
                                    let label = toolLabels[name] || `Using ${name}`;
                                    let tool = toolModels[name] || 'opus';
                                    if (name === 'exec' && typeof args.command === 'string') {
                                        const cmd = args.command;
                                        if (cmd.includes('whisper')) { label = 'Transcribing audio via Whisper'; tool = 'whisper'; }
                                        else if (cmd.includes('ollama')) { label = 'Running Ollama model'; tool = 'ollama'; }
                                        else if (cmd.includes('txt2image') || cmd.includes('stable_diffusion') || cmd.includes('mflux')) { label = 'Generating image'; tool = 'sd'; }
                                        else if (cmd.includes('ssh mini2')) { label = 'Running command on Mini #2'; tool = 'opus'; }
                                        else if (cmd.includes('curl') && cmd.includes('sorare')) { label = 'Querying Sorare API'; tool = 'opus'; }
                                        else if (cmd.includes('curl') && cmd.includes('nba')) { label = 'Checking NBA scores'; tool = 'opus'; }
                                        else if (cmd.includes('fetch-sorare')) { label = 'Refreshing Sorare data'; tool = 'opus'; }
                                        else if (cmd.includes('launchctl')) { label = 'Restarting service'; tool = 'opus'; }
                                        else if (cmd.includes('grep') || cmd.includes('cat') || cmd.includes('head') || cmd.includes('tail')) { label = 'Inspecting files'; tool = 'opus'; }
                                        else if (cmd.includes('python3')) { label = 'Running Python script'; tool = 'opus'; }
                                    }
                                    if (name === 'edit') {
                                        const fp = args.path || args.file_path || '';
                                        if (fp.includes('mind-state')) { return null; }
                                        else if (fp.includes('index.html')) { label = 'Editing dashboard UI'; }
                                        else if (fp.includes('server.js')) { label = 'Editing dashboard server'; }
                                        else if (fp.includes('.json')) { label = `Editing ${fp.split('/').pop()}`; }
                                        else if (fp.includes('.md')) { label = `Editing ${fp.split('/').pop()}`; }
                                        else { label = `Editing ${fp.split('/').pop() || 'file'}`; }
                                    }
                                    if (name === 'read') {
                                        const fp = args.path || args.file_path || '';
                                        if (fp.includes('index.html')) { label = 'Reading dashboard code'; }
                                        else if (fp) { label = `Reading ${fp.split('/').pop()}`; }
                                    }
                                    if (name === 'write') {
                                        const fp = args.path || args.file_path || '';
                                        if (fp.includes('mind-state')) { return null; } // Skip — meta update, not real work
                                        else if (fp.includes('sorare')) { label = 'Updating Sorare data'; }
                                        else if (fp.includes('x-plan') || fp.includes('x-stats')) { label = 'Updating X/Twitter data'; }
                                        else if (fp.includes('index.html')) { label = 'Updating dashboard UI'; }
                                        else if (fp.includes('server.js')) { label = 'Updating dashboard server'; }
                                    }
                                    return { label, status: 'active', tool };
                                });
                                // Keep existing descriptive task name — only set if truly empty
                                // NEVER use generic "Working..." — infer from steps instead
                                if (!current.task || current.task === 'Processing incoming message...' || current.task === 'Working...') {
                                    // Try to infer a descriptive task from the latest step labels
                                    const latestLabel = steps.filter(Boolean).map(s => s.label).pop();
                                    if (latestLabel) {
                                        current.task = latestLabel;
                                    } else {
                                        current.task = 'Processing request...';
                                    }
                                }
                                // Filter out null entries (skipped tools like mind-state writes)
                                const validSteps = steps.filter(Boolean);
                                if (validSteps.length === 0) continue; // Nothing to show
                                // Append new steps to existing ones (mark previous active as done)
                                const existingSteps = (current.steps || []).map(s => 
                                    s.status === 'active' ? { ...s, status: 'done' } : s
                                );
                                // Only keep last 6 steps to prevent overflow
                                const combined = [...existingSteps, ...validSteps].slice(-6);
                                current.steps = combined;
                                // Use assistant narration if available, otherwise only overwrite stale thoughts
                                const genericThoughts = ['New message received — processing...', 'Composing response...', 'Reply sent. Idle — waiting for Josh.', ''];
                                if (narration && narration.length > 10) {
                                    current.thought = narration;
                                } else if (!current.thought || genericThoughts.includes(current.thought)) {
                                    const stepLabels = validSteps.map(s => s.label);
                                    current.thought = stepLabels.length === 1 ? stepLabels[0] : stepLabels.join(' → ');
                                }
                                current.lastUpdated = Date.now();
                                fs.writeFileSync(mindFile, JSON.stringify(current, null, 2));
                                console.log(`⚡ Mind updated: ${toolCalls.length} tool calls (${toolCalls.map(tc => tc.name).join(', ')})`);
                            } else if (textParts.length > 0 && msg.stopReason === 'stop') {
                                // Final text response with stop — return to idle but keep steps as "done" (dimmed)
                                // Skip HEARTBEAT_OK and NO_REPLY (not real replies)
                                const replyText = textParts.map(t => t.text).join('').trim();
                                if (replyText === 'HEARTBEAT_OK' || replyText === 'NO_REPLY') continue;
                                current.lastTask = current.task || current.lastTask;
                                current.task = null;
                                if (current.steps && current.steps.length > 0) {
                                    current.steps = current.steps.map(s => ({ ...s, status: 'done' }));
                                }
                                current.thought = 'Reply sent. Idle — waiting for Josh.';
                                current.lastUpdated = Date.now();
                                idleProtectedUntil = Date.now() + 2000; // Protect idle for 2s
                                fs.writeFileSync(mindFile, JSON.stringify(current, null, 2));
                                console.log('⚡ Mind updated: reply sent, steps dimmed, returning to idle');
                            } else if (textParts.length > 0) {
                                // Text but not final (might have more tool calls coming)
                                current.thought = 'Composing response...';
                                current.steps = [{ label: 'Sending reply', status: 'active', tool: 'opus' }];
                                current.lastUpdated = Date.now();
                                fs.writeFileSync(mindFile, JSON.stringify(current, null, 2));
                                console.log('⚡ Mind updated: composing reply');
                            }
                        } else if (role === 'toolResult') {
                            // Tool result came back — just update timestamp, preserve existing thought
                            try {
                                const current2 = JSON.parse(fs.readFileSync(mindFile, 'utf8'));
                                current2.lastUpdated = Date.now();
                                fs.writeFileSync(mindFile, JSON.stringify(current2, null, 2));
                            } catch {}
                        }
                    } catch { /* skip unparseable lines */ }
                }
            } else {
                lastSize = stat.size;
            }
        } catch {
            // Transcript might have rotated
            mainTranscript = findMainTranscript();
            lastSize = 0;
        }
    }

    // Poll every 200ms for near-instant detection
    setInterval(checkForNewMessage, 100);
    // Re-discover transcript every 60s in case of rotation
    setInterval(() => { mainTranscript = findMainTranscript(); lastSize = 0; }, 60000);
    console.log('⚡ Instant mind activation watcher enabled');
})();

// API endpoint for Jane to trigger manual push
// POST /api/push { widget: 'tasks', data: {...} }
// This allows Jane to push updates without writing files

server.listen(PORT, '0.0.0.0', () => {
    console.log(`🌿 Jane Dashboard running at:`);
    console.log(`   Local:   http://localhost:${PORT}`);
    console.log(`   Network: http://${getLocalIP()}:${PORT}`);
    console.log(`   WebSocket: ws://localhost:${PORT}`);
    if (httpsServer) {
        httpsServer.listen(HTTPS_PORT, '0.0.0.0', () => {
            console.log(`   HTTPS:   https://${getLocalIP()}:${HTTPS_PORT}`);
            console.log(`   Tailscale HTTPS: https://100.121.89.84:${HTTPS_PORT}`);
            console.log(`   WSS:     wss://localhost:${HTTPS_PORT}`);
        });
    }
    console.log('');
    console.log('Press Ctrl+C to stop');
});

function getLocalIP() {
    const { networkInterfaces } = require('os');
    const nets = networkInterfaces();
    for (const name of Object.keys(nets)) {
        for (const net of nets[name]) {
            if (net.family === 'IPv4' && !net.internal) {
                return net.address;
            }
        }
    }
    return '127.0.0.1';
}
