#!/bin/bash
# Fetch Sorare NBA data and update dashboard stats

TOKEN=$(cat ~/.openclaw/workspace/.secrets/sorare_token.txt)
OUTPUT=~/.openclaw/workspace/dashboard/sorare-stats.json

# Fetch all data in one query
DATA=$(curl -s 'https://api.sorare.com/graphql' \
  -H "Authorization: Bearer $TOKEN" \
  -H "JWT-AUD: jane-dashboard" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ currentUser { slug nickname nbaUserProfile { clubName blueprintCardsCount } } user(slug: \"jcubnft\") { blueprintCards(first: 50) { nodes { slug rarityTyped serialNumber seasonYear ... on NBACard { basketballPlayer { displayName } anyTeam { name } pictureUrl } } } } so5 { allSo5Fixtures(first: 3, sport: NBA, eventType: CLASSIC, future: true) { nodes { slug gameWeek startDate endDate } } } }"
  }')

# Format and save
echo "$DATA" | jq '{
  lastUpdated: (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
  user: {
    slug: .data.currentUser.slug,
    nickname: .data.currentUser.nickname,
    clubName: .data.currentUser.nbaUserProfile.clubName,
    blueprintCardsCount: .data.currentUser.nbaUserProfile.blueprintCardsCount
  },
  cards: [.data.user.blueprintCards.nodes[] | {
    slug,
    rarity: .rarityTyped,
    serial: .serialNumber,
    season: .seasonYear,
    player: .basketballPlayer.displayName,
    team: .anyTeam.name,
    pictureUrl
  }],
  upcomingFixtures: [.data.so5.allSo5Fixtures.nodes[] | {
    slug,
    gameWeek,
    startDate,
    endDate
  }]
}' > "$OUTPUT"

echo "Updated: $OUTPUT"
cat "$OUTPUT" | jq -c '{cards: (.cards | length), fixtures: (.upcomingFixtures | length)}'
