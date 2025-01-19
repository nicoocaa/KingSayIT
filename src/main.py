import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from player import Player
from enemy import Skeleton

pygame.init()

# Initialiser le mixer de Pygame
pygame.mixer.init()

# Charger la musique de fond
pygame.mixer.music.load("../assets/Sounds/fond.mp3")  # Remplacez par le nom de votre fichier MP3
pygame.mixer.music.set_volume(5)  # Ajustez cette valeur selon vos préférences
pygame.mixer.music.play(-1)  # Jouer la musique en boucle

# Charger le son de mort
death_sound = pygame.mixer.Sound("../assets/Sounds/morts.mp3")  # Remplacez par le nom de votre fichier audio

# Charger le son de dégâts
damage_sound = pygame.mixer.Sound("../assets/Sounds/dégâts.mp3")  # Remplacez par le nom de votre fichier audio

# Charger le son d'attaque
attack_sound = pygame.mixer.Sound("../assets/Sounds/attaque.mp3")  # Remplacez par le nom de votre fichier audio

# Configurations de base
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Configuration des textes
font = pygame.font.Font(None, 74)
death_text = font.render('YOU DIED', True, (255, 0, 0))
death_text_rect = death_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

# Charger et configurer le bouton Start
game_button_img = pygame.image.load("../assets/images/GameButton.png")
game_button_img = pygame.transform.scale(game_button_img, (200, 80))
game_button = game_button_img.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100))

start_button_img = pygame.image.load("../assets/images/TutoButton.png")
start_button_img = pygame.transform.scale(start_button_img, (200, 80))
start_button = start_button_img.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

# Charger et configurer le bouton New Game
new_game_button_img = pygame.image.load("../assets/images/GameButton.png")
new_game_button_img = pygame.transform.scale(new_game_button_img, (200, 80))
new_game_button = new_game_button_img.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100))

def spawn_skeleton():
    side = random.choice(["left", "right"])
    if side == "left":
        x = -100
    else:
        x = SCREEN_WIDTH + 100
    return Skeleton(x, scaled_height - 350)

# Charger l'image de fond et la nouvelle carte
background = pygame.image.load("../assets/images/background.png").convert()
main_game_map = pygame.image.load("../assets/images/mainGame.png").convert()

# Redimensionner la carte pour la rendre plus grande (3.5x la taille originale)
MAP_SCALE = 3.5
scaled_width = int(main_game_map.get_width() * MAP_SCALE)
scaled_height = int(main_game_map.get_height() * MAP_SCALE)
main_game_map = pygame.transform.scale(main_game_map, (scaled_width, scaled_height))

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity_rect):
        return entity_rect.move(self.camera.topleft)

    def update(self, target_rect):
        x = -target_rect.centerx + SCREEN_WIDTH // 2
        y = -target_rect.centery + SCREEN_HEIGHT // 2 - 200

        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - SCREEN_WIDTH), x)
        y = max(-(self.height - SCREEN_HEIGHT), y)

        self.camera = pygame.Rect(x, y, self.width, self.height)

# Créer le héros pour le menu
menu_player = Player(100, SCREEN_HEIGHT // 2 - 75, death_sound, damage_sound, attack_sound)

class Pit:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 0, 0)  # Couleur noire pour le trou

    def draw(self, screen, camera):
        # Dessiner le trou avec le décalage de la caméra
        pit_rect = camera.apply(self.rect)
        pygame.draw.rect(screen, self.color, pit_rect)

    def check_collision(self, player):
        # Vérifier si le joueur tombe dans le trou
        return self.rect.colliderect(player.hitbox)

