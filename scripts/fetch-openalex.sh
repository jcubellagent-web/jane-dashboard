#!/bin/bash
# Fetch recent AI papers from OpenAlex API (free, no key needed)

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"

# Get yesterday's date for filtering recent papers
YESTERDAY=$(date -v-1d +%Y-%m-%d)

# Fetch recent AI papers (concept C154945302 = Artificial Intelligence)
# Sort by citations, get top 5
RESPONSE=$(curl -s "https://api.openalex.org/works?filter=concept.id:C154945302,from_publication_date:${YESTERDAY}&sort=cited_by_count:desc&per_page=5" \
  -H "User-Agent: OpenClaw-Agent (jcubellagent@gmail.com)")

if [ $? -ne 0 ] || [ -z "$RESPONSE" ]; then
  echo "❌ OpenAlex API fetch failed"
  exit 1
fi

# Parse and format the response
PAPERS=$(echo "$RESPONSE" | jq -c '[.results[] | {
  title: .title,
  authors: [.authorships[0:3][].author.display_name] | join(", "),
  publication_date: .publication_date,
  citations: .cited_by_count,
  url: .id,
  abstract: .abstract
}]')

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson papers "$PAPERS" '.openAlex = $papers' "$CACHE_FILE" > "${CACHE_FILE}.tmp" && mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"openAlex\": $PAPERS}" > "$CACHE_FILE"
fi

echo "✅ OpenAlex: Fetched $(echo "$PAPERS" | jq 'length') recent AI papers"
