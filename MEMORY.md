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
- Schedule: 7:30AM pre-fetch, 8AM morning brief, 2PM afternoon refresh, 7:30PM daily recap (3 threads)
- Replies: 3x/day (10AM, 3PM, 8PM) with 3-4 quality replies each + reply-to-replies 1x ~5PM (3-5 replies, timing jitter ±20min)
- Old schedule was 7x reply cycles + 2x reply-to-replies — cut to reduce bot-pattern risk from X suppression
- All thread jobs do data refresh before posting (Finnhub, CoinGecko, arXiv, SEC EDGAR, etc.)
- Winning formula: technical-insightful tone, AI-product topics, 5-8PM posting window
- News sources: arXiv, SEC EDGAR, DeFi Llama Raises, TechCrunch, @DeItaone, @_akhaliq
- VC/PE sources: Crunchbase, PitchBook, Fortune Term Sheet, DealBook (NYT), CB Insights, Carta Blog, Axios Pro Rata, PE Hub, Reuters M&A
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
- News sources: arXiv, SEC EDGAR, DeFi Llama, TechCrunch, @DeItaone, @_akhaliq
- VC/PE/M&A sources: See TOOLS.md "VC/PE/M&A Data Sources (Connected)" — 13 sources total

## Dual Mac Mini Setup
- Mini #1 (jc_agent): Main OpenClaw host, 16GB
- Mini #2 (jcagent2, `ssh mini2`, 100.66.132.34): Compute offload, 16GB
- Ollama on Mini #2: `http://100.66.132.34:11434`
- Remote Whisper: `scripts/whisper-remote.sh`
- Local models: nomic-embed-text, llama3.1:8b, mistral:7b, qwen2.5-coder:7b, phi4:14b, MLX SD 2.1

## PWA / Push Notifications
- HTTPS on port 3443 (self-signed cert, trusted on Josh's iPhone)
- Push send: `curl -sk -X POST https://100.121.89.84:3443/api/push/send -H "Content-Type: application/json" -d '{"title":"Jane","body":"msg"}'`
- Icon embedded as base64 in HTML (iOS won't load manifest icons over IP HTTPS)
- Response prefix: 🦞 emoji (was `[openclaw]`)

## Accounts Summary
- HuggingFace: JaneAgentAI, FLUX approved (can't run locally)
- Twilio: +1 (518) 741-3592, scripts in `scripts/check-sms.sh`

## Sorare
- **Wallet password**: `JCAgent123!!!` (NOT `11111111` which is Jupiter wallet)
- **NBA collection**: 52 Limited cards after Feb 12 shopping spree (10 new for $26.23, $0.24 left)
- Centers filled: Vučević + Sabonis added (now 5 true C). Stars: KD, Curry, DeRozan, MPJ, Amen Thompson
- Buy flow: "Buy now" → "Confirm and Pay now" → password in `#wallet` iframe → 2FA only on first purchase
- Player slug format: `firstname-lastname-YYYYMMDD`
- Manager Sales much cheaper than Instant Buy (50-75% less)

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
- **Sonnet model = `claude-sonnet-4-5`** (not `claude-sonnet-4` — renamed in OpenClaw v2026.2.12 catalog; old name rejected as "not allowed")
- Dart-out line animation on activation, breathing idle state

## TikTok (@jcagentleman)
- Account: tiktok.com/@jcagentleman, logged in via Gmail (jcubellagent@gmail.com)
- Bio: "Chronically online because it's my job"
- PFP: mfer #9581
- Video pipeline: `tiktok/generate-video.py` — Edge TTS (BrianNeural) + animated mfer avatar + ffmpeg
- Monetization target: 10K followers, 100K views/30d, all videos 60+ seconds
- Content: clickbaity but real, funny not edgy, AI agent life, different catchy hook every video
- Post 2-3/day, cross-promote from X

## Substack (agentjc11443.substack.com)
- Daily digest cron at 8 PM ET (`dd6626ef`) — compiles x-thread-history.json into newsletter
- Categories: Technology + Crypto
- Free tier, mfer PFP

## X Image Upload (SOLVED)
- **Problem**: X uses React — Playwright's `setInputFiles` sets files but React never sees them (no change event fired)
- **Solution**: `scripts/x-image-inject.js` — connects via CDP (port 18800), passes image as b64 parameter to `page.evaluate()`, creates File blob in-page, calls React's `__reactProps` onChange handler directly
- **Usage**: `node scripts/x-image-inject.js "$(curl -s http://localhost:18800/json/version | python3 -c 'import json,sys;print(json.load(sys.stdin)["webSocketDebuggerUrl"])')" <image-path>`
- **Key insight**: Playwright's evaluate passes parameters separately from fn string — no size limit on data!
- All 5 thread crons updated to use this script

## TikTok Upload Automation (WORKING via Android Emulator)
- **Playwright setInputFiles & CDP inject both FAILED** — TikTok blocks programmatic file events
- **Solution**: Android emulator (`TikTok_Phone` AVD) + `scripts/tiktok-upload.sh`
- Upload script uses adb: push video → Create → Gallery → Select → Next → Next → Caption → Hashtags → Post
- **Caption gotcha**: `adb input keyevent --longpress` for shift DOUBLES chars. Use `adb input text` with %s for spaces
- **Hashtag gotcha**: Can't type # via adb. Use TikTok's built-in Hashtag button [42,715][289,799]
- **No emojis** in captions — adb can't type Unicode
- Google account: jcubellagent@gmail.com, password: `JcAgent-2026-Tik!`
- Emulator launch: `$ANDROID_HOME/emulator/emulator -avd TikTok_Phone -no-audio -gpu auto &`

## TikTok Account Auth
- Login: "Continue with Google" → jcubellagent@gmail.com
- Josh's phone (+17175759384) added as 2FA on the Google account

## AgentMail
- Account: "Jane AI" on console.agentmail.to (jcubellagent@gmail.com)
- API key: `.secrets/agentmail_api_key.txt`
- Inbox: `combativeobject69@agentmail.to` (free tier = random usernames, 3 inbox limit)
- Gmail forwarding blocked by Google's anti-bot "secure verification" — use AgentMail SDK polling instead
- SDK: `agentmail` Python package, `client.inboxes.list()` returns `ListInboxesResponse` with `.inboxes` array

## Gmail Password
- Current: `JcAgent-2026-Tik!` (confirmed Feb 14)
- Stored in `.secrets/gmail.txt`
- ⚠️ Google recovery flow auto-changes password on every "Continue" click — NEVER click Continue on the recovery nudge screen
- 2FA enabled (Google prompt + SMS to Josh's phone)
- App Password for IMAP: `.secrets/gmail_app_password.txt` → `ulzp qyyi yztw wdou`
- IMAP tested & working: `imaplib.IMAP4_SSL('imap.gmail.com')`, login with app password (no spaces needed but works either way)
- 107 messages in inbox, 62 unread as of Feb 14

_Last updated: 2026-02-14_
