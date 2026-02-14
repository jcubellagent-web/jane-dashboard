#!/bin/bash
# Fetch trending HuggingFace models
# Output: JSON array of top 5 trending models

set -euo pipefail

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
TMP_FILE=$(mktemp)

# Scrape trending models page
TRENDING_HTML=$(curl -s "https://huggingface.co/models?sort=trending")

# Extract model data using simple parsing
# HF uses data attributes we can grep for
echo "[" > "$TMP_FILE"

# Parse out model cards (looking for model IDs in URLs)
echo "$TRENDING_HTML" | grep -oE 'href="/[^/]+/[^/"]+' | head -20 | while IFS= read -r line; do
  model_id=$(echo "$line" | sed 's|href="/||')
  
  # Skip non-model pages
  if [[ "$model_id" == "models"* ]] || [[ "$model_id" == "docs"* ]] || [[ "$model_id" == "spaces"* ]]; then
    continue
  fi
  
  # Fetch model API info
  model_data=$(curl -s "https://huggingface.co/api/models/${model_id}" 2>/dev/null || echo "{}")
  
  if [ "$(echo "$model_data" | jq 'has("id")')" = "true" ]; then
    echo "$model_data" | jq '{
      id,
      author: (.author // (.id | split("/")[0])),
      name: (.id | split("/")[1]),
      description: (.description // ""),
      likes,
      downloads,
      tags: (.tags[:5]),
      pipeline_tag
    }' >> "$TMP_FILE"
    echo "," >> "$TMP_FILE"
  fi
done

# Remove trailing comma and close array
sed -i.bak '$ s/,$//' "$TMP_FILE"
echo "]" >> "$TMP_FILE"

# Limit to top 5 and clean up
jq '.[0:5]' "$TMP_FILE" > "${TMP_FILE}.clean"
mv "${TMP_FILE}.clean" "$TMP_FILE"

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson hf "$(cat $TMP_FILE)" '.huggingfaceTrending = $hf' "$CACHE_FILE" > "${CACHE_FILE}.tmp"
  mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"huggingfaceTrending\": $(cat $TMP_FILE)}" > "$CACHE_FILE"
fi

# Output for verification
cat "$TMP_FILE"
rm "$TMP_FILE" "${TMP_FILE}.bak" 2>/dev/null || true