def tutorial_loop():
    # Charger l'image du King et de la zone de texte
    king_img = pygame.image.load("../assets/images/king.png")
    king_img = pygame.transform.scale(king_img, (300, 400))
    king_rect = king_img.get_rect(center=(SCREEN_WIDTH/2 - 200, SCREEN_HEIGHT/2))
    
    text_zone_img = pygame.image.load("../assets/images/TexteZone.png")
    text_zone_img = pygame.transform.scale(text_zone_img, (SCREEN_WIDTH - 100, 150))
    text_zone_rect = text_zone_img.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 100))

    # Texte du dialogue
    dialogue_font = pygame.font.Font(None, 25)
    dialogues = [
        ["Héros, je te remercie d'avoir répondu à mon appel…",
         "Mon royaume est plongé dans les ténèbres."],
        ["Une maladie, inconnue et cruelle, s'est abattue sur nos terres.",
         "Elle n'épargne personne. Les villageois, mes soldats, mes conseillers…"],
        ["Tous sont tombés, mais leur repos éternel leur a été refusé.",
         "Leur chair a pourri, et leurs âmes sont prisonnières de corps squelettiques."],
        ["Ils ne sont plus eux-mêmes, Héros.",
         "Ce ne sont plus que des monstres, des pantins assoiffés de destruction."],
        ["Nos villages brûlent, nos récoltes pourrissent.",
         "Mon royaume tout entier s'effondre…"],
        ["Toi seul peux briser cette malédiction.",
         "Retrouve l'origine de ce fléau et détruis-le, quel qu'en soit le prix."],
        ["Je ne peux t'offrir qu'un maigre soutien :",
         "Une épée digne des plus grands chevaliers et ma bénédiction."],
        ["Mais, Héros… sache que les ténèbres sont profondes,",
         "Et que tu ne pourras faire confiance à personne."],
        ["Pars maintenant, et que les dieux veillent sur toi."]
    ]

    current_dialogue = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and current_dialogue < len(dialogues) - 1:
                    current_dialogue += 1
                elif event.key == pygame.K_SPACE and current_dialogue == len(dialogues) - 1:
                    return True

        screen.blit(background, (0, 0))
        screen.blit(king_img, king_rect)
        screen.blit(text_zone_img, text_zone_rect)
        
        for i, line in enumerate(dialogues[current_dialogue]):
            text_surface = dialogue_font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 130 + i * 40))
            screen.blit(text_surface, text_rect)

        if current_dialogue < len(dialogues) - 1:
            continue_text = dialogue_font.render("Appuyez sur ENTRÉE pour continuer...", True, (0, 0, 0))
        else:
            continue_text = dialogue_font.render("Appuyez sur ESPACE pour commencer...", True, (0, 0, 0))
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH/2, text_zone_rect.bottom - 25))
        screen.blit(continue_text, continue_rect)

        pygame.display.update()
        clock.tick(FPS)

    return True

def spawn_skeletons(skeletons, wave):
    nbsquelettes = wave * 2  # Nombre de squelettes à générer
    print(f"Spawning {nbsquelettes} skeletons for wave {wave}")  # Message de débogage
    for _ in range(nbsquelettes):
        skeletons.append(spawn_skeleton())
    print(f"Spawned {nbsquelettes} skeletons")  # Message de débogage

