#!/bin/bash
# Browser lock for sub-agent serialization
# Usage:
#   browser-lock.sh acquire [label] [timeout_seconds]  — blocks until lock acquired
#   browser-lock.sh release                             — releases lock
#   browser-lock.sh status                              — shows current lock holder

LOCK_FILE="/tmp/openclaw-browser-lock"
LOCK_INFO="/tmp/openclaw-browser-lock-info"

case "$1" in
  acquire)
    LABEL="${2:-unknown}"
    TIMEOUT="${3:-300}"
    ELAPSED=0
    while ! mkdir "$LOCK_FILE" 2>/dev/null; do
      if [ $ELAPSED -ge $TIMEOUT ]; then
        echo "TIMEOUT: Could not acquire browser lock after ${TIMEOUT}s"
        echo "Current holder: $(cat "$LOCK_INFO" 2>/dev/null || echo 'unknown')"
        exit 1
      fi
      sleep 5
      ELAPSED=$((ELAPSED + 5))
    done
    echo "$LABEL (pid $$, $(date '+%Y-%m-%d %H:%M:%S'))" > "$LOCK_INFO"
    echo "ACQUIRED: Browser lock held by $LABEL"
    ;;
  release)
    rm -rf "$LOCK_FILE" "$LOCK_INFO"
    echo "RELEASED: Browser lock freed"
    ;;
  status)
    if [ -d "$LOCK_FILE" ]; then
      echo "LOCKED: $(cat "$LOCK_INFO" 2>/dev/null || echo 'unknown')"
    else
      echo "FREE: No browser lock held"
    fi
    ;;
  *)
    echo "Usage: browser-lock.sh {acquire|release|status} [label] [timeout]"
    exit 1
    ;;
esac
