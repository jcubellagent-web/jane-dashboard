# Sorare NBA Navigation Guide

## Key URLs

### Main Pages
- **Home**: `https://sorare.com/nba/home` (Pickers, Live scores, Upcoming GW)
- **Play Overview**: `https://sorare.com/nba/play` (Default to Pro tab)
- **My Cards**: `https://sorare.com/nba/my-cards/cards` (Gallery view)
- **My Cards (Limited)**: `https://sorare.com/nba/my-cards/cards/limited`
- **Market**: `https://sorare.com/nba/market`
- **Scores**: `https://sorare.com/nba/scores` (Live scores, game center)

### Competition URLs (Direct Links)
```
# Current GW Lineups (all tiers)
https://sorare.com/nba/play/classic/{gw-slug}/lineups

# Specific Competition Tier
https://sorare.com/nba/play/classic/{gw-slug}/competition/{gw-slug}~competition~champion
https://sorare.com/nba/play/classic/{gw-slug}/competition/{gw-slug}~competition~contender  
https://sorare.com/nba/play/classic/{gw-slug}/competition/{gw-slug}~competition~challenger
```

### URL Patterns
- Game week slugs: `nba-{start_day}-{end_day}-{month}-{year}` or `nba-{day}-{day}-{month}-{year}`
- Example: `nba-7-8-feb-2026` = Feb 7-8, 2026
- Cross-month: `nba-31-jan-2-feb-2026`

---

## Page Structure

### Play Page (`/nba/play`)
- **Tabs**: Pro | Arena | Set
- **Sub-tabs**: Daily | Biweekly
- **Game Week Selector**: Scrollable horizontal list with GW numbers, dates, countdown timers
- **Competition Cards**: Click Champion/Contender/Challenger icons to go directly to those competitions

### Competition Tiers
| Tier | Cards Required | Cap | MVP Excluded from Cap | Prize Type |
|------|---------------|-----|----------------------|------------|
| Champion | 5x Limited | 120 pts | Yes | Cash ($) |
| Contender | 5x Common | 120 pts | No | XP |
| Challenger | 5x Limited | 140 pts | Yes | Cards (Star/Tier 1-3) + XP |

### Lineup Card Actions
- **"Level Up"** button: Upgrade card XP
- **"Clear Team"** / **"Delete"** button: Remove lineup
- **"Edit Lineup"** button: Open lineup editor

### Home Page Features
- **Top Lineups**: Shows best-performing current lineup with live scores
- **Missions Section** (see below)
- **Scores Widget**: Live game scores, upcoming games
- **My Circle**: Friend/rival tracking
- **Upcoming GW**: Countdown timer + quick links to Champion/Contender/Challenger
- **For You**: Quick links to Play Today, Next GW, Scouting Center

---

## Daily Missions (Home Page)

### Daily Picker
- **Objective**: Pick player to outperform L10 by 7+ pts AND score min 20 fantasy pts
- **Slots**: 3 picks
- **Reward**: 100 XP per successful pick
- **Resets**: Daily with new games

### Sharpshooter Picker
- **Objective**: Pick player to make 3+ three-pointers
- **Slots**: 3 picks
- **Reward**: 25 Essence per successful pick, 250 Essence bonus if all 3 hit
- **Note**: Players used in one picker are LOCKED from the other

---

## My Cards Page

### Tabs
- **Gallery**: Card collection view (default)
- **Collections**: ??? (TBD)
- **Vault**: Locked cards for boost bonuses

### Gallery Features
- **Card Count Display**: Shows Common/Limited counts (e.g., "171" Common, "39" Limited)
- **Vault Progress**: Shows level + progress bar (e.g., "Limited Vault LVL 2 80/150")
- **Boost Display**: Current boost % and next level boost %

### Filters Available
- **Scarcity Toggle**: Click Common/Limited count to filter
- **In-Season / All**: Filter by current season cards
- **Cards on sale**: Show only listed cards
- **Not in lineup**: Show available cards
- **Season**: Filter by card year
- **Team**: Filter by NBA team
- **Playing Game Day**: Filter players with games today
- **Ten Game Average**: Sort/filter by L10
- **Position**: G/F/C
- **Card Level**: XP level
- **Card edition**: Regular/special editions

