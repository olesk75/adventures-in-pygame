"""
Monster (pygame Sprite class)       : base class for all mobs
Projectile (pygame Sprite class)    : class for all projectiles (arrows etc.)
"""


import random
import pygame

class Monster(pygame.sprite.Sprite):
    def __init__(self,x, y, walk_anim, attack_anim, mob_data):
        """
        The Player class constructor - note that x and y is only for initialization,
        the player position will be tracked by the rect
        """
        super().__init__()
        self.gravity = 0.5 
        
        self.data = mob_data  # a MonsterData() instance

        # Setting up walk animation
        self.walk_anim = walk_anim
        self.image = walk_anim.image()
        self.width = walk_anim.ss.x_dim * walk_anim.ss.scale
        self.height = walk_anim.ss.y_dim * walk_anim.ss.scale

        # Setting up attack animation
        self.attack_anim = attack_anim

        # Setting up death animation
        self.dead = False

        # Manual adjustments of hitbox
        self.X_ADJ = walk_anim.ss.scale * 44
        self.Y_ADJ = walk_anim.ss.scale * 18
        self.X_CENTER = 40
        self.Y_CENTER = 28

        self.rect = pygame.Rect(0,0, self.width - self.X_ADJ, self.height - self.Y_ADJ)
        self.rect_detect = pygame.Rect(0,0,0,0)
        self.rect_attack = pygame.Rect(0,0,0,0)

        self.rect.center = (x + self.X_CENTER, y + self.Y_CENTER)
        self.vel_y = 0
        self.flip = False
        self.at_bottom = False
        self.attacking = False
        self.last_attack = 0
        self.ready_to_attack = True  
        self.score_flag = False  # We can only add more score when this is True
        self.prev_y_lvl = self.rect.y  # Tracking vertical progress


    def _create_rects(self) -> None:
        # Create the detection and attack rect which we will use for collision detection

        # Creating a DETECTION rect where to mob will attack if the player rect collides
        x = self.rect.centerx
        y = self.rect.top + 30 + (self.data.detection_range_high * -100)

        width = self.data.detection_range
        height = self.height - 100 + (self.data.detection_range_high * 200)

        if self.flip:       
            self.rect_detect = pygame.Rect(x - self.data.detection_range, y, width, height) 
        else:
            self.rect_detect = pygame.Rect(x, y,width, height) 

        # Creating an ATTACK rect 
        if self.attacking:
            y = y + (self.data.detection_range_high * 100)
            height = self.height / 2
            if self.flip:
                self.rect_attack = pygame.Rect(x - self.data.attack_range, y, self.data.attack_range, height) 
            else:
                self.rect_attack = pygame.Rect(x , y, self.data.attack_range, height) 
            



    def _check_platform_collision(self, dx, dy, platforms_sprite_group) -> None:
         #
        # Checking platform collision to prevent falling and to turn when either at end of platform or hitting a solid tile
        #
        all_platforms = platforms_sprite_group.sprites()
        for platform in all_platforms:
            # collision in the y direction only, using a collision rect indicating _next_ position (y + dy)
            collider_rect = pygame.Rect(self.rect.x, self.rect.y + dy, self.width - self.X_ADJ, self.height - self.Y_ADJ)
            if platform.rect.colliderect(collider_rect):  # we are standing on a platform essentially
                # Preventing falling through platforms
                if self.rect.bottom < platform.rect.centery:  # Is player above platform?
                    if self.vel_y > 0 and self.dead == False:  # Is monster falling and not dead?
                        dy = 0
                        self.at_bottom = True                     
                        self.vel_y = 0
                
                # Preventing falling off left/right edge of platforms if there is NO collision (-1) to the side and down (and it's not a jumping mob
                left_fall_rect  = pygame.Rect(self.rect.x + dx + 35, self.rect.y + 30 , self.width - self.X_ADJ, self.height - self.Y_ADJ)
                right_fall_rect = pygame.Rect(self.rect.x + dx - 35, self.rect.y + 30 , self.width - self.X_ADJ, self.height - self.Y_ADJ)
                if  left_fall_rect.collidelist(all_platforms) == -1 and not self.data.attack_jumper:
                    self.data.direction = -1
                    self.flip = True
                if right_fall_rect.collidelist(all_platforms) == -1 and not self.data.attack_jumper:
                    self.data.direction = 1
                    self.flip = False
                
                # Turning around if hitting a solid tile  TODO: separate collision and non-collision tiles
                tile_collider_rect = pygame.Rect(self.rect.x + dx, self.rect.y, self.width - self.X_ADJ, (self.height - self.Y_ADJ) - 10)
                if platform.rect.colliderect(tile_collider_rect):
                    #print(f'crash: {self.data.monster}')
                    self.data.direction *= -1
                    self.rect.x += dx * 2  * self.data.direction # far enough to avoid re-triggering in an endless loop
                    self.flip = not self.flip

    def attack_start(self) -> None: 
        """ Called to set attack variables and keep track of attack timings for repeat attacks """                
        if self.ready_to_attack:
            self.attacking = True  # set the "is attacking" flag to true
            self.attack_anim.active = True
            self.last_attack = pygame.time.get_ticks()


    def attack_stop(self) -> None: 
        self.attacking = False  # set the "is attacking" flag to true
        self.attack_anim.active = False
        self.rect_attack = pygame.Rect(0,0,0,0)

    def update(self, scroll, platforms_sprite_group, player) -> None:
        
        # if we've fallen off the screen, kill sprite TODO: doesn't wor
        #print(f'self.rect.top: {self.rect.top}, player.world_data.SCREEN_HEIGHT: {player.world_data.SCREEN_HEIGHT}')
        # if int(self.rect.top) > int(player.world_data.SCREEN_HEIGHT):
        #     self.kill()
        #     print('die')

        # we set start speeds for x and y
        dy = 0
        if self.attacking:
            dx = self.data.speed_attacking

            # Sometimes a jumping mob can jump if player is higher than the mob and mob is attacking
            #print(f'player.rect.centery: {player.rect.centery}, self.rect.center: {self.rect.centery }')
            max_dist_centery = -7
            player_above_mob = player.rect.centery -  (self.rect.centery + max_dist_centery)
            #print(f'player is this much above attacking mob: {player_above_mob}')

            if self.data.attack_jumper and player_above_mob < 0 and self.vel_y == 0:  # player is higher up and we're not already jumping
                if 0.001  > random.random():  
                    self.vel_y = -10
        else:
            dx = self.data.speed_walking  #  we start at walking speed

            # We throw in random cahnges in direction, different by mod type
            if self.data.random_turns / 100  > random.random():
                dx *= -1
                self.data.direction *= -1
                self.flip = not self.flip

        # we compensate for scrolling
        self.scroll = scroll
        self.rect.x += scroll

        # we compensate for graivty
        self.vel_y += self.gravity  # allows us to let mobs fall (including during death)
        dy += self.vel_y
        
        # Update rectangle position
        self.rect.x += dx * self.data.direction
        self.rect.y += dy 

        if not self.dead:
            self._create_rects()
            self._check_platform_collision(dx, dy, platforms_sprite_group)
        else:
            self.rect_attack = None
            self.rect_detect = None

        # Updating the ready_to_attack flag 
        now = pygame.time.get_ticks()
        if now - self.last_attack > self.data.attack_delay:
            self.ready_to_attack = True
        else:
            self.ready_to_attack = False


    def draw(self, screen) -> None:
        # As collision detection is done with the rectangle, it's size and shape matters
        if self.attacking:
            # If we have a diffent size attack sprites, we need to take scale into account
            self.image = self.attack_anim.image(self.data.attack_delay).convert_alpha()
            x_correction = self.attack_anim.ss.x_dim - self.walk_anim.ss.x_dim
            y_correction = self.attack_anim.ss.y_dim - self.walk_anim.ss.y_dim
            x = (self.rect.x - self.X_CENTER) - x_correction
            y = (self.rect.y - self.Y_CENTER) - y_correction
            screen.blit(pygame.transform.flip( self.image, self.flip, False), (x, y))
        elif self.dead:
            # Spin sprite
            angle = 5
            orig_rect = self.image.get_rect()
            rot_image = pygame.transform.rotate(self.image, angle)
            rot_rect = orig_rect.copy()
            rot_rect.center = rot_image.get_rect().center
            self.image = rot_image.subsurface(rot_rect).copy()
            screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))
        else:
            self.image = self.walk_anim.image().convert_alpha()
            screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))

        #pygame.draw.rect(self.screen, (255,255,255), self.rect, 2 )  # Debug show rect on screen (white)


class Projectile(pygame.sprite.Sprite):
    def __init__(self,x, y, image, flip, scale = 1):
        """
        The Player class constructor - note that x and y is only for initialization,
        the player position will be tracked by the rect
        """
        super().__init__()
        # self.gravity = 0.5  # TODO
        self.image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))

        self.dead = False  
        self.speed = 10
        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.flip = flip
        
    def update(self, scroll, platforms_sprite_group) -> None:
        
        # we set start speeds for x and y
        dx = self.speed
        if self.flip:
            dx = -self.speed
            
        dy = 0  # projectiles have no gravity

        # we compensate for scrolling
        self.scroll = scroll
        self.rect.x += scroll

        # Update rectangle position
        self.rect.x += dx 
        self.rect.y += dy 

        # Collision with platform
        if pygame.sprite.spritecollideany(self, platforms_sprite_group):
            self.kill()

    def draw(self, screen) -> None:
        self.image = self.anim.image().convert_alpha()
        screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x, self.rect.y))