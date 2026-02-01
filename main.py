import pygame
from GUI import MenuGUI, charger_assets
from fruitninja import jouer_classique
from fruitninja_arcade import jouer_arcade
from score_manager import charger_scores

WIDTH, HEIGHT = 1200, 800

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fruit Ninja - Neon Edition")

    assets = charger_assets()

    while True:
        scores = charger_scores()
        menu = MenuGUI(screen, WIDTH, HEIGHT, assets, scores)
        action, mode, difficulty = menu.run()

        if action == "quit":
            break

        if action == "start":
            if mode == "classique":
                jouer_classique(difficulty=difficulty, window_size=(WIDTH, HEIGHT))
            else:
                jouer_arcade(difficulty=difficulty, window_size=(WIDTH, HEIGHT))

            # Revenir au menu ensuite (boucle)

    pygame.quit()

if __name__ == "__main__":
    main()
