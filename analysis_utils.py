import json

import plotly.graph_objs as go
import plotly.io as pio

import networkx as nx
import matplotlib.pyplot as plt

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