from flask import Flask, abort, render_template, request, redirect, url_for, jsonify, send_from_directory
import qrcode
import io
import base64

from foosrater import League
from storage import PostgresStorage


app = Flask(__name__)
storage = PostgresStorage()


def _new_league(league_name):
    if league_name == "hmt_2024":
        from elo_2024 import HMT2024League
        return HMT2024League()
    return League()


def _date_to_string(value):
    """Convert a Postgres datetime to the format expected by League.add_game."""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    return str(value)


def load_league(league_name):
    """Load one league from Postgres and rebuild its derived Elo state."""
    rows = storage.list_games(league_name)
    league = _new_league(league_name)

    for row in rows:
        league.add_game(
            [row["r1"], row["r2"], row["b1"], row["b2"]],
            row["red_score"],
            row["blue_score"],
            _date_to_string(row["date_time"]),
        )

    return league, rows


def _row_for_game_index(rows, game_id):
    if game_id < 0 or game_id >= len(rows):
        abort(404)
    return rows[game_id]


@app.route("/<league_name>", methods=["GET", "POST"])
def index(league_name):
    if request.method == "POST":
        storage.add_game(
            league_name=league_name,
            r1=request.form["red_player1"].strip(),
            r2=request.form["red_player2"].strip(),
            b1=request.form["blue_player1"].strip(),
            b2=request.form["blue_player2"].strip(),
            red_score=request.form["red_score"],
            blue_score=request.form["blue_score"],
            date_time=request.form["date_time"],
        )
        return redirect(url_for("index", league_name=league_name))

    league, _ = load_league(league_name)

    games = reversed([game.__dict__ for game in league.games])
    league._sort_players()
    players_ranked = [
        player.__dict__
        for player in league.players.values()
        if player.name != "" and player.ranking > 0
    ]
    players_unranked = [
        player.__dict__
        for player in league.players.values()
        if player.name != "" and player.ranking == 0
    ]

    return render_template(
        "index.html",
        players_ranked=players_ranked,
        players_unranked=players_unranked,
        games=games,
        league_name=league_name,
    )


@app.route("/create_league/<league_name>", methods=["GET", "POST"])
def create_league(league_name):
    # Leagues are implicit in the games table. An empty league starts existing
    # as soon as its first game is inserted.
    return redirect(url_for("index", league_name=league_name))


@app.route("/<league_name>/edit_game/<int:game_id>", methods=["GET", "POST"])
def edit_game(league_name, game_id):
    league, rows = load_league(league_name)
    row = _row_for_game_index(rows, game_id)

    if request.method == "POST":
        storage.update_game(
            game_id=row["id"],
            league_name=league_name,
            r1=request.form["red_player1"].strip(),
            r2=request.form["red_player2"].strip(),
            b1=request.form["blue_player1"].strip(),
            b2=request.form["blue_player2"].strip(),
            red_score=request.form["red_score"],
            blue_score=request.form["blue_score"],
            date_time=request.form["date_time"],
        )
        return redirect(url_for("index", league_name=league_name))

    game = league.games[game_id]
    return render_template(
        "edit_game.html",
        game=game,
        game_id=game_id,
        league_name=league_name,
    )


@app.route("/<league_name>/delete_game/<int:game_id>", methods=["POST"])
def delete_game(league_name, game_id):
    _, rows = load_league(league_name)
    row = _row_for_game_index(rows, game_id)
    storage.delete_game(game_id=row["id"], league_name=league_name)
    return redirect(url_for("index", league_name=league_name))


@app.route("/<league_name>/player/<string:player_name>")
def player_profile(league_name, player_name):
    league, _ = load_league(league_name)
    data = league.players[player_name].get_player_profile()
    return jsonify(data)


@app.route("/<league_name>/make_qr_poster")
def make_qr_poster(league_name):
    # Build the QR target from the active hostname so this works on Vercel
    # preview/production domains and custom domains.
    target_url = url_for("index", league_name=league_name, _external=True)

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(target_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return render_template(
        "qr_poster.html",
        league_name=league_name,
        target_url=target_url,
        img_base64=img_base64,
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/vnd.microsoft.icon")


if __name__ == "__main__":
    app.run(debug=True)
