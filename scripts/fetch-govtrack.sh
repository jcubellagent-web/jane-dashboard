#!/bin/bash
# Fetch AI legislation from GovTrack API
# Output: JSON object with recent AI-related bills

set -euo pipefail

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TMP_FILE=$(mktemp)
API_URL="https://www.govtrack.us/api/v2/bill?q=artificial+intelligence&sort=-introduced_date&limit=10"

# Fetch GovTrack data
curl -sL "$API_URL" | jq '{
  bills: [.objects[] | {
    title: .title,
    number: .display_number,
    introduced: .introduced_date,
    sponsor: .sponsor.name,
    status: .current_status_description,
    url: ("https://www.govtrack.us" + .link)
  }]
}' > "$TMP_FILE" 2>/dev/null || echo '{"bills": [], "error": "API unavailable"}' > "$TMP_FILE"

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson data "$(cat $TMP_FILE)" '.govTrack = $data' "$CACHE_FILE" > "${CACHE_FILE}.tmp"
  mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"govTrack\": $(cat $TMP_FILE)}" > "$CACHE_FILE"
fi

# Output for verification
cat "$TMP_FILE"
rm "$TMP_FILE"
