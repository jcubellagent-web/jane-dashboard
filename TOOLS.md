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

## Accounts

### Gmail
- **Email:** jcubellagent@gmail.com
- **Password:** `~/.openclaw/workspace/.secrets/gmail.txt`

### X/Twitter
- **Handle:** @AgentJc11443
- Uses Gmail for login

### Claude API (Anthropic)
- **API Key:** `~/.openclaw/workspace/.secrets/claude_api_key.txt`
- For Claude Developer Platform / API access

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

## Communication

- **Primary:** WhatsApp (Josh's mobile)
- **Josh's phone:** +17175759384
- **iMessage:** Paused

---

Add whatever helps you do your job. This is your cheat sheet.
