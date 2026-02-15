#!/bin/bash
# fetch-gdelt.sh - Query GDELT API for global conflict/trade events

set -euo pipefail

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TEMP_FILE="/tmp/gdelt-$$.json"

# Ensure cache file exists
if [ ! -f "$CACHE_FILE" ]; then
    echo '{}' > "$CACHE_FILE"
fi

# GDELT GKG (Global Knowledge Graph) API query for trade/conflict themes
# Query last 24 hours for trade war, tariff, sanctions, conflict themes
QUERY="trade%20war%20OR%20tariff%20OR%20sanctions%20OR%20conflict"
MODE="ArtList"
MAXRECORDS="10"
FORMAT="json"
TIMESPAN="24h"

# Build GDELT API request (using GKG summary API)
# Note: GDELT's public API endpoint
GDELT_URL="https://api.gdeltproject.org/api/v2/doc/doc?query=${QUERY}&mode=${MODE}&maxrecords=${MAXRECORDS}&format=${FORMAT}&timespan=${TIMESPAN}"

# Fetch and parse - handle potential API errors
RESPONSE=$(curl -s "$GDELT_URL" 2>/dev/null || echo "")

if [ -n "$RESPONSE" ] && echo "$RESPONSE" | jq empty 2>/dev/null; then
    echo "$RESPONSE" | \
        jq -c '{
            source: "GDELT Global Events",
            events: [.articles[]? | {
                title: .title,
                url: .url,
                domain: .domain,
                language: .language,
                seendate: .seendate
            }] | .[0:5]
        }' > "$TEMP_FILE"
else
    echo '{"source": "GDELT Global Events", "events": [], "error": "API unavailable or invalid response"}' > "$TEMP_FILE"
fi

# Merge into cache
jq --argjson gdelt "$(cat "$TEMP_FILE")" '.gdelt = $gdelt' "$CACHE_FILE" > "${CACHE_FILE}.tmp"
mv "${CACHE_FILE}.tmp" "$CACHE_FILE"

rm -f "$TEMP_FILE"
echo "✅ GDELT geopolitics data cached"
