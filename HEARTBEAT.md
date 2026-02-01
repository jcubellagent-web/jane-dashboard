# HEARTBEAT.md

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
