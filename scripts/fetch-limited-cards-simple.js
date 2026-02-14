#!/usr/bin/env node
/**
 * Fetch all Limited NBA cards - simple version without stats
 */

const fs = require('fs');
const path = require('path');

const TOKEN = fs.readFileSync(path.join(process.env.HOME, '.openclaw/workspace/.secrets/sorare_token.txt'), 'utf8').trim();
const API_URL = 'https://api.sorare.com/graphql';

async function query(gql) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'JWT-AUD': 'jane-dashboard',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query: gql }),
  });
  return response.json();
}

async function getAllLimitedCards() {
  const cards = [];
  let cursor = null;
  let hasNext = true;

  while (hasNext) {
    const afterClause = cursor ? `, after: "${cursor}"` : '';
    const gql = `{
      user(slug: "jcubnft") {
        cards(first: 50, sport: NBA, rarities: [limited]${afterClause}) {
          nodes {
            slug
            serialNumber
            seasonYear
            ... on NBACard {
              basketballPlayer {
                displayName
                slug
              }
              anyTeam {
                name
                slug
              }
            }
          }
          pageInfo {
            endCursor
            hasNextPage
          }
        }
      }
    }`;

    const result = await query(gql);
    if (!result.data) {
      console.error('Error:', JSON.stringify(result.errors, null, 2));
      break;
    }
    const data = result.data.user.cards;
    
    cards.push(...data.nodes);
    hasNext = data.pageInfo.hasNextPage;
    cursor = data.pageInfo.endCursor;
    
    console.error(`Fetched ${cards.length} Limited cards so far...`);
  }

  return cards;
}

async function main() {
  console.error('Fetching all Limited NBA cards...');
  const cards = await getAllLimitedCards();
  
  // Transform to simpler format
  const transformed = cards.map(card => ({
    player: card.basketballPlayer.displayName,
    playerSlug: card.basketballPlayer.slug,
    team: card.anyTeam.name,
    teamSlug: card.anyTeam.slug,
    serialNumber: card.serialNumber,
    season: card.seasonYear,
    cardSlug: card.slug,
  }));

  console.log(JSON.stringify(transformed, null, 2));
  console.error(`\nTotal Limited cards: ${transformed.length}`);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
