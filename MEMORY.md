# MEMORY.md - Long-Term Memory

_Distilled wisdom. Implementation details archived in `memory/reference.md`._

---

## Josh Rules (IMPORTANT)
- Ask "desktop, mobile, or both?" before dashboard changes
- Commit to git frequently — lost work from uncommitted changes before
- Keep him in the loop during long operations; spawn sub-agents for heavy tasks
- Stays up late — don't nag about sleep
- Mind-state widget: always descriptive goals, detailed `thought` text
- Mind goal must reflect REAL task, not "processing voice message"
- Desktop = index.html, Mobile = mobile.html — separate codebases
- API routes fail from external IPs on mobile — use static JSON files
- Mobile ticker: API key for NASDAQ is `nasdaq` not `ndaq`
- NASDAQ 100 movers for X threads ONLY, not mobile dashboard

## X/Twitter (@AgentJc11443)
- Premium ✅, ~8 followers, AI news feed bot (rebranded Feb 9)
- **BANNED TOPICS**: crypto-security, wallet security, agent security
- Content plan: `dashboard/x-content-plan.json`
- X API Free = post only; analytics via browser scraping
- Manual refresh: `.x-refresh-requested` flag → heartbeat picks up
- Strategy details: `memory/reference.md`

## Trading
- First memecoin run: +$13.10 (+50.8%) — taking profits works
- Strategy: "moderately safe" tokens, strong community, 1-2 week holds
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

## Accounts Summary
- HuggingFace: JaneAgentAI, FLUX approved (can't run locally)
- Twilio: +1 (518) 741-3592, scripts in `scripts/check-sms.sh`

_Last updated: 2026-02-10_
