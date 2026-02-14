#!/usr/bin/env node
/**
 * X (Twitter) Image Upload via React onChange hack
 * 
 * This script injects an image into X's compose dialog by:
 * 1. Splitting the image base64 into chunks
 * 2. Injecting each chunk via browser evaluate calls
 * 3. Creating a File blob and triggering React's onChange
 * 
 * Usage: node x-upload-image.js <image-path> <browser-target-id> [profile]
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const imagePath = process.argv[2];
const targetId = process.argv[3];
const profile = process.argv[4] || 'openclaw';

if (!imagePath || !targetId) {
  console.error('Usage: node x-upload-image.js <image-path> <browser-target-id> [profile]');
  process.exit(1);
}

// Read image and convert to base64
const imageBuffer = fs.readFileSync(imagePath);
const b64 = imageBuffer.toString('base64');
console.log(`Image size: ${imageBuffer.length} bytes, base64 length: ${b64.length}`);

// Split into chunks of ~18000 chars (safe for evaluate)
const CHUNK_SIZE = 18000;
const chunks = [];
for (let i = 0; i < b64.length; i += CHUNK_SIZE) {
  chunks.push(b64.slice(i, i + CHUNK_SIZE));
}
console.log(`Split into ${chunks.length} chunks`);

// Helper to call openclaw CLI for browser evaluate
function browserEval(fn) {
  // Use the gateway API directly
  const gatewayToken = process.env.OPENCLAW_GATEWAY_TOKEN;
  const port = 18789;
  
  const payload = JSON.stringify({
    action: 'act',
    profile,
    targetId,
    request: { kind: 'evaluate', fn }
  });
  
  const cmd = `curl -s -X POST http://localhost:${port}/api/browser -H "Content-Type: application/json" -H "Authorization: Bearer ${gatewayToken}" -d '${payload.replace(/'/g, "'\\''")}'`;
  
  try {
    const result = execSync(cmd, { encoding: 'utf8', timeout: 30000 });
    const parsed = JSON.parse(result);
    return parsed;
  } catch (e) {
    console.error('Error:', e.message);
    return null;
  }
}

// Initialize
console.log('Initializing...');
let result = browserEval("() => { window.__imgB64 = ''; return 'ready'; }");
console.log('Init:', result?.result);

// Inject chunks
for (let i = 0; i < chunks.length; i++) {
  const chunk = chunks[i];
  console.log(`Injecting chunk ${i + 1}/${chunks.length} (${chunk.length} chars)...`);
  result = browserEval(`() => { window.__imgB64 += '${chunk}'; return 'chunk ${i + 1} added, total: ' + window.__imgB64.length; }`);
  console.log(`  Result: ${result?.result}`);
}

// Verify
result = browserEval("() => { return 'Final b64 length: ' + window.__imgB64.length; }");
console.log('Verify:', result?.result);

// Create blob and trigger React onChange
console.log('Creating file and triggering onChange...');
const triggerFn = `async () => {
  try {
    const b64 = window.__imgB64;
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    const blob = new Blob([bytes], { type: 'image/png' });
    const file = new File([blob], 'header.png', { type: 'image/png' });
    const dt = new DataTransfer();
    dt.items.add(file);
    const input = document.querySelectorAll('input[type="file"]')[0];
    input.files = dt.files;
    const rk = Object.keys(input).find(k => k.startsWith('__reactProps'));
    if (rk && input[rk].onChange) {
      input[rk].onChange({ target: input, currentTarget: input, nativeEvent: new Event('change'), bubbles: true, type: 'change' });
      return 'SUCCESS: file size=' + file.size;
    }
    return 'No onChange found';
  } catch(e) {
    return 'Error: ' + e.message;
  }
}`;

result = browserEval(triggerFn);
console.log('Trigger result:', result?.result);

// Cleanup
browserEval("() => { delete window.__imgB64; return 'cleaned up'; }");
console.log('Done!');
