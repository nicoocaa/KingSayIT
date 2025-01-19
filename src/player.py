import pygame

class Player:
    def __init__(self, x, y, death_sound, damage_sound, attack_sound):
        # Charger les images d'animation pour chaque direction
        self.idle_image = [pygame.image.load(f"../assets/images/player/idle/HeroKnight_Idle_{i}.png") for i in range(7)] # Image au repos
        self.walk_right = [pygame.image.load(f"../assets/images/player/run/HeroKnight_Run_{i}.png") for i in range(10)]
        self.walk_left = [pygame.image.load(f"../assets/images/player/run/back/HeroKnight_Run_{i}.png") for i in range(10)]
        self.jump_image = [pygame.image.load(f"../assets/images/player/jump/HeroKnight_Jump_{i}.png") for i in range(3)] # Image pour le saut
        self.fall_image = [pygame.image.load(f"../assets/images/player/fall/HeroKnight_Fall_{i}.png") for i in range(3)]  # Nouvelle animation
        
        # Charger les trois types d'attaques
        self.attack1_sprites = [pygame.image.load(f"../assets/images/player/Attack1/HeroKnight_Attack1_{i}.png") for i in range(6)]
        self.attack2_sprites = [pygame.image.load(f"../assets/images/player/Attack2/HeroKnight_Attack2_{i}.png") for i in range(5)]
        self.attack3_sprites = [pygame.image.load(f"../assets/images/player/Attack3/HeroKnight_Attack3_{i}.png") for i in range(8)]
        
        # Redimensionner toutes les images
        size = (350, 250)
        self.idle_image = [pygame.transform.scale(img, size) for img in self.idle_image]
        self.walk_left = [pygame.transform.scale(img, size) for img in self.walk_left]
        self.walk_right = [pygame.transform.scale(img, size) for img in self.walk_right]
        self.jump_image = [pygame.transform.scale(img, size) for img in self.jump_image]
        self.fall_image = [pygame.transform.scale(img, size) for img in self.fall_image]  # Redimensionner les images de chute
        self.attack1_sprites = [pygame.transform.scale(img, size) for img in self.attack1_sprites]
        self.attack2_sprites = [pygame.transform.scale(img, size) for img in self.attack2_sprites]
        self.attack3_sprites = [pygame.transform.scale(img, size) for img in self.attack3_sprites]

        # Ajouter l'animation de blessure
        self.hurt_sprites = [pygame.image.load(f"../assets/images/player/Hurt/HeroKnight_Hurt_{i}.png") for i in range(2)]
        self.hurt_sprites = [pygame.transform.scale(img, (350, 250)) for img in self.hurt_sprites]

        # Ajouter l'animation de mort
        self.die_sprites = [pygame.image.load(f"../assets/images/player/Death/HeroKnight_Death_{i}.png") for i in range(10)]
        self.die_sprites = [pygame.transform.scale(img, (350, 250)) for img in self.die_sprites]

        # Ajouter les variables pour gérer les attaques
        self.current_attack = None
        self.attack_sprites = None
        self.last_attack_time = 0
        self.attack_cooldown = 0.5
        self.last_attack_type = 0  # Pour suivre la dernière attaque utilisée
        self.attack_combo_count = 0  # Pour compter les combos
        self.attack_combo_timeout = 1.0  # Temps en secondes avant de réinitialiser le combo

        self.x = x
        self.y = y
        self.start_y = y
        self.speed = 5
        self.is_moving = False
        self.is_running = False
        self.is_jumping = False
        self.is_attacking = False
        self.current_frame = 0
        self.frame_timer = 0
        self.direction = "right"  # Par défaut, direction droite

        # Variables pour le saut
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_power = -10

        self.is_falling = False  # Nouvelle variable pour suivre l'état de chute

        # Ajouter une hitbox pour l'attaque et une pour le joueur
        self.attack_hitbox = pygame.Rect(0, 0, 100, 150)  # La taille sera ajustée selon la direction
        self.hitbox = pygame.Rect(x + 100, y + 50, 50, 150)  # Hitbox du joueur

        self.is_hurt = False
        self.hurt_timer = 0
        self.hurt_duration = 0.4  # Durée de l'animation de blessure
        self.invincible = False
        self.invincible_duration = 1.0  # Durée d'invincibilité après être touché

        # Ajouter les variables de vie et de mort
        self.max_health = 3
        self.current_health = self.max_health
        self.is_dead = False
        self.death_animation_complete = False
        self.death_animation_speed = 0.2

        self.is_fall_death = False
        self.fall_speed = 0
        self.fall_acceleration = 0.8

        self.death_sound = death_sound  # Stocker le son de mort
        self.damage_sound = damage_sound  # Stocker le son de dégâts
        self.attack_sound = attack_sound  # Stocker le son d'attaque

    def move(self, keys, delta_time):
        current_time = pygame.time.get_ticks() / 1000

        # Si le joueur est en chute mortelle, continuer la chute
        if self.is_fall_death:
            self.fall_speed += self.fall_acceleration  # Accélération de la chute
            self.y += self.fall_speed  # Application de la vitesse de chute
            # Utiliser l'animation de chute
            self.frame_timer += delta_time
            if self.frame_timer >= 0.1:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.fall_image)
            return  # Ne pas exécuter le reste de la méthode move

        # Si le joueur est mort, gérer uniquement l'animation de mort
        if self.is_dead:
            self.frame_timer += delta_time
            if self.frame_timer >= self.death_animation_speed:
                self.frame_timer = 0
                if self.current_frame < len(self.die_sprites) - 1:
                    self.current_frame += 1
                else:
                    self.death_animation_complete = True
            return

        # Gérer l'état de blessure
        if self.is_hurt:
            self.hurt_timer += delta_time
            if self.hurt_timer >= self.hurt_duration:
                self.is_hurt = False
                self.hurt_timer = 0
            return  # Ne pas permettre d'autres actions pendant la blessure
        
        if self.invincible:
            self.hurt_timer += delta_time
            if self.hurt_timer >= self.invincible_duration:
                self.invincible = False
                self.hurt_timer = 0

        # Gérer les différentes attaques
        if not self.is_attacking:
            # Réinitialiser le combo si trop de temps s'est écoulé
            if current_time - self.last_attack_time > self.attack_combo_timeout:
                self.attack_combo_count = 0

            if keys[pygame.K_SPACE] and current_time - self.last_attack_time > self.attack_cooldown:
                # Déterminer le type d'attaque basé sur le combo
                if self.attack_combo_count == 0:
                    self.current_attack = "attack1"
                    self.attack_sprites = self.attack1_sprites
                elif self.attack_combo_count == 1:
                    self.current_attack = "attack2"
                    self.attack_sprites = self.attack2_sprites
                else:
                    self.current_attack = "attack3"
                    self.attack_sprites = self.attack3_sprites
                    self.attack_combo_count = -1  # Réinitialiser pour le prochain combo

                print(f"Executing {self.current_attack}")
                self.is_attacking = True
                self.current_frame = 0
                self.last_attack_time = current_time
                self.attack_combo_count += 1
                
                # Jouer le son d'attaque
                self.attack_sound.play()  # Jouer le son d'attaque
                
                return

        # Gérer l'animation de l'attaque en cours
        if self.is_attacking:
            self.frame_timer += delta_time
            if self.frame_timer >= 0.1:  # Vitesse d'animation pour l'attaque
                self.frame_timer = 0
                self.current_frame += 1
                if self.current_frame >= len(self.attack_sprites):
                    self.current_frame = 0
                    self.is_attacking = False
                    self.current_attack = None
                    self.attack_sprites = None
            return

        self.is_moving = False
        self.is_running = False

        if keys[pygame.K_q]:  # Déplacement vers la gauche
            print("left")
            self.x -= self.speed
            self.is_moving = True
            self.direction = "left"
            if self.is_attacking:  # Si le joueur attaque en se déplaçant vers la gauche
                self.attack_sprites = self.attack1_sprites  # Utiliser les sprites d'attaque gauche
        if keys[pygame.K_d]:  # Déplacement vers la droite
            self.x += self.speed
            self.is_moving = True
            self.direction = "right"
            if self.is_attacking:  # Si le joueur attaque en se déplaçant vers la droite
                self.attack_sprites = self.attack1_sprites  # Utiliser les sprites d'attaque droite

        if keys[pygame.K_LSHIFT]:
            self.is_running = True
            self.speed = 10
        else:
            self.speed = 5

        if keys[pygame.K_z] and not self.is_jumping and not self.is_falling:
            self.is_jumping = True
            self.velocity_y = self.jump_power
            self.current_frame = 0

        # Gestion du saut et de la chute
        if self.is_jumping or self.is_falling:
            self.velocity_y += self.gravity
            self.y += self.velocity_y

            # Déterminer si on monte ou on descend
            if self.velocity_y > 0:
                self.is_jumping = False
                self.is_falling = True
            
            if self.y >= self.start_y:
                self.y = self.start_y
                self.is_jumping = False
                self.is_falling = False
                self.velocity_y = 0
                self.current_frame = 0

        # Mise à jour du timer d'animation
        self.frame_timer += delta_time
        frame_delay = 0.2 if not self.is_attacking else 0.1  # Animation plus rapide pour l'attaque
        if self.frame_timer >= frame_delay:
            self.frame_timer = 0
            self.update_animation()

        # Mettre à jour la position des hitboxes
        self.hitbox.x = self.x + 100  # Ajuster selon la taille de votre sprite
        self.hitbox.y = self.y + 50
        
        if self.direction == "right":
            self.attack_hitbox.x = self.x + 200
        else:
            self.attack_hitbox.x = self.x - 50
        self.attack_hitbox.y = self.y + 50

    def update_animation(self):
        if self.is_attacking:
            # Gérer l'animation d'attaque
            self.current_frame += 1
            if self.current_frame >= len(self.attack_sprites):
                self.current_frame = 0
                self.is_attacking = False
        elif self.is_jumping:
            # Ne rien faire ici car l'animation du saut est gérée dans move()
            pass
        elif self.is_running or self.is_moving:
            self.current_frame = (self.current_frame + 1) % len(self.walk_right)
        else:
            self.current_frame = (self.current_frame + 1) % len(self.idle_image)

    def draw(self, screen, camera=None):
        # Calculer la position avec le décalage de la caméra si elle existe
        draw_x = self.x
        draw_y = self.y
        if camera:
            camera_adjusted_rect = camera.apply(pygame.Rect(self.x, self.y, 1, 1))
            draw_x = camera_adjusted_rect.x
            draw_y = camera_adjusted_rect.y

        if self.is_fall_death:
            # Utiliser l'animation de chute pour la mort par chute
            screen.blit(self.fall_image[self.current_frame % len(self.fall_image)], (draw_x, draw_y))
            return

        if self.is_dead:
            if not self.death_animation_complete:
                screen.blit(self.die_sprites[self.current_frame], (draw_x, draw_y))
        elif self.is_hurt:
            screen.blit(self.hurt_sprites[self.current_frame % len(self.hurt_sprites)], (draw_x, draw_y))
        elif self.is_attacking and self.attack_sprites:
            screen.blit(self.attack_sprites[self.current_frame], (draw_x, draw_y))
        elif self.is_jumping:
            screen.blit(self.jump_image[self.current_frame % len(self.jump_image)], (draw_x, draw_y))
        elif self.is_falling:
            screen.blit(self.fall_image[self.current_frame % len(self.fall_image)], (draw_x, draw_y))
        else:
            if self.direction == "left":
                screen.blit(self.walk_left[self.current_frame], (draw_x, draw_y))
            else:
                screen.blit(self.walk_right[self.current_frame], (draw_x, draw_y))

        # Debug: dessiner les hitboxes (à commenter en production)
        # if camera:
        #     pygame.draw.rect(screen, (255, 0, 0), camera.apply(self.attack_hitbox), 2)
        #     pygame.draw.rect(screen, (0, 255, 0), camera.apply(self.hitbox), 2)
        # else:
        #     pygame.draw.rect(screen, (255, 0, 0), self.attack_hitbox, 2)
        #     pygame.draw.rect(screen, (0, 255, 0), self.hitbox, 2)

    def check_attack_collision(self, skeleton):
        if self.is_attacking and skeleton.is_alive and not skeleton.is_dying:
            if self.attack_hitbox.colliderect(skeleton.hitbox):
                skeleton.start_death()
                return True
        return False

    def take_damage(self):
        if not self.invincible and not self.is_dead:
            self.current_health -= 1
            self.is_hurt = True
            self.invincible = True
            self.current_frame = 0
            self.hurt_timer = 0
            
            # Jouer le son de dégâts
            self.damage_sound.play()  # Jouer le son de dégâts
            
            # Vérifier si le joueur est mort
            if self.current_health <= 0:
                self.start_death()

    def start_death(self):
        self.is_dead = True
        self.current_frame = 0
        self.is_hurt = False
        self.is_attacking = False
        self.is_moving = False
        self.is_jumping = False
        self.is_falling = False
        
        # Jouer le son de mort
        self.death_sound.play()  # Jouer le son de mort

    def start_fall_death(self):
        """Démarre l'animation de chute mortelle"""
        self.is_fall_death = True
        self.fall_speed = 5  # Vitesse initiale de chute
        self.is_jumping = False
        self.is_attacking = False
        self.is_moving = False
        self.current_frame = 0

    def reset_state(self):
        """Réinitialise l'état du joueur après une chute mortelle"""
        self.is_fall_death = False
        self.fall_speed = 0
        self.is_jumping = False
        self.is_attacking = False
        self.is_moving = False
        self.current_frame = 0


# Boucle principale pour tester la classe
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Création du joueur
    player = Player(200, 300, death_sound, damage_sound, attack_sound)

    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0  # Temps écoulé en secondes
        screen.fill((0, 0, 0))  # Fond noir

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.move(keys, delta_time)
        player.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
