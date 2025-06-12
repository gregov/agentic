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

# Constante pour la taille de l'image de l'agent
AGENT_TARGET_HEIGHT_PIXELS = 50 # Définissez ici la hauteur souhaitée en pixels

class Agent:
    def __init__(self, x, y, default_image_path, boost_image_path):
        self.x = x
        self.y = y
        self.normal_speed_range = (-5, 5)
        self.default_image_path = default_image_path
        self.boost_image_path = boost_image_path
        self.current_speed_range = self.normal_speed_range
        self.boost_active = False
        self.boost_end_time = 0
        self.boost_duration_ms = 5000 # 5 secondes en millisecondes
        self.is_paused = False
        self.pause_end_time = 0
        self.pause_duration_ms = random.randint(500, 5000) # Durée de la pause entre 0.5 et 5 secondes
        self.time_to_next_pause_check = pygame.time.get_ticks() + random.randint(1000, 3000) # Prochain check dans 1-3 secondes
        self.pause_probability = 0.2 # 20% de chance de faire une pause lors d'un check

        self.boost_multiplier = 3
        try:
            # Charger et redimensionner l'image par défaut
            self.image_default = pygame.image.load(self.default_image_path)
            original_width = self.image_default.get_width()
            original_height = self.image_default.get_height()
            if original_height == 0: # Éviter la division par zéro
                aspect_ratio = 1 # Ou gérer comme une erreur/fallback
            else:
                aspect_ratio = original_width / original_height
            new_height = AGENT_TARGET_HEIGHT_PIXELS
            new_width = int(new_height * aspect_ratio)
            self.image_default = pygame.transform.scale(self.image_default, (new_width, new_height))

            # Charger et redimensionner l'image de boost
            self.image_boost = pygame.image.load(self.boost_image_path).convert()  # Convert to 24-bit
            original_width_boost = self.image_boost.get_width()
            original_height_boost = self.image_boost.get_height()
            aspect_ratio_boost = original_width_boost / original_height_boost if original_height_boost != 0 else 1
            new_width_boost = int(new_height * aspect_ratio_boost)
            self.image_boost = pygame.transform.smoothscale(self.image_boost, (new_width_boost, new_height))

            self.image = self.image_default # Image actuelle à afficher
        except pygame.error as e:
            print(f"Impossible de charger une des images ({self.default_image_path} ou {self.boost_image_path}): {e}")
            # Fallback sur un carré si l'image n'est pas trouvée
            self.image = pygame.Surface([50, 50])
            self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    def move_randomly(self):
        if self.is_paused:
            return # Ne pas bouger si en pause

        # Mouvement aléatoire simple
        self.x += random.randint(self.current_speed_range[0], self.current_speed_range[1])
        self.y += random.randint(self.current_speed_range[0], self.current_speed_range[1])

        # Garder l'agent dans les limites de l'écran en utilisant le rect
        # Mettre à jour le rectangle basé sur les nouvelles coordonnées
        self.rect.topleft = (self.x, self.y)

        # Clamper le rectangle aux limites de l'écran
        self.rect.clamp_ip(screen.get_rect())
        # Mettre à jour les coordonnées x et y de l'agent pour qu'elles correspondent au rectangle clampé
        self.x = self.rect.x
        self.y = self.rect.y

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def activate_boost(self):
        if not self.boost_active:
            print("Boost activé !")
            self.boost_active = True
            self.boost_end_time = pygame.time.get_ticks() + self.boost_duration_ms
            boosted_min = self.normal_speed_range[0] * self.boost_multiplier
            boosted_max = self.normal_speed_range[1] * self.boost_multiplier
            self.current_speed_range = (boosted_min, boosted_max)
            self.image = self.image_boost # Changer l'image pour l'image de boost

    def update_boost_status(self):
        if self.boost_active and pygame.time.get_ticks() > self.boost_end_time:
            print("Boost terminé.")
            self.boost_active = False
            self.current_speed_range = self.normal_speed_range
            self.image = self.image_default # Revenir à l'image par défaut

    def update_pause_status(self):
        current_time = pygame.time.get_ticks()
        if self.is_paused:
            if current_time > self.pause_end_time:
                self.is_paused = False
                print("Pause terminée.")
                # Planifier le prochain check de pause
                self.time_to_next_pause_check = current_time + random.randint(5000, 15000) # Prochain check dans 5-15 secondes
        elif not self.boost_active and current_time > self.time_to_next_pause_check: # Ne pas pauser si en boost
            if random.random() < self.pause_probability:
                self.is_paused = True
                self.pause_duration_ms = random.randint(500, 2000) # Nouvelle durée de pause
                self.pause_end_time = current_time + self.pause_duration_ms
                print(f"Agent en pause pour {self.pause_duration_ms / 1000.0}s.")
            else: # Si pas de pause, replanifier le prochain check
                self.time_to_next_pause_check = current_time + random.randint(3000, 8000)

# Création d'un agent
homer_default_image_path = os.path.join(ASSETS_DIR, 'homer.gif')
homer_boost_image_path = os.path.join(ASSETS_DIR, 'homer_up.gif')

agent = Agent(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, homer_default_image_path, homer_boost_image_path)

# Boucle principale de la simulation
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Clic gauche
                if agent.rect.collidepoint(event.pos):
                    agent.activate_boost()

    # Mettre à jour l'état de la simulation
    agent.update_boost_status()
    agent.update_pause_status()
    agent.move_randomly()

    # Dessiner
    screen.fill(BLACK)  # Fond noir
    agent.draw(screen)

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Contrôler la vitesse de la simulation (FPS)
    clock.tick(30)

pygame.quit()