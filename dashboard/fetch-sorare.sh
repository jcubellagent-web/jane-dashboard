#!/bin/bash
# Fetch Sorare NBA data and update dashboard stats

TOKEN=$(cat ~/.openclaw/workspace/.secrets/sorare_token.txt)
OUTPUT=~/.openclaw/workspace/dashboard/sorare-stats.json

# Get user info
USER_DATA=$(curl -s 'https://api.sorare.com/graphql' \
  -H "Authorization: Bearer $TOKEN" \
  -H "JWT-AUD: jane-dashboard" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ currentUser { slug nickname sorareAddress nbaUserProfile { clubName } } user(slug: \"jcubnft\") { cards(first: 1, sport: NBA) { totalCount } } }"
  }')

TOTAL_CARDS=$(echo "$USER_DATA" | jq '.data.user.cards.totalCount')

# Paginate through ALL cards to get accurate rarity breakdown
COMMON=0
LIMITED=0
RARE=0
SUPER_RARE=0
UNIQUE=0
CURSOR=""
TOP_CARDS="[]"

for page in 1 2 3 4 5; do
  if [ -z "$CURSOR" ] || [ "$CURSOR" = "null" ]; then
    QUERY='{ user(slug: "jcubnft") { cards(first: 50, sport: NBA) { nodes { slug rarityTyped serialNumber seasonYear ... on NBACard { basketballPlayer { displayName } anyTeam { name } pictureUrl } } pageInfo { endCursor hasNextPage } } } }'
  else
    QUERY="{ user(slug: \"jcubnft\") { cards(first: 50, sport: NBA, after: \"$CURSOR\") { nodes { slug rarityTyped serialNumber seasonYear ... on NBACard { basketballPlayer { displayName } anyTeam { name } pictureUrl } } pageInfo { endCursor hasNextPage } } } }"
  fi
  
  RESULT=$(curl -s 'https://api.sorare.com/graphql' \
    -H "Authorization: Bearer $TOKEN" \
    -H "JWT-AUD: jane-dashboard" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$QUERY\"}" 2>/dev/null)
  
  # Count rarities
  COMMON=$((COMMON + $(echo "$RESULT" | jq '[.data.user.cards.nodes[] | select(.rarityTyped == "common")] | length')))
  LIMITED=$((LIMITED + $(echo "$RESULT" | jq '[.data.user.cards.nodes[] | select(.rarityTyped == "limited")] | length')))
  RARE=$((RARE + $(echo "$RESULT" | jq '[.data.user.cards.nodes[] | select(.rarityTyped == "rare")] | length')))
  SUPER_RARE=$((SUPER_RARE + $(echo "$RESULT" | jq '[.data.user.cards.nodes[] | select(.rarityTyped == "super_rare")] | length')))
  UNIQUE=$((UNIQUE + $(echo "$RESULT" | jq '[.data.user.cards.nodes[] | select(.rarityTyped == "unique")] | length')))
  
  # Save top cards from first page
  if [ $page -eq 1 ]; then
    TOP_CARDS=$(echo "$RESULT" | jq '[.data.user.cards.nodes[:10][] | {slug, rarity: .rarityTyped, serial: .serialNumber, season: .seasonYear, player: .basketballPlayer.displayName, team: .anyTeam.name, pictureUrl}]')
  fi
  
  HAS_NEXT=$(echo "$RESULT" | jq -r '.data.user.cards.pageInfo.hasNextPage')
  if [ "$HAS_NEXT" != "true" ]; then
    break
  fi
  CURSOR=$(echo "$RESULT" | jq -r '.data.user.cards.pageInfo.endCursor')
done

# Get upcoming fixtures
FIXTURES=$(curl -s 'https://api.sorare.com/graphql' \
  -H "Authorization: Bearer $TOKEN" \
  -H "JWT-AUD: jane-dashboard" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ so5 { allSo5Fixtures(first: 3, sport: NBA, eventType: CLASSIC, future: true) { nodes { slug gameWeek startDate endDate } } } }"
  }')

