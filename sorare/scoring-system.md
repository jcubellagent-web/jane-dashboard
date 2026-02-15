# Sorare NBA Scoring System

## Overview
Sorare NBA uses an **action-based scoring system** where every event on the basketball court translates into fantasy points. The highest game score for each player in a submitted lineup across all games in a given game week counts toward your team total.

## Base Scoring (Per Game)

### Offensive Stats
- **Points Scored**: +1.0 per point
- **Assists**: +2.0 per assist
- **Offensive Rebounds**: +2.0 per offensive rebound
- **Defensive Rebounds**: +1.2 per defensive rebound

### Defensive Stats
- **Steals**: +3.0 per steal
- **Blocks**: +3.0 per block

### Negative Stats
- **Turnovers**: -2.0 per turnover
- **Missed Field Goals**: -0.5 per miss
- **Missed Free Throws**: -0.75 per miss

### Milestone Bonuses
- **Double-Double**: +1.0 bonus (10+ in any two stat categories: points, rebounds, assists, steals, blocks)
- **Triple-Double**: +1.0 bonus (on top of double-double bonus, so +2.0 total)

## Scoring Formula (Estimated)
Based on typical NBA fantasy systems, the approximate formula is:

```
Score = (Points × 1.0) 
      + (Assists × 2.0)
      + (Off Rebounds × 2.0) 
      + (Def Rebounds × 1.2)
      + (Steals × 3.0)
      + (Blocks × 3.0)
      - (Turnovers × 2.0)
      - (FG Missed × 0.5)
      - (FT Missed × 0.75)
      + Double-Double Bonus (+1)
      + Triple-Double Bonus (+1, in addition to double-double)
```

## Game Week Mechanics
- **Multiple Games**: If a player has multiple games in a game week, only the **highest scoring game** counts
- **Lineup Slots**: 5 players per lineup (standard positions vary by league)
- **Rarity Matters**: Higher rarity cards may have score multipliers in certain leagues

## Key Notes
- **Action-Based**: Every play matters (unlike stat-line only systems)
- **Efficiency Rewards**: Making shots is rewarded, missing shots is penalized
- **Defensive Value**: Steals and blocks are highly valued (3x points)
- **Turnover Penalty**: Ball security matters (-2 per turnover)
- **Milestone Bonuses**: Small bonuses for exceptional games

## Data Sources for Projection
To project Sorare scores from real NBA stats, we need:
1. **Box Score Stats**: Points, rebounds, assists, steals, blocks, turnovers
2. **Shooting Stats**: FG attempts, FG made, FT attempts, FT made
3. **Rebound Breakdown**: Offensive vs defensive rebounds
4. **Game Context**: Home/away, opponent defensive rating, back-to-back games

## Projection Strategy
1. Fetch last 10 game logs for each player
2. Calculate average fantasy score per game
3. Weight recent games more heavily
4. Adjust for:
   - Opponent defensive rating (harder matchups = lower projection)
   - Home/away splits
   - Rest days (back-to-back = fatigue penalty)
   - Injury status
5. Output: projected score, floor (10th percentile), ceiling (90th percentile), consistency (std dev)

---

**Note**: The exact scoring coefficients may vary slightly from Sorare's actual implementation. This is based on typical NBA fantasy scoring systems and community reverse-engineering. For precise calculations, monitor actual Sorare game scores vs NBA box scores to calibrate the formula.

**Last Updated**: 2026-02-14
