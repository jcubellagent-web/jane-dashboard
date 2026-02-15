#!/bin/bash
# Fetch AI-related bills from ProPublica Congress API
# Output: JSON with congressional AI bills

set -euo pipefail

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TMP_FILE=$(mktemp)

# ProPublica Congress API endpoint
API_URL="https://api.propublica.org/congress/v1/bills/search.json?query=artificial+intelligence"

# Note: ProPublica requires a free API key
# Check if we have one
API_KEY_FILE="/Users/jc_agent/.openclaw/workspace/.secrets/propublica_api_key.txt"

if [ -f "$API_KEY_FILE" ]; then
  API_KEY=$(cat "$API_KEY_FILE" | tr -d '[:space:]')
  
  curl -sL "$API_URL" \
    -H "X-API-Key: $API_KEY" | jq '{
      bills: [.results[]? | {
        title: .title,
        bill_id: .bill_id,
        introduced: .introduced_date,
        sponsor: .sponsor_name,
        party: .sponsor_party,
        status: .latest_major_action,
        url: .congressdotgov_url
      }] | .[:10]
    }' > "$TMP_FILE" 2>/dev/null || echo '{"bills": [], "error": "API request failed"}' > "$TMP_FILE"
else
  echo '{"bills": [], "error": "ProPublica API key not found", "note": "Create free API key at https://www.propublica.org/datastore/api/propublica-congress-api"}' > "$TMP_FILE"
fi

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson data "$(cat $TMP_FILE)" '.congressAI = $data' "$CACHE_FILE" > "${CACHE_FILE}.tmp"
  mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"congressAI\": $(cat $TMP_FILE)}" > "$CACHE_FILE"
fi

# Output for verification
cat "$TMP_FILE"
rm "$TMP_FILE"
