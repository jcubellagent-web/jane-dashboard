# News Sources Research for @AgentJc11443
*Compiled: 2026-02-10*

## 1. RSS Feeds & Newsletters (Free, No Paywall)

### AI News
| Source | RSS/URL | Covers | Why Valuable | Access |
|--------|---------|--------|-------------|--------|
| **The Batch (deeplearning.ai)** | `https://www.deeplearning.ai/the-batch/` | Weekly AI news digest by Andrew Ng | Authoritative, covers research + industry | Email signup, scrape archive |
| **MarkTechPost** | `https://www.marktechpost.com/feed/` | AI/ML research papers in digestible format | Covers papers 12-24h before mainstream media | RSS |
| **The Decoder** | `https://the-decoder.com/feed/` | AI news, model releases, company moves | Fast coverage of model launches | RSS |
| **AI News (artificialintelligence-news.com)** | `https://www.artificialintelligence-news.com/feed/` | Enterprise AI, policy, launches | Good for regulatory/policy angle | RSS |
| **VentureBeat AI** | `https://venturebeat.com/category/ai/feed/` | AI enterprise, funding, launches | Often breaks funding news early | RSS |
| **Import AI (Jack Clark)** | `https://importai.substack.com/feed` | Weekly AI research + policy newsletter | Jack Clark = co-founder Anthropic, insider perspective | RSS/Substack |
| **The Information** | N/A (paywalled) | Skip — paywalled | — | — |
| **Interconnects (Nathan Lambert)** | `https://www.interconnects.ai/feed` | RLHF, training methods, model evals | Deep technical AI analysis, often ahead of news | RSS/Substack |

### Market / Finance
| Source | RSS/URL | Covers | Why Valuable | Access |
|--------|---------|--------|-------------|--------|
| **Unusual Whales** | `https://unusualwhales.com/` | Options flow, congressional trades, market news | Real-time unusual options activity | Scrape/X account |
| **Finviz News** | `https://finviz.com/news.ashx` | Aggregated financial news | Fast headline aggregation | Scrape |
| **Yahoo Finance RSS** | `https://finance.yahoo.com/news/rssindex` | Market news | Free, broad coverage | RSS |

### Crypto
| Source | RSS/URL | Covers | Why Valuable | Access |
|--------|---------|--------|-------------|--------|
| **The Block** | `https://www.theblock.co/rss.xml` | Crypto industry, M&A, regulation | Breaks crypto deals/partnerships early | RSS |
| **CoinDesk** | `https://www.coindesk.com/arc/outboundfeeds/rss/` | Crypto markets, regulation | Industry standard | RSS |
| **Decrypt** | `https://decrypt.co/feed` | Crypto/web3 news | Consumer-friendly, fast | RSS |

### M&A / Deals / Funding
| Source | RSS/URL | Covers | Why Valuable | Access |
|--------|---------|--------|-------------|--------|
| **Crunchbase News** | `https://news.crunchbase.com/feed/` | Startup funding, M&A | Breaks funding rounds early | RSS |
| **TechCrunch** | `https://techcrunch.com/feed/` | Startup funding, product launches | Still first on many funding announcements | RSS |
| **PitchBook Blog** | `https://pitchbook.com/blog/rss` | VC/PE deals, market data | Institutional-grade deal coverage | RSS |

---

## 2. X Accounts to Monitor for Breaking News

### AI-Specific
- **@AnthropicAI** — Official Anthropic announcements
- **@OpenAI** — Official OpenAI
- **@GoogleDeepMind** — Google AI research
- **@xaboratory** / **@xaboratory** — xAI official
- **@AIatMeta** — Meta AI official
- **@_akhaliq** — Posts new papers from arXiv FAST (often first on X)
- **@DrJimFan** — NVIDIA senior researcher, great AI takes
- **@svpino** — ML engineering, practical AI
- **@EMostaque** — Stability AI, industry insider
- **@bindureddy** — AbacusAI CEO, posts benchmarks/evals early
- **@kaborium** — AI news aggregator
- **@AravSrinivas** — Perplexity CEO, industry moves
- **@sama** — Sam Altman, OpenAI CEO
- **@demaborosh** — AI research paper highlights

### Markets / Finance
- **@unusual_whales** — Options flow, congress trades
- **@DeItaone** — Breaking financial news (fastest on X)
- **@Fxhedgers** — Macro/markets breaking news
- **@zabornikov** — Market structure
- **@WallStJesus** — Market commentary
- **@MarketWatch** — Market headlines

### Crypto
- **@WatcherGuru** — Breaking crypto news, very fast
- **@whale_alert** — Large on-chain transactions
- **@lookonchain** — On-chain analytics
- **@EmberCN** — Whale wallet tracking

### M&A / Deals
- **@DealBook** — NYT Dealbook, M&A coverage
- **@MergerArbitrage** — M&A deal tracking

---

## 3. Data APIs (Free Tier)

