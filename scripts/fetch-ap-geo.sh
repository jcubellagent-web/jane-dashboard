#!/bin/bash
# fetch-ap-geo.sh - Fetch AP News World section headlines

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TEMP_FILE="/tmp/ap-geo-$$.json"

# Ensure cache file exists
if [ ! -f "$CACHE_FILE" ]; then
    echo '{}' > "$CACHE_FILE"
fi

# Use AP News RSS feed (more reliable than scraping)
RESPONSE=$(curl -s "https://rssmix.com/u/8/apnews" 2>/dev/null || curl -s "https://apnews.com/index.rss" 2>/dev/null || echo "")

if [ -n "$RESPONSE" ]; then
    # Extract titles from RSS feed
    echo "$RESPONSE" | \
        grep -o '<title>.*</title>' | \
        sed -E 's/<\/?title>//g' | \
        grep -v "AP News" | \
        head -n 5 | \
        jq -R -s -c 'split("\n") | map(select(length > 0)) | {source: "AP World News", stories: .}' > "$TEMP_FILE" 2>/dev/null || \
        echo '{"source": "AP World News", "stories": [], "error": "Parse failed"}' > "$TEMP_FILE"
else
    echo '{"source": "AP World News", "stories": [], "error": "Feed unavailable"}' > "$TEMP_FILE"
fi

# Merge into cache
jq --argjson ap "$(cat "$TEMP_FILE")" '.apNews = $ap' "$CACHE_FILE" > "${CACHE_FILE}.tmp" 2>/dev/null && \
    mv "${CACHE_FILE}.tmp" "$CACHE_FILE" || \
    echo '{"error": "jq merge failed"}' > "${CACHE_FILE}.tmp"

rm -f "$TEMP_FILE"
echo "✅ AP News geopolitics data cached"
