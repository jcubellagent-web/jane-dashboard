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

        res.writeHead(200, { 'Content-Type': contentType });
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
