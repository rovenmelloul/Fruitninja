import json
import os

SCORE_FILE = "scores.json"


def charger_scores():
    if not os.path.exists(SCORE_FILE):
        return {"classique": 0, "arcade": 0}

    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # sécurise
        return {
            "classique": int(data.get("classique", 0)),
            "arcade": int(data.get("arcade", 0)),
        }
    except Exception:
        return {"classique": 0, "arcade": 0}


def sauvegarder_score(mode, score):
    scores = charger_scores()
    score = int(score)

    if score > int(scores.get(mode, 0)):
        scores[mode] = score
        try:
            with open(SCORE_FILE, "w", encoding="utf-8") as f:
                json.dump(scores, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    return False