# Get current fixture lineups
CURRENT_SLUG=$(echo "$FIXTURES" | jq -r '.data.so5.allSo5Fixtures.nodes[0].slug')
CURRENT_DATA=$(curl -s 'https://api.sorare.com/graphql' \
  -H "Authorization: Bearer $TOKEN" \
  -H "JWT-AUD: jane-dashboard" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"{ so5 { so5Fixture(slug: \\\"$CURRENT_SLUG\\\") { slug gameWeek startDate endDate so5Leaderboards { slug displayName mySo5Lineups { id so5Rankings { ranking score } so5Appearances { score anyCard { slug rarityTyped ... on NBACard { basketballPlayer { displayName } anyTeam { name } } } } } } } } }\"
  }")

# Get upcoming (next) fixture lineups
UPCOMING_SLUG=$(echo "$FIXTURES" | jq -r '.data.so5.allSo5Fixtures.nodes[1].slug // empty')
UPCOMING_DATA='{"data":{"so5":{"so5Fixture":{"slug":"none","gameWeek":0,"so5Leaderboards":[]}}}}'
if [ -n "$UPCOMING_SLUG" ]; then
  UPCOMING_DATA=$(curl -s 'https://api.sorare.com/graphql' \
    -H "Authorization: Bearer $TOKEN" \
    -H "JWT-AUD: jane-dashboard" \
    -H "Content-Type: application/json" \
    -d "{
      \"query\": \"{ so5 { so5Fixture(slug: \\\"$UPCOMING_SLUG\\\") { slug gameWeek startDate endDate so5Leaderboards { slug displayName mySo5Lineups { id so5Rankings { ranking score } so5Appearances { score anyCard { slug rarityTyped ... on NBACard { basketballPlayer { displayName } anyTeam { name } } } } } } } } }\"
    }")
fi

# Get past fixtures and find one with completed results
PAST_FIXTURES=$(curl -s 'https://api.sorare.com/graphql' \
  -H "Authorization: Bearer $TOKEN" \
  -H "JWT-AUD: jane-dashboard" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ so5 { allSo5Fixtures(last: 5, sport: NBA, eventType: CLASSIC, future: false) { nodes { slug gameWeek startDate endDate } } } }"
  }')

COMPLETED_DATA=""
for SLUG in $(echo "$PAST_FIXTURES" | jq -r '.data.so5.allSo5Fixtures.nodes | reverse | .[].slug'); do
  RESULT=$(curl -s 'https://api.sorare.com/graphql' \
    -H "Authorization: Bearer $TOKEN" \
    -H "JWT-AUD: jane-dashboard" \
    -H "Content-Type: application/json" \
    -d "{
      \"query\": \"{ so5 { so5Fixture(slug: \\\"$SLUG\\\") { slug gameWeek startDate endDate so5Leaderboards { slug displayName mySo5Lineups { id so5Rankings { ranking score } so5Appearances { score anyCard { slug rarityTyped ... on NBACard { basketballPlayer { displayName } anyTeam { name } } } } } } } } }\"
    }")
  
  HAS_SCORES=$(echo "$RESULT" | jq '[.data.so5.so5Fixture.so5Leaderboards[].mySo5Lineups[].so5Rankings[0].score // 0] | add')
  if [ "$HAS_SCORES" != "null" ] && [ "$(echo "$HAS_SCORES > 0" | bc)" -eq 1 ]; then
    COMPLETED_DATA="$RESULT"
    break
  fi
done

if [ -z "$COMPLETED_DATA" ]; then
  COMPLETED_DATA='{"data":{"so5":{"so5Fixture":{"slug":"none","gameWeek":0,"so5Leaderboards":[]}}}}'
fi

# Build final JSON
jq -n \
  --argjson total "$TOTAL_CARDS" \
  --argjson common "$COMMON" \
  --argjson limited "$LIMITED" \
  --argjson rare "$RARE" \
  --argjson super_rare "$SUPER_RARE" \
  --argjson unique "$UNIQUE" \
  --argjson top_cards "$TOP_CARDS" \
  --argjson user "$USER_DATA" \
  --argjson fixtures "$FIXTURES" \
  --argjson current "$CURRENT_DATA" \
  --argjson upcoming "$UPCOMING_DATA" \
  --argjson completed "$COMPLETED_DATA" \
