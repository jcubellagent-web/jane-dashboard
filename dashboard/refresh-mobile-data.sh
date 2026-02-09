#!/bin/bash
cd /Users/jc_agent/.openclaw/workspace/dashboard
curl -s http://localhost:3000/api/system > system-status.json 2>/dev/null
curl -s http://localhost:3000/api/usage-today > usage-today.json 2>/dev/null
