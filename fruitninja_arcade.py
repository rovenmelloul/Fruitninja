# ============================================
# FRUITNINJA_ARCADE.py - Mode Arcade
# ============================================
# Mode 60 secondes, score max, pas de Game Over !
# ============================================

import pygame
import random
from GUI import (
    charger_images,
    dessiner_fond,
    dessiner_fruit,
    dessiner_bombe,
    dessiner_lame,
    dessiner_score,
    dessiner_bonus,
    dessiner_fruit_coupe,
    dessiner_pause
)
from score_manager import sauvegarder_score

# -------------------------------------------
# PARAMÈTRES DU JEU
# -------------------------------------------
LARGEUR = 800
HAUTEUR = 600
TAILLE_FRUIT = 40

# Physique similaire au jeu de base
VITESSE_INITIALE = 11.0   
VITESSE_MAX = 13.5        
GRAVITE_INITIALE = 0.32
GRAVITE_MAX = 0.45
SPAWN_INITIAL = 60        # Plus rapide dès le début !
SPAWN_MIN = 20            # Très très rapide à la fin
FRUITS_MAX = 20           # Plus de fruits possible en Arcade

# -------------------------------------------
# CRÉER UN FRUIT
# -------------------------------------------
def creer_fruit(vitesse, gravite, allow_freeze=True):
    """Crée un nouveau fruit"""
    noms_fruits = ["pasteque", "orange", "pomme", "banane", "kiwi"]
    
    # Plus de chance de Freeze en Arcade (5%)
    nom_fruit = random.choice(noms_fruits)
    if allow_freeze and random.random() < 0.05:
        nom_fruit = "freeze"
    
    x = random.randint(50, LARGEUR - 50)
    
    if x < LARGEUR // 3:
        vitesse_x = random.uniform(2, 6) # Un peu plus rapide horizontalement
    elif x > LARGEUR * 2 // 3:
        vitesse_x = random.uniform(-6, -2)
    else:
        vitesse_x = random.uniform(-3, 3)
    
    fruit = {
        "nom": nom_fruit,
        "x": x,
        "y": HAUTEUR + 50,
        "vitesse_x": vitesse_x,
        "vitesse_y": -vitesse - random.uniform(0, 3),
        "gravite": gravite,
        "rotation": 0,
        "rotation_vitesse": random.uniform(-10, 10), # Rotation plus rapide
        "coupe": False
    }
    return fruit

# -------------------------------------------
# CRÉER UNE BOMBE
# -------------------------------------------
def creer_bombe(vitesse, gravite):
    """Crée une bombe"""
    bombe = {
        "x": random.randint(100, LARGEUR - 100),
        "y": HAUTEUR + 50,
        "vitesse_x": random.uniform(-2, 2),
        "vitesse_y": -vitesse - random.uniform(0, 2),
        "gravite": gravite
    }
    return bombe

# -------------------------------------------
# CRÉER UNE MOITIÉ
# -------------------------------------------
def creer_moitie(fruit, direction):
    moitie = {
        "nom": fruit["nom"],
        "x": fruit["x"],
        "y": fruit["y"],
        "vitesse_x": direction * 4,
        "vitesse_y": -3,
        "gravite": 0.35,
        "rotation": 0,
        "rotation_vitesse": direction * 15,
        "timer": 60
    }
    return moitie

# -------------------------------------------
# MOUVEMENTS
# -------------------------------------------
def bouger_fruit(fruit, facteur_vitesse=1.0):
    fruit["x"] += fruit["vitesse_x"] * facteur_vitesse
    fruit["y"] += fruit["vitesse_y"] * facteur_vitesse
    fruit["vitesse_y"] += fruit["gravite"] * facteur_vitesse
    fruit["rotation"] += fruit["rotation_vitesse"] * facteur_vitesse