'{
  lastUpdated: (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
  user: {
    slug: $user.data.currentUser.slug,
    nickname: $user.data.currentUser.nickname,
    clubName: $user.data.currentUser.nbaUserProfile.clubName,
    walletAddress: $user.data.currentUser.sorareAddress
  },
  cards: {
    total: $total,
    breakdown: [
      {rarity: "common", count: $common},
      {rarity: "limited", count: $limited},
      {rarity: "rare", count: $rare},
      {rarity: "super_rare", count: $super_rare},
      {rarity: "unique", count: $unique}
    ],
    items: $top_cards
  },
  upcomingFixtures: [$fixtures.data.so5.allSo5Fixtures.nodes[] | {slug, gameWeek, startDate, endDate}],
  currentFixture: {
    slug: $current.data.so5.so5Fixture.slug,
    gameWeek: $current.data.so5.so5Fixture.gameWeek,
    startDate: $current.data.so5.so5Fixture.startDate,
    endDate: $current.data.so5.so5Fixture.endDate,
    lineups: [($current.data.so5.so5Fixture.so5Leaderboards // [])[] | select(.mySo5Lineups | length > 0) | {
      leaderboard: .displayName,
      entries: [.mySo5Lineups[] | {
        id: .id,
        ranking: .so5Rankings[0].ranking,
        score: .so5Rankings[0].score,
        players: [.so5Appearances[] | {name: .anyCard.basketballPlayer.displayName, team: .anyCard.anyTeam.name, score: .score, rarity: .anyCard.rarityTyped}]
      }]
    }]
  },
  upcomingFixture: {
    slug: $upcoming.data.so5.so5Fixture.slug,
    gameWeek: $upcoming.data.so5.so5Fixture.gameWeek,
    startDate: $upcoming.data.so5.so5Fixture.startDate,
    endDate: $upcoming.data.so5.so5Fixture.endDate,
    lineups: [($upcoming.data.so5.so5Fixture.so5Leaderboards // [])[] | select(.mySo5Lineups | length > 0) | {
      leaderboard: .displayName,
      entries: [.mySo5Lineups[] | {
        id: .id,
        ranking: .so5Rankings[0].ranking,
        score: .so5Rankings[0].score,
        players: [.so5Appearances[] | {name: .anyCard.basketballPlayer.displayName, team: .anyCard.anyTeam.name, score: .score, rarity: .anyCard.rarityTyped}]
      }]
    }]
  },
  completedFixture: {
    slug: $completed.data.so5.so5Fixture.slug,
    gameWeek: $completed.data.so5.so5Fixture.gameWeek,
    startDate: $completed.data.so5.so5Fixture.startDate,
    endDate: $completed.data.so5.so5Fixture.endDate,
    lineups: [($completed.data.so5.so5Fixture.so5Leaderboards // [])[] | select(.mySo5Lineups | length > 0) | {
      leaderboard: .displayName,
      entries: [.mySo5Lineups[] | {
        id: .id,
        ranking: .so5Rankings[0].ranking,
        score: .so5Rankings[0].score,
        players: [.so5Appearances[] | {name: .anyCard.basketballPlayer.displayName, team: .anyCard.anyTeam.name, score: .score, rarity: .anyCard.rarityTyped}]
      }]
    }]
  }
}' > "$OUTPUT"

echo "Updated: $OUTPUT"
echo "Cards: $TOTAL_CARDS (Common: $COMMON, Limited: $LIMITED, Rare: $RARE, SR: $SUPER_RARE)"
cat "$OUTPUT" | jq -c '{cards: .cards.total, common: .cards.breakdown[0].count, limited: .cards.breakdown[1].count, currentGW: .currentFixture.gameWeek, completedGW: .completedFixture.gameWeek}'
