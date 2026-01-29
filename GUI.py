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


def dessiner_menu(ecran, largeur, hauteur, images=None):
    # Fond
    if images and "bg" in images:
        dessiner_fond(ecran, largeur, hauteur, images)
    else:
        ecran.fill((10, 8, 25))

    # Fonts
    title_font = pygame.font.SysFont("arial", 72, bold=True)
    sub_font = pygame.font.SysFont("arial", 28, bold=True)
    hint_font = pygame.font.SysFont("arial", 22)

    # Couleurs néon
    cyan = (0, 255, 255)
    pink = (255, 40, 180)
    white = (230, 230, 240)

    # Petit pulse (anime le menu)
    t = pygame.time.get_ticks()
    pulse = 1.0 + 0.03 * (1 if (t // 300) % 2 == 0 else -1)

    #Titre (double rendu pour effet glow simple)
    title = "NEON SLICE DOJO"
    title_glow = title_font.render(title, True, pink)
    title_main = title_font.render(title, True, cyan)

    rect = title_main.get_rect(center=(largeur // 2, hauteur // 3))
    glow_rect = title_glow.get_rect(center=(rect.centerx + 2, rect.centery + 2))

    ecran.blit(title_glow, glow_rect)
    ecran.blit(title_main, rect)

    #Bouton START
    btn_text = "▶  START"
    btn = sub_font.render(btn_text, True, white)
    btn_rect = btn.get_rect(center=(largeur // 2, int(hauteur * 0.55)))

    #Fond du bouton (néon)
    padding_x, padding_y = 22, 14
    box = pygame.Rect(
        btn_rect.x - padding_x, btn_rect.y - padding_y,
        btn_rect.width + padding_x * 2, btn_rect.height + padding_y * 2
    )

    pygame.draw.rect(ecran, (20, 18, 45), box, border_radius=14)
    pygame.draw.rect(ecran, cyan, box, width=2, border_radius=14)

    ecran.blit(btn, btn_rect)

    # Hint
    hint = hint_font.render("Clique pour jouer (ou ENTER)", True, white)
    hint_rect = hint.get_rect(center=(largeur // 2, int(hauteur * 0.70)))
    ecran.blit(hint, hint_rect)

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
