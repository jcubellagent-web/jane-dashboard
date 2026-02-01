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

// Crypto price cache (to avoid rate limits)
let cryptoCache = { data: null, timestamp: 0 };

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
