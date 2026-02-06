#!/usr/bin/env node
// Fetch Sorare NBA data - Premium Limited Champion focus

const fs = require('fs');
const https = require('https');

const TOKEN = fs.readFileSync(`${process.env.HOME}/.openclaw/workspace/.secrets/sorare_token.txt`, 'utf8').trim();
const OUTPUT = `${process.env.HOME}/.openclaw/workspace/dashboard/sorare-stats.json`;

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
  // Get user info and limited card count
  const userData = await query(`{
    currentUser { slug nickname sorareAddress nbaUserProfile { clubName } }
  }`);
  
  // Count limited cards specifically (paginate)
  let limitedCount = 0;
  let cursor = null;
  for (let page = 0; page < 10; page++) {
    const afterClause = cursor ? `, after: "${cursor}"` : '';
    const result = await query(`{
      user(slug: "jcubnft") {
        cards(first: 50, sport: NBA${afterClause}) {
          nodes { rarityTyped }
          pageInfo { endCursor hasNextPage }
        }
      }
    }`);
    const nodes = result.data?.user?.cards?.nodes || [];
    limitedCount += nodes.filter(c => c.rarityTyped === 'limited').length;
    if (!result.data?.user?.cards?.pageInfo?.hasNextPage) break;
    cursor = result.data.user.cards.pageInfo.endCursor;
  }
  
  // Get upcoming and current fixtures
  const fixtures = await query(`{
    so5 { allSo5Fixtures(first: 3, sport: NBA, eventType: CLASSIC, future: true) {
      nodes { slug gameWeek startDate endDate }
    }}
  }`);
  
  const fixtureNodes = fixtures.data?.so5?.allSo5Fixtures?.nodes || [];
  
  // Get detailed current fixture with lineups
  const currentSlug = fixtureNodes[0]?.slug;
  let currentFixture = null;
  
  if (currentSlug) {
    const result = await query(`{
      so5 { so5Fixture(slug: "${currentSlug}") {
        slug gameWeek startDate endDate
        so5Leaderboards {
          slug displayName so5LineupsCount
          mySo5Lineups {
            id
            so5Rankings { ranking score eligibleForReward }
            so5Appearances {
              score status
              anyCard {
                rarityTyped
                ... on NBACard { basketballPlayer { displayName } anyTeam { name } }
              }
            }
          }
        }
      }}
    }`);
    
    const fixture = result.data?.so5?.so5Fixture;
    if (fixture) {
      // Find Limited Champion leaderboard
      const limitedChampion = fixture.so5Leaderboards?.find(l => 
        l.displayName === 'Limited Champion' || l.slug?.includes('limited_champion')
      );
      
      currentFixture = {
        slug: fixture.slug,
        gameWeek: fixture.gameWeek,
        startDate: fixture.startDate,
        endDate: fixture.endDate,
        leaderboard: limitedChampion ? {
          name: limitedChampion.displayName,
          totalLineups: limitedChampion.so5LineupsCount,
          myLineups: (limitedChampion.mySo5Lineups || []).map((l, i) => ({
            id: l.id,
            number: i + 1,
            ranking: l.so5Rankings?.[0]?.ranking,
            score: l.so5Rankings?.[0]?.score || 0,
            rewardEligible: l.so5Rankings?.[0]?.eligibleForReward,
            players: (l.so5Appearances || []).map(a => ({
              name: a.anyCard?.basketballPlayer?.displayName,
              team: a.anyCard?.anyTeam?.name,
              score: a.score,
              status: a.status // scheduled, playing, final
            }))
          }))
        } : null
      };
    }
  }
  
  // Get last completed fixture
  const pastFixtures = await query(`{
    so5 { allSo5Fixtures(last: 5, sport: NBA, eventType: CLASSIC, future: false) {
      nodes { slug gameWeek startDate endDate }
    }}
  }`);
  
  let completedFixture = null;
  const pastNodes = pastFixtures.data?.so5?.allSo5Fixtures?.nodes || [];
  
  for (const f of [...pastNodes].reverse()) {
    const result = await query(`{
      so5 { so5Fixture(slug: "${f.slug}") {
        slug gameWeek startDate endDate
        so5Leaderboards {
          displayName so5LineupsCount
          mySo5Lineups {
            id
            so5Rankings { ranking score eligibleForReward }
          }
        }
      }}
    }`);
    
    const fixture = result.data?.so5?.so5Fixture;
    const limitedChampion = fixture?.so5Leaderboards?.find(l => 
      l.displayName === 'Limited Champion' || l.slug?.includes('limited_champion')
    );
    
    if (limitedChampion?.mySo5Lineups?.length > 0) {
      const lineups = limitedChampion.mySo5Lineups;
      const scores = lineups.map(l => l.so5Rankings?.[0]?.score || 0);
      if (scores.some(s => s > 0)) {
        const rankings = lineups.map(l => l.so5Rankings?.[0]?.ranking).filter(r => r);
        completedFixture = {
          slug: fixture.slug,
          gameWeek: fixture.gameWeek,
          startDate: fixture.startDate,
          endDate: fixture.endDate,
          totalLineups: limitedChampion.so5LineupsCount,
          myLineups: lineups.length,
          bestRank: Math.min(...rankings),
          totalScore: scores.reduce((a, b) => a + b, 0),
          results: lineups.map((l, i) => ({
            number: i + 1,
            ranking: l.so5Rankings?.[0]?.ranking,
            score: l.so5Rankings?.[0]?.score,
            rewardEligible: l.so5Rankings?.[0]?.eligibleForReward
          }))
        };
        break;
      }
    }
  }
  
  // Build output
  const output = {
    lastUpdated: new Date().toISOString(),
    user: {
      slug: userData.data?.currentUser?.slug,
      nickname: userData.data?.currentUser?.nickname,
      walletAddress: userData.data?.currentUser?.sorareAddress
    },
    limitedCards: limitedCount,
    currentFixture,
    nextFixtures: fixtureNodes.slice(1).map(f => ({
      slug: f.slug,
      gameWeek: f.gameWeek,
      startDate: f.startDate,
      endDate: f.endDate
    })),
    completedFixture
  };
  
  fs.writeFileSync(OUTPUT, JSON.stringify(output, null, 2));
  console.log(`Updated: ${OUTPUT}`);
  console.log(`Limited Cards: ${limitedCount}`);
  console.log(`Current GW: ${currentFixture?.gameWeek || 'none'} - ${currentFixture?.leaderboard?.myLineups?.length || 0} lineups`);
  console.log(`Last Completed: GW${completedFixture?.gameWeek || '?'} - Best #${completedFixture?.bestRank || '?'}`);
}

main().catch(console.error);
