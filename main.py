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

# Configuration de l'écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

# Horloge pour contrôler le FPS
clock = pygame.time.Clock()

# Chemin vers le dossier des assets
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# Constante pour la taille de l'image de l'agent
AGENT_TARGET_HEIGHT_PIXELS = 50 # Définissez ici la hauteur souhaitée en pixels

# Constantes pour la simulation de vie
GESTATION_DURATION_MS = 30000  # 30 secondes
MIN_FERTILITY_AGE_MS = 15000   # Devient fertile à 15 secondes
MAX_AGE_MS = 90000             # Durée de vie de 90 secondes (peut être ajusté)
REPRODUCTION_COOLDOWN_MS = 10000 # 10 secondes de repos après naissance/tentative
TARGET_POPULATION = 10
BASE_CONCEPTION_PROBABILITY = 0.5 # Chance de base de concevoir lors d'une rencontre fertile

ALL_AGENTS = [] # Liste globale pour que les agents puissent interagir

FOOD_RADIUS = 7
FOOD_ATTRACT_RADIUS = 200  # Distance max d'attraction
FOOD_LIST = []

FOOD_SPAWN_INTERVAL_MS = 30000 # 30 secondes
last_food_spawn_time_ms = 0

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
        self.pause_probability = 0.2 # 20% de chance de faire une pause lors d'un check

        self.is_fertile = False
        self.is_pregnant = False
        self.gestation_start_ms = 0
        self.last_reproduction_attempt_ms = 0

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
        self.y += random.randint(self.current_speed_range[0], self.current_speed_range[1])

        # Garder l'agent dans les limites de l'écran en utilisant le rect
        # Mettre à jour le rectangle baséon les nouvelles coordonnées
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
            else:
                # print(f"DEBUG: Échec du jet de probabilité pour repro entre {self.id} et {partner.id} (Prob: {conception_probability:.2f})")
        return False

    def update_animation(self):
        if not self.current_frames or len(self.current_frames) <= 1:
            return # Pas d'animation si pas de frames ou une seule frame
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_last_update > self.animation_frame_duration:
            self.animation_last_update = current_time
            self.current_frame_index = (self.current_frame_index + 1) % len(self.current_frames)
            self.image = self.current_frames[self.current_frame_index]

    def move_towards_food(self, food_list):
        if not food_list or self.is_paused:
            return

        # Chercher la nourriture la plus proche
        closest_food = None
        min_dist = float('inf')
        for food in food_list:
            dx = food["x"] - self.x
            dy = food["y"] - self.y
            dist = (dx**2 + dy**2) ** 0.5
            if dist < min_dist and dist < FOOD_ATTRACT_RADIUS:
                min_dist = dist
                closest_food = food

        if closest_food:
            # Déplacement simple vers la nourriture
            dx = closest_food["x"] - self.x
            dy = closest_food["y"] - self.y
            dist = (dx**2 + dy**2) ** 0.5
            if dist > 1:
                speed = max(abs(self.current_speed_range[0]), abs(self.current_speed_range[1]))
                self.x += int(round(dx / dist * speed))
                self.y += int(round(dy / dist * speed))
                self.rect.topleft = (self.x, self.y)
                self.rect.clamp_ip(screen.get_rect())
                self.x = self.rect.x
                self.y = self.rect.y

# Création d'un agent
DEFAULT_IMG_PATH = os.path.join(ASSETS_DIR, 'homer.gif')
BOOST_IMG_PATH = os.path.join(ASSETS_DIR, 'homer_up.gif')

# Initialiser la population
for _ in range(2): # Commencer avec 2 agents
    start_x = random.randint(50, SCREEN_WIDTH - 50)
    start_y = random.randint(50, SCREEN_HEIGHT - 50)
    agent = Agent(start_x, start_y, DEFAULT_IMG_PATH, BOOST_IMG_PATH)
    ALL_AGENTS.append(agent)

# Boucle principale de la simulation
running = True
while running:
    global last_food_spawn_time_ms # Rendre la variable globale accessible
    current_time_ticks = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        # Renommé 'event' en 'pygame_event' pour éviter confusion avec les événements de simulation
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
        agent.update_pause_status()

        if FOOD_LIST:
            agent.move_towards_food(FOOD_LIST)
        else:
            agent.move_randomly()
        
        life_cycle_event = agent.update_life_cycle(current_time_ticks, len(ALL_AGENTS))
        if life_cycle_event:
            current_tick_simulation_events.append(life_cycle_event)

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
                # Ici, on pourrait ajouter un effet à l'agent (ex: gain d'énergie)
    # Supprimer la nourriture consommée (en ordre inverse pour éviter les problèmes d'indice)
    for i in sorted(food_consumed_indices, reverse=True):
        del FOOD_LIST[i]

    # Dessiner
    screen.fill(BLACK)  # Fond noir
    for food in FOOD_LIST: # Dessiner la nourriture
        pygame.draw.circle(screen, ORANGE, (food["x"], food["y"]), FOOD_RADIUS)
    for agent in ALL_AGENTS: # Dessiner les agents
        agent.draw(screen)

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Contrôler la vitesse de la simulation (FPS)
    clock.tick(30)

pygame.quit()