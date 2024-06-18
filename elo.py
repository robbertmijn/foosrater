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
    players = load_data(PLAYERS_FILE)
    games = load_data(GAMES_FILE)
    player_dict = {player['name']: player for player in players}

    for player in player_dict.values():
        player['elo'] = 1000  # Reset ELO to base value

    for game in games:
        print(game)
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
        player_dict[game['red_player1']]['elo'] += round(red_elo_change, 0)
        game['red_player1_elo'] = round(red_elo_change, 0)

        player_dict[game['blue_player1']]['elo'] += round(blue_elo_change, 0)
        game['blue_player1_elo'] = round(blue_elo_change, 0) 

        # in case of 2v1 or 2v2
        if game['red_player2'] != "":
            player_dict[game['red_player2']]['elo'] += round(red_elo_change, 0) 
            game['red_player2_elo'] = red_elo_change
        if game['blue_player2'] != "":
            player_dict[game['blue_player2']]['elo'] += round(blue_elo_change, 0)
            game['blue_player2_elo'] = blue_elo_change

    save_data(list(player_dict.values()), PLAYERS_FILE)
    save_data(games, GAMES_FILE)
