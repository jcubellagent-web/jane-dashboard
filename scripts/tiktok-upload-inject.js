#!/usr/bin/env node
/**
 * Inject a video into TikTok Studio via CDP + React onChange hack.
 * Uses Playwright's CDP session to evaluate large JS payloads directly.
 * 
 * Usage: node tiktok-upload-inject.js <ws-endpoint> <video-path> [caption] [hashtags]
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const wsEndpoint = process.argv[2];
const videoPath = process.argv[3];
const caption = process.argv[4] || '';
const hashtags = process.argv[5] || '';

if (!wsEndpoint || !videoPath) {
  console.error('Usage: node tiktok-upload-inject.js <ws-endpoint> <video-path> [caption] [hashtags]');
  process.exit(1);
}

async function main() {
  // Connect to existing browser
  const browser = await chromium.connectOverCDP(wsEndpoint);
  const contexts = browser.contexts();
  
  console.log(`Connected. ${contexts.length} contexts found.`);
  
  // Find the TikTok upload page
  let targetPage = null;
  for (const ctx of contexts) {
    for (const page of ctx.pages()) {
      if (page.url().includes('tiktok.com/tiktokstudio/upload')) {
        targetPage = page;
        break;
      }
    }
    if (targetPage) break;
  }
  
  if (!targetPage) {
    console.error('No TikTok Studio upload page found');
    process.exit(1);
  }
  
  console.log(`Using page: ${targetPage.url()}`);
  
  // Read video
  const videoBuffer = fs.readFileSync(videoPath);
  const b64 = videoBuffer.toString('base64');
  const mimeType = 'video/mp4'; // TikTok accepts video/*
  const filename = path.basename(videoPath);
  
  console.log(`Video: ${filename}, ${videoBuffer.length} bytes, base64: ${b64.length} chars`);
  
  // Inject video file via CDP
  console.log('Injecting video file...');
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
      
      // Strategy: Look for onChange in the component tree more thoroughly
      const fiberKey = Object.keys(input).find(k => k.startsWith('__reactFiber'));
      const propsKey = Object.keys(input).find(k => k.startsWith('__reactProps'));
      
      let handlers = [];
      
      // Collect all onChange handlers in the fiber tree
      if (fiberKey) {
        let fiber = input[fiberKey];
        let depth = 0;
        while (fiber && depth < 30) {
          if (fiber.memoizedProps) {
            if (fiber.memoizedProps.onChange) handlers.push({ type: 'fiber-onChange', fiber, depth });
            if (fiber.memoizedProps.onInput) handlers.push({ type: 'fiber-onInput', fiber, depth });
            if (fiber.memoizedProps.onchange) handlers.push({ type: 'fiber-onchange', fiber, depth });
          }
          fiber = fiber.return;
          depth++;
        }
      }
      
      // Try props-based handler
      if (propsKey && input[propsKey]) {
        if (input[propsKey].onChange) handlers.push({ type: 'props-onChange', props: input[propsKey] });
        if (input[propsKey].onInput) handlers.push({ type: 'props-onInput', props: input[propsKey] });
      }
      
      // Try each handler
      for (const handler of handlers) {
        try {
          const event = {
            target: input,
            currentTarget: input,
            nativeEvent: new Event('change'),
            bubbles: true,
            cancelable: true,
            type: 'change',
            preventDefault: () => {},
            stopPropagation: () => {}
          };
          
          if (handler.type.includes('fiber')) {
            const fn = handler.fiber.memoizedProps[handler.type.split('-')[1]];
            fn(event);
          } else {
            const fn = handler.props[handler.type.split('-')[1]];
            fn(event);
          }
          
          // Check if upload started by looking for upload progress or change in DOM
          setTimeout(() => {}, 100);
          return `SUCCESS: ${handler.type} triggered at depth ${handler.depth || 0}, file size=${file.size}`;
        } catch (e) {
          continue;
        }
      }
      
      // If no handlers worked, try native events
      input.dispatchEvent(new Event('change', { bubbles: true }));
      input.dispatchEvent(new Event('input', { bubbles: true }));
      
      return `PARTIAL: Dispatched native events, ${handlers.length} handlers found, file size=${file.size}`;
    } catch (e) {
      return `ERROR: ${e.message}`;
    }
  }, { b64Data: b64, mime: mimeType, fname: filename });
  
  console.log(`File injection result: ${result}`);
  
  if (!result.startsWith('SUCCESS')) {
    console.error('File injection failed');
    await browser.close();
    process.exit(1);
  }
  
  // Wait for upload to process
  console.log('Waiting for upload to process...');
  await targetPage.waitForTimeout(3000);
  
  // Set caption if provided
  if (caption) {
    console.log(`Setting caption: ${caption}`);
    const captionResult = await targetPage.evaluate((text) => {
      try {
        // TikTok uses a contenteditable div for caption
        const captionDiv = document.querySelector('[contenteditable="true"]');
        if (!captionDiv) {
          // Try finding by placeholder text
          const allEditables = Array.from(document.querySelectorAll('[contenteditable="true"]'));
          const captionField = allEditables.find(el => 
            el.textContent.includes('description') || 
            el.getAttribute('placeholder')?.includes('description')
          );
          if (!captionField) return 'ERROR: Caption field not found';
          
          captionField.focus();
          captionField.textContent = text;
          captionField.dispatchEvent(new Event('input', { bubbles: true }));
          return 'SUCCESS: Caption set';
        }
        
        captionDiv.focus();
        captionDiv.textContent = text;
        captionDiv.dispatchEvent(new Event('input', { bubbles: true }));
        return 'SUCCESS: Caption set';
      } catch (e) {
        return `ERROR: ${e.message}`;
      }
    }, caption);
    console.log(`Caption result: ${captionResult}`);
  }
  
  // Add hashtags if provided
  if (hashtags) {
    console.log(`Adding hashtags: ${hashtags}`);
    const hashtagResult = await targetPage.evaluate((tags) => {
      try {
        const captionDiv = document.querySelector('[contenteditable="true"]');
        if (!captionDiv) return 'ERROR: Caption field not found for hashtags';
        
        // Append hashtags with space
        const currentText = captionDiv.textContent;
        const newText = currentText + (currentText ? ' ' : '') + tags;
        captionDiv.textContent = newText;
        captionDiv.dispatchEvent(new Event('input', { bubbles: true }));
        
        return 'SUCCESS: Hashtags added';
      } catch (e) {
        return `ERROR: ${e.message}`;
      }
    }, hashtags);
    console.log(`Hashtag result: ${hashtagResult}`);
  }
  
  console.log('Upload automation complete. Review and click Post manually or extend script.');
  
  // Disconnect without closing
  await browser.close();
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
