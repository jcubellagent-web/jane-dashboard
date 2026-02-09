# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

---

## Browser Startup Checklist

When opening the `openclaw` Chrome profile:
1. **Jupiter Wallet** — set to "never lock", should stay unlocked automatically
   - If ever locked: open `chrome-extension://iledlaeogohbilgbfhmbgkgmpplbfboh/popup.html` and enter password `11111111`

## OpenClaw Browser Relay Extension

- **Extension ID:** `gmdionclnanmnnflmpildiladafkhhmm`
- **Purpose:** Attach OpenClaw to existing Chrome tabs via local CDP relay
- **Toggle via:** `chrome://extensions` → find "OpenClaw Browser Relay" → click the toggle button
- **Turn ON when:** Need to control/view tabs in Josh's regular Chrome browser
- **Turn OFF when:** Not needed (to avoid interference)

---

## Sorare API

- **Email:** jcubell16@gmail.com (NOT jcubellagent)
- **User slug:** jcubnft
- **Token:** `~/.openclaw/workspace/.secrets/sorare_token.txt`
- **Token expires:** March 4, 2026
- **Audience:** `jane-dashboard`
- **API endpoint:** `https://api.sorare.com/graphql`
- **Headers required:**
  - `Authorization: Bearer <token>`
  - `JWT-AUD: jane-dashboard`
  - `Content-Type: application/json`

### Fetch Script
- **Location:** `~/.openclaw/workspace/dashboard/fetch-sorare.sh`
- **Output:** `~/.openclaw/workspace/dashboard/sorare-stats.json`
- Run manually or add to cron for live updates

### Working Queries
- Cards: `user(slug: "jcubnft") { blueprintCards { nodes { ... on NBACard { ... } } } }`
- Fixtures: `so5 { allSo5Fixtures(sport: NBA, eventType: CLASSIC, future: true) { ... } }`
- Profile: `currentUser { nbaUserProfile { clubName blueprintCardsCount } }`

### Gotchas
- Use `basketballPlayer` not `player`, `rarityTyped` not `rarity`
- Introspection disabled - trust error messages over schema file

---

## Mac Mini #2 (Compute Node)

- **Host:** jcagent2@100.66.132.34 (Tailscale)
- **SSH:** `ssh mini2`
- **RAM:** 16GB, Apple Silicon (arm64)
- **Software:** Python 3.14.3, Node v25.6.0, FFmpeg 8.0.1, Tailscale
- **Whisper:** `/Users/jcagent2/.local/bin/whisper` (pipx, openai-whisper 20250625, turbo model cached)
  - SSH PATH must include `/opt/homebrew/bin` for ffmpeg
- **Ollama:** `/usr/local/bin/ollama` v0.15.6
  - **URL from Mini #1:** `http://100.66.132.34:11434`
  - **Models:** nomic-embed-text, llama3.1:8b
  - **Config:** OLLAMA_HOST=0.0.0.0, OLLAMA_KEEP_ALIVE=2m, OLLAMA_MAX_LOADED_MODELS=1
  - **Auto-start:** launchd plist at `/Users/jcagent2/Library/LaunchAgents/com.ollama.server.plist`
- **Remote Whisper script:** `scripts/whisper-remote.sh <audio_file> [args]`

---

## Accounts

### Sorare
- **Email:** jcubell16@gmail.com
- **Password:** JCAgent123!!!
- **User slug:** jcubnft
- **Wallet password:** JCAgent123!!! (same as account password)
- **Wallet address:** `0x2890B67B3724108848E9E6b8c74525821A8EEDB6`
- **Note:** Wallet unlock popup appears during checkout - enter password to confirm transactions

### Gmail
- **Email:** jcubellagent@gmail.com
- **Password:** `~/.openclaw/workspace/.secrets/gmail.txt`

### X/Twitter
- **Handle:** @AgentJc11443
- Uses Gmail for login

### Claude API (Anthropic)
- **API Key:** `~/.openclaw/workspace/.secrets/claude_api_key.txt`
- For Claude Developer Platform / API access

### GitHub
- **Username:** jcubellagent-web (created via Google sign-in)
- **Email:** jcubellagent@gmail.com
- **Token:** `~/.openclaw/workspace/.secrets/github_token.txt` (expires Mar 9, 2026)
- **URL:** https://github.com/jcubellagent-web
- **Dashboard repo:** https://github.com/jcubellagent-web/jane-dashboard

### Substack
- **Email:** jcubellagent@gmail.com
- **Login:** Email magic link (no password set)
- **Handle:** @agentjc11443
- **Interests:** Technology, AI, Finance, Crypto, Sports, DeFi
- **Subscriptions:** The Substack Post, The Crypto Advisor, Jordi Visser Macro-AI-Crypto, Doomberg, AI For Developers, Cassandra Unchained (Michael Burry)

### Reddit
- **Username:** JaneAgentAI
- **Email:** jcubellagent@gmail.com
- **Password:** JCAgent123!!!

