from flask import Flask, render_template, redirect, url_for, jsonify, request
from forms import GameResultForm  # Import your form
from flask_wtf.csrf import CSRFProtect

import json
import os
# from elo import update_elo_ratings, calculate_elo_change

# from analysis_utils import *

from foosrater import League

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key
csrf = CSRFProtect(app)

DATA_FOLDER = 'data'

@app.route('/<league_name>', methods=['GET', 'POST'])
def index(league_name):

    data = os.path.join(DATA_FOLDER, league_name + ".csv")
    league = League()
    league.load_foosdat(data)
    form = GameResultForm()
    
    if request.method == 'POST':
        red_score = form.red_score.data
        blue_score = form.blue_score.data
        R1_name = form.player_red1.data
        R2_name = form.player_red2.data
        B1_name = form.player_blue1.data
        B2_name = form.player_blue2.data
        date_time = form.date_time.data

        league.add_game([R1_name, R2_name, B1_name, B2_name], red_score, blue_score, date_time)
        
        # league.add_game(
        #     [request.form['red_player1'].strip(), request.form['red_player2'].strip(), request.form['blue_player1'].strip(), request.form['blue_player2'].strip()], 
        #     request.form['red_score'], 
        #     request.form['blue_score'], 
        #     request.form['date'],
        #     len(league.games)
        # )
        
        league.save_foosdat(data)
        
        return redirect(url_for('index', league_name=league_name))
    
    # extract games and player dicts to send to HTML
    games = [game.__dict__ for game in league.games]
    players_ranked = [player.__dict__ for player in league.players.values() if player.name != "" and player.n_games >= 3]
    players_unranked = [player.__dict__ for player in league.players.values() if player.name != "" and player.n_games <= 2]
                
    return render_template('index.html', players_ranked=players_ranked, players_unranked=players_unranked, games=games, league_name=league_name, form=form)


@app.route('/<league_name>/edit_game/<int:game_id>', methods=['GET', 'POST'])
def edit_game(league_name, game_id):
    
    data = os.path.join(DATA_FOLDER, league_name + ".csv")
    league = League()
    league.load_foosdat(data)
    
    game = league.games[game_id]
    
    if request.method == 'POST':

        league.edit_game(
            [request.form['red_player1'].strip(), request.form['red_player2'].strip(), request.form['blue_player1'].strip(), request.form['blue_player2'].strip()], 
            request.form['red_score'], 
            request.form['blue_score'], 
            request.form['date'],
            game_id
        )
        
        league.save_foosdat(data)

        return redirect(url_for('index', league_name=league_name))
    
    return render_template('edit_game.html', game=game, game_id=game_id, league_name=league_name)


@app.route('/<league_name>/delete_game/<int:game_id>', methods=['POST'])
def delete_game(league_name, game_id):

    
    
    return redirect(url_for('index'))


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
