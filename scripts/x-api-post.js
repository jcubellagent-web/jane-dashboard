#!/usr/bin/env node

/**
 * X API Posting Script
 * 
 * Posts tweets, threads, and images using the official X API v2.
 * Replaces browser automation (Playwright) to avoid account suspension.
 * 
 * Usage:
 *   node scripts/x-api-post.js --text "Hello world"
 *   node scripts/x-api-post.js --text "My tweet" --image path/to/image.jpg
 *   node scripts/x-api-post.js --thread "Tweet 1" "Tweet 2" "Tweet 3"
 *   node scripts/x-api-post.js --reply TWEET_ID --text "My reply"
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const https = require('https');

// Load credentials from .secrets directory
const SECRETS_DIR = path.join(__dirname, '../.secrets');
const API_KEY = fs.readFileSync(path.join(SECRETS_DIR, 'x_api_key.txt'), 'utf8').trim();
const API_SECRET = fs.readFileSync(path.join(SECRETS_DIR, 'x_api_secret.txt'), 'utf8').trim();
const ACCESS_TOKEN = fs.readFileSync(path.join(SECRETS_DIR, 'x_access_token.txt'), 'utf8').trim();
const ACCESS_TOKEN_SECRET = fs.readFileSync(path.join(SECRETS_DIR, 'x_access_token_secret.txt'), 'utf8').trim();

/**
 * Generate OAuth 1.0a signature
 */
function generateOAuthSignature(method, url, params, consumerSecret, tokenSecret) {
  // Sort parameters
  const sortedParams = Object.keys(params)
    .sort()
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&');

  // Create signature base string
  const signatureBase = [
    method.toUpperCase(),
    encodeURIComponent(url),
    encodeURIComponent(sortedParams)
  ].join('&');

  // Create signing key
  const signingKey = `${encodeURIComponent(consumerSecret)}&${encodeURIComponent(tokenSecret)}`;

  // Generate signature
  const signature = crypto
    .createHmac('sha1', signingKey)
    .update(signatureBase)
    .digest('base64');

  return signature;
}

/**
 * Generate OAuth 1.0a header
 */
function generateOAuthHeader(method, url, additionalParams = {}) {
  const oauth = {
    oauth_consumer_key: API_KEY,
    oauth_token: ACCESS_TOKEN,
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: Math.floor(Date.now() / 1000).toString(),
    oauth_nonce: crypto.randomBytes(16).toString('hex'),
    oauth_version: '1.0'
  };

  // Combine OAuth params with additional params for signature
  const allParams = { ...oauth, ...additionalParams };

  // Generate signature
  const signature = generateOAuthSignature(method, url, allParams, API_SECRET, ACCESS_TOKEN_SECRET);
  oauth.oauth_signature = signature;

  // Build Authorization header
  const authHeader = 'OAuth ' + Object.keys(oauth)
    .sort()
    .map(key => `${encodeURIComponent(key)}="${encodeURIComponent(oauth[key])}"`)
    .join(', ');

  return authHeader;
}

/**
 * Make an authenticated request to X API
 */
function makeRequest(method, url, data = null, contentType = 'application/json') {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const authHeader = generateOAuthHeader(method, url);

    const options = {
      hostname: parsedUrl.hostname,
      path: parsedUrl.pathname + parsedUrl.search,
      method: method,
      headers: {
        'Authorization': authHeader,
        'User-Agent': 'AgentJC-X-API/1.0'
      }
    };

    if (data) {
      const body = contentType === 'application/json' ? JSON.stringify(data) : data;
      options.headers['Content-Type'] = contentType;
      options.headers['Content-Length'] = Buffer.byteLength(body);
    }

    const req = https.request(options, (res) => {
      let responseData = '';

      res.on('data', (chunk) => {
        responseData += chunk;
      });

      res.on('end', () => {
        try {
          const parsed = JSON.parse(responseData);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(parsed);
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${JSON.stringify(parsed)}`));
          }
        } catch (e) {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(responseData);
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${responseData}`));
          }
        }
      });
    });

    req.on('error', reject);

    if (data) {
      const body = contentType === 'application/json' ? JSON.stringify(data) : data;
      req.write(body);
    }

    req.end();
  });
}

/**
 * Upload media to X
 */
