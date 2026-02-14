#!/bin/bash
# Fetch hot AI/tech posts from Reddit (no auth needed, public JSON)

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
USER_AGENT="OpenClaw-Agent/1.0 (by /u/JaneAgentAI)"

SUBREDDITS=("MachineLearning" "artificial" "technology")
ALL_POSTS="[]"

for sub in "${SUBREDDITS[@]}"; do
  echo "Fetching r/$sub..."
  RESPONSE=$(curl -s "https://www.reddit.com/r/${sub}/hot.json?limit=10" \
    -H "User-Agent: $USER_AGENT")
  
  if [ $? -eq 0 ] && [ -n "$RESPONSE" ]; then
    # Extract posts
    POSTS=$(echo "$RESPONSE" | jq -c '[.data.children[].data | {
      title: .title,
      author: .author,
      subreddit: .subreddit,
      score: .score,
      num_comments: .num_comments,
      url: .url,
      permalink: ("https://reddit.com" + .permalink),
      created_utc: .created_utc
    }]')
    
    # Merge with ALL_POSTS
    ALL_POSTS=$(echo "$ALL_POSTS" | jq --argjson posts "$POSTS" '. + $posts')
  fi
done

# Sort by score, take top 15
SORTED=$(echo "$ALL_POSTS" | jq -c 'sort_by(-.score) | .[0:15]')

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson posts "$SORTED" '.redditAI = $posts' "$CACHE_FILE" > "${CACHE_FILE}.tmp" && mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"redditAI\": $SORTED}" > "$CACHE_FILE"
fi

echo "✅ Reddit AI: Fetched $(echo "$SORTED" | jq 'length') top posts from ${#SUBREDDITS[@]} subreddits"
