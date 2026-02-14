#!/usr/bin/env node
/**
 * Inject an image into X's compose dialog via CDP + React onChange hack.
 * Uses Playwright's CDP session to evaluate large JS payloads directly.
 * 
 * Usage: node x-image-inject.js <ws-endpoint> <image-path>
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const wsEndpoint = process.argv[2];
const imagePath = process.argv[3];

if (!wsEndpoint || !imagePath) {
  console.error('Usage: node x-image-inject.js <ws-endpoint> <image-path>');
  process.exit(1);
}

async function main() {
  // Connect to existing browser
  const browser = await chromium.connectOverCDP(wsEndpoint);
  const contexts = browser.contexts();
  
  console.log(`Connected. ${contexts.length} contexts found.`);
  
  // Find the X compose page
  let targetPage = null;
  for (const ctx of contexts) {
    for (const page of ctx.pages()) {
      if (page.url().includes('x.com/compose')) {
        targetPage = page;
        break;
      }
    }
    if (targetPage) break;
  }
  
  if (!targetPage) {
    // Try opening compose
    const ctx = contexts[0];
    targetPage = ctx.pages()[0];
    if (targetPage) {
      await targetPage.goto('https://x.com/compose/post');
      await targetPage.waitForTimeout(2000);
    } else {
      console.error('No pages found');
      process.exit(1);
    }
  }
  
  console.log(`Using page: ${targetPage.url()}`);
  
  // Read image
  const imageBuffer = fs.readFileSync(imagePath);
  const b64 = imageBuffer.toString('base64');
  const mimeType = imagePath.endsWith('.jpg') || imagePath.endsWith('.jpeg') ? 'image/jpeg' : 'image/png';
  const filename = path.basename(imagePath);
  
  console.log(`Image: ${filename}, ${imageBuffer.length} bytes, base64: ${b64.length} chars`);
  
  // Use page.evaluate with the b64 as a parameter (not embedded in fn string)
  const result = await targetPage.evaluate(({ b64Data, mime, fname }) => {
    try {
      const binary = atob(b64Data);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
      const blob = new Blob([bytes], { type: mime });
      const file = new File([blob], fname, { type: mime });
      const dt = new DataTransfer();
      dt.items.add(file);
      const input = document.querySelector('input[type="file"]');
      if (!input) return 'ERROR: No file input found';
      input.files = dt.files;
      const rk = Object.keys(input).find(k => k.startsWith('__reactProps'));
      if (rk && input[rk].onChange) {
        input[rk].onChange({
          target: input,
          currentTarget: input,
          nativeEvent: new Event('change'),
          bubbles: true,
          type: 'change'
        });
        return `SUCCESS: onChange triggered, file size=${file.size}`;
      }
      return 'ERROR: No React onChange found';
    } catch (e) {
      return `ERROR: ${e.message}`;
    }
  }, { b64Data: b64, mime: mimeType, fname: filename });
  
  console.log(`Result: ${result}`);
  
  // Disconnect without closing
  await browser.close();
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
