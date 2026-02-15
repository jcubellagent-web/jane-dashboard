#!/usr/bin/env python3
"""
Sorare NBA Market Value Analyzer
Find undervalued limited cards on the market based on projected performance
"""

import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
import os
import time
import statistics

WORKSPACE = '/Users/jc_agent/.openclaw/workspace/sorare'
PLAYER_IDS_FILE = os.path.join(WORKSPACE, 'nba-player-ids.json')

# Sorare GraphQL endpoint
SORARE_API = "https://api.sorare.com/graphql"
SORARE_TOKEN_FILE = os.path.join(WORKSPACE, '../.secrets/sorare_token.txt')

SCORING = {
    'points': 1.0,
    'assists': 2.0,
    'off_rebounds': 2.0,
    'def_rebounds': 1.2,
    'steals': 3.0,
    'blocks': 3.0,
    'turnovers': -2.0,
    'fg_miss': -0.5,
    'ft_miss': -0.75,
    'double_double': 1.0,
    'triple_double': 1.0
}

NBA_STATS_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Referer': 'https://www.nba.com/',
    'Accept': 'application/json'
}


def load_sorare_token() -> Optional[str]:
    """Load Sorare API token"""
    try:
        with open(SORARE_TOKEN_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        print("⚠️  Sorare token not found. Market prices unavailable.")
        return None


def calculate_sorare_score(stats: Dict) -> float:
    """Convert NBA box score to Sorare fantasy points"""
    pts = stats.get('PTS', 0)
    ast = stats.get('AST', 0)
    stl = stats.get('STL', 0)
    blk = stats.get('BLK', 0)
    tov = stats.get('TOV', 0)
    fgm = stats.get('FGM', 0)
    fga = stats.get('FGA', 0)
    ftm = stats.get('FTM', 0)
    fta = stats.get('FTA', 0)
    oreb = stats.get('OREB', 0)
    dreb = stats.get('DREB', 0)
    reb = stats.get('REB', 0)
    
    if oreb == 0 and dreb == 0 and reb > 0:
        oreb = round(reb * 0.3)
        dreb = reb - oreb
    
    score = (
        pts * SCORING['points'] +
        ast * SCORING['assists'] +
        oreb * SCORING['off_rebounds'] +
        dreb * SCORING['def_rebounds'] +
        stl * SCORING['steals'] +
        blk * SCORING['blocks'] +
        tov * SCORING['turnovers'] +
        (fga - fgm) * SCORING['fg_miss'] +
        (fta - ftm) * SCORING['ft_miss']
    )
    
    stat_categories = [pts, reb, ast, stl, blk]
    double_digit_count = sum(1 for s in stat_categories if s >= 10)
    
    if double_digit_count >= 2:
        score += SCORING['double_double']
    if double_digit_count >= 3:
        score += SCORING['triple_double']
    
    return round(score, 2)


def fetch_game_logs(player_id: str, last_n_games: int = 10) -> List[Dict]:
    """Fetch recent game logs for a player"""
    try:
        url = "https://stats.nba.com/stats/playergamelog"
        params = {
            'PlayerID': player_id,
            'Season': '2025-26',
            'SeasonType': 'Regular Season'
        }
        
        time.sleep(0.6)
        response = requests.get(url, params=params, headers=NBA_STATS_HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        headers = data['resultSets'][0]['headers']
        rows = data['resultSets'][0]['rowSet'][:last_n_games]
        
        return [dict(zip(headers, row)) for row in rows]
    except Exception as e:
        return []


def calculate_avg_score(game_logs: List[Dict]) -> float:
    """Calculate average Sorare score from game logs"""
    if not game_logs:
        return 0
    
    scores = [calculate_sorare_score(game) for game in game_logs]
    return round(statistics.mean(scores), 2)


def fetch_market_listings(sorare_token: str, rarity: str = 'limited', limit: int = 50) -> List[Dict]:
    """
    Fetch current market listings from Sorare
    Note: This is a simplified version - would need proper GraphQL query
    """
    if not sorare_token:
        return []
    
    # GraphQL query to fetch market listings
    # This is a placeholder - actual implementation would need:
    # 1. Proper GraphQL query structure
    # 2. Pagination
    # 3. Filtering by sport (NBA), rarity, etc.
    
    query = """
    query GetMarketListings($sport: Sport!, $rarity: Rarity!) {
      tokenOffers(
        sport: $sport
        rarities: [$rarity]
        sortByEndDate: ASC
      ) {
        nodes {
          card {
            player {
              displayName
              team {
                name
              }
            }
          }
          price
          endDate
        }
      }
    }
    """
    
    # Note: This is a mock implementation
    # Real implementation would require proper Sorare API integration
    print("ℹ️  Market data fetching requires proper Sorare API integration")
    print("   Skipping market price comparison for now")
    
    return []


def load_player_ids() -> Dict[str, str]:
    """Load cached NBA player ID mappings"""
    if os.path.exists(PLAYER_IDS_FILE):
        with open(PLAYER_IDS_FILE) as f:
            return json.load(f)
    return {}


def fetch_all_nba_players() -> Dict[str, Dict]:
    """Fetch all NBA players from stats API"""
    try:
        url = "https://stats.nba.com/stats/commonallplayers"
        params = {
            'IsOnlyCurrentSeason': '1',
            'LeagueID': '00',
            'Season': '2025-26'
        }
        
        response = requests.get(url, params=params, headers=NBA_STATS_HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        headers = data['resultSets'][0]['headers']
        rows = data['resultSets'][0]['rowSet']
        
        name_idx = headers.index('DISPLAY_FIRST_LAST')
        id_idx = headers.index('PERSON_ID')
        
        players = {}
        for row in rows:
            player_name = row[name_idx]
            players[player_name.lower()] = {
                'id': str(row[id_idx]),
                'name': row[name_idx]
            }
        
        return players
    except Exception as e:
        print(f"⚠️  Error fetching NBA players: {e}")
        return {}


def main():
    """Main market value analyzer"""
    print("💰 SORARE NBA MARKET VALUE ANALYZER")
    print("=" * 80)
    print()
    
    # Load our collection to know what we already own
    collection_file = os.path.join(WORKSPACE, 'our-collection.json')
    with open(collection_file) as f:
        collection = json.load(f)
    
    owned_players = set()
    for card in collection['cards']:
        if 'basketballPlayer' in card:
            owned_players.add(card['basketballPlayer']['displayName'])
    
    print(f"📋 You own {len(owned_players)} unique players")
    print()
    
    # Load Sorare token
    sorare_token = load_sorare_token()
    
    # Load NBA player IDs
    player_ids = load_player_ids()
    
    # For demonstration, analyze top NBA players not in our collection
    print("🔍 Analyzing top NBA performers not in your collection...")
    print()
    
    # Fetch NBA players
    nba_players = fetch_all_nba_players()
    
    # Get top performers (would normally fetch from market, but using top NBA players as example)
    # In real implementation, this would come from Sorare market listings
    sample_players = [
        "Nikola Jokić",
        "Luka Dončić", 
        "Giannis Antetokounmpo",
        "Shai Gilgeous-Alexander",
        "Anthony Davis",
        "Kevin Durant",
        "LeBron James",
        "Stephen Curry",
        "Jayson Tatum",
        "Joel Embiid",
        "Damian Lillard",
        "Donovan Mitchell",
        "Anthony Edwards",
        "Tyrese Haliburton",
        "Kawhi Leonard"
    ]
    
    undervalued_targets = []
    
    for player_name in sample_players:
        if player_name in owned_players:
            continue
        
        print(f"Analyzing {player_name}...", end=' ')
        
        # Get NBA ID
        player_lower = player_name.lower()
        nba_id = None
        
        for nba_name, data in nba_players.items():
            if player_lower in nba_name or nba_name in player_lower:
                nba_id = data['id']
                break
        
        if not nba_id:
            print("❌ NBA ID not found")
            continue
        
        # Fetch game logs
        game_logs = fetch_game_logs(nba_id, last_n_games=10)
        if not game_logs:
            print("❌ No game logs")
            continue
        
        # Calculate average score
        avg_score = calculate_avg_score(game_logs)
        scores = [calculate_sorare_score(game) for game in game_logs]
        
        undervalued_targets.append({
            'name': player_name,
            'avg_score': avg_score,
            'floor': min(scores),
            'ceiling': max(scores),
            'consistency': round(statistics.stdev(scores), 2) if len(scores) > 1 else 0,
            'games_analyzed': len(scores),
            'estimated_value': 'TBD'  # Would come from market analysis
        })
        
        print(f"✅ Avg: {avg_score:.1f}, Range: {min(scores):.1f}-{max(scores):.1f}")
    
    # Sort by average score
    undervalued_targets.sort(key=lambda x: x['avg_score'], reverse=True)
    
    print()
    print("=" * 80)
    print("📊 TOP PERFORMERS NOT IN YOUR COLLECTION")
    print("=" * 80)
    print()
    print(f"{'Rank':<6} {'Player':<30} {'Avg Score':<12} {'Floor':<8} {'Ceiling':<10} {'Consistency'}")
    print("-" * 80)
    
    for idx, player in enumerate(undervalued_targets[:15], 1):
        print(f"{idx:<6} {player['name']:<30} {player['avg_score']:<12.1f} "
              f"{player['floor']:<8.1f} {player['ceiling']:<10.1f} {player['consistency']:.2f}")
    
    print()
    print("=" * 80)
    print("💡 BUYING STRATEGY RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    # High-ceiling players (for tournament upside)
    high_ceiling = sorted(undervalued_targets, key=lambda x: x['ceiling'], reverse=True)[:5]
    print("🚀 HIGHEST CEILING (Tournament Upside):")
    for p in high_ceiling:
        print(f"  • {p['name']}: {p['ceiling']:.1f} ceiling, {p['avg_score']:.1f} avg")
    print()
    
    # Consistent performers (for steady points)
    consistent = sorted(undervalued_targets, key=lambda x: x['consistency'])[:5]
    print("🎯 MOST CONSISTENT (Safe Floor):")
    for p in consistent:
        print(f"  • {p['name']}: {p['avg_score']:.1f} avg, ±{p['consistency']:.2f} std dev")
    print()
    
    # Defense-first players (steals + blocks priority)
    print("🛡️  DEFENSIVE SPECIALISTS:")
    print("  (Manual review needed - check game logs for STL + BLK averages)")
    print("  • Look for players averaging 2+ steals + blocks combined")
    print("  • Defense = 3x multiplier in Sorare scoring")
    print()
    
    # Save results
    output = {
        'generated_at': datetime.now().isoformat(),
        'owned_players': list(owned_players),
        'targets': undervalued_targets,
        'recommendations': {
            'high_ceiling': [p['name'] for p in high_ceiling],
            'consistent': [p['name'] for p in consistent]
        }
    }
    
    output_file = os.path.join(WORKSPACE, 'market-analysis.json')
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Full market analysis saved to: market-analysis.json")
    print()
    print("ℹ️  Note: Market price integration requires Sorare API access")
    print("   For now, use these projections to manually evaluate market listings")


if __name__ == '__main__':
    main()
