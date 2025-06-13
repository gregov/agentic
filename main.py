import pygame
import random
import os
import uuid # Pour des IDs uniques pour les agents

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
ORANGE = (255, 140, 0)
BROWN = (139, 69, 19)
DARK_RED = (139, 0, 0)
LIGHT_BLUE = (173, 216, 230) # Couleur pour les fenêtres
DARK_BROWN = (101, 67, 33) # Couleur pour la porte
SAND_COLOR = (244, 164, 96) # Couleur sable
WATER_BLUE = (0, 119, 190) # Couleur eau
WET_SAND_COLOR = (220, 150, 80) # Couleur sable humide, légèrement plus foncée
UMBRELLA_RED = (255, 0, 0) # Couleur pour le parasol
UMBRELLA_POLE = (150, 75, 0) # Marron pour le mât du parasol
LOUNGE_CHAIR_BLUE = (100, 149, 237) # Bleu pour la chaise longue
CINEMA_DARK_GREY = (50, 50, 50) # Gris foncé pour le cinéma
CINEMA_MARQUEE_YELLOW = (255, 223, 0) # Jaune pour l'enseigne du cinéma
ARCADE_PURPLE = (128, 0, 128) # Violet pour la salle de jeux
ARCADE_NEON_PINK = (255, 105, 180) # Rose néon pour détails salle de jeux
ARCADE_NEON_GREEN = (57, 255, 20) # Vert néon pour détails salle de jeux
PARK_GRASS_GREEN = (34, 139, 34) # Vert pour l'herbe du parc
TREE_TRUNK_BROWN = (139, 69, 19) # Marron pour le tronc (peut réutiliser BROWN)
TREE_LEAVES_GREEN = (0, 100, 0) # Vert foncé pour les feuilles des arbres
SCHOOL_BUILDING_COLOR = (210, 180, 140) # Beige pour le bâtiment de l'école
SCHOOL_ROOF_COLOR = (160, 82, 45)    # Sienne pour le toit de l'école
SCHOOL_DOOR_COLOR = (139, 69, 19)    # Marron foncé pour la porte de l'école

# Configuration de l'écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

# Horloge pour contrôler le FPS
clock = pygame.time.Clock()

# Police pour le texte
SMALL_FONT = pygame.font.Font(None, 24) # Police simple pour les enseignes

# Chemin vers le dossier des assets
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# Constante pour la taille de l'image de l'agent
AGENT_TARGET_HEIGHT_PIXELS = 50 # Définissez ici la hauteur souhaitée en pixels

# Constantes pour la simulation de vie
GESTATION_DURATION_MS = 10000  # 10 secondes (au lieu de 30)
MIN_FERTILITY_AGE_MS = 5000   # Devient fertile à 5 secondes (au lieu de 15)
MAX_AGE_MS = 90000             # Durée de vie de 90 secondes (peut être ajusté)
REPRODUCTION_COOLDOWN_MS = 3000 # 3 secondes de repos (au lieu de 10)
TARGET_POPULATION = 15 # Augmenté légèrement pour voir plus d'interactions scolaires
BASE_CONCEPTION_PROBABILITY = 0.75 # Chance de base de concevoir (au lieu de 0.5)
NEWBORN_DURATION_MS = 15000 # 15 secondes pendant lesquelles l'agent est plus petit et va à l'école
NEWBORN_SCALE_FACTOR = 0.5 # Facteur de réduction de taille pour les nouveau-nés

# Constantes pour les orages
THUNDERSTORM_PROBABILITY_PER_CHECK = 0.15 # Chance de démarrer un orage lors d'un check (ajustée à 15%)
THUNDERSTORM_CHECK_INTERVAL_MS = 10000   # Vérifier toutes les 10 secondes (fortement diminué)
MIN_THUNDERSTORM_DURATION_MS = 8000      # Durée minimale d'un orage (8s)
MAX_THUNDERSTORM_DURATION_MS = 15000     # Durée maximale d'un orage (15s)
LIGHTNING_STRIKE_PROBABILITY_PER_AGENT_PER_TICK = 0.0001 # Encore plus faible

# État de l'orage
IS_THUNDERSTORM_ACTIVE = False
LAST_THUNDERSTORM_CHECK_MS = 0
THUNDERSTORM_END_TIME_MS = 0

# Stockage des rectangles des corps des maisons pour la détection d'abri
# (les agents iront ici pendant les orages)
HOUSE_BODY_RECTS = []

# Constantes pour les activités des agents
MIN_LEISURE_DURATION_MS = 10000      # Durée minimale d'une activité de loisir (10s)
MAX_LEISURE_DURATION_MS = 25000      # Durée maximale d'une activité de loisir (25s)
MIN_TIME_BETWEEN_LEISURE_MS = 8000   # Temps minimal avant de choisir une nouvelle activité de loisir (8s)
MAX_TIME_BETWEEN_LEISURE_MS = 20000  # Temps maximal avant de choisir une nouvelle activité de loisir (20s)
LEISURE_ACTIVITY_PROBABILITY = 0.4 # Chance de choisir une activité de loisir quand les conditions sont remplies
ACTIVITY_REACH_THRESHOLD = 20      # Distance pour considérer qu'un agent est "arrivé" à sa cible ponctuelle

ALL_AGENTS = [] # Liste globale pour que les agents puissent interagir

FOOD_RADIUS = 7
FOOD_ATTRACT_RADIUS = 200  # Distance max d'attraction
REPRODUCTION_ATTRACT_RADIUS = 150 # Distance max pour chercher un partenaire
FOOD_LIST = []

FOOD_SPAWN_INTERVAL_MS = 30000 # 30 secondes

