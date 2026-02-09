#!/bin/bash
# RAG Query - Search indexed documents on Mini #2
# Usage: ./rag-query.sh "your question here"
# Options:
#   --search    Search only (no LLM answer)
#   --model     LLM model to use (default: llama3.1:8b)

set -e

QUERY=""
MODE="ask"
MODEL="llama3.1:8b"

while [[ $# -gt 0 ]]; do
  case $1 in
    --search) MODE="search"; shift ;;
    --model) MODEL="$2"; shift 2 ;;
    *) QUERY="$QUERY $1"; shift ;;
  esac
done

QUERY=$(echo "$QUERY" | xargs)  # trim

if [ -z "$QUERY" ]; then
  echo "Usage: $0 [--search] [--model name] \"your query\""
  exit 1
fi

echo "🔍 RAG $MODE: $QUERY"
echo "📡 Connecting to Mini #2..."

ssh mini2 "cd /Users/jcagent2/rag && RAG_LLM_MODEL='$MODEL' node index.js $MODE $QUERY"
