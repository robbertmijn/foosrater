from datetime import datetime
from typing import List, Tuple
import csv
from collections import defaultdict


class Player:

    def __init__(self, name: str, elo: list = [1000], games: list = None):
        self.name = name
        self.elo = elo
        self.games = games if games is not None else []
        self.n_games = 0
        self.league = "❌"
        self.ranking = 0
    
    
    def _update_league(self):
        league_ranges = [
                (800, "🎷"),
                (850, "🛒"),
                (900, "🏹"),
                (950, "🧀"),
                (1000, "🤖"),
                (1050, "🗜️"), 
                (1100, "🦒"),
                (1150, "🦋"),
            ]

        for threshold, img in league_ranges:
            if self.elo[-1] < threshold:
                self.league = img
                break
            else:
                self.league = "❌"
    

    def get_player_profile(self):
        
        # with open(GAMES_FILE, 'r') as f:
        #     games = json.load(f)

        def countdict():
            return {"opponent": 0, "made": 0, "let": 0, }
        
        # Store how many times players have played against each other
        opponents = defaultdict(lambda: defaultdict(countdict))
        teammates = defaultdict(int)
        # teammates = defaultdict(lambda: defaultdict(int))
        player_game_counts = defaultdict(int)

        # Analyze all the matches in the data
        for game in self.games:
            
            # Which position did the player play?
            team = "red" if self.name in [game.R1.name, game.R2.name] else "blue"
            opposing_team = "blue" if team == "red" else "red"
            teammate_index = 1 if self.name in [game.R1.name, game.B1.name] else 0

            team_players = {
                "red": (game.R1.name, game.R2.name),
                "blue": (game.B1.name, game.B2.name)
            }

            # Assign teammates
            teammates[team_players[team][teammate_index]] += 1

            # Assign opponents
            for opponent in team_players[opposing_team]:
                print(opponents[opponent]["opponent"]["opponent"])
                opponents[opponent]["opponent"]["opponent"] += 1
                opponents[opponent]["opponent"]["made"] += int(game.red_score if team == "red" else game.blue_score)
                opponents[opponent]["opponent"]["let"] += int(game.blue_score if team == "red" else game.red_score)

        opponents=sorted(opponents[self.name].items(), key=lambda x: x[1]["opponent"], reverse=True)[:5]
        teammates=sorted(teammates[self.name].items(), key=lambda x: x[1], reverse=True)[:5]
        
        player_profile = dict(name=self.name, 
                            opponents=opponents,
                            teammates=teammates)
            
        return player_profile


    def plot_elo(self):
        import matplotlib.pyplot as plt
        from datetime import datetime
        plt.figure("Scatterplot with Dates", figsize=(8, 6))  # Creates or references a figure named "Scatterplot with Dates"
        plt.clf()  # Clear the figure to overwrite any existing content
        plt.scatter([datetime.strptime(g.date_time, "%Y-%m-%d") for g in self.games], self.elo[1:])
        plt.plot([datetime.strptime(g.date_time, "%Y-%m-%d") for g in self.games], self.elo[1:])

        plt.show()

    def __repr__(self):
        return self.name


class Game:
    def __init__(self, 
                 id: int,
                 players: list,
                 red_score: int, 
                 blue_score: int, 
                 date_time: datetime):
        self.id = id
        self.R1, self.R2, self.B1, self.B2 = players
        self.r1_elo = self.R1.elo[-1]
        self.r2_elo = self.R2.elo[-1]
        self.r1_elo_delta = 0
        self.r2_elo_delta = 0
        self.b1_elo = self.B1.elo[-1]
        self.b2_elo = self.B2.elo[-1]
        self.b1_elo_delta = 0
        self.b2_elo_delta = 0
        self.red_score = int(red_score)
        self.blue_score = int(blue_score)
        self.date_time = date_time
        self.red_team_elo = _load_team_elo((self.R1, self.R2))
        self.blue_team_elo = _load_team_elo((self.B1, self.B2))
        self.abs_error = 0


    def __repr__(self):
        return (f"{self.R1}/{self.R2} vs {self.B1}/{self.B2}"
                f"{self.red_score} - {self.blue_score}, on {self.date_time}\n"
                )
    

