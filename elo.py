import json
import os

DATA_FOLDER = 'data'
GAMES_FILE = os.path.join(DATA_FOLDER, 'games.json')
PLAYERS_FILE = os.path.join(DATA_FOLDER, 'players.json')

K_FACTOR = 64

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

def save_data(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def calculate_elo_change(player_elo, opponent_elo, result):
    expected_score = 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))
    return K_FACTOR * (result - expected_score)

def update_elo_ratings():

    # Load names of previous players
    players = load_data(PLAYERS_FILE)
    games = load_data(GAMES_FILE)

    # Create fresh dict with all players reset to base elo
    player_dict = {player['name']: player for player in players}
    for player in player_dict.values():
        player['elo'] = 1000  # Reset ELO to base value
        player['games'] = 0

    # loop over all games and calculate ratings
    for game in games:

        game['players'] = {}
        
        # Calculate mean elo for the teams
        red_team_elo = (player_dict[game['red_player1']]['elo'] + player_dict[game['red_player2']]['elo']) / 2 if game['red_player2'] != "" else player_dict[game['red_player1']]['elo']
        blue_team_elo = (player_dict[game['blue_player1']]['elo'] + player_dict[game['blue_player2']]['elo']) / 2 if game['blue_player2'] != "" else player_dict[game['blue_player1']]['elo']

        # Calculate the result of the game (scored goals/total goals)
        red_result = int(game['red_goals']) / (int(game['blue_goals']) + int(game['red_goals']))
        blue_result = int(game['blue_goals']) / (int(game['blue_goals']) + int(game['red_goals']))

        # Calculate elo change for the teammembers
        red_elo_change = calculate_elo_change(red_team_elo, blue_team_elo, red_result)
        blue_elo_change = calculate_elo_change(blue_team_elo, red_team_elo, blue_result)

        # edit player and game database
        player_dict[game['red_player1']]['elo'] += int(red_elo_change)
        player_dict[game['red_player1']]['games'] += 1
        game['red_player1_elo_change'] = int(red_elo_change)
        game['red_player1_elo'] = player_dict[game['red_player1']]['elo']
        game['players'][game['red_player_1']] = player_dict[game['red_player1']]['elo']

        player_dict[game['blue_player1']]['elo'] += int(blue_elo_change)
        player_dict[game['blue_player1']]['games'] += 1
        game['blue_player1_elo_change'] = player_dict[game['blue_player1']]['elo']
        game['players'][game['blue_player_1']] = player_dict[game['blue_player1']]['elo']

        # in case of 2v1 or 2v2
        if game['red_player2'] != "":
            player_dict[game['red_player2']]['elo'] += int(red_elo_change)
            player_dict[game['red_player2']]['games'] += 1
            game['red_player2_elo_change'] = int(red_elo_change)
            game['red_player2_elo'] = player_dict[game['red_player2']]['elo']
            game['players'][game['red_player_2']] = player_dict[game['red_player2']]['elo']

        if game['blue_player2'] != "":
            player_dict[game['blue_player2']]['elo'] += int(blue_elo_change)
            player_dict[game['blue_player2']]['games'] += 1
            game['blue_player2_elo_change'] = int(blue_elo_change)
            game['blue_player2_elo'] = player_dict[game['blue_player2']]['elo']
            game['players'][game['blue_player_2']] = player_dict[game['blue_player2']]['elo']

    # overwrite previous players dict with newly sorted dict
    players = list(player_dict.values())
    players = sorted(players, key=lambda x: x['elo'], reverse=True)
    for i, player in enumerate(players):
        player["ranking"] = i + 1

    save_data(players, PLAYERS_FILE)
    save_data(games, GAMES_FILE)
