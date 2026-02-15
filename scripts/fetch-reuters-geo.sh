#!/bin/bash
# fetch-reuters-geo.sh - Fetch Reuters World News headlines

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TEMP_FILE="/tmp/reuters-geo-$$.json"

# Ensure cache file exists
if [ ! -f "$CACHE_FILE" ]; then
    echo '{}' > "$CACHE_FILE"
fi

# Use Reuters RSS feed (more reliable than scraping)
RESPONSE=$(curl -s "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best" 2>/dev/null || echo "")

if [ -n "$RESPONSE" ]; then
    # Extract titles from RSS feed
    echo "$RESPONSE" | \
        grep -o '<title>.*</title>' | \
        sed -E 's/<\/?title>//g' | \
        grep -v "Reuters" | \
        head -n 5 | \
        jq -R -s -c 'split("\n") | map(select(length > 0)) | {source: "Reuters World", stories: .}' > "$TEMP_FILE" 2>/dev/null || \
        echo '{"source": "Reuters World", "stories": [], "error": "Parse failed"}' > "$TEMP_FILE"
else
    echo '{"source": "Reuters World", "stories": [], "error": "Feed unavailable"}' > "$TEMP_FILE"
fi

# Merge into cache
jq --argjson reuters "$(cat "$TEMP_FILE")" '.reuters = $reuters' "$CACHE_FILE" > "${CACHE_FILE}.tmp" 2>/dev/null && \
    mv "${CACHE_FILE}.tmp" "$CACHE_FILE" || \
    echo '{"error": "jq merge failed"}' > "${CACHE_FILE}.tmp"

rm -f "$TEMP_FILE"
echo "✅ Reuters geopolitics data cached"
