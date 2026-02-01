import os
import pygame

# =========================
# CHEMINS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def path(*parts):
    return os.path.join(BASE_DIR, *parts)

BG_PATH = path("images", "backgrounds", "bg_neon_grid_v1.png")
SHEET_PATH = path("images", "spritesheets", "neon_pack_v1.png")
FONT_PATH = path("fonts", "PressStart2P-Regular.ttf")

# IMPORTANT: ce spritesheet = 5x3
SHEET_COLS = 5
SHEET_ROWS = 3

# =========================
# MAPPING SPRITES (5x3)
# index = row*5 + col
# Row0: 0 pomme, 1 banane, 2 pasteque, 3 prune, 4 bombe
# Row1: 5 pomme cut, 6 banane cut, 7 pasteque cut, 8 fraise cut, 9 citron cut
# Row2: 10 pomme slice, 11 banane slice, 12 pasteque slice, 13 fraise slice, 14 freeze
# =========================
SPRITE_INDEX = {
    "pomme":    {"whole": 0, "cut": [5, 10]},
    "banane":   {"whole": 1, "cut": [6, 11]},
    "pasteque": {"whole": 2, "cut": [7, 12]},
    "prune":    {"whole": 3, "cut": [8, 13]},   # si tu veux garder "kiwi" on le mappe sur prune
    "kiwi":     {"whole": 3, "cut": [8, 13]},   # compat avec ton ancien code
    "orange":   {"whole": 2, "cut": [7, 12]},   # compat (si ton code parle d'orange)
    "bombe":    {"whole": 4, "cut": [4]},
    "freeze":   {"whole": 14, "cut": [14]},
}

# =========================
# CHARGEMENT / DECOUPE
# =========================
def _load_font(size, fallback):
    try:
        return pygame.font.Font(FONT_PATH, size)
    except Exception:
        return pygame.font.Font(None, fallback)

def extraire_sprites(sheet, cols, rows):
    """Découpe propre SANS numpy / surfarray."""
    sprites = []
    w = sheet.get_width() // cols
    h = sheet.get_height() // rows

    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c * w, r * h, w, h)
            img = pygame.Surface((w, h), pygame.SRCALPHA)
            img.blit(sheet, (0, 0), rect)
            sprites.append(img)
    return sprites

def charger_assets():
    """Charge fond, spritesheet et polices."""
    assets = {
        "bg": None,
        "sheet": None,
        "sprites": [],
        "font_title": None,
        "font_ui": None,
        "font_small": None,
        "bg_scroll": 0,
    }

    # Fonts
    assets["font_title"] = _load_font(44, 60)
    assets["font_ui"] = _load_font(18, 30)
    assets["font_small"] = _load_font(14, 22)

    # Background
    if os.path.exists(BG_PATH):
        assets["bg"] = pygame.image.load(BG_PATH).convert()

    # Spritesheet
    if os.path.exists(SHEET_PATH):
        sheet = pygame.image.load(SHEET_PATH).convert_alpha()

        # Si jamais ton sheet avait du noir "plein" (normalement non),
        # tu peux décommenter:
        # sheet.set_colorkey((0, 0, 0))

        assets["sheet"] = sheet
        assets["sprites"] = extraire_sprites(sheet, SHEET_COLS, SHEET_ROWS)

    return assets

# =========================
# DESSIN FOND
# =========================
def dessiner_fond(ecran, largeur, hauteur, assets):
    if not assets or assets.get("bg") is None:
        ecran.fill((10, 8, 25))
        return

    bg = assets["bg"]
    bg_scaled = pygame.transform.smoothscale(bg, (largeur, hauteur))

    assets["bg_scroll"] = (assets["bg_scroll"] + 1) % hauteur
    y = assets["bg_scroll"]

    ecran.blit(bg_scaled, (0, -y))
    ecran.blit(bg_scaled, (0, hauteur - y))

