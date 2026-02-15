#!/bin/bash
# Fetch latest podcast episode transcripts from YouTube auto-captions
# Uses yt-dlp to download auto-generated subtitles

set -e

# Configuration
WORKSPACE="/Users/jc_agent/.openclaw/workspace"
TRANSCRIPT_DIR="${WORKSPACE}/podcast-transcripts"
TEMP_DIR="/tmp/podcast-fetch-$$"

# Create directories
mkdir -p "${TRANSCRIPT_DIR}"
mkdir -p "${TEMP_DIR}"

# Podcast configuration arrays (parallel arrays for Bash 3.2 compatibility)
# Original 5 podcasts
PODCAST_NAMES=("all-in" "pomp" "unchained" "twis" "the-daily")
PODCAST_CHANNELS=("UCESLZhusAkFfsNsApnjF_Cg" "UCevXpeL8cNyAnww-NqJ4m2w" "UCWiiMnsnw5Isc2PP1to9nNw" "UC1UbgWkb41KrhF824U6t6uQ" "UCkdnY2hNC0sdlVXPtWuNQ8g")
PODCAST_HANDLES=("@allin" "@AnthonyPompliano" "@unchained" "@thisweekinstartups" "@thedaily")

# New 9 podcasts added Feb 2026
PODCAST_NAMES+=("acquired" "bg2" "20vc" "bankless" "hardfork" "turpentine" "profg" "lennys" "oddlots")
PODCAST_CHANNELS+=("UCyFqFYfTW2VoIQKylJ04Rtw" "UC-yRDvpR99LUc5l7i7jLzew" "UCf0PBRjhf0rF8fWBIxTuoWA" "UCAl9Ld79qaZxp9JzEOwd3aA" "UCZcR2SVWaGWNlMqPxvQS3vw" "UCIiUCv0yvVGx2XYU4IJ2CKg" "UC1E1SVcVyU3ntWMSQEp38Yw" "UC6t1O76G0jYXOAoYCm153dA" "UChF5O40UBqAc82I7-i5ig6A")
PODCAST_HANDLES+=("@AcquiredFM" "@Bg2Pod" "@20VC" "@Bankless" "@hardfork" "@TurpentineVC" "@TheProfGPod" "@LennysPodcast" "@BloombergPodcasts")

# Function to clean VTT/SRT to plain text
clean_subtitles() {
    local file="$1"
    local output="$2"
    
    if [[ ! -f "$file" ]]; then
        echo "ERROR: Subtitle file not found: $file" >&2
        return 1
    fi
    
    # Remove VTT/SRT formatting, timestamps, and duplicates
    # Keep only the actual text content
    if grep -q "WEBVTT" "$file"; then
        # VTT format
        sed -e '/^WEBVTT/d' \
            -e '/^Kind:/d' \
            -e '/^Language:/d' \
            -e '/^[0-9][0-9]:[0-9][0-9]/d' \
            -e '/^$/d' \
            -e 's/<[^>]*>//g' \
            -e '/^[0-9]*$/d' \
            "$file" | awk '!seen[$0]++' > "$output"
    else
        # SRT format
        sed -e '/^[0-9]*$/d' \
            -e '/^[0-9][0-9]:[0-9][0-9]/d' \
            -e '/^$/d' \
            -e 's/<[^>]*>//g' \
            "$file" | awk '!seen[$0]++' > "$output"
    fi
    
    # Add spaces between sentences if missing (macOS sed needs empty string after -i)
    sed -i '' 's/\([.!?]\)\([A-Z]\)/\1 \2/g' "$output" 2>/dev/null || true
}

# Function to fetch latest episode for a podcast
fetch_podcast() {
    local name="$1"
    local channel_id="$2"
    local handle="$3"
    
    echo "========================================"
    echo "Fetching: $name ($handle)"
    echo "========================================"
    
    # Get latest video ID from channel
    echo "Getting latest video..."
    local video_url=$(yt-dlp --flat-playlist --print url "https://www.youtube.com/$handle/videos" 2>/dev/null | head -1)
    
    if [[ -z "$video_url" ]]; then
        echo "ERROR: Could not find latest video for $name" >&2
        return 1
    fi
    
    local video_id=$(echo "$video_url" | sed 's/.*v=\([^&]*\).*/\1/' | sed 's/.*\/\([^\/]*\)$/\1/')
    echo "Latest video ID: $video_id"
    
    # Get video title and upload date
    local video_title=$(yt-dlp --print title "$video_url" 2>/dev/null)
    local upload_date=$(yt-dlp --print upload_date "$video_url" 2>/dev/null)
    
    # Format date as YYYY-MM-DD
    local formatted_date="${upload_date:0:4}-${upload_date:4:2}-${upload_date:6:2}"
    
    echo "Title: $video_title"
    echo "Upload date: $formatted_date"
    
    # Download auto-generated captions
    echo "Downloading auto-captions..."
    cd "${TEMP_DIR}"
    
    # Try to get English auto-generated captions
    if yt-dlp --write-auto-sub --skip-download --sub-lang en --sub-format vtt --output "${name}.%(ext)s" "$video_url" 2>/dev/null; then
        echo "Auto-captions downloaded successfully"
    else
        echo "WARNING: Could not download auto-captions for $name" >&2
        cd - >/dev/null
        return 1
    fi
    
    # Find the subtitle file
    local subtitle_file=$(find "${TEMP_DIR}" -name "${name}.en.*" -type f | head -1)
    
    if [[ -z "$subtitle_file" ]]; then
        echo "ERROR: Subtitle file not found for $name" >&2
        cd - >/dev/null
        return 1
    fi
    
    # Clean and save transcript
    local output_file="${TRANSCRIPT_DIR}/${formatted_date}-${name}.txt"
    echo "Cleaning subtitles..."
    clean_subtitles "$subtitle_file" "$output_file"
    
    # Add metadata header
    {
        echo "==================================="
        echo "Podcast: $name"
        echo "Title: $video_title"
        echo "Date: $formatted_date"
        echo "Video: https://youtube.com/watch?v=$video_id"
        echo "==================================="
        echo ""
        cat "$output_file"
    } > "${output_file}.tmp" && mv "${output_file}.tmp" "$output_file"
    
    echo "✓ Transcript saved to: $output_file"
    echo "Size: $(wc -w < "$output_file") words"
    
    # Clean up temp files
    rm -f "$subtitle_file"
    cd - >/dev/null
    
    return 0
}

# Main execution
echo "========================================"
echo "Podcast Transcript Fetcher"
echo "Started: $(date)"
echo "========================================"
echo ""

SUCCESS=0
FAILED=0

# Loop through all podcasts
for i in "${!PODCAST_NAMES[@]}"; do
    name="${PODCAST_NAMES[$i]}"
    channel="${PODCAST_CHANNELS[$i]}"
    handle="${PODCAST_HANDLES[$i]}"
    
    if fetch_podcast "$name" "$channel" "$handle"; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
    fi
    echo ""
done

# Clean up temp directory
rm -rf "${TEMP_DIR}"

echo "========================================"
echo "Summary"
echo "========================================"
echo "Successful: $SUCCESS"
echo "Failed: $FAILED"
echo "Transcripts saved to: $TRANSCRIPT_DIR"
echo ""
echo "Finished: $(date)"
