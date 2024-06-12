import json
import os

DATA_FOLDER = 'data'
GAMES_FILE = os.path.join(DATA_FOLDER, 'games.json')
PLAYERS_FILE = os.path.join(DATA_FOLDER, 'players.json')

K_FACTOR = 32

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
    players = load_data(PLAYERS_FILE)
    games = load_data(GAMES_FILE)
    player_dict = {player['name']: player for player in players}

    for player in player_dict.values():
        player['elo'] = 1000  # Reset ELO to base value

    for game in games:
        red_team_elo = (player_dict[game['red_player1']]['elo'] + player_dict[game['red_player2']]['elo']) / 2
        blue_team_elo = (player_dict[game['blue_player1']]['elo'] + player_dict[game['blue_player2']]['elo']) / 2

        if game['result'] == 'red':
            red_result, blue_result = 1, 0
        else:
            red_result, blue_result = 0, 1

        red_elo_change = calculate_elo_change(red_team_elo, blue_team_elo, red_result)
        blue_elo_change = calculate_elo_change(blue_team_elo, red_team_elo, blue_result)

        player_dict[game['red_player1']]['elo'] += round(red_elo_change, 0)
        player_dict[game['red_player2']]['elo'] += round(red_elo_change, 0)
        player_dict[game['blue_player1']]['elo'] += round(blue_elo_change, 0)
        player_dict[game['blue_player2']]['elo'] += round(blue_elo_change, 0)

    save_data(list(player_dict.values()), PLAYERS_FILE)
