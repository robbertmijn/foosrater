from datetime import datetime
from typing import List, Tuple
import csv


def _elo_change(expected_goals, actual_goals, k):
    
    return k * (actual_goals - expected_goals)

def _load_team_elo(team):
        """
        Return mean elo, or in the case of 1v1, the elo of player 1
        """

        if "" in team: 
            return team[0].elo[-1]
        else:
            return (team[0].elo[-1] + team[1].elo[-1]) / 2
        

def _expected_outcome_red(red_elo, blue_elo):
    return 1 / (1 + 10 ** ((red_elo - blue_elo) / 400))

class Player:
    def __init__(self, name: str, elo: list = [1000], games: list = None):
        self.name = name
        self.elo = elo
        self.games = games if games is not None else []
    

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
                 players: list,
                 red_score: int, 
                 blue_score: int, 
                 date_time: datetime):
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

    def load_foosdat(self, foosfile):
        
        with open(foosfile, mode="r", encoding="utf-8") as file:
            games = csv.reader(file)
            for game in games:
                self.add_game([game[0], game[1], game[2], game[3]], game[4], game[5], game[6])

    def save_foosdat(self, foosfile):
        
        foosdat = []
        for game in self.games:
            players = game.R1.name + game.R2.name + game.B1.name + game.name
            foosdat.append([players + 
                           [game.red_score] + 
                           [game.blue_score] + 
                           [game.date_time]][0])

        with open(foosfile, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(foosdat)


    def add_player(self, name):

        if name not in self.players:
            self.players[name] = Player(name)
        else:
            pass


    def add_game(self, 
                 player_names: list, 
                 red_score: int, 
                 blue_score: int, 
                 date_time: datetime):

        cur_players = []
        for player_name in player_names:
            self.add_player(player_name)
            cur_players.append(self.players[player_name])
                
        game = Game(cur_players, red_score, blue_score, date_time)

        for player in cur_players:
            player.games.append(game)
            
        self.games.append(game)

        self._update_elo()


    def edit_game(self, game_index: int, red_score: int, blue_score: int):
        if 0 <= game_index < len(self.games):
            # TODO: edit date_time
            self.games[game_index].red_score = red_score
            self.games[game_index].blue_score = blue_score
        else:
            print("Invalid game index")


    def _update_elo(self):

        K = 32

        for player in self.players.values():
            player.elo = [1000.0]

        # TODO: sort games on date
        for game in reversed(self.games):
            # calculate proportion of red goals
            red_outcome = game.red_score / (game.red_score + game.blue_score)
            # proportions add up to 1
            blue_outcome = 1 - red_outcome

            expected_outcome_red = _expected_outcome_red(game.red_team_elo, game.blue_team_elo)
            expected_outcome_blue = 1 - expected_outcome_red

            game.abs_error = abs(expected_outcome_red - red_outcome)

            # TODO: these are not changed in edit yet!
            game.R1.elo.append(game.R1.elo[-1] + (red_outcome - expected_outcome_red) * K)
            game.R2.elo.append(game.R2.elo[-1] + (red_outcome - expected_outcome_red) * K)
            game.B1.elo.append(game.B1.elo[-1] + (blue_outcome - expected_outcome_blue) * K)
            game.B2.elo.append(game.B2.elo[-1] + (blue_outcome - expected_outcome_blue) * K)
            

    def _sort_players(self):

        self.players = dict(sorted(self.players.items(), key=lambda kv: kv[1].elo[-1]))
        

    def __repr__(self):
        
        return(f"{self.games}")
    

league = League()
league.load_foosdat("foosrater/data/foosdat.csv")
# league.players["Robbert"].plot_elo()
# league.players["Robin"].plot_elo()
# print(league._get_ranking())
league._sort_players()
[f"{p.name}/{p.elo[-1]}" for p in league.players]