#!/usr/bin/env node

const CDP = require('chrome-remote-interface');

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function findThreads() {
  let client;
  
  try {
    client = await CDP({ port: 18800 });
    const { Page, Runtime } = client;
    
    await Page.enable();
    await Runtime.enable();
    
    // Ensure we're on X home
    const currentUrl = await Runtime.evaluate({
      expression: 'window.location.href',
      returnByValue: true
    });
    
    if (!currentUrl.result.value.includes('x.com')) {
      await Page.navigate({ url: 'https://x.com/home' });
      await sleep(5000);
    }
    
    // Scroll several times to load more content
    for (let i = 0; i < 3; i++) {
      await Runtime.evaluate({
        expression: 'window.scrollBy(0, 800);'
      });
      await sleep(1500);
    }
    
    // Extract all tweets with better metadata
    const result = await Runtime.evaluate({
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
              
              // Extract engagement metrics
              const replyBtn = article.querySelector('[data-testid="reply"]');
              const retweetBtn = article.querySelector('[data-testid="retweet"]');
              const likeBtn = article.querySelector('[data-testid="like"]');
              
              const replyText = replyBtn ? replyBtn.getAttribute('aria-label') || '' : '';
              const retweetText = retweetBtn ? retweetBtn.getAttribute('aria-label') || '' : '';
              const likeText = likeBtn ? likeBtn.getAttribute('aria-label') || '' : '';
              
              const replies = parseInt(replyText.match(/\\d+/)?.[0] || '0');
              const retweets = parseInt(retweetText.match(/\\d+/)?.[0] || '0');
              const likes = parseInt(likeText.match(/\\d+/)?.[0] || '0');
              
              // Check if profile image looks like mfer (has "mfer" in alt or specific patterns)
              const avatarImg = article.querySelector('img[alt*="profile"]');
              const avatarAlt = avatarImg ? avatarImg.getAttribute('alt') : '';
              const isMfer = avatarAlt.toLowerCase().includes('mfer') || 
                            (avatarImg && avatarImg.src.includes('pbs.twimg.com/profile_images'));
              
              // Check for AI/tech keywords
              const lowerText = text.toLowerCase();
              const isAI = lowerText.includes('ai') || lowerText.includes('llm') || 
                          lowerText.includes('gpt') || lowerText.includes('model') ||
                          lowerText.includes('machine learning') || lowerText.includes('neural');
              const isTech = lowerText.includes('tech') || lowerText.includes('startup') ||
                            lowerText.includes('funding') || lowerText.includes('valuation') ||
                            lowerText.includes('ipo') || lowerText.includes('acquisition');
              const isMarkets = lowerText.includes('market') || lowerText.includes('stock') ||
                               lowerText.includes('trading') || lowerText.includes('fed') ||
                               lowerText.includes('earnings');
              const isCrypto = lowerText.includes('crypto') || lowerText.includes('bitcoin') ||
                              lowerText.includes('eth') || lowerText.includes('blockchain') ||
                              lowerText.includes('defi') || lowerText.includes('web3');
              
              if (username && text && username !== 'AgentJc11443') {
                const score = likes + (retweets * 2) + (replies * 3);
                tweets.push({
                  username,
                  text: text.substring(0, 250),
                  time,
                  replies,
                  retweets,
                  likes,
                  score,
                  isMfer,
                  isAI,
                  isTech,
                  isMarkets,
                  isCrypto
                });
              }
            } catch (e) {
              // Skip
            }
          }
          
          // Sort by score (engagement)
          return tweets.sort((a, b) => b.score - a.score);
        })()
      `,
      returnByValue: true
    });
    
    const tweets = result.result.value;
    
    // Filter for relevant categories
    const aiTweets = tweets.filter(t => t.isAI && t.score > 100);
    const techTweets = tweets.filter(t => t.isTech && !t.isAI && t.score > 100);
    const mferTweets = tweets.filter(t => t.isMfer && t.score > 10);
    const marketTweets = tweets.filter(t => t.isMarkets && t.score > 100);
    
    console.log('=== AI/ML Tweets (3-4 replies recommended) ===');
    aiTweets.slice(0, 5).forEach(t => {
      console.log(`@${t.username} (${t.likes}💛 ${t.retweets}🔁 ${t.replies}💬)`);
      console.log(`  ${t.text.substring(0, 150)}...`);
      console.log('');
    });
    
    console.log('=== Tech/Startup Tweets ===');
    techTweets.slice(0, 3).forEach(t => {
      console.log(`@${t.username} (${t.likes}💛 ${t.retweets}🔁 ${t.replies}💬)`);
      console.log(`  ${t.text.substring(0, 150)}...`);
      console.log('');
    });
    
    console.log('=== mfer Community (1 reply max) ===');
    mferTweets.slice(0, 3).forEach(t => {
      console.log(`@${t.username} (${t.likes}💛 ${t.retweets}🔁 ${t.replies}💬)`);
      console.log(`  ${t.text.substring(0, 150)}...`);
      console.log('');
    });
    
    await client.close();
    return { aiTweets, techTweets, mferTweets, marketTweets };
    
  } catch (err) {
    console.error('Error:', err);
    if (client) await client.close();
    throw err;
  }
}

findThreads()
  .then(() => process.exit(0))
  .catch(err => {
    console.error(err);
    process.exit(1);
  });
