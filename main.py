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
        self.pause_probability = 0.2 # 20% de chance de faire une pause lors d'un check_

        self.boost_multiplier = 3

        # Pour l'animation des GIFs
        self.current_frame_index = 0
        self.animation_last_update = pygame.time.get_ticks()
        self.animation_frame_duration = 100 # Durée de chaque frame en ms (100ms = 10 FPS d'animation)

        try:
            self.frames_default = self._load_gif_frames(self.default_image_path, AGENT_TARGET_HEIGHT_PIXELS)
            self.frames_boost = self._load_gif_frames(self.boost_image_path, AGENT_TARGET_HEIGHT_PIXELS)

            if not self.frames_default:
                print(f"Fallback: Impossible de charger l'image par défaut animée {self.default_image_path}")
                fallback_surface = pygame.Surface([AGENT_TARGET_HEIGHT_PIXELS, AGENT_TARGET_HEIGHT_PIXELS])
                fallback_surface.fill(RED)
                self.frames_default = [fallback_surface]
            
            if not self.frames_boost:
                print(f"Fallback: Impossible de charger l'image boost animée {self.boost_image_path}, utilisation de l'image par défaut.")
                self.frames_boost = self.frames_default

            self.current_frames = self.frames_default
            self.image = self.current_frames[self.current_frame_index]

        except Exception as e: # Erreur générale imprévue (ex: Pillow non installé)
            print(f"Erreur majeure lors de l'initialisation des images animées: {e}")
            fallback_surface = pygame.Surface([AGENT_TARGET_HEIGHT_PIXELS, AGENT_TARGET_HEIGHT_PIXELS])
            fallback_surface.fill(RED)
            self.frames_default = [fallback_surface]
            self.frames_boost = [fallback_surface]
            self.current_frames = self.frames_default
            self.image = self.current_frames[0]

        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    def _load_gif_frames(self, path, target_height):
        frames = []
        try:
            from PIL import Image, ImageSequence
        except ImportError:
            print("Pillow (PIL) n'est pas installé. L'animation GIF est désactivée. Tentative de chargement statique.")
            try:
                img = pygame.image.load(path).convert_alpha()
                original_width, original_height = img.get_size()
                aspect_ratio = original_width / original_height if original_height else 1
                new_width = int(target_height * aspect_ratio)
                return [pygame.transform.smoothscale(img, (new_width, target_height))]
            except pygame.error as e:
                print(f"Impossible de charger {path} comme image statique: {e}")
                return []

        try:
            pil_image = Image.open(path)
            for frame in ImageSequence.Iterator(pil_image):
                frame_image = frame.convert("RGBA")
                pygame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode).convert_alpha()
                original_width, original_height = pygame_surface.get_size()
                aspect_ratio = original_width / original_height if original_height else 1
                new_width = int(target_height * aspect_ratio)
                scaled_surface = pygame.transform.smoothscale(pygame_surface, (new_width, target_height))
                frames.append(scaled_surface)
            if not frames and pil_image: # Cas d'une image statique ouverte avec PIL
                frame_image = pil_image.convert("RGBA")
                pygame_surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode).convert_alpha()
                original_width, original_height = pygame_surface.get_size()
                aspect_ratio = original_width / original_height if original_height else 1
                new_width = int(target_height * aspect_ratio)
                scaled_surface = pygame.transform.smoothscale(pygame_surface, (new_width, target_height))
                frames.append(scaled_surface)
        except Exception as e:
            print(f"Erreur lors du traitement du GIF {path} avec Pillow: {e}")
        return frames

    def move_randomly(self):
        if self.is_paused:
            return # Ne pas bouger si en pause

        # Mouvement aléatoire simple
        self.x += random.randint(self.current_speed_range[0], self.current_speed_range[1])
        self.y += random.randint(self.current_speed_range[0], self.current_speed_range[1])/4

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
            self.current_frames = self.frames_boost
            self.current_frame_index = 0 # Redémarrer l'animation du boost
            if self.current_frames:
                 self.image = self.current_frames[self.current_frame_index]

    def update_boost_status(self):
        if self.boost_active and pygame.time.get_ticks() > self.boost_end_time:
            print("Boost terminé.")
            self.boost_active = False
            self.current_speed_range = self.normal_speed_range
            self.current_frames = self.frames_default
            self.current_frame_index = 0 # Redémarrer l'animation par défaut
            if self.current_frames:
                self.image = self.current_frames[self.current_frame_index]


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

    def update_animation(self):
        if not self.current_frames or len(self.current_frames) <= 1:
            return # Pas d'animation si pas de frames ou une seule frame

        current_time = pygame.time.get_ticks()
        if current_time - self.animation_last_update > self.animation_frame_duration:
            self.animation_last_update = current_time
            self.current_frame_index = (self.current_frame_index + 1) % len(self.current_frames)
            self.image = self.current_frames[self.current_frame_index]

# Création d'un agent
homer_default_image_path = os.path.join(ASSETS_DIR, 'homer.gif')
homer_boost_image_path = os.path.join(ASSETS_DIR, 'homer_up.gif')

agent = Agent(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, homer_default_image_path, homer_boost_image_path)

# Boucle principale de la simulation
running = True
counter = 0
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
    agent.update_animation() # Mettre à jour l'animation avant de vérifier la pause ou de bouger
    agent.update_pause_status()
    if not counter % 10:  # Toutes les 10 itérations, l'agent bouge
        agent.move_randomly()

    # Dessiner
    screen.fill(BLACK)  # Fond noir
    agent.draw(screen)

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Contrôler la vitesse de la simulation (FPS)
    clock.tick(30)

    # Incrementer le compteur
    counter += 1

pygame.quit()