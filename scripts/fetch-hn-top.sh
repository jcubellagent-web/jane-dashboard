#!/bin/bash
# Fetch top Hacker News stories (AI/tech/crypto focused)
# Output: JSON array of relevant stories

set -euo pipefail

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TMP_FILE=$(mktemp)

# Fetch top 500 story IDs
TOP_IDS=$(curl -s "https://hacker-news.firebaseio.com/v0/topstories.json")

# Keywords for filtering
KEYWORDS="AI|artificial intelligence|machine learning|ML|GPT|LLM|crypto|blockchain|bitcoin|ethereum|tech|startup|venture|funding|Y Combinator|OpenAI|Anthropic|AGI"

echo "[" > "$TMP_FILE"
count=0
max_stories=10

for id in $(echo "$TOP_IDS" | jq -r '.[:50][]'); do
  if [ $count -ge $max_stories ]; then
    break
  fi
  
  story=$(curl -s "https://hacker-news.firebaseio.com/v0/item/${id}.json")
  title=$(echo "$story" | jq -r '.title // ""')
  
  # Check if title matches keywords (case insensitive)
  if echo "$title" | grep -iEq "$KEYWORDS"; then
    if [ $count -gt 0 ]; then
      echo "," >> "$TMP_FILE"
    fi
    echo "$story" | jq '{
      id,
      title,
      url,
      score,
      by,
      time,
      descendants
    }' >> "$TMP_FILE"
    count=$((count + 1))
  fi
done

echo "]" >> "$TMP_FILE"

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson hn "$(cat $TMP_FILE)" '.hackerNews = $hn' "$CACHE_FILE" > "${CACHE_FILE}.tmp"
  mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"hackerNews\": $(cat $TMP_FILE)}" > "$CACHE_FILE"
fi

# Output for verification
cat "$TMP_FILE"
rm "$TMP_FILE"
