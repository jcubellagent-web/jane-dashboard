# Lineup Optimizer Demo Output

## Current Status (Feb 14, 2026)
🏀 **NBA All-Star Break** - No games until Feb 19

## Expected Output (When Games Resume)

### Sample Run
```bash
$ python3 lineup-optimizer.py

🏀 SORARE NBA LINEUP OPTIMIZER
================================================================================

📋 Found 186 unique players in collection

🔍 Fetching NBA player database...
✅ Loaded 5,439 NBA players

📊 Fetching team defensive ratings...
✅ Loaded 30 team ratings

📅 Fetching NBA schedule...
✅ Loaded games for next 7 days

🎯 Calculating player projections...

[1/186] Keldon Johnson... ✅ Projected: 32.4 (trend: up)
[2/186] Brice Sensabaugh... ✅ Projected: 18.2 (trend: flat)
[3/186] Jusuf Nurkić... ✅ Projected: 35.1 (trend: down)
...
[186/186] Complete

================================================================================

🏆 OPTIMAL LIMITED LINEUP
--------------------------------------------------------------------------------
Player                    Team                 vs                   Proj     Floor    Ceiling
--------------------------------------------------------------------------------
Jusuf Nurkić              Utah Jazz            @ Lakers             35.1     22.3     48.7
Bam Adebayo               Miami Heat           vs Raptors           38.4     28.1     52.3
Keldon Johnson            San Antonio Spurs    @ Warriors           32.4     18.7     45.2
Payton Pritchard          Boston Celtics       vs Cavaliers         29.8     15.4     42.1
Jaylen Brown              Boston Celtics       vs Cavaliers         41.2     31.5     58.9
--------------------------------------------------------------------------------
TOTAL PROJECTED SCORE:                                              176.9
```

## How It Works

### 1. Data Collection
- Fetches last 10 game logs for each player from NBA Stats API
- Pulls team defensive ratings (opponent difficulty adjustment)
- Checks NBA schedule for upcoming games (next 7 days)

### 2. Score Calculation
For each game log, converts NBA stats → Sorare fantasy points:
```
Score = Points×1.0 + Assists×2.0 + Off.Reb×2.0 + Def.Reb×1.2 
      + Steals×3.0 + Blocks×3.0 - Turnovers×2.0 
      - Missed.FG×0.5 - Missed.FT×0.75
      + Double-Double Bonus + Triple-Double Bonus
```

### 3. Projection Adjustments
- **Recent weighting**: Last 5 games weighted higher than games 6-10
- **Opponent defense**: Multiply by (110 / opponent defensive rating)
- **Trend analysis**: Up/down/flat based on last 3 vs previous 7 games
- **Home/away**: Captured in historical data, not explicitly adjusted

### 4. Lineup Optimization
- Filters players by rarity (Limited, Rare, etc.)
- Only includes players with upcoming games
- Sorts by projected score (greedy selection)
- Returns top 5 players for each rarity tier

## Output Files

### `lineup-recommendations.json`
```json
{
  "generated_at": "2026-02-19T10:00:00",
  "players_analyzed": 142,
  "projections": [
    {
      "name": "Bam Adebayo",
      "team": "Miami Heat",
      "positions": ["basketball_center"],
      "rarity": "limited",
      "projection": {
        "projected_score": 38.4,
        "floor": 28.1,
        "ceiling": 52.3,
        "std_dev": 7.2,
        "games": 10,
        "recent_trend": "up",
        "last_5_scores": [45.2, 41.3, 38.7, 32.1, 29.8]
      },
      "upcoming_games": [
        {
          "date": "2026-02-19",
          "opponent": "Toronto Raptors",
          "home": true
        }
      ],
      "opponent_def_rating": 112.4
    }
  ]
}
```

### `nba-player-ids.json` (Auto-generated)
Maps Sorare player names → NBA Stats API player IDs:
```json
{
  "Bam Adebayo": "1628389",
  "Jaylen Brown": "1627759",
  "Keldon Johnson": "1629640"
}
```

## Rate Limiting
- NBA Stats API: 0.6s delay between requests (safe zone)
- Full collection (186 players): ~2-3 minutes to complete
- Results cached in JSON for quick re-runs

## Future Enhancements

### v2.0 - Position Constraints
Currently uses greedy selection (top 5 by score). Future version will:
- Enforce position requirements (if Sorare has them)
- Try combinations to find true optimal lineup
- Account for correlation (avoid same-team stacking)

### v3.0 - Multi-Game Week Optimization
- Players with 4 games > players with 3 games (more opportunities)
- But factor in fatigue for back-to-back-to-back games

### v4.0 - Injury Integration
- Real-time injury scraping from ESPN/Rotoworld
- GTD (game-time decision) flagging
- Automatic lineup adjustments when starters ruled out

## Testing Notes
Tested during All-Star break (Feb 14) with limited game data:
- ✅ Schedule checker: Works, correctly shows 0 games during break
- ✅ Market analyzer: Works, successfully pulled game logs for star players
- ⏸️ Lineup optimizer: Functional, but no lineups generated (no games scheduled)

**Next test**: Feb 19 when games resume
