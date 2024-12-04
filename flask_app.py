from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from elo import update_elo_ratings

from analysis_utils import *

app = Flask(__name__)

DATA_FOLDER = 'data'
GAMES_FILE = os.path.join(DATA_FOLDER, 'games.json')
PLAYERS_FILE = os.path.join(DATA_FOLDER, 'players.json')
__VERSION = 1.1


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
            new_players.append({'name': player, 'elo': 1000, 'games': 0})
            player_names.add(player)
    
    if new_players:
        players.extend(new_players)
        save_data(players, PLAYERS_FILE)


@app.route('/', methods=['GET', 'POST'])
def index():
    players = load_data(PLAYERS_FILE)
    games = load_data(GAMES_FILE)
    update_elo_ratings()
    if request.method == 'POST':
        
        game = {
            'red_player1': request.form['red_player1'].strip(),
            'red_player2': request.form['red_player2'].strip(),
            'blue_player1': request.form['blue_player1'].strip(),
            'blue_player2': request.form['blue_player2'].strip(),
            'blue_goals': request.form['blue_goals'],
            'red_goals': request.form['red_goals'],
            'date': request.form['date']
        }
        games = load_data(GAMES_FILE)
        games.append(game)
        save_data(games, GAMES_FILE)
        add_new_players(game)
        update_elo_ratings()
        return redirect(url_for('index'))
    
    games = reversed(games)
    return render_template('index.html', players=players, games=games, version=str(__VERSION))


@app.route('/edit_game/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    games = load_data(GAMES_FILE)
    game = games[-(game_id+1)]
    if request.method == 'POST':

        game['red_player1'] = request.form['red_player1'].strip()
        game['red_player2'] = request.form['red_player2'].strip()
        game['blue_player1'] = request.form['blue_player1'].strip()
        game['blue_player2'] = request.form['blue_player2'].strip()
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
    games.pop(-(game_id+1))
    save_data(games, GAMES_FILE)
    update_elo_ratings()
    return redirect(url_for('index'))


@app.route('/social_graph')
def social_graph():
    
    social_graph = make_social_graph(GAMES_FILE)
        
    return render_template('social_graph.html', social_graph=social_graph)


@app.route('/player_stats')
def player_stats():
    
    player_stats = make_player_stats(GAMES_FILE)
        
    return render_template('player_stats.html', player_stats=player_stats)


@app.route('/player_matrix')
def player_matrix():
    
    players, matchups, counts = make_player_matrix(GAMES_FILE)
        
    return render_template('player_matrix.html', players=players, matchups=matchups, player_game_counts=counts)


@app.route('/player/<string:player>')
def player_profile(player):
    
    data = get_player_profile(GAMES_FILE, player)
    print(data)
    
    return jsonify(data)


@app.route('/clean_db')
def clean_db():
    
    players = load_data(PLAYERS_FILE)
    players = [player for player in players if player["games"] >= 1]
    save_data(players, PLAYERS_FILE)
    
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)
