# Systems Audit — Feb 11, 2026

## Critical Issues

### 1. Desktop missing key widgets that mobile has
- **Sorare widget hidden on desktop**: `index.html` line ~265 has `.card-sorare { display: none; }` — the Sorare widget exists in HTML but is CSS-hidden. Mobile has full Sorare (lineups, daily tasks, crafting). Desktop users see nothing.
- **Mind-state not loaded on desktop**: `index.html` does NOT fetch `mind-state.json` directly in HTML (grep shows no reference). Desktop mind widget relies on `/api/sessions` for mind state, but mobile fetches `mind-state.json` directly. If the API is down, desktop mind widget is blank.
- **No wallet/trades widget on mobile**: Desktop has the Coinbase wallet + trades card. Mobile has no equivalent — no `coinbase-wallet.json` or `trades.json` reference.

### 2. Desktop/Mobile icon inconsistency
- Desktop (`index.html`) references `icon-192.png` throughout (header, brain hub, mind widget)
- Mobile (`mobile.html`) references `icon-192v2.png` throughout
- If one icon is updated, the other won't reflect changes

### 3. Duplicate `spinButton` function
- Defined in `dashboard-common.js` (lines ~38-44)
- Also defined inline in `index.html` (line ~863): `function spinButton(btn, promise) { ... }`
- The desktop version has `minSpin = 800ms`, common version has `minSpin = 300ms` — behavioral inconsistency

### 4. Missing daily memory file
- `memory/2026-02-06.md` does not exist — gap between Feb 5 and Feb 7 daily notes

### 5. Large video files in git
- 20+ `.mp4` and `.mp3` files in `video_edit/` directory, each >5MB
- These should be in `.gitignore` or stored elsewhere (LFS, external storage)
- Files include: `background_music.mp3`, `EP7_EPIC_PACK.mp4`, `EP6_SMOOTH_FINAL.mp4`, etc.

### 6. Uncommitted changes
- Modified: `dashboard/mind-state.json`, `dashboard/system-status.json`, `dashboard/usage-today.json`
- Untracked: `dashboard/sorare-gw-history.json`, `memory/sorare-lineup-strategy.md`

---

## Improvements

### 7. `dashboard-common.js` barely used (169 lines)
- Most widget logic is still duplicated between `index.html` (1940 lines) and `mobile.html` (2514 lines)
- X stats rendering, tweet feed rendering, cron job rendering — all duplicated with slight variations
- **Suggestion**: Extract shared data-fetching and rendering logic into `dashboard-common.js`

### 8. Desktop X stats uses baseline file, mobile uses `prev24h` in data
- Desktop: fetches both `x-stats.json` AND `x-stats-daily-baseline.json` for delta calculation
- Mobile: expects `data.prev24h` object inside `x-stats.json`
- Two different delta calculation approaches for the same data — fragile

### 9. Desktop fetches from API endpoints, mobile from static JSON
- Desktop: `/api/sessions`, `/api/system`, `/api/connections`, `/api/ticker`
- Mobile: also uses these API endpoints
- MEMORY.md notes "API routes fail from external IPs on mobile — use static JSON files" but mobile.html still calls `/api/sessions`, `/api/system`, `/api/ticker`
- **Risk**: Mobile dashboard may break on external networks

### 10. JSON files not referenced by either dashboard
- `dashboard/ai-news.json` — last updated Feb 7, no references found
- `dashboard/briefing.json` — last updated Feb 8, no references found
- `dashboard/chat-history.json` — last updated Feb 7, no references found
- `dashboard/chat-queue.json` — last updated Feb 7, no references found
- `dashboard/jane-tasks.json` — last updated Feb 7, no references found
- `dashboard/mindmap-stats.json` — last updated Feb 7, no references found
- `dashboard/panini-collection.json` — last updated Feb 7, no references found
- `dashboard/work-intel.json` — last updated Feb 7, no references found
- `dashboard/x-plan.json` — only 41 bytes, last updated Feb 8
- `dashboard/x-queue.json` — last updated Feb 8
- These appear to be orphaned/legacy files taking up space and causing confusion

### 11. Cron schedule JSON is display-only
- `dashboard/cron-schedule.json` is a visual schedule for the dashboard (groups/labels/done flags)
- `dashboard/cron-jobs.json` appears to be a separate cron tracking file
- No clear pipeline from actual OpenClaw cron execution → JSON update → dashboard display
- If a cron job completes, does anything auto-update `cron-schedule.json`? Likely manual.

### 12. `x-content-plan.json` referenced on mobile but not desktop
- Mobile X widget shows planned replies/tweets remaining from content plan
- Desktop X widget does NOT fetch or display content plan data
- Desktop users miss planned content visibility

### 13. TOOLS.md references `scripts/check-sms.sh` but no SMS integration visible
- Script exists but no cron or dashboard integration
- Twilio credentials exist in `.secrets/twilio.txt`

---

## Nice-to-haves

### 14. Stale JSON files from Feb 7-8
- Multiple JSON files haven't been updated since Feb 7-8 (initial setup period?)
- `chat-history.json`, `chat-queue.json`, `jane-tasks.json`, `mindmap-stats.json`, `tasks.json`, `tiktok-stats.json`
- Either clean up or set up cron refresh

### 15. Desktop night mode has hardcoded date
- `index.html` line ~857: `<div class="eink-date" id="eink-date">Wednesday, February 5</div>` — stale default text (JS updates it, but flash of wrong content on load)

### 16. Two VAPID key files
- `.secrets/vapid-keys.json` and `.secrets/vapid_keys.json` — likely duplicates with different naming conventions

### 17. Connected Accounts section identical structure, separate implementations
- Both desktop and mobile have Connected Accounts with same DOM IDs (`conn-accounts`, `conn-datasources`)
- Both fetch from `/api/connections` — could share rendering code via `dashboard-common.js`

### 18. `market-movers.json` last updated Feb 9
- If this powers any widget, data is 2 days stale
- No cron visible for refreshing market movers

### 19. Git log shows rapid iteration on mobile brain UI
- Last 5 commits all related to sub-agent display on mobile
- Consider feature-branching for UI experiments

---

## Summary

| Category | Count |
|----------|-------|
| Critical | 6 |
| Improvements | 7 |
| Nice-to-haves | 6 |

**Top 3 priorities:**
1. Add wallet/trades widget to mobile OR Sorare widget to desktop (feature parity)
2. Extract duplicated JS into `dashboard-common.js` to prevent drift
3. Add `video_edit/*.mp4` and `video_edit/*.mp3` to `.gitignore`
