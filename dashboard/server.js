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
        while ((match = itemRegex.exec(xml)) !== null && items.length < 5) {
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
            agenticRetail: allItems.slice(1, 5),
            agenticEnterprise: allItems.slice(5, 9),
            general: allItems.slice(9, 12).map(item => ({ tag: '📰 News', ...item }))
        };
    } catch (error) {
        console.error('AI News fetch error:', error.message);
        return null;
    }
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
        
        // Also check for a dedicated tasks file
        const tasksFile = path.join(WORKSPACE, 'tasks.json');
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

    // API endpoint for system stats
    if (req.url === '/api/system') {
        const stats = getSystemStats();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(stats));
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
    
    // API endpoint for TikTok stats (reads from JSON, updated by Jane's heartbeat)
    if (req.url === '/api/tiktok') {
        const statsFile = path.join(ROOT, 'tiktok-stats.json');
        if (fs.existsSync(statsFile)) {
            const stats = JSON.parse(fs.readFileSync(statsFile, 'utf8'));
            stats.note = 'Updated via heartbeat browser scraping (TikTok has no public API)';
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
    
    // API endpoint for Sorare lineup (reads from JSON, can be updated via Sorare GraphQL API)
    if (req.url === '/api/sorare') {
        const statsFile = path.join(ROOT, 'sorare-stats.json');
        if (fs.existsSync(statsFile)) {
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
        
        Promise.all([fetchUrl(mainUrl), fetchUrl(superBowlUrl)]).then(([mainMarkets, nflMarkets]) => {
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
                    endDate: m.endDate
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
                        question: '🏈 Super Bowl LX: Seahawks vs Patriots',
                        yesOdds: seahawks.yesOdds,
                        noOdds: patriots.yesOdds,
                        volume24h: (seahawks.volume24h || 0) + (patriots.volume24h || 0),
                        slug: 'will-the-seattle-seahawks-win-super-bowl-2026',
                        isPinned: true,
                        teams: {
                            favorite: { name: 'Seahawks', odds: seahawks.yesOdds },
                            underdog: { name: 'Patriots', odds: patriots.yesOdds }
                        }
                    };
                }
            }
            
            // Filter for competitive markets (odds between 15% and 85%)
            const competitive = simplified.filter(m => {
                if (m.question && m.question.toLowerCase().includes('super bowl')) return false;
                return m.yesOdds >= 15 && m.yesOdds <= 85;
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
            
            // Build balanced list: max 3 sports in top 5
            const sports = competitive.filter(isSportsMarket);
            const nonSports = competitive.filter(m => !isSportsMarket(m));
            
            let balanced = [];
            let sportsCount = 0;
            let sportsIdx = 0;
            let nonSportsIdx = 0;
            
            // Fill top 10 with max 3 sports in positions 1-5
            while (balanced.length < 10 && (sportsIdx < sports.length || nonSportsIdx < nonSports.length)) {
                const inTop5 = balanced.length < 5;
                
                if (inTop5 && sportsCount < 3 && sportsIdx < sports.length) {
                    // Can still add sports to top 5
                    const nextSports = sports[sportsIdx];
                    const nextNonSports = nonSports[nonSportsIdx];
                    
                    // Pick higher volume
                    if (!nextNonSports || (nextSports && nextSports.volume24h >= nextNonSports.volume24h)) {
                        balanced.push(sports[sportsIdx++]);
                        sportsCount++;
                    } else {
                        balanced.push(nonSports[nonSportsIdx++]);
                    }
                } else if (inTop5) {
                    // Top 5 but sports maxed out - must use non-sports
                    if (nonSportsIdx < nonSports.length) {
                        balanced.push(nonSports[nonSportsIdx++]);
                    } else if (sportsIdx < sports.length) {
                        balanced.push(sports[sportsIdx++]);
                    }
                } else {
                    // After top 5, just fill by volume
                    const nextS = sports[sportsIdx];
                    const nextN = nonSports[nonSportsIdx];
                    if (nextS && (!nextN || nextS.volume24h >= nextN.volume24h)) {
                        balanced.push(sports[sportsIdx++]);
                    } else if (nextN) {
                        balanced.push(nonSports[nonSportsIdx++]);
                    }
                }
            }
            
            const finalMarkets = pinnedMarket 
                ? [pinnedMarket, ...balanced.slice(0, 9)]
                : balanced.slice(0, 10);
            
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
    // Creates a flag file that Jane checks during heartbeats
    if (req.url === '/api/tiktok-request-update') {
        const flagFile = path.join(ROOT, '.tiktok-refresh-requested');
        fs.writeFileSync(flagFile, new Date().toISOString());
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
            success: true, 
            message: 'Update requested. Jane will refresh TikTok stats shortly.',
            requestedAt: new Date().toISOString()
        }));
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
    let filePath = path.join(ROOT, urlPath === '/' ? 'index.html' : urlPath);
    
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

server.listen(PORT, '0.0.0.0', () => {
    console.log(`🌿 Jane Dashboard running at:`);
    console.log(`   Local:   http://localhost:${PORT}`);
    console.log(`   Network: http://${getLocalIP()}:${PORT}`);
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
