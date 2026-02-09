#!/bin/bash
# ffmpeg-remote.sh — Offload ffmpeg to Mac Mini #2, fallback to local
set -euo pipefail

REMOTE="mini2"
REMOTE_FFMPEG="/opt/homebrew/bin/ffmpeg"
REMOTE_TMP="/tmp/ffmpeg-remote-$$"

usage() { echo "Usage: $0 -i <input> -o <output> [ffmpeg args...]"; exit 1; }

INPUT="" OUTPUT="" FFARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -i) INPUT="$2"; shift 2;;
    -o) OUTPUT="$2"; shift 2;;
    *) FFARGS+=("$1"); shift;;
  esac
done
[[ -z "$INPUT" || -z "$OUTPUT" ]] && usage

INPUT_BASE=$(basename "$INPUT")
OUTPUT_BASE=$(basename "$OUTPUT")

# Check Mini #2 reachability
if ssh -o ConnectTimeout=3 "$REMOTE" true 2>/dev/null; then
  echo "→ Using remote ffmpeg on Mini #2"
  ssh "$REMOTE" "mkdir -p $REMOTE_TMP"
  scp -q "$INPUT" "$REMOTE:$REMOTE_TMP/$INPUT_BASE"
  ssh "$REMOTE" "$REMOTE_FFMPEG -y -i '$REMOTE_TMP/$INPUT_BASE' ${FFARGS[*]} '$REMOTE_TMP/$OUTPUT_BASE'" 2>&1
  scp -q "$REMOTE:$REMOTE_TMP/$OUTPUT_BASE" "$OUTPUT"
  ssh "$REMOTE" "rm -rf $REMOTE_TMP"
  echo "✓ Done (remote)"
else
  echo "→ Mini #2 unreachable, using local ffmpeg"
  ffmpeg -y -i "$INPUT" "${FFARGS[@]}" "$OUTPUT" 2>&1
  echo "✓ Done (local fallback)"
fi
