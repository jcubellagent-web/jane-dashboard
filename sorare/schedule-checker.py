#!/usr/bin/env python3
"""
Sorare NBA Schedule Checker
Check which players in your collection have games in the current/upcoming game week
"""

import json
import requests
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
import os

WORKSPACE = '/Users/jc_agent/.openclaw/workspace/sorare'
PLAYER_IDS_FILE = os.path.join(WORKSPACE, 'nba-player-ids.json')

NBA_STATS_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Referer': 'https://www.nba.com/',
    'Accept': 'application/json'
}


def fetch_nba_schedule() -> Dict:
    """Fetch NBA schedule"""
    try:
        url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching schedule: {e}")
        return {}


def get_games_in_window(schedule_data: Dict, start_days: int = 0, end_days: int = 7) -> Dict[str, List[Dict]]:
    """Get games for each team in a time window"""
    games_by_team = defaultdict(list)
    
    if not schedule_data or 'leagueSchedule' not in schedule_data:
        return games_by_team
    
    today = datetime.now()
    start_date = today + timedelta(days=start_days)
    end_date = today + timedelta(days=end_days)
    
    for game_date in schedule_data['leagueSchedule']['gameDates']:
        game_date_str = game_date['gameDate']
        try:
            game_dt = datetime.strptime(game_date_str, '%m/%d/%Y %H:%M:%S')
        except ValueError:
            continue
        
        if start_date <= game_dt <= end_date:
            for game in game_date.get('games', []):
                home_team = game['homeTeam']['teamName']
                away_team = game['awayTeam']['teamName']
                
                game_info = {
                    'date': game_dt.strftime('%Y-%m-%d'),
                    'time': game_dt.strftime('%H:%M'),
                    'opponent': away_team,
                    'home': True,
                    'game_id': game.get('gameId')
                }
                games_by_team[home_team].append(game_info)
                
                game_info_away = {
                    'date': game_dt.strftime('%Y-%m-%d'),
                    'time': game_dt.strftime('%H:%M'),
                    'opponent': home_team,
                    'home': False,
                    'game_id': game.get('gameId')
                }
                games_by_team[away_team].append(game_info_away)
    
    return games_by_team


def check_injury_status(player_name: str) -> str:
    """
    Check injury status for a player
    Note: This is a placeholder - would need injury API integration
    For now, returns 'Unknown' - can be enhanced with ESPN/official injury reports
    """
    # TODO: Integrate with injury API
    # Options: ESPN API, NBA.com injury reports, or scraping
    return 'Unknown'


def main():
    """Main schedule checker"""
    print("📅 SORARE NBA SCHEDULE CHECKER")
    print("=" * 80)
    print()
    
    # Load our collection
    collection_file = os.path.join(WORKSPACE, 'our-collection.json')
    with open(collection_file) as f:
        collection = json.load(f)
    
    # Get unique players
    player_info = {}
    for card in collection['cards']:
        if 'basketballPlayer' not in card:
            continue
        
        player_name = card['basketballPlayer']['displayName']
        if player_name not in player_info:
            team = card.get('anyTeam', {}).get('name', 'Unknown')
            positions = card['basketballPlayer'].get('anyPositions', [])
            rarities = []
            
            player_info[player_name] = {
                'team': team,
                'positions': positions,
                'rarities': rarities
            }
        
        player_info[player_name]['rarities'].append(card['rarityTyped'])
    
    print(f"📋 Checking {len(player_info)} unique players")
    print()
    
    # Fetch schedule
    print("🔍 Fetching NBA schedule...")
    schedule = fetch_nba_schedule()
    
    # Check next 7 days
    upcoming_games = get_games_in_window(schedule, start_days=0, end_days=7)
    print(f"✅ Found games for {len(upcoming_games)} teams")
    print()
    
    # Categorize players
    players_with_games = []
    players_no_games = []
    
    for player_name, info in player_info.items():
        team = info['team']
        
        if team in upcoming_games and len(upcoming_games[team]) > 0:
            # Check injury status (placeholder)
            injury_status = check_injury_status(player_name)
            
            players_with_games.append({
                'name': player_name,
                'team': team,
                'positions': info['positions'],
                'rarities': list(set(info['rarities'])),
                'num_games': len(upcoming_games[team]),
                'games': upcoming_games[team],
                'injury_status': injury_status
            })
        else:
            players_no_games.append({
                'name': player_name,
                'team': team,
                'positions': info['positions'],
                'rarities': list(set(info['rarities']))
            })
    
    # Sort by number of games (descending)
    players_with_games.sort(key=lambda x: x['num_games'], reverse=True)
    
    # Display results
    print("=" * 80)
    print(f"✅ PLAYERS WITH GAMES THIS WEEK ({len(players_with_games)})")
    print("=" * 80)
    print()
    
    # Group by number of games
    games_grouped = defaultdict(list)
    for p in players_with_games:
        games_grouped[p['num_games']].append(p)
    
    for num_games in sorted(games_grouped.keys(), reverse=True):
        players = games_grouped[num_games]
        print(f"🏀 {num_games} Game{'s' if num_games > 1 else ''} ({len(players)} players)")
        print("-" * 80)
        
        for p in players:
            rarities = ', '.join(sorted(set(p['rarities'])))
            positions = '/'.join([pos.replace('basketball_', '') for pos in p['positions'][:2]])
            
            print(f"  {p['name']:<28} {p['team']:<22} {positions:<15} [{rarities}]")
            
            # Show game schedule
            for game in p['games']:
                home_away = 'vs' if game['home'] else '@'
                print(f"    {game['date']} {game['time']} - {home_away} {game['opponent']}")
            
            # Show injury status if not healthy
            if p['injury_status'] != 'Unknown' and p['injury_status'] != 'Healthy':
                print(f"    ⚠️  Injury: {p['injury_status']}")
            
            print()
        
        print()
    
    # Players without games
    if players_no_games:
        print("=" * 80)
        print(f"⏸️  PLAYERS WITHOUT GAMES THIS WEEK ({len(players_no_games)})")
        print("=" * 80)
        print()
        
        # Group by rarity
        by_rarity = defaultdict(list)
        for p in players_no_games:
            best_rarity = 'limited' if 'limited' in p['rarities'] else p['rarities'][0]
            by_rarity[best_rarity].append(p)
        
        for rarity in ['unique', 'super_rare', 'limited', 'rare']:
            if rarity in by_rarity:
                players = by_rarity[rarity]
                print(f"{rarity.upper()}: {len(players)} players")
                for p in players[:10]:  # Show first 10
                    print(f"  • {p['name']} ({p['team']})")
                if len(players) > 10:
                    print(f"  ... and {len(players) - 10} more")
                print()
    
    # Save results
    output = {
        'generated_at': datetime.now().isoformat(),
        'window': {
            'start': datetime.now().strftime('%Y-%m-%d'),
            'end': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        },
        'players_with_games': players_with_games,
        'players_no_games': players_no_games,
        'summary': {
            'total_players': len(player_info),
            'with_games': len(players_with_games),
            'no_games': len(players_no_games)
        }
    }
    
    output_file = os.path.join(WORKSPACE, 'schedule-report.json')
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Full schedule report saved to: schedule-report.json")
    print()
    
    # Quick summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Total players in collection: {len(player_info)}")
    print(f"Players with games this week: {len(players_with_games)}")
    print(f"Players without games: {len(players_no_games)}")
    print(f"Eligible for lineup: {len([p for p in players_with_games if 'limited' in p['rarities']])} limited cards")


if __name__ == '__main__':
    main()