def game_loop():
    player = Player(100, scaled_height - 350, death_sound, damage_sound, attack_sound)
    death_timer = 0
    death_delay = 5
    camera = Camera(scaled_width, scaled_height)

    skeletons = []  # Liste pour stocker les squelettes
    current_wave = 1  # Vague actuelle
    spawn_skeletons(skeletons, current_wave)  # Appeler la fonction pour faire apparaître les squelettes

    # Variables pour le tutoriel de contrôle
    tutorial_phase = 1  # Phase 1: déplacement, Phase 2: saut
    show_controls = True
    control_start_time = pygame.time.get_ticks()
    control_duration = 5000  # 5 secondes
    text_zone_img = pygame.image.load("../assets/images/TexteZone.png")
    text_zone_img = pygame.transform.scale(text_zone_img, (400, 100))
    has_moved = False  # Pour détecter si le joueur s'est déplacé
    has_jumped = False  # Pour détecter si le joueur a sauté

    # Créer un trou pour la phase de saut
    pit = Pit(500, scaled_height - 122, 200, 200)  # Position correcte du trou

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        delta_time = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        keys = pygame.key.get_pressed()

        # Détecter si le joueur se déplace
        if keys[pygame.K_q] or keys[pygame.K_d]:
            has_moved = True

        # Détecter si le joueur saute
        if keys[pygame.K_z]:
            has_jumped = True

        player.move(keys, delta_time)
        camera.update(player.hitbox)

        # Dessiner la carte et appliquer le scrolling
        map_rect = main_game_map.get_rect()
        screen.blit(main_game_map, camera.apply(map_rect))

        # Dessiner le trou pendant la phase 2 du tutoriel
        if tutorial_phase == 2:
            pit.draw(screen, camera)

        # Dessiner le joueur
        player.draw(screen, camera)

        # Gérer le tutoriel de contrôle
        if show_controls:
            if tutorial_phase == 1:
                if not has_moved:
                    # Afficher les instructions de déplacement
                    text_rect = text_zone_img.get_rect(center=(player.x + 100, player.y - 100))
                    screen.blit(text_zone_img, camera.apply(text_rect))
                    controls_font = pygame.font.Font(None, 32)
                    controls_text = controls_font.render("Q pour reculer, D pour avancer", True, (0, 0, 0))
                    text_pos = camera.apply(pygame.Rect(player.x - 50, player.y - 110, 0, 0))
                    screen.blit(controls_text, text_pos)
                else:
                    tutorial_phase = 2
                    control_start_time = pygame.time.get_ticks()

            elif tutorial_phase == 2:
                if not has_jumped:
                    # Afficher les instructions de saut
                    text_rect = text_zone_img.get_rect(center=(player.x + 100, player.y - 100))
                    screen.blit(text_zone_img, camera.apply(text_rect))
                    controls_font = pygame.font.Font(None, 32)
                    controls_text = controls_font.render("Appuyez sur Z pour sauter", True,
                                                         (0, 0, 0))
                    text_pos = camera.apply(pygame.Rect(player.x - 50, player.y - 110, 0, 0))
                    screen.blit(controls_text, text_pos)

                    # Vérifier si le joueur tombe dans le trou
                    if pit.check_collision(player):
                        print("Le héros est tombé dans le trou !")  # Message dans le terminal
                        if not player.is_fall_death:
                            player.start_fall_death()

                    # Vérifier si le joueur est tombé hors de l'écran
                    if player.y > scaled_height + 500:  # Distance de chute
                        player.x = 300  # Position de départ
                        player.y = scaled_height - 350
                        player.reset_state()

                    # Mettre à jour la hitbox du joueur
                    player.hitbox.x = player.x + 100
                    player.hitbox.y = player.y + 50
                else:
                    show_controls = False
                    skeletons.append(spawn_skeleton())

        # Vérifier si tous les squelettes de la vague actuelle sont morts
        if all(not skeleton.is_alive for skeleton in skeletons):
            current_wave += 1  # Passer à la vague suivante
            print(f"Vague {current_wave} apparaît !")  # Imprimer le message dans le terminal
            spawn_skeletons(skeletons, current_wave)  # Faire apparaître les squelettes de la nouvelle vague

        # Dessiner tous les squelettes
        for skeleton in skeletons:
            if skeleton.is_alive:
                player.check_attack_collision(skeleton)
                skeleton.check_player_collision(player)
                skeleton.update(delta_time, player.x)
                skeleton.draw(screen, camera)

        if player.death_animation_complete:
            death_timer += delta_time
            if death_timer >= death_delay:
                running = False
            dark_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            dark_surface.fill((0, 0, 0))
            dark_surface.set_alpha(128)
            screen.blit(dark_surface, (0, 0))
            screen.blit(death_text, death_text_rect)

        pygame.display.update()

    return True

def menu_loop():
    menu_frame_timer = 0
    menu_current_frame = 0

    while True:
        delta_time = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button.collidepoint(mouse_pos):
                    # Lancer le tutoriel d'abord
                    if tutorial_loop() == False:
                        return False
                    # Puis lancer le jeu
                    if game_loop() == False:
                        return False
                elif new_game_button.collidepoint(mouse_pos):  # Vérifiez si le bouton New Game est cliqué
                    # Lancer le jeu directement
                    if game_loop() == False:
                        return False

        # Animation du héros en idle dans le menu
        menu_frame_timer += delta_time
        if menu_frame_timer >= 0.2:
            menu_frame_timer = 0
            menu_current_frame = (menu_current_frame + 1) % len(menu_player.idle_image)
            

        # Effet de survol des boutons
        mouse_pos = pygame.mouse.get_pos()
        tuto_scale_factor = 1.1 if start_button.collidepoint(mouse_pos) else 1.0
        game_scale_factor = 1.1 if game_button.collidepoint(mouse_pos) else 1.0

        # Calculer la nouvelle taille du bouton Tuto pour l'effet de survol
        current_tuto_button_img = pygame.transform.scale(
            start_button_img,
            (int(200 * tuto_scale_factor), int(80 * tuto_scale_factor))
        )
        current_tuto_button_rect = current_tuto_button_img.get_rect(center=start_button.center)

        # Calculer la nouvelle taille du bouton Game pour l'effet de survol
        current_game_button_img = pygame.transform.scale(
            game_button_img,
            (int(200 * game_scale_factor), int(80 * game_scale_factor))
        )
        current_game_button_rect = current_game_button_img.get_rect(center=game_button.center)

        # Dessin du menu
        screen.blit(background, (0, 0))
        screen.blit(menu_player.idle_image[menu_current_frame], (menu_player.x, menu_player.y))
        screen.blit(current_game_button_img, current_game_button_rect)
        screen.blit(current_tuto_button_img, current_tuto_button_rect)

        pygame.display.update()

# Lancer le menu principal
menu_loop()
pygame.quit()
