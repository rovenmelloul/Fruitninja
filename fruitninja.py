# ============================================
# FRUITNINJA.py - Logique du jeu
# ============================================
# Ce fichier gère toute la logique du jeu
# Code simple sans classes, lisible par un enfant !
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
    dessiner_menu,
    dessiner_game_over,
    dessiner_bonus,
    dessiner_fruit_coupe,
    dessiner_pause
)
from fruitninja_arcade import jouer_arcade
from score_manager import charger_scores, sauvegarder_score

# -------------------------------------------
# PARAMÈTRES DU JEU
# -------------------------------------------
LARGEUR = 800
HAUTEUR = 600
TAILLE_FRUIT = 40  # Pour la collision

# Paramètres de physique FRUIT NINJA - COMBOS & HAUTEUR
# Les fruits montent plus haut pour permettre des combos
VITESSE_INITIALE = 10.5   # Vitesse PLUS ZEN
VITESSE_MAX = 12.5        # Vitesse max raisonnable
GRAVITE_INITIALE = 0.32   # Gravité légère
GRAVITE_MAX = 0.45        # Gravité max contrôlée
SPAWN_INITIAL = 80        # Spawns plus fréquents
SPAWN_MIN = 30            # Cap minimum
FRUITS_MAX = 15           # Beaucoup de fruits pour le chaos !

# -------------------------------------------
# CRÉER UN FRUIT
# -------------------------------------------
def creer_fruit(vitesse, gravite, allow_freeze=True):
    """Crée un nouveau fruit avec trajectoire réaliste style Fruit Ninja"""
    noms_fruits = ["pasteque", "orange", "pomme", "banane", "kiwi"]
    
    # 3% de chance de spawn un fruit FREEZE (Ajusté selon feedback)
    # MAIS SEULEMENT SI AUTORISÉ (Cooldown)
    nom_fruit = random.choice(noms_fruits)
    if allow_freeze and random.random() < 0.03:
        nom_fruit = "freeze"
    
    # Position de départ VARIÉE (toute la largeur)
    x = random.randint(50, LARGEUR - 50)
    
    # Vitesse horizontale INTELLIGENTE
    # Si à gauche -> va vers la droite
    # Si à droite -> va vers la gauche
    # Si au centre -> aléatoire
    if x < LARGEUR // 3:
        vitesse_x = random.uniform(2, 5)
    elif x > LARGEUR * 2 // 3:
        vitesse_x = random.uniform(-5, -2)
    else:
        vitesse_x = random.uniform(-2, 2)
    
    fruit = {
        "nom": nom_fruit,
        "x": x,
        "y": HAUTEUR + 50,
        "vitesse_x": vitesse_x,
        "vitesse_y": -vitesse - random.uniform(0, 3),  # Variation de hauteur
        "gravite": gravite,
        "rotation": 0,
        "rotation_vitesse": random.uniform(-5, 5),  # Rotation
        "coupe": False
    }
    return fruit


# -------------------------------------------
# CRÉER UNE BOMBE
# -------------------------------------------
def creer_bombe(vitesse, gravite):
    """Crée une bombe (à éviter !)"""
    bombe = {
        "x": random.randint(100, LARGEUR - 100),
        "y": HAUTEUR + 50,
        "vitesse_x": random.uniform(-1.5, 1.5),
        "vitesse_y": -vitesse - random.uniform(0, 2),
        "gravite": gravite
    }
    return bombe


# -------------------------------------------
# CRÉER UNE MOITIÉ DE FRUIT COUPÉ
# -------------------------------------------
def creer_moitie(fruit, direction):
    """Crée une moitié de fruit qui tombe"""
    moitie = {
        "nom": fruit["nom"],
        "x": fruit["x"],
        "y": fruit["y"],
        "vitesse_x": direction * 3,
        "vitesse_y": -2,
        "gravite": 0.3,
        "rotation": 0,
        "rotation_vitesse": direction * 10,
        "timer": 60  # Disparaît après 1 seconde
    }
    return moitie


# -------------------------------------------
# BOUGER UN FRUIT
# -------------------------------------------
def bouger_fruit(fruit, facteur_vitesse=1.0):
    """Met à jour la position du fruit"""
    fruit["x"] += fruit["vitesse_x"] * facteur_vitesse
    fruit["y"] += fruit["vitesse_y"] * facteur_vitesse
    fruit["vitesse_y"] += fruit["gravite"] * facteur_vitesse
    fruit["rotation"] += fruit["rotation_vitesse"] * facteur_vitesse


