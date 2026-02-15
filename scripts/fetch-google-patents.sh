#!/bin/bash
# Fetch recent AI patents from Google Patents (via web scraping or public data)
# Output: JSON object with patent results

set -euo pipefail

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TMP_FILE=$(mktemp)

# Calculate date range (last 7 days for AI patents)
AFTER_DATE=$(date -v-7d "+%Y%m%d" 2>/dev/null || date -d '7 days ago' "+%Y%m%d")
BEFORE_DATE=$(date "+%Y%m%d")

# Google Patents search URL for AI patents
SEARCH_URL="https://patents.google.com/?q=artificial+intelligence&before=priority:${BEFORE_DATE}&after=priority:${AFTER_DATE}&oq=artificial+intelligence"

# Fetch and extract patent data (using simple text extraction from HTML)
curl -sL "$SEARCH_URL" | python3 -c "
import sys, json, re

try:
    html = sys.stdin.read()
    
    # Simple regex-based extraction (Google Patents has structured data)
    # This is a fallback; ideally we'd use their public BigQuery dataset
    patents = []
    
    # Try to extract patent titles and IDs from the HTML
    # (Note: This is fragile and may break if Google changes their layout)
    title_pattern = r'<span[^>]*result-title[^>]*>([^<]+)</span>'
    id_pattern = r'/patent/([A-Z0-9]+)'
    
    titles = re.findall(title_pattern, html)
    ids = re.findall(id_pattern, html)
    
    for i, (title, patent_id) in enumerate(zip(titles[:10], ids[:10])):
        patents.append({
            'title': title.strip(),
            'id': patent_id,
            'url': f'https://patents.google.com/patent/{patent_id}'
        })
    
    if not patents:
        patents = [{'note': 'Google Patents search returned no structured data - may need manual review', 'url': '${SEARCH_URL}'}]
    
    print(json.dumps(patents, indent=2))
except Exception as e:
    print(json.dumps([{'error': str(e), 'url': '${SEARCH_URL}'}]), file=sys.stderr)
    print('[{\"note\": \"Check Google Patents manually\", \"url\": \"${SEARCH_URL}\"}]')
" > "$TMP_FILE" 2>/dev/null || echo '[{"note": "Check Google Patents manually", "url": "'$SEARCH_URL'"}]' > "$TMP_FILE"

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson patents "$(cat $TMP_FILE)" '.googlePatents = $patents' "$CACHE_FILE" > "${CACHE_FILE}.tmp"
  mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"googlePatents\": $(cat $TMP_FILE)}" > "$CACHE_FILE"
fi

# Output for verification
cat "$TMP_FILE"
rm "$TMP_FILE"
