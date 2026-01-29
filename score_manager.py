import json
import os

SCORE_FILE = "scores.json"

def charger_scores():
    if not os.path.exists(SCORE_FILE):
        return {"classique": 0, "arcade": 0}
    try:
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"classique": 0, "arcade": 0}

def sauvegarder_score(mode, score):
    scores = charger_scores()
    
    # On ne sauvegarde que si c'est un meilleur score
    if score > scores.get(mode, 0):
        scores[mode] = score
        try:
            with open(SCORE_FILE, "w") as f:
                json.dump(scores, f)
            return True # Nouveau Record !
        except:
            pass
    return False