| API | URL | Covers | Free Tier | Why Add It |
|-----|-----|--------|-----------|-----------|
| **SEC EDGAR API** | `https://efts.sec.gov/LATEST/` | SEC filings (8-K, 10-Q, S-1) | Completely free, 10 req/sec | Catch IPO filings, M&A disclosures BEFORE news breaks |
| **Federal Reserve FRED** | `https://fred.stlouisfed.org/docs/api/fred/` | Economic indicators | Free w/ API key | Macro context (rates, CPI, GDP) |
| **Polygon.io** | `https://polygon.io/` | Stocks, options, crypto | Free: 5 calls/min, delayed | Backup market data source |
| **Messari** | `https://messari.io/api` | Crypto fundamentals, metrics | Free tier available | Better crypto analytics than CoinGecko |
| **DeFi Llama** | `https://defillama.com/docs/api` | TVL, DeFi protocols, yields | Completely free, no key needed | DeFi metrics, protocol tracking |
| **CryptoCompare** | `https://min-api.cryptocompare.com/` | Crypto prices, social stats | Free: 100K calls/mo | Social sentiment data for crypto |
| **NewsAPI.org** | `https://newsapi.org/` | News headlines from 150K sources | Free: 100 req/day (dev) | Aggregate headlines, keyword monitoring |
| **GitHub API** | `https://api.github.com/` | Repo activity, releases | Free: 60 req/hr unauth | Track model releases (llama, whisper, etc.) |

---

## 4. Niche / Edge Sources (Most AI Bots Miss These)

### Research Papers — Be First on Breakthroughs
- **arXiv RSS** — `http://arxiv.org/rss/cs.AI` + `cs.CL` + `cs.LG`
  - New papers drop ~6PM ET daily. Monitor for papers by Anthropic/OpenAI/Google/Meta authors
  - Edge: Most accounts wait for Twitter discussion; scrape arXiv directly
- **Hugging Face Daily Papers** — `https://huggingface.co/papers`
  - Curated trending papers, often surface important work same-day
- **Google Scholar Alerts** — Set alerts for "large language model", "AI safety", company names
  - Email alerts for new publications

### Regulatory / Government — Nobody Watches These
- **SEC EDGAR Full-Text Search** — `https://efts.sec.gov/LATEST/search-index?q=%22artificial+intelligence%22`
  - Search for AI mentions in SEC filings. Catches: new AI products in 10-K, AI acquisitions in 8-K
- **FTC Press Releases** — `https://www.ftc.gov/news-events/feeds`
  - AI regulation, antitrust actions against tech companies
- **EU AI Act Updates** — `https://artificialintelligenceact.eu/`
  - European AI regulation moves
- **USPTO Patent Search** — `https://patentsview.org/apis`
  - Track AI patent filings by major companies (early signal of product direction)
- **Federal Register** — `https://www.federalregister.gov/api/v1/`
  - Free API. Track AI-related executive orders, proposed rules

### Startup Funding — Breaking Rounds Before Press
- **Crunchbase Daily** — Email newsletter, free
- **SEC Form D Filings** — `https://efts.sec.gov/LATEST/search-index?q=&forms=D`
  - Companies must file Form D when raising private capital. You can catch funding rounds BEFORE the press release
- **Y Combinator Launch** — `https://www.ycombinator.com/launches`
  - New YC companies launch here first
- **Product Hunt** — `https://api.producthunt.com/v2/api/graphql`
  - New AI products launch here; free GraphQL API

### On-Chain / Crypto Edge
- **Etherscan API** — `https://api.etherscan.io/` (free key)
  - Track smart contract deployments, whale wallets
- **Nansen** — Paywalled but their free X account (@naborilsen) posts good alpha
- **Token Unlocks** — `https://token.unlocks.app/`
  - Track upcoming token unlock schedules (price-moving events)

---

## 5. Implementation Priority

### Quick Wins (add this week)
1. **arXiv RSS** for cs.AI + cs.CL — first on research papers
2. **SEC EDGAR API** — catch filings before news
3. **@DeItaone** + **@_akhaliq** on X — fastest breaking news accounts
4. **DeFi Llama API** — free, no key, instant crypto data
5. **TechCrunch + Crunchbase RSS** — funding rounds

### Medium-Term (next 2 weeks)
6. **Federal Register API** — AI policy monitoring
7. **GitHub API** — track model repo releases
8. **NewsAPI.org** — aggregate headline scanning
9. **Import AI + Interconnects** newsletters — expert AI analysis
10. **SEC Form D monitoring** — catch private funding rounds

### Stretch Goals
11. Build arXiv paper summarizer (auto-detect papers by major lab authors)
12. SEC filing keyword alerter (8-K filings mentioning "AI", "acquisition")
13. GitHub release watcher for key repos (meta-llama, openai, google-deepmind)

---

## 6. Access Method Summary

| Method | Sources |
|--------|---------|
| **RSS (fetch periodically)** | arXiv, MarkTechPost, The Decoder, TechCrunch, Crunchbase, CoinDesk, The Block, VentureBeat |
| **API (free key)** | SEC EDGAR, FRED, DeFi Llama, Polygon, NewsAPI, GitHub, Etherscan |
| **X monitoring** | @DeItaone, @_akhaliq, @WatcherGuru, @whale_alert, @unusual_whales |
| **Email/Newsletter** | Import AI, Interconnects, Crunchbase Daily, The Batch |
| **Scrape** | Finviz, HuggingFace Papers, YC Launches, Token Unlocks |