def bouger_bombe(bombe, facteur_vitesse=1.0):
    bombe["x"] += bombe["vitesse_x"] * facteur_vitesse
    bombe["y"] += bombe["vitesse_y"] * facteur_vitesse
    bombe["vitesse_y"] += bombe["gravite"] * facteur_vitesse

def bouger_moitie(moitie, facteur_vitesse=1.0):
    moitie["x"] += moitie["vitesse_x"] * facteur_vitesse
    moitie["y"] += moitie["vitesse_y"] * facteur_vitesse
    moitie["vitesse_y"] += moitie["gravite"] * facteur_vitesse
    moitie["rotation"] += moitie["rotation_vitesse"] * facteur_vitesse
    moitie["timer"] -= 1

def souris_touche(objet, point):
    dx = objet["x"] - point[0]
    dy = objet["y"] - point[1]
    distance = (dx * dx + dy * dy) ** 0.5
    return distance < TAILLE_FRUIT

# -------------------------------------------
# DESSINER RESULTATS ARCADE
# -------------------------------------------
def dessiner_resultats_arcade(ecran, score_base, combos_stats):
    """Affiche la grille de score finale"""
    # Fond sombre
    overlay = pygame.Surface((LARGEUR, HAUTEUR))
    overlay.fill((20, 10, 30))
    overlay.set_alpha(240)
    ecran.blit(overlay, (0, 0))
    
    police_titre = pygame.font.Font(None, 80)
    police_texte = pygame.font.Font(None, 40)
    police_chiffre = pygame.font.Font(None, 50)
    
    # Titre
    titre = police_titre.render("TEMPS ÉCOULÉ !", True, (255, 200, 50))
    ecran.blit(titre, (LARGEUR // 2 - titre.get_width() // 2, 50))
    
    # Grille des combos
    y_start = 150
    x_col1 = 200
    x_col2 = 400
    x_col3 = 600
    
    # En-têtes
    ecran.blit(police_texte.render("Combo", True, (200, 200, 200)), (x_col1, y_start))
    ecran.blit(police_texte.render("Quantité", True, (200, 200, 200)), (x_col2, y_start))
    ecran.blit(police_texte.render("Points", True, (200, 200, 200)), (x_col3, y_start))
    
    total_bonus = 0
    ligne_h = 50
    
    # Lignes 3, 4, 5+ fruits
    types_combo = [
        (3, "3 Fruits", 5),   # +5 points bonus par occurrence
        (4, "4 Fruits", 10),  # +10 points bonus
        (5, "5+ Fruits", 20)  # +20 points bonus
    ]
    
    for i, (min_hits, label, points_bonus) in enumerate(types_combo):
        y = y_start + (i + 1) * ligne_h
        
        count = combos_stats.get(min_hits, 0)
        # Gestion du cas 5+ (qui regroupe tout ce qui est >= 5)
        if min_hits == 5:
             for k in combos_stats:
                if k > 5: count += combos_stats[k]
        
        score_ligne = count * points_bonus
        total_bonus += score_ligne
        
        # Affichage
        coul = (255, 255, 255)
        if count > 0: coul = (255, 255, 100) # Jaune si on en a fait
        
        ecran.blit(police_texte.render(label, True, coul), (x_col1, y))
        ecran.blit(police_chiffre.render(str(count), True, coul), (x_col2, y))
        ecran.blit(police_chiffre.render(f"+{score_ligne}", True, (100, 255, 100)), (x_col3, y))

    # Totaux
    y_total = 450
    pygame.draw.line(ecran, (255, 255, 255), (150, y_total - 20), (650, y_total - 20), 2)
    
    score_final = score_base + total_bonus
    
    lbl_base = police_texte.render(f"Score Base: {score_base}", True, (200, 200, 200))
    lbl_bonus = police_texte.render(f"Bonus Combos: +{total_bonus}", True, (100, 255, 100))
    
    lbl_final = police_titre.render(f"TOTAL: {score_final}", True, (255, 255, 255))
    
    ecran.blit(lbl_base, (LARGEUR // 2 - lbl_base.get_width() // 2, y_total))
    ecran.blit(lbl_bonus, (LARGEUR // 2 - lbl_bonus.get_width() // 2, y_total + 40))
    ecran.blit(lbl_final, (LARGEUR // 2 - lbl_final.get_width() // 2, y_total + 100))
    
    # Rejouer
    txt_rejouer = police_texte.render("Clique pour retourner au menu", True, (255, 230, 100))
    rect_rejouer = txt_rejouer.get_rect(center=(LARGEUR//2, HAUTEUR - 30))
    
    # Effet de clignotement simple
    if (pygame.time.get_ticks() // 500) % 2 == 0:
        ecran.blit(txt_rejouer, rect_rejouer)

# -------------------------------------------
# CALCULER DIFFICULTÉ (ARCADE)
# -------------------------------------------
def calculer_difficulte_arcade(temps_restant):
    # Mode 30 secondes : Tout est plus condensé !
    
    # Densité ajustée (Un peu moins hard que le 60s pour commencer)
    if temps_restant > 20: # 30-20s : Démarrage
        nb = random.randint(1, 3)
    elif temps_restant > 10: # 20-10s : Milieu
        nb = random.randint(2, 5)
    elif temps_restant > 5: # 10-5s : Intense
        nb = random.randint(4, 7)
    else: # Dernières 5 secondes = FRENZY
        nb = random.randint(6, 10)
        
    # Vitesse max et spawn très rapide
    return {
        "vitesse": VITESSE_MAX,
        "spawn_delay": max(SPAWN_MIN, SPAWN_INITIAL - (30 - temps_restant)), 
        "nb_fruits": nb
    }

# -------------------------------------------
# JOUER ARCADE
# -------------------------------------------
def jouer_arcade():
    """Lance le mode Arcade"""
    pygame.init()
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("🍉 Fruit Ninja - MODE ARCADE 🍉")
    horloge = pygame.time.Clock()
    images = charger_images()
    
    en_cours = True
    etat_jeu = "jeu" # "jeu", "resultats", "pause"
    
    fruits = []
    bombes = []
    moities = []
    bonus_textes = []
    points_souris = []
    souris_appuyee = False
    
    score = 0
    combo_stats = {} # {3: 0, 4: 0, 5: 0}
    
    temps_total = 30 # secondes (Pour présentation)
    temps_restant = temps_total
    start_ticks = pygame.time.get_ticks()
    
    timer_spawn = 0
    freeze_timer = 0
    last_freeze_time = -10000
    
    while en_cours:
        actuel = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
                return # Quitte tout
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if etat_jeu == "jeu":
                        etat_jeu = "pause"
                    elif etat_jeu == "pause":
                        etat_jeu = "jeu"
                
                if etat_jeu == "pause" and event.key == pygame.K_q:
                    en_cours = False # Retour menu
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                souris_appuyee = True
                points_souris = [event.pos]
                
                if etat_jeu == "resultats":
                    en_cours = False # Retour au menu principal (géré par fruitninja.py)
            
            if event.type == pygame.MOUSEBUTTONUP:
                souris_appuyee = False
                points_souris = []
                combo_count = 0
            
            if event.type == pygame.MOUSEMOTION:
                if souris_appuyee:
                    points_souris.append(event.pos)
                    if len(points_souris) > 10: points_souris.pop(0)

        # -------------------------------------------
        # UPDATE
        # -------------------------------------------
        if etat_jeu == "jeu":
            # Timer global
            # Si freeze, on ne décompte PAS le temps de jeu principal ou moins vite ?
            # Dans Fruit Ninja classique, Freeze arrête le timer.
            if freeze_timer > 0:
                # On "recule" le start_ticks pour que le temps n'avance pas
                start_ticks += 16 # ~1 frame ms
            
            elapsed = (actuel - start_ticks) / 1000
            temps_restant = max(0, temps_total - elapsed)
            
            if temps_restant <= 0:
                etat_jeu = "resultats"
                # Calcul final score + bonus
                total_bonus = 0
                 # Lignes 3, 4, 5+ fruits
                types_combo = [(3, 5), (4, 10), (5, 20)]
                for min_hits, pts in types_combo:
                    c = combo_stats.get(min_hits, 0)
                    if min_hits == 5:
                         for k in combo_stats:
                            if k > 5: c += combo_stats[k]
                    total_bonus += c * pts
                
                sauvegarder_score("arcade", score + total_bonus)
            
            # Difficulté
            diff = calculer_difficulte_arcade(temps_restant)
            
            # Freeze Logic
            facteur_vitesse = 1.0
            if freeze_timer > 0:
                freeze_timer -= 1
                facteur_vitesse = 0.2 # Très lent
                if freeze_timer % 60 == 0:
                     bonus_textes.append({"texte": "❄️", "x": LARGEUR/2, "y": HAUTEUR/3, "timer": 20})

            # Gestion Spawn
            timer_spawn += 1 * facteur_vitesse
            if timer_spawn >= diff["spawn_delay"]:
                timer_spawn = 0
                
                # Spawn Logic
                nb_a_lancer = diff["nb_fruits"]
                if len(fruits) + nb_a_lancer > FRUITS_MAX:
                    nb_a_lancer = max(0, FRUITS_MAX - len(fruits))
                
                for i in range(nb_a_lancer):
                    allow_freeze = (actuel - last_freeze_time > 10000)
                    nouv = creer_fruit(diff["vitesse"], 0.35, allow_freeze)
                    fruits.append(nouv)
                    if nouv["nom"] == "freeze":
                        last_freeze_time = actuel
                
                # Bombes (Mode Arcade = Plus de bombes pour piéger !)
                if random.random() < 0.4 and len(bombes) < 5:
                    bombes.append(creer_bombe(diff["vitesse"], 0.35))
            
            # Mouvements
            for f in fruits: bouger_fruit(f, facteur_vitesse)
            for b in bombes: bouger_bombe(b, facteur_vitesse)
            for m in moities: bouger_moitie(m, facteur_vitesse)
            
            # Collisions Souris
            if souris_appuyee and len(points_souris) > 0:
                # Fruits
                fruits_coupes_ce_tick = 0
                for f in fruits:
                    if not f["coupe"]:
                        for p in points_souris:
                            if souris_touche(f, p):
                                f["coupe"] = True
                                
                                # Combo Logic (Local à la frame ou "courte durée" ?)
                                # Pour simplifier en python: on compte les coupes continues
                                if 'combo_count' not in locals(): combo_count = 0
                                combo_count += 1
                                
                                pts = 1
                                txt = "+1"
                                
                                # Si c'est un combo
                                if combo_count >= 3:
                                    pts = combo_count
                                    txt = f"{combo_count}x!"
                                    
                                    # Enregistrer pour stat de fin
                                    # On enregistre SEULEMENT si c'est le "sommet" du combo ?
                                    # Simplification: on incrémente le bucket correspondant
                                    # Correction: Le combo se valide quand il s'arrête normalement.
                                    # Ici on va juste compter "raw" hits pour le score immédiat
                                    
                                    # Pour la grille de fin, on veut savoir combien de "Combos 3 fruits", "Combos 4 fruits"...
                                    # C'est complexe en temps réel. 
                                    # Approche simple: On stocke le MAX combo atteint dans une série de coupes
                                    pass

                                # Score immédiat
                                score += pts
                                
                                # Freeze
                                if f["nom"] == "freeze":
                                    freeze_timer = 300
                                    txt = "❄️ FREEZE ❄️"
                                
                                moities.append(creer_moitie(f, -1))
                                moities.append(creer_moitie(f, 1))
                                
                                bonus_textes.append({"texte": txt, "x": f["x"], "y": f["y"], "timer": 40})
                                
                                # Gestion stats combos (Approche simple accumulative)
                                # On incrémente le compteur correspondant au niveau actuel du combo
                                # ex: 3eme fruit -> hop une entrée dans "3 fruits"
                                # C'est pas EXACTEMENT Fruit Ninja (qui compte par "coup") mais ça marche
                                if combo_count >= 3:
                                     # On retire 1 au précédent pour "déplacer" le compte vers le haut
                                     # ex: j'avais un combo de 3, maintenant 4 -> -1 au "3", +1 au "4"
                                    if combo_count > 3:
                                        prev = combo_count - 1
                                        if prev in combo_stats and combo_stats[prev] > 0:
                                            combo_stats[prev] -= 1
                                    
                                    if combo_count not in combo_stats: combo_stats[combo_count] = 0
                                    combo_stats[combo_count] += 1
                                
                                break

                # Bombes
                for b in bombes:
                    for p in points_souris:
                        if souris_touche(b, p):
                            # PAS DE GAME OVER !
                            # Juste pénalité -10
                            score -= 10
                            score = max(0, score) # Pas de score négatif
                            
                            bonus_textes.append({
                                "texte": "-10 BOMB!", 
                                "x": b["x"], 
                                "y": b["y"], 
                                "timer": 60
                            })
                            
                            # On enlève la bombe (elle explose)
                            b["y"] = HAUTEUR + 200 # Hack pour la supprimer au clean
                            
                            # Effet visuel blanc (flash)
                            ecran.fill((255, 255, 255))
                            pygame.display.flip()
                            pygame.time.delay(50) 
            
            # Nettoyage
            fruits = [f for f in fruits if f["y"] < HAUTEUR + 100 or f["coupe"] == False] 
            # Note: Bug ci-dessus, on veut garder ceux qui sont PAS coupé (et pas trop bas) 
            # OU ceux qui viennent d'être coupés (mais ils sont gérés par is_coupe=True, on les vire ?)
            # Correction: Si coupé, on le vire (car transformé en moitiés)
            
            nouveaux = []
            for f in fruits:
                if f["coupe"]: continue
                if f["y"] < HAUTEUR + 150: nouveaux.append(f)
            fruits = nouveaux
            
            bombes = [b for b in bombes if b["y"] < HAUTEUR + 150]
            moities = [m for m in moities if m["timer"] > 0]
            
            for b in bonus_textes:
                b["y"] -= 1
                b["timer"] -= 1
            bonus_textes = [b for b in bonus_textes if b["timer"] > 0]
        
        # -------------------------------------------
        # DESSIN
        # -------------------------------------------
        dessiner_fond(ecran, LARGEUR, HAUTEUR)
        
        if etat_jeu == "jeu":
            for m in moities: dessiner_fruit_coupe(ecran, images, m)
            for f in fruits: 
                 if not f["coupe"]: dessiner_fruit(ecran, images, f)
            for b in bombes: dessiner_bombe(ecran, images, b)
            dessiner_lame(ecran, points_souris)
            
            # Score en haut à gauche
            font = pygame.font.Font(None, 60)
            img_score = font.render(str(score), True, (255, 255, 255))
            ecran.blit(img_score, (20, 20))
            
            # Timer en haut à droite
            coul_t = (255, 255, 100)
            if temps_restant < 10: coul_t = (255, 50, 50)
            img_timer = font.render(f"{int(temps_restant)}", True, coul_t)
            ecran.blit(img_timer, (LARGEUR - 80, 20))
            
            dessiner_bonus(ecran, bonus_textes)
            
        elif etat_jeu == "resultats":
            dessiner_resultats_arcade(ecran, score, combo_stats)
            
        elif etat_jeu == "pause":
            dessiner_fond(ecran, LARGEUR, HAUTEUR)
            dessiner_pause(ecran, LARGEUR, HAUTEUR)
        
        pygame.display.flip()
        horloge.tick(60)
