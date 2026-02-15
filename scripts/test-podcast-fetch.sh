#!/bin/bash
# Test version - fetch only 2 podcasts
set -e

WORKSPACE="/Users/jc_agent/.openclaw/workspace"
TRANSCRIPT_DIR="${WORKSPACE}/podcast-transcripts"
TEMP_DIR="/tmp/podcast-fetch-$$"

mkdir -p "${TRANSCRIPT_DIR}"
mkdir -p "${TEMP_DIR}"

# Test with just 2 podcasts
PODCAST_NAMES=("all-in" "pomp")
PODCAST_CHANNELS=("UCESLZhusAkFfsNsApnjF_Cg" "UCevXpeL8cNyAnww-NqJ4m2w")
PODCAST_HANDLES=("@allin" "@AnthonyPompliano")

clean_subtitles() {
    local file="$1"
    local output="$2"
    
    if [[ ! -f "$file" ]]; then
        echo "ERROR: Subtitle file not found: $file" >&2
        return 1
    fi
    
    if grep -q "WEBVTT" "$file"; then
        sed -e '/^WEBVTT/d' \
            -e '/^Kind:/d' \
            -e '/^Language:/d' \
            -e '/^[0-9][0-9]:[0-9][0-9]/d' \
            -e '/^$/d' \
            -e 's/<[^>]*>//g' \
            -e '/^[0-9]*$/d' \
            "$file" | awk '!seen[$0]++' > "$output"
    else
        sed -e '/^[0-9]*$/d' \
            -e '/^[0-9][0-9]:[0-9][0-9]/d' \
            -e '/^$/d' \
            -e 's/<[^>]*>//g' \
            "$file" | awk '!seen[$0]++' > "$output"
    fi
    
    sed -i '' 's/\([.!?]\)\([A-Z]\)/\1 \2/g' "$output" 2>/dev/null || true
}

fetch_podcast() {
    local name="$1"
    local channel_id="$2"
    local handle="$3"
    
    echo "========================================"
    echo "Fetching: $name ($handle)"
    echo "========================================"
    
    echo "Getting latest video..."
    local video_url=$(yt-dlp --flat-playlist --print url "https://www.youtube.com/$handle/videos" 2>/dev/null | head -1)
    
    if [[ -z "$video_url" ]]; then
        echo "ERROR: Could not find latest video for $name" >&2
        return 1
    fi
    
    local video_id=$(echo "$video_url" | sed 's/.*v=\([^&]*\).*/\1/' | sed 's/.*\/\([^\/]*\)$/\1/')
    echo "Latest video ID: $video_id"
    
    local video_title=$(yt-dlp --print title "$video_url" 2>/dev/null)
    local upload_date=$(yt-dlp --print upload_date "$video_url" 2>/dev/null)
    local formatted_date="${upload_date:0:4}-${upload_date:4:2}-${upload_date:6:2}"
    
    echo "Title: $video_title"
    echo "Upload date: $formatted_date"
    
    echo "Downloading auto-captions..."
    cd "${TEMP_DIR}"
    
    if yt-dlp --write-auto-sub --skip-download --sub-lang en --sub-format vtt --output "${name}.%(ext)s" "$video_url" 2>/dev/null; then
        echo "Auto-captions downloaded successfully"
    else
        echo "WARNING: Could not download auto-captions for $name" >&2
        cd - >/dev/null
        return 1
    fi
    
    local subtitle_file=$(find "${TEMP_DIR}" -name "${name}.en.*" -type f | head -1)
    
    if [[ -z "$subtitle_file" ]]; then
        echo "ERROR: Subtitle file not found for $name" >&2
        cd - >/dev/null
        return 1
    fi
    
    local output_file="${TRANSCRIPT_DIR}/${formatted_date}-${name}.txt"
    echo "Cleaning subtitles..."
    clean_subtitles "$subtitle_file" "$output_file"
    
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
    
    rm -f "$subtitle_file"
    cd - >/dev/null
    
    return 0
}

echo "========================================"
echo "Podcast Transcript Fetcher (TEST)"
echo "Started: $(date)"
echo "========================================"
echo ""

SUCCESS=0
FAILED=0

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

rm -rf "${TEMP_DIR}"

echo "========================================"
echo "Summary"
echo "========================================"
echo "Successful: $SUCCESS"
echo "Failed: $FAILED"
echo ""
echo "Finished: $(date)"
