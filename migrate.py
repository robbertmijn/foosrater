import os
import json
import csv
import foosrater as fr

def load_json_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []


games = load_json_data("data/games.json")
foosdat = []
for game in games:
    foosdat.append([game["red_player1"],
                    game["red_player2"],
                    game["blue_player1"],
                    game["blue_player2"],
                    game["red_goals"],
                    game["blue_goals"],
                    game["date"] + "T00:00:00",
                    ])
    
# create new league
DATA_FOLDER = "data"
league_name = "foosdat_all"
league_data = os.path.join(DATA_FOLDER, league_name + ".csv")

with open(league_data, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["R1", "R2", "B1", "B2", "red_score", "blue_score", "date_time"])
    writer.writerows(foosdat)

# with open("data/foosdat_2025.csv", mode="r", encoding="utf-8") as file:
#     reader = csv.reader(file)
#     for row in reader:
#         print(row)

# league = fr.League()
# league.load_foosdat("foosrater/data/foosdat.csv")

# league.save_foosdat("data/foosdat_2024.csv")