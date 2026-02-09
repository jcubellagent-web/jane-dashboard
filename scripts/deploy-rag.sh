#!/bin/bash
# Deploy RAG pipeline to Mini #2
# Run this when Mini #2 is back online
set -e

echo "📦 Creating directories on Mini #2..."
ssh mini2 'mkdir -p /Users/jcagent2/rag/docs'

echo "📄 Copying RAG script..."
scp /tmp/rag-index.js mini2:/Users/jcagent2/rag/index.js

echo "📚 Copying memory files for indexing..."
scp /Users/jc_agent/.openclaw/workspace/MEMORY.md mini2:/Users/jcagent2/rag/docs/
scp /Users/jc_agent/.openclaw/workspace/memory/*.md mini2:/Users/jcagent2/rag/docs/

echo "🔢 Indexing documents..."
ssh mini2 'cd /Users/jcagent2/rag && node index.js index ./docs'

echo "🤖 Pulling mistral:7b..."
ssh mini2 '/usr/local/bin/ollama pull mistral:7b'

echo "🧪 Testing with sample query..."
ssh mini2 'cd /Users/jcagent2/rag && node index.js ask "What was the memecoin trading result?"'

echo "✅ RAG pipeline deployed!"
