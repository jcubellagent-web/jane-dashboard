#!/bin/bash
# Fetch latest Federal Reserve Economic Data (FRED)
# Output: JSON object with key economic indicators

set -euo pipefail

API_KEY_FILE="/Users/jc_agent/.openclaw/workspace/.secrets/fred_api_key.txt"
CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TMP_FILE=$(mktemp)

if [ ! -f "$API_KEY_FILE" ]; then
  echo "ERROR: FRED API key not found at $API_KEY_FILE" >&2
  exit 1
fi

API_KEY=$(cat "$API_KEY_FILE" | tr -d '[:space:]')

# Key economic series (format: "ID:Description")
SERIES=(
  "GDP:Gross Domestic Product"
  "UNRATE:Unemployment Rate"
  "CPIAUCSL:Consumer Price Index (Inflation)"
  "FEDFUNDS:Federal Funds Rate"
  "T10Y2Y:10Y-2Y Treasury Yield Spread"
  "PAYEMS:Nonfarm Payrolls"
)

echo "{" > "$TMP_FILE"
first=true

for entry in "${SERIES[@]}"; do
  series_id="${entry%%:*}"
  description="${entry#*:}"
  
  # Fetch latest observation
  data=$(curl -s "https://api.stlouisfed.org/fred/series/observations?series_id=${series_id}&api_key=${API_KEY}&file_type=json&sort_order=desc&limit=1")
  
  observation=$(echo "$data" | jq -r '.observations[0] // {}')
  
  if [ "$observation" != "{}" ]; then
    if [ "$first" = false ]; then
      echo "," >> "$TMP_FILE"
    fi
    first=false
    
    echo "\"$series_id\": {
      \"name\": \"$description\",
      \"value\": $(echo "$observation" | jq '.value'),
      \"date\": $(echo "$observation" | jq '.date')
    }" >> "$TMP_FILE"
  fi
  
  # Rate limit protection
  sleep 0.2
done

echo "}" >> "$TMP_FILE"

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson fred "$(cat $TMP_FILE)" '.fredData = $fred' "$CACHE_FILE" > "${CACHE_FILE}.tmp"
  mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"fredData\": $(cat $TMP_FILE)}" > "$CACHE_FILE"
fi

# Output for verification
cat "$TMP_FILE"
rm "$TMP_FILE"
