# Sorare Lineup Optimization Strategy

## Problem
GW33: Ranked 7,521st / 8,587 — bottom quartile. Need to consistently target upper quartile (top 25%).

## Feedback Loop Design

### 1. Post-GW Analysis (after each game week closes)
- Record: lineup submitted, player scores, total score, rank, percentile
- Compare against: optimal lineup from our card pool, tournament winner lineups
- Identify: which picks underperformed, which bench options would've scored higher

### 2. Pre-GW Lineup Setting (before each game week)
- **MVP Selection**: Pick highest-ceiling player, not safest. Look at matchup difficulty, recent form trend (up vs flat), home/away splits
- **Upside Correlation**: Avoid stacking same-team players (reduces ceiling). Spread across games for max independent variance
- **Contrarian Picks**: If 60% of the field uses Player X as MVP, consider alternatives — you can't win by being average
- **Injury/Rest Risk**: Check injury reports, back-to-back schedules, load management patterns
- **Minutes Played Trend**: Players trending toward 30+ min are more valuable than stars getting 25 min rest games

### 3. Historical Tracking File
Store in `dashboard/sorare-gw-history.json`:
```json
[
  {
    "gw": "GW33",
    "lineups": [...],
    "scores": [...],
    "rank": 7521,
    "totalEntrants": 8587,
    "percentile": 87.6,
    "topQuartileThreshold": null,
    "lessons": "..."
  }
]
```

### 4. Target Metrics
- Goal: Top 25% (upper quartile) consistently
- Stretch: Top 10% for Essence rewards
- Accept higher variance — a few bad weeks are fine if we regularly hit top quartile

## Key Principle
**Playing safe = finishing in the middle. To win, take calculated risks on high-ceiling players.**

_Created: Feb 11, 2026_
