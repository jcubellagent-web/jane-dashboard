#!/bin/bash
# Fetch social stats and trending coins from CoinGecko (free tier)

CACHE_FILE="/Users/jc_agent/.openclaw/workspace/pre-brief-cache.json"
API_KEY=$(cat /Users/jc_agent/.openclaw/workspace/.secrets/coingecko_api_key.txt)

# Fetch trending coins
TRENDING=$(curl -s "https://api.coingecko.com/api/v3/search/trending" \
  -H "x-cg-demo-api-key: ${API_KEY}")

if [ $? -ne 0 ] || [ -z "$TRENDING" ]; then
  echo "❌ CoinGecko trending fetch failed"
  exit 1
fi

# Fetch top coins with social data
TOP_COINS=$(curl -s "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&sparkline=false&price_change_percentage=24h" \
  -H "x-cg-demo-api-key: ${API_KEY}")

if [ $? -ne 0 ] || [ -z "$TOP_COINS" ]; then
  echo "❌ CoinGecko top coins fetch failed"
  exit 1
fi

# Parse trending coins
TRENDING_PARSED=$(echo "$TRENDING" | jq -c '[.coins[0:7] | .[] | {
  name: .item.name,
  symbol: .item.symbol,
  market_cap_rank: .item.market_cap_rank,
  price_btc: .item.price_btc,
  score: .item.score
}]')

# Parse top coins
TOP_PARSED=$(echo "$TOP_COINS" | jq -c '[.[] | {
  name: .name,
  symbol: .symbol,
  current_price: .current_price,
  market_cap: .market_cap,
  price_change_24h: .price_change_percentage_24h,
  volume_24h: .total_volume
}]')

# Combine data
COMBINED=$(jq -n --argjson trending "$TRENDING_PARSED" --argjson top "$TOP_PARSED" '{
  trending: $trending,
  top_coins: $top
}')

# Update cache file
if [ -f "$CACHE_FILE" ]; then
  jq --argjson data "$COMBINED" '.coinGecko = $data' "$CACHE_FILE" > "${CACHE_FILE}.tmp" && mv "${CACHE_FILE}.tmp" "$CACHE_FILE"
else
  echo "{\"coinGecko\": $COMBINED}" > "$CACHE_FILE"
fi

echo "✅ CoinGecko: Fetched $(echo "$TRENDING_PARSED" | jq 'length') trending + $(echo "$TOP_PARSED" | jq 'length') top coins"
