import pygame
import random
from GUI import (
    charger_assets,
    dessiner_fond,
    dessiner_fruit,
    dessiner_bombe,
    dessiner_fruit_coupe,
    dessiner_lame,
    dessiner_bonus,
    dessiner_pause,
)

from score_manager import sauvegarder_score

def _params_difficulty(diff):
    if diff == "easy":
        return {"speed": 16.0, "gravity": 0.32, "spawn": 34}
    if diff == "hard":
        return {"speed": 18.0, "gravity": 0.36, "spawn": 24}
    return {"speed": 17.0, "gravity": 0.34, "spawn": 28}

def _spawn_fruit(cfg, width, height, now_ms, last_freeze_ms):
    noms = ["pomme", "banane", "pasteque", "kiwi"]
    allow_freeze = (now_ms - last_freeze_ms) > 8000  # arcade: 8s

    nom = random.choice(noms)
    if allow_freeze and random.random() < 0.05:
        nom = "freeze"
        last_freeze_ms = now_ms

    x = random.randint(80, width - 80)
    if x < width // 3:
        vx = random.uniform(2.5, 6.5)
    elif x > (width * 2) // 3:
        vx = random.uniform(-6.5, -2.5)
    else:
        vx = random.uniform(-3.5, 3.5)

    fruit = {
        "nom": nom,
        "x": float(x),
        "y": float(height + 80),
        "vx": vx,
        "vy": -(cfg["speed"] + random.uniform(3.0, 7.0)),
        "g": cfg["gravity"],
        "rot": random.uniform(-12, 12),
        "rot_v": random.uniform(-8, 8),
        "size": 130 if nom != "freeze" else 125,
        "coupe": False,
    }
    return fruit, last_freeze_ms

def _spawn_bombe(cfg, width, height):
    x = random.randint(100, width - 100)
    vx = random.uniform(-3.0, 3.0)
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
    variante = 0 if direction < 0 else 1
    return {
        "nom": fruit["nom"],
        "x": fruit["x"],
        "y": fruit["y"],
        "vx": direction * 4.5,
        "vy": -2.8,
        "g": 0.38,
        "rot": 0.0,
        "rot_v": direction * 12.0,
        "timer": 50,
        "variant": variante,
        "size": 120,
    }

def _dessiner_timer_score(screen, assets, width, score, temps_restant):
    font = assets["font_ui"]
    t_score = font.render(f"{score}", True, (255, 255, 255))
    t_time = font.render(f"{int(temps_restant)}", True, (255, 255, 100) if temps_restant > 10 else (255, 80, 80))
    screen.blit(t_score, (20, 20))
    screen.blit(t_time, (width - 120, 20))

def jouer_arcade(difficulty="normal", window_size=(1200, 800)):
    pygame.init()

    WIDTH, HEIGHT = window_size
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fruit Ninja - Arcade (Neon)")
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
    etat = "jeu"  # jeu / pause / resultats

    start_ms = pygame.time.get_ticks()
    total_time = 30.0

    timer_spawn = 0
    freeze_timer = 0
    last_freeze_ms = -999999
    combo_count = 0

    running = True
    while running:
        now_ms = pygame.time.get_ticks()

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if etat == "jeu":
                        etat = "pause"
                    elif etat == "pause":
                        etat = "jeu"
                if etat == "pause" and event.key == pygame.K_q:
                    return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
                points = [event.pos]
                if etat == "resultats":
                    return

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
                points = []
                combo_count = 0

            if event.type == pygame.MOUSEMOTION and mouse_down:
                points.append(event.pos)
                if len(points) > 12:
                    points.pop(0)

        # TIMER
        elapsed = (now_ms - start_ms) / 1000.0
        temps_restant = max(0.0, total_time - elapsed)

        if etat == "jeu" and temps_restant <= 0:
            sauvegarder_score("arcade", score)
            etat = "resultats"

        # UPDATE
        if etat == "jeu":
            facteur = 1.0
            if freeze_timer > 0:
                freeze_timer -= 1
                facteur = 0.25

            # spawn
            timer_spawn += 1 * facteur
            if timer_spawn >= cfg["spawn"]:
                timer_spawn = 0

                # densité selon temps restant
                if temps_restant > 20:
                    nb = random.randint(2, 4)
                elif temps_restant > 10:
                    nb = random.randint(3, 6)
                elif temps_restant > 5:
                    nb = random.randint(5, 8)
                else:
                    nb = random.randint(7, 11)

                max_on_screen = 18
                if len(fruits) + nb > max_on_screen:
                    nb = max(0, max_on_screen - len(fruits))

                for _ in range(nb):
                    f, last_freeze_ms = _spawn_fruit(cfg, WIDTH, HEIGHT, now_ms, last_freeze_ms)
                    fruits.append(f)

                # bombs (plus fréquent)
                if random.random() < 0.40 and len(bombes) < 5:
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
                for f in fruits:
                    if f["coupe"]:
                        continue
                    for p in points:
                        if _souris_touche(f, p):
                            f["coupe"] = True

                            combo_count += 1
                            pts = 1
                            txt = "+1"

                            if combo_count >= 3:
                                pts = combo_count
                                txt = f"{combo_count}x!"

                            if f["nom"] == "freeze":
                                freeze_timer = 240
                                txt = "FREEZE"
                                pts = 0

                            score += pts

                            if f["nom"] != "freeze":
                                moities.append(_creer_moitie(f, -1))
                                moities.append(_creer_moitie(f, 1))

                            bonus_textes.append({
                                "texte": txt,
                                "x": f["x"],
                                "y": f["y"],
                                "timer": 35,
                                "color": (255, 230, 100) if "x" in txt else (255, 255, 255),
                            })
                            break

                # bombes => pénalité, pas game over
                for b in bombes:
                    for p in points:
                        if _souris_touche(b, p):
                            score = max(0, score - 10)
                            bonus_textes.append({
                                "texte": "-10",
                                "x": b["x"],
                                "y": b["y"],
                                "timer": 40,
                                "color": (255, 80, 80),
                            })
                            b["y"] = HEIGHT + 999  # remove
                            break

            # cleanup
            fruits = [f for f in fruits if (not f["coupe"]) and f["y"] < HEIGHT + 140]
            bombes = [b for b in bombes if b["y"] < HEIGHT + 140]
            moities = [m for m in moities if m["timer"] > 0]

            for b in bonus_textes:
                b["y"] -= 1.4
                b["timer"] -= 1
            bonus_textes = [b for b in bonus_textes if b["timer"] > 0]

        # DRAW
        dessiner_fond(screen, WIDTH, HEIGHT, assets)

        if etat == "jeu":
            for m in moities:
                dessiner_fruit_coupe(screen, assets, m)
            for f in fruits:
                dessiner_fruit(screen, assets, f)
            for b in bombes:
                dessiner_bombe(screen, assets, b)

            dessiner_lame(screen, points)
            _dessiner_timer_score(screen, assets, WIDTH, score, temps_restant)
            dessiner_bonus(screen, assets, bonus_textes)

        elif etat == "pause":
            dessiner_pause(screen, assets, WIDTH, HEIGHT)

        else:  # resultats
            # écran simple de fin (propre, rapide)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            screen.blit(overlay, (0, 0))

            ft = assets["font_title"]
            fu = assets["font_ui"]

            t = ft.render("TEMPS ECOULE !", True, (255, 255, 255))
            s = fu.render(f"Score : {score}", True, (255, 230, 100))
            h = fu.render("Clique pour revenir au menu", True, (200, 200, 200))

            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 120))
            screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT // 2 + 30))

        pygame.display.flip()
        clock.tick(60)
