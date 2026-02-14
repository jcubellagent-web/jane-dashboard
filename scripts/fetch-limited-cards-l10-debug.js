#!/usr/bin/env node
/**
 * Debug Limited NBA cards fetch
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
  const json = await response.json();
  console.log('Full response:', JSON.stringify(json, null, 2));
  return json;
}

async function main() {
  const gql = `{
    user(slug: "jcubnft") {
      cards(first: 5, sport: NBA, rarities: [limited]) {
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

  await query(gql);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
