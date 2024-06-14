from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime
from elo import update_elo_ratings, calculate_elo_change

app = Flask(__name__)

DATA_FOLDER = 'data'
GAMES_FILE = os.path.join(DATA_FOLDER, 'games.json')
PLAYERS_FILE = os.path.join(DATA_FOLDER, 'players.json')

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

def save_data(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def add_new_players(game):
    players = load_data(PLAYERS_FILE)
    player_names = {player['name'] for player in players}
    new_players = []

    for player in [game['red_player1'], game['red_player2'], game['blue_player1'], game['blue_player2']]:
        if player not in player_names and player != "":
            new_players.append({'name': player, 'elo': 1000})
            player_names.add(player)
    
    if new_players:
        players.extend(new_players)
        save_data(players, PLAYERS_FILE)

@app.route('/')
def index():
    players = load_data(PLAYERS_FILE)
    players_sorted = sorted(players, key=lambda x: x['elo'], reverse=True)
    games = load_data(GAMES_FILE)
    # games = reversed(games) #TODO game IDs fixen
    return render_template('index.html', players=players_sorted, games=games)

@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        game_date = request.form['date']
        
        game = {
            'red_player1': request.form['red_player1'],
            'red_player2': request.form['red_player2'],
            'blue_player1': request.form['blue_player1'],
            'blue_player2': request.form['blue_player2'],
            'blue_goals': request.form['blue_goals'],
            'red_goals': request.form['red_goals'],
            'date': game_date
        }
        games = load_data(GAMES_FILE)
        games.append(game)
        save_data(games, GAMES_FILE)
        add_new_players(game)
        update_elo_ratings()
        return redirect(url_for('index'))
    return render_template('add_game.html')

@app.route('/edit_game/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    games = load_data(GAMES_FILE)
    game = games[game_id]
    if request.method == 'POST':
        # game_date = request.form['date']

        game['red_player1'] = request.form['red_player1']
        game['red_player2'] = request.form['red_player2']
        game['blue_player1'] = request.form['blue_player1']
        game['blue_player2'] = request.form['blue_player2']
        game['blue_goals'] = request.form['blue_goals']
        game['red_goals'] = request.form['red_goals']
        game['date'] = request.form['date']

        save_data(games, GAMES_FILE)
        add_new_players(game)
        update_elo_ratings()
        return redirect(url_for('index'))
    return render_template('edit_game.html', game=game, game_id=game_id)

@app.route('/delete_game/<int:game_id>', methods=['POST'])
def delete_game(game_id):
    games = load_data(GAMES_FILE)
    games.pop(game_id)
    save_data(games, GAMES_FILE)
    update_elo_ratings()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
