from foosrater import _expected_outcome

def _update_elo_2024(self):
    """
    Recalculates elo rating by going over each game
    """
    K = 64
    self.S = 400

    # Reset each players' rating, initialize a list starting with the init_elo (1000)
    for player in self.players.values():
        player.elo = [self.init_elo]

    # TODO: sort games on date
    for game in self.games:
        # calculate proportion of red score
        
        red_C = 1 if game.red_score > game.blue_score else 0
        blue_C = 0 if game.red_score > game.blue_score else 1
        game.red_outcome = (game.red_score + red_C) / (game.red_score + game.blue_score)
        game.blue_outcome = (game.blue_score + blue_C) / (game.red_score + game.blue_score)

        game.expected_outcome_red = _expected_outcome(game.red_team_elo[0], game.blue_team_elo[0], self.S)
        game.expected_outcome_blue = _expected_outcome(game.blue_team_elo[0], game.red_team_elo[0], self.S)

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