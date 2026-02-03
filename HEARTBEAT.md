# HEARTBEAT.md

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

## TikTok Stats Check
Check @degencollector TikTok stats:
1. **Scheduled**: 2-3x daily (morning ~9am, afternoon ~2pm, evening ~8pm) if last check was 4+ hours ago
2. **On-demand**: Immediately if `/dashboard/.tiktok-refresh-requested` exists (delete after checking)

**How to check:**
- Navigate to https://www.tiktok.com/@degencollector
- Get: followers, total likes, and view counts for recent videos
- Update `/dashboard/tiktok-stats.json`
- Update `memory/heartbeat-state.json` with new timestamp

Track last check in `memory/heartbeat-state.json`
