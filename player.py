import pygame
from settings import *
from level import GameAudio

DEBUG_HITBOXES = True

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, surface, health_max) -> None:
        # need also walk_anim, attack_anim, death_anim, sounds
        """
        The Player class constructor - note that x and y is only for initialization,
        the player position will be tracked by the rect, as the class inherits from the Sprite class
        Player is added to a sprite group, which then is used for calling the draw(method)
        """
        super().__init__()

        self.screen = surface

        # TODO: fix hardcoded values
        self.health_max = health_max
        self.health_current = self.health_max

        self.invincible = False
        self.invincibility_duration = 500

        from animation_data import anim

        # Setting up animations
        self.animations = {
            'idle': None,  # TODO
            'walk': anim['player']['walk'],
            'attack': anim['player']['attack'],
            'death': anim['player']['death']
        }
        
        self.animation = self.animations['walk']  # Walking by default
        self.image = self.animation.get_image()
        
        # Convert from original resolution to game resolution
        self.width = int(self.animations['walk'].ss.x_dim * self.animations['walk'].ss.scale * 1.4 )  # we make the sprite a bit wider so we can encapsulate the attack anim without resizing
        self.height = self.animations['walk'].ss.y_dim * self.animations['walk'].ss.scale

        self.vel_x = 0  # we add and substract to this value based on keypresses
        self.vel_y = 0  # jumping or falling
        self.walking = False

        # Manual adjustments of player rect - as we use general draw() method from SpriteGroup(), the rect will position the surface, so need to be full size
        self.X_ADJ = self.animations['walk'].ss.scale * 44
        self.Y_ADJ = self.animations['walk'].ss.scale * 18

        # The main rect for the player sprite
        self.rect = pygame.Rect(x,y, self.width, self.height)  

        # Hitbox rect and spriteflip
        self.hitbox = pygame.Rect(x,y, self.width - self.X_ADJ, self.height - self.Y_ADJ)
        hitbox_image = pygame.Surface((self.width, self.height)).convert_alpha()
        hitbox_image.fill((0, 0, 0, 0))

        # To do efficient sprite collision check against monster groups, the hitbox need to be a Sprite, not just a rect
        self.hitbox_sprite = pygame.sprite.Sprite()
        self.hitbox_sprite.image = hitbox_image
        self.hitbox_sprite.rect = self.hitbox

        # Attack rect
        self.attack_rect = pygame.Rect(0,0,0,0)

        # Setting up sound effects
        sounds = GameAudio(1)  # TODO: remove level hardcoding
        self.fx_attack = sounds.player['attack']
        self.fx_jump = sounds.player['jump']
        self.fx_die = sounds.player['die']
        self.fx_hit = sounds.player['hit']
        self.fx_attack.set_volume(0.5)
        self.fx_jump.set_volume(0.5)
        self.fx_die.set_volume(0.5)
        self.fx_hit.set_volume(0.2)
        self.fx_attack_channel = pygame.mixer.Channel(0)  # we use separate channel to avoid overlapping sounds with repeat attacks

        # Status variables
        self.turned = False  # flip sprite/animations when moving left
        self.on_ground = False  # standing on solid ground
        self.state = WALKING  # we start walking always
        self.previous_state = None  # to check if we change state for sprite scaling etc.
        self.bouncing = False  # hit by something --> small bounce in the opposite direction
        self.last_env_damage = 0  # to manage frequency of damage
        self.last_attack = 0  # slowing down the attack
        self.attack_delay = 100

        self.world_x_pos = x + self.rect.width / 2 # player center x position across the whole world, not just screen

    def _manage_state_change(self) -> None:
        # Handles state changes 
        if self.state != self.previous_state:
            # New attack
            if self.state == ATTACKING:
                self.animation = self.animations['attack']
                self.animation.active = True
                
                # Attack rect
                if self.turned:
                    x = self.hitbox.left - self.hitbox.width / 2
                else:
                    x = self.hitbox.right

                self.attack_rect = pygame.Rect(x, self.rect.top + 30, self.rect.right - self.hitbox.right, 100) 

            # Dying
            if self.state == DYING:
                self.animation = self.animations['death']

            # Walking, jumping or idle
            if self.state == WALKING:  # the only other possible previous state is ATTACKING
                self.animation = self.animations['walk']
                self.animation.active = True
                self.attack_rect = None  # removing the attack rect

            self.previous_state = self.state
            self.animation.anim_counter = 0  # start over after transition

    def _flash(self) -> None: 
        coloured_image = pygame.Surface(self.image.get_size())
        coloured_image.fill(RED)
        
        final_image = self.image.copy()
        final_image.blit(coloured_image, (0, 0), special_flags = pygame.BLEND_MULT)
        self.image = final_image
 
    def check_game_over(self) -> bool:
        """ Manage the time from player is hit and dies until the death animation is complete and GAME OVER screen shows  """
        # print(f'self.death.anim_counter ({self.death.anim_counter})> self.death.frames ({self.death.frames})')  # DEBUG
        if  self.animations['death'].anim_counter == self.animations['death'].frames -1:
            self.state = DEAD
            return True
        else:
            return False

    def die(self) -> None:
        """ Starting the death animation and settings state to DYING """
        if self.state != DYING:
            self.state = DYING  # we start the death sequence
            self.animation = self.animations['death']
            self.animation.anim_counter = 0  # Animation counter the death animation
   
    def get_anim_image(self) -> None:
        # Once animation points to the correct state animation, we have our image
        anim_frame = self.animation.get_image().convert_alpha()
        anim_frame = pygame.transform.flip( anim_frame, self.turned, False)
        
        self.image = pygame.Surface((self.width, self.height)).convert_alpha()
        self.image.fill((0, 0, 0, 0))

        x_adjustment = 25  # to center the player image in the sprite

        if self.state == WALKING or self.state == DYING:
            self.image.blit(anim_frame, (x_adjustment, 0))
        if self.state == ATTACKING:
            # The sprite is larger when we attack, so we need to adjust center
            ATTACK_X = -2 * 64
            ATTACK_Y = -2 * 64
            self.image.blit(anim_frame,(ATTACK_X + x_adjustment, ATTACK_Y))

    def get_input(self) -> None:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.walking = 1  # right
            self.state = WALKING
            self.turned = False
            if self.on_ground == True:
                self.animations['walk'].active = True

        elif keys[pygame.K_LEFT]:
            self.walking = -1  # left
            self.state = WALKING
            self.turned = True
            if self.on_ground == True:
                self.animations['walk'].active = True
        else:
            self.walking = False

        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = - JUMP_HEIGHT
            self.animations['walk'].active = False
            self.state = WALKING
            self.on_ground = False
            self.fx_jump.play()

        if keys[pygame.K_SPACE]:
            # Updating the ready_to_attack flag 
            now = pygame.time.get_ticks()
            if now - self.last_attack > self.attack_delay:
                self.state = ATTACKING
                if not self.fx_attack_channel.get_busy():  # playing sound if not all channels busy
                    self.fx_attack_channel.play(self.fx_attack)
                self.last_attack = now
                
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit(0)

    def hazard_damage(self, damage: int, hits_per_second:int=0) -> None:
        """ Player has been in contact with enviromnmental damage, gets damage once or frequency per second """
        now = pygame.time.get_ticks()
        if now > self.last_env_damage + 1000 / hits_per_second:
            self.fx_hit.play()
            # Adjust health and bars
            self.health_current -= damage
            if self.health_current <= 0:
                self.health_current = 0
                self.die()
            self.health_bar_length = int(SCREEN_WIDTH / 6 * self.health_current / 1000)
            self.last_env_damage = now

    def heal(self, damage) -> None:
        """ Player is being healed """
        self.health_current += damage
        if self.health_current > self.health_max:
            self.health_current = self.health_max
        self.health_bar_length = int(SCREEN_WIDTH / 6 * self.health_current / 1000)

    def hit(self, damage: int, turned: bool, platforms) -> None:
        """ Player has been hit by mob or projectile, gets damage and bounces backs"""
        self.fx_hit.play()
        # Adjust health and bars
        self.health_current -= damage
        if self.health_current <= 0:
            self.health_current = 0
            self.die()

        self.health_bar_length = int(SCREEN_WIDTH / 6 * self.health_current / 1000)

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
        for platform in platforms:
            if platform.rect.colliderect(self.rect.x + x_bounce, self.rect.y, self.width - self.X_ADJ, self.height - self.Y_ADJ):
                x_bounce = 0

        self.rect.x += x_bounce * direction
        # Update world position 
        self.world_x_pos += x_bounce * direction

    def move(self, platforms) -> int:
        """ Movement as a result of keypresses as well as gravity and collision """
        dx = 0
        dy = 0
        scroll = 0

        self.hitbox.center = (self.rect.centerx, self.rect.centery + 10)  # updating hitbox location to follow player sprite
        
        # Moving left or right (also possible while attacking) and turning
        if self.state in (WALKING, ATTACKING):
            if self.walking == 1:  # right
                dx += WALKING_SPEED
                self.turned = False
                if self.on_ground:
                    self.animation.active = True
            elif self.walking == -1:  # left
                dx -= WALKING_SPEED
                self.turned = True
                if self.on_ground:
                    self.animation.active = True
            else:
                self.animation.active = False  # we're idle

        if self.state == ATTACKING: 
            self.animation.active = True
            if self.animation.anim_counter == self.animation.frames -1:  # reset after attack animation is complete
                self.animation.active = False  # stopping attack anim
                self.attack_rect = None
                self.state = WALKING
        
        if self.state == DYING:
            self.animation.active = True
            if self.animation.anim_counter == self.animation.frames -1:
                self.state = DEAD
        
        self._manage_state_change()  # manages state transitions

        # Gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Watch screen boundaries (effectively world boundaries since the screen scrolls to world edges before player can get to end of screen)
        if self.rect.left + dx < 0:
            dx = - self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right
        if self.rect.top + dy < 0:
            dy = - self.rect.top
            self.vel_y = GRAVITY
        
        
        # Check if player has reached scroll threshold to the LEFT (and we're not on the far left) + we're walking left
        if dx < 0 and self.rect.centerx <= SCROLL_THRESHOLD and self.world_x_pos > SCROLL_THRESHOLD + self.hitbox.width:
            scroll = -dx  # We scroll left by the opposite of the player's x speed
        
         # Check if player has reached scroll threshold to the right (and we're not on the far right) + we're walking right
        if dx > 0 and self.rect.centerx >= SCREEN_WIDTH - SCROLL_THRESHOLD and self.world_x_pos < TILE_SIZE * MAX_COLS - SCROLL_THRESHOLD:
            scroll = -dx  # We scroll right by the opposite of the player's x speed

        # Checking vertical collision with terrain (falling)
        for platform in platforms:
            # collision in the y direction only, so instead of using self.hitbox directly, we create
            # this temporaty rectangle with dy added for where the rectange _would_ be after the move (or we'd end up inside the platform)
            collision_rect = self.hitbox.copy() 
            collision_rect.centery += dy
            
            if platform.rect.colliderect(collision_rect):
                if self.hitbox.bottom < platform.rect.centery:  # Is player above platform?
                    if platform.solid == True:
                        if self.vel_y > 0:  # Is player falling?
                            dy = 0
                            self.on_ground = True
                            self.vel_y = 0
                    if platform.moving == True:  # We add the travel of the platform to the x pos of the player
                        self.rect.centerx += platform.dist_player_pushed
                        platform.dist_player_pushed = 0     
            
            # Checking horisontal collision - walking into terrain
            if platform.rect.colliderect(self.hitbox.x + dx, self.hitbox.y, self.width - self.X_ADJ, self.height - self.Y_ADJ):
                #print(f'platform.rect.x: {platform.rect.x}, platform.rect.y: {platform.rect.y} AND self.hitbox.x: {self.hitbox.x} and self.hitbox.y: {self.hitbox.y}')
                dx = 0


        # Update rectangle position
        self.rect.x += dx + scroll
        self.rect.y += dy 

        self.world_x_pos += dx

        if DEBUG_HITBOXES:
            pygame.draw.rect(self.screen, (128,128,128), self.hitbox, 2 )  # Player hitbox (GREY)
            pygame.draw.rect(self.screen, (255,255,255), self.rect, 2 )  # Player rect (WHITE)
            #pygame.draw.rect(self.screen, (255,0,255, 128), collision_rect, 2 )  # Ground colliosion rect (semitransparent purple)
            if self.attack_rect:
                pygame.draw.rect(self.screen, (255,0,0), self.attack_rect, 2 )  # attack rect (RED)

        return scroll
 
    def update(self, platforms) -> int:
        self.get_input()
        scroll = self.move(platforms)
        self.get_anim_image()
        return scroll
        

class PlayerInOut(pygame.sprite.Sprite):
    def __init__(self, x, y, inout) -> None:
        super().__init__()

        self.inout = inout

        if self.inout == 'in':
            self.in_x = x
            self.in_y = y
        
        if self.inout == 'out':
            self.out_x = x
            self.out_y = y
        
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))  #  empty surface
        self.rect = self.image.get_rect()



