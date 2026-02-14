#!/bin/bash
# Query Qwen 2.5 Coder on Mini #2 via Ollama API
# Usage: echo "prompt" | qwen-query.sh
# Or: qwen-query.sh "prompt"
PROMPT="${1:-$(cat)}"
curl -s http://100.66.132.34:11434/api/generate \
  -d "{\"model\":\"qwen2.5-coder:7b\",\"prompt\":$(echo "$PROMPT" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))'),\"stream\":false}" \
  | python3 -c 'import json,sys;print(json.load(sys.stdin).get("response",""))'
