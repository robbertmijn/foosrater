import json
import os
import matplotlib.pyplot as plt

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

def calculate_error(player_elo, opponent_elo, result):
    expected_score = 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))
    return result - expected_score

def get_league(elo):
    if 0 <= elo < 1000:
        return "🎷"
    elif 1000 <= elo < 1050:
        return "🛒"
    elif 1050 <= elo < 1100:
        return "🏹"
    elif 1100 <= elo < 1150:
        return "🧀"
    elif 1150 <= elo < 1200:
        return "🤖"
    elif 1200 <= elo < 1250:
        return "🗜️"
    elif elo > 1250:
        return "🥼"
    else:
        return "❌"


def elo_change(error, n_games):
    
    if n_games < 5:
        return error *  128
    elif 5 < n_games < 30:
        return error * 64
    else:
        return error * 32
    

def update_elo_ratings():
    error = []

    # Load names of previous players
    players = load_data(PLAYERS_FILE)
    games = load_data(GAMES_FILE)

    # Create fresh dict with all players reset to base elo
    player_dict = {player['name']: player for player in players}
    for player in player_dict.values():
        player['elo'] = 1000  # Reset ELO to base value
        player['games'] = 0

    # loop over all games and calculate ratings
    for i, game in enumerate(games):

        game['players'] = {}
        game['id'] = i
        
        # Calculate mean elo for the teams
        red_team_elo = (player_dict[game['red_player1']]['elo'] + player_dict[game['red_player2']]['elo']) / 2 if game['red_player2'] != "" else player_dict[game['red_player1']]['elo']
        blue_team_elo = (player_dict[game['blue_player1']]['elo'] + player_dict[game['blue_player2']]['elo']) / 2 if game['blue_player2'] != "" else player_dict[game['blue_player1']]['elo']

        red_C =  0
        blue_C = 0
        # red_C = 1 if float(game['red_goals']) > float(game['blue_goals']) else 0
        # blue_C = 1 if float(game['blue_goals']) > float(game['red_goals']) else 0
        
        # Calculate the result of the game (scored goals/total goals)
        red_result = (float(game['red_goals']) + red_C) / (float(game['blue_goals']) + float(game['red_goals']))
        blue_result = (float(game['blue_goals']) + blue_C) / (float(game['blue_goals']) + float(game['red_goals']))

        # Calculate elo change for the teammembers
        error_red = calculate_error(red_team_elo, blue_team_elo, red_result)
        error_blue = calculate_error(blue_team_elo, red_team_elo, blue_result)
        error.append(abs(error_blue))

        # edit player and game database
        player_dict[game['red_player1']]['elo'] += elo_change(error_red, player_dict[game['red_player1']]['games'])
        player_dict[game['red_player1']]['games'] += 1
        game['red_player1_elo_change'] = elo_change(error_red, player_dict[game['red_player1']]['games'])
        game['red_player1_elo'] = player_dict[game['red_player1']]['elo']
        game['red_player1_league'] = get_league(player_dict[game['red_player1']]['elo'])
        game['players'][game['red_player1']] = player_dict[game['red_player1']]['elo']

        player_dict[game['blue_player1']]['elo'] += elo_change(error_blue, player_dict[game['blue_player1']]['games'])
        player_dict[game['blue_player1']]['games'] += 1
        game['blue_player1_elo_change'] = elo_change(error_blue, player_dict[game['blue_player1']]['games'])
        game['blue_player1_elo'] = player_dict[game['blue_player1']]['elo']
        game['blue_player1_league'] = get_league(player_dict[game['blue_player1']]['elo'])
        game['players'][game['blue_player1']] = player_dict[game['blue_player1']]['elo']

        # in case of 2v1 or 2v2
        if game['red_player2'] != "":
            player_dict[game['red_player2']]['elo'] += elo_change(error_red, player_dict[game['red_player2']]['games'])
            player_dict[game['red_player2']]['games'] += 1
            game['red_player2_elo_change'] = elo_change(error_red, player_dict[game['red_player2']]['games'])
            game['red_player2_elo'] = player_dict[game['red_player2']]['elo']
            game['red_player2_league'] = get_league(player_dict[game['red_player2']]['elo'])
            game['players'][game['red_player2']] = player_dict[game['red_player2']]['elo']

        if game['blue_player2'] != "":
            player_dict[game['blue_player2']]['elo'] += elo_change(error_blue, player_dict[game['blue_player2']]['games'])
            player_dict[game['blue_player2']]['games'] += 1
            game['blue_player2_elo_change'] = elo_change(error_blue, player_dict[game['blue_player2']]['games'])
            game['blue_player2_elo'] = player_dict[game['blue_player2']]['elo']
            game['blue_player2_league'] = get_league(player_dict[game['blue_player2']]['elo'])
            game['players'][game['blue_player2']] = player_dict[game['blue_player2']]['elo']

    # overwrite previous players dict with newly sorted dict
    players = list(player_dict.values())
    players = sorted(players, key=lambda x: x['elo'], reverse=True)
    for i, player in enumerate(players):
        player["ranking"] = i + 1
        player["league"] = get_league(player["elo"])

    save_data(players, PLAYERS_FILE)
    save_data(games, GAMES_FILE)
    
    with open("error.txt", 'w') as file:
        for e in error:
            file.write(f"{e}\n")

