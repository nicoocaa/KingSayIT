import pygame

class Skeleton:
    def __init__(self, x, y):
        # Charger les animations du squelette
        self.idle_sprites = [pygame.image.load(f"../assets/images/skeleton/idle/Skeleton_0{i}_White_Idle.png") for i in range(8)]
        self.walk_sprites = [pygame.image.load(f"../assets/images/skeleton/walk/Skeleton_0{i}_White_Walk.png") for i in range(8)]
        self.walk_back_sprites = [pygame.image.load(f"../assets/images/skeleton/walk/back/Skeleton_0{i}_White_Walk.png") for i in range(8)]
        self.die_sprites = [pygame.image.load(f"../assets/images/skeleton/die/Skeleton_0{i}_White_Die.png") for i in range(11)]
        self.attack_sprites = [pygame.image.load(f"../assets/images/skeleton/attaque/Skeleton_0{i}_White_Attack1.png") for i in range(8)]
        
        # Redimensionner les images
        size = (150, 250)
        self.idle_sprites = [pygame.transform.scale(img, size) for img in self.idle_sprites]
        self.walk_sprites = [pygame.transform.scale(img, size) for img in self.walk_sprites]
        self.walk_back_sprites = [pygame.transform.scale(img, size) for img in self.walk_back_sprites]
        self.die_sprites = [pygame.transform.scale(img, size) for img in self.die_sprites]
        self.attack_sprites = [pygame.transform.scale(img, size) for img in self.attack_sprites]
        
        # Position et état
        self.x = x
        self.y = y
        self.speed = 2
        self.current_frame = 0
        self.frame_timer = 0
        self.animation_speed = 0.1
        self.death_animation_speed = 0.3
        self.attack_animation_speed = 0.15
        self.direction = "right"
        self.is_moving = False
        self.is_dying = False
        self.is_attacking = False
        self.attack_cooldown = 1.0  # Temps entre chaque attaque
        self.last_attack_time = 0
        
        # Ajouter une hitbox pour le squelette
        self.hitbox = pygame.Rect(x + 50, y + 50, 50, 150)
        self.attack_hitbox = pygame.Rect(x + 50, y + 50, 100, 150)  # Hitbox pour l'attaque
        self.is_alive = True
        
    def update(self, delta_time, player_x):
        if not self.is_alive and not self.is_dying:
            return
            
        current_time = pygame.time.get_ticks() / 1000
        
        # Mettre à jour les hitboxes
        self.hitbox.x = self.x + 50
        self.hitbox.y = self.y + 50
        
        if self.direction == "right":
            self.attack_hitbox.x = self.x + 100
        else:
            self.attack_hitbox.x = self.x - 50
        self.attack_hitbox.y = self.y + 50
        
        # Mettre à jour l'animation
        self.frame_timer += delta_time
        
        # Choisir la bonne vitesse d'animation
        if self.is_dying:
            current_animation_speed = self.death_animation_speed
        elif self.is_attacking:
            current_animation_speed = self.attack_animation_speed
        else:
            current_animation_speed = self.animation_speed
        
        if self.frame_timer >= current_animation_speed:
            self.frame_timer = 0
            
            if self.is_dying:
                if self.current_frame < len(self.die_sprites) - 1:
                    self.current_frame += 1
                else:
                    self.is_alive = False
                    self.is_dying = False
                return
            elif self.is_attacking:
                if self.current_frame < len(self.attack_sprites) - 1:
                    self.current_frame += 1
                else:
                    self.current_frame = 0
                    self.is_attacking = False
                return
                
            # Animation normale
            if self.is_moving:
                self.current_frame = (self.current_frame + 1) % len(self.walk_sprites)
            else:
                self.current_frame = (self.current_frame + 1) % len(self.idle_sprites)
        
        # Ne pas bouger si en train de mourir ou d'attaquer
        if self.is_dying or self.is_attacking:
            return
            
        # Logique de mouvement et d'attaque
        distance_to_player = player_x - self.x
        abs_distance = abs(distance_to_player)
        
        # Mettre à jour la direction
        if distance_to_player > 0:
            self.direction = "right"
        else:
            self.direction = "left"
            
        # Décider si on attaque ou on bouge
        if abs_distance < 100 and current_time - self.last_attack_time > self.attack_cooldown:  # Distance d'attaque
            self.is_attacking = True
            self.is_moving = False
            self.current_frame = 0
            self.last_attack_time = current_time
        elif abs_distance > 10:  # Distance de mouvement
            self.is_moving = True
            if distance_to_player > 0:
                self.x += self.speed
            else:
                self.x -= self.speed
        else:
            self.is_moving = False
    
    def draw(self, screen, camera=None):
        if not self.is_alive and not self.is_dying:
            return
            
        # Calculer la position avec le décalage de la caméra si elle existe
        draw_x = self.x
        draw_y = self.y
        if camera:
            camera_adjusted_rect = camera.apply(pygame.Rect(self.x, self.y, 1, 1))
            draw_x = camera_adjusted_rect.x
            draw_y = camera_adjusted_rect.y
            
        if self.is_dying:
            screen.blit(self.die_sprites[self.current_frame], (draw_x, draw_y))
        elif self.is_attacking:
            screen.blit(self.attack_sprites[self.current_frame], (draw_x, draw_y))
        elif self.is_moving:
            if self.direction == "right":
                screen.blit(self.walk_sprites[self.current_frame], (draw_x, draw_y))
            else:
                screen.blit(self.walk_back_sprites[self.current_frame], (draw_x, draw_y))
        else:
            screen.blit(self.idle_sprites[self.current_frame], (draw_x, draw_y)) 
    
    def start_death(self):
        """Démarre l'animation de mort du squelette"""
        self.is_dying = True
        self.is_attacking = False  # Arrêter l'attaque si en cours
        self.is_moving = False    # Arrêter le mouvement
        self.current_frame = 0    # Réinitialiser l'animation 
    
    def check_player_collision(self, player):
        if self.is_attacking and not player.invincible:
            if self.attack_hitbox.colliderect(player.hitbox):
                player.take_damage()
                return True
        return False 