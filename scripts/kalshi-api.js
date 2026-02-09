const crypto = require('crypto');
const fs = require('fs');
const https = require('https');

const API_KEY = fs.readFileSync('/Users/jc_agent/.openclaw/workspace/.secrets/kalshi_api_key.txt', 'utf8').trim();
const PRIVATE_KEY = fs.readFileSync('/Users/jc_agent/.openclaw/workspace/.secrets/kalshi_private_key.pem', 'utf8');
const BASE_URL = 'https://api.elections.kalshi.com';

function signRequest(method, path) {
  const timestamp = Date.now().toString();
  const msgString = timestamp + method + path;
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

function apiGet(path) {
  return new Promise((resolve, reject) => {
    const { timestamp, signature } = signRequest('GET', path);
    const url = new URL(BASE_URL + path);
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
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch(e) { resolve(data); }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function main() {
  const endpoint = process.argv[2] || '/trade-api/v2/portfolio/balance';
  try {
    const result = await apiGet(endpoint);
    console.log(JSON.stringify(result, null, 2));
  } catch(e) {
    console.error('Error:', e.message);
  }
}

main();
