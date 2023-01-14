import pygame

class Monster(pygame.sprite.Sprite):
    def __init__(self,x, y, walk_anim, attack_anim, ai):
        """
        The Player class constructor - note that x and y is only for initialization,
        the player position will be tracked by the rect
        """
        super().__init__()
        self.gravity = 0.5 
        
        self.ai = ai  # a MonsterAI() instance

        # Setting up walk animation
        self.animation = walk_anim
        self.image = walk_anim.image()
        self.width = walk_anim.ss.x_dim * walk_anim.ss.scale
        self.height = walk_anim.ss.y_dim * walk_anim.ss.scale

        # Setting up attack animation
        self.attack = attack_anim

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
        self.score_flag = False  # We can only add more score when this is True
        self.prev_y_lvl = self.rect.y  # Tracking vertical progress


    def _create_rects(self):
        # Create the detection and attack rect which we will use for collision detection

        # Creating a DETECTION rect where to mob will attack if the player rect collides
        x = self.rect.center[0]
        y = self.rect.top
        if self.flip:       
            self.rect_detect = pygame.Rect(x - self.ai.detection_range, y, self.ai.detection_range, self.height) 
        else:
            self.rect_detect = pygame.Rect(x, y, self.ai.detection_range, self.height) 


        # Creating an ATTACK rect where to mob will kill player if player rect collides
        if self.attacking:
            self.attack.anim_counter += 1  # update the attack animation
            dx = self.ai.speed_attacking  # once we're attacking we speed up
                    
            # The attack rect is an offset from the mob rect
            x = self.rect.center[0]
            y = self.rect.top

            if self.flip:
                self.rect_attack = pygame.Rect(x - self.ai.attack_range, y, self.ai.attack_range, self.height) 
            else:
                self.rect_attack = pygame.Rect(x , y, self.ai.attack_range, self.height) 
            
            if self.attack.anim_counter == self.attack.frames:  # after each attack animation we stop the attack
                self.attacking = False
                self.rect_attack = self.rect
                self.attack.anim_counter = 0

    def _check_platform_collision(self, dx, dy, platforms_sprite_group):
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
                
                # Preventing falling off left/right edge of platforms if there is NO collision (-1) to the side and down
                left_fall_rect  = pygame.Rect(self.rect.x + dx + 35, self.rect.y + 30 , self.width - self.X_ADJ, self.height - self.Y_ADJ)
                right_fall_rect = pygame.Rect(self.rect.x + dx - 35, self.rect.y + 30 , self.width - self.X_ADJ, self.height - self.Y_ADJ)
                if  left_fall_rect.collidelist(all_platforms) == -1:
                    self.ai.direction = -1
                    self.flip = True
                if right_fall_rect.collidelist(all_platforms) == -1:
                    self.ai.direction = 1
                    self.flip = False
                
                # Turning around if hitting a solid tile  TODO: separate collision and non-collision tiles
                tile_collider_rect = pygame.Rect(self.rect.x + dx, self.rect.y, self.width - self.X_ADJ, (self.height - self.Y_ADJ) - 10)
                if platform.rect.colliderect(tile_collider_rect):
                    #print(f'crash: {self.ai.monster}')
                    self.ai.direction *= -1
                    self.rect.x += dx
                    self.flip = not self.flip
                

    def update(self, scroll, platforms_sprite_group):
        
        # we set start speeds for x and y
        dy = 0
        dx = self.ai.speed_walking  #  we start at walking speed

        # we compensate for scrolling
        self.scroll = scroll
        self.rect.x += scroll

        # we compensate for graivty
        self.vel_y += self.gravity  # allows us to let mobs fall (including during death)
        dy += self.vel_y
                # Update rectangle position
        self.rect.x += dx * self.ai.direction
        self.rect.y += dy 

        if not self.dead:
            self._create_rects()
            self._check_platform_collision(dx, dy, platforms_sprite_group)
        else:
            self.rect_attack = None
            self.rect_detect = None



    


    def draw(self, screen):
        # As collision detection is done with the rectangle, it's size and shape matters
        if self.attacking:
            self.image = self.attack.image().convert_alpha()
            screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))
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
            self.image = self.animation.image().convert_alpha()
            screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))

        #pygame.draw.rect(self.screen, (255,255,255), self.rect, 2 )  # Debug show rect on screen (white)