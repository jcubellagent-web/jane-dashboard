#!/usr/bin/env node
const puppeteer = require('puppeteer-core');

async function scrapeXAnalytics() {
  try {
    const browser = await puppeteer.connect({
      browserURL: 'http://127.0.0.1:18800',
      defaultViewport: null
    });

    const pages = await browser.pages();
    const page = pages.find(p => p.url().includes('account_analytics')) || pages[0];
    
    if (!page.url().includes('account_analytics')) {
      await page.goto('https://x.com/i/account_analytics', { waitUntil: 'networkidle2' });
      await page.waitForTimeout(3000);
    }

    // Extract analytics data
    const data = await page.evaluate(() => {
      const stats = {};
      
      // Try to find impression count
      const impressionEl = document.querySelector('[data-testid="impressions"]') || 
                          Array.from(document.querySelectorAll('span')).find(el => 
                            el.textContent.includes('Impressions') || el.textContent.includes('impressions'));
      
      // Try various selectors for the metrics
      const metrics = Array.from(document.querySelectorAll('div[role="group"], div[data-testid]'));
      
      // Extract visible numbers from the page
      const numbers = Array.from(document.querySelectorAll('span, div')).map(el => el.textContent.trim())
        .filter(text => /^[\d,]+\.?\d*%?$/.test(text));
      
      return {
        rawText: document.body.innerText.substring(0, 2000),
        numbers: numbers.slice(0, 20)
      };
    });

    console.log(JSON.stringify(data, null, 2));
    await browser.disconnect();
    
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

scrapeXAnalytics();
