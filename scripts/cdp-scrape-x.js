#!/usr/bin/env node
const http = require('http');

async function cdpRequest(url, method, params = {}) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ id: 1, method, params });
    const req = http.request(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function scrape() {
  try {
    // Get WebSocket URL for the analytics tab
    const listResp = await new Promise((resolve, reject) => {
      http.get('http://127.0.0.1:18800/json/list', (res) => {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => resolve(JSON.parse(body)));
      }).on('error', reject);
    });

    const analyticsTab = listResp.find(t => t.type === 'page' && t.url.includes('account_analytics'));
    if (!analyticsTab) {
      console.error('No analytics tab found');
      process.exit(1);
    }

    const wsUrl = analyticsTab.webSocketDebuggerUrl.replace('ws://', 'http://').replace('/devtools/page/', '/json/');
    const cdpUrl = `http://127.0.0.1:18800/json/${analyticsTab.id}`;

    // Extract data via Runtime.evaluate
    const evalResp = await cdpRequest(cdpUrl, 'Runtime.evaluate', {
      expression: `
        (() => {
          const stats = {};
          
          // Extract all visible text and numbers
          const allText = document.body.innerText;
          const lines = allText.split('\\n').map(l => l.trim()).filter(Boolean);
          
          // Find metrics by pattern
          const numbers = lines.filter(l => /^[\\d,]+(\\.\\d+)?%?$/.test(l));
          const labels = lines.filter(l => /impressions|engagement|visits|followers|following|likes|repost/i.test(l));
          
          // Try to extract specific metrics
          const textLower = allText.toLowerCase();
          
          return {
            allText: allText.substring(0, 3000),
            numbers: numbers.slice(0, 30),
            labels: labels.slice(0, 20)
          };
        })()
      `,
      returnByValue: true
    });

    if (evalResp.result && evalResp.result.result) {
      console.log(JSON.stringify(evalResp.result.result.value, null, 2));
    } else {
      console.error('Failed to evaluate:', JSON.stringify(evalResp, null, 2));
      process.exit(1);
    }

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

scrape();
