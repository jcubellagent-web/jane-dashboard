#!/bin/bash
# Deploy monitoring to Mini #2
set -euo pipefail
REMOTE="mini2"
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Deploying monitoring to Mini #2..."
ssh "$REMOTE" "mkdir -p /Users/jcagent2/monitoring /Users/jcagent2/Library/LaunchAgents"
scp "$DIR/monitor.js" "$REMOTE:/Users/jcagent2/monitoring/monitor.js"
scp "$DIR/com.jcagent2.monitor.plist" "$REMOTE:/Users/jcagent2/Library/LaunchAgents/"

ssh "$REMOTE" "launchctl unload /Users/jcagent2/Library/LaunchAgents/com.jcagent2.monitor.plist 2>/dev/null || true"
ssh "$REMOTE" "launchctl load /Users/jcagent2/Library/LaunchAgents/com.jcagent2.monitor.plist"
echo "✓ Deployed and started. Test: curl http://100.66.132.34:3001/status"
