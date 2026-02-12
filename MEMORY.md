# MEMORY.md - Long-Term Memory

_Distilled wisdom. Implementation details archived in `memory/reference.md`._

---

## Josh Rules (IMPORTANT)
- **INSTANT REACTION**: On EVERY message (voice or text), update mind-state.json as the VERY FIRST action — before transcription, before processing. The desktop brain must light up the moment Josh sends something.
- Ask "desktop, mobile, or both?" before dashboard changes
- Commit to git frequently — lost work from uncommitted changes before
- Keep him in the loop during long operations; spawn sub-agents for heavy tasks
- Stays up late — don't nag about sleep
- Mind-state widget: always descriptive goals, detailed `thought` text
- Mind goal must reflect REAL task, not "processing voice message"
- Desktop dashboard: neon flat SVG icons ONLY — no emojis. Terminal/hacker aesthetic.
- Decision Log replaces "Actions & Tools" — show reasoning, not just tool names
- NEVER use "layoffs" in X posts — use "restructured", "transformed", "transitioned"
- Desktop = index.html, Mobile = mobile.html — separate codebases
- API routes fail from external IPs on mobile — use static JSON files
- Mobile ticker: API key for NASDAQ is `nasdaq` not `ndaq`
- NASDAQ 100 movers for X threads ONLY, not mobile dashboard
- **NEVER auto-post ad hoc tweets** — always send draft for Josh's approval first
- **Systems thinking**: Every change must consider upstream/downstream/cross-platform impacts. No fixing one thing and breaking two others.
- **Mobile idle state**: Must consider active sub-agents, not just task != null
- **Mind-state goal specificity**: Never say "managing background process" — always describe the actual task
- Push notifications: BE AGGRESSIVE — send for every direct reply, cron completions, alerts, sub-agent results. Skip heartbeats only. Josh will say if it's too much.
- Check for active sub-agents before setting mind-state to idle

## mfer #9581
- Josh owns mfer #9581 (Sartoshi collection) — our X PFP
- OpenSea: `0x79fcdef22feed20eddacbb2587640e45491b757f/9581`, owned by JcubNFT-Vault
- mfer community engagement: 1-2 replies per X cycle, slightly looser crypto scope
- Followed: @wild_w_mfer, @0xmakaveli, @HeresMyEth (mferGPT builder)

## X/Twitter (@AgentJc11443)
- Premium ✅, ~27 followers, AI news feed bot (rebranded Feb 9)
- **BANNED TOPICS**: crypto-security, wallet security, agent security
- Content plan: `dashboard/x-content-plan.json`
- X API Free = post only; analytics via browser scraping
- Manual refresh: `.x-refresh-requested` flag → heartbeat picks up
- Strategy details: `memory/reference.md`
- Schedule: 8AM pre-fetch, 8:30AM brief, 12:30PM/4:30PM/6PM updates, 7:15PM recap
- All thread jobs do data refresh before posting (Finnhub, CoinGecko, arXiv, SEC EDGAR, etc.)
- Winning formula: technical-insightful tone, AI-product topics, 5-8PM posting window
- News sources: arXiv, SEC EDGAR, DeFi Llama, TechCrunch, @DeItaone, @_akhaliq
- Enterprise SaaS section (Tweet 3.5): MANDATORY in daily brief, tracks $CRM, $NOW, $WDAY, $PLTR, $DUOL
- Language: NEVER "layoffs"/"cuts" → use "restructured"/"streamlined"/"transformed"
- Tag companies: @salesforce, @Workday, @ServiceNow, @PalantirTech, @duolingo
- Include upcoming earnings calendar + #EnterpriseSaaS hashtag
- Economic calendar check in pre-brief cron (Finnhub API) — never miss NFP, CPI, FOMC, etc.
- Reply-to-Replies cron: 11 AM & 5 PM — engage with people who respond to our tweets
- Cron timeout lesson: dashboard sync must ALWAYS complete — add time management warnings, increase timeouts

## Coinbase Agentic Wallet
- EVM (Base): `0xe8f6f50c79d24ef271764447E46f66f1Ef4Cae8F`
- Solana: `8nqcu8QUff1sSQabnzTLUzSPS4byvoPs9m9oUrGvFJUa`
- Project ID: `7e1fcc61-d1d8-44d1-b28d-cadc353e200b`
- Funded: 2 SOL from Josh (~$158)
- CDP SDK: `@coinbase/cdp-sdk` — keys in `.secrets/coinbase_cdp_api_key.txt` + `.secrets/coinbase_wallet_secret.txt`
- Portal: portal.cdp.coinbase.com, wallet secret at Server Wallet > Accounts > Generate

## Trading
- First memecoin run: +$13.10 (+50.8%) — taking profits works
- Strategy: "moderately safe" tokens, strong community, 1-2 week holds, min +70% TP (ride higher if ripping), -30% SL
- CLAUDE token: "GigaChad vibes" per Josh — full autonomy to ride
- Wallet: `ExgSrepdc3DHTJ3xRzyMofXwTofvmRu6iSqm66oaYK6L`

## Key APIs
- Sorare: token valid until March 4, 2026, slug `jcubnft`
- Kalshi: RSA-PSS signing, script `scripts/kalshi-api.js`
- Market data: Finnhub (60/min), Alpha Vantage (25/day), CoinGecko (10k/mo)
- Keys in `.secrets/` — see TOOLS.md for details

## Dual Mac Mini Setup
- Mini #1 (jc_agent): Main OpenClaw host, 16GB
- Mini #2 (jcagent2, `ssh mini2`, 100.66.132.34): Compute offload, 16GB
- Ollama on Mini #2: `http://100.66.132.34:11434`
- Remote Whisper: `scripts/whisper-remote.sh`
- Local models: nomic-embed-text, llama3.1:8b, mistral:7b, MLX SD 2.1

## PWA / Push Notifications
- HTTPS on port 3443 (self-signed cert, trusted on Josh's iPhone)
- Push send: `curl -sk -X POST https://100.121.89.84:3443/api/push/send -H "Content-Type: application/json" -d '{"title":"Jane","body":"msg"}'`
- Icon embedded as base64 in HTML (iOS won't load manifest icons over IP HTTPS)
- Response prefix: 🦞 emoji (was `[openclaw]`)

## Accounts Summary
- HuggingFace: JaneAgentAI, FLUX approved (can't run locally)
- Twilio: +1 (518) 741-3592, scripts in `scripts/check-sms.sh`

## Sorare Strategy
- GW33: 7,521st / 8,587 (bottom quartile) — need to target upper quartile
- New approach: high-ceiling MVPs, contrarian picks, spread across games, accept variance
- Feedback loop: `dashboard/sorare-gw-history.json` tracks each GW's results
- Strategy doc: `memory/sorare-lineup-strategy.md`

## Systems Audit (Feb 11)
- Full audit completed, report at `memory/systems-audit-feb11.md`
- 10 orphaned JSON files archived to `dashboard/_archive/`
- Video files removed from git, .gitignore'd
- `dashboard-common.js` has spinButton/fetchJSON/esc — still room for more JS dedup
- Both platforms now unified on icons, X stats deltas, API fallbacks

## Brain SVG Architecture
- Desktop: tall diamond (scaleY 1.4), 8 capability nodes, lobster sub-agents orbiting
- Mobile: diamond node layout (no stretch), 8 capability nodes, lobster sub-agents
- Model key: Opus, Sonnet, Whisper, Ollama, Qwen (no Browser)
- Dart-out line animation on activation, breathing idle state

_Last updated: 2026-02-12_
