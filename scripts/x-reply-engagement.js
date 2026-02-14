#!/usr/bin/env node

const CDP = require('chrome-remote-interface');

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function findAndReplyToThreads() {
  let client;
  
  try {
    // Connect to CDP
    client = await CDP({ port: 18800 });
    const { Page, Runtime, Network } = client;
    
    await Page.enable();
    await Network.enable();
    await Runtime.enable();
    
    // Navigate to X home
    console.log('Navigating to X...');
    await Page.navigate({ url: 'https://x.com/home' });
    await sleep(5000);
    
    // Scroll down to load more tweets
    console.log('Scrolling to load tweets...');
    await Runtime.evaluate({
      expression: 'window.scrollBy(0, 1000);'
    });
    await sleep(2000);
    
    // Extract tweets from timeline
    const tweetsResult = await Runtime.evaluate({
      expression: `
        (() => {
          const tweets = [];
          const articles = document.querySelectorAll('article[data-testid="tweet"]');
          
          for (let article of articles) {
            try {
              const userLink = article.querySelector('a[href^="/"][role="link"]');
              const username = userLink ? userLink.getAttribute('href').slice(1) : null;
              
              const textElement = article.querySelector('[data-testid="tweetText"]');
              const text = textElement ? textElement.textContent : '';
              
              const timeElement = article.querySelector('time');
              const time = timeElement ? timeElement.getAttribute('datetime') : null;
              
              const replyButton = article.querySelector('[data-testid="reply"]');
              const retweetButton = article.querySelector('[data-testid="retweet"]');
              const likeButton = article.querySelector('[data-testid="like"]');
              
              const replies = replyButton ? replyButton.getAttribute('aria-label') : '0';
              const retweets = retweetButton ? retweetButton.getAttribute('aria-label') : '0';
              const likes = likeButton ? likeButton.getAttribute('aria-label') : '0';
              
              // Check for mfer PFP
              const avatarImg = article.querySelector('img[alt][src*="profile_images"]');
              const isMfer = avatarImg && avatarImg.getAttribute('src').includes('profile_images');
              
              if (username && text && username !== 'AgentJc11443') {
                tweets.push({
                  username,
                  text: text.substring(0, 200),
                  time,
                  replies: parseInt(replies) || 0,
                  retweets: parseInt(retweets) || 0,
                  likes: parseInt(likes) || 0,
                  isMfer
                });
              }
            } catch (e) {
              // Skip invalid tweets
            }
          }
          
          return tweets;
        })()
      `,
      returnByValue: true
    });
    
    const tweets = tweetsResult.result.value;
    console.log(`Found ${tweets.length} tweets`);
    console.log(JSON.stringify(tweets, null, 2));
    
    await client.close();
    return tweets;
    
  } catch (err) {
    console.error('Error:', err);
    if (client) await client.close();
    throw err;
  }
}

findAndReplyToThreads()
  .then(() => process.exit(0))
  .catch(err => {
    console.error(err);
    process.exit(1);
  });
