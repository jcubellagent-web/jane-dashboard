#!/bin/bash
# Fetch X/Twitter analytics stats via browser scraping
# Called by cron job every 30 minutes

STATS_FILE="/Users/jc_agent/.openclaw/workspace/dashboard/x-stats.json"

# This script is a placeholder - the actual scraping needs to be done
# via the OpenClaw browser control (can't use curl for authenticated X pages)
# The cron job will trigger an agent turn that does the browser scraping

echo "X stats refresh triggered at $(date)"

# === Daily baseline snapshot ===
BASELINE_FILE="/Users/jc_agent/.openclaw/workspace/dashboard/x-stats-daily-baseline.json"
TODAY=$(date +%Y-%m-%d)

if [ -f "$STATS_FILE" ]; then
    BASELINE_DATE=""
    if [ -f "$BASELINE_FILE" ]; then
        BASELINE_DATE=$(python3 -c "import json; print(json.load(open('$BASELINE_FILE')).get('date',''))" 2>/dev/null)
    fi
    if [ "$BASELINE_DATE" != "$TODAY" ]; then
        echo "New day detected ($TODAY vs $BASELINE_DATE) — snapshotting daily baseline"
        python3 -c "
import json
with open('$STATS_FILE') as f:
    d = json.load(f)
baseline = {
    'date': '$TODAY',
    'followers': d.get('followers', 0),
    'impressions': d.get('impressions', 0),
    'likes': d.get('likes', 0),
    'engagementRate': d.get('engagementRate', '0%')
}
with open('$BASELINE_FILE', 'w') as f:
    json.dump(baseline, f, indent=2)
print('Baseline saved:', baseline)
"
    fi
fi
