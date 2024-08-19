from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime
from elo import update_elo_ratings, calculate_elo_change

import plotly.graph_objs as go
import plotly.io as pio

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


@app.route('/stats')
def stats():
    games = load_data(GAMES_FILE)
    players_data = {}
    
    # Organize data by player and date
    for game in games:
        
        date = datetime.strptime(game['date'], "%Y-%m-%d")
            
        for player, rating in game['players'].items():
            if player not in players_data:
                players_data[player] = {'dates': [], 'ratings': []}
            players_data[player]['dates'].append(date)
            players_data[player]['ratings'].append(rating)
    
    # Create traces for each player
    traces = []
    for player, pdata in players_data.items():
        trace = go.Scatter(x=pdata['dates'], y=pdata['ratings'], mode='lines+markers', name=player)
        traces.append(trace)
    
    layout = go.Layout(title='Player Ratings Over Time', xaxis={'title': 'Date'}, yaxis={'title': 'Rating'})
    fig = go.Figure(data=traces, layout=layout)
    graph = pio.to_html(fig, full_html=False)
    
    return render_template('stats.html', graph=graph)


if __name__ == '__main__':
    app.run(debug=True)
