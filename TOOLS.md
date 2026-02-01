# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

---

## Accounts

### Gmail
- **Email:** agentjc11443@gmail.com
- **Password:** `~/.openclaw/workspace/.secrets/gmail.txt`

### X/Twitter
- **Handle:** @AgentJc11443
- Uses Gmail for login

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
