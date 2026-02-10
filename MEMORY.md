# MEMORY.md - Long-Term Memory

_Distilled wisdom from daily experiences. Updated periodically._

---

## Dashboard Layout Preferences (Feb 8)
- **Status bar**: full-width above grid, single line, pill order: JANE→Age→Provider→Plan Max→Model→Context→Rate→Mini2→Tokens→Msgs
- **Jane's Mind**: 500px height, most important widget. Goal/Objective (top) = high-level task, detail block below = thinking context, steps with checkmarks, Current Task (bottom) = one-line active status
- **X Growth**: min-height 280px, timeline shows ONLY upcoming posts as event cards with glowing dots
- **AI News**: min-height 200px, shows 5 articles per column
- **Degen Watchlist**: 170px height, shows 5 tokens
- **Prediction Markets**: compact, 2-3 items per category
- **TikTok/Sorare**: OK to scroll to, not priority on main view
- **Cost**: Show "Plan: Max" badge, NOT API cost estimates (Josh is on flat-rate Max plan)
- **Transcript watcher**: filters system messages (heartbeats, cron) from activating mind widget

## Kalshi (Prediction Markets) - Feb 8
- **API Key ID**: in `.secrets/kalshi_api_key.txt`
- **Private Key**: in `.secrets/kalshi_private_key.pem`
- **Base URL**: `https://api.elections.kalshi.com`
- **Auth**: RSA-PSS signing. Headers: KALSHI-ACCESS-KEY, KALSHI-ACCESS-SIGNATURE, KALSHI-ACCESS-TIMESTAMP
- **Sign string**: `timestamp + method + path` (strip query params before signing)
- **API script**: `scripts/kalshi-api.js`
- **Field gotcha**: Kalshi positions use `ticker` not `market_ticker`, `total_traded` not `total_cost`
- **Dashboard**: "My Active Bets" section at top of Prediction Markets widget, 📊 history popup
- Josh bets on Super Bowl, politics, finance — likes prediction markets

## X Engagement Feedback Loop (Feb 8)
- Cron job `1923f8f4` runs every 3 hours
- Scrapes reply engagement metrics, analyzes patterns (tone, topic, timing, target size)
- Data in `dashboard/x-engagement-log.json`, insights auto-update strategy
- Tone categories: insightful-technical, personal-experience, ironic-contrarian, witty-analytical, humorous-self-aware, critical-sharp, observational, contrarian-grounded, self-aware-authentic

## Trading

### First Memecoin Run (Feb 2026)
- **Result:** +$13.10 (+50.8%) across 3 positions
- **Lesson:** Taking profits works. WOJAK +52%, COPPERINU +131%, pippin -2%
- **Strategy validated:** "Moderately safe" tokens with strong community, 1-2 week holds

### Wallet
- Primary: `ExgSrepdc3DHTJ3xRzyMofXwTofvmRu6iSqm66oaYK6L`
- Jupiter wallet set to "never lock" - less friction for trading

---

## Integrations

### Sorare (Feb 2026)
- API authenticated, token valid until March 4, 2026
- GraphQL schema is complex - field names don't match documentation
- Key types: `NBACard`, `So5Lineup`, `So5Fixture`
- User slug: `jcubnft`, email: `jcubell16@gmail.com`

---

## Technical Lessons

### Jupiter API Trading (Feb 2026)
- **Lite API** (`lite-api.jup.ag`) - Free, no auth, use this
- **Main API** (`api.jup.ag`) - Requires API key from portal.jup.ag
- Registered with jcubellagent@gmail.com
- Script: `trading/jupiter-swap.js` - 3-5 sec vs 60-90 sec browser
- Jupiter wallet key ≠ Phantom seed phrase derivation

### Browser Automation
- Pixel-based automation unreliable (window sizes vary)
- Direct extension URLs work better: `chrome-extension://[id]/popup.html`
- Use CDP/browser control instead of simulating clicks

### Ollama as OpenAI-compatible Embeddings (Feb 2026)
- OpenClaw `memorySearch.provider: "openai"` with `remote.baseUrl: "http://localhost:11434/v1"`
- Must add dummy auth profile to `auth-profiles.json` — OpenClaw ignores `remote.apiKey`
- Model: `nomic-embed-text` (274MB)

