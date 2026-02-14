#!/usr/bin/env node

const CDP = require('chrome-remote-interface');
const fs = require('fs');

const username = process.argv[2];
const replyText = process.argv[3];

if (!username || !replyText) {
  console.error('Usage: x-post-reply.js <username> <reply_text>');
  process.exit(1);
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function postReply() {
  let client;
  
  try {
    client = await CDP({ port: 18800 });
    const { Page, Runtime, Input } = client;
    
    await Page.enable();
    await Runtime.enable();
    
    console.log(`Searching for @${username}'s tweet...`);
    
    // Find the tweet on the current page
    const foundTweet = await Runtime.evaluate({
      expression: `
        (() => {
          const articles = document.querySelectorAll('article[data-testid="tweet"]');
          
          for (let article of articles) {
            const userLink = article.querySelector('a[href^="/"][role="link"]');
            const username = userLink ? userLink.getAttribute('href').slice(1) : null;
            
            if (username === '${username}') {
              const replyBtn = article.querySelector('[data-testid="reply"]');
              if (replyBtn) {
                const rect = replyBtn.getBoundingClientRect();
                return {
                  found: true,
                  x: rect.x + rect.width / 2,
                  y: rect.y + rect.height / 2
                };
              }
            }
          }
          
          return { found: false };
        })()
      `,
      returnByValue: true
    });
    
    if (!foundTweet.result.value.found) {
      console.error('Tweet not found on current page');
      await client.close();
      return false;
    }
    
    console.log('Found tweet! Clicking reply button...');
    
    // Click reply button
    const { x, y } = foundTweet.result.value;
    await Input.dispatchMouseEvent({
      type: 'mousePressed',
      x: x,
      y: y,
      button: 'left',
      clickCount: 1
    });
    await Input.dispatchMouseEvent({
      type: 'mouseReleased',
      x: x,
      y: y,
      button: 'left',
      clickCount: 1
    });
    
    await sleep(2000);
    
    console.log('Typing reply...');
    
    // Type the reply text using React injection
    await Runtime.evaluate({
      expression: `
        (() => {
          const replyBox = document.querySelector('[data-testid="tweetTextarea_0"]');
          if (!replyBox) return false;
          
          // Get React props
          const reactKey = Object.keys(replyBox).find(k => k.startsWith('__reactProps'));
          if (!reactKey) return false;
          
          const reactProps = replyBox[reactKey];
          
          // Set value
          replyBox.textContent = ${JSON.stringify(replyText)};
          
          // Trigger React onChange
          if (reactProps && reactProps.onChange) {
            const event = new InputEvent('input', { bubbles: true, cancelable: true });
            Object.defineProperty(event, 'target', { value: replyBox, enumerable: true });
            reactProps.onChange(event);
          }
          
          // Also dispatch native input event
          replyBox.dispatchEvent(new InputEvent('input', { bubbles: true }));
          
          return true;
        })()
      `,
      returnByValue: true
    });
    
    await sleep(1500);
    
    console.log('Clicking post button...');
    
    // Click post button
    await Runtime.evaluate({
      expression: `
        (() => {
          const postBtn = document.querySelector('[data-testid="tweetButton"]');
          if (postBtn && !postBtn.disabled) {
            postBtn.click();
            return true;
          }
          return false;
        })()
      `,
      returnByValue: true
    });
    
    await sleep(2000);
    
    console.log('Reply posted successfully!');
    
    await client.close();
    return true;
    
  } catch (err) {
    console.error('Error:', err);
    if (client) await client.close();
    return false;
  }
}

postReply()
  .then(success => process.exit(success ? 0 : 1))
  .catch(err => {
    console.error(err);
    process.exit(1);
  });
