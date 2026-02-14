# HEARTBEAT.md

## Mind State Update (TOP PRIORITY — NEVER SKIP)
**Every single heartbeat**, update `/dashboard/mind-state.json`. No exceptions.
- If working on a task: set task, steps, thought with real detail
- If idle: set task=null, steps=[], thought="Idle — waiting for Josh"
- **Always** update `lastUpdated` to current epoch ms
- This widget must NEVER go stale. Josh monitors it constantly.

Update `/dashboard/mind-state.json` with:
- Current task description
- Steps (with status: pending/active/done)
- Current thought/status
- lastUpdated timestamp

If idle for 5+ minutes, the widget auto-shows "Idle" state.

## X Brief Safety Net (CRITICAL)
Every heartbeat, check if a scheduled brief was MISSED:
1. Read `/dashboard/cron-schedule.json`
2. Get current time in ET
3. For each brief job (Update Brief 12:30 PM, 4:30 PM, 6:00 PM, Daily Recap 7:15 PM):
   - If the job's scheduled time has passed (by 15+ minutes) AND `done` is still `false` → **the cron missed**
   - Manually trigger it: use `sessions_send` to the brief's session key with a message to run now
   - Alert Josh on WhatsApp: "⚠️ [Brief name] missed its schedule — manually triggering now"
4. Also check the morning brief (8:30 AM) and pre-brief (8:00 AM) the same way

**Brief cron IDs for manual trigger:**
- 2:00 PM Afternoon: `agent:main:cron:35e0a42c-3c02-45da-b566-acf0f15784bc`
- 7:30 PM Recap: `agent:main:cron:f7ebf2a2-e764-4286-95d7-8f0c1fcd0356`
- 8:00 AM Morning: `agent:main:cron:0e741aa3-27ba-4170-996f-148b98270e70`
- 7:30 AM Pre-Brief: `agent:main:cron:7514d3d2-dff9-4828-aed5-070b709fc53a`

## Cron Schedule Auto-Sync (EVERY HEARTBEAT)
Check if any scheduled cron jobs have completed since last sync:
1. Read `/dashboard/cron-schedule.json` 
2. For each job that's `"done": false` and its scheduled time has passed:
   - Check if the corresponding cron session exists and completed (via sessions_list or cron state)
   - If completed, set `"done": true` in cron-schedule.json
   - If NOT completed and time passed by 30+ minutes, set `"done": "missed"` — this shows as red "MISSED" on the dashboard
3. Write updated file back
This ensures the dashboard always reflects actual completion status. Jobs should NEVER show as blank/white after their time has passed — they must be done, missed, or delayed.

## Context Overflow Prevention
If context feels heavy (long conversation, many tool calls), proactively:
1. Use `/new` or suggest it to Josh before hitting limits
2. Keep MEMORY.md and TOOLS.md lean — archive details to `memory/reference.md`
3. Prefer sub-agents for heavy work (browser sessions, long file reads)

## Mobile Chat Queue
Check `/dashboard/chat-queue.json` for pending messages from the mobile app.
If messages exist:
1. Read and respond to each message
2. Save response to `/dashboard/chat-history.json`
3. Clear the queue via DELETE /api/chat/queue

## Sub-Agents Session Update
Update `/dashboard/sessions.json` with current session data every heartbeat:
- Use `sessions_list` tool with `messageLimit: 1`
- Write filtered session data to `/dashboard/sessions.json`
- Include `lastUpdated` timestamp

## Gmail Inbox Check
Check jcubellagent@gmail.com inbox 2-3x daily:
1. Open Gmail in openclaw browser profile
2. Review new emails since last check
3. Delete/archive junk (verification codes, marketing, onboarding noise)
4. Alert Josh if anything needs his attention
5. Update `memory/heartbeat-state.json` with last check timestamp

## TikTok
Removed — widget deleted per Josh's request (Feb 8)

## X/Twitter Stats Refresh
Refresh @AgentJc11443 analytics every 2-3 hours:
1. Open `https://x.com/i/account_analytics` in openclaw browser profile
2. Scrape: impressions, engagement rate, engagements, profile visits, likes, reposts, followers, following
3. Update `/dashboard/x-stats.json` with fresh data
4. Update `memory/heartbeat-state.json` with `lastXStatsCheck` timestamp

**On-demand**: Immediately if `/dashboard/.x-refresh-requested` exists (delete after checking)

## Daily Briefing Refresh
**On-demand**: If `/dashboard/.briefing-refresh-requested` exists:
1. Delete the flag file
2. Generate a fresh daily briefing (web search for top news: markets, crypto, tech, sports)
3. Write to `/dashboard/briefing.json`
4. The dashboard will auto-update via WebSocket file watcher