### Card Status Badges
- **OUT**: Player will not play (skip them!)
- **GTD**: Game Time Decision (risky pick)
- **No badge**: Expected to play

### Card Info Displayed
- Player name
- Team
- L10 average (cost for cap)
- Card level bonus ("+7%", "+8%", etc.)
- Market price (if listed)
- Acquisition date/type ("Crafted", "Bought")

---

## Scores Page

### Tabs
- **Games**: Game-by-game view with live scores
- **Top players**: Player leaderboard

### Features
- **Date Selector**: Scrollable horizontal dates
- **My Cards Filter**: Show only your players' scores
- **Live Game Display**: Shows current quarter, score, fantasy points for your players
- **Upcoming Games**: Start times for unstarted games

---

## Automation-Friendly Patterns

### Checking Deadline
1. Go to `/nba/play/classic/{current-gw-slug}/lineups`
2. Look for countdown timer (e.g., "1d 22h")
3. Or check Home page → Upcoming GW section

### Checking All Competition Status
1. **Quick view**: Home page shows Upcoming GW with links to all 3 tiers
2. **Detailed view**: Go to lineups page, see lineup cards for each tier
3. **URL Pattern**: Replace `champion` with `contender` or `challenger` in URL

### Checking Player Injury Status
1. **Best method**: My Cards page → shows OUT/GTD badges directly on cards
2. **Alternative**: Scores page → "My Cards" filter
3. **In lineup builder**: Status badges show on player selection

### Setting Lineups
1. Navigate to competition page or lineups overview
2. Click "Team 1", "Team 2", etc. or "Set my Lineup" / "Edit my Team"
3. Select MVP first (excluded from cap in Champion/Challenger)
4. Add 4 more players within cap limit
5. Click "Confirm Lineup"

### Batch Workflow for Weekly Setup
1. Check injury report on My Cards page first
2. Open each competition tier via direct URLs
3. Set lineups starting with Champion (most restrictive)
4. Use same core players across lineups where cap allows

---

## User Profile Stats (jcubnft)

### Current Balances
- XP: 1.9K
- Essence: 1.1K
- Tickets: 5
- Cash: $41
- ETH: 0.0003

### Card Collection
- Common: 171
- Limited: 39
- Limited Vault: Level 2 (80/150), +2% boost (+3% at Level 3)

### Notable Limited Cards
| Player | Cost (Cap) | Bonus | Status | Value |
|--------|-----------|-------|--------|-------|
| Nikola Jokić | 60 | +10% | OK | $206 |
| SGA | 49 | +11% | OUT | $172 |
| Anthony Edwards | 47 | +5-8% | OK | $18-25 |
| Jaylen Brown | 47 | +10% | OUT | $47 |
| Cooper Flagg | 41 | +10-11% | OK | $85-118 |
| Brandon Miller | 38 | +9% | OK | - |
| Saddiq Bey | 37 | +9% | OK | - |
| Zion Williamson | 34 | +8% | OK | $52 |
| Payton Pritchard | 31 | +9-10% | OK | $68 |
| Derrick White | 30 | +9-11% | OK | $37-53 |
| Deandre Ayton | 27 | +8% | OK | - |

---

## API Notes (Limited Use)

- GraphQL endpoint: `https://api.sorare.com/graphql`
- Can query cards, fixtures, user profile, scores
- **Cannot set lineups via API** (permission/authentication issues)
- Must use browser automation for lineup management

---

## Common Issues & Solutions

### 500 errors on Arena tab
- Intermittent server issue, retry later

### Cards slow to load in gallery
- Normal behavior, they load progressively

### Picker game selection not working
- Click directly on the numbered slot button

### Can't find current GW
- Home page always shows next upcoming GW with countdown
- Play page highlights current/next GW in selector
