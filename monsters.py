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


    def update(self, scroll, platforms_sprite_group):
        
        self.platforms_sprite_group = platforms_sprite_group

        self.scroll = scroll
        self.rect.x += scroll
        
        dy = 0  # we start with no vertical speed
        dx = self.ai.speed_walking  #  we start at walking speed

        # 
        # Creating a DETECTION rect where to mob will attack if the player rect collides
        #
        x = self.rect.center[0]
        y = self.rect.top
        if self.flip:       
            self.rect_detect = pygame.Rect(x - self.ai.detection_range, y, self.ai.detection_range, self.height) 
        else:
            self.rect_detect = pygame.Rect(x, y, self.ai.detection_range, self.height) 

        #
        # Creating an ATTACK rect where to mob will kill player if player rect collides
        #
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

        self.vel_y += self.gravity  # allows us to let mobs fall (including during death)
        dy += self.vel_y

        #
        # Checking platform collision to prevent falling and to turn when either at end of platform or hitting a solid tile
        #
        all_platforms = self.platforms_sprite_group.sprites()
        for platform in all_platforms:
            # collision in the y direction only, so instead of using self.rect directly, we create
            # this temporaty rectangle with dy added for where the rectange _would_ be after the move
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width - self.X_ADJ, self.height - self.Y_ADJ) and not self.dead:
                if self.rect.bottom < platform.rect.centery:  # Is player above platform?
                    if self.vel_y > 0 and self.dead == False:  # Is monster falling and not dead?
                        dy = 0
                        self.at_bottom = True                     
                        self.vel_y = 0
                
                # # X: change direction if hit a rect
                # if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width - self.X_ADJ, self.height - self.Y_ADJ):
                #     dx = 6
                #     self.ai.direction *= -1
                # else:
                #     # X: change direction if no rect in front and also below (falling off edge) - must test ALL
                left_fall_rect  = pygame.Rect(self.rect.x + dx + 35, self.rect.y + 30 , self.width - self.X_ADJ, self.height - self.Y_ADJ)
                right_fall_rect = pygame.Rect(self.rect.x + dx - 35, self.rect.y + 30 , self.width - self.X_ADJ, self.height - self.Y_ADJ)
                if  left_fall_rect.collidelist(all_platforms) == -1 or right_fall_rect.collidelist(all_platforms) == -1:
                    self.ai.direction *= -1

        # Update rectangle position
        self.rect.x += dx * self.ai.direction
        self.rect.y += dy 


    def draw(self, screen):
        self.screen = screen
        self.flip = False

        if self.ai.direction == -1: 
            self.flip = True

        # As collision detection is done with the rectangle, it's size and shape matters
        if self.attacking:
            self.image = self.attack.image().convert_alpha()
            self.screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))
        elif self.dead:
            # Spin sprite
            angle = 5
            orig_rect = self.image.get_rect()
            rot_image = pygame.transform.rotate(self.image, angle)
            rot_rect = orig_rect.copy()
            rot_rect.center = rot_image.get_rect().center
            self.image = rot_image.subsurface(rot_rect).copy()
            self.screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))
        else:
            self.image = self.animation.image().convert_alpha()
            self.screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))

        #pygame.draw.rect(self.screen, (255,255,255), self.rect, 2 )  # Debug show rect on screen (white)