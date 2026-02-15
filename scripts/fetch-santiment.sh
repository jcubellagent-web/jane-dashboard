#!/bin/bash
# Fetch on-chain metrics from Santiment free tier
# Output: JSON with crypto metrics

set -euo pipefail

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TMP_FILE=$(mktemp)

# Santiment GraphQL endpoint
API_URL="https://api.santiment.net/graphql"

# GraphQL query for basic on-chain metrics (free tier)
QUERY='{"query": "{ getMetric(metric: \"active_addresses_24h\") { timeseriesData(slug: \"bitcoin\" from: \"utc_now-1d\" to: \"utc_now\" interval: \"1d\") { datetime value } } }"}'

# Fetch Santiment data
curl -sL -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "$QUERY" | jq '{
    metric: "active_addresses_24h",
    asset: "bitcoin",
    data: .data.getMetric.timeseriesData,
    note: "Free tier - limited metrics"
  }' > "$TMP_FILE" 2>/dev/null || echo '{"error": "API unavailable or requires authentication", "note": "Santiment free tier may have changed"}' > "$TMP_FILE"

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson data "$(cat $TMP_FILE)" '.santiment = $data' "$CACHE_FILE" > "${CACHE_FILE}.tmp"
  mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"santiment\": $(cat $TMP_FILE)}" > "$CACHE_FILE"
fi

# Output for verification
cat "$TMP_FILE"
rm "$TMP_FILE"
