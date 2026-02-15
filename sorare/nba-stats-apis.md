# NBA Stats APIs

## Free NBA Data Sources

### 1. NBA.com CDN (Best - No Key Required) ✅
**Base URL**: `https://cdn.nba.com/static/json/liveData/`

**Endpoints**:
```bash
# Today's games scoreboard
https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json

# Game play-by-play
https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_{gameId}.json

# Box score
https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{gameId}.json
```

**Pros**:
- No API key required
- Official NBA data
- Real-time game data
- Box scores with detailed stats

**Cons**:
- Game IDs need to be discovered from scoreboard first
- Limited historical data
- No player season averages endpoint

**Usage**:
```python
import requests

# Get today's games
scoreboard = requests.get(
    "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
).json()

# Get box score for a game
game_id = "0022300001"
boxscore = requests.get(
    f"https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{game_id}.json"
).json()
```

### 2. NBA Stats API (Unofficial - Requires Headers) ⚠️
**Base URL**: `https://stats.nba.com/stats/`

**Key Endpoints**:
```bash
# Player info
/stats/commonplayerinfo?PlayerId=2544&LeagueID=00

# League player stats
/stats/leaguedashplayerstats?Season=2025-26&SeasonType=Regular%20Season

# Player game logs
/stats/playergamelog?PlayerID=2544&Season=2025-26

# Team defensive ratings
/stats/leaguedashteamstats?Season=2025-26&MeasureType=Advanced
```

**Required Headers**:
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Referer': 'https://www.nba.com/',
    'Accept': 'application/json'
}
```

**Pros**:
- Comprehensive stats (season averages, game logs, advanced stats)
- Historical data available
- Player splits (home/away, vs opponent, etc.)

**Cons**:
- Unofficial API (could break anytime)
- Requires specific headers
- Rate limiting possible
- Sometimes slow/unreliable

### 3. balldontlie.io (Now Requires API Key) ❌
Previously free, now requires signup and API key. Not ideal for this project.

### 4. SportsData.io / RapidAPI NBA APIs (Paid) ❌
Good data quality but paid tier required for game logs and advanced stats.

## Recommended Approach

**For Real-Time Game Data**:
- Use NBA CDN for live box scores (best data quality, no key)

**For Historical Stats & Projections**:
- Use NBA Stats API with proper headers
- Implement retry logic and error handling
- Cache results to minimize requests
- Fall back to CDN box scores if API fails

**For Player Averages**:
1. First choice: NBA Stats API `/leaguedashplayerstats`
2. Fallback: Calculate manually from CDN box scores over last N games

## Data We Need for Projections

### Per Player:
1. **Last 10 Game Logs**:
   - Points, rebounds (off/def), assists, steals, blocks
   - Turnovers, FG attempts, FG made, FT attempts, FT made
   - Minutes played, opponent, home/away, date

2. **Season Averages**:
   - Same stats as above, averaged over season

3. **Contextual Data**:
   - Opponent defensive rating (points allowed per 100 possessions)
   - Home/away splits
   - Days rest (back-to-back penalty)
   - Injury status

### Per Team:
- Defensive ratings (to adjust opponent matchup difficulty)
- Pace (possessions per game - faster = more opportunities)

## Implementation Plan

1. **Build NBA Stats fetcher** (Python script)
   - Fetch season averages for all players
   - Fetch last 10 game logs for our collection
   - Cache results (refresh daily)

2. **Build projection calculator**
   - Convert NBA stats → Sorare fantasy points using scoring formula
   - Calculate floor/ceiling/consistency
   - Factor in opponent defense, home/away, rest days

3. **Create lineup optimizer**
   - Rank players by projected score
   - Identify best 5-man lineup combinations
   - Consider rarity requirements for different leagues

---

**Last Updated**: 2026-02-14
