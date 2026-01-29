import pygame
import os

# CHARGER LES IMAGES DES FRUITS

def charger_images():
    images = {}

    #Background néon
    images["bg"] = pygame.image.load("images/backgrounds/bg_neon_grid_v1.png").convert()

    #Spritesheet néon (pack fruits)
    images["sheet"] = pygame.image.load("images/spritesheets/neon_pack_v1.png").convert_alpha()

    # Pour l’animation de fond (scroll)
    images["bg_scroll"] = 0

    return images

    for nom in noms:
        chemin = os.path.join(images_dossier, f"{nom}.png")
        if os.path.exists(chemin):
            image = pygame.image.load(chemin).convert_alpha()
            # Redimensionner à 80x80 pixels
            images[nom] = pygame.transform.scale(image, (80, 80))
    
    return images

def dessiner_fond(ecran, largeur, hauteur, images=None):
    # Si le jeu n’envoie pas "images", on fait un fallback simple
    if images is None or "bg" not in images:
        ecran.fill((10, 8, 25))
        return

    bg = images["bg"]
    bg_scaled = pygame.transform.smoothscale(bg, (largeur, hauteur))

    # Scroll vertical léger (illusion arcade)
    images["bg_scroll"] = (images["bg_scroll"] + 1) % hauteur
    y = images["bg_scroll"]

    ecran.blit(bg_scaled, (0, -y))
    ecran.blit(bg_scaled, (0, hauteur - y))


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
def dessiner_menu(ecran, largeur, hauteur, scores={"classique": 0, "arcade": 0}):
    """Dessine le menu principal avec 2 modes"""
    # Fond sombre
    ecran.fill((40, 30, 50))
    
    # Titre
    grande_police = pygame.font.Font(None, 90)
    titre = grande_police.render("FRUIT NINJA", True, (255, 100, 50))
    ecran.blit(titre, (largeur // 2 - titre.get_width() // 2, 50))
    
    # ZONE CLASSIQUE (Gauche)
    rect_classique = pygame.Rect(50, 150, 300, 300)
    pygame.draw.rect(ecran, (50, 100, 50), rect_classique, border_radius=20)
    pygame.draw.rect(ecran, (100, 200, 100), rect_classique, 3, border_radius=20)
    
    font_mode = pygame.font.Font(None, 60)
    txt_classique = font_mode.render("CLASSIQUE", True, (150, 255, 150))
    ecran.blit(txt_classique, (rect_classique.centerx - txt_classique.get_width()//2, rect_classique.centery - 60))
    
    # Score Classique
    score_c = scores.get('classique', 0)
    font_record = pygame.font.Font(None, 35)
    txt_rec_label = font_record.render("RECORD", True, (200, 200, 100))
    ecran.blit(txt_rec_label, (rect_classique.centerx - txt_rec_label.get_width()//2, rect_classique.centery + 10))
    
    font_score_val = pygame.font.Font(None, 65)
    txt_rec_val = font_score_val.render(str(score_c), True, (255, 255, 100))
    ecran.blit(txt_rec_val, (rect_classique.centerx - txt_rec_val.get_width()//2, rect_classique.centery + 40))
    
    txt_info = pygame.font.Font(None, 30).render("(Cliquez Ici)", True, (200, 200, 200))
    ecran.blit(txt_info, (rect_classique.centerx - txt_info.get_width()//2, rect_classique.centery + 90))

    # ZONE ARCADE (Droite)
    rect_arcade = pygame.Rect(largeur - 350, 150, 300, 300)
    pygame.draw.rect(ecran, (100, 50, 100), rect_arcade, border_radius=20)
    pygame.draw.rect(ecran, (255, 100, 255), rect_arcade, 3, border_radius=20)
    
    txt_arcade = font_mode.render("ARCADE", True, (255, 150, 255))
    ecran.blit(txt_arcade, (rect_arcade.centerx - txt_arcade.get_width()//2, rect_arcade.centery - 60))
    
    # Score Arcade
    score_a = scores.get('arcade', 0)
    ecran.blit(txt_rec_label, (rect_arcade.centerx - txt_rec_label.get_width()//2, rect_arcade.centery + 10))
    
    txt_rec_val_a = font_score_val.render(str(score_a), True, (255, 255, 100))
    ecran.blit(txt_rec_val_a, (rect_arcade.centerx - txt_rec_val_a.get_width()//2, rect_arcade.centery + 40))
    
    txt_info_a = pygame.font.Font(None, 30).render("(Touche 'A' / Clic)", True, (200, 200, 200))
    ecran.blit(txt_info_a, (rect_arcade.centerx - txt_info_a.get_width()//2, rect_arcade.centery + 60))
    
    # Instructions bas
    instructions = "ESC pour Pause  |  Coupez les fruits !"
    txt_inst = pygame.font.Font(None, 35).render(instructions, True, (150, 150, 150))
    ecran.blit(txt_inst, (largeur // 2 - txt_inst.get_width() // 2, hauteur - 50))


# DESSINER GAME OVER
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


# -------------------------------------------
# DESSINER LA PAUSE
# -------------------------------------------
def dessiner_pause(ecran, largeur, hauteur):
    """Affiche l'écran de pause"""
    # Overlay sombre
    overlay = pygame.Surface((largeur, hauteur))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(150)
    ecran.blit(overlay, (0, 0))
    
    # Texte PAUSE
    font = pygame.font.Font(None, 100)
    txt = font.render("PAUSE", True, (255, 255, 255))
    ecran.blit(txt, (largeur // 2 - txt.get_width() // 2, hauteur // 3))
    
    # Instructions
    font_small = pygame.font.Font(None, 50)
    resume = font_small.render("ESC: Reprendre", True, (200, 200, 200))
    quit_txt = font_small.render("Q: Quitter", True, (200, 200, 200))
    
    ecran.blit(resume, (largeur // 2 - resume.get_width() // 2, hauteur // 2))
    ecran.blit(quit_txt, (largeur // 2 - quit_txt.get_width() // 2, hauteur // 2 + 60))
