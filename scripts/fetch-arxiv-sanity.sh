#!/bin/bash
# Fetch recent AI/ML papers from arXiv API
# Output: JSON object with recent papers

set -euo pipefail

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TMP_FILE=$(mktemp)
API_URL="http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=10"

# Fetch and parse arXiv XML feed
curl -sL "$API_URL" | python3 -c "
import sys, xml.etree.ElementTree as ET, json

try:
    tree = ET.parse(sys.stdin)
    root = tree.getroot()
    
    # arXiv uses Atom namespace
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    papers = []
    for entry in root.findall('atom:entry', ns)[:10]:
        title = entry.find('atom:title', ns)
        authors = entry.findall('atom:author', ns)
        published = entry.find('atom:published', ns)
        summary = entry.find('atom:summary', ns)
        link = entry.find('atom:id', ns)
        
        author_names = ', '.join([a.find('atom:name', ns).text for a in authors[:3]])
        
        papers.append({
            'title': title.text.strip().replace('\n', ' ') if title is not None else '',
            'authors': author_names,
            'published': published.text if published is not None else '',
            'summary': summary.text[:200] + '...' if summary is not None and len(summary.text) > 200 else (summary.text.strip() if summary is not None else ''),
            'url': link.text if link is not None else ''
        })
    
    print(json.dumps(papers, indent=2))
except Exception as e:
    print(json.dumps({'error': str(e)}), file=sys.stderr)
    print('[]')
" > "$TMP_FILE" 2>/dev/null || echo '[]' > "$TMP_FILE"

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson papers "$(cat $TMP_FILE)" '.arxivSanity = $papers' "$CACHE_FILE" > "${CACHE_FILE}.tmp"
  mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"arxivSanity\": $(cat $TMP_FILE)}" > "$CACHE_FILE"
fi

# Output for verification
cat "$TMP_FILE"
rm "$TMP_FILE"
