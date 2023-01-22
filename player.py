import pygame

WHITE = (255, 255, 255)

# State constants
WALKING = 1
ATTACKING = 2
CASTING = 3
DYING = 4
DEAD = 5

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
        self.health_current = self.health_max
        self.powers_max = 1
        self.powers_current = self.powers_max
        self.score = 0
        self.inventory = []  # player inventory items

        # Setting up halth bar and powers list
        self.health_bar_length = int(self.world_data.SCREEN_WIDTH / 6 * self.health_current / 1000)  # grows when max health grows
        self.health_bar_max_length = int(self.world_data.SCREEN_WIDTH / 6 * self.health_max / 1000)  # grows when max health grows

        # Setting up walk animation
        self.animation = walk_anim
        self.image = walk_anim.get_image()
        self.width = walk_anim.ss.x_dim * walk_anim.ss.scale
        self.height = walk_anim.ss.y_dim * walk_anim.ss.scale

        self.vel_x = 0  # we add and substract to this value based on keypresses
        self.vel_y = 0  # jumping or falling
        self.walking = False

        # Setting up animations
        self.attack_anim = attack_anim
        self.death = death_anim

        # Setting up sound effects
        self.fx_attack = sounds[0]
        self.fx_jump = sounds[1]
        self.fx_die = sounds[2]
        self.fx_hit = sounds[3]
        self.fx_attack.set_volume(0.5)
        self.fx_jump.set_volume(0.5)
        self.fx_die.set_volume(0.5)
        self.fx_hit.set_volume(0.2)

        self.fx_attack_channel = pygame.mixer.Channel(0)  # we sue separate channel to avoid overlapping sounds with repeat attacks
        

        # Manual adjustmentsplayer rect
        self.X_ADJ = walk_anim.ss.scale * 44
        self.Y_ADJ = walk_anim.ss.scale * 18
        self.X_CENTER = 40
        self.Y_CENTER = 28
        self.rect = pygame.Rect(x,y, self.width - self.X_ADJ, self.height - self.Y_ADJ)
        
        self.attack_rect = pygame.Rect(0,0,0,0)
        
        self.turned = False  # flip sprite/animations when moving left
        self.on_ground = False  # standing on solid ground
        self.state = WALKING  # we start walking always
        self.bouncing = False  # hit by something --> small bounce in the opposite direction
        self.last_env_damage = 0  # to manage frequency of damage
        self.dead = False  # Death animation complete

        self.world_x_pos = x + self.X_CENTER # player x position across the whole world, not just screen


    def _get_attack_rect(self) -> None:
        # Returns a the attack rect for collision detection
        # The attack rect is an offset from the player rect
        if self.turned:
            offset = -90
        else:
            offset = 30
        x = self.rect.left 
        y = self.rect.top
        self.attack_rect = pygame.Rect(x + offset, y, 100, 100) 
        
        # pygame.draw.rect(self.screen, (255,0,0), attack_rect, 2 )  # DEBUG: to see hitbox for weapon

    def check_game_over(self) -> bool:
        # Manage the time from player is hit and dies until the death animation is complete and GAME OVER screen shows
        # print(f'self.death.anim_counter ({self.death.anim_counter})> self.death.frames ({self.death.frames})')  # DEBUG
        if  self.death.anim_counter == self.death.frames -1:
            self.dead = True
            self.fx_die.play()
            self.death.anim_counter = 0
            return True
        else:
            return False

    def hit(self, damage: int, turned: int) -> None:
        """ Player has been hit by mob or projectile, gets damage and bounces backs"""
        self.fx_hit.play()
        # Adjust health and bars
        self.health_current -= damage
        if self.health_current <= 0:
            self.health_current = 0
            self.state = DYING
        self.health_bar_length = int(self.world_data.SCREEN_WIDTH / 6 * self.health_current / 1000)

        direction = 1
        if turned:
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

    def take_damage(self, damage: int, hits_per_second:int=0) -> None:
        """ Player has been in contact with enviromnmental damage, gets damage once or frequency per second """

        now = pygame.time.get_ticks()
        if now > self.last_env_damage + 1000 / hits_per_second:
            self.fx_hit.play()
            # Adjust health and bars
            self.health_current -= damage
            if self.health_current <= 0:
                self.health_current = 0
                self.state = DYING
            self.health_bar_length = int(self.world_data.SCREEN_WIDTH / 6 * self.health_current / 1000)
            self.last_env_damage = now


    def heal(self, damage) -> None:
        self.health_current += damage
        if self.health_current > self.health_max:
            self.health_current = self.health_max
        self.health_bar_length = int(self.world_data.SCREEN_WIDTH / 6 * self.health_current / 1000)


    def die(self) -> None:
        if self.state != DYING:
            self.state = DYING  # we start the death sequence
            self.death.anim_counter = 0  # Animation counter the death animation

    def move(self) -> list:
        distance = 5  # How far we move in one keypress
        dx = 0
        dy = 0
        scroll = 0
        
        if self.state in (WALKING, ATTACKING):
            if self.walking == 1:  # right
                dx += distance
                self.turned = False
                if self.on_ground:
                    self.animation.active = True
            elif self.walking == -1:  # left
                dx -= distance
                self.turned = True
                if self.on_ground:
                    self.animation.active = True
            else:
                self.animation.active = False
        if self.state == ATTACKING:
            self._get_attack_rect()
            self.attack_anim.active = True 
            if self.attack_anim.anim_counter == self.attack_anim.frames -1:  # reset after attack animation is complete
                self.state = WALKING
                self.attack_anim.active = False
                self.attack_anim.anim_counter = 0

        # Die
        elif self.state == DYING:
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
        if dx < 0 and x_pos <= self.world_data.SCROLL_THRESHOLD and self.world_x_pos > self.world_data.SCROLL_THRESHOLD + self.width:
            scroll = -dx  # We scroll left by the opposite of the player's x speed
        
         # Check if player has reached scroll threshold to the right (and we're not on the far right) + we're walking right
        if dx > 0 and x_pos >= self.world_data.SCREEN_WIDTH - self.world_data.SCROLL_THRESHOLD and self.world_x_pos < self.world_data.TILE_SIZE * self.world_data.MAX_COLS - self.world_data.SCROLL_THRESHOLD:
            scroll = -dx  # We scroll right by the opposite of the player's x speed
        

        # Update rectangle position
        self.rect.x += dx + scroll
        self.rect.y += dy 

        # Update world position
        self.world_x_pos += dx

        return scroll

    def draw(self) -> None:
        self.screen = pygame.display.get_surface()
        # First test if we're busy doing something 
        # Attacking?      
        if self.state == ATTACKING:
            self.image = self.attack_anim.get_image()
            self.image = self.image.convert_alpha()
            # The sprite is larger when we attack, so we need to adjust center
            ATTACK_X = -2 * 64
            ATTACK_Y = -2 * 64
            self.screen.blit(pygame.transform.flip( self.image, self.turned, False), (self.rect.x - self.X_CENTER + ATTACK_X, self.rect.y - self.Y_CENTER + ATTACK_Y))
        # Dying?
        elif self.state == DYING:
            self.image = self.death.get_image()
            self.image = self.image.convert_alpha()
            self.screen.blit(pygame.transform.flip( self.image, self.turned, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))
        # Player walking, jumping or idle
        elif self.state == WALKING:
            self.image = self.animation.get_image()
            self.image = self.image.convert_alpha()
            self.screen.blit(pygame.transform.flip( self.image, self.turned, False), (self.rect.x - self.X_CENTER, self.rect.y - self.Y_CENTER))
        else:
            print(f'ERROR: illegal player state {self.state}')
            exit(1)

        #pygame.draw.rect(self.screen, (255,255,255), self.rect, 2 )  # Just to show hitboxes