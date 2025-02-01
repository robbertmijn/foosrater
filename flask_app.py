from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
# from elo import update_elo_ratings, calculate_elo_change

# from analysis_utils import *

from foosrater import League

app = Flask(__name__)

DATA_FOLDER = 'data'
DATA = os.path.join(DATA_FOLDER, "foosdat_2025.csv")

@app.route('/<league>', methods=['GET', 'POST'])
def index(league):

    data = os.path.join(DATA_FOLDER, league + ".csv")
    league = League()
    league.load_foosdat(data)
    
    if request.method == 'POST':
         
        league.add_game(
            request.form['red_player1'].strip(), 
            request.form['red_player2'].strip(), 
            request.form['blue_player1'].strip(), 
            request.form['blue_player2'].strip(), 
            request.form['red_goals'], 
            request.form['blue_goals'], 
            request.form['date']
        )
        
        return redirect(url_for('index'))
    
    games = [game.__dict__ for game in league.games]
    players = [player.__dict__ for player in league.players.values()]
                
    return render_template('index.html', players=players, games=games)


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
    
    # player_stats = make_player_stats(GAMES_FILE)
        
    return render_template('player_stats.html', player_stats=player_stats)


@app.route('/player_matrix')
def player_matrix():
    
    # players, matchups, counts = make_player_matrix(GAMES_FILE)
        
    return render_template('player_matrix.html', players=players, matchups=matchups, player_game_counts=counts)


@app.route('/player/<string:player>')
def player_profile(player):
    
    # data = get_player_profile(GAMES_FILE, player)
    # print(data)
    
    return jsonify(data)


@app.route('/clean_db')
def clean_db():
    
    # players = load_data(PLAYERS_FILE)
    # players = [player for player in players if player["games"] >= 1]
    # save_data(players, PLAYERS_FILE)
    
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)
