#!/bin/bash
# Fetch top AI/tech headlines from NewsAPI.org (100 requests/day limit)

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
API_KEY=$(cat /Users/jc_agent/.openclaw/workspace/.secrets/newsapi_key.txt)

# Fetch top AI headlines from past 24h
RESPONSE=$(curl -s "https://newsapi.org/v2/everything?q=artificial+intelligence&sortBy=publishedAt&pageSize=10&apiKey=${API_KEY}")

if [ $? -ne 0 ] || [ -z "$RESPONSE" ]; then
  echo "❌ NewsAPI fetch failed"
  exit 1
fi

# Check for error in response
if echo "$RESPONSE" | jq -e '.status == "error"' > /dev/null 2>&1; then
  echo "❌ NewsAPI error: $(echo "$RESPONSE" | jq -r '.message')"
  exit 1
fi

# Parse and format articles
ARTICLES=$(echo "$RESPONSE" | jq -c '[.articles[] | {
  title: .title,
  source: .source.name,
  author: .author,
  description: .description,
  url: .url,
  publishedAt: .publishedAt,
  content: .content
}]')

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson articles "$ARTICLES" '.newsAPI = $articles' "$CACHE_FILE" > "${CACHE_FILE}.tmp" && mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"newsAPI\": $ARTICLES}" > "$CACHE_FILE"
fi

echo "✅ NewsAPI: Fetched $(echo "$ARTICLES" | jq 'length') AI/tech headlines"
