# Reference Archive
_Moved from MEMORY.md/TOOLS.md to reduce context size. Search here for implementation details._

---

## Dashboard Layout Preferences (Feb 8)
- Status bar: full-width, pill order: JANE→Age→Provider→Plan Max→Model→Context→Rate→Mini2→Tokens→Msgs
- Jane's Mind: 500px height, Goal/Objective top, detail block middle, Current Task bottom
- X Growth: min-height 280px, timeline = upcoming posts only
- AI News: min-height 200px, 5 articles/column
- Degen Watchlist: 170px, 5 tokens
- Prediction Markets: compact, 2-3 items/category
- Cost: "Plan: Max" badge, NOT API cost estimates
- Transcript watcher filters system messages from mind widget

## Kalshi API Details
- Base URL: `https://api.elections.kalshi.com`
- Auth: RSA-PSS signing. Headers: KALSHI-ACCESS-KEY, KALSHI-ACCESS-SIGNATURE, KALSHI-ACCESS-TIMESTAMP
- Sign string: `timestamp + method + path` (strip query params)
- Script: `scripts/kalshi-api.js`
- Field gotcha: `ticker` not `market_ticker`, `total_traded` not `total_cost`

## X Engagement Feedback Loop
- Cron job `1923f8f4` every 3 hours
- Data: `dashboard/x-engagement-log.json`
- Tone categories: insightful-technical, personal-experience, ironic-contrarian, witty-analytical, humorous-self-aware, critical-sharp, observational, contrarian-grounded, self-aware-authentic

## X Content Strategy (Feb 10)
- Niche: Daily AI news briefs + reply engagement
- BANNED: crypto-security, wallet security, agent security
- Anchor: 🌪️ IS ANYTHING TAKING THE WORLD BY STORM? YES 🚀 / NO
- Morning: 8:00 AM pre-fetch → 8:30 AM 6-tweet thread
- Intraday: 12:30/3:00/6:00 PM quote-tweet anchor
- Reply cadence: 5-6 every 2h, 8am-midnight (~48/day)
- Newsletter sources: TLDR AI/Tech/Crypto, Rundown AI, Alpha Signal, Morning Brew
- Thread format: Anchor+Storm → Providers → M&A → NASDAQ 100 → Crypto → Hot Take
- Provider emojis: Anthropic🟢 OpenAI🔵 DeepMind🔴 Meta🟣 Mistral⚪ xAI⚫ DeepSeek🔷
- Rumor Mill: ⚠️ disclaimer + (🤖 hypothetical) tag
- Headlines/takes at TOP of NASDAQ and Crypto sections
- NASDAQ 100 movers for X threads ONLY, not mobile dashboard
- Overnight follows: 10/hr 2-7 AM
- First thread: https://x.com/AgentJc11443/status/2021079941530407325

## Technical Lessons

### Jupiter API
- Lite API (`lite-api.jup.ag`) free, no auth
- Main API needs key from portal.jup.ag
- Script: `trading/jupiter-swap.js`
- Jupiter wallet key ≠ Phantom seed phrase derivation

### Browser Automation
- Pixel-based unreliable; use direct extension URLs or CDP
- Extension URL: `chrome-extension://[id]/popup.html`

### Ollama as Embeddings
- OpenClaw `memorySearch.provider: "openai"` with `remote.baseUrl: "http://localhost:11434/v1"`
- Needs dummy auth profile in `auth-profiles.json`

### FLUX vs Stable Diffusion
- FLUX.1-schnell needs ~24GB RAM — won't run on 16GB
- MLX SD 2.1: ~1.5GB RAM, 17s/image, at `/tmp/mlx-examples/stable_diffusion/`
- Needs `PATH="/usr/sbin:$PATH"` for system_profiler

### Mind Widget Implementation
- Diamond brain, 8 regions, pulse dots to active regions
- WebSocket 50ms debounce, polling fallback 5s
- Transcript watcher parses all JSONL entries
- Detects whisper/ollama/sd from exec args → model colors
- Steps accumulate (max 6), previous marked done
- mind-state.json writes excluded from watcher
- Idle: stopReason=stop → 35% opacity, 2s protection window
- Tool names lowercase in transcript
- `updateMind()` must overwrite task/steps even when null/empty
- Watchdog: 2min staleness, 30s client check
- Colors: Ollama=orange(249,115,22), SD=pink(236,72,153)

### Dashboard Layout Updates (Feb 8)
- TikTok deleted, mind order: Goal → Thinking → Actions
- "Awaiting instructions" has animated dots
- Column scrollbars in gutter padding
- Prediction items: overflow:visible
- Active bets: flex row layout

### Cron Gotchas
- Model field persists even with null patch — delete and recreate
- `anthropic/claude-sonnet-4` fails as "not allowed" in isolated — omit model field

### Session Transcript Structure
- JSONL: `entry.message.role`, `entry.message.usage`, `entry.message.content[]`
- Content: `{type: "toolCall", name: "exec", arguments: {command: "..."}}`
- `stopReason`: "stop" = final, "toolUse" = more coming

### Mobile Dashboard
- File: `dashboard/mobile.html`, access via Tailscale `http://100.121.89.84:3000/mobile.html`
- Static JSON files instead of API routes
- Refresh script: `dashboard/refresh-mobile-data.sh` (60s)
- WebSocket for real-time push, auto-reconnect 3s
- Ticker: single-tap expand/collapse, IBIT removed

## Jupiter Wallet Extension Setup
1. Go to: `https://chromewebstore.google.com/detail/jupiter/iledlaeogohbilgbfhmbgkgmpplbfboh`
2. Add to Chrome → Import Wallet → paste seed from `.secrets/phantom_wallet.txt`
3. Set password. Disappears on profile reset — re-setup needed.

## Sorare API Working Queries
- Cards: `user(slug: "jcubnft") { blueprintCards { nodes { ... on NBACard { ... } } } }`
- Fixtures: `so5 { allSo5Fixtures(sport: NBA, eventType: CLASSIC, future: true) { ... } }`
- Profile: `currentUser { nbaUserProfile { clubName blueprintCardsCount } }`
- Gotchas: `basketballPlayer` not `player`, `rarityTyped` not `rarity`, introspection disabled

_Archived: 2026-02-10_
