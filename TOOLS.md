# TOOLS.md - Credentials & Setup

_How-to details and implementation notes archived in `memory/reference.md`._

---

## Browser
- Jupiter Wallet: "never lock", password `11111111`, extension `chrome-extension://iledlaeogohbilgbfhmbgkgmpplbfboh/popup.html`
- Sorare Wallet: password `JCAgent123!!!` (same as account), unlocks in `#wallet` iframe, re-locks after each purchase
- Browser Relay Extension: `gmdionclnanmnnflmpildiladafkhhmm` — toggle via `chrome://extensions`

## Accounts & Credentials

| Service | User/Email | Password/Token |
|---------|-----------|---------------|
| Sorare | jcubell16@gmail.com / jcubnft | JCAgent123!!! / wallet same |
| Sorare wallet | 0x2890B67B... | same as account |
| Gmail | jcubellagent@gmail.com | `.secrets/gmail.txt` |
| X/Twitter | @AgentJc11443 | JCAgent123!!! / `.secrets/x_password.txt` |
| Claude API | — | `.secrets/claude_api_key.txt` |
| GitHub | jcubellagent-web | `.secrets/github_token.txt` (exp Mar 9 2026) |
| Substack | jcubellagent@gmail.com | magic link |
| Reddit | JaneAgentAI | JCAgent123!!! |
| HuggingFace | JaneAgentAI | JCAgent123!!! / `.secrets/huggingface_token.txt` |
| Phantom | ExgSrepdc3... | `.secrets/phantom_wallet.txt` |
| Kalshi | — | `.secrets/kalshi_api_key.txt` + `.secrets/kalshi_private_key.pem` |
| Finnhub | — | `.secrets/finnhub_api_key.txt` |
| Alpha Vantage | — | `.secrets/alphavantage_api_key.txt` |
| CoinGecko | — | `.secrets/coingecko_api_key.txt` (header: x-cg-demo-api-key) |
| Brave Search | — | `.secrets/brave_search_api_key.txt` |
| Coinbase CDP | jcubellagent@gmail.com | `.secrets/coinbase_cdp_api_key.txt` + `.secrets/coinbase_wallet_secret.txt` |
| Twilio | +1(518)741-3592 | `.secrets/twilio.txt` |

## Sorare API
- Endpoint: `https://api.sorare.com/graphql`
- Headers: `Authorization: Bearer <token>`, `JWT-AUD: jane-dashboard`
- Token: `.secrets/sorare_token.txt` (exp March 4 2026)
- Fetch script: `dashboard/fetch-sorare.sh`

## Mac Mini #2
- SSH: `ssh mini2` (100.66.132.34)
- Whisper: `scripts/whisper-remote.sh`
- Ollama: `http://100.66.132.34:11434`

## Dashboard
- Local: `http://localhost:3000` | Network: `http://192.168.5.21:3000`
- Server: `dashboard/server.js` (launchd)

## Communication
- Primary: WhatsApp, Josh: +17175759384
- Twilio SMS: `scripts/check-sms.sh`

## Trading
- Strategy: moderately safe tokens, 1-2 week hold, 50% at 2x, stop -30%
- Monitor cron: `memecoin-price-monitor`, positions: `trading/positions.json`
- Jupiter script: `trading/jupiter-swap.js`

## TikTok Video Editing
- Workflow: `video_edit/PACK_OPENING_WORKFLOW.md`
- Get floor prices from `https://nft.paniniamerica.net/marketplace/nfts.html`

## Browser Serialization
- **Lock script:** `scripts/browser-lock.sh`
- **Rule:** Only ONE sub-agent may use the browser at a time
- Before browser work: `bash scripts/browser-lock.sh acquire "task-label" 300`
- After browser work: `bash scripts/browser-lock.sh release`
- Check status: `bash scripts/browser-lock.sh status`
- Lock uses `/tmp/openclaw-browser-lock` (mkdir-based, atomic)
- Timeout default: 300s (5 min) — adjust per task
- **Priority order:** X/Twitter tasks first, then Sorare, then other browser tasks
- API-only tasks (no browser) can run in parallel — no lock needed

## Model Usage
- Default Opus for conversations, Sonnet for sub-agents/background
- Minimize screenshots, use snapshots; cache API results
- Rate limit incident: Feb 5 10:24 PM
