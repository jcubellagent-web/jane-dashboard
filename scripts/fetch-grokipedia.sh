#!/bin/bash
# Fetch trending/featured content from Grokipedia for daily brief
# Usage: bash fetch-grokipedia.sh

CACHE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"

# Fetch the main page for trending topics
CONTENT=$(curl -sL --max-time 15 "https://grokipedia.com" | head -c 50000)

# Extract readable text
READABLE=$(echo "$CONTENT" | python3 -c "
import sys, json, re
html = sys.stdin.read()
# Strip tags
text = re.sub(r'<[^>]+>', ' ', html)
text = re.sub(r'\s+', ' ', text).strip()
# Truncate
print(text[:3000])
" 2>/dev/null)

# Also try trending/recent if available
TRENDING=$(curl -sL --max-time 10 "https://grokipedia.com/trending" 2>/dev/null | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub(r'<[^>]+>', ' ', html)
text = re.sub(r'\s+', ' ', text).strip()
print(text[:2000])
" 2>/dev/null)

# Build JSON entry
python3 -c "
import json, sys

cache_path = '$CACHE'
try:
    with open(cache_path) as f:
        cache = json.load(f)
except:
    cache = {}

cache['grokipedia'] = {
    'source': 'grokipedia.com',
    'mainPage': '''$READABLE'''[:2000],
    'trending': '''$TRENDING'''[:1500],
    'fetchedAt': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
}

with open(cache_path, 'w') as f:
    json.dump(cache, f, indent=2)

print('Grokipedia data cached.')
"
