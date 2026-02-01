import pygame
import random
from GUI import (
    charger_assets,
    dessiner_fond,
    dessiner_fruit,
    dessiner_bombe,
    dessiner_fruit_coupe,
    dessiner_lame,
    dessiner_score,
    dessiner_bonus,
    dessiner_game_over,
    dessiner_pause,
)

from score_manager import sauvegarder_score

# ======================
# PARAM DIFFICULTÉ
# ======================
def _params_difficulty(diff):
    # Objectif: fruits montent bien => vitesse verticale initiale plus forte (plus négative)
    # Gravité: pas trop forte sinon ça retombe trop vite.
    if diff == "easy":
        return {"speed": 15.0, "gravity": 0.30, "spawn": 70, "spawn_min": 40}
    if diff == "hard":
        return {"speed": 17.0, "gravity": 0.34, "spawn": 55, "spawn_min": 28}
    return {"speed": 16.0, "gravity": 0.32, "spawn": 62, "spawn_min": 32}

def _spawn_fruit(cfg, width, height, now_ms, last_freeze_ms):
    noms = ["pomme", "banane", "pasteque", "kiwi"]  # kiwi mappé sur prune dans GUI
    allow_freeze = (now_ms - last_freeze_ms) > 10000  # 10 sec cooldown
    nom = random.choice(noms)

    # petite chance freeze
    if allow_freeze and random.random() < 0.03:
        nom = "freeze"
        last_freeze_ms = now_ms

    x = random.randint(80, width - 80)

    # vx selon position
    if x < width // 3:
        vx = random.uniform(2.0, 5.5)
    elif x > (width * 2) // 3:
        vx = random.uniform(-5.5, -2.0)
    else:
        vx = random.uniform(-2.5, 2.5)

    fruit = {
        "nom": nom,
        "x": float(x),
        "y": float(height + 80),
        "vx": vx,
        # IMPORTANT: pour monter plus haut -> on augmente l'impulsion initiale (vitesse_y plus négative)
        "vy": -(cfg["speed"] + random.uniform(3.0, 7.0)),
        "g": cfg["gravity"],
        "rot": random.uniform(-10, 10),
        "rot_v": random.uniform(-6, 6),
        "size": 130 if nom != "freeze" else 125,
        "coupe": False,
    }
    return fruit, last_freeze_ms

def _spawn_bombe(cfg, width, height):
    x = random.randint(100, width - 100)
    vx = random.uniform(-2.5, 2.5)
    bombe = {
        "x": float(x),
        "y": float(height + 80),
        "vx": vx,
        "vy": -(cfg["speed"] + random.uniform(2.0, 5.0)),
        "g": cfg["gravity"],
        "size": 130,
    }
    return bombe

def _move_obj(obj, facteur=1.0):
    obj["x"] += obj["vx"] * facteur
    obj["y"] += obj["vy"] * facteur
    obj["vy"] += obj["g"] * facteur
    if "rot" in obj:
        obj["rot"] += obj.get("rot_v", 0.0) * facteur

def _souris_touche(obj, point, radius=55):
    dx = obj["x"] - point[0]
    dy = obj["y"] - point[1]
    return (dx * dx + dy * dy) ** 0.5 < radius

def _creer_moitie(fruit, direction):
    # variante 0 ou 1 => on alterne les 2 sprites cut dispo
    variante = 0 if direction < 0 else 1
    return {
        "nom": fruit["nom"],
        "x": fruit["x"],
        "y": fruit["y"],
        "vx": direction * 4.0,
        "vy": -2.5,
        "g": 0.35,
        "rot": 0.0,
        "rot_v": direction * 10.0,
        "timer": 55,
        "variant": variante,
        "size": 120,
    }