# =========================
# OUTILS SPRITES
# =========================
def sprite_pour(nom, coupe=False, variante=0, sprites=None):
    """Renvoie une Surface Pygame pour le nom demandé."""
    if sprites is None or len(sprites) == 0:
        return None

    data = SPRITE_INDEX.get(nom)
    if not data:
        return None

    if not coupe:
        idx = data["whole"]
        return sprites[idx] if 0 <= idx < len(sprites) else None

    choices = data["cut"]
    idx = choices[variante % len(choices)]
    return sprites[idx] if 0 <= idx < len(sprites) else None

def _blit_center(ecran, img, x, y, size):
    """Blit une image centrée (x,y) avec scale 'size' (int)."""
    if img is None:
        return
    surf = pygame.transform.smoothscale(img, (size, size))
    ecran.blit(surf, (x - size // 2, y - size // 2))

# =========================
# MENU UI
# =========================
class MenuGUI:
    def __init__(self, ecran, largeur, hauteur, assets, scores):
        self.ecran = ecran
        self.largeur = largeur
        self.hauteur = hauteur
        self.assets = assets
        self.scores = scores

        self.mode = "classique"
        self.difficulty = "normal"

        # Layout proche de ce que tu avais (grand, propre)
        w_block = 480
        h_block = 300
        gap = 40
        x1 = (largeur // 2) - w_block - (gap // 2)
        x2 = (largeur // 2) + (gap // 2)
        y = 170

        self.rect_classique = pygame.Rect(x1, y, w_block, h_block)
        self.rect_arcade = pygame.Rect(x2, y, w_block, h_block)

        # Difficulté
        btn_w, btn_h = 210, 70
        y_btn = 520
        gap_btn = 30
        start_x = (largeur // 2) - (btn_w * 3 + gap_btn * 2) // 2

        self.rect_easy = pygame.Rect(start_x + 0 * (btn_w + gap_btn), y_btn, btn_w, btn_h)
        self.rect_normal = pygame.Rect(start_x + 1 * (btn_w + gap_btn), y_btn, btn_w, btn_h)
        self.rect_hard = pygame.Rect(start_x + 2 * (btn_w + gap_btn), y_btn, btn_w, btn_h)

        # Jouer
        self.rect_start = pygame.Rect(largeur // 2 - 220, 620, 440, 85)

    def _draw_panel(self, rect, selected, accent_color):
        pygame.draw.rect(self.ecran, (0, 0, 0), rect, border_radius=28)
        border = accent_color if selected else (130, 130, 130)
        pygame.draw.rect(self.ecran, border, rect, 3, border_radius=28)

    def _draw_button(self, rect, label, selected=False, accent=(0, 220, 255)):
        fill = (25, 15, 45) if not selected else (55, 30, 95)
        border = accent if selected else (140, 140, 140)

        pygame.draw.rect(self.ecran, fill, rect, border_radius=18)
        pygame.draw.rect(self.ecran, border, rect, 3, border_radius=18)

        font = self.assets["font_ui"]
        txt = font.render(label, True, (255, 255, 255))
        self.ecran.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

    def draw(self):
        dessiner_fond(self.ecran, self.largeur, self.hauteur, self.assets)

        font_title = self.assets["font_title"]
        font_ui = self.assets["font_ui"]
        font_small = self.assets["font_small"]
        sprites = self.assets.get("sprites", [])

        title = font_title.render("FRUIT NINJA  NEON", True, (255, 255, 255))
        subtitle = font_small.render("Choisis un mode + une difficulte (puis JOUER)", True, (220, 220, 220))

        self.ecran.blit(title, (self.largeur // 2 - title.get_width() // 2, 70))
        self.ecran.blit(subtitle, (self.largeur // 2 - subtitle.get_width() // 2, 125))

        # Panels
        self._draw_panel(self.rect_classique, self.mode == "classique", (0, 220, 255))
        self._draw_panel(self.rect_arcade, self.mode == "arcade", (255, 120, 255))

        # Text modes
        t1 = font_ui.render("MODE : CLASSIQUE", True, (200, 255, 255))
        t2 = font_ui.render("MODE : ARCADE", True, (255, 200, 255))

        self.ecran.blit(t1, (self.rect_classique.centerx - t1.get_width() // 2, self.rect_classique.y + 35))
        self.ecran.blit(t2, (self.rect_arcade.centerx - t2.get_width() // 2, self.rect_arcade.y + 35))

        # Icônes (images, pas emojis -> pas de "????")
        # Classique: pomme, banane, pastèque
        y_icons = self.rect_classique.y + 125
        _blit_center(self.ecran, sprite_pour("pomme", False, 0, sprites), self.rect_classique.centerx - 90, y_icons, 80)
        _blit_center(self.ecran, sprite_pour("banane", False, 0, sprites), self.rect_classique.centerx, y_icons, 80)
        _blit_center(self.ecran, sprite_pour("pasteque", False, 0, sprites), self.rect_classique.centerx + 90, y_icons, 80)

        # Arcade: prune, bombe, freeze
        y_icons2 = self.rect_arcade.y + 125
        _blit_center(self.ecran, sprite_pour("prune", False, 0, sprites), self.rect_arcade.centerx - 90, y_icons2, 80)
        _blit_center(self.ecran, sprite_pour("bombe", False, 0, sprites), self.rect_arcade.centerx, y_icons2, 80)
        _blit_center(self.ecran, sprite_pour("freeze", False, 0, sprites), self.rect_arcade.centerx + 90, y_icons2, 80)

        # Records
        rec_c = self.scores.get("classique", 0)
        rec_a = self.scores.get("arcade", 0)

        r1 = font_ui.render("RECORD", True, (220, 220, 220))
        r2 = font_ui.render("RECORD", True, (220, 220, 220))

        s1 = font_title.render(str(rec_c), True, (255, 255, 255))
        s2 = font_title.render(str(rec_a), True, (255, 255, 255))

        self.ecran.blit(r1, (self.rect_classique.centerx - r1.get_width() // 2, self.rect_classique.y + 190))
        self.ecran.blit(s1, (self.rect_classique.centerx - s1.get_width() // 2, self.rect_classique.y + 220))

        self.ecran.blit(r2, (self.rect_arcade.centerx - r2.get_width() // 2, self.rect_arcade.y + 190))
        self.ecran.blit(s2, (self.rect_arcade.centerx - s2.get_width() // 2, self.rect_arcade.y + 220))

        # Difficulty label
        lbl = font_ui.render("DIFFICULTE :", True, (200, 200, 200))
        self.ecran.blit(lbl, (self.largeur // 2 - lbl.get_width() // 2, 485))

        # Buttons difficulty
        self._draw_button(self.rect_easy, "FACILE", selected=(self.difficulty == "easy"), accent=(0, 220, 255))
        self._draw_button(self.rect_normal, "NORMAL", selected=(self.difficulty == "normal"), accent=(0, 220, 255))
        self._draw_button(self.rect_hard, "DIFFICILE", selected=(self.difficulty == "hard"), accent=(0, 220, 255))

        # Start
        self._draw_button(self.rect_start, "JOUER", selected=True, accent=(255, 230, 100))

        footer = font_small.render("ECHAP : quitter", True, (170, 170, 170))
        self.ecran.blit(footer, (self.largeur // 2 - footer.get_width() // 2, self.hauteur - 32))

    def run(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.draw()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return ("quit", None, None)

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return ("quit", None, None)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos

                    if self.rect_classique.collidepoint(mx, my):
                        self.mode = "classique"
                    elif self.rect_arcade.collidepoint(mx, my):
                        self.mode = "arcade"
                    elif self.rect_easy.collidepoint(mx, my):
                        self.difficulty = "easy"
                    elif self.rect_normal.collidepoint(mx, my):
                        self.difficulty = "normal"
                    elif self.rect_hard.collidepoint(mx, my):
                        self.difficulty = "hard"
                    elif self.rect_start.collidepoint(mx, my):
                        return ("start", self.mode, self.difficulty)

# =========================
# FONCTIONS DESSIN POUR LE JEU
# =========================
def dessiner_fruit(ecran, assets, fruit):
    sprites = assets.get("sprites", [])
    img = sprite_pour(fruit["nom"], coupe=False, sprites=sprites)
    if img is None:
        return

    size = int(fruit.get("size", 120))
    img = pygame.transform.smoothscale(img, (size, size))

    # rotation
    rot = fruit.get("rot", 0.0)
    img = pygame.transform.rotate(img, rot)
    rect = img.get_rect(center=(int(fruit["x"]), int(fruit["y"])))
    ecran.blit(img, rect.topleft)

def dessiner_bombe(ecran, assets, bombe):
    sprites = assets.get("sprites", [])
    img = sprite_pour("bombe", coupe=False, sprites=sprites)
    if img is None:
        return

    size = int(bombe.get("size", 120))
    img = pygame.transform.smoothscale(img, (size, size))
    rect = img.get_rect(center=(int(bombe["x"]), int(bombe["y"])))
    ecran.blit(img, rect.topleft)

def dessiner_fruit_coupe(ecran, assets, moitie):
    sprites = assets.get("sprites", [])
    img = sprite_pour(moitie["nom"], coupe=True, variante=moitie.get("variant", 0), sprites=sprites)
    if img is None:
        return

    size = int(moitie.get("size", 110))
    img = pygame.transform.smoothscale(img, (size, size))

    rot = moitie.get("rot", 0.0)
    img = pygame.transform.rotate(img, rot)
    rect = img.get_rect(center=(int(moitie["x"]), int(moitie["y"])))
    ecran.blit(img, rect.topleft)

def dessiner_lame(ecran, points):
    if not points or len(points) < 2:
        return
    # simple lame néon
    for i in range(1, len(points)):
        pygame.draw.line(ecran, (0, 220, 255), points[i - 1], points[i], 4)
        pygame.draw.line(ecran, (255, 255, 255), points[i - 1], points[i], 2)

def dessiner_score(ecran, assets, score, vies):
    font = assets["font_ui"]
    t1 = font.render(f"SCORE : {score}", True, (255, 255, 255))
    t2 = font.render(f"VIES : {vies}", True, (255, 255, 255))
    ecran.blit(t1, (20, 20))
    ecran.blit(t2, (20, 50))

def dessiner_bonus(ecran, assets, bonus_textes):
    font = assets["font_small"]
    for b in bonus_textes:
        img = font.render(b["texte"], True, b.get("color", (255, 255, 255)))
        ecran.blit(img, (int(b["x"]), int(b["y"])))

def dessiner_game_over(ecran, assets, largeur, hauteur, score):
    overlay = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    ecran.blit(overlay, (0, 0))

    ft = assets["font_title"]
    fu = assets["font_ui"]

    t = ft.render("GAME OVER", True, (255, 255, 255))
    s = fu.render(f"Score : {score}", True, (255, 230, 100))
    h = fu.render("Clique pour revenir au menu", True, (200, 200, 200))

    ecran.blit(t, (largeur // 2 - t.get_width() // 2, hauteur // 2 - 120))
    ecran.blit(s, (largeur // 2 - s.get_width() // 2, hauteur // 2 - 40))
    ecran.blit(h, (largeur // 2 - h.get_width() // 2, hauteur // 2 + 30))

def dessiner_pause(ecran, assets, largeur, hauteur):
    overlay = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    ecran.blit(overlay, (0, 0))

    ft = assets["font_title"]
    fu = assets["font_ui"]

    t = ft.render("PAUSE", True, (255, 255, 255))
    h = fu.render("ECHAP : reprendre | Q : menu", True, (200, 200, 200))

    ecran.blit(t, (largeur // 2 - t.get_width() // 2, hauteur // 2 - 80))
    ecran.blit(h, (largeur // 2 - h.get_width() // 2, hauteur // 2 + 10))
