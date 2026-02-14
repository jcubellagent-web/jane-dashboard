#!/bin/bash
# Fetch trending GitHub repositories (AI/ML focus)

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"

# Fetch daily trending repos
RESPONSE=$(curl -s "https://github.com/trending?since=daily" \
  -H "User-Agent: OpenClaw-Agent/1.0")

if [ $? -ne 0 ] || [ -z "$RESPONSE" ]; then
  echo "❌ GitHub Trending fetch failed"
  exit 1
fi

# Parse HTML to extract repo info (simplified parsing)
# Extract repo names, descriptions, and stars
REPOS=$(echo "$RESPONSE" | grep -o 'href="/[^"]*"' | grep -v 'http' | \
  sed 's/href="//;s/"$//' | grep '^/[^/]*/[^/]*$' | head -20 | \
  while read repo; do
    # Try to filter AI/ML repos by common keywords in repo path
    if echo "$repo" | grep -iE '(ai|ml|llm|agent|neural|deep|learning|gpt|transformer|diffusion)' > /dev/null; then
      echo "{\"repo\":\"$repo\",\"url\":\"https://github.com$repo\"}"
    fi
  done | jq -s '.')

# If no AI/ML specific repos found, just take first 5 trending
if [ "$(echo "$REPOS" | jq 'length')" -eq 0 ]; then
  REPOS=$(echo "$RESPONSE" | grep -o 'href="/[^"]*"' | grep -v 'http' | \
    sed 's/href="//;s/"$//' | grep '^/[^/]*/[^/]*$' | head -5 | \
    while read repo; do
      echo "{\"repo\":\"$repo\",\"url\":\"https://github.com$repo\"}"
    done | jq -s '.')
fi

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson repos "$REPOS" '.githubTrending = $repos' "$CACHE_FILE" > "${CACHE_FILE}.tmp" && mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"githubTrending\": $REPOS}" > "$CACHE_FILE"
fi

echo "✅ GitHub Trending: Fetched $(echo "$REPOS" | jq 'length') repos"