class League:
    def __init__(self):
        self.players = {}
        self.games = []

        # Set some general parameters. Only S seems to influence prediction accuracy. Experiments showed 271 as optimum.
        # self.K = 64
        # self.S = 400
        self.K = 64
        self.S = 271
        self.init_elo = 1000.0


    def load_foosdat(self, foosfile):
        """
        Adds the rows of a csv as games in the league
        order:
        [name red1, name red2, name blue 1, name blue 2, red score, blue score, date]
        """
        with open(foosfile, mode="r", encoding="utf-8") as file:
            game_rows = csv.DictReader(file)
            for game in game_rows:
                self.add_game([game["R1"], game["R2"], game["B1"], game["B2"]], 
                              game["red_score"], 
                              game["blue_score"], 
                              game["date_time"])


    def save_foosdat(self, foosfile):
        
        with open(foosfile, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["R1", "R2", "B1", "B2", "red_score", "blue_score", "date_time"])
            for game in self.games:

                writer.writerow([game.R1.name, game.R2.name, game.B1.name, game.B2.name,
                                 game.red_score, 
                                 game.blue_score, 
                                 game.date_time.strftime("%Y-%m-%dT%H:%M:%S")])


    def edit_game(self, 
                  player_names: list, 
                  red_score: int, 
                  blue_score: int, 
                  date_time: datetime, 
                  game_index: int):
        """
        Overwrites the game in the passed index with a new one.
        """
        if 0 <= game_index < len(self.games):
            self.games.pop(game_index)
            self.add_game(player_names, red_score, blue_score, date_time, game_index+1)
        else:
            print("Invalid game index")


    def add_player(self, name):
        """
        Adds a player to the league if its new
        """
        if name not in self.players:
            self.players[name] = Player(name)
        else:
            pass


    def add_game(self, 
                 player_names: list, 
                 red_score: int, 
                 blue_score: int, 
                 date_time_str: str, 
                 insert: int = 0):
        """
        Add a new game
        """
        # gets players and adds them to the league if needed
        cur_players = []
        for player_name in player_names:
            self.add_player(player_name)
            cur_players.append(self.players[player_name])
        
        # initialize new game object and insert at beginning of games list
        date_time = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S")
        game = Game(len(self.games), cur_players, red_score, blue_score, date_time)
        self.games.insert(insert, game)
        
        self._sort_games()
        
        # Recalculate elo ratings
        self._update_elo()
        
        # adds game to the player objects, and to the league object
        for player in cur_players:
            player.games.insert(insert, game)
            player.n_games = len(player.games)
            player._update_league()
        

    def _update_elo(self):
        """
        Recalculates elo rating by going over each game
        """
        K = self.K

        # Reset each players' rating, initialize a list starting with the init_elo (1000)
        for player in self.players.values():
            player.elo = [self.init_elo]

        # TODO: sort games on date
        for game in self.games:
            # calculate proportion of red score
            game.red_outcome = game.red_score / (game.red_score + game.blue_score)
            # proportions add up to 1
            game.blue_outcome = 1 - game.red_outcome

            game.expected_outcome_red = _expected_outcome_red(game.red_team_elo[0], game.blue_team_elo[0], self.S)
            game.expected_outcome_blue = 1 - game.expected_outcome_red

            game.abs_error = abs(game.expected_outcome_red - game.red_outcome)

            game.r1_elo_delta = (game.red_outcome - game.expected_outcome_red) * K
            game.r2_elo_delta = (game.red_outcome - game.expected_outcome_red) * K
            game.b1_elo_delta = (game.blue_outcome - game.expected_outcome_blue) * K
            game.b2_elo_delta = (game.blue_outcome - game.expected_outcome_blue) * K
            
            game.r1_elo = game.R1.elo[-1]
            game.r2_elo = game.R2.elo[-1]
            game.b1_elo = game.B1.elo[-1]
            game.b2_elo = game.B2.elo[-1]

            game.R1.elo.append(game.R1.elo[-1] + game.r1_elo_delta)
            game.R2.elo.append(game.R2.elo[-1] + game.r2_elo_delta)
            game.B1.elo.append(game.B1.elo[-1] + game.b1_elo_delta)
            game.B2.elo.append(game.B2.elo[-1] + game.b2_elo_delta)
        
        self._sort_players()
            

    def _sort_players(self):
        """
        Sort player list based on their latest elo rating
        """

        # Sort the dict
        self.players = dict(reversed(sorted(self.players.items(), key=lambda kv: kv[1].elo[-1])))
        
        # Based on position in the new dict, set ranking
        rank = 1
        for player in self.players.values():
            if player.n_games >= 3:
                player.ranking = rank
                rank += 1
            else:
                player.ranking = 0
    
    
    def _sort_games(self):
        """
        Sort games list based on date
        """
        # Sort the dict
        self.games = list(reversed(sorted(self.games, key=lambda game: game.date_time)))
        game_ids = reversed(range(len(self.games)))
        for game, game_id in zip(self.games, game_ids):
            game.id = game_id
            

    def __repr__(self):
        
        return(f"{self.games}")


def _load_team_elo(team):
    """
    Return mean elo, or in the case of 1v1, the elo of player 1
    Also returns the mean number of games each team has played earlier
    """
    if "" in [p.name for p in team]: 
        return team[0].elo[-1], len(team[0].games)
    else:
        return (team[0].elo[-1] + team[1].elo[-1]) / 2, (len(team[0].games) + len(team[1].games)) / 2
        

def _expected_outcome_red(red_elo, blue_elo, S: int=400):
    """
    Returns expected proportion of score the read team will make
    """
    return 1 / (1 + 10 ** ((blue_elo - red_elo) / S))