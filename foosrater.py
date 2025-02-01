from datetime import datetime
from typing import List, Tuple
import csv


class Player:

    def __init__(self, name: str, elo: list = [1000], games: list = None):
        self.name = name
        self.elo = elo
        self.games = games if games is not None else []
        self.n_games = 0
        self.league = "❌"
        self.ranking = 1
    
    
    def _update_league(self):
        league_ranges = [
                (1000, "🎷"),
                (1050, "🛒"),
                (1100, "🏹"),
                (1150, "🧀"),
                (1200, "🤖"),
                (1250, "🗜️"), 
                (1300, "🦒"),
                (1350, "🦋"),
            ]

        for threshold, img in league_ranges:
            if self.elo[-1] < threshold:
                self.league = img
                break
        self.league = "❌"
    

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
        self.K = 64
        self.S = 400
        # self.K = 64
        # self.S = 271
        self.init_elo = 1000.0


    def load_foosdat(self, foosfile):
        """
        Adds the rows of a csv as games in the league
        order:
        [name red1, name red2, name blue 1, name blue 2, red goals, blue goals, date]
        """

        with open(foosfile, mode="r", encoding="utf-8") as file:
            games = csv.reader(file)
            for game in games:
                self.add_game([game[0], game[1], game[2], game[3]], game[4], game[5], game[6])


    def save_foosdat(self, foosfile):
        
        foosdat = []
        for game in self.games:
            players = [game.R1.name, game.R2.name, game.B1.name, game.B2.name]
            foosdat.append([players + 
                           [game.red_score] + 
                           [game.blue_score] + 
                           [game.date_time]][0])

        with open(foosfile, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(foosdat)


    def edit_game(self, 
                  game_index: int,
                  player_names: list, 
                  red_score: int, 
                  blue_score: int, 
                  date_time: datetime):
        """
        Overwrites the game in the passed index with a new one.
        """
        if 0 <= game_index < len(self.games):
            self.add_game(player_names, red_score, blue_score, date_time, game_index)
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
                 date_time: datetime, 
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
        game = Game(len(self.games), cur_players, red_score, blue_score, date_time)
        self.games.insert(insert, game)

        # adds game to the player objects, and to the league object
        for player in cur_players:
            player.games.insert(insert, game)
            player.n_games = len(player.games)
            player._update_league()
        
        # Recalculate elo ratings
        self._update_elo()


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
            # calculate proportion of red goals
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
        for rank, player in enumerate(self.players.values()):
            player.ranking = rank + 1

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
    Returns expected proportion of goals the read team will make
    """
    return 1 / (1 + 10 ** ((blue_elo - red_elo) / S))