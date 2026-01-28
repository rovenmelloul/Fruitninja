# ============================================
# GUI.py - Interface graphique Pygame
# ============================================
# Ce fichier gère TOUT l'affichage du jeu
# ============================================

import pygame
import os

# -------------------------------------------
# CHARGER LES IMAGES DES FRUITS
# -------------------------------------------
def charger_images():
    """Charge toutes les images du dossier images/"""
    dossier = os.path.dirname(__file__)
    images_dossier = os.path.join(dossier, "images")
    
    images = {}
    
    # Liste des fruits à charger
    noms = ["pasteque", "orange", "pomme", "banane", "kiwi", "bombe"]
    
    for nom in noms:
        chemin = os.path.join(images_dossier, f"{nom}.png")
        if os.path.exists(chemin):
            image = pygame.image.load(chemin).convert_alpha()
            # Redimensionner à 80x80 pixels
            images[nom] = pygame.transform.scale(image, (80, 80))
    
    return images


# -------------------------------------------
# DESSINER LE FOND
# -------------------------------------------
def dessiner_fond(ecran, largeur, hauteur):
    """Dessine un fond dégradé bleu nuit"""
    for y in range(hauteur):
        # Dégradé du bleu foncé vers le bleu-violet
        bleu = int(20 + (y / hauteur) * 60)
        vert = int(20 + (y / hauteur) * 40)
        rouge = int(30 + (y / hauteur) * 50)
        pygame.draw.line(ecran, (rouge, vert, bleu), (0, y), (largeur, y))


# -------------------------------------------
# DESSINER UN FRUIT
# -------------------------------------------
def dessiner_fruit(ecran, images, fruit):
    """Dessine un fruit à sa position"""
    nom = fruit["nom"]
    x = int(fruit["x"])
    y = int(fruit["y"])
    
    if nom in images:
        image = images[nom]
        # Rotation du fruit
        angle = fruit.get("rotation", 0)
        image_tournee = pygame.transform.rotate(image, angle)
        rect = image_tournee.get_rect(center=(x, y))
        ecran.blit(image_tournee, rect)


# -------------------------------------------
# DESSINER UNE BOMBE
# -------------------------------------------
def dessiner_bombe(ecran, images, bombe):
    """Dessine une bombe à sa position"""
    x = int(bombe["x"])
    y = int(bombe["y"])
    
    if "bombe" in images:
        image = images["bombe"]
        rect = image.get_rect(center=(x, y))
        ecran.blit(image, rect)


# -------------------------------------------
# DESSINER LA LAME (SLICE)
# -------------------------------------------
def dessiner_lame(ecran, points):
    """Dessine la traînée de la lame blanche"""
    if len(points) < 2:
        return
    
    for i in range(1, len(points)):
        debut = points[i - 1]
        fin = points[i]
        
        # Épaisseur qui augmente vers la fin
        epaisseur = 2 + i * 2
        
        # Ligne blanche brillante
        pygame.draw.line(ecran, (255, 255, 255), debut, fin, epaisseur)
        # Ligne centrale bleue claire
        if epaisseur > 4:
            pygame.draw.line(ecran, (200, 220, 255), debut, fin, epaisseur // 2)


# -------------------------------------------
# DESSINER LE SCORE ET LES VIES
# -------------------------------------------
def dessiner_score(ecran, score, vies):
    """Affiche le score et les vies (sans niveau visible)"""
    police = pygame.font.Font(None, 50)
    
    # Score en haut à gauche
    texte_score = police.render(f"Score: {score}", True, (255, 255, 255))
    ecran.blit(texte_score, (20, 20))
    
    # Vies sous le score
    coeurs = "♥ " * vies
    texte_vies = police.render(f"Vies: {coeurs}", True, (255, 100, 100))
    ecran.blit(texte_vies, (20, 70))


# -------------------------------------------
# DESSINER LE MENU
# -------------------------------------------
def dessiner_menu(ecran, largeur, hauteur):
    """Dessine le menu principal"""
    # Fond sombre
    ecran.fill((40, 30, 50))
    
    # Titre
    grande_police = pygame.font.Font(None, 90)
    titre = grande_police.render("FRUIT NINJA", True, (255, 100, 50))
    ombre = grande_police.render("FRUIT NINJA", True, (100, 40, 20))
    ecran.blit(ombre, (largeur // 2 - ombre.get_width() // 2 + 4, 124))
    ecran.blit(titre, (largeur // 2 - titre.get_width() // 2, 120))
    
    # Sous-titre
    police = pygame.font.Font(None, 45)
    sous_titre = police.render("Clique pour jouer !", True, (255, 230, 100))
    ecran.blit(sous_titre, (largeur // 2 - sous_titre.get_width() // 2, 250))
    
    # Instructions
    petite_police = pygame.font.Font(None, 35)
    instructions = [
        "Glisse la souris pour couper les fruits",
        "Évite les bombes !",
        "Le jeu accélère petit à petit...",
        "Jeu adapté pour les enfants"
    ]
    
    y = 350
    for texte in instructions:
        surface = petite_police.render(texte, True, (200, 200, 200))
        ecran.blit(surface, (largeur // 2 - surface.get_width() // 2, y))
        y += 45


# -------------------------------------------
# DESSINER GAME OVER
# -------------------------------------------
def dessiner_game_over(ecran, largeur, hauteur, score):
    """Dessine l'écran de fin de partie"""
    # Fond sombre semi-transparent
    overlay = pygame.Surface((largeur, hauteur))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(200)
    ecran.blit(overlay, (0, 0))
    
    # GAME OVER
    grande_police = pygame.font.Font(None, 90)
    texte = grande_police.render("GAME OVER", True, (255, 80, 80))
    ecran.blit(texte, (largeur // 2 - texte.get_width() // 2, 180))
    
    # Score final
    police = pygame.font.Font(None, 60)
    score_final = police.render(f"Score Final: {score}", True, (255, 255, 255))
    ecran.blit(score_final, (largeur // 2 - score_final.get_width() // 2, 300))
    
    # Rejouer
    petite_police = pygame.font.Font(None, 45)
    rejouer = petite_police.render("Clique pour rejouer", True, (255, 230, 100))
    ecran.blit(rejouer, (largeur // 2 - rejouer.get_width() // 2, 420))


# -------------------------------------------
# DESSINER LES POINTS BONUS
# -------------------------------------------
def dessiner_bonus(ecran, bonus_liste):
    """Affiche les textes de bonus flottants"""
    police = pygame.font.Font(None, 45)
    
    for bonus in bonus_liste:
        texte = bonus["texte"]
        x = int(bonus["x"])
        y = int(bonus["y"])
        
        # Couleur jaune/orange
        surface = police.render(texte, True, (255, 230, 100))
        ecran.blit(surface, (x - surface.get_width() // 2, y))


# -------------------------------------------
# DESSINER LES MOITIÉS DE FRUITS COUPÉS
# -------------------------------------------
def dessiner_fruit_coupe(ecran, images, moitie):
    """Dessine une moitié de fruit qui tombe"""
    nom = moitie["nom"]
    x = int(moitie["x"])
    y = int(moitie["y"])
    
    if nom in images:
        image = images[nom]
        # Réduire la taille pour la moitié
        petite = pygame.transform.scale(image, (50, 50))
        # Rotation
        angle = moitie.get("rotation", 0)
        tournee = pygame.transform.rotate(petite, angle)
        rect = tournee.get_rect(center=(x, y))
        ecran.blit(tournee, rect)
