from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime
from elo import update_elo_ratings, calculate_elo_change

import plotly.graph_objs as go
import plotly.io as pio

import networkx as nx
import matplotlib.pyplot as plt

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


@app.route('/social')
def social_graph():
    # Load the data from the JSON file
    with open(GAMES_FILE) as f:
        data = json.load(f)

    # Initialize the graph
    G = nx.Graph()

    # Function to add or update edges between players
    def add_game_edge(player1, player2, weight=1):
        if G.has_edge(player1, player2):
            G[player1][player2]['weight'] += weight
        else:
            G.add_edge(player1, player2, weight=weight)

    # Process each game in the dataset
    for game in data:
        red_players = [game['red_player1'], game.get('red_player2', '')]
        blue_players = [game['blue_player1'], game.get('blue_player2', '')]
        
        # Remove empty player entries
        red_players = [p for p in red_players if p]
        blue_players = [p for p in blue_players if p]
        
        # Create edges between all red players and blue players
        for red_player in red_players:
            for blue_player in blue_players:
                add_game_edge(red_player, blue_player)

    # Get the layout positions
    pos = nx.spring_layout(G)

    # Create plotly traces for edges
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)  # to separate segments
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Create plotly traces for nodes
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            )
        )
    )

    # Add hover information for nodes
    node_adjacencies = []
    node_text = []
    for node, adjacencies in G.adjacency():
        node_adjacencies.append(len(adjacencies))
        node_text.append(f'{node} has {len(adjacencies)} connections')

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=0),
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False)
                    ))


    # For Flask app, return the figure as HTML:
    graph = fig.to_html(full_html=False)

    return render_template('social.html', graph=graph)


if __name__ == '__main__':
    app.run(debug=True)
