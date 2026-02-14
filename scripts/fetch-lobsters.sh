#!/bin/bash
# Fetch hot tech stories from Lobste.rs (no auth needed)

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"

# Fetch hottest stories
RESPONSE=$(curl -s "https://lobste.rs/hottest.json" \
  -H "User-Agent: OpenClaw-Agent/1.0")

if [ $? -ne 0 ] || [ -z "$RESPONSE" ]; then
  echo "❌ Lobste.rs API fetch failed"
  exit 1
fi

# Filter for AI/ML/tech tags and format
AI_ML_TAGS=("ai" "ml" "programming" "security" "crypto" "blockchain" "python" "javascript")

FILTERED=$(echo "$RESPONSE" | jq -c --argjson tags "$(printf '%s\n' "${AI_ML_TAGS[@]}" | jq -R . | jq -s .)" '
  [.[] | select(.tags as $story_tags | $tags | any(. as $tag | $story_tags | index($tag))) | {
    title: .title,
    author: .submitter_user,
    score: .score,
    comment_count: .comment_count,
    url: .url,
    short_id_url: .short_id_url,
    tags: .tags,
    created_at: .created_at
  }] | .[0:10]
')

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson stories "$FILTERED" '.lobsters = $stories' "$CACHE_FILE" > "${CACHE_FILE}.tmp" && mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"lobsters\": $FILTERED}" > "$CACHE_FILE"
fi

echo "✅ Lobste.rs: Fetched $(echo "$FILTERED" | jq 'length') AI/ML/tech stories"