class Agent:
    def __init__(self, x, y, default_image_path, boost_image_path):
        self.id = uuid.uuid4()
        self.x = x
        self.y = y

        # Attributs de cycle de vie
        self.time_created_ms = pygame.time.get_ticks()
        self.age_ms = 0
        self.max_age_ms = MAX_AGE_MS + random.randint(-10000, 10000) # Un peu de variation
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
        # self.is_seeking_shelter = False # Remplacé par current_activity

        self.current_activity = "idle" # ex: "idle", "seeking_food", "seeking_shelter", "at_beach", etc.
        self.activity_target_pos = None # (x, y)
        self.activity_end_time = 0 # timestamp pour la fin de l'activité de loisir
        self.time_to_next_leisure_decision = pygame.time.get_ticks() + random.randint(MIN_TIME_BETWEEN_LEISURE_MS, MAX_TIME_BETWEEN_LEISURE_MS)
        self.last_leisure_activity_finish_time = pygame.time.get_ticks()
        self.pause_probability = 0.2 # 20% de chance de faire une pause lors d'un check

        self.is_fertile = False
        self.is_pregnant = False
        self.gestation_start_ms = 0
        self.last_reproduction_attempt_ms = 0

        # Attributs pour la taille du nouveau-né
        self.is_newborn = True # Commence comme nouveau-né
        self.newborn_end_time = self.time_created_ms + NEWBORN_DURATION_MS


        self.boost_multiplier = 3

        # Pour l'animation des GIFs
        self.current_frame_index = 0
        self.animation_last_update = pygame.time.get_ticks()
        self.animation_frame_duration = 100 # Durée de chaque frame en ms (100ms = 10 FPS d'animation)

        try:
            # Charger les frames à leur taille normale (pleine échelle)
            self.full_scale_frames_default = self._load_gif_frames(self.default_image_path, AGENT_TARGET_HEIGHT_PIXELS)
            self.full_scale_frames_boost = self._load_gif_frames(self.boost_image_path, AGENT_TARGET_HEIGHT_PIXELS)

            if not self.full_scale_frames_default:
                print(f"Fallback: Impossible de charger l'image par défaut animée {self.default_image_path}")
                fallback_surface = pygame.Surface([AGENT_TARGET_HEIGHT_PIXELS, AGENT_TARGET_HEIGHT_PIXELS])
                fallback_surface.fill(RED)
                self.full_scale_frames_default = [fallback_surface]
            
            if not self.full_scale_frames_boost:
                print(f"Fallback: Impossible de charger l'image boost animée {self.boost_image_path}, utilisation de l'image par défaut.")
                self.full_scale_frames_boost = self.full_scale_frames_default

        except Exception as e: # Erreur générale imprévue (ex: Pillow non installé)
            print(f"Erreur majeure lors de l'initialisation des images animées: {e}")
            fallback_surface = pygame.Surface([AGENT_TARGET_HEIGHT_PIXELS, AGENT_TARGET_HEIGHT_PIXELS])
            fallback_surface.fill(RED)
            self.full_scale_frames_default = [fallback_surface]
            self.full_scale_frames_boost = [fallback_surface]

        self._apply_current_scale() # Appliquer l'échelle initiale (nouveau-né)

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

    def _scale_frame_list(self, original_frames, target_height):
        if not original_frames:
            # Créer un fallback si original_frames est vide, basé sur target_height
            fallback_surface = pygame.Surface([int(target_height), int(target_height)]) # Assurer des dimensions entières
            fallback_surface.fill(RED)
            return [fallback_surface]
            
        scaled_frames = []
        for frame in original_frames:
            original_width, original_height = frame.get_size()
            aspect_ratio = original_width / original_height if original_height else 1
            new_width = int(target_height * aspect_ratio)
            if new_width <= 0 or target_height <= 0: # Empêcher les dimensions nulles ou négatives
                # print(f"Warning: Tentative de redimensionnement à {new_width}x{target_height}. Utilisation d'un fallback 1x1.")
                scaled_surface = pygame.Surface((1,1)) # Fallback minimal
                scaled_surface.fill(RED)
            else:
                scaled_surface = pygame.transform.smoothscale(frame, (new_width, int(target_height)))
            scaled_frames.append(scaled_surface)
        return scaled_frames

    def _apply_current_scale(self):
        current_target_height = AGENT_TARGET_HEIGHT_PIXELS
        if self.is_newborn:
            current_target_height *= NEWBORN_SCALE_FACTOR

        self.frames_default = self._scale_frame_list(self.full_scale_frames_default, int(current_target_height))
        self.frames_boost = self._scale_frame_list(self.full_scale_frames_boost, int(current_target_height))

        self.current_frames = self.frames_boost if self.boost_active else self.frames_default
        self.image = self.current_frames[self.current_frame_index % len(self.current_frames)]

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
                 self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update_boost_status(self):
        if self.boost_active and pygame.time.get_ticks() > self.boost_end_time:
            print("Boost terminé.")
            self.boost_active = False
            self.current_speed_range = self.normal_speed_range
            
            self.current_frames = self.frames_default
            self.current_frame_index = 0 # Redémarrer l'animation par défaut
            if self.current_frames:
                self.image = self.current_frames[self.current_frame_index]
                self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update_size_status(self, current_time):
        if self.is_newborn and current_time > self.newborn_end_time:
            self.is_newborn = False
            print(f"Agent {self.id} a grandi !")
            # Si l'agent était à l'école ou en route, il quitte maintenant
            if self.current_activity in ["going_to_school", "at_school"]:
                print(f"Agent {self.id} a terminé l'école (a grandi).")
                self.current_activity = "idle"
                self.activity_target_pos = None
                self.time_to_next_leisure_decision = current_time # Peut choisir une activité de loisir
            self._apply_current_scale() # Appliquer la nouvelle taille (normale)

    def update_pause_status(self):
        current_time = pygame.time.get_ticks()
        if self.is_paused:
            if current_time > self.pause_end_time:
                self.is_paused = False
                # print("Pause terminée.") # Moins de logs
                # Planifier le prochain check de pause
                self.time_to_next_pause_check = current_time + random.randint(5000, 15000) # Prochain check dans 5-15 secondes
        elif not self.boost_active and current_time > self.time_to_next_pause_check: # Ne pas pauser si en boost
            if random.random() < self.pause_probability:
                self.is_paused = True
                self.pause_duration_ms = random.randint(500, 2000) # Nouvelle durée de pause
                self.pause_end_time = current_time + self.pause_duration_ms
                # print(f"Agent en pause pour {self.pause_duration_ms / 1000.0}s.") # Moins de logs
            else: # Si pas de pause, replanifier le prochain check
                self.time_to_next_pause_check = current_time + random.randint(3000, 8000)

    def update_life_cycle(self, current_time, current_population_size):
        self.age_ms = current_time - self.time_created_ms

        # Vérifier la mort par vieillesse
        if self.age_ms > self.max_age_ms:
            print(f"Agent {self.id} est mort de vieillesse.")
            return {"type": "death", "id": self.id}

        # Mettre à jour la fertilité
        if not self.is_pregnant and \
           self.age_ms > MIN_FERTILITY_AGE_MS and \
           current_time > self.last_reproduction_attempt_ms + REPRODUCTION_COOLDOWN_MS:
            if not self.is_fertile: # Pour n'afficher le message qu'une fois lors du changement d'état
                # print(f"DEBUG: Agent {self.id} devient fertile. Age: {self.age_ms/1000:.1f}s, Cooldown_OK: {current_time > self.last_reproduction_attempt_ms + REPRODUCTION_COOLDOWN_MS}")
                self.is_fertile = True
        else:
            self.is_fertile = False

        # Gérer la gestation et la naissance
        if self.is_pregnant and current_time > self.gestation_start_ms + GESTATION_DURATION_MS:
            self.is_pregnant = False
            self.is_fertile = False # Entra en cooldown
            self.last_reproduction_attempt_ms = current_time
            print(f"Agent {self.id} a donné naissance !")
            
            # Position du nouveau-né légèrement décalée
            birth_x = self.x + random.randint(-20, 20)
            birth_y = self.y + random.randint(-20, 20)
            return {"type": "birth", "x": birth_x, "y": birth_y, "parent_id": self.id}
        
        return None # Aucun événement de cycle de vie majeur

    def attempt_reproduction(self, partner, current_time, current_population_size):
        # print(f"DEBUG: Tentative repro entre {self.id} (fertile: {self.is_fertile}, preg: {self.is_pregnant}) et {partner.id} (fertile: {partner.is_fertile}, preg: {partner.is_pregnant})")
        if self.is_fertile and partner.is_fertile and \
           not self.is_pregnant and not partner.is_pregnant:
            
            # print(f"DEBUG: Conditions initiales OK pour repro entre {self.id} et {partner.id}")
            # Ajuster la probabilité de conception en fonction de la population
            conception_probability = BASE_CONCEPTION_PROBABILITY
            if current_population_size > TARGET_POPULATION + 2:
                conception_probability *= 0.3 # Réduit fortement si surpopulation
            elif current_population_size < TARGET_POPULATION - 2:
                conception_probability *= 1.5 # Augmente si sous-population
            conception_probability = min(1.0, conception_probability) # Capper à 100%

            if random.random() < conception_probability:
                # Un des deux devient gestant (ici, self)
                self.is_pregnant = True
                self.gestation_start_ms = current_time
                self.is_fertile = False # Plus fertile pendant la gestation
                self.last_reproduction_attempt_ms = current_time
                partner.last_reproduction_attempt_ms = current_time # Cooldown pour le partenaire aussi
                print(f"Agent {self.id} est maintenant gestant après rencontre avec {partner.id}. Pop: {current_population_size}, Prob: {conception_probability:.2f}")
                return True
            # else:
                # print(f"DEBUG: Échec du jet de probabilité pour repro entre {self.id} et {partner.id} (Prob: {conception_probability:.2f})")
        return False

    def update_animation(self):
        if not self.current_frames or len(self.current_frames) <= 1:
            return # Pas d'animation si pas de frames ou une seule frame
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_last_update > self.animation_frame_duration:
            self.animation_last_update = current_time
            self.current_frame_index = (self.current_frame_index + 1) % len(self.current_frames)
            # S'assurer que l'index est valide même si current_frames a changé (ex: _apply_current_scale)
            if self.current_frame_index >= len(self.current_frames):
                self.current_frame_index = 0
            self.image = self.current_frames[self.current_frame_index]

    def move_towards_target(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx**2 + dy**2)**0.5

        if dist > 1: # Arrêter si très proche pour éviter de "vibrer"
            # Utiliser la magnitude de la vitesse actuelle (peut être boostée)
            speed = max(abs(self.current_speed_range[0]), abs(self.current_speed_range[1]))
            
            self.x += int(round(dx / dist * speed))
            self.y += int(round(dy / dist * speed))
            
            self.rect.topleft = (self.x, self.y)
            self.rect.clamp_ip(screen.get_rect()) # Assurer que l'agent reste dans l'écran
            self.x = self.rect.x
            self.y = self.rect.y
            # Mettre à jour le rect après le clamp, car la taille peut avoir changé (nouveau-né -> adulte)
            self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def decide_and_move_towards_food(self, food_list):
        if not food_list or self.is_paused: # Ne rien faire si pas de nourriture ou en pause
            return False

        # Chercher la nourriture la plus proche
        closest_food = None
        min_dist_sq = float('inf') # Utiliser la distance au carré pour l'optimisation

        for food in food_list:
            dx = food["x"] - self.x
            dy = food["y"] - self.y
            dist_sq = dx**2 + dy**2
            if dist_sq < min_dist_sq and dist_sq < FOOD_ATTRACT_RADIUS**2:
                min_dist_sq = dist_sq
                closest_food = food

        if closest_food:
            self.move_towards_target(closest_food["x"], closest_food["y"])
            return True # Indique qu'un mouvement vers la nourriture a été initié
        return False # Aucune nourriture ciblée

    def decide_and_move_towards_partner(self, all_agents_list):
        if self.is_paused or not self.is_fertile or self.is_pregnant:
            return False # Conditions non remplies pour chercher un partenaire

        closest_partner = None
        min_dist_sq = float('inf')

        for other_agent in all_agents_list:
            if other_agent.id == self.id: # Ne pas se cibler soi-même
                continue
            
            # Vérifier si l'autre agent est un partenaire potentiel
            if other_agent.is_fertile and not other_agent.is_pregnant:
                dx = other_agent.x - self.x
                dy = other_agent.y - self.y
                dist_sq = dx**2 + dy**2

                if dist_sq < REPRODUCTION_ATTRACT_RADIUS**2: # Si dans le rayon d'attraction pour la reproduction
                    if dist_sq < min_dist_sq: # Et si c'est le plus proche trouvé jusqu'à présent
                        min_dist_sq = dist_sq
                        closest_partner = other_agent
        
        if closest_partner:
            # print(f"Agent {self.id} se déplace vers partenaire potentiel {closest_partner.id}") # Debug
            self.move_towards_target(closest_partner.x, closest_partner.y)
            return True # Indique qu'un mouvement vers un partenaire a été initié
        return False # Aucun partenaire ciblé

    def move_randomly(self):
        # Mouvement aléatoire simple (utilisé comme fallback)
        self.x += random.randint(self.current_speed_range[0], self.current_speed_range[1])
        self.y += random.randint(self.current_speed_range[0], self.current_speed_range[1])
        self.rect.topleft = (self.x, self.y)
        self.rect.clamp_ip(screen.get_rect())
        self.x = self.rect.x
        self.y = self.rect.y
        # Mettre à jour le rect après le clamp
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def _find_closest_target(self, target_locations_list):
        if not target_locations_list:
            return None
        
        closest_target_coords = None
        min_dist_sq = float('inf')
        
        for target_pos in target_locations_list:
            dx = target_pos[0] - self.x
            dy = target_pos[1] - self.y
            dist_sq = dx**2 + dy**2
            
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_target_coords = target_pos
        return closest_target_coords


    def _find_closest_house_center(self, house_body_rects_list):
        if not house_body_rects_list:
            return None
        
        closest_house_center_coords = None
        min_dist_sq = float('inf')
        
        for house_rect in house_body_rects_list:
            house_center_x = house_rect.centerx
            house_center_y = house_rect.centery
            
            dx = house_center_x - self.x
            dy = house_center_y - self.y
            dist_sq = dx**2 + dy**2
            
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_house_center_coords = (house_center_x, house_center_y)
        return closest_house_center_coords

    def is_at_activity_location(self, target_activity_type, beach_rect, park_rects_list, cinema_locs_list, arcade_locs_list,
                                school_locations_list): # river_bank_areas_list removed
        if not self.activity_target_pos:
            return False

        if target_activity_type == "at_beach" and beach_rect:
            return beach_rect.collidepoint(self.rect.centerx, self.rect.centery)
        elif target_activity_type == "at_park" and park_rects_list:
            for park_rect in park_rects_list:
                if park_rect.collidepoint(self.rect.centerx, self.rect.centery):
                    return True
            return False
        # Pour les cibles ponctuelles (cinéma, salle de jeux, maison)
        elif target_activity_type in ["at_cinema", "at_arcade", "seeking_shelter", "sheltered", "at_school"]:
            dx = self.activity_target_pos[0] - self.rect.centerx
            dy = self.activity_target_pos[1] - self.rect.centery
            return (dx**2 + dy**2) < ACTIVITY_REACH_THRESHOLD**2
        return False

    def choose_new_leisure_activity(self, beach_rect, park_rects_list, cinema_locs_list, arcade_locs_list): # river_bank_areas_list removed
        possible_activities = []
        if beach_rect: possible_activities.append("at_beach")
        if park_rects_list: possible_activities.append("at_park")
        if cinema_locs_list: possible_activities.append("at_cinema")
        if arcade_locs_list: possible_activities.append("at_arcade")

        if not possible_activities:
            return

        chosen_activity_type = random.choice(possible_activities)
        self.current_activity = chosen_activity_type
        self.activity_end_time = pygame.time.get_ticks() + random.randint(MIN_LEISURE_DURATION_MS, MAX_LEISURE_DURATION_MS)

        if chosen_activity_type == "at_beach":
            # Choisir un point aléatoire sur la plage (partie sable sec)
            self.activity_target_pos = (random.randint(beach_rect.left, beach_rect.right),
                                        random.randint(beach_rect.top, beach_rect.bottom))
        elif chosen_activity_type == "at_park":
            target_park_rect = random.choice(park_rects_list)
            self.activity_target_pos = (random.randint(target_park_rect.left, target_park_rect.right),
                                        random.randint(target_park_rect.top, target_park_rect.bottom))
        elif chosen_activity_type == "at_cinema":
            self.activity_target_pos = random.choice(cinema_locs_list)
        elif chosen_activity_type == "at_arcade":
            self.activity_target_pos = random.choice(arcade_locs_list)
        
        print(f"Agent {self.id} a choisi l'activité: {self.current_activity} vers {self.activity_target_pos}")

    def perform_movement_decision(self, food_list, all_agents_list, is_thunderstorm_active, house_rects_list,
                                  beach_sand_rect, park_areas_list, cinema_locations_list, arcade_locations_list, school_locations_list): # river_bank_areas_list removed
        if self.is_paused:
            return
        
        current_time = pygame.time.get_ticks()

        # 1. GESTION DES ORAGES (PRIORITÉ MAXIMALE)
        if is_thunderstorm_active:
            agent_is_sheltered_now = is_agent_inside_house(self.rect) # Vérifie si l'agent est DANS une maison
            if not agent_is_sheltered_now:
                if self.current_activity != "seeking_shelter":
                    print(f"Agent {self.id} cherche un abri à cause de l'orage.")
                    self.current_activity = "seeking_shelter"
                    self.activity_target_pos = self._find_closest_house_center(house_rects_list)
                if self.activity_target_pos:
                    self.move_towards_target(self.activity_target_pos[0], self.activity_target_pos[1])
                else: # Pas de maison trouvée, mouvement aléatoire (panique)
                    self.move_randomly()
                return
            else: # Agent est à l'abri
                if self.current_activity != "sheltered":
                    print(f"Agent {self.id} est à l'abri.")
                    self.current_activity = "sheltered"
                    self.activity_target_pos = None # Reste sur place
                return # Reste à l'abri
        elif self.current_activity in ["seeking_shelter", "sheltered"]: # L'orage est terminé, l'agent peut sortir
            print(f"Agent {self.id} quitte l'abri / arrête de chercher, l'orage est fini.")
            self.current_activity = "idle"
            self.activity_target_pos = None
            self.time_to_next_leisure_decision = current_time # Peut décider d'une activité de loisir bientôt

        # 2. GESTION DE L'ÉCOLE POUR LES JEUNES AGENTS (PRIORITÉ APRÈS ORAGE)
        if self.is_newborn: # "is_newborn" signifie maintenant "est jeune / d'âge scolaire"
            if self.current_activity not in ["going_to_school", "at_school"]:
                # Si pas déjà en route ou à l'école, décider d'y aller
                closest_school_loc = self._find_closest_target(school_locations_list)
                if closest_school_loc:
                    print(f"Agent {self.id} (jeune) va à l'école.")
                    self.current_activity = "going_to_school"
                    self.activity_target_pos = closest_school_loc
                # S'il n'y a pas d'école, l'agent passera aux comportements suivants (faim, etc.)

            if self.current_activity == "going_to_school":
                if self.activity_target_pos:
                    # Utiliser "at_school" comme type pour la vérification de la localisation
                    if self.is_at_activity_location("at_school", beach_sand_rect, park_areas_list, cinema_locations_list, arcade_locations_list, school_locations_list):
                        print(f"Agent {self.id} (jeune) est arrivé à l'école.")
                        self.current_activity = "at_school"
                    else:
                        self.move_towards_target(self.activity_target_pos[0], self.activity_target_pos[1])
                return # Priorité à l'école
            
            elif self.current_activity == "at_school":
                # Reste à l'école. La sortie est gérée par update_size_status quand is_newborn devient False.
                return # Priorité à rester à l'école


        # 2. GESTION DE L'ACTIVITÉ DE LOISIR EN COURS
        leisure_activity_types = ["at_beach", "at_park", "at_cinema", "at_arcade"]
        if self.current_activity in leisure_activity_types:
            if current_time >= self.activity_end_time: # Fin de l'activité
                print(f"Agent {self.id} a terminé son activité: {self.current_activity}.")
                self.last_leisure_activity_finish_time = current_time
                self.current_activity = "idle"
                self.activity_target_pos = None
                self.time_to_next_leisure_decision = current_time + random.randint(MIN_TIME_BETWEEN_LEISURE_MS, MAX_TIME_BETWEEN_LEISURE_MS)
            else: # Activité en cours
                is_at_location = self.is_at_activity_location(self.current_activity, beach_sand_rect, park_areas_list, cinema_locations_list, arcade_locations_list, school_locations_list)
                if self.activity_target_pos and not is_at_location:
                    self.move_towards_target(self.activity_target_pos[0], self.activity_target_pos[1])
                # else: Arrivé à destination, reste sur place (ne fait rien d'autre ce tick)
                return

        # 3. SATISFACTION DES BESOINS (NOURRITURE, PARTENAIRE) - Si "idle"
        if self.current_activity == "idle":
            if self.decide_and_move_towards_food(food_list):
                # L'agent se déplace vers la nourriture. Pas besoin de changer current_activity ici,
                # car decide_and_move_towards_food est une action prioritaire si les conditions sont remplies.
                # Si l'agent mange, il reçoit un boost (géré ailleurs). Après avoir mangé, il redevient "idle".
                return
            if self.decide_and_move_towards_partner(all_agents_list):
                # Similaire à la nourriture.
                return

        # 4. CHOIX D'UNE NOUVELLE ACTIVITÉ DE LOISIR - Si "idle" et conditions remplies
        if self.current_activity == "idle" and \
           current_time >= self.time_to_next_leisure_decision and \
           current_time >= self.last_leisure_activity_finish_time + MIN_TIME_BETWEEN_LEISURE_MS: # Cooldown général entre loisirs
            
            if random.random() < LEISURE_ACTIVITY_PROBABILITY:
                self.choose_new_leisure_activity(beach_sand_rect, park_areas_list, cinema_locations_list, arcade_locs_list)
                # Si une activité a été choisie, self.current_activity n'est plus "idle"
                if self.current_activity != "idle" and self.activity_target_pos:
                    self.move_towards_target(self.activity_target_pos[0], self.activity_target_pos[1])
                    return
            else: # Pas envie de loisir ce coup-ci, reporter la décision
                self.time_to_next_leisure_decision = current_time + random.randint(MIN_TIME_BETWEEN_LEISURE_MS // 2, MAX_TIME_BETWEEN_LEISURE_MS // 2)


        # 5. MOUVEMENT ALÉATOIRE (FALLBACK) - Si "idle" et rien d'autre à faire
        if self.current_activity == "idle":
            self.move_randomly()

def draw_house(surface, x, y, width=50, height=40, roof_height=25, window_color=LIGHT_BLUE, door_color=DARK_BROWN):
    """Dessine une maison simple à la position (x, y)."""
    # Corps de la maison (rectangle)
    body_y_start = y + roof_height
    body_rect = pygame.Rect(x, body_y_start, width, height)
    pygame.draw.rect(surface, BROWN, body_rect)

    # Fenêtres (deux petits rectangles)
    window_width = width // 5  # Fenêtres plus petites en largeur
    window_height = height // 4 # Fenêtres plus petites en hauteur
    window_padding_x = width // 7 # Ajustement du padding horizontal
    window_padding_y = height // 5 # Garder un padding vertical raisonnable depuis le haut du corps

    pygame.draw.rect(surface, window_color, (x + window_padding_x, body_y_start + window_padding_y, window_width, window_height))
    pygame.draw.rect(surface, window_color, (x + width - window_padding_x - window_width, body_y_start + window_padding_y, window_width, window_height))

    # Porte (rectangle au centre en bas du corps)
    door_width = width // 3
    door_height = height // 2  # Porte plus basse (moitié de la hauteur du corps)
    door_x = x + (width - door_width) // 2
    door_y = body_y_start + height - door_height # Positionnée en bas
    pygame.draw.rect(surface, door_color, (door_x, door_y, door_width, door_height))

    # Toit de la maison (triangle)
    roof_points = [
        (x, y + roof_height),             # Point gauche du toit
        (x + width / 2, y),               # Sommet du toit
        (x + width, y + roof_height)      # Point droit du toit
    ]
    pygame.draw.polygon(surface, DARK_RED, roof_points)

def draw_cinema(surface, x, y, width=100, height=70, marquee_height=20, door_color=DARK_BROWN, text_color=BLACK):
    """Dessine un cinéma simple."""
    # Enseigne (Marquee)
    marquee_rect = pygame.Rect(x, y, width, marquee_height)
    pygame.draw.rect(surface, CINEMA_MARQUEE_YELLOW, marquee_rect)
    
    # Texte sur l'enseigne
    text_surface = SMALL_FONT.render("CINEMA", True, text_color)
    text_rect = text_surface.get_rect(center=marquee_rect.center)
    surface.blit(text_surface, text_rect)

    # Corps du cinéma
    body_y_start = y + marquee_height
    body_rect = pygame.Rect(x, body_y_start, width, height)
    pygame.draw.rect(surface, CINEMA_DARK_GREY, body_rect)

    # Porte
    door_width = width // 4
    door_height = height // 2
    door_x = x + (width - door_width) // 2
    door_y = body_y_start + height - door_height
    pygame.draw.rect(surface, door_color, (door_x, door_y, door_width, door_height))

def draw_arcade(surface, x, y, width=80, height=50, sign_height=15, door_color=DARK_BROWN, text_color=BLACK):
    """Dessine une salle de jeux simple."""
    # Enseigne
    sign_rect = pygame.Rect(x, y, width, sign_height)
    pygame.draw.rect(surface, ARCADE_NEON_GREEN, sign_rect)

    # Texte sur l'enseigne
    text_surface = SMALL_FONT.render("ARCADE", True, text_color)
    text_rect = text_surface.get_rect(center=sign_rect.center)
    surface.blit(text_surface, text_rect)

    # Corps de la salle de jeux
    body_y_start = y + sign_height
    body_rect = pygame.Rect(x, body_y_start, width, height)
    pygame.draw.rect(surface, ARCADE_PURPLE, body_rect)

    # "Fenêtres" ou lumières décoratives
    light_width = width // 6
    light_height = height // 3
    pygame.draw.rect(surface, ARCADE_NEON_PINK, (x + width // 5, body_y_start + height // 4, light_width, light_height))
    pygame.draw.rect(surface, ARCADE_NEON_PINK, (x + width - width // 5 - light_width, body_y_start + height // 4, light_width, light_height))

    # Porte
    door_width = width // 4
    door_height = height // 2
    door_x = x + (width - door_width) // 2
    door_y = body_y_start + height - door_height
    pygame.draw.rect(surface, DARK_BROWN, (door_x, door_y, door_width, door_height))

def draw_park(surface, x, y, width, height):
    """Dessine un parc simple avec de l'herbe et des arbres."""
    # Herbe
    pygame.draw.rect(surface, PARK_GRASS_GREEN, (x, y, width, height))

    # Dessiner quelques arbres simples
    tree_positions = [
        (x + width * 0.2, y + height * 0.5),
        (x + width * 0.5, y + height * 0.3),
        (x + width * 0.8, y + height * 0.6),
    ]
    trunk_width = 10
    trunk_height = 20
    leaves_radius = 15

    for tx, ty in tree_positions:
        # Tronc
        pygame.draw.rect(surface, TREE_TRUNK_BROWN, (tx - trunk_width // 2, ty - trunk_height // 2, trunk_width, trunk_height))
        # Feuilles
        pygame.draw.circle(surface, TREE_LEAVES_GREEN, (int(tx), int(ty - trunk_height // 2 - leaves_radius * 0.8)), leaves_radius)

def draw_school(surface, x, y, width=120, height=80, roof_h=30, door_color=SCHOOL_DOOR_COLOR, text_color=BLACK):
    """Dessine une école simple."""
    # Corps de l'école
    body_y_start = y + roof_h
    pygame.draw.rect(surface, SCHOOL_BUILDING_COLOR, (x, body_y_start, width, height))

    # Toit
    roof_points = [(x, body_y_start), (x + width / 2, y), (x + width, body_y_start)]
    pygame.draw.polygon(surface, SCHOOL_ROOF_COLOR, roof_points)

    # Porte
    door_w = width // 4
    door_h = height // 1.8
    door_x_pos = x + (width - door_w) // 2
    door_y_pos = body_y_start + height - door_h
    pygame.draw.rect(surface, door_color, (door_x_pos, door_y_pos, door_w, door_h))

    # Texte "ECOLE"
    text_surface = SMALL_FONT.render("ECOLE", True, text_color)
    text_rect = text_surface.get_rect(center=(x + width / 2, y + roof_h / 2.5)) # Sur le toit ou juste au-dessus du corps
    surface.blit(text_surface, text_rect)

def initialize_house_rects(specs_list):
    """Initialise HOUSE_BODY_RECTS à partir d'une liste de spécifications de bâtiments de type 'house'."""
    global HOUSE_BODY_RECTS
    HOUSE_BODY_RECTS = []
    for spec in specs_list:
        if spec.get("type") == "house": # On ne considère que les maisons comme abri pour l'instant
            body_y_start = spec["y"] + spec["roof_height"]
            body_rect = pygame.Rect(spec["x"], body_y_start, spec["width"], spec["height"])
            HOUSE_BODY_RECTS.append(body_rect)

def is_agent_inside_house(agent_rect):
    """Vérifie si le rectangle d'un agent est en collision avec un corps de maison."""
    for house_rect in HOUSE_BODY_RECTS:
        if agent_rect.colliderect(house_rect):
            return True
    return False

def draw_parasol(surface, x, y, radius=15, pole_height=25):
    """Dessine un parasol simple."""
    # Mât du parasol
    pygame.draw.line(surface, UMBRELLA_POLE, (x, y), (x, y + pole_height), 3)
    # Toile du parasol (demi-cercle ou polygone)
    # Utilisation d'un polygone pour un look plus "parasol"
    umbrella_points = [
        (x - radius, y),
        (x + radius, y),
        (x + radius * 0.7, y - radius * 0.5),
        (x, y - radius * 0.8),
        (x - radius * 0.7, y - radius * 0.5),
    ]
    pygame.draw.polygon(surface, UMBRELLA_RED, umbrella_points)
    pygame.draw.circle(surface, UMBRELLA_RED, (x,y), radius, draw_top_right=True, draw_top_left=True) # Alternative plus simple

def draw_lounge_chair(surface, x, y, width=30, height=10, back_height=15):
    """Dessine une chaise longue simple."""
    # Assise
    pygame.draw.rect(surface, LOUNGE_CHAIR_BLUE, (x, y, width, height))
    # Dossier (incliné)
    pygame.draw.line(surface, LOUNGE_CHAIR_BLUE, (x, y), (x - height // 2, y - back_height), 3)

# Création d'un agent
DEFAULT_IMG_PATH = os.path.join(ASSETS_DIR, 'homer.gif')
BOOST_IMG_PATH = os.path.join(ASSETS_DIR, 'homer_up.gif')

# Spécifications des bâtiments (pour le dessin et la détection d'abri pour les maisons)
BUILDINGS_SPECS = [
    {"type": "house", "x": 20, "y": 20, "width": 50, "height": 40, "roof_height": 25, "name": "Maison 1"},
    {"type": "house", "x": 90, "y": 20, "width": 60, "height": 50, "roof_height": 30, "name": "Maison 2"},
    {"type": "house", "x": 170, "y": 30, "width": 45, "height": 35, "roof_height": 20, "name": "Maison 3"},
    {"type": "house", "x": 30, "y": 90, "width": 55, "height": 45, "roof_height": 28, "name": "Maison 4"},
    {"type": "house", "x": 120, "y": 100, "width": 70, "height": 55, "roof_height": 35, "name": "Maison 5"},
    # Nouveaux bâtiments en bas à gauche
    # Parc (au-dessus du cinéma et de la salle de jeux)
    # Le cinéma est à y = SCREEN_HEIGHT - 110. Le parc sera au-dessus avec une marge de 10.
    # Nouvelle largeur: 230, Nouvelle hauteur: 200. y_parc = SCREEN_HEIGHT - 110 - 200 - 10 = SCREEN_HEIGHT - 320
    {"type": "park", "x": 30, "y": SCREEN_HEIGHT - 320, "width": 230, "height": 200, "name": "Grand Parc Central"},
    # y = SCREEN_HEIGHT - total_building_height - padding_bottom
    
    # Cinema: total height = 70 (body) + 20 (marquee) = 90. y = 600 - 90 - 20 = 490
    {"type": "cinema", "x": 30, "y": SCREEN_HEIGHT - 110, "width": 120, "height": 70, "marquee_height": 20, "name": "Le Grand Rex"},
    # Arcade: total height = 50 (body) + 15 (sign) = 65. y = 600 - 65 - 20 = 515
    {"type": "arcade", "x": 170, "y": SCREEN_HEIGHT - 85, "width": 100, "height": 50, "sign_height": 15, "name": "Pixel Palace"}, # Légèrement plus large
    # École en bas au centre/droite du parc
    # École: hauteur corps 80 + toit 30 = 110. y = SCREEN_HEIGHT - 110 - 20 = 470
    {"type": "school", "x": 280, "y": SCREEN_HEIGHT - 130, "width": 150, "height": 80, "roof_height":30, "name": "École Primaire"},
]

# Initialisation des zones d'activité (une seule fois)
PARK_AREAS_LIST = []
CINEMA_LOCATIONS_LIST = []
ARCADE_LOCATIONS_LIST = []
SCHOOL_LOCATIONS_LIST = []

def initialize_all_activity_zones_and_targets():
    global HOUSE_BODY_RECTS, PARK_AREAS_LIST, CINEMA_LOCATIONS_LIST, ARCADE_LOCATIONS_LIST, SCHOOL_LOCATIONS_LIST
    HOUSE_BODY_RECTS = [] # Réinitialiser au cas où
    PARK_AREAS_LIST = []
    CINEMA_LOCATIONS_LIST = []
    ARCADE_LOCATIONS_LIST = []
    SCHOOL_LOCATIONS_LIST = []

    for spec in BUILDINGS_SPECS:
        if spec["type"] == "house":
            body_y_start = spec["y"] + spec["roof_height"]
            HOUSE_BODY_RECTS.append(pygame.Rect(spec["x"], body_y_start, spec["width"], spec["height"]))
        elif spec["type"] == "park":
            PARK_AREAS_LIST.append(pygame.Rect(spec["x"], spec["y"], spec["width"], spec["height"]))
        elif spec["type"] == "cinema":
            CINEMA_LOCATIONS_LIST.append((spec["x"] + spec["width"] // 2, spec["y"] + spec.get("marquee_height",0) + spec["height"] // 2))
        elif spec["type"] == "arcade":
            ARCADE_LOCATIONS_LIST.append((spec["x"] + spec["width"] // 2, spec["y"] + spec.get("sign_height",0) + spec["height"] // 2))
        elif spec["type"] == "school":
            SCHOOL_LOCATIONS_LIST.append((spec["x"] + spec["width"] // 2, spec["y"] + spec.get("roof_height",0) + spec["height"] // 2))

initialize_all_activity_zones_and_targets()

# Initialiser la population
for _ in range(2): #
    # Commencer avec 2 agents
    start_x = random.randint(50, SCREEN_WIDTH - 50)
    start_y = random.randint(50, SCREEN_HEIGHT - 50)
    agent = Agent(start_x, start_y, DEFAULT_IMG_PATH, BOOST_IMG_PATH)
    agent.time_to_next_leisure_decision = pygame.time.get_ticks() + random.randint(MIN_TIME_BETWEEN_LEISURE_MS, MAX_TIME_BETWEEN_LEISURE_MS) # Échelonner la première décision
    ALL_AGENTS.append(agent)

def update_thunderstorm_status(current_time):
    """Gère le début et la fin des orages."""
    global IS_THUNDERSTORM_ACTIVE, LAST_THUNDERSTORM_CHECK_MS, THUNDERSTORM_END_TIME_MS

    if IS_THUNDERSTORM_ACTIVE:
        if current_time > THUNDERSTORM_END_TIME_MS:
            IS_THUNDERSTORM_ACTIVE = False
            print("L'orage est terminé.")
            # Optionnel: changer la couleur du fond pour revenir à la normale
            # screen.fill(BLACK) # Ou une autre couleur de fond normale
    else:
        if current_time - LAST_THUNDERSTORM_CHECK_MS > THUNDERSTORM_CHECK_INTERVAL_MS:
            LAST_THUNDERSTORM_CHECK_MS = current_time
            if random.random() < THUNDERSTORM_PROBABILITY_PER_CHECK:
                IS_THUNDERSTORM_ACTIVE = True
                duration = random.randint(MIN_THUNDERSTORM_DURATION_MS, MAX_THUNDERSTORM_DURATION_MS)
                THUNDERSTORM_END_TIME_MS = current_time + duration
                print(f"Un orage commence ! Durée: {duration / 1000.0}s.")
                # Optionnel: changer la couleur du fond pour l'orage
                # screen.fill((50, 50, 70)) # Gris foncé pour l'orage

# ... (le reste du code jusqu'à la boucle principale)

last_food_spawn_time_ms = 0
BEACH_SAND_RECT_GLOBAL = None # Sera défini dans la boucle de dessin
# Boucle principale de la simulation
running = True
while running:
    current_time_ticks = pygame.time.get_ticks()
    
    update_thunderstorm_status(current_time_ticks)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                clicked_on_agent = False
                for agent_obj in ALL_AGENTS:
                    if agent_obj.rect.collidepoint(event.pos):
                        agent_obj.activate_boost()
                        clicked_on_agent = True
                        break  # Un seul boost par clic
                if not clicked_on_agent:
                    # Ajout de nourriture si on ne clique pas sur un agent
                    FOOD_LIST.append({"x": event.pos[0], "y": event.pos[1]})

    current_tick_simulation_events = []
    agents_to_remove_ids_this_tick = []
    new_agents_born_this_tick = []

    # Mettre à jour chaque agent (mouvement, états, cycle de vie -> naissances/morts)
    for agent in ALL_AGENTS:
        agent.update_boost_status()
        agent.update_animation()
        agent.update_size_status(current_time_ticks) # Vérifier si l'agent doit grandir
        agent.update_pause_status()

        agent.perform_movement_decision(FOOD_LIST, ALL_AGENTS, IS_THUNDERSTORM_ACTIVE, HOUSE_BODY_RECTS,
                                          BEACH_SAND_RECT_GLOBAL, PARK_AREAS_LIST, CINEMA_LOCATIONS_LIST, ARCADE_LOCATIONS_LIST, SCHOOL_LOCATIONS_LIST)

        life_cycle_event = agent.update_life_cycle(current_time_ticks, len(ALL_AGENTS))
        if life_cycle_event:
            current_tick_simulation_events.append(life_cycle_event)

        # Logique de foudre pendant un orage
        if IS_THUNDERSTORM_ACTIVE and agent.id not in agents_to_remove_ids_this_tick:
            if not is_agent_inside_house(agent.rect):
                if random.random() < LIGHTNING_STRIKE_PROBABILITY_PER_AGENT_PER_TICK:
                    print(f"Agent {agent.id} a été frappé par la foudre et est mort !")
                    current_tick_simulation_events.append({"type": "death", "id": agent.id, "cause": "lightning"})
                    # Pas besoin d'ajouter à agents_to_remove_ids_this_tick ici, car l'événement "death" sera traité

    # Générer les événements de tentative de reproduction à partir des collisions
    for i in range(len(ALL_AGENTS)):
        for j in range(i + 1, len(ALL_AGENTS)):
            agent1 = ALL_AGENTS[i]
            agent2 = ALL_AGENTS[j]

            # S'assurer que les agents ne sont pas déjà marqués pour suppression ce tick
            if agent1.id in agents_to_remove_ids_this_tick or agent2.id in agents_to_remove_ids_this_tick:
                continue

            if agent1.rect.colliderect(agent2.rect):
                # print(f"DEBUG: Collision détectée entre {agent1.id} (fertile: {agent1.is_fertile}) et {agent2.id} (fertile: {agent2.is_fertile})")
                current_tick_simulation_events.append({
                    "type": "reproduction_check",
                    "agent1_id": agent1.id,
                    "agent2_id": agent2.id
                })

    # Traiter tous les événements de simulation accumulés pour ce tick
    for event_data in current_tick_simulation_events:
        if event_data["type"] == "birth":
            new_born_agent = Agent(event_data["x"], event_data["y"], DEFAULT_IMG_PATH, BOOST_IMG_PATH)
            new_agents_born_this_tick.append(new_born_agent)
        elif event_data["type"] == "death":
            # S'assurer de ne pas ajouter deux fois si déjà marqué (ex: mort par foudre puis par vieillesse dans le même tick)
            if event_data["id"] not in agents_to_remove_ids_this_tick:
                agents_to_remove_ids_this_tick.append(event_data["id"])
        elif event_data["type"] == "reproduction_check":
            agent1 = next((a for a in ALL_AGENTS if a.id == event_data["agent1_id"] and a.id not in agents_to_remove_ids_this_tick), None)
            agent2 = next((a for a in ALL_AGENTS if a.id == event_data["agent2_id"] and a.id not in agents_to_remove_ids_this_tick), None)
            if agent1 and agent2: # S'assurer que les deux agents existent toujours
                # La méthode attempt_reproduction gère les conditions internes (fertilité, gestation, cooldown)
                # et modifie directement l'état de l'agent (is_pregnant).
                # Les messages de debug dans attempt_reproduction sont toujours actifs.
                current_pop_approx = len(ALL_AGENTS) + len(new_agents_born_this_tick) - len(agents_to_remove_ids_this_tick)
                agent1.attempt_reproduction(agent2, current_time_ticks, current_pop_approx)

    # Appliquer les changements à la liste principale des agents
    ALL_AGENTS.extend(new_agents_born_this_tick)
    ALL_AGENTS = [agent for agent in ALL_AGENTS if agent.id not in agents_to_remove_ids_this_tick]

    if new_agents_born_this_tick:
        print(f"Nés ce tour: {len(new_agents_born_this_tick)}. Population actuelle: {len(ALL_AGENTS)}")
    if agents_to_remove_ids_this_tick:
        print(f"Morts ce tour: {len(agents_to_remove_ids_this_tick)}. Population actuelle: {len(ALL_AGENTS)}")

    # Vérifier si tous les agents sont morts
    if not ALL_AGENTS:
        print("Tous les agents sont morts. Fin de la simulation.")
        running = False # Arrêter la boucle principale du jeu

    # Spawn de nourriture aléatoire
    if current_time_ticks - last_food_spawn_time_ms > FOOD_SPAWN_INTERVAL_MS:
        food_x = random.randint(FOOD_RADIUS, SCREEN_WIDTH - FOOD_RADIUS)
        food_y = random.randint(FOOD_RADIUS, SCREEN_HEIGHT - FOOD_RADIUS)
        FOOD_LIST.append({"x": food_x, "y": food_y})
        last_food_spawn_time_ms = current_time_ticks
        print(f"Nourriture apparue à ({food_x}, {food_y})")

    # Vérifier la consommation de nourriture
    food_consumed_indices = []
    for agent in ALL_AGENTS:
        for i, food_item in enumerate(FOOD_LIST):
            if i in food_consumed_indices: # Déjà marquée pour suppression
                continue
            food_rect = pygame.Rect(food_item["x"] - FOOD_RADIUS, food_item["y"] - FOOD_RADIUS, FOOD_RADIUS * 2, FOOD_RADIUS * 2)
            if agent.rect.colliderect(food_rect):
                food_consumed_indices.append(i)
                agent.activate_boost() # Activer le boost lorsque la nourriture est consommée
                print(f"Agent {agent.id} a mangé et a reçu un boost!")
    # Supprimer la nourriture consommée (en ordre inverse pour éviter les problèmes d'indice)
    for i in sorted(food_consumed_indices, reverse=True):
        del FOOD_LIST[i]

    # Dessiner
    if IS_THUNDERSTORM_ACTIVE:
        screen.fill((40, 40, 60)) # Fond plus sombre pendant l'orage
        if random.random() < 0.02 : # Chance de flash de foudre
            pygame.draw.rect(screen, WHITE, (0,0,SCREEN_WIDTH, SCREEN_HEIGHT)) # Flash blanc rapide
    else:
        screen.fill(BLACK)  # Fond noir normal

    # Dessiner la plage et l'eau sur le côté droit
    beach_total_width = 150  # Largeur totale de la plage (réduite)
    water_area_width = 80   # Largeur de la zone d'eau (réduite)
    wet_sand_strip_thickness = 15 # Épaisseur de la bande de sable humide

    dry_sand_width = beach_total_width - wet_sand_strip_thickness
    
    beach_area_start_x = SCREEN_WIDTH - beach_total_width - water_area_width
    
    # Définir et dessiner le sable sec (c'est la zone de la plage pour les agents)
    current_beach_sand_rect = pygame.Rect(beach_area_start_x, 0, dry_sand_width, SCREEN_HEIGHT)
    pygame.draw.rect(screen, SAND_COLOR, current_beach_sand_rect)
    BEACH_SAND_RECT_GLOBAL = current_beach_sand_rect # Mettre à jour la variable globale
    
    # Dessiner la bande de sable humide (décoratif)
    wet_sand_start_x = beach_area_start_x + dry_sand_width
    pygame.draw.rect(screen, WET_SAND_COLOR, (wet_sand_start_x, 0, wet_sand_strip_thickness, SCREEN_HEIGHT))
    
    # Dessiner l'eau
    water_start_x = wet_sand_start_x + wet_sand_strip_thickness
    pygame.draw.rect(screen, WATER_BLUE, (water_start_x, 0, water_area_width, SCREEN_HEIGHT))

    # Dessiner des éléments de plage
    draw_parasol(screen, beach_area_start_x + 25, 100) # Ajusté pour la nouvelle largeur
    draw_lounge_chair(screen, beach_area_start_x + 10, 130) # Ajusté

    draw_parasol(screen, beach_area_start_x + 90, 250, radius=20) # Ajusté
    draw_lounge_chair(screen, beach_area_start_x + 75, 280, width=35) # Ajusté

    # Dessiner tous les bâtiments
    for spec in BUILDINGS_SPECS:
        if spec["type"] == "house":
            draw_house(screen, spec["x"], spec["y"], spec["width"], spec["height"], spec["roof_height"])
        elif spec["type"] == "cinema":
            draw_cinema(screen, spec["x"], spec["y"], spec["width"], spec["height"], spec["marquee_height"])
        elif spec["type"] == "arcade":
            draw_arcade(screen, spec["x"], spec["y"], spec["width"], spec["height"], spec["sign_height"])
        elif spec["type"] == "park":
            draw_park(screen, spec["x"], spec["y"], spec["width"], spec["height"])
        elif spec["type"] == "school":
            draw_school(screen, spec["x"], spec["y"], spec["width"], spec["height"], spec["roof_height"])


    for food in FOOD_LIST: # Dessiner la nourriture
        pygame.draw.circle(screen, ORANGE, (food["x"], food["y"]), FOOD_RADIUS)
    for agent in ALL_AGENTS: # Dessiner les agents
        agent.draw(screen)

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Contrôler la vitesse de la simulation (FPS)
    clock.tick(30)

pygame.quit()