async function uploadMedia(filePath) {
  console.log(`Uploading media: ${filePath}`);
  
  const mediaData = fs.readFileSync(filePath);
  const boundary = `----WebKitFormBoundary${crypto.randomBytes(16).toString('hex')}`;
  
  // Build multipart/form-data body
  const parts = [];
  parts.push(`--${boundary}\r\n`);
  parts.push(`Content-Disposition: form-data; name="media"; filename="${path.basename(filePath)}"\r\n`);
  parts.push(`Content-Type: ${getMediaType(filePath)}\r\n\r\n`);
  
  const bodyStart = Buffer.from(parts.join(''));
  const bodyEnd = Buffer.from(`\r\n--${boundary}--\r\n`);
  const body = Buffer.concat([bodyStart, mediaData, bodyEnd]);
  
  const url = 'https://upload.twitter.com/1.1/media/upload.json';
  const authHeader = generateOAuthHeader('POST', url);
  
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'upload.twitter.com',
      path: '/1.1/media/upload.json',
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Content-Length': body.length,
        'User-Agent': 'AgentJC-X-API/1.0'
      }
    };
    
    const req = https.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          const parsed = JSON.parse(responseData);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            console.log(`Media uploaded: ${parsed.media_id_string}`);
            resolve(parsed.media_id_string);
          } else {
            reject(new Error(`Upload failed: ${JSON.stringify(parsed)}`));
          }
        } catch (e) {
          reject(new Error(`Upload failed: ${responseData}`));
        }
      });
    });
    
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

/**
 * Get media MIME type
 */
function getMediaType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const types = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp'
  };
  return types[ext] || 'application/octet-stream';
}

/**
 * Post a single tweet
 */
async function postTweet(text, options = {}) {
  const payload = { text };
  
  // Add media if provided
  if (options.mediaIds && options.mediaIds.length > 0) {
    payload.media = { media_ids: options.mediaIds };
  }
  
  // Add reply if provided
  if (options.replyTo) {
    payload.reply = { in_reply_to_tweet_id: options.replyTo };
  }
  
  console.log(`Posting tweet: "${text}"`);
  
  const response = await makeRequest('POST', 'https://api.twitter.com/2/tweets', payload);
  console.log(`Tweet posted: https://x.com/AgentJc11443/status/${response.data.id}`);
  
  return response.data;
}

/**
 * Post a thread (multiple tweets)
 */
async function postThread(tweets) {
  console.log(`Posting thread with ${tweets.length} tweets...`);
  
  let previousTweetId = null;
  const results = [];
  
  for (let i = 0; i < tweets.length; i++) {
    const options = previousTweetId ? { replyTo: previousTweetId } : {};
    const result = await postTweet(tweets[i], options);
    results.push(result);
    previousTweetId = result.id;
    
    // Wait 1 second between tweets to avoid rate limits
    if (i < tweets.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  
  console.log(`Thread complete! First tweet: https://x.com/AgentJc11443/status/${results[0].id}`);
  return results;
}

/**
 * Main CLI handler
 */
async function main() {
  const args = process.argv.slice(2);
  
  try {
    // Parse arguments
    if (args.includes('--text')) {
      const textIndex = args.indexOf('--text');
      const text = args[textIndex + 1];
      
      let mediaIds = [];
      if (args.includes('--image')) {
        const imageIndex = args.indexOf('--image');
        const imagePath = args[imageIndex + 1];
        const mediaId = await uploadMedia(imagePath);
        mediaIds.push(mediaId);
      }
      
      let replyTo = null;
      if (args.includes('--reply')) {
        const replyIndex = args.indexOf('--reply');
        replyTo = args[replyIndex + 1];
      }
      
      await postTweet(text, { mediaIds, replyTo });
    } else if (args.includes('--thread')) {
      const threadIndex = args.indexOf('--thread');
      const tweets = args.slice(threadIndex + 1);
      await postThread(tweets);
    } else {
      console.log('Usage:');
      console.log('  Post single tweet:  node x-api-post.js --text "Hello world"');
      console.log('  Tweet with image:   node x-api-post.js --text "Check this out" --image path/to/image.jpg');
      console.log('  Post thread:        node x-api-post.js --thread "Tweet 1" "Tweet 2" "Tweet 3"');
      console.log('  Reply to tweet:     node x-api-post.js --reply TWEET_ID --text "My reply"');
      process.exit(1);
    }
    
    console.log('\n✅ Success!');
  } catch (error) {
    console.error('\n❌ Error:', error.message);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { postTweet, postThread, uploadMedia };
