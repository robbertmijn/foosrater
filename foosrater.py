from datetime import datetime
from typing import List, Tuple

# test

class Player:
    def __init__(self, name: str, elo: int = 1000, games: list = None):
        self.name = name
        self.elo = elo
        self.games = games if games is not None else []

    def __repr__(self):
        return f"PLAYER | {self.name}, elo: {self.elo}, games: {len(self.games)}"


class Game:
    def __init__(self, 
                 red_team: Tuple[Player, Player], 
                 blue_team: Tuple[Player, Player], 
                 red_score: int, 
                 blue_score: int, 
                 date_time: datetime):
        self.red_team = red_team
        self.blue_team = blue_team
        self.red_score = red_score
        self.blue_score = blue_score
        self.date_time = date_time             
        
    def __repr__(self):
        return (f"GAME | red team: {self.red_team[0].name} & {self.red_team[1].name} vs "
                f"blue team: {self.blue_team[0].name} & {self.blue_team[1].name} - "
                f"{self.red_score} - {self.blue_score}, on {self.date_time}"
                )


class League:
    def __init__(self):
        self.players = {}
        self.games = []

    # def add_players(self, player: Player):
    #     self.players[player.name] = player

    def add_game(self, 
                 red_team: Tuple[str, str], 
                 blue_team: Tuple[str, str], 
                 red_score: int, 
                 blue_score: int, 
                 date_time: datetime):
        
        for player_name in [red_team[0], red_team[1], blue_team[0], blue_team[1]]:
            if player_name != "" and player_name not in self.players:
                self.players[player_name] = Player(player_name)
                
        game = Game((self.players[red_team[0]], self.players[red_team[1]]),
                    (self.players[blue_team[0]], self.players[blue_team[1]]),
                    red_score, blue_score, date_time)
        
        for player in [self.players[red_team[0]],  self.players[red_team[1]], 
                    self.players[blue_team[0]], self.players[blue_team[1]]]:

            player.games.append(game)
            
        self.games.append(game)
        # self.recalculate_elo()

    def edit_game(self, game_index: int, red_score: int, blue_score: int):
        if 0 <= game_index < len(self.games):
            self.games[game_index].red_score = red_score
            self.games[game_index].blue_score = blue_score
            self.recalculate_elo()
        else:
            print("Invalid game index")

    def calculate_elo(self, red_team_elo: float, blue_team_elo: float, red_score: int, blue_score: int):
        K = 32
        expected_red = 1 / (1 + 10 ** ((blue_team_elo - red_team_elo) / 400))
        expected_blue = 1 / (1 + 10 ** ((red_team_elo - blue_team_elo) / 400))
        if red_score > blue_score:
            red_actual, blue_actual = 1, 0
        elif blue_score > red_score:
            red_actual, blue_actual = 0, 1
        else:
            red_actual, blue_actual = 0.5, 0.5
        
        red_team_elo += K * (red_actual - expected_red)
        blue_team_elo += K * (blue_actual - expected_blue)
        return red_team_elo, blue_team_elo

    def recalculate_elo(self):
        for player in self.players.values():
            player.elo = 1000.0

        for game in self.games:
            red_team_elo = (game.red_team[0].elo + game.red_team[1].elo) / 2
            blue_team_elo = (game.blue_team[0].elo + game.blue_team[1].elo) / 2
            red_team_elo, blue_team_elo = self.calculate_elo(red_team_elo, blue_team_elo, game.red_score, game.blue_score)

            game.red_team[0].elo = red_team_elo
            game.red_team[1].elo = red_team_elo
            game.blue_team[0].elo = blue_team_elo
            game.blue_team[1].elo = blue_team_elo
            
    def __repr__(self):
        
        return(f"{self.games}")


league = League()

league.add_game(("Robbert", "Anne"), ("Manon", "Sjoerd"), 3, 2, datetime.now())
league.add_game(("Anne", "Manon"), ("Jasper", "Rob"), 1, 4, datetime.now())

league.games
league.players
league

# for player in league.players.values():
#     print(player)

# league.edit_game(0, 2, 2)

# for player in league.players.values():
#     print(player)
