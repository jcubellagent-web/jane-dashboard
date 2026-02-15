#!/bin/bash
# Summarize podcast transcripts - extract key topics and quotes
# Focus areas: AI, enterprise SaaS, crypto, markets, startups

set -e

WORKSPACE="/Users/jc_agent/.openclaw/workspace"
TRANSCRIPT_DIR="${WORKSPACE}/podcast-transcripts"
OUTPUT_FILE="${WORKSPACE}/podcast-summary-$(date +%Y-%m-%d).md"

# Configuration
DAYS_BACK="${1:-7}"  # Default to last 7 days

# Keywords to search for (case insensitive)
KEYWORDS=(
    "AI|artificial intelligence|machine learning|LLM|GPT|Claude|OpenAI|Anthropic"
    "SaaS|enterprise software|B2B|software|cloud"
    "crypto|bitcoin|ethereum|blockchain|defi|web3|NFT|token"
    "market|stock|equity|trading|valuation|IPO|M&A|acquisition"
    "startup|venture|funding|raise|seed|series|exit"
)

# Function to extract relevant sections from a transcript
extract_relevant() {
    local file="$1"
    local context_lines=3  # Lines before and after match
    
    echo "## $(basename "$file" .txt)"
    echo ""
    
    # Get metadata from file header
    head -6 "$file" | tail -4
    echo ""
    
    # Search for each keyword category
    for keyword in "${KEYWORDS[@]}"; do
        if grep -iE "$keyword" "$file" >/dev/null 2>&1; then
            # Extract matching lines with context
            grep -iE "$keyword" "$file" | head -20
            echo ""
        fi
    done
    
    echo "---"
    echo ""
}

# Function to create summary with keyword highlighting
create_summary() {
    local file="$1"
    local output="$2"
    
    # Extract file metadata
    local podcast_name=$(grep "^Podcast:" "$file" | cut -d: -f2- | xargs)
    local title=$(grep "^Title:" "$file" | cut -d: -f2- | xargs)
    local date=$(grep "^Date:" "$file" | cut -d: -f2- | xargs)
    local video=$(grep "^Video:" "$file" | cut -d: -f2- | xargs)
    
    echo "### $podcast_name - $date" >> "$output"
    echo "" >> "$output"
    echo "**$title**" >> "$output"
    echo "" >> "$output"
    echo "🎥 [$video]($video)" >> "$output"
    echo "" >> "$output"
    
    # Extract key topics by searching for keywords
    local found_topics=0
    
    # AI Topics
    if grep -iE "AI|artificial intelligence|machine learning|LLM|GPT|Claude|OpenAI|Anthropic|model|neural" "$file" >/dev/null 2>&1; then
        echo "**🤖 AI Topics:**" >> "$output"
        grep -iE "AI|artificial intelligence|machine learning|LLM|GPT|Claude|OpenAI|Anthropic" "$file" | \
            grep -v "^===" | head -5 | sed 's/^/- /' >> "$output"
        echo "" >> "$output"
        found_topics=1
    fi
    
    # Crypto Topics
    if grep -iE "crypto|bitcoin|ethereum|blockchain|defi|web3|NFT|token|solana|base" "$file" >/dev/null 2>&1; then
        echo "**₿ Crypto Topics:**" >> "$output"
        grep -iE "crypto|bitcoin|ethereum|blockchain|defi|web3|NFT|token" "$file" | \
            grep -v "^===" | head -5 | sed 's/^/- /' >> "$output"
        echo "" >> "$output"
        found_topics=1
    fi
    
    # Market/Business Topics
    if grep -iE "market|valuation|IPO|M&A|acquisition|funding|raise|billion|trillion" "$file" >/dev/null 2>&1; then
        echo "**📈 Markets & Business:**" >> "$output"
        grep -iE "market|valuation|IPO|M&A|acquisition|funding|raise|billion" "$file" | \
            grep -v "^===" | head -5 | sed 's/^/- /' >> "$output"
        echo "" >> "$output"
        found_topics=1
    fi
    
    # Startup Topics
    if grep -iE "startup|founder|venture|seed|series|YC|accelerator|pitch" "$file" >/dev/null 2>&1; then
        echo "**🚀 Startup Topics:**" >> "$output"
        grep -iE "startup|founder|venture|seed|series" "$file" | \
            grep -v "^===" | head -5 | sed 's/^/- /' >> "$output"
        echo "" >> "$output"
        found_topics=1
    fi
    
    if [[ $found_topics -eq 0 ]]; then
        echo "_No relevant topics found in configured categories._" >> "$output"
        echo "" >> "$output"
    fi
    
    echo "---" >> "$output"
    echo "" >> "$output"
}

# Main execution
echo "========================================"
echo "Podcast Summary Generator"
echo "========================================"
echo "Analyzing transcripts from last $DAYS_BACK days"
echo "Output: $OUTPUT_FILE"
echo ""

# Initialize output file
cat > "$OUTPUT_FILE" << EOF
# Podcast Summary - $(date +"%B %d, %Y")

Extracted from podcasts over the last $DAYS_BACK days.

Topics: AI, Enterprise SaaS, Crypto, Markets, Startups

---

EOF

# Find transcripts from last N days
CUTOFF_DATE=$(date -v-${DAYS_BACK}d +%Y-%m-%d 2>/dev/null || date -d "${DAYS_BACK} days ago" +%Y-%m-%d)
echo "Cutoff date: $CUTOFF_DATE"
echo ""

COUNT=0
for transcript in "$TRANSCRIPT_DIR"/*.txt; do
    if [[ ! -f "$transcript" ]]; then
        continue
    fi
    
    # Extract date from filename (format: YYYY-MM-DD-podcast-name.txt)
    filename=$(basename "$transcript")
    file_date="${filename:0:10}"
    
    # Compare dates (simple string comparison works for YYYY-MM-DD format)
    if [[ "$file_date" > "$CUTOFF_DATE" ]] || [[ "$file_date" == "$CUTOFF_DATE" ]]; then
        echo "Processing: $filename ($file_date)"
        create_summary "$transcript" "$OUTPUT_FILE"
        COUNT=$((COUNT + 1))
    else
        echo "Skipping (too old): $filename ($file_date)"
    fi
done

echo ""
echo "========================================"
echo "Summary Complete"
echo "========================================"
echo "Processed: $COUNT transcripts"
echo "Output: $OUTPUT_FILE"
echo ""

# Show preview
echo "Preview (first 50 lines):"
echo "========================================"
head -50 "$OUTPUT_FILE"
echo "========================================"
echo ""
echo "Full summary saved to: $OUTPUT_FILE"