# -------------------------------------------
# BOUGER UNE BOMBE
# -------------------------------------------
def bouger_bombe(bombe, facteur_vitesse=1.0):
    """Met à jour la position de la bombe"""
    bombe["x"] += bombe["vitesse_x"] * facteur_vitesse
    bombe["y"] += bombe["vitesse_y"] * facteur_vitesse
    bombe["vitesse_y"] += bombe["gravite"] * facteur_vitesse


# -------------------------------------------
# BOUGER UNE MOITIÉ DE FRUIT
# -------------------------------------------
def bouger_moitie(moitie, facteur_vitesse=1.0):
    """Met à jour la moitié de fruit coupé"""
    moitie["x"] += moitie["vitesse_x"] * facteur_vitesse
    moitie["y"] += moitie["vitesse_y"] * facteur_vitesse
    moitie["vitesse_y"] += moitie["gravite"] * facteur_vitesse
    moitie["rotation"] += moitie["rotation_vitesse"] * facteur_vitesse
    moitie["timer"] -= 1


# -------------------------------------------
# VÉRIFIER SI LA SOURIS TOUCHE UN OBJET
# -------------------------------------------
def souris_touche(objet, point):
    """Vérifie si le point touche l'objet"""
    dx = objet["x"] - point[0]
    dy = objet["y"] - point[1]
    distance = (dx * dx + dy * dy) ** 0.5
    return distance < TAILLE_FRUIT


