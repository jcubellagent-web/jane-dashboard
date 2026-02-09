#!/bin/bash
# whisper-remote.sh - Run Whisper transcription on Mini #2, fallback to local
# Usage: whisper-remote.sh <audio_file> [whisper_args...]

set -euo pipefail

REMOTE_HOST="mini2"
REMOTE_WHISPER="/Users/jcagent2/.local/bin/whisper"
REMOTE_TMP="/tmp/whisper-remote"
LOCAL_WHISPER="whisper"

AUDIO_FILE="$1"
shift
EXTRA_ARGS="${@:---model turbo --output_format txt}"

if [ ! -f "$AUDIO_FILE" ]; then
    echo "ERROR: File not found: $AUDIO_FILE" >&2
    exit 1
fi

BASENAME="$(basename "$AUDIO_FILE")"
OUTPUT_DIR="$(dirname "$AUDIO_FILE")"

run_remote() {
    echo "→ Transcribing on Mini #2 ($REMOTE_HOST)..."
    ssh "$REMOTE_HOST" "mkdir -p $REMOTE_TMP" || return 1
    scp -q "$AUDIO_FILE" "$REMOTE_HOST:$REMOTE_TMP/$BASENAME" || return 1
    ssh "$REMOTE_HOST" "export PATH=/opt/homebrew/bin:/usr/local/bin:\$PATH; $REMOTE_WHISPER $EXTRA_ARGS --output_dir $REMOTE_TMP '$REMOTE_TMP/$BASENAME'" || return 1
    scp -q "$REMOTE_HOST:$REMOTE_TMP/*" "$OUTPUT_DIR/" || return 1
    ssh "$REMOTE_HOST" "rm -rf $REMOTE_TMP" 2>/dev/null
    echo "✓ Done (remote). Output in $OUTPUT_DIR"
}

run_local() {
    echo "→ Transcribing locally..."
    $LOCAL_WHISPER $EXTRA_ARGS --output_dir "$OUTPUT_DIR" "$AUDIO_FILE"
    echo "✓ Done (local). Output in $OUTPUT_DIR"
}

# Try remote, fallback to local
if ssh -o ConnectTimeout=5 "$REMOTE_HOST" "true" 2>/dev/null; then
    run_remote || { echo "⚠ Remote failed, falling back to local..." >&2; run_local; }
else
    echo "⚠ Mini #2 unreachable, using local Whisper..." >&2
    run_local
fi
