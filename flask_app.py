from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import json
import os
import csv

from foosrater import League, Player

app = Flask(__name__)

DATA_FOLDER = 'data'

@app.route('/', methods=['GET', 'POST'])
def landing():
    return redirect(url_for('index', league_name="hmt_2025"))


@app.route('/<league_name>', methods=['GET', 'POST'])
def index(league_name):


        
    data = os.path.join(DATA_FOLDER, league_name + ".csv")
    
    if league_name == "hmt_2024":
        from elo_2024 import HMT2024League
        league = HMT2024League()
    else:
        league = League()
    
    league.load_foosdat(data)
    
    if request.method == 'POST':
        league.add_game(
            [request.form['red_player1'].strip(), request.form['red_player2'].strip(), request.form['blue_player1'].strip(), request.form['blue_player2'].strip()], 
            request.form['red_score'], 
            request.form['blue_score'], 
            request.form['date_time'],
            len(league.games)
        )
        
        league.save_foosdat(data)
        
        return redirect(url_for('index', league_name=league_name))
    
    # extract games and player dicts to send to HTML
    games = reversed([game.__dict__ for game in league.games])
    players_ranked = [player.__dict__ for player in league.players.values() if player.name != "" and player.n_games >= 3]
    players_unranked = [player.__dict__ for player in league.players.values() if player.name != "" and player.n_games <= 2]
                
    return render_template('index.html', players_ranked=players_ranked, players_unranked=players_unranked, games=games, league_name=league_name)


@app.route('/create_league/<league_name>', methods=['GET', 'POST'])
def create_league(league_name):

    # create new league
    league_data = os.path.join(DATA_FOLDER, league_name + ".csv")
    if not os.path.exists(league_data):
        # Create the file with headers
        with open(league_data, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["R1", "R2", "B1", "B2", "red_score", "blue_score", "date_time"])
    
    return redirect(url_for('index', league_name=league_name))
            
                     
@app.route('/<league_name>/edit_game/<int:game_id>', methods=['GET', 'POST'])
def edit_game(league_name, game_id):
    
    league_data = os.path.join(DATA_FOLDER, league_name + ".csv")
    league = League()
    league.load_foosdat(league_data)
    
    game = league.games[game_id]
    
    if request.method == 'POST':

        league.edit_game(
            [request.form['red_player1'].strip(), request.form['red_player2'].strip(), request.form['blue_player1'].strip(), request.form['blue_player2'].strip()], 
            request.form['red_score'], 
            request.form['blue_score'], 
            request.form['date_time'],
            game_id
        )
        
        league.save_foosdat(league_data)

        return redirect(url_for('index', league_name=league_name))
    
    return render_template('edit_game.html', game=game, game_id=game_id, league_name=league_name)


@app.route('/<league_name>/delete_game/<int:game_id>', methods=['POST'])
def delete_game(league_name, game_id):

    league_data = os.path.join(DATA_FOLDER, league_name + ".csv")
    league = League()
    league.load_foosdat(league_data)
    league.games.pop(game_id)
    league.save_foosdat(league_data)
    
    return redirect(url_for('index', league_name=league_name))
    

@app.route('/<league_name>/player/<string:player_name>')
def player_profile(league_name, player_name):
    
    league_data = os.path.join(DATA_FOLDER, league_name + ".csv")
    league = League()
    league.load_foosdat(league_data)
    
    data = league.players[player_name].get_player_profile()
    
    return jsonify(data)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True)
