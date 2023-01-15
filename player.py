import pygame

WHITE = (255, 255, 255)


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, game_world_data, game_world, walk_anim, attack_anim, death_anim, sounds):
        """
        The Player class constructor - note that x and y is only for initialization,
        the player position will be tracked by the rect
        """
        super().__init__()
        self.world = game_world
        self.world_data = game_world_data


        # Basic state information
        self.health_max = 1000
        self.health_current = self.health_max - 200 # TODO: FOR TESTING ONLY
        self.powers_max = 1
        self.powers_current = self.powers_max

        # Setting up halth bar and powers list
        self.health_bar_length = int(self.world_data.SCREEN_WIDTH / 6 * self.health_current / 1000)  # grows when max health grows
        self.health_bar_max_length = int(self.world_data.SCREEN_WIDTH / 6 * self.health_max / 1000)  # grows when max health grows

        # Setting up walk animation
        self.animation = walk_anim
        self.image = walk_anim.image()
        self.width = walk_anim.ss.x_dim * walk_anim.ss.scale
        self.height = walk_anim.ss.y_dim * walk_anim.ss.scale

        self.vel_y = 0  # jumping or falling

        # Setting up animations
        self.attack = attack_anim
        self.death = death_anim

        # Setting up sound effects
        self.fx_attack = sounds[0]
        self.fx_jump = sounds[1]
        self.fx_die = sounds[2]
        self.fx_attack.set_volume(0.5)
        self.fx_jump.set_volume(0.5)
        self.fx_die.set_volume(0.5)

        self.fx_attack_channel = pygame.mixer.Channel(0)  # we sue separate channel to avoid overlapping sounds with repeat attacks
        

        # Manual adjustments of hitbox for player rect
        self.X_ADJ = walk_anim.ss.scale * 44
        self.Y_ADJ = walk_anim.ss.scale * 18
        self.X_CENTER = 40
        self.Y_CENTER = 28
        self.rect = pygame.Rect(0,0, self.width - self.X_ADJ, self.height - self.Y_ADJ)
        self.rect.center = (x + self.X_CENTER, y + self.Y_CENTER)
        self.attack_rect = pygame.Rect(0,0,0,0)
        
        self.flip = False  # flip sprite/animations when moving left
        self.on_ground = False  # standing on solid ground
        self.attacking = False
        self.bouncing = False  # hit by something --> small bounce in the opposite direction

        self.dying = False  # Playing death animations
        self.dead = False  # Death animation complete

        self.world_x_pos = x + self.X_CENTER # player x position across the whole world, not just screen


    def _get_attack_rect(self):
        # Returns a the attack rect for collision detection
        # The attack rect is an offset from the player rect
        if self.flip:
            offset = -90
        else:
            offset = 30
        x = self.rect.left 
        y = self.rect.top
        self.attack_rect = pygame.Rect(x + offset, y, 100, 100) 
        
        # pygame.draw.rect(self.screen, (255,0,0), attack_rect, 2 )  # DEBUG: to see hitbox for weapon

    def check_game_over(self):
        # Manage the time from player is hit and dies until the death animation is complete and GAME OVER screen shows
        # print(f'self.death.anim_counter ({self.death.anim_counter})> self.death.frames ({self.death.frames})')  # DEBUG
        if  self.death.anim_counter == self.death.frames -1:
            self.dead = True
            self.fx_die.play()
            return True
        else:
            return False

    def hit(self, damage, flip):
        # Adjust health and bars
        self.health_current -= damage
        if self.health_current <= 0:
            self.health_current = 0
            self.dying = True
        self.health_bar_length = int(self.world_data.SCREEN_WIDTH / 6 * self.health_current / 1000)

        direction = 1
        if flip:
            direction = -1

        # Bounce back
        x_bounce = 20
        y_bounce = -5         

        if not self.bouncing:
            self.vel_y = y_bounce
            self.bouncing = True

        # Prevent us getting bounced inside platforms
        for platform in self.world.platforms_sprite_group.sprites():
            if platform.rect.colliderect(self.rect.x + x_bounce, self.rect.y, self.width - self.X_ADJ, self.height - self.Y_ADJ):
                x_bounce = 0

        self.rect.x += x_bounce * direction
        # Update world position
        self.world_x_pos += x_bounce * direction

    def heal(self, damage):
        self.health_current += damage
        if self.health_current > self.health_max:
            self.health_current = self.health_max
        self.health_bar_length = int(self.world_data.SCREEN_WIDTH / 6 * self.health_current / 1000)


    def die(self):
        if not self.dying:
            self.dying = True  # we start the death sequence
            self.death.anim_counter = 0  # Animation counter the death animation

    def move(self):
        distance = 5  # How far we move in one keypress
        dx = 0
        dy = 0
        scroll = 0
        self.score = 0  # score from each move, added up outside of class

        self.animation.active = False  # Only animate on keypress

        #(self.attack.anim_counter)  # DEBUG
        # Process keypresses
        if not self.dead and not self.dying:  # We ignore keypresses after death or deatn anim start
            key = pygame.key.get_pressed()
        
            # Left
            if key[pygame.K_LEFT] or key[pygame.K_a]:
                    dx = -distance
                    self.flip = True
                    self.attacking = False
                    if self.on_ground == True:
                        self.animation.active = True
            # Right
            if key[pygame.K_RIGHT] or key[pygame.K_d]:
                    dx = distance
                    self.flip = False
                    self.attacking = False
                    if self.on_ground == True:
                        self.animation.active = True
            # Jump
            if key[pygame.K_UP] or key[pygame.K_w]:
                    if self.vel_y == 0 and self.on_ground == True:
                        self.vel_y = - self.world_data.JUMP_HEIGHT
                        self.animation.active = False
                        self.attacking = False
                        self.on_ground = False
                        self.fx_jump.play()

            # Exit
            if key[pygame.K_q]:
                exit(0)

            # Attack
            if key[pygame.K_SPACE]:
                self.attacking = True
                if not self.fx_attack_channel.get_busy():
                    self.fx_attack_channel.play(self.fx_attack)

        if self.attacking == True:
            self._get_attack_rect()
            self.attack.active = True 

        # print(self.attack.anim_counter, self.attack.frames)
        if self.attack.anim_counter == self.attack.frames -1:
            self.attacking = False
            self.attack.active = False
            self.attack.anim_counter = 0

        # Die
        if self.dying:
            self.death.anim_counter += 1

        # Gravity
        self.vel_y += self.world_data.GRAVITY
        dy += self.vel_y

        # Watch screen boundaries (effectively world boundaries since the screen scrolls to world edges before player can get to end of screen)
        if self.rect.left + dx < 0:
            dx = - self.rect.left
        if self.rect.right + dx > self.world_data.SCREEN_WIDTH:
            dx = self.world_data.SCREEN_WIDTH - self.rect.right
        if self.rect.top + dy < 0:
            dy = - self.rect.top
            self.vel_y = self.world_data.GRAVITY

        # Check platform collision
        for platform in self.world.platforms_sprite_group.sprites():
            # collision in the y direction only, so instead of using self.rect directly, we create
            # this temporaty rectangle with dy added for where the rectange _would_ be after the move (or we'd end up inside the platform)
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width - self.X_ADJ, self.height - self.Y_ADJ):
                if self.rect.bottom < platform.rect.centery:  # Is player above platform?
                    if self.vel_y > 0:  # Is player falling?
                        dy = 0
                        self.on_ground = True
                        self.vel_y = 0
            
            if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width - self.X_ADJ, self.height - self.Y_ADJ):
                #print(f'platform.rect.x: {platform.rect.x}, platform.rect.y: {platform.rect.y} AND self.rect.x: {self.rect.x} and self.rect.y: {self.rect.y}')
                dx = 0

        
        x_pos = self.rect.center[0]

        # Check if player has reached scroll threshold to the LEFT (and we're not on the far left) + we're walking left
        #print(f'world_x_pos: {self.world_x_pos}')
        if dx < 0 and x_pos <= self.world_data.SCROLL_THRESHOLD and self.world_x_pos > self.world_data.SCROLL_THRESHOLD:
            scroll = -dx  # We scroll left by the opposite of the player's x speed
        
         # Check if player has reached scroll threshold to the right (and we're not on the far right) + we're walking right
        if dx > 0 and x_pos >= self.world_data.SCREEN_WIDTH - self.world_data.SCROLL_THRESHOLD and self.world_x_pos < self.world_data.TILE_SIZE * self.world_data.MAX_COLS - self.world_data.SCROLL_THRESHOLD:
            scroll = -dx  # We scroll right by the opposite of the player's x speed
        

        # Update rectangle position
        self.rect.x += dx + scroll
        self.rect.y += dy 

        # Update world position
        self.world_x_pos += dx

        return [scroll, self.score]

    def draw(self, screen):
        self.screen = screen
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
        elif self.dying:
            self.image = self.death.image()
            self.image = self.image.convert_alpha()
            self.screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))
        # Player walking, jumping or idle
        else:
            self.image = self.animation.image()
            self.image = self.image.convert_alpha()
            self.screen.blit(pygame.transform.flip( self.image, self.flip, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))

        #pygame.draw.rect(self.screen, (255,255,255), self.rect, 2 )  # Just to show hitboxes