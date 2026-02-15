#!/bin/bash
# Fetch Crunchbase News RSS feed - VC/PE deal flow and funding rounds
# Output: JSON object with recent stories

set -euo pipefail

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TMP_FILE=$(mktemp)
RSS_URL="https://news.crunchbase.com/feed/"

# Fetch and parse RSS feed
curl -sL "$RSS_URL" | python3 -c "
import sys, xml.etree.ElementTree as ET, json
from datetime import datetime

try:
    tree = ET.parse(sys.stdin)
    root = tree.getroot()
    
    items = []
    for item in root.findall('.//item')[:10]:  # Top 10 stories
        title = item.find('title')
        link = item.find('link')
        pubDate = item.find('pubDate')
        description = item.find('description')
        
        items.append({
            'title': title.text if title is not None else '',
            'url': link.text if link is not None else '',
            'published': pubDate.text if pubDate is not None else '',
            'description': description.text[:200] + '...' if description is not None and len(description.text) > 200 else (description.text if description is not None else '')
        })
    
    print(json.dumps(items, indent=2))
except Exception as e:
    print(json.dumps({'error': str(e)}), file=sys.stderr)
    print('[]')
" > "$TMP_FILE" 2>/dev/null || echo '[]' > "$TMP_FILE"

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson news "$(cat $TMP_FILE)" '.crunchbaseNews = $news' "$CACHE_FILE" > "${CACHE_FILE}.tmp"
  mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"crunchbaseNews\": $(cat $TMP_FILE)}" > "$CACHE_FILE"
fi

# Output for verification
cat "$TMP_FILE"
rm "$TMP_FILE"
