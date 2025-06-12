import pygame
import random
import os

# Initialisation de Pygame
pygame.init()

# Constantes de l'écran
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Simulation de Vie 3D Démo"

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Configuration de l'écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

# Horloge pour contrôler le FPS
clock = pygame.time.Clock()

# Chemin vers le dossier des assets
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

class Agent:
    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        try:
            self.image = pygame.image.load(image_path)
            # Redimensionner l'image si nécessaire (exemple : 50 pixels de large, hauteur proportionnelle)
            # width = 50
            # height = int(self.image.get_height() * (width / self.image.get_width()))
            # self.image = pygame.transform.scale(self.image, (width, height))
        except pygame.error as e:
            print(f"Impossible de charger l'image {image_path}: {e}")
            # Fallback sur un carré si l'image n'est pas trouvée
            self.image = pygame.Surface([50, 50])
            self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    def move_randomly(self):
        # Mouvement aléatoire simple
        self.x += random.randint(-5, 5)
        self.y += random.randint(-5, 5)

        # Garder l'agent dans les limites de l'écran en utilisant le rect
        self.rect.clamp_ip(screen.get_rect())
        self.x = self.rect.x
        self.y = self.rect.y
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Création d'un agent
homer_image_path = os.path.join(ASSETS_DIR, 'homer.png') # Assurez-vous que 'homer.png' est dans le dossier 'assets'
agent = Agent(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, homer_image_path)

# Boucle principale de la simulation
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Mettre à jour l'état de la simulation
    agent.move_randomly()

    # Dessiner
    screen.fill(BLACK)  # Fond noir
    agent.draw(screen)

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Contrôler la vitesse de la simulation (FPS)
    clock.tick(30)

pygame.quit()