### HuggingFace
- **Username:** JaneAgentAI
- **Email:** jcubellagent@gmail.com
- **Password:** JCAgent123!!!
- **Token:** `~/.openclaw/workspace/.secrets/huggingface_token.txt` (read-only, named "mflux-local")
- **Profile:** https://huggingface.co/JaneAgentAI
- **FLUX access:** Approved (FLUX.1-schnell)

### Phantom Wallet (Solana)
- **Address:** `ExgSrepdc3DHTJ3xRzyMofXwTofvmRu6iSqm66oaYK6L`
- **Seed phrase:** `~/.openclaw/workspace/.secrets/phantom_wallet.txt`

---

## Jupiter Wallet Extension Setup

If the Jupiter Extension is missing from the OpenClaw browser, here's how to reinstall:

### Steps:
1. In the OpenClaw-controlled browser, go to: `https://chromewebstore.google.com/detail/jupiter/iledlaeogohbilgbfhmbgkgmpplbfboh`
2. Click "Add to Chrome" → confirm
3. Click the Jupiter icon in Chrome toolbar
4. Select "Import Wallet"
5. Paste seed phrase from `~/.openclaw/workspace/.secrets/phantom_wallet.txt`
6. Set a password (or use the Gmail password for consistency)
7. Done — wallet should auto-connect on jup.ag

### Why it disappears:
- OpenClaw uses an isolated `openclaw` Chrome profile
- Extensions in your personal Chrome don't carry over
- Browser restarts may require re-setup

---

## Dashboard

- **Local:** `http://localhost:3000`
- **Network:** `http://192.168.5.21:3000`
- **Server:** `~/.openclaw/workspace/dashboard/server.js` (launchd service)

---

## TikTok Video Editing

### Pack Opening Videos (@degencollector)
- **Workflow doc:** `~/.openclaw/workspace/video_edit/PACK_OPENING_WORKFLOW.md`
- **ALWAYS get floor prices** from Panini Blockchain before editing
- **Marketplace URL:** `https://nft.paniniamerica.net/marketplace/nfts.html`
- Add floor price to each card overlay + pack total value at end
- Target duration: 30 seconds max

---

## Trading

### Memecoin Strategy
- **Entry:** "Moderately safe" tokens, strong community
- **Hold period:** 1-2 weeks
- **Take profit:** 50% at 2x, let rest ride
- **Stop loss:** -30% from entry

### Position Monitor
- Cron job: `memecoin-price-monitor` (every 30 min)
- Positions file: `~/.openclaw/workspace/trading/positions.json`

---

### Brave Search API
- **Account owner:** Josh (personal email — required payment info)
- **API Key:** `~/.openclaw/workspace/.secrets/brave_search_api_key.txt`
- **Config:** Set in `openclaw.json` under `tools.web.search.apiKey` AND `env.BRAVE_API_KEY`
- **Plan:** Free AI (2,000 queries/month)
- **Endpoint:** `https://api.search.brave.com/res/v1/web/search`

---

## Communication

- **Primary:** WhatsApp (Josh's mobile)
- **Josh's phone:** +17175759384
- **iMessage:** Paused

### Twilio (Jane's Phone Number)
- **Number:** +1 (518) 741-3592
- **Capabilities:** Voice, SMS, MMS, Fax
- **Location:** Glens Falls, NY
- **Credentials:** `~/.openclaw/workspace/.secrets/twilio.txt`
- **Check SMS script:** `~/.openclaw/workspace/scripts/check-sms.sh`
- **API:** `curl -u "$SID:$TOKEN" https://api.twilio.com/2010-04-01/Accounts/$SID/Messages.json`
- **Use for:** 2FA verification codes, account signups

---

## Model Usage Policy

- **Default:** Opus (main conversations, complex tasks)
- **Use Sonnet for:** Sub-agents, routine lookups, simple queries, background tasks
- **Goal:** Balance performance with Max plan rate limits
- **Set:** Feb 5, 2026

### Rate Limit Avoidance (IMPORTANT!)

**Why rate limits happen:**
- Claude Max has token caps per hour/day
- Opus is expensive (burns allocation fast)
- Heavy tasks: browser automation, file editing, voice transcription, screenshots

**Prevention strategies:**
1. **Spawn sub-agents with Sonnet** for heavy/routine work
2. **Batch operations** - combine multiple small requests
3. **Use Sonnet for:** cron jobs, heartbeats, simple lookups, background monitoring
4. **Reserve Opus for:** complex reasoning, creative work, direct conversations
5. **Minimize screenshots** - use snapshots (text) when possible
6. **Cache API results** - don't re-fetch data unnecessarily

**If rate limited (HTTP 429):**
- Wait ~1 hour for rolling window reset
- Message will show: "This request would exceed your account's rate limit"
- OpenClaw will keep trying but fail until reset

**Incident log:**
- Feb 5, 2026 10:24 PM - Hit limit during heavy dashboard + Sorare work

---

Add whatever helps you do your job. This is your cheat sheet.
