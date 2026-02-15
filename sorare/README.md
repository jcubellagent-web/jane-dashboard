# Sorare NBA Analytics Engine

Data-driven player projection system for optimizing Sorare NBA fantasy lineups.

## 🎯 Project Goal
Map real NBA statistics to Sorare fantasy points to make intelligent lineup decisions instead of relying on intuition.

## 📁 Files

### Documentation
- **`scoring-system.md`** - Complete breakdown of how Sorare NBA scoring works
- **`nba-stats-apis.md`** - Free NBA data sources and API documentation
- **`roster-analysis.md`** - Strategic analysis of our collection and improvement areas
- **`README.md`** - This file

### Data
- **`our-collection.json`** - All 254 NBA cards in our collection (186 unique players)
- **`player-projections.json`** - Fantasy point projections (sample data, needs full run)

### Scripts
- **`fetch-collection.js`** - Query Sorare GraphQL API for our card collection
- **`player-projections.py`** - Fetch NBA stats and calculate Sorare fantasy projections
- **`lineup-optimizer.py`** ⭐ - **Main optimizer** - Recommend optimal 5-player lineups by rarity
- **`schedule-checker.py`** - Check which players have games in the current game week
- **`market-value.py`** - Analyze market opportunities for undervalued cards

## 🏀 Scoring System Summary

### Base Points
- **Points**: +1.0 per point scored
- **Assists**: +2.0 per assist
- **Offensive Rebounds**: +2.0 each
- **Defensive Rebounds**: +1.2 each
- **Steals**: +3.0 each
- **Blocks**: +3.0 each
- **Turnovers**: -2.0 each
- **Missed FG**: -0.5 each
- **Missed FT**: -0.75 each

### Bonuses
- **Double-Double**: +1.0
- **Triple-Double**: +2.0 total (+1 on top of double-double)

### Key Insights
1. **Defense is valuable** - Steals/blocks worth 3x as much as points
2. **Efficiency matters** - Missing shots hurts your score
3. **Rebounds are king** - Offensive rebounds worth 2x points, defensive 1.2x
4. **Assists > Points** - Playmakers score better than pure scorers

## 📊 Our Collection (Snapshot)

- **Total Cards**: 254 NBA cards
- **Unique Players**: 186
- **Rarity Breakdown**:
  - Common: 195 (77%)
  - Limited: 59 (23%)
  - Rare+: 0 (need to acquire for premium leagues)

## 🔧 How to Use

### Quick Start (Recommended Workflow)

#### 1. Fetch Latest Collection
```bash
node fetch-collection.js > our-collection.json
```

#### 2. Check Game Schedule
```bash
python3 schedule-checker.py
```
**Output**: Shows which players have games this week, grouped by number of games. Saves to `schedule-report.json`.

#### 3. Run Lineup Optimizer ⭐
```bash
python3 lineup-optimizer.py
```
**Output**: 
- Fetches last 10 games for each player with upcoming games
- Calculates projected Sorare scores
- Factors in opponent defense, home/away, recent trends
- Recommends optimal 5-player lineups by rarity (Limited, Rare, etc.)
- Saves full results to `lineup-recommendations.json`

**Runtime**: ~2-4 minutes depending on number of players with games

#### 4. Find Market Opportunities
```bash
python3 market-value.py
```
**Output**: Identifies top performers NOT in your collection, sorted by projected value. Use this to scout undervalued cards on the market.

### Individual Tools

#### Player Projections (Legacy)
```bash
python3 player-projections.py
```
Analyzes all players in collection (even without upcoming games). Good for offseason research.

### Output Files
- **`lineup-recommendations.json`** - Optimal lineups with projections
- **`schedule-report.json`** - Game schedule for all players
- **`market-analysis.json`** - Buy targets ranked by value
- **`nba-player-ids.json`** - Cached NBA API player ID mappings (auto-generated)
- **`player-projections.json`** - Historical projection data

## 📈 Next Steps

### Immediate
- [x] Document Sorare scoring system
- [x] Catalog our 254-card collection
- [x] Build projection script framework
- [ ] Run full projections (during active NBA season)
- [ ] Analyze position gaps
- [ ] Identify top 5 budget buys under $10

### Future Enhancements
1. **Matchup Adjustments**
   - Factor in opponent defensive rating
   - Home/away splits
   - Back-to-back game fatigue

2. **Lineup Optimizer**
   - Given 5-card constraints, find optimal combos
   - Account for rarity requirements (Limited Champion league)
   - Maximize expected points while minimizing variance

3. **Market Inefficiency Scanner**
   - Compare Sorare card prices to projected fantasy points
   - Find undervalued players
   - Alert on mispriced cards

4. **Injury & News Tracker**
   - Monitor starting lineup changes
   - Track minutes distribution shifts
   - Alert on newly traded players (opportunity for mispricing)

5. **Schedule Optimization**
   - Favor players with multiple games in a game week
   - Avoid players on bye weeks or single-game weeks

## 🔑 API Keys & Credentials

- **Sorare API**: Token in `~/.openclaw/workspace/.secrets/sorare_token.txt`
- **NBA Stats API**: No key required, but needs proper headers (see `nba-stats-apis.md`)

## 🐛 Known Issues

1. **NBA Stats API Reliability**: Unofficial API can be slow or unresponsive during off-peak hours
2. **Season Dependency**: Projections require active NBA season with recent game data
3. **All-Star Break**: Current timing (Feb 14) is during All-Star break - API may have limited recent data

## 💡 Strategy Tips

### For Limited Champion Leagues
- Mix 1 elite scorer (35+ avg) + 2 solid (25-30) + 2 high-floor budget (20+)
- Always include one elite rebounder (centers are undervalued)
- Prioritize consistency over boom-or-bust

### Budget Buys to Target
1. **Backup centers on bad teams** - High minutes, lots of rebounds
2. **3-and-D wings** - Consistent points + steals
3. **Defensive specialists** - Market undervalues steals/blocks (3.0 points each!)
4. **High-assist point guards** - 8+ assists = 16 fantasy points alone

### Market Inefficiencies
- Newly traded players (market hasn't adjusted to new role)
- Post-injury returns (underpriced until they prove health)
- Defensive-first players (Sorare scoring loves steals/blocks more than casual fans realize)

---

**Created**: 2026-02-14  
**Status**: Foundation complete, ready for active season analysis  
**Next Run**: During NBA regular season (post All-Star break)
