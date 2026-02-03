#!/usr/bin/env node
/**
 * Fetches Sorare NBA data and updates sorare-stats.json
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const TOKEN_PATH = path.join(__dirname, '../.secrets/sorare_token.txt');
const OUTPUT_PATH = path.join(__dirname, 'sorare-stats.json');

function readToken() {
  return fs.readFileSync(TOKEN_PATH, 'utf8').trim();
}

// NBA team abbreviations
const TEAM_ABBRS = {
  'Atlanta Hawks': 'ATL', 'Boston Celtics': 'BOS', 'Brooklyn Nets': 'BKN',
  'Charlotte Hornets': 'CHA', 'Chicago Bulls': 'CHI', 'Cleveland Cavaliers': 'CLE',
  'Dallas Mavericks': 'DAL', 'Denver Nuggets': 'DEN', 'Detroit Pistons': 'DET',
  'Golden State Warriors': 'GSW', 'Houston Rockets': 'HOU', 'Indiana Pacers': 'IND',
  'LA Clippers': 'LAC', 'Los Angeles Clippers': 'LAC', 'Los Angeles Lakers': 'LAL',
  'Memphis Grizzlies': 'MEM', 'Miami Heat': 'MIA', 'Milwaukee Bucks': 'MIL',
  'Minnesota Timberwolves': 'MIN', 'New Orleans Pelicans': 'NOP', 'New York Knicks': 'NYK',
  'Oklahoma City Thunder': 'OKC', 'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI',
  'Phoenix Suns': 'PHX', 'Portland Trail Blazers': 'POR', 'Sacramento Kings': 'SAC',
  'San Antonio Spurs': 'SAS', 'Toronto Raptors': 'TOR', 'Utah Jazz': 'UTA',
  'Washington Wizards': 'WAS'
};

function getTeamAbbr(name) {
  return TEAM_ABBRS[name] || name?.substring(0, 3).toUpperCase() || '???';
}

function graphqlRequest(query, token) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({ query });
    const options = {
      hostname: 'api.sorare.com',
      path: '/graphql',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'JWT-AUD': 'jane-dashboard',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

async function fetchSorareData() {
  const token = readToken();
  
  // Get current fixture and lineups in one query
  const query = `query {
    currentUser {
      slug
      nickname
    }
    so5 {
      featuredSo5Fixtures(sport: NBA, first: 2) {
        slug
        displayName
        gameWeek
        startDate
        endDate
        mySo5Lineups {
          id
          so5Leaderboard { displayName }
          so5Appearances {
            captain
            score
            bonus
            anyCard {
              anyPlayer { displayName }
            }
            anyTeam { name }
            upcomingGame {
              date
              homeTeam { name }
              awayTeam { name }
            }
          }
          so5Rankings {
            score
            ranking
          }
        }
      }
    }
  }`;
  
  const result = await graphqlRequest(query, token);
  
  if (result.errors) {
    console.error('GraphQL errors:', JSON.stringify(result.errors, null, 2));
  }
  
  const user = result.data?.currentUser;
  const fixtures = result.data?.so5?.featuredSo5Fixtures || [];
  
  // Find fixture with lineups
  let fixture = fixtures.find(f => f.mySo5Lineups?.length > 0) || fixtures[0];
  let lineups = fixture?.mySo5Lineups || [];
  
  if (!fixture) {
    throw new Error('No fixture found');
  }
  
  // Find best lineup (highest score)
  const bestLineup = lineups.reduce((best, lineup) => {
    const score = lineup.so5Rankings?.[0]?.score || 0;
    const bestScore = best?.so5Rankings?.[0]?.score || 0;
    return score > bestScore ? lineup : best;
  }, lineups[0]);
  
  // Format output
  const output = {
    lastUpdated: new Date().toISOString(),
    account: user?.slug || 'jcubnft',
    game: 'NBA',
    currentLineup: bestLineup ? {
      competition: bestLineup.so5Leaderboard?.displayName || 'Unknown',
      gameWeek: fixture.displayName,
      rating: Math.round((bestLineup.so5Rankings?.[0]?.score || 0) * 100),
      capUsed: bestLineup.so5Appearances?.reduce((sum, a) => sum + Math.round((a.bonus - 1) * 100), 0) || 0,
      capLimit: 120,
      players: bestLineup.so5Appearances?.map(app => {
        const teamName = app.anyTeam?.name || '';
        const teamAbbr = getTeamAbbr(teamName);
        const isHome = app.upcomingGame?.homeTeam?.name === teamName;
        const oppName = isHome ? app.upcomingGame?.awayTeam?.name : app.upcomingGame?.homeTeam?.name;
        const oppAbbr = getTeamAbbr(oppName || '');
        return {
          name: app.anyCard?.anyPlayer?.displayName || 'Unknown',
          team: teamAbbr,
          gameTime: app.upcomingGame ? new Date(app.upcomingGame.date).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) : 'TBD',
          opponent: oppAbbr,
          avg: Math.round(app.score || 0),
          isMVP: app.captain
        };
      }) || []
    } : null,
    todaysGames: [],
    recentResults: lineups.map(l => ({
      date: fixture.displayName,
      competition: l.so5Leaderboard?.displayName || 'Unknown',
      rank: l.so5Rankings?.[0]?.ranking || 0,
      score: l.so5Rankings?.[0]?.score || 0
    })),
    upcomingGameWeek: {
      name: fixture.displayName,
      startsIn: 'Live',
      dates: `${new Date(fixture.startDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${new Date(fixture.endDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`
    }
  };
  
  return output;
}

async function main() {
  try {
    console.log('Fetching Sorare NBA data...');
    const data = await fetchSorareData();
    
    fs.writeFileSync(OUTPUT_PATH, JSON.stringify(data, null, 2));
    console.log('Updated sorare-stats.json');
    console.log(`Current lineup: ${data.currentLineup?.competition} - Score: ${data.currentLineup?.rating / 100}`);
    console.log(`Players: ${data.currentLineup?.players?.map(p => p.name).join(', ')}`);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
