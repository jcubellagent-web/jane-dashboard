#!/bin/bash
# Send a push notification to all subscribed dashboard clients
# Usage: push-notify.sh "Title" "Body" [tag]
TITLE="${1:-Jane}"
BODY="${2:-Notification}"
TAG="${3:-jane}"
curl -s -X POST http://localhost:3000/api/push/send \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"$TITLE\",\"body\":\"$BODY\",\"tag\":\"$TAG\"}"
