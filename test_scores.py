from score_manager import charger_scores, sauvegarder_score
import os

print("Testing Score Manager...")
if os.path.exists("scores.json"):
    print("scores.json found.")
    print(open("scores.json").read())
else:
    print("scores.json NOT found.")

scores = charger_scores()
print(f"Loaded scores: {scores}")

print("Saving dummy score...")
sauvegarder_score("classique", 100)
sauvegarder_score("arcade", 500)

scores_new = charger_scores()
print(f"New scores: {scores_new}")