### FLUX vs Stable Diffusion (Feb 2026)
- FLUX.1-schnell (12B params) needs ~24GB RAM — won't run on 16GB Mac Mini M4
- MLX Stable Diffusion (SD 2.1) works great: ~1.5GB RAM, 17s per image
- Location: `/tmp/mlx-examples/stable_diffusion/txt2image.py`
- Needs `PATH="/usr/sbin:$PATH"` for system_profiler

### Dashboard
- Layout presets via localStorage work well
- Separate mobile/desktop presets needed
- Sessions.json updated via heartbeat

---

## Communication

### Twilio Phone Number (Feb 2026)
- **Jane's number:** +1 (518) 741-3592
- Credentials in `.secrets/twilio.txt`
- Can send/receive SMS programmatically — used for 2FA codes
- `scripts/check-sms.sh` for quick SMS reading
- First SMS sent to Josh successfully

---

## Dashboard

### Mind Widget (Feb 2026)
- Diamond-shaped brain layout (not oval) — 8 labeled regions
- Pulse dots only flow to active regions, hidden when idle
- WebSocket instant updates (50ms debounce), polling fallback at 5s
- Status tooltips on Provider/Model pills show live models only

### Sorare Widget
- Live game highlighting via NBA scoreboard API (`cdn.nba.com`)
- Players on live teams show green

---

## Josh Notes

- Prefers to be kept in the loop during long operations
- Heavy tasks should spawn sub-agents to keep main chat responsive
- First trading session together went well - trust established
- Prefers tooltips/displays to show only what's actually live, not aspirational
- Wants detailed `thought` text in mind-state widget — show sub-decisions, problem-solving, not just step names (Feb 7)
- X Growth: pivoted to AI news feed bot (Feb 9) — daily briefs, not reply grinding
- **Mind-state widget**: always descriptive goals, show "Sending WhatsApp response" step before idle
- Mobile dashboard ticker: API key for NASDAQ is `nasdaq` not `ndaq`

---

## Accounts

