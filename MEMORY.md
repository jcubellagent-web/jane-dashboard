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
- Desktop = index.html, Mobile = mobile.html — separate codebases
- API routes fail from external IPs on mobile — use static JSON files
- Mobile ticker: API key for NASDAQ is `nasdaq` not `ndaq`
- NASDAQ 100 movers for X threads ONLY, not mobile dashboard
- **NEVER auto-post ad hoc tweets** — always send draft for Josh's approval first
- Push notifications: BE AGGRESSIVE — send for every direct reply, cron completions, alerts, sub-agent results. Skip heartbeats only. Josh will say if it's too much.
- Check for active sub-agents before setting mind-state to idle

## X/Twitter (@AgentJc11443)
- Premium ✅, ~15 followers (doubled in 2 days), AI news feed bot (rebranded Feb 9)
- **BANNED TOPICS**: crypto-security, wallet security, agent security
- Content plan: `dashboard/x-content-plan.json`
- X API Free = post only; analytics via browser scraping
- Manual refresh: `.x-refresh-requested` flag → heartbeat picks up
- Strategy details: `memory/reference.md`
- Schedule: 8AM pre-fetch, 8:30AM brief, 12:30PM/4:30PM/6PM updates, 7:15PM recap
- All thread jobs do data refresh before posting (Finnhub, CoinGecko, arXiv, SEC EDGAR, etc.)
- Winning formula: technical-insightful tone, AI-product topics, 5-8PM posting window
- News sources: arXiv, SEC EDGAR, DeFi Llama, TechCrunch, @DeItaone, @_akhaliq

## Coinbase Agentic Wallet
- EVM (Base): `0xe8f6f50c79d24ef271764447E46f66f1Ef4Cae8F`
- Solana: `8nqcu8QUff1sSQabnzTLUzSPS4byvoPs9m9oUrGvFJUa`
- Project ID: `7e1fcc61-d1d8-44d1-b28d-cadc353e200b`
- Funded: 2 SOL from Josh (~$158)
- CDP SDK: `@coinbase/cdp-sdk` — keys in `.secrets/coinbase_cdp_api_key.txt` + `.secrets/coinbase_wallet_secret.txt`
- Portal: portal.cdp.coinbase.com, wallet secret at Server Wallet > Accounts > Generate

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

## PWA / Push Notifications
- HTTPS on port 3443 (self-signed cert, trusted on Josh's iPhone)
- Push send: `curl -sk -X POST https://100.121.89.84:3443/api/push/send -H "Content-Type: application/json" -d '{"title":"Jane","body":"msg"}'`
- Icon embedded as base64 in HTML (iOS won't load manifest icons over IP HTTPS)
- Response prefix: 🦞 emoji (was `[openclaw]`)

## Accounts Summary
- HuggingFace: JaneAgentAI, FLUX approved (can't run locally)
- Twilio: +1 (518) 741-3592, scripts in `scripts/check-sms.sh`

_Last updated: 2026-02-10_
