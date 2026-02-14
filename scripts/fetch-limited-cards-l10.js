#!/usr/bin/env node
/**
 * Fetch all Limited NBA cards for jcubnft with L10 averages
 * Usage: node fetch-limited-cards-l10.js
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
                lastFifteenSo5Scores: stats(gameWeek: 0) {
                  last15AverageScore
                  last10AverageScore
                  last5AverageScore
                  averageScore
                }
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
    const data = result.data.user.cards;
    
    cards.push(...data.nodes);
    hasNext = data.pageInfo.hasNextPage;
    cursor = data.pageInfo.endCursor;
    
    console.error(`Fetched ${cards.length} Limited cards so far...`);
  }

  return cards;
}

async function main() {
  console.error('Fetching all Limited NBA cards with L10 averages...');
  const cards = await getAllLimitedCards();
  
  // Transform to simpler format
  const transformed = cards.map(card => ({
    player: card.basketballPlayer.displayName,
    playerSlug: card.basketballPlayer.slug,
    team: card.anyTeam.name,
    teamSlug: card.anyTeam.slug,
    serialNumber: card.serialNumber,
    season: card.seasonYear,
    l10Avg: card.basketballPlayer.lastFifteenSo5Scores?.last10AverageScore || 0,
    l5Avg: card.basketballPlayer.lastFifteenSo5Scores?.last5AverageScore || 0,
    l15Avg: card.basketballPlayer.lastFifteenSo5Scores?.last15AverageScore || 0,
    seasonAvg: card.basketballPlayer.lastFifteenSo5Scores?.averageScore || 0,
  }));

  // Sort by L10 average descending
  transformed.sort((a, b) => b.l10Avg - a.l10Avg);

  console.log(JSON.stringify(transformed, null, 2));
  console.error(`\nTotal Limited cards: ${transformed.length}`);
  console.error(`Top 10 by L10 average:`);
  transformed.slice(0, 10).forEach((c, i) => {
    console.error(`${i+1}. ${c.player} (${c.team}) - L10: ${c.l10Avg.toFixed(1)}`);
  });
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
