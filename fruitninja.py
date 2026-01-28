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
    dessiner_fruit_coupe
)

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
def creer_fruit(vitesse, gravite):
    """Crée un nouveau fruit avec trajectoire réaliste style Fruit Ninja"""
    noms_fruits = ["pasteque", "orange", "pomme", "banane", "kiwi"]
    
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
        "nom": random.choice(noms_fruits),
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
def bouger_fruit(fruit):
    """Met à jour la position du fruit"""
    fruit["x"] += fruit["vitesse_x"]
    fruit["y"] += fruit["vitesse_y"]
    fruit["vitesse_y"] += fruit["gravite"]
    fruit["rotation"] += fruit["rotation_vitesse"]


# -------------------------------------------
# BOUGER UNE BOMBE
# -------------------------------------------
def bouger_bombe(bombe):
    """Met à jour la position de la bombe"""
    bombe["x"] += bombe["vitesse_x"]
    bombe["y"] += bombe["vitesse_y"]
    bombe["vitesse_y"] += bombe["gravite"]


# -------------------------------------------
# BOUGER UNE MOITIÉ DE FRUIT
# -------------------------------------------
def bouger_moitie(moitie):
    """Met à jour la moitié de fruit coupé"""
    moitie["x"] += moitie["vitesse_x"]
    moitie["y"] += moitie["vitesse_y"]
    moitie["vitesse_y"] += moitie["gravite"]
    moitie["rotation"] += moitie["rotation_vitesse"]
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
def calculer_difficulte(score):
    """
    Augmente la difficulté en fonction du score
    ADAPTÉ AUX ENFANTS : progression très douce
    """
    # Niveau = score / 150 (progression BEAUCOUP plus lente)
    # 6 sec de jeu = ~60 pts = Niveau 1 (et pas Niveau 2 ou 3)
    niveau = 1 + score // 150
    
    # Limiter le niveau max à 20
    niveau = min(niveau, 20)
    
    # Vitesse STABLE (optimisée pour le fun et les combos)
    # On ne l'augmente presque plus, c'est la quantité de fruits qui compte
    vitesse = VITESSE_MAX
    
    # Gravité stable
    gravite = GRAVITE_INITIALE
    
    # Temps entre les spawns diminue
    spawn_delay = SPAWN_INITIAL - (niveau - 1) * 3
    spawn_delay = max(spawn_delay, SPAWN_MIN)
    
    # DENSITÉ : Augmente très progressivement
    if niveau < 4:      # Jusqu'à ~600 pts (longtemps)
        nb_fruits = 2   # Calme
    elif niveau < 8:    # ~1200 pts
        nb_fruits = 4   # Moyen
    elif niveau < 14:   # ~2100 pts
        nb_fruits = 6   # Intense
    else:
        nb_fruits = 8   # Chaos (fin de partie)
    
    return {
        "niveau": niveau,
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
    etat = "menu"  # menu, jeu, game_over
    
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
    vague_count = 0  # Compteur global de vagues
    
    # -------------------------------------------
    # BOUCLE PRINCIPALE
    # -------------------------------------------
    while en_cours:
        
        # Événements
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                en_cours = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                souris_appuyee = True
                points_souris = [event.pos]
                
                if etat == "menu":
                    etat = "jeu"
                    score = 0
                    vies = 3
                    fruits = []
                    bombes = []
                    moities = []
                    bonus_textes = []
                    vague_count = 0  # Réinitialiser le compteur de vagues
                    combo_count = 0  # Reset combo
                
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
            
            # Calculer la difficulté actuelle
            diff = calculer_difficulte(score)
            niveau = diff["niveau"]
            vitesse = diff["vitesse"]
            gravite = diff["gravite"]
            spawn_delay = diff["spawn_delay"]
            nb_fruits = diff["nb_fruits"]
            
            # Spawn des fruits
            timer_spawn += 1
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
                # Les 3 premiers lancers sont calmes (1 ou 2 fruits)
                fruits_actuels = len(fruits)
                nb_a_lancer = 1
                
                if vague_count <= 3:
                    nb_a_lancer = random.randint(1, 2)
                else:
                    # Ensuite : MODE COMBO (60% chance)
                    if random.random() < 0.6:  
                         nb_a_lancer = random.randint(3, 5)
                    else:
                         nb_a_lancer = random.randint(1, nb_fruits)
                
                # Ajouter des fruits
                if fruits_actuels < FRUITS_MAX:
                    for i in range(nb_a_lancer):
                        fruits.append(creer_fruit(vitesse, gravite))
                
                # Bombe (toujours possible, 1 chance sur 3, pour pimenter)
                if random.randint(1, 3) == 1 and len(bombes) < 3:
                     bombes.append(creer_bombe(vitesse, gravite))
            
            # Bouger les fruits
            for fruit in fruits:
                bouger_fruit(fruit)
            
            # Bouger les bombes
            for bombe in bombes:
                bouger_bombe(bombe)
            
            # Bouger les moitiés
            for moitie in moities:
                bouger_moitie(moitie)
            
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
            dessiner_menu(ecran, LARGEUR, HAUTEUR)
        
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
            diff = calculer_difficulte(score)
            dessiner_score(ecran, score, vies)
            
            # Dessiner les bonus
            dessiner_bonus(ecran, bonus_textes)
        
        elif etat == "game_over":
            dessiner_fond(ecran, LARGEUR, HAUTEUR)
            dessiner_game_over(ecran, LARGEUR, HAUTEUR, score)
        
        # Mettre à jour l'écran
        pygame.display.flip()
        horloge.tick(60)
    
    pygame.quit()


# -------------------------------------------
# LANCER LE JEU !
# -------------------------------------------
if __name__ == "__main__":
    jouer()
