from flask_app import load_data
import csv
import foosrater.foosrater as fr


# games = load_data("data/games (1).json")
# foosdat = []
# for game in games:
#     foosdat.append([game["red_player1"],
#                     game["red_player2"],
#                     game["blue_player1"],
#                     game["blue_player2"],
#                     game["red_goals"],
#                     game["blue_goals"],
#                     game["date"],
#                     ])

# with open("foosdat.csv", mode="w", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerows(foosdat)

# with open("foosdat.csv", mode="r", encoding="utf-8") as file:
#     reader = csv.reader(file)
#     for row in reader:
#         print(row)

league = League()
league.load_foosdat("foosrater/data/foosdat.csv")

league.save_foosdat("foosrater/data/foosdat2.csv")