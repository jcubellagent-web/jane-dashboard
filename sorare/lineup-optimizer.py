#!/usr/bin/env python3
"""
Sorare NBA Lineup Optimizer
Finds optimal 5-player lineups from your collection based on projected scores
"""

import json
import requests
import statistics
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import itertools
import time
import os

# Sorare scoring coefficients
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

WORKSPACE = '/Users/jc_agent/.openclaw/workspace/sorare'
CACHE_FILE = os.path.join(WORKSPACE, 'optimizer-cache.json')
PLAYER_IDS_FILE = os.path.join(WORKSPACE, 'nba-player-ids.json')


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
    
    # If separate rebounds not available, estimate 30% offensive
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
    
    # Double-double / triple-double bonuses
    stat_categories = [pts, reb, ast, stl, blk]
    double_digit_count = sum(1 for s in stat_categories if s >= 10)
    
    if double_digit_count >= 2:
        score += SCORING['double_double']
    if double_digit_count >= 3:
        score += SCORING['triple_double']
    
    return round(score, 2)


def load_player_ids() -> Dict[str, str]:
    """Load cached NBA player ID mappings"""
    if os.path.exists(PLAYER_IDS_FILE):
        with open(PLAYER_IDS_FILE) as f:
            return json.load(f)
    return {}


def save_player_ids(player_ids: Dict[str, str]):
    """Save NBA player ID mappings"""
    with open(PLAYER_IDS_FILE, 'w') as f:
        json.dump(player_ids, f, indent=2)


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
        team_idx = headers.index('TEAM_NAME')
        
        players = {}
        for row in rows:
            player_name = row[name_idx]
            players[player_name.lower()] = {
                'id': str(row[id_idx]),
                'name': row[name_idx],
                'team': row[team_idx]
            }
        
        return players
    except Exception as e:
        print(f"⚠️  Error fetching NBA players: {e}")
        return {}


def get_player_nba_id(player_name: str, nba_players: Dict) -> Optional[str]:
    """Find NBA player ID by name (fuzzy matching)"""
    name_lower = player_name.lower()
    
    # Direct match
    if name_lower in nba_players:
        return nba_players[name_lower]['id']
    
    # Try partial match
    for nba_name, player_data in nba_players.items():
        if name_lower in nba_name or nba_name in name_lower:
            return player_data['id']
    
    return None


def fetch_game_logs(player_id: str, last_n_games: int = 10) -> List[Dict]:
    """Fetch recent game logs for a player"""
    try:
        url = "https://stats.nba.com/stats/playergamelog"
        params = {
            'PlayerID': player_id,
            'Season': '2025-26',
            'SeasonType': 'Regular Season'
        }
        
        time.sleep(0.6)  # Rate limiting
        response = requests.get(url, params=params, headers=NBA_STATS_HEADERS, timeout=15)
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
        print(f"⚠️  Error fetching game logs for player {player_id}: {e}")
        return []


def fetch_team_defense_ratings() -> Dict[str, float]:
    """Fetch defensive ratings for all teams (points allowed per 100 possessions)"""
    try:
        url = "https://stats.nba.com/stats/leaguedashteamstats"
        params = {
            'Season': '2025-26',
            'SeasonType': 'Regular Season',
            'MeasureType': 'Advanced'
        }
        
        response = requests.get(url, params=params, headers=NBA_STATS_HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        headers = data['resultSets'][0]['headers']
        rows = data['resultSets'][0]['rowSet']
        
        team_idx = headers.index('TEAM_NAME')
        def_rtg_idx = headers.index('DEF_RATING')
        
        ratings = {}
        for row in rows:
            team_name = row[team_idx]
            def_rating = row[def_rtg_idx]
            ratings[team_name] = def_rating
        
        return ratings
    except Exception as e:
        print(f"⚠️  Error fetching team defense ratings: {e}")
        return {}


def calculate_projection(game_logs: List[Dict], opponent_def_rating: Optional[float] = None) -> Dict:
    """Calculate projected Sorare score from game logs"""
    if not game_logs:
        return {
            'projected_score': 0,
            'floor': 0,
            'ceiling': 0,
            'std_dev': 0,
            'games': 0,
            'recent_trend': 'unknown'
        }
    
    sorare_scores = [calculate_sorare_score(game) for game in game_logs]
    avg_score = statistics.mean(sorare_scores)
    
    # Weight recent games more heavily (exponential decay)
    weighted_scores = []
    for i, score in enumerate(sorare_scores):
        weight = 0.9 ** i  # Recent games weighted higher
        weighted_scores.extend([score] * max(1, int(weight * 10)))
    weighted_avg = statistics.mean(weighted_scores)
    
    # Adjust for opponent defense (league average ~110)
    if opponent_def_rating:
        league_avg = 110
        difficulty_multiplier = league_avg / opponent_def_rating
        weighted_avg *= difficulty_multiplier
    
    # Calculate recent trend (last 3 vs previous 7)
    recent_avg = statistics.mean(sorare_scores[:3]) if len(sorare_scores) >= 3 else avg_score
    older_avg = statistics.mean(sorare_scores[3:]) if len(sorare_scores) > 3 else avg_score
    trend = 'up' if recent_avg > older_avg * 1.1 else 'down' if recent_avg < older_avg * 0.9 else 'flat'
    
    return {
        'projected_score': round(weighted_avg, 2),
        'floor': round(min(sorare_scores), 2),
        'ceiling': round(max(sorare_scores), 2),
        'std_dev': round(statistics.stdev(sorare_scores), 2) if len(sorare_scores) > 1 else 0,
        'games': len(sorare_scores),
        'recent_trend': trend,
        'last_5_scores': sorare_scores[:5]
    }


def fetch_nba_schedule() -> Dict:
    """Fetch NBA schedule for upcoming games"""
    try:
        url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️  Error fetching NBA schedule: {e}")
        return {}


def get_upcoming_games(schedule_data: Dict, days_ahead: int = 7) -> Dict[str, List[Dict]]:
    """Get games for each team in the next N days"""
    games_by_team = defaultdict(list)
    
    if not schedule_data or 'leagueSchedule' not in schedule_data:
        return games_by_team
    
    today = datetime.now()
    cutoff = today + timedelta(days=days_ahead)
    
    for game_date in schedule_data['leagueSchedule']['gameDates']:
        game_date_str = game_date['gameDate']
        game_dt = datetime.strptime(game_date_str, '%m/%d/%Y %H:%M:%S')
        
        if today <= game_dt <= cutoff:
            for game in game_date.get('games', []):
                home_team = game['homeTeam']['teamName']
                away_team = game['awayTeam']['teamName']
                
                game_info = {
                    'date': game_date_str,
                    'opponent': away_team,
                    'home': True,
                    'game_id': game.get('gameId')
                }
                games_by_team[home_team].append(game_info)
                
                game_info_away = {
                    'date': game_date_str,
                    'opponent': home_team,
                    'home': False,
                    'game_id': game.get('gameId')
                }
                games_by_team[away_team].append(game_info_away)
    
    return games_by_team


def optimize_lineup(players: List[Dict], rarity_filter: Optional[str] = None, lineup_size: int = 5) -> List[Dict]:
    """Find optimal lineup from available players"""
    # Filter by rarity if specified
    if rarity_filter:
        players = [p for p in players if p['rarity'] == rarity_filter]
    
    # Sort by projected score
    players_sorted = sorted(players, key=lambda x: x['projection']['projected_score'], reverse=True)
    
    # For now, simple greedy selection (top N players)
    # Future enhancement: combinatorial optimization with position constraints
    optimal_lineup = players_sorted[:lineup_size]
    
    return optimal_lineup


def main():
    """Main lineup optimizer"""
    print("🏀 SORARE NBA LINEUP OPTIMIZER")
    print("=" * 80)
    print()
    
    # Load our collection
    collection_file = os.path.join(WORKSPACE, 'our-collection.json')
    with open(collection_file) as f:
        collection = json.load(f)
    
    # Get unique players with their best card rarity
    player_cards = defaultdict(list)
    for card in collection['cards']:
        if 'basketballPlayer' not in card:
            continue
        
        player_name = card['basketballPlayer']['displayName']
        rarity = card['rarityTyped']
        team = card.get('anyTeam', {}).get('name', 'Unknown')
        positions = card['basketballPlayer'].get('anyPositions', [])
        
        player_cards[player_name].append({
            'rarity': rarity,
            'team': team,
            'positions': positions,
            'serial': card.get('serialNumber')
        })
    
    print(f"📋 Found {len(player_cards)} unique players in collection")
    print()
    
    # Fetch NBA data
    print("🔍 Fetching NBA player database...")
    nba_players = fetch_all_nba_players()
    print(f"✅ Loaded {len(nba_players)} NBA players")
    print()
    
    print("📊 Fetching team defensive ratings...")
    defense_ratings = fetch_team_defense_ratings()
    print(f"✅ Loaded {len(defense_ratings)} team ratings")
    print()
    
    print("📅 Fetching NBA schedule...")
    schedule = fetch_nba_schedule()
    upcoming_games = get_upcoming_games(schedule, days_ahead=7)
    print(f"✅ Loaded games for next 7 days")
    print()
    
    # Load cached player IDs
    player_ids = load_player_ids()
    
    # Calculate projections for each player
    print("🎯 Calculating player projections...")
    print()
    
    player_projections = []
    
    for idx, (player_name, cards) in enumerate(player_cards.items(), 1):
        print(f"[{idx}/{len(player_cards)}] {player_name}...", end=' ')
        
        # Get NBA player ID
        nba_id = player_ids.get(player_name)
        if not nba_id:
            nba_id = get_player_nba_id(player_name, nba_players)
            if nba_id:
                player_ids[player_name] = nba_id
        
        if not nba_id:
            print("❌ Not found in NBA database")
            continue
        
        # Fetch game logs
        game_logs = fetch_game_logs(nba_id, last_n_games=10)
        if not game_logs:
            print("❌ No game logs")
            continue
        
        # Get team and check for upcoming games
        team = cards[0]['team']
        has_games = team in upcoming_games and len(upcoming_games[team]) > 0
        
        if not has_games:
            print("⏸️  No games this week")
            continue
        
        # Calculate projection
        opponent = upcoming_games[team][0]['opponent'] if has_games else None
        opponent_def_rating = defense_ratings.get(opponent)
        projection = calculate_projection(game_logs, opponent_def_rating)
        
        # Get best rarity card
        rarities = [c['rarity'] for c in cards]
        best_rarity = 'limited' if 'limited' in rarities else rarities[0]
        
        player_projections.append({
            'name': player_name,
            'team': team,
            'positions': cards[0]['positions'],
            'rarity': best_rarity,
            'cards_owned': len(cards),
            'projection': projection,
            'upcoming_games': upcoming_games[team][:3],  # Next 3 games
            'opponent': opponent,
            'opponent_def_rating': opponent_def_rating
        })
        
        print(f"✅ Projected: {projection['projected_score']:.1f} (trend: {projection['recent_trend']})")
    
    # Save updated player IDs
    save_player_ids(player_ids)
    
    print()
    print("=" * 80)
    print()
    
    if not player_projections:
        print("❌ No players with upcoming games found")
        return
    
    # Optimize lineups for each rarity
    rarities = ['limited', 'rare', 'super_rare', 'unique']
    
    for rarity in rarities:
        eligible_players = [p for p in player_projections if p['rarity'] == rarity]
        
        if len(eligible_players) < 5:
            continue
        
        print(f"🏆 OPTIMAL {rarity.upper()} LINEUP")
        print("-" * 80)
        
        optimal = optimize_lineup(eligible_players, rarity, lineup_size=5)
        total_projected = sum(p['projection']['projected_score'] for p in optimal)
        
        print(f"{'Player':<25} {'Team':<20} {'vs':<20} {'Proj':<8} {'Floor':<8} {'Ceiling'}")
        print("-" * 80)
        
        for p in optimal:
            opponent = p['opponent'] or 'TBD'
            proj = p['projection']
            print(f"{p['name']:<25} {p['team']:<20} {opponent:<20} "
                  f"{proj['projected_score']:<8.1f} {proj['floor']:<8.1f} {proj['ceiling']:.1f}")
        
        print("-" * 80)
        print(f"{'TOTAL PROJECTED SCORE:':<65} {total_projected:.1f}")
        print()
    
    # Save full results
    output = {
        'generated_at': datetime.now().isoformat(),
        'players_analyzed': len(player_projections),
        'projections': player_projections
    }
    
    output_file = os.path.join(WORKSPACE, 'lineup-recommendations.json')
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Full recommendations saved to: lineup-recommendations.json")


if __name__ == '__main__':
    main()
