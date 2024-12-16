import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Configuration de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mon Projet Pygame")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Variables du jeu
clock = pygame.time.Clock()
running = True

# Boucle principale
while running:
    # Gérer les événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Fermer la fenêtre
            running = False

    # Mise à jour des éléments du jeu

    # Dessiner à l'écran
    screen.fill(WHITE)  # Efface l'écran avec une couleur de fond
    pygame.display.flip()  # Met à jour l'affichage

    # Limiter à 60 FPS
    clock.tick(60)

# Quitter Pygame
pygame.quit()
sys.exit()
