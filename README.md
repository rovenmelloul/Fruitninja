# 🍎 Fruit Ninja : Neon Edition ⚔️

Une réinterprétation moderne et stylisée du célèbre jeu Fruit Ninja, développée en Python avec la bibliothèque Pygame. Ce projet propose une esthétique "Neon/Cyberpunk" et deux modes de jeu distincts.

## ✨ Fonctionnalités
- **Mode Classique** : Survie avec 3 vies, évitez les bombes et ne ratez aucun fruit.
- **Mode Arcade** : Score maximum en 30 secondes avec bonus de combo intensifs.
- **Système de Difficulté** : Trois niveaux (Facile, Normal, Difficile) influençant la physique (gravité/vitesse).
- **Bonus Freeze** : Un fruit spécial qui ralentit le temps (Time Scaling).
- **Records** : Sauvegarde automatique des meilleurs scores via `scores.json`.

## 🚀 Spécificités Techniques

### 1. Physique & Vecteurs
Le mouvement des fruits est calculé à l'aide de vecteurs de vitesse et d'une accélération gravitationnelle constante.
- **Vitesse verticale ($v_y$)** : Impulsion aléatoire au spawn.
- **Gravité ($g$)** : Appliquée à chaque frame pour simuler une parabole réaliste.

[Image of projectile motion physics diagram]


### 2. Détection de Collision
Utilisation de la **distance euclidienne** entre la trajectoire de la souris et le centre du fruit pour garantir une sensation de tranche naturelle.

### 3. Gestion des Assets (Spritesheets)
Optimisation des performances : tous les visuels sont regroupés dans une **Spritesheet 5x3**. Le script `GUI.py` découpe dynamiquement les textures en mémoire vive.

## 🛠️ Installation

1. **Clonez le dépôt** :
   ```bash
   git clone [https://github.com/votre-compte/fruit-ninja-neon.git](https://github.com/votre-compte/fruit-ninja-neon.git)
Installez Pygame :Bashpip install pygame
Lancez le jeu :Bashpython main.py
Bashpython main.py
📂 Structure du Projet
main.py : Point d'entrée et gestionnaire d'états.
GUI.py : Moteur de rendu et interface utilisateur (Néon HUD).
fruitninja.py : Logique du mode Classique.
fruitninja_arcade.py : Logique du mode Arcade.
score_manager.py : Persistance des données (JSON).

⌨️ Commandes : 
Touche,Action
Souris GAUCHE,Trancher (Maintenir et glisser)
ECHAP,Pause / Reprendre

Projet réalisé dans le cadre d'une soutenance technique - 2026.
Q (en pause),Retour au menu
