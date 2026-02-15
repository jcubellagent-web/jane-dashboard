#!/usr/bin/env python3
"""
Sorare NBA Player Projections
Maps real NBA stats to Sorare fantasy points for lineup optimization
"""

import json
import requests
import statistics
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import time

# Sorare scoring coefficients (estimated)
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
    'triple_double': 1.0  # additional bonus on top of double-double
}

NBA_STATS_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Referer': 'https://www.nba.com/',
    'Accept': 'application/json'
}

def calculate_sorare_score(stats: Dict) -> float:
    """Convert NBA box score to Sorare fantasy points"""
    pts = stats.get('PTS', 0)
    reb = stats.get('REB', 0)
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
    
    # Calculate base score
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
    
    # Check for double-double (10+ in any two categories)
    stat_categories = [pts, reb, ast, stl, blk]
    double_digit_count = sum(1 for s in stat_categories if s >= 10)
    
    if double_digit_count >= 2:
        score += SCORING['double_double']
    if double_digit_count >= 3:
        score += SCORING['triple_double']
    
    return round(score, 2)

def fetch_player_info(player_name: str) -> Dict:
    """Get player ID from NBA Stats API"""
    try:
        url = "https://stats.nba.com/stats/commonallplayers"
        params = {
            'IsOnlyCurrentSeason': '1',
            'LeagueID': '00',
            'Season': '2025-26'
        }
        
        response = requests.get(url, params=params, headers=NBA_STATS_HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Search for player by name
        headers = data['resultSets'][0]['headers']
        rows = data['resultSets'][0]['rowSet']
        
        name_idx = headers.index('DISPLAY_FIRST_LAST')
        id_idx = headers.index('PERSON_ID')
        
        for row in rows:
            if player_name.lower() in row[name_idx].lower():
                return {
                    'id': row[id_idx],
                    'name': row[name_idx]
                }
        
        return None
    except Exception as e:
        print(f"Error fetching player info for {player_name}: {e}")
        return None

def fetch_game_logs(player_id: int, last_n_games: int = 10) -> List[Dict]:
    """Fetch recent game logs for a player"""
    try:
        url = "https://stats.nba.com/stats/playergamelog"
        params = {
            'PlayerID': player_id,
            'Season': '2025-26',
            'SeasonType': 'Regular Season'
        }
        
        time.sleep(0.6)  # Rate limiting
        response = requests.get(url, params=params, headers=NBA_STATS_HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        headers = data['resultSets'][0]['headers']
        rows = data['resultSets'][0]['rowSet'][:last_n_games]
        
        game_logs = []
        for row in rows:
            game = dict(zip(headers, row))
            game_logs.append(game)
        
        return game_logs
    except Exception as e:
        print(f"Error fetching game logs for player {player_id}: {e}")
        return []

def calculate_projections(game_logs: List[Dict]) -> Dict:
    """Calculate fantasy projections from game logs"""
    if not game_logs:
        return {
            'avg_score': 0,
            'floor': 0,
            'ceiling': 0,
            'std_dev': 0,
            'games_played': 0
        }
    
    sorare_scores = [calculate_sorare_score(game) for game in game_logs]
    
    return {
        'avg_score': round(statistics.mean(sorare_scores), 2),
        'floor': round(min(sorare_scores), 2),
        'ceiling': round(max(sorare_scores), 2),
        'std_dev': round(statistics.stdev(sorare_scores), 2) if len(sorare_scores) > 1 else 0,
        'games_played': len(sorare_scores),
        'recent_scores': sorare_scores[:5]
    }

def main():
    """Main projection pipeline"""
    print("🏀 Sorare NBA Player Projections\n")
    
    # Load our collection
    with open('/Users/jc_agent/.openclaw/workspace/sorare/our-collection.json') as f:
        collection = json.load(f)
    
    nba_cards = [c for c in collection['cards'] if c.get('basketballPlayer')]
    print(f"Found {len(nba_cards)} NBA cards in collection\n")
    
    # Get unique players
    unique_players = {}
    for card in nba_cards:
        player_name = card['basketballPlayer']['displayName']
        if player_name not in unique_players:
            unique_players[player_name] = {
                'name': player_name,
                'positions': card['basketballPlayer'].get('anyPositions', []),
                'team': card.get('anyTeam', {}).get('name', 'Unknown'),
                'cards': []
            }
        unique_players[player_name]['cards'].append({
            'rarity': card['rarityTyped'],
            'serial': card.get('serialNumber')
        })
    
    print(f"Analyzing {len(unique_players)} unique players...\n")
    
    # Fetch projections for each player
    projections = []
    for idx, (player_name, player_data) in enumerate(unique_players.items(), 1):
        print(f"[{idx}/{len(unique_players)}] Fetching {player_name}...", end=' ')
        
        player_info = fetch_player_info(player_name)
        if not player_info:
            print("❌ Not found")
            continue
        
        game_logs = fetch_game_logs(player_info['id'])
        if not game_logs:
            print("❌ No game logs")
            continue
        
        proj = calculate_projections(game_logs)
        
        projections.append({
            'name': player_name,
            'positions': player_data['positions'],
            'team': player_data['team'],
            'cards_owned': len(player_data['cards']),
            'rarities': [c['rarity'] for c in player_data['cards']],
            **proj
        })
        
        print(f"✅ Avg: {proj['avg_score']:.1f}, Floor: {proj['floor']:.1f}, Ceiling: {proj['ceiling']:.1f}")
    
    # Sort by projected score
    projections.sort(key=lambda x: x['avg_score'], reverse=True)
    
    # Save results
    output = {
        'generated_at': datetime.now().isoformat(),
        'total_players': len(projections),
        'projections': projections
    }
    
    with open('/Users/jc_agent/.openclaw/workspace/sorare/player-projections.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    # Print top performers
    print(f"\n{'='*80}")
    print("📊 TOP 10 PROJECTED PLAYERS")
    print(f"{'='*80}")
    print(f"{'Rank':<5} {'Player':<25} {'Pos':<8} {'Team':<20} {'Avg':<6} {'Floor':<6} {'Ceiling':<8} {'Cards'}")
    print(f"{'-'*80}")
    
    for idx, p in enumerate(projections[:10], 1):
        positions = '/'.join(p['positions'][:2]) if p['positions'] else 'N/A'
        rarities = ', '.join(p['rarities'])
        print(f"{idx:<5} {p['name']:<25} {positions:<8} {p['team']:<20} "
              f"{p['avg_score']:<6.1f} {p['floor']:<6.1f} {p['ceiling']:<8.1f} {p['cards_owned']} ({rarities})")
    
    print(f"\n✅ Full projections saved to: player-projections.json")

if __name__ == '__main__':
    main()
