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
| FRED (St. Louis Fed) | jcubellagent@gmail.com | JCAgent123!!! / `.secrets/fred_api_key.txt` |

## VC/PE/M&A Data Sources (Connected)
- **Crunchbase News** — news.crunchbase.com (funding rounds, deal flow)
- **PitchBook News** — pitchbook.com/news (PE deals, exits, fund raises)
- **TechCrunch Venture** — techcrunch.com/category/venture
- **SEC EDGAR** — Full-text search for 8-K, S-1, DEFM14A (M&A disclosures, IPOs)
- **Fortune Term Sheet** — fortune.com/newsletter/termsheet (daily PE/VC deals recap)
- **DealBook (NYT)** — nytimes.com/section/dealbook (M&A, PE, VC scoops)
- **PE Hub** — pehub.com (PE transactions)
- **Axios Pro Rata** — axios.com/pro-rata (deals roundup)
- **Reuters M&A** — reuters.com/markets/deals
- **DeFi Llama Raises** — defillama.com/raises (crypto/web3 funding rounds, real-time)
- **CB Insights** — cbinsights.com/research (AI deal tracking, funding visualizations)
- **Carta Blog** — carta.com/blog (private market valuations, secondary trends)
- **Web search** — "AI venture funding" / "private equity AI" / "tech M&A" queries

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

## News Sources (for Daily X Threads & Pre-Brief)

### API-Based Sources
1. **FRED API (Federal Reserve Economic Data)**
   - Free, API key required: `.secrets/fred_api_key.txt`
   - Script: `scripts/fetch-fred-data.sh`
   - Series: GDP, UNRATE (unemployment), CPIAUCSL (CPI), FEDFUNDS, T10Y2Y (yield curve), PAYEMS (payrolls)
   - Endpoint: `https://api.stlouisfed.org/fred/series/observations`
   - Output: `pre-brief-cache.json` under `fredData` key

2. **Hacker News API**
   - Free, no key needed
   - Script: `scripts/fetch-hn-top.sh`
   - Fetches top 10 AI/tech/crypto stories from HN front page
   - Endpoint: `https://hacker-news.firebaseio.com/v0/topstories.json`
   - Output: `pre-brief-cache.json` under `hackerNews` key

3. **HuggingFace Trending**
   - Free, no key needed
   - Script: `scripts/fetch-hf-trending.sh`
   - Top 5 trending AI models with stats (likes, downloads, tags)
   - Endpoint: `https://huggingface.co/models?sort=trending` + API
   - Output: `pre-brief-cache.json` under `huggingfaceTrending` key

4. **Product Hunt**
   - Free (requires browser or API for Cloudflare bypass)
   - Script: `scripts/fetch-producthunt.sh`
   - Top 5 AI/tech products of the day
   - Note: Currently returns empty (needs browser automation or API key)
   - Output: `pre-brief-cache.json` under `productHunt` key

### Newsletter Subscriptions (Email-based)
5. **Ben's Bites**
   - Subscribed: jcubellagent@gmail.com
   - Frequency: Tues & Thurs
   - Focus: AI news summaries, product launches, community
   - URL: bensbites.com

6. **The Neuron**
   - Subscribed: jcubellagent@gmail.com
   - Frequency: Daily
   - Focus: AI trends, tools, industry analysis
   - URL: theneurondaily.com

**Cache File:** All API sources write to `/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json`  
**Usage:** Run all fetch scripts before generating daily X threads or pre-brief reports
