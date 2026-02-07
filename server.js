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

const { execSync } = require('child_process');
const os = require('os');
const https = require('https');

// Caches (to avoid rate limits)
let cryptoCache = { data: null, timestamp: 0 };
let aiNewsCache = { data: null, timestamp: 0 };
let tickerCache = { data: null, timestamp: 0 };

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

// Get system stats
function getSystemStats() {
    try {
        // CPU usage (macOS)
        const cpuRaw = execSync("top -l 1 | grep 'CPU usage' | awk '{print $3}' | tr -d '%'", { encoding: 'utf8' });
        const cpu = parseFloat(cpuRaw) || 0;
        
        // Memory usage
        const totalMem = os.totalmem();
        const freeMem = os.freemem();
        const memory = Math.round(((totalMem - freeMem) / totalMem) * 100);
        
        // Disk usage
        const diskRaw = execSync("df -h / | tail -1 | awk '{print $5}' | tr -d '%'", { encoding: 'utf8' });
        const disk = parseInt(diskRaw) || 0;
        
        // System uptime
        const uptimeSeconds = os.uptime();
        const days = Math.floor(uptimeSeconds / 86400);
        const hours = Math.floor((uptimeSeconds % 86400) / 3600);
        const minutes = Math.floor((uptimeSeconds % 3600) / 60);
        let uptime = '';
        if (days > 0) uptime += `${days}d `;
        if (hours > 0) uptime += `${hours}h `;
        uptime += `${minutes}m`;
        
        return { cpu: Math.round(cpu), memory, disk, uptime };
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

const server = http.createServer((req, res) => {
    // CORS headers for local development
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
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
                { name: 'Phantom Wallet', detail: 'Solana', icon: icons.phantom, active: true }
            ],
            dataSources: [
                { name: 'Polymarket', detail: 'prediction markets', icon: icons.polymarket, active: true },
                { name: 'Kalshi', detail: 'prediction markets', icon: icons.kalshi, active: true },
                { name: 'Manifold', detail: 'prediction markets', icon: icons.manifold, active: true },
                { name: 'Metaculus', detail: 'prediction markets', icon: icons.metaculus, active: true },
                { name: 'CoinGecko', detail: 'crypto prices', icon: icons.coingecko, active: true },
                { name: 'Yahoo Finance', detail: 'stock prices', icon: icons.yahoo, active: true },
                { name: 'DexScreener', detail: 'memecoin data', icon: icons.dexscreener, active: true },
                { name: 'Sorare GraphQL', detail: 'fantasy sports', icon: icons.sorare, active: true },
                { name: 'GitHub API', detail: 'code repos', icon: icons.github, active: true }
            ]
        };
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(connections));
        return;
    }

    // API endpoint for system stats
    if (req.url === '/api/system') {
        const stats = getSystemStats();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(stats));
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
    
    // API endpoint for wallet balances (live from Solana RPC)
    if (req.url === '/api/wallet') {
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
                
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    memecoins,
                    lastUpdated: new Date().toISOString(),
                    source: 'GeckoTerminal',
                    filters: { minMcap: MIN_MCAP, maxMcap: MAX_MCAP }
                }));
            });
        }).catch(err => {
            console.error('Memecoin fetch error:', err);
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Failed to fetch memecoins' }));
        });
        
        return;
    }
    
    // API endpoint for Sorare lineup (reads from JSON, triggers background refresh if stale)
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
            
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ 
                markets: finalMarkets, 
                lastUpdated: new Date().toISOString(),
                filter: 'competitive (15-85% odds)',
                hasPinned: !!pinnedMarket
            }));
        }).catch(err => {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: err.message }));
        });
        return;
    }
    
    // API endpoint for market data
    if (req.url === '/api/market') {
        fetchMarketData().then(data => {
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

    // Parse URL and strip query string
    const urlPath = new URL(req.url, `http://${req.headers.host}`).pathname;
    
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
});

// ============================================
// WebSocket Server for Real-Time Push Updates
// ============================================
const WebSocket = require('ws');
const wss = new WebSocket.Server({ server });

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
    'panini': path.join(ROOT, 'panini-collection.json'),
    'mind': path.join(ROOT, 'mind-state.json')
};

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
                debounceFileChange(key, () => {
                    try {
                        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                        console.log(`📤 Broadcasting ${key} update to ${clients.size} clients`);
                        broadcast({ type: 'update', widget: key, data, timestamp: Date.now() });
                    } catch (err) {
                        console.error(`Failed to read ${key}:`, err.message);
                    }
                });
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
                console.log(`📤 Broadcasting tasks update to ${clients.size} clients`);
                broadcast({ type: 'update', widget: 'tasks', data, timestamp: Date.now() });
            } catch (err) {
                // File might not exist yet
            }
        });
    }
});

// API endpoint for Jane to trigger manual push
// POST /api/push { widget: 'tasks', data: {...} }
// This allows Jane to push updates without writing files

server.listen(PORT, '0.0.0.0', () => {
    console.log(`🌿 Jane Dashboard running at:`);
    console.log(`   Local:   http://localhost:${PORT}`);
    console.log(`   Network: http://${getLocalIP()}:${PORT}`);
    console.log(`   WebSocket: ws://localhost:${PORT}`);
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
