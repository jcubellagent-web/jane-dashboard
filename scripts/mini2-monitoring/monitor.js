const http = require('http');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const STATUS_FILE = path.join(__dirname, 'status.json');
const PORT = 3001;
const CHECK_INTERVAL = 60_000; // 1 minute

function run(cmd) {
  try { return execSync(cmd, { timeout: 5000 }).toString().trim(); }
  catch { return null; }
}

function checkAll() {
  const status = { timestamp: new Date().toISOString(), checks: {} };

  // Mini #1 reachability
  const ping = run('ping -c 1 -W 3 100.121.89.84');
  status.checks.mini1 = { ok: !!ping, detail: ping ? 'reachable' : 'unreachable' };

  // Ollama health
  try {
    const res = run('curl -sf http://localhost:11434/api/tags');
    const tags = res ? JSON.parse(res) : null;
    status.checks.ollama = { ok: !!tags, models: tags?.models?.map(m => m.name) || [] };
  } catch { status.checks.ollama = { ok: false }; }

  // Disk space
  const df = run("df -h / | tail -1 | awk '{print $4, $5}'");
  if (df) {
    const [avail, usePct] = df.split(' ');
    status.checks.disk = { ok: parseInt(usePct) < 90, available: avail, usedPercent: usePct };
  }

  // Memory
  const mem = run("vm_stat | head -5");
  const memInfo = run("sysctl -n hw.memsize");
  const totalGB = memInfo ? (parseInt(memInfo) / 1073741824).toFixed(1) : '?';
  status.checks.memory = { ok: true, totalGB, raw: mem };

  fs.writeFileSync(STATUS_FILE, JSON.stringify(status, null, 2));
  return status;
}

// Run checks periodically
checkAll();
setInterval(checkAll, CHECK_INTERVAL);

// HTTP server
http.createServer((req, res) => {
  if (req.url === '/status' || req.url === '/') {
    try {
      const data = fs.readFileSync(STATUS_FILE, 'utf8');
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(data);
    } catch {
      res.writeHead(500); res.end('{}');
    }
  } else {
    res.writeHead(404); res.end('Not found');
  }
}).listen(PORT, '0.0.0.0', () => console.log(`Monitor listening on :${PORT}`));