# -------------------------------------------
# CALCULER LE NIVEAU ET LA DIFFICULTÉ
# -------------------------------------------
def calculer_difficulte(temps_jeu):
    """
    Augmente la difficulté en fonction du TEMPS de jeu (en secondes)
    """
    # Vitesse : Augmente très très légèrement avec le temps
    vitesse = VITESSE_MAX
    
    # Gravité stable
    gravite = GRAVITE_INITIALE
    
    # Temps entre les spawns (diminue avec le temps)
    # Démarre lent (80 ticks) -> finit rapide (30 ticks)
    spawn_delay = SPAWN_INITIAL - (temps_jeu // 2) 
    spawn_delay = max(spawn_delay, SPAWN_MIN)
    
    # DENSITÉ : Basée sur des phases de temps
    if temps_jeu < 15:          # 0-15s : Échauffement
        nb_fruits = random.randint(1, 2)
    elif temps_jeu < 45:        # 15-45s : Montée en puissance
        nb_fruits = random.randint(2, 4)
    elif temps_jeu < 90:        # 45-90s : Intense
        nb_fruits = random.randint(3, 6)
    else:                       # 90s+ : Chaos contrôlé
        nb_fruits = random.randint(4, 8) 
    
    return {
        "niveau": int(temps_jeu // 10),
        "vitesse": vitesse,
        "gravite": gravite,
        "spawn_delay": spawn_delay,
        "nb_fruits": nb_fruits
    }


# -------------------------------------------
# BOUCLE PRINCIPALE DU JEU
# -------------------------------------------
def jouer():
    """Lance le jeu Fruit Ninja !"""
    
    # Initialiser Pygame
    pygame.init()
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("🍉 Fruit Ninja - Édition Enfants")
    horloge = pygame.time.Clock()
    
    # Charger les images
    images = charger_images()
    
    # État du jeu
    en_cours = True
    etat = "menu"  # menu, jeu, game_over, pause
    scores_actuels = charger_scores()

    
    # Listes des objets
    fruits = []
    bombes = []
    moities = []
    bonus_textes = []
    
    # Points de la souris (pour la lame)
    points_souris = []
    souris_appuyee = False
    
    # Score et vies
    score = 0
    vies = 3
    
    # Timer pour le spawn
    timer_spawn = 0
    freeze_timer = 0 # Timer pour l'effet de gel
    last_freeze_time = -10000 # Pour gérer le cooldown de spawn (10s)
    vague_count = 0  # Compteur global de vagues
    
    # -------------------------------------------
    # BOUCLE PRINCIPALE
    # -------------------------------------------
    while en_cours:
        
        # Événements
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                en_cours = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if etat == "jeu":
                        etat = "pause"
                    elif etat == "pause":
                        etat = "jeu"
                
                if etat == "pause" and event.key == pygame.K_q:
                    etat = "menu"
                    scores_actuels = charger_scores() # Update scores

                if etat == "menu" and event.key == pygame.K_a:
                    # Lancer le mode Arcade !
                    jouer_arcade()
                    scores_actuels = charger_scores() # Reload scores au retour
                    pygame.display.set_mode((LARGEUR, HAUTEUR)) 
                    etat = "menu"

            
            if event.type == pygame.MOUSEBUTTONDOWN:
                souris_appuyee = True
                points_souris = [event.pos]
                
                if etat == "menu":
                    mx, my = event.pos
                    
                    # Zone CLASSIQUE (50, 150, 300, 300)
                    if 50 <= mx <= 350 and 150 <= my <= 450:
                        etat = "jeu"
                        score = 0
                        vies = 3
                        fruits = []
                        bombes = []
                        moities = []
                        bonus_textes = []
                        vague_count = 0 
                        combo_count = 0
                        freeze_timer = 0
                        last_freeze_time = -10000
                        temps_debut = pygame.time.get_ticks()
                    
                    # Zone ARCADE (LARGEUR - 350, 150, 300, 300) -> (450, 150, 300, 300)
                    elif 450 <= mx <= 750 and 150 <= my <= 450:
                        jouer_arcade()
                        scores_actuels = charger_scores()
                        pygame.display.set_mode((LARGEUR, HAUTEUR))
                        etat = "menu"
                
                elif etat == "game_over":
                    etat = "menu"
            
            if event.type == pygame.MOUSEBUTTONUP:
                souris_appuyee = False
                points_souris = []
                combo_count = 0  # Fin du combo
            
            if event.type == pygame.MOUSEMOTION:
                if souris_appuyee:
                    points_souris.append(event.pos)
                    if len(points_souris) > 10:
                        points_souris.pop(0)
        
        # -------------------------------------------
        # LOGIQUE DU JEU
        # -------------------------------------------
        if etat == "jeu":
            
            # Calculer la difficulté actuelle basée sur le TEMPS
            temps_actuel = (pygame.time.get_ticks() - temps_debut) / 1000
            diff = calculer_difficulte(temps_actuel)
            niveau = diff["niveau"]
            vitesse = diff["vitesse"]
            gravite = diff["gravite"]
            spawn_delay = diff["spawn_delay"]
            nb_fruits = diff["nb_fruits"]
            
            # Spawn des fruits
            
            # Gérer le Freeze
            facteur_vitesse = 1.0
            if freeze_timer > 0:
                freeze_timer -= 1
                facteur_vitesse = 0.3 # RALENTI LE TEMPS
                
                 # Feedback visuel (simple overlay bleuâtre simulé par du texte pour l'instant)
                if freeze_timer % 60 == 0: # Chaque seconde
                     bonus_textes.append({
                        "texte": "❄️ FREEZE! ❄️",
                        "x": LARGEUR // 2,
                        "y": HAUTEUR // 4,
                        "timer": 30
                    })
            
            timer_spawn += 1 * facteur_vitesse # Le spawn ralentit aussi !
            if timer_spawn >= spawn_delay:
                timer_spawn = 0
                
                # LOGIQUE DE VAGUES (PROGRESION DOUCE)
                # Les 3 premiers lancers sont calmes (1 ou 2 fruits)
                fruits_actuels = len(fruits)
                
                # Incrémenter les vagues
                if 'vague_count' not in locals():
                     vague_count = 0
                vague_count += 1
                
                # LOGIQUE DE VAGUES
                # On utilise directement le nombre calculé par le temps
                fruits_actuels = len(fruits)
                nb_a_lancer = nb_fruits # La base vient du temps maintenant
                
                # Petite part d'aléatoire pour pas être robotique
                if random.random() < 0.3:
                     nb_a_lancer += random.randint(-1, 1)
                     nb_a_lancer = max(1, nb_a_lancer) # Au moins 1 fruit
                
                 # Limite STRICTE pour éviter les lags et l'illisible
                if fruits_actuels + nb_a_lancer > 12: # Max 12 fruits à l'écran simultanés
                     nb_a_lancer = max(0, 12 - fruits_actuels)
                
                # Ajouter des fruits
                if fruits_actuels < FRUITS_MAX:
                    for i in range(nb_a_lancer):
                        # Gestion du cooldown de spawn
                        # Ne peut pas apparaître dans les 10s après le précédent
                        temps_actuel_ms = pygame.time.get_ticks()
                        allow_freeze = (temps_actuel_ms - last_freeze_time > 10000)
                        
                        nouveau_fruit = creer_fruit(vitesse, gravite, allow_freeze)
                        fruits.append(nouveau_fruit)
                        
                        # Si c'était un freeze, on enregistre le temps
                        if nouveau_fruit["nom"] == "freeze":
                            last_freeze_time = temps_actuel_ms
                            allow_freeze = False # Un seul par vague max
                
                # Bombe (toujours possible, 1 chance sur 3, pour pimenter)
                if random.randint(1, 3) == 1 and len(bombes) < 3:
                     bombes.append(creer_bombe(vitesse, gravite))
            
            # Bouger les fruits
            for fruit in fruits:
                bouger_fruit(fruit, facteur_vitesse)
            
            # Bouger les bombes
            for bombe in bombes:
                bouger_bombe(bombe, facteur_vitesse)
            
            # Bouger les moitiés
            for moitie in moities:
                bouger_moitie(moitie, facteur_vitesse)
            
            # Vérifier les collisions avec la souris
            if souris_appuyee and len(points_souris) > 0:
                
                # Fruits
                for fruit in fruits:
                    if not fruit["coupe"]:
                        for point in points_souris:
                            if souris_touche(fruit, point):
                                fruit["coupe"] = True
                                
                                # GESTION DU COMBO
                                if 'combo_count' not in locals(): combo_count = 0
                                combo_count += 1
                                
                                points_gagnes = 10
                                texte_bonus = "+10"
                                
                                # Bonus de combo (à partir de 3 fruits)
                                if combo_count >= 3:
                                    points_gagnes = 10 * combo_count  # Multiplicateur !
                                    texte_bonus = f"{combo_count}x COMBO! (+{points_gagnes})"
                                
                                score += points_gagnes
                                
                                # EFFET FREEZE
                                if fruit["nom"] == "freeze":
                                    freeze_timer = 300 # 5 Secondes de freeze (60 FPS * 5)
                                    texte_bonus = "❄️ FREEZE! ❄️"
                                    
                                    # Tout ralentir immédiatement
                                    for f in fruits: f["vitesse_x"] *= 0.5; f["vitesse_y"] *= 0.5
                                    for b in bombes: b["vitesse_x"] *= 0.5; b["vitesse_y"] *= 0.5
                                
                                # Créer les moitiés
                                moities.append(creer_moitie(fruit, -1))
                                moities.append(creer_moitie(fruit, 1))
                                
                                # Bonus visuel
                                bonus_textes.append({
                                    "texte": texte_bonus,
                                    "x": fruit["x"],
                                    "y": fruit["y"],
                                    "timer": 50
                                })
                                break
                
                # Bombes
                for bombe in bombes:
                    for point in points_souris:
                        if souris_touche(bombe, point):
                            etat = "game_over"
            
            # Supprimer les fruits coupés ou tombés
            nouveaux_fruits = []
            for fruit in fruits:
                if fruit["coupe"]:
                    continue
                if fruit["y"] > HAUTEUR + 100:
                    # Fruit raté = perte de vie
                    vies -= 1
                    if vies <= 0:
                        etat = "game_over"
                        sauvegarder_score("classique", score)
                    continue
                nouveaux_fruits.append(fruit)
            fruits = nouveaux_fruits
            
            # Supprimer les bombes tombées
            bombes = [b for b in bombes if b["y"] < HAUTEUR + 100]
            
            # Supprimer les moitiés expirées
            moities = [m for m in moities if m["timer"] > 0]
            
            # Mettre à jour les bonus
            for bonus in bonus_textes:
                bonus["y"] -= 2
                bonus["timer"] -= 1
            bonus_textes = [b for b in bonus_textes if b["timer"] > 0]
        
        # -------------------------------------------
        # AFFICHAGE
        # -------------------------------------------
        if etat == "menu":
            dessiner_menu(ecran, LARGEUR, HAUTEUR, scores_actuels)
        
        elif etat == "jeu":
            dessiner_fond(ecran, LARGEUR, HAUTEUR)
            
            # Dessiner les moitiés de fruits (en arrière)
            for moitie in moities:
                dessiner_fruit_coupe(ecran, images, moitie)
            
            # Dessiner les fruits
            for fruit in fruits:
                if not fruit["coupe"]:
                    dessiner_fruit(ecran, images, fruit)
            
            # Dessiner les bombes
            for bombe in bombes:
                dessiner_bombe(ecran, images, bombe)
            
            # Dessiner la lame
            dessiner_lame(ecran, points_souris)
            
            # Dessiner le score et les vies
            # Dessiner le score et les vies
            dessiner_score(ecran, score, vies)
            
            # Dessiner les bonus
            dessiner_bonus(ecran, bonus_textes)
        
        elif etat == "game_over":
            dessiner_fond(ecran, LARGEUR, HAUTEUR)
            dessiner_game_over(ecran, LARGEUR, HAUTEUR, score)
            
        elif etat == "pause":
            dessiner_fond(ecran, LARGEUR, HAUTEUR)
            # On pourrait dessiner les fruits figés ici si on voulait
            dessiner_pause(ecran, LARGEUR, HAUTEUR)

        
        # Mettre à jour l'écran
        pygame.display.flip()
        horloge.tick(60)
    
    pygame.quit()


# -------------------------------------------
# LANCER LE JEU !
# -------------------------------------------
if __name__ == "__main__":
    jouer()
