#!/usr/bin/env node
/**
 * Scrape X analytics via CDP + Playwright.
 */

const { chromium } = require('playwright');

const wsEndpoint = process.argv[2];

if (!wsEndpoint) {
  console.error('Usage: node scrape-x-analytics.js <ws-endpoint>');
  process.exit(1);
}

async function main() {
  // Connect to existing browser
  const browser = await chromium.connectOverCDP(wsEndpoint);
  const contexts = browser.contexts();
  
  console.error(`Connected. ${contexts.length} contexts found.`);
  
  // Find the analytics page
  let targetPage = null;
  for (const ctx of contexts) {
    for (const page of ctx.pages()) {
      if (page.url().includes('account_analytics')) {
        targetPage = page;
        break;
      }
    }
    if (targetPage) break;
  }
  
  if (!targetPage) {
    console.error('Analytics page not found');
    process.exit(1);
  }
  
  console.error(`Using page: ${targetPage.url()}`);
  
  // Wait longer for page to load
  await targetPage.waitForTimeout(5000);
  
  // Scrape the data
  const data = await targetPage.evaluate(() => {
    const result = {};
    
    // Try multiple selectors and approaches
    // First, try to find specific elements
    const allText = document.body.innerText;
    
    // Debug: log first 500 chars
    console.log('Page text (first 500):', allText.substring(0, 500));
    
    // Try different patterns
    const patterns = {
      impressions: /([\\d,]+)\\s*[Ii]mpressions/,
      engagements: /([\\d,]+)\\s*[Ee]ngagements/,
      profileVisits: /([\\d,]+)\\s*[Pp]rofile\\s+[Vv]isits/,
      likes: /([\\d,]+)\\s*[Ll]ikes/,
      reposts: /([\\d,]+)\\s*([Rr]eposts|[Rr]etweets)/,
      followers: /([\\d,]+)\\s*[Ff]ollowers/,
      following: /([\\d,]+)\\s*[Ff]ollowing/,
      engagementRate: /([\\d.]+)%\\s*[Ee]ngagement\\s+[Rr]ate/
    };
    
    for (const [key, pattern] of Object.entries(patterns)) {
      const match = allText.match(pattern);
      if (match) {
        if (key === 'engagementRate') {
          result[key] = parseFloat(match[1]);
        } else {
          result[key] = parseInt(match[1].replace(/,/g, ''));
        }
      }
    }
    
    // Also try to find any numbers that look like stats
    const lines = allText.split('\\n');
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      // Look for lines with just numbers (possibly with commas)
      if (/^[\\d,]+$/.test(line)) {
        console.log(`Found number line ${i}: ${line}`);
      }
    }
    
    return result;
  });
  
  console.log(JSON.stringify(data, null, 2));
  
  // Disconnect without closing
  await browser.close();
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
