#!/bin/bash
# Fetch AI job posting trends from LinkedIn via Google search
# Output: JSON with job posting count/trending data

set -euo pipefail

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TMP_FILE=$(mktemp)

# Use Google search to estimate AI job postings on LinkedIn
# (This is a proxy metric - actual count requires LinkedIn API or scraping)
SEARCH_QUERY="AI+engineer+jobs+posted+today+site:linkedin.com"
GOOGLE_URL="https://www.google.com/search?q=${SEARCH_QUERY}"

# Fetch and extract rough count from Google results
curl -sL -A "Mozilla/5.0" "$GOOGLE_URL" | python3 -c "
import sys, json, re

try:
    html = sys.stdin.read()
    
    # Try to extract result count from Google
    count_pattern = r'About ([0-9,]+) results'
    match = re.search(count_pattern, html)
    
    count = match.group(1) if match else 'N/A'
    
    result = {
        'metric': 'AI job postings (LinkedIn, today)',
        'estimated_count': count,
        'source': 'Google search proxy',
        'query': '${SEARCH_QUERY}',
        'note': 'Rough estimate - actual count requires LinkedIn API'
    }
    
    print(json.dumps(result, indent=2))
except Exception as e:
    print(json.dumps({'error': str(e), 'metric': 'AI job postings', 'estimated_count': 'N/A'}), file=sys.stderr)
    print('{\"metric\": \"AI job postings\", \"estimated_count\": \"N/A\"}')
" > "$TMP_FILE" 2>/dev/null || echo '{"metric": "AI job postings", "estimated_count": "N/A"}' > "$TMP_FILE"

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson data "$(cat $TMP_FILE)" '.aiJobsPulse = $data' "$CACHE_FILE" > "${CACHE_FILE}.tmp"
  mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"aiJobsPulse\": $(cat $TMP_FILE)}" > "$CACHE_FILE"
fi

# Output for verification
cat "$TMP_FILE"
rm "$TMP_FILE"