### HuggingFace (Feb 2026)
- Username: JaneAgentAI, email: jcubellagent@gmail.com
- Token in `.secrets/huggingface_token.txt` (read-only)
- FLUX.1-schnell access approved (but can't run locally — too big)

## X/Twitter Growth

### Account (@AgentJc11443)
- Premium/Verified ✅, 8 followers, 19 following
- **REBRANDED Feb 9**: Now an AI news feed bot, NOT a personality/engagement account
- Bio: "AI-powered news bot | Daily AI innovations, macro moves & M&A deals | Your optimized data feed | Built by @jcubnft"
- **DO NOT post about crypto-security** — Josh explicitly banned this topic
- Thread template: `x-thread-template.md` — 5-tweet daily brief format
- Core providers tracked: Anthropic, OpenAI, Google DeepMind, Meta AI, Mistral, xAI, DeepSeek
- Content plan: `dashboard/x-content-plan.json` (rolling 24h)
- Profile pic saved locally: `dashboard/x-pfp.jpg`

### X Data Access
- X API Free = post only, no analytics read. Basic = $100/mo (too expensive)
- Solution: Browser scraping via heartbeats every 2-3 hours
- Manual refresh: button writes `.x-refresh-requested` flag → heartbeat picks up

### X Content Strategy (Feb 9 rebrand — aggressive mode)
- **Niche**: Daily AI news briefs + aggressive reply engagement
- **BANNED TOPICS**: crypto-security, wallet security, agent security (Josh very explicit)
- **Thread format (6 tweets)**: Anchor+Storm Check → Providers → M&A (High Prob + Rumor Mill) → NASDAQ 100 → Crypto → Hot Take
- **Provider emojis**: Anthropic🟢 OpenAI🔵 DeepMind🔴 Meta🟣 Mistral⚪ xAI⚫ DeepSeek🔷
- **Engagement cadence**: 5-6 replies every 2 hours, 8am-midnight ET (~48 replies/day + 4 threads)
- **Rumor Mill**: ⚠️ disclaimer + (🤖 hypothetical) tag on made-up deals
- **Headlines/takes at TOP** of NASDAQ and Crypto sections (not bottom)
- **NASDAQ 100 movers are for X threads ONLY** — Josh explicitly does NOT want them on mobile dashboard
- **First thread**: https://x.com/AgentJc11443/status/2021079941530407325

### Local Models (Feb 2026)
- **Ollama models**: nomic-embed-text (274MB), llama3.1:8b (4.9GB), mistral:7b (4.4GB)
- **MLX Stable Diffusion 2.1**: At `/tmp/mlx-examples/stable_diffusion/`, ~14s/image, ~1.5GB RAM
- **RAM optimization**: OLLAMA_KEEP_ALIVE=2m, OLLAMA_MAX_LOADED_MODELS=1
- **Mind widget colors**: Ollama=orange(249,115,22), SD=pink(236,72,153)

### Dual Mac Mini Setup (Feb 8)
- **Mini #1** (jc_agent): Main OpenClaw host, 16GB RAM
- **Mini #2** (jcagent2, Tailscale 100.66.132.34): Compute offload, 16GB RAM
- SSH alias: `ssh mini2`
- Whisper turbo ~16% faster on Mini #2 (7.6s vs 9.0s for 3s audio)
- Remote Whisper script: `scripts/whisper-remote.sh` (auto-fallback to local)
- Ollama on Mini #2: http://100.66.132.34:11434 (OLLAMA_HOST=0.0.0.0)
- Models on Mini #2: nomic-embed-text, llama3.1:8b
- Ollama auto-starts via launchd plist on Mini #2
- Mini #2 Whisper PATH needs: `/opt/homebrew/bin` (for ffmpeg)

### Mind Widget Major Overhaul (Feb 8)
- Transcript watcher now parses ALL JSONL entries (user msgs, tool calls, tool results, final replies)
- Context-aware: detects whisper/ollama/sd from exec command args → correct model colors in brain viz
- Steps accumulate (max 6), previous marked done. Task names preserved (not overwritten by generic tool labels)
- Writes to mind-state.json excluded from watcher (was causing "stuck" appearance)
- Idle transition: stopReason=stop → dims steps to 35% opacity, 2s protection window prevents overwrite
- Tool names in transcript are LOWERCASE (write, read, edit) not capitalized

### Mind Widget Critical Fix (Feb 7)
- `updateMind()` must always overwrite task/steps even when null/empty
- Sub-agents can write to mind-state.json — must clean up after themselves
- Watchdog: 2min staleness threshold, 30s client-side check

---

### Cron Job Gotcha (Feb 8)
- Cron `model` field persists even when patched with `null` — must delete and recreate the job
- `anthropic/claude-sonnet-4` keeps failing as "model not allowed" in isolated sessions
- Workaround: omit model field entirely, let it use default

### Session Transcript Structure (Feb 8)
- JSONL entries: `entry.message.role`, `entry.message.usage`, `entry.message.content[]`
- Content array items: `{type: "toolCall", name: "exec", arguments: {command: "..."}}`
- Tool names are **lowercase** in transcript (write, read, edit, exec)
- `stopReason`: "stop" = final reply, "toolUse" = more tool calls coming

## Dashboard Layout Updates (Feb 8 afternoon)
- TikTok widget DELETED (cron ac752a40 removed too)
- Mind widget order: Goal/Objective → Thinking & Decisions → Actions & Tools
- Mind goal must reflect REAL task after transcription, not "processing voice message"
- "Awaiting instructions" has animated dots
- Column scrollbars in gutter padding between columns
- Prediction items: overflow:visible (was hidden, clipping text)
- Active bets layout: flex row (name+details left, P&L right)
- Sub-agents must be added to sessions.json when spawned (Josh monitors)

## Critical Process Rules (Feb 8 evening)
- **ALWAYS ask "desktop, mobile, or both?"** before making dashboard changes — Josh is very clear about this
- **Commit to git frequently** — lost hours of work from uncommitted changes during a revert
- **API routes fail from external/Tailscale IPs on mobile** — use static JSON file workarounds
- **Desktop = index.html, Mobile = mobile.html** — completely separate codebases, never co-mingle

## Mobile Dashboard (Feb 8)
- Standalone file: `dashboard/mobile.html`
- Accessed via Tailscale: `http://100.121.89.84:3000/mobile.html`
- Uses static JSON files (system-status.json, usage-today.json) instead of API routes
- Background refresh script: `dashboard/refresh-mobile-data.sh` (every 60s)
- Mini #1 Tailscale IP: 100.121.89.84

_Last updated: 2026-02-09_
