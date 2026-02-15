#!/usr/bin/env node
const fs = require('fs');
const https = require('https');

const TOKEN = fs.readFileSync(`${process.env.HOME}/.openclaw/workspace/.secrets/sorare_token.txt`, 'utf8').trim();

async function query(q) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ query: q });
    const req = https.request({
      hostname: 'api.sorare.com',
      path: '/graphql',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${TOKEN}`,
        'JWT-AUD': 'jane-dashboard',
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    }, res => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(body)); } catch(e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function main() {
  const cards = [];
  let cursor = null;
  
  for (let page = 0; page < 10; page++) {
    const afterClause = cursor ? `, after: "${cursor}"` : '';
    const result = await query(`{
      user(slug: "jcubnft") {
        cards(first: 50${afterClause}) {
          nodes {
            __typename
            slug
            rarityTyped
            serialNumber
            ... on NBACard {
              basketballPlayer {
                slug
                displayName
                anyPositions
              }
              anyTeam { name }
            }
          }
          pageInfo { endCursor hasNextPage }
        }
      }
    }`);
    
    if (result.errors) {
      console.error('GraphQL errors:', JSON.stringify(result.errors, null, 2));
      break;
    }
    
    const nodes = result.data?.user?.cards?.nodes || [];
    cards.push(...nodes);
    
    console.error(`Page ${page + 1}: fetched ${nodes.length} cards (total: ${cards.length})`);
    
    if (!result.data?.user?.cards?.pageInfo?.hasNextPage) break;
    cursor = result.data.user.cards.pageInfo.endCursor;
  }
  
  console.log(JSON.stringify({ total: cards.length, cards }, null, 2));
}

main().catch(console.error);
