from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import csv
from foosrater import League, Player

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

DATA_FOLDER = 'data'

def get_league_data(league_name):
    data_path = os.path.join(DATA_FOLDER, f"{league_name}.csv")
    league = League()
    league.load_foosdat(data_path)
    return league

# ------------------- API ROUTES ------------------- #

@app.route('/api/games/<league_name>', methods=['GET'])
def get_games(league_name):
    league = get_league_data(league_name)
    games = [game.__dict__ for game in league.games]
    return jsonify(games)

@app.route('/api/players/<league_name>', methods=['GET'])
def get_players(league_name):
    league = get_league_data(league_name)
    players = [player.__dict__ for player in league.players.values()]
    return jsonify(players)

@app.route('/api/player/<league_name>/<player_name>', methods=['GET'])
def get_player_profile(league_name, player_name):
    league = get_league_data(league_name)
    if player_name in league.players:
        return jsonify(league.players[player_name].get_player_profile())
    return jsonify({'error': 'Player not found'}), 404

@app.route('/api/add_game/<league_name>', methods=['POST'])
def add_game(league_name):
    data = request.json
    league = get_league_data(league_name)
    
    league.add_game(
        [data['red_player1'], data['red_player2'], data['blue_player1'], data['blue_player2']],
        data['red_score'],
        data['blue_score'],
        data['date_time']
    )
    league.save_foosdat(os.path.join(DATA_FOLDER, f"{league_name}.csv"))
    return jsonify({'message': 'Game added successfully'})

@app.route('/api/delete_game/<league_name>/<int:game_id>', methods=['DELETE'])
def delete_game(league_name, game_id):
    league = get_league_data(league_name)
    if game_id < len(league.games):
        league.games.pop(game_id)
        league.save_foosdat(os.path.join(DATA_FOLDER, f"{league_name}.csv"))
        return jsonify({'message': 'Game deleted successfully'})
    return jsonify({'error': 'Invalid game ID'}), 400

# ------------------- RUN APP ------------------- #

if __name__ == '__main__':
    app.run(debug=True)
