#!/bin/bash
# Standalone trade price monitor - no AI needed
# Reads trading/positions.json, fetches prices, checks TP/SL, sends alerts

WORKSPACE="/Users/jc_agent/.openclaw/workspace"
POSITIONS_FILE="$WORKSPACE/trading/positions.json"
TEMP_FILE="/tmp/trade-monitor-$$.json"

# Check if positions file exists
if [ ! -f "$POSITIONS_FILE" ]; then
    echo "NO_REPLY"
    exit 0
fi

# Export for Python
export POSITIONS_FILE
export TEMP_FILE

# Read positions using Python
python3 <<'PYEOF'
import json
import sys
import os
import urllib.request
import urllib.error
from datetime import datetime

POSITIONS_FILE = os.environ['POSITIONS_FILE']
TEMP_FILE = os.environ['TEMP_FILE']

# Load positions
with open(POSITIONS_FILE, 'r') as f:
    data = json.load(f)

positions = data.get('positions', [])

# If no open positions, exit quietly
if not positions:
    print("NO_REPLY")
    sys.exit(0)

alerts = []
current_prices = {}

# Check each position
for pos in positions:
    token = pos.get('token', '')
    entry_price = pos.get('entryPrice', 0)
    amount = pos.get('amount', 0)
    contract = pos.get('contract', '')
    
    if not contract or not entry_price:
        continue
    
    # Fetch price from DexScreener
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{contract}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            pairs = result.get('pairs', [])
            
            if pairs:
                # Get first pair's price
                current_price = float(pairs[0].get('priceUsd', 0))
                current_prices[token] = current_price
                
                # Calculate P&L
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                
                # Check thresholds (TP: +100%, SL: -30%)
                if pnl_percent >= 100:
                    alerts.append(f"🎯 {token} hit 2x! Entry: ${entry_price:.6f}, Now: ${current_price:.6f} (+{pnl_percent:.1f}%)")
                elif pnl_percent <= -30:
                    alerts.append(f"⚠️ {token} hit stop loss! Entry: ${entry_price:.6f}, Now: ${current_price:.6f} ({pnl_percent:.1f}%)")
                
    except Exception as e:
        # Silent fail for individual tokens
        pass

# Update lastPrices and lastChecked
data['lastPrices'] = current_prices
data['lastChecked'] = datetime.utcnow().isoformat() + 'Z'

# Write updated data
with open(TEMP_FILE, 'w') as f:
    json.dump(data, f, indent=2)

# Output alerts or NO_REPLY
if alerts:
    for alert in alerts:
        print(alert)
else:
    print("NO_REPLY")
PYEOF

PYEXIT=$?

# If Python script succeeded, update positions file
if [ $PYEXIT -eq 0 ] && [ -f "$TEMP_FILE" ]; then
    mv "$TEMP_FILE" "$POSITIONS_FILE"
fi

# Clean up
rm -f "$TEMP_FILE"

exit 0
