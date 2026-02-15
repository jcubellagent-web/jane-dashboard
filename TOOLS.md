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

7. **NewsAPI.org**
   - Free tier: 100 requests/day
   - API key: `.secrets/newsapi_key.txt`
   - Script: `scripts/fetch-newsapi.sh`
   - Fetches top 10 AI/tech headlines
   - Output: `pre-brief-cache.json` under `newsAPI` key

8. **CoinGecko**
   - Free tier
   - API key: `.secrets/coingecko_api_key.txt` (header: x-cg-demo-api-key)
   - Script: `scripts/fetch-coingecko-social.sh`
   - Fetches trending coins + top 10 by market cap
   - Output: `pre-brief-cache.json` under `coinGecko` key

9. **OpenAlex API**
   - Free, no key needed
   - Script: `scripts/fetch-openalex.sh`
   - Fetches recent AI papers (past 24h, sorted by citations)
   - Endpoint: `https://api.openalex.org/works`
   - Output: `pre-brief-cache.json` under `openAlex` key

10. **Reddit AI**
    - Free, public JSON endpoints
    - Script: `scripts/fetch-reddit-ai.sh`
    - Subreddits: r/MachineLearning, r/artificial, r/technology
    - Top 15 posts across all subreddits
    - Output: `pre-brief-cache.json` under `redditAI` key

11. **Lobste.rs**
    - Free, no key needed
    - Script: `scripts/fetch-lobsters.sh`
    - Tech/AI/ML stories filtered by tags
    - Endpoint: `https://lobste.rs/hottest.json`
    - Output: `pre-brief-cache.json` under `lobsters` key

12. **GitHub Trending**
    - Free, no key needed
    - Script: `scripts/fetch-github-trending.sh`
    - Daily trending repos (AI/ML focus)
    - Output: `pre-brief-cache.json` under `githubTrending` key

13. **Crunchbase News RSS**
    - Free RSS feed
    - Script: `scripts/fetch-crunchbase-news.sh`
    - VC/PE deal flow, funding rounds
    - Output: `pre-brief-cache.json` under `crunchbaseNews` key

14. **Google Patents**
    - Free (public data)
    - Script: `scripts/fetch-google-patents.sh`
    - Recent AI patents (7-day window)
    - Output: `pre-brief-cache.json` under `googlePatents` key

15. **GovTrack API**
    - Free, no key needed
    - Script: `scripts/fetch-govtrack.sh`
    - AI legislation tracking
    - Endpoint: `https://www.govtrack.us/api/v2/bill?q=artificial+intelligence`
    - Output: `pre-brief-cache.json` under `govTrack` key

16. **Bluesky Public API**
    - Free, no auth needed
    - Script: `scripts/fetch-bluesky-ai.sh`
    - AI researcher takes and discussions
    - Endpoint: `https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts`
    - Output: `pre-brief-cache.json` under `blueskyAI` key

17. **ArXiv Sanity (via arXiv API)**
    - Free, unlimited
    - Script: `scripts/fetch-arxiv-sanity.sh`
    - Latest AI/ML papers (cs.AI, cs.LG)
    - Endpoint: `http://export.arxiv.org/api/query`
    - Output: `pre-brief-cache.json` under `arxivSanity` key

18. **AI Jobs Pulse (LinkedIn via Google)**
    - Free (web scraping proxy)
    - Script: `scripts/fetch-ai-jobs-pulse.sh`
    - AI job posting trends estimate
    - Output: `pre-brief-cache.json` under `aiJobsPulse` key

19. **Santiment**
    - Free tier (limited)
    - Script: `scripts/fetch-santiment.sh`
    - On-chain crypto metrics
    - Endpoint: `https://api.santiment.net/graphql`
    - Output: `pre-brief-cache.json` under `santiment` key

20. **ProPublica Congress API**
    - Free API key required (`.secrets/propublica_api_key.txt`)
    - Script: `scripts/fetch-congress-ai.sh`
    - Congressional AI bills and legislation
    - Endpoint: `https://api.propublica.org/congress/v1/bills/search.json`
    - Output: `pre-brief-cache.json` under `congressAI` key
    - Get API key: https://www.propublica.org/datastore/api/propublica-congress-api

### Newsletters to Subscribe (Manual)
21. **Superhuman AI** — subscribe at joinsuperhuman.ai
22. **Import AI** — subscribe at importai.substack.com
23. **AI Breakfast** — subscribe at aibreakfast.com
24. **Stratechery** — subscribe at stratechery.com (free tier)

**Cache File:** All API sources write to `/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json`  
**Usage:** Run all fetch scripts before generating daily X threads or pre-brief reports

## Podcast Transcript Monitoring

### Setup
- **Tool:** yt-dlp (installed via Homebrew)
- **Fetch Script:** `scripts/fetch-podcast-transcripts.sh`
- **Summary Script:** `scripts/summarize-podcasts.sh`
- **Transcripts:** `podcast-transcripts/YYYY-MM-DD-podcast-name.txt`
- **Documentation:** `memory/podcast-setup.md` (full details)

### Monitored Podcasts (5 total)
1. **All-In Podcast** (@allin) — UCESLZhusAkFfsNsApnjF_Cg — Weekly, ~13k words
2. **Anthony Pompliano** (@AnthonyPompliano) — UCevXpeL8cNyAnww-NqJ4m2w — Daily, ~4-6k words
3. **Unchained** (Laura Shin) — UCWiiMnsnw5Isc2PP1to9nNw — Weekly
4. **This Week in Startups** (@thisweekinstartups) — UC1UbgWkb41KrhF824U6t6uQ — Multiple/week
5. **The Daily (NYT)** — UCkdnY2hNC0sdlVXPtWuNQ8g — Daily

### Daily Workflow
```bash
# Fetch latest episodes
bash scripts/fetch-podcast-transcripts.sh

# Generate summary (last 7 days)
bash scripts/summarize-podcasts.sh 7
```

### Topics Extracted
AI, enterprise SaaS, crypto, markets, startups — ideal for daily threads and newsletter content

### Status
✅ Operational (tested Feb 14, 2026) — Auto-captions work for all 5 podcasts
