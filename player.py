import pygame

# Game variables in a named tuple (new in Python 3.6)
class PlayerData():
    def __init__(self):
        self.score = 0


# Player class
class Player():
    def __init__(self, x, y, world, screen, walk_anim, attack_anim, death_anim):
        """
        The Player class constructor - note that x and y is only for initialization,
        the player position will be tracked by the rect
        """
        WHITE = (255, 255, 255)
        self.JUMP_HEIGHT = 30
        self.SCROLL_THRESHOLD = 400

        self.world = world
        self.screen = screen
        # Setting up walk animation
        self.animation = walk_anim
        self.image = walk_anim.image()
        self.width = walk_anim.ss.x_dim * walk_anim.ss.scale
        self.height = walk_anim.ss.y_dim * walk_anim.ss.scale

        self.world_x_pos = x
        self.vel_y = 0

        # Setting up attack animation
        self.attack = attack_anim

        # Setting up death animation
        self.death = death_anim

        # Manual adjustments of hitbox
        self.X_ADJ = walk_anim.ss.scale * 44
        self.Y_ADJ = walk_anim.ss.scale * 18
        self.X_CENTER = 40
        self.Y_CENTER = 28

        self.rect = pygame.Rect(0,0, self.width - self.X_ADJ, self.height - self.Y_ADJ)
        self.rect.center = (x + self.X_CENTER, y + self.Y_CENTER)
        
        self.flip = False
        self.at_bottom = False
        self.attacking = False
        self.score_flag = False  # We can only add more score when this is True
        self.prev_y_lvl = self.rect.y  # Tracking vertical progress

        self.alive = True  # Goes negative once we've been hit but are still playing death animations

        self.SCREEN_WIDTH = pygame.display.get_window_size()[0]
        self.SCREEN_HEIGHT = pygame.display.get_window_size()[1]

    def die(self):

        # print(f'self.death.anim_counter ({self.death.anim_counter})> self.death.frames ({self.death.frames})')  #
        if self.alive == True:
            self.alive = False
            self.death.anim_counter = 0  # Animation counter for the Animation instance

        if  self.death.anim_counter >= self.death.frames -2:  # TODO: why minus 2?
            pygame.time.delay(3 * 100) # 1 second == 1000 milliseconds
            return True
        
        return False

    def get_attack_rect(self):
        # Returns a the attack rect for collision detection
        attack_width = 100
        attack_height = 10
        if self.flip:
            offset = -100
        else:
            offset = 40
        x = self.rect.left
        y = self.rect.top

        pygame.Rect(0,0, self.width - self.X_ADJ, self.height - self.Y_ADJ)
        attack_rect = pygame.Rect(x + offset, y, 100, 100) 
        
        # pygame.draw.rect(self.screen, (255,0,0), attack_rect, 2 )  # DEBUG: to see hitbox for weapon
        return attack_rect


    def move(self, platforms):
        distance = 5  # How far we move in one keypress
        dx = 0
        dy = 0
        scroll = 0
        self.score = 0  # score from each move, added up outside of class

        self.platform_group = platforms

        self.animation.active = False  # Only animate on keypress

        #(self.attack.anim_counter)  # DEBUG
        # Process keypresses
        if self.alive == True:  # We ignore keypresses after death
            key = pygame.key.get_pressed()
        
            # Left
            if key[pygame.K_LEFT] or key[pygame.K_a]:
                    dx = -distance
                    self.world_x_pos += dx
                    self.flip = True
                    self.attacking = False
                    if self.at_bottom == True:
                        self.animation.active = True
            # Right
            if key[pygame.K_RIGHT] or key[pygame.K_d]:
                    dx = distance
                    self.world_x_pos += dx
                    self.flip = False
                    self.attacking = False
                    if self.at_bottom == True:
                        self.animation.active = True
            # Jump
            if key[pygame.K_UP] or key[pygame.K_w]:
                    if self.vel_y == 0 and self.at_bottom == True:
                        self.vel_y = - self.world.JUMP_HEIGHT
                        self.animation.active = False
                        self.attacking = False
                        self.at_bottom = False

            #print(self.world_x_pos)  # DEBUG

            # Attack
            if key[pygame.K_SPACE]:
                self.attacking = True

        if self.attacking == True:
            self.attack.anim_counter += 1

        if self.attack.anim_counter == self.attack.frames:
            self.attacking = False
            self.attack.anim_counter = 0

        # Die
        if self.alive == False:
            self.death.anim_counter += 1

        # Gravity
        self.vel_y += self.world.GRAVITY
        dy += self.vel_y

        # Watch screen boundaries
        if self.rect.left + dx < 0:
            dx = - self.rect.left
        if self.rect.right + dx > self.SCREEN_WIDTH:
            dx = self.SCREEN_WIDTH - self.rect.right
        if self.rect.top + dy < 0:
            dy = - self.rect.top
            self.vel_y = self.world.GRAVITY

        # Check platform collision
        for platform in self.platform_group:
            # collision in the y direction only, so instead of using self.rect directly, we create
            # this temporaty rectangle with dy added for where the rectange _would_ be after the move
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width - self.X_ADJ, self.height - self.Y_ADJ):
                if self.rect.bottom < platform.rect.centery:  # Is player above platform?
                    if self.vel_y > 0:  # Is player falling?
                        dy = 0
                        self.at_bottom = True
                        self.vel_y = 0
                
        x_pos = self.rect.center[0]
        # Check if player has reached scroll threshold to the left (and we're not on the far left) + we're walking left
        if dx < 0 and x_pos <= self.SCROLL_THRESHOLD and self.world_x_pos > 100:
            scroll = -dx  # We scroll left by the opposite of the player's x speed
        
         # Check if player has reached scroll threshold to the right (and we're not on the far right) + we're walking right
        if dx > 0 and x_pos >= self.SCREEN_WIDTH - self.SCROLL_THRESHOLD and self.world_x_pos < self.world.TOT_WIDTH - 100:
            scroll = -dx  # We scroll right by the opposite of the player's x speed

        # Update rectangle position
        self.rect.x += dx + scroll
        self.rect.y += dy 

        return [scroll, self.score]

    def draw(self):
        # First test if we're busy doing something 
        # Attacking?      
        if self.attacking == True:
            self.image = self.attack.image()
            self.image = self.image.convert_alpha()
            # The sprite is larger when we attack, so we need to adjust center
            ATTACK_X = -2 * 64
            ATTACK_Y = -2 * 64
            self.screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER + ATTACK_X, self.rect.y - self.Y_CENTER + ATTACK_Y))
        # Dying?
        elif self.alive == False:
            self.image = self.death.image(repeat=False)
            self.image = self.image.convert_alpha()
            self.screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))
        # Nothins special going on
        else:
            self.image = self.animation.image()
            self.image = self.image.convert_alpha()
            self.screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))

        #pygame.draw.rect(self.screen, (255,255,255), self.rect, 2 )  # Just to show hitboxes