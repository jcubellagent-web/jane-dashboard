#!/bin/bash
# Fetch AI-related posts from Bluesky Public API
# Output: JSON object with top AI posts

set -euo pipefail

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TMP_FILE=$(mktemp)
API_URL="https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?q=AI&sort=top&limit=10"

# Fetch Bluesky data
curl -sL "$API_URL" | jq '{
  posts: [.posts[]? | {
    text: .record.text,
    author: .author.handle,
    created: .record.createdAt,
    likes: .likeCount,
    replies: .replyCount,
    reposts: .repostCount,
    uri: .uri
  }]
}' > "$TMP_FILE" 2>/dev/null || echo '{"posts": [], "error": "API unavailable"}' > "$TMP_FILE"

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson data "$(cat $TMP_FILE)" '.blueskyAI = $data' "$CACHE_FILE" > "${CACHE_FILE}.tmp"
  mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"blueskyAI\": $(cat $TMP_FILE)}" > "$CACHE_FILE"
fi

# Output for verification
cat "$TMP_FILE"
rm "$TMP_FILE"