def jouer_classique(difficulty="normal", window_size=(1200, 800)):
    pygame.init()

    WIDTH, HEIGHT = window_size
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fruit Ninja - Classique (Neon)")
    clock = pygame.time.Clock()

    assets = charger_assets()
    cfg = _params_difficulty(difficulty)

    fruits = []
    bombes = []
    moities = []
    bonus_textes = []

    points = []
    mouse_down = False

    score = 0
    vies = 3
    etat = "jeu"  # jeu / pause / game_over

    timer_spawn = 0
    start_ms = pygame.time.get_ticks()

    freeze_timer = 0
    last_freeze_ms = -999999

    combo_count = 0

    running = True
    while running:
        now_ms = pygame.time.get_ticks()

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if etat == "jeu":
                        etat = "pause"
                    elif etat == "pause":
                        etat = "jeu"
                if etat == "pause" and event.key == pygame.K_q:
                    return  # retour menu

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
                points = [event.pos]
                if etat == "game_over":
                    return

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
                points = []
                combo_count = 0

            if event.type == pygame.MOUSEMOTION and mouse_down:
                points.append(event.pos)
                if len(points) > 12:
                    points.pop(0)

        # UPDATE
        if etat == "jeu":
            facteur = 1.0

            # freeze ralentit tout
            if freeze_timer > 0:
                freeze_timer -= 1
                facteur = 0.30

            # spawn rate qui accélère légèrement avec le temps
            t_sec = (now_ms - start_ms) / 1000
            spawn_delay = int(cfg["spawn"] - (t_sec / 2))
            spawn_delay = max(spawn_delay, cfg["spawn_min"])

            timer_spawn += 1 * facteur
            if timer_spawn >= spawn_delay:
                timer_spawn = 0

                # nombre fruits par vague selon temps
                if t_sec < 15:
                    nb = random.randint(1, 2)
                elif t_sec < 45:
                    nb = random.randint(2, 4)
                elif t_sec < 90:
                    nb = random.randint(3, 6)
                else:
                    nb = random.randint(4, 7)

                # limite écran
                max_on_screen = 12
                if len(fruits) + nb > max_on_screen:
                    nb = max(0, max_on_screen - len(fruits))

                for _ in range(nb):
                    f, last_freeze_ms = _spawn_fruit(cfg, WIDTH, HEIGHT, now_ms, last_freeze_ms)
                    fruits.append(f)

                # bombe (1/3)
                if random.randint(1, 3) == 1 and len(bombes) < 3:
                    bombes.append(_spawn_bombe(cfg, WIDTH, HEIGHT))

            # move
            for f in fruits:
                _move_obj(f, facteur)
            for b in bombes:
                _move_obj(b, facteur)
            for m in moities:
                _move_obj(m, facteur)
                m["timer"] -= 1

            # collisions
            if mouse_down and points:
                # fruits
                for f in fruits:
                    if f["coupe"]:
                        continue
                    for p in points:
                        if _souris_touche(f, p):
                            f["coupe"] = True

                            combo_count += 1
                            gain = 10
                            txt = "+10"

                            if combo_count >= 3:
                                gain = 10 * combo_count
                                txt = f"{combo_count}x COMBO (+{gain})"

                            # freeze
                            if f["nom"] == "freeze":
                                freeze_timer = 300  # 5s
                                txt = "FREEZE !"
                                gain = 0

                            score += gain

                            # moities uniquement pour fruits "normaux" (pas bombe/freeze)
                            if f["nom"] not in ("freeze",):
                                moities.append(_creer_moitie(f, -1))
                                moities.append(_creer_moitie(f, 1))

                            bonus_textes.append({
                                "texte": txt,
                                "x": f["x"],
                                "y": f["y"],
                                "timer": 45,
                                "color": (255, 230, 100) if "COMBO" in txt else (255, 255, 255)
                            })
                            break

                # bombes => game over
                for b in bombes:
                    for p in points:
                        if _souris_touche(b, p):
                            etat = "game_over"
                            sauvegarder_score("classique", score)
                            break

            # cleanup fruits
            new_fruits = []
            for f in fruits:
                if f["coupe"]:
                    continue
                if f["y"] > HEIGHT + 140:
                    vies -= 1
                    if vies <= 0:
                        etat = "game_over"
                        sauvegarder_score("classique", score)
                    continue
                new_fruits.append(f)
            fruits = new_fruits

            bombes = [b for b in bombes if b["y"] < HEIGHT + 140]
            moities = [m for m in moities if m["timer"] > 0]

            for b in bonus_textes:
                b["y"] -= 1.8
                b["timer"] -= 1
            bonus_textes = [b for b in bonus_textes if b["timer"] > 0]

        # DRAW
        dessiner_fond(screen, WIDTH, HEIGHT, assets)

        if etat == "jeu":
            for m in moities:
                dessiner_fruit_coupe(screen, assets, m)

            for f in fruits:
                if not f["coupe"]:
                    dessiner_fruit(screen, assets, f)

            for b in bombes:
                dessiner_bombe(screen, assets, b)

            dessiner_lame(screen, points)
            dessiner_score(screen, assets, score, vies)
            dessiner_bonus(screen, assets, bonus_textes)

        elif etat == "pause":
            dessiner_pause(screen, assets, WIDTH, HEIGHT)

        elif etat == "game_over":
            dessiner_game_over(screen, assets, WIDTH, HEIGHT, score)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
