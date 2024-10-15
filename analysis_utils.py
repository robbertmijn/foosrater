import json

import plotly.graph_objs as go
import plotly.io as pio

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

from datetime import datetime


def make_social_graph(GAMES_FILE):
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
    
    return graph


def make_player_stats(GAMES_FILE):

    with open(GAMES_FILE) as f:
        games = json.load(f)
        
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
    
    return graph

# Function to load JSON and process the data
def make_player_matrix(GAMES_FILE):
    with open(GAMES_FILE, 'r') as f:
        games = json.load(f)

    # Store how many times players have played against each other
    matchups = defaultdict(lambda: defaultdict(int))
    player_game_counts = defaultdict(int)

    # Analyze all the matches in the data
    for game in games:
        players_red = [game['red_player1'], game.get('red_player2', '')]
        players_blue = [game['blue_player1'], game.get('blue_player2', '')]

        players_red = [p for p in players_red if p]  # Filter out empty strings
        players_blue = [p for p in players_blue if p]

        for red_player in players_red:
            player_game_counts[red_player] += 1
            for blue_player in players_blue:
                player_game_counts[blue_player] += 1
                matchups[red_player][blue_player] += 1
                matchups[blue_player][red_player] += 1

    # Create the virtual player and exclude players with less than 3 games
    virtual_player = "Other players"
    filtered_matchups = defaultdict(lambda: defaultdict(int))

    for player1 in matchups:
        for player2 in matchups[player1]:
            if player_game_counts[player1] < 3 or player_game_counts[player2] < 3:
                filtered_matchups[virtual_player][player1] += matchups[player1][player2]
                filtered_matchups[player1][virtual_player] += matchups[player1][player2]
            else:
                filtered_matchups[player1][player2] += matchups[player1][player2]

    # Keep only players with 3 or more games and the virtual player
    final_players = [p for p, count in player_game_counts.items() if count >= 3]
    final_players.append(virtual_player)

    # Sort players by the number of games played
    final_players_sorted = sorted(final_players, key=lambda p: player_game_counts[p] if p != virtual_player else 0, reverse=True)

    # Create the final matchups for sorted players
    final_matchups = {p: filtered_matchups[p] for p in final_players_sorted}

    return final_players_sorted, final_matchups, player_game_counts


def get_player_profile(GAMES_FILE, player):
    
    with open(GAMES_FILE, 'r') as f:
        games = json.load(f)

    # Store how many times players have played against each other
    opponents = defaultdict(lambda: defaultdict(int))
    goals_made = defaultdict(lambda: defaultdict(int))
    goals_let = defaultdict(lambda: defaultdict(int))
    
    teammates = defaultdict(lambda: defaultdict(int))
    player_game_counts = defaultdict(int)

    # Analyze all the matches in the data
    for game in games:
        players_red = [game['red_player1'], game.get('red_player2', '')]
        players_blue = [game['blue_player1'], game.get('blue_player2', '')]

        # red_wins = True if game['red_goals'] > game['blue_goals'] else False
        # blue_wins = True if game['blue_goals'] > game['red_goals'] else False

        # only continue for current players
        if player in players_blue or player in players_red:
            pass
        else:
            continue
        
        # remove empty players (in 1v1 or 1v2)
        players_red = [p for p in players_red if p]
        players_blue = [p for p in players_blue if p]
        
        for p in players_red + players_blue:
            player_game_counts[p] += 1
        
        # count teammates
        if len(players_red) > 1:
            teammates[game['red_player1']][game['red_player2']] += 1
            teammates[game['red_player2']][game['red_player1']] += 1
        if len(players_blue) > 1:
            teammates[game['blue_player1']][game['blue_player2']] += 1
            teammates[game['blue_player2']][game['blue_player1']] += 1
        
        # count opponents
        for red_player in players_red:
            for blue_player in players_blue:
                opponents[red_player][blue_player] += 1
                goals_made[red_player][blue_player] += int(game['red_goals'])
                goals_let[red_player][blue_player] += int(game['blue_goals'])
                
        for blue_player in players_blue:
            for red_player in players_red:
                opponents[blue_player][red_player] += 1
                goals_made[blue_player][red_player] += int(game['blue_goals'])
                goals_let[blue_player][red_player] += int(game['red_goals'])

    player_profile = dict(name=player, 
                          opponents=sorted(opponents[player].items(), key=lambda x: x[1], reverse=True)[:5],
                          teammates=sorted(teammates[player].items(), key=lambda x: x[1], reverse=True)[:5])
    print(goals_let[player])
    print(goals_made[player])
    
    return player_profile