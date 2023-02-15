import pygame
import logging
import math

from settings import *
from decor_and_effects import ExpandingCircle, SpeedLines


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, surface, audio, level_data: dict, game_state) -> None:
        # need also walk_anim, attack_anim, death_anim, sounds
        """
        The Player class constructor - note that x and y is only for initialization,
        the player position will be tracked by the rect, as the class inherits from the Sprite class
        Player is added to a sprite group, which then is used for calling the draw(method)
        """
        super().__init__()

        self.screen = surface

        self.gs = game_state  # contains keyboard and joystick events + health

        self.gs.player_health_max = PLAYER_HEALTH
        self.gs.player_health = self.gs.player_health_max

        self.level_data = level_data

        self.invincibility_duration = 500
        self.last_damage = 0

        # Setting up animations
        from animation_data import anim

        self.animations = {
            'idle': anim['player']['idle'],
            'walk': anim['player']['walk'],
            'attack': anim['player']['attack'],
            'death': anim['player']['death'],
            'cast':  anim['player']['cast'],
            'stomp': anim['player']['stomp']
        }

        self.state = {
            'active': IDLE,
            'next': IDLE,
        }

        self.rects = {
            'player': pygame.Rect,  # the rect for the full player sprite
            'attack': pygame.Rect,  # the rect for the player attack, to test collision with monsters and projectiles
        }
        
        self.animation = self.animations['idle']  # Idle by default
        self.image = self.animation.get_image()
        self.stomp_trigger = False
        self.stomp_trigger_lock = False  # we lock it after trigger to avoid duplicate triggers
        self.stomp_start_timer = 0  # we freeze for a second after a stomp (invulnerable)
        
        # Convert from original resolution to game resolution
        self.width = int(self.animations['walk'].ss.x_dim * self.animations['walk'].ss.scale * 1.4 )  # we make the sprite a bit wider so we can encapsulate the attack anim without resizing
        self.height = self.animations['walk'].ss.y_dim * self.animations['walk'].ss.scale

        self.vel_x = 0  # we add and substract to this value based on keypresses
        self.vel_y = 0  # jumping or falling
        self.walking = False

        self.destination = None  # we use this teleports and special effects wher the player is moved great distances in a flash (without a flash)

        # The main rect for the player sprite
        self.rects['player'] = pygame.Rect(x,y, self.width, self.height)  

        # Manual adjustments of hitbox rect - as we use general draw() method from SpriteGroup(), the rect will position the surface, so need to be full size
        # self.X_ADJ = self.animations['walk'].ss.scale * 44
        # self.Y_ADJ = self.animations['walk'].ss.scale * 10
        x_reduction = 150  # making the hitbox narrower
        y_reduction = 28  # making the hitbox shorter to better fit player

        self.rects['hitbox'] = pygame.Rect(0, 0, self.width - x_reduction, self.height - y_reduction)  # we ignore the x and y and center in next line instead
        self.rects['hitbox'].center = self.rects['player'].center

        # To do efficient sprite collision check against monster groups, the hitbox and collision box both need to be full Sprites, not just a rect, with an image
        self.hitbox_sprite = pygame.sprite.Sprite()
        self.collision_sprite = pygame.sprite.Sprite()
        self.side_collision_sprite = pygame.sprite.Sprite()

        empty_surf = pygame.Surface((self.width, self.height)).convert_alpha()
        empty_surf.fill((0, 0, 0, 0))
        self.hitbox_sprite.image = empty_surf
        self.collision_sprite.image = empty_surf
        self.side_collision_sprite.image = empty_surf

        self.hitbox_sprite.rect = self.rects['hitbox']
        self.collision_sprite.rect = pygame.Rect(0, 0, self.width - (x_reduction + 5) , self.height - y_reduction)  # narrower to see better
        self.side_collision_sprite.rect = self.rects['hitbox']
        
        # Setting up sound effects
        sounds = audio
        self.fx_attack = sounds.player['attack']
        self.fx_jump = sounds.player['jump']
        self.fx_die = sounds.player['die']
        self.fx_hit = sounds.player['hit']
        self.fx_stomp = sounds.player['stomp']
        self.fx_attack.set_volume(0.5)
        self.fx_jump.set_volume(0.5)
        self.fx_die.set_volume(0.5)
        self.fx_hit.set_volume(0.2)
        self.fx_attack_channel = pygame.mixer.Channel(0)  # we use separate channel to avoid overlapping sounds with repeat attacks

        # Status variables - initial values
        self.turned = False  # flip sprite/animations when moving left
        self.on_ground = False  # standing on solid ground
        self.on_slope = False  # we reduce the collision hitbox on slopes
        self.bouncing = False  # hit by something --> small bounce in the opposite direction
        self.last_env_damage = 0  # to manage frequency of damage
        self.last_attack = 0  # slowing down the attack
        self.attack_delay = 100
        self.last_cast = 0  # slowing down the cast
        self.cast_delay = 500
        self.cast_active = []  # all player spells
        self.world_x_pos = x + self.rects['player'].width / 2 # player center x position across the whole world, not just screen
        self.world_y_pos = y - self.rects['player'].height / 2 # player center y position across the whole world, not just screen (remember: up is negative y)
        self.v_scroll_initial = self.world_y_pos - V_SCROLL_THRESHOLD # just for the "camera" to see the player on the initial placement if he's not in the topleft screen


    def _check_collision(self, dx, dy, platforms) -> tuple:
        """ 
        Collision detection with terrain 
        """
        self.collision_sprite.rect.centery = self.hitbox_sprite.rect.centery + dy  # adding next-step y movement
        self.collision_sprite.rect.centerx = self.hitbox_sprite.rect.centerx  # aligning center
        
        # Checking vertical collision with terrain (falling), taking slope into account
        platform = pygame.sprite.spritecollideany(self.collision_sprite, platforms)
        if platform and platform.solid == True:  # player has collided with a solid platform
            if DEBUG_HITBOXES:
                pygame.draw.rect(self.screen, (128,128,255), platform.rect, 4 )  # self.rect - LIGHT BLUE

            if not platform.slope and platform.rect.top >= self.hitbox_sprite.rect.bottom:  # we are standing on the platform and it's a _flat_ platform
                self.on_slope = False
                dy = platform.rect.top - self.hitbox_sprite.rect.bottom  # the last y movement will cover the difference
            
                if platform.moving == True:  # the platform we're standing on moves, and moves us
                    self.rect.centerx += platform.dist_player_pushed
                    platform.dist_player_pushed = 0     

            if platform.slope:
                """ If we're on a sloped tile, we need to adjust the y position """
                self.on_slope = True
                h = TILE_SIZE_SCREEN
                adjustment = 15  # this is critical, as if we go too low, we'll fall through at the bottom
                x = self.rects['hitbox'].centerx - platform.rect.left
                # Steep, 45 degree slopes
                if platform.slope == 1:
                    y = h - x
                elif platform.slope == -1:
                    y = x
                # Shallower 22.5 degree slopes (always in pairs - 2 horis, 1 vert)
                elif platform.slope == 2:  # Going DOWN and right
                    if platform.slope_pos == -1:  # we're the left platform
                        y = h - x/2
                    if platform.slope_pos == 1: # we're on the right platform
                        y = h/2 - x/2
                elif platform.slope == -2:  # Going UP and right
                    if platform.slope_pos == -1:  # we're the left platform
                        y = x/2
                    if platform.slope_pos == 1: # we're on the right platform
                        y = h/2 + x/2
                else:
                    logging.error(f'Invalid value {platform.slope=}')
                
                y = math.ceil(y)  # only integers for coordinate positions


                dy = platform.rect.bottom - self.rects['hitbox'].bottom - y - adjustment  # from the bottom, as we add y which starts at platform.rect.bottom
                #print(f'{x=}, {y=}')  # debug
            self.vel_y = 0
            self.on_ground = True
            self.bouncing = False

            if platform.rect.bottom <= self.rects['hitbox'].top:  # we bumped into a platform from below 
                dy = 0
                self.vel_y = GRAVITY 
                self.bouncing = False

                    
        # Checking horisontal collision with 3 scenarios:

        if dx:
            self.side_collision_sprite.rect.centery = self.hitbox_sprite.rect.centery
            if dx > 0:  # going right
                self.side_collision_sprite.rect.centerx = self.hitbox_sprite.rect.centerx + 10
            if dx < 0:  # going left
                self.side_collision_sprite.rect.centerx = self.hitbox_sprite.rect.centerx - 10

            platform = pygame.sprite.spritecollideany(self.side_collision_sprite, platforms)
            if platform and platform.solid == True and not platform.slope:  # player has collided with a solid platform and is not walking a slope
                dx = 0
           
            if DEBUG_HITBOXES:
                pygame.draw.rect(self.screen, '#f6e445', self.side_collision_sprite.rect, 6)  # horizontal collision test, re-using collider sprite - YELLOW

        return dx, dy


    def _flash(self) -> None:   # TODO: nothing works as a new image with be generated by move() before the screen is updated
        coloured_image = pygame.Surface(self.image.get_size())
        coloured_image.fill(RED)
        
        final_image = self.image.copy()
        final_image.blit(coloured_image, (0, 0), special_flags = pygame.BLEND_MULT)
        self.image = final_image
    

    def _state_engine(self) -> None:
        """
        Manage state changes

        If state['next'] is different from state['active]...
        
        """
        if self.state['next'] != self.state['active']:

            # --> Idle
            if self.state['next'] == IDLE:
                # If we were attacking, and now we're done with the animation (if not, we ignore for now)
                if self.state['active'] == ATTACKING and self.animation.on_last_frame:
                    self.state['active'] = IDLE
                    self.animation = self.animations['idle']
                    self.animation.start_over()  # important as if we're starting a new game, the animation might be in a random state
                    self.animation.active = True

                # If we were walking, and now we're done with the animation (if not, we ignore for now)
                if self.state['active'] == WALKING and self.animation.on_last_frame:
                    self.state['active'] = IDLE
                    self.animation = self.animations['idle']
                    self.animation.start_over()
                    self.animation.active = True

                # If we were casting, and now we're done with the animation (if not, we ignore for now)
                if self.state['active'] == CASTING and self.animation.on_last_frame:
                    self.state['active'] = IDLE
                    self.animation = self.animations['idle']
                    self.animation.start_over()
                    self.animation.active = True

                # If we were jumping and have landed, we switch right away
                if self.state['active'] == JUMPING and self.on_ground:
                    self.state['active'] = IDLE
                    self.animation = self.animations['idle']
                    self.animation.start_over()
                    self.animation.active = True

                # If we were stomping and have landed, we trigger effect right away, but we stay in state for one second
                if self.state['active'] == STOMPING and self.on_ground:
                    now = pygame.time.get_ticks()
                    if now - self.stomp_start_timer > 500 and self.stomp_trigger_lock == True:
                        self.state['active'] = IDLE
                        self.animation = self.animations['idle']
                        self.animation.start_over()
                        self.animation.active = True
                        self.stomp_trigger_lock = False  # we unlock triggering the effect again, as we're now changing state
                    else:
                        if not self.stomp_trigger_lock:  # before 1000ms has passed, we trigger the effect and lock it
                            self.stomp_trigger = True
                            self.stomp_trigger_lock = True
                            self.stomp_start_timer = now


            # --> Jumping
            if self.state['next'] == JUMPING:
                # Jumping, like attacking, interrupts anything 
                self.state['active'] = JUMPING
                self.animation = self.animations['walk']
                self.animation.frame_number = -1  # last frame of walk anim is also jump anim for stabby
                self.animation.active = False
               
            # --> Walking
            if self.state['next'] == WALKING:
                # If we were attacking, and now we're done with the animation (if not, we ignore for now)
                if self.state['active'] == ATTACKING and self.animation.on_last_frame:
                    self.state['active'] = WALKING
                    self.animation = self.animations['walk']
                    self.animation.start_over()
                    self.animation.active = True

                # If we were idle, we start walking straight away
                if self.state['active'] == IDLE:
                    self.state['active'] = WALKING
                    self.animation = self.animations['walk']
                    self.animation.start_over()
                    self.animation.active = True

                # If we were jumping, and we're bak on the ground, we start stright away
                if self.state['active'] == JUMPING and self.on_ground:
                    self.state['active'] = WALKING
                    self.animation = self.animations['walk']
                    self.animation.start_over()
                    self.animation.active = True
    
            # --> Attacking 
            if self.state['next'] == ATTACKING:
                # Attack interrupts anything
                self.state['active'] = ATTACKING
                self.animation = self.animations['attack']
                self.animation.start_over()
                self.animation.active = True

            # --> Stomping
            if self.state['next'] == STOMPING:
                # Attack interrupts anything
                self.state['active'] = STOMPING
                self.animation = self.animations['stomp']
                self.animation.start_over()
                self.animation.active = True
                stomp_streaks = SpeedLines(self.hitbox_sprite.rect)
                self.cast_active.append(stomp_streaks)

            # --> Casting 
            if self.state['next'] == CASTING:
                # Cast interrupts anything
                self.state['active'] = CASTING
                self.animation = self.animations['cast']
                self.animation.start_over()
                self.animation.active = True

                # test expanding circle TODO: TEST TEST DEBUG
                circle1 = ExpandingCircle(self.hitbox_sprite.rect.centerx, self.hitbox_sprite.rect.centery, WHITE, 30, 300,10)
                circle2 = ExpandingCircle(self.hitbox_sprite.rect.centerx, self.hitbox_sprite.rect.centery, WHITE, 30, 200,10)
                circle3 = ExpandingCircle(self.hitbox_sprite.rect.centerx, self.hitbox_sprite.rect.centery, WHITE, 30, 100,10)
                self.cast_active.append(circle1)
                self.cast_active.append(circle2)
                self.cast_active.append(circle3)


            # --> Dying, running through death animation until dead
            if self.state['next'] == DYING:
                self.animation = self.animations['death']
                self.animation.active = True
                self.animation.start_over()
                self.state['active'] = DYING
                logging.debug('--- DYING ---')
                

            # --> Dead, of the animation has run to the end
            if self.state['next'] == DEAD:
                self.state['active'] = DEAD
                logging.debug('--- DEAD ---')
                pygame.time.wait(3000)  # we freeze the game to look at your corpse for a moment

             
    def actions(self, platforms: pygame.sprite.Group ) -> tuple:
        """ Movement as a result of keypresses as well as gravity and collision """
        dx = 0
        dy = 0
        h_scroll = 0
        v_scroll = 0

        # Initial adjustment of "camera" on first update
        if self.v_scroll_initial:
            if self.v_scroll_initial > self.world_y_pos - V_SCROLL_THRESHOLD:
                self.v_scroll_initial = self.world_y_pos - V_SCROLL_THRESHOLD
            v_scroll = -self.v_scroll_initial
            self.v_scroll_initial = False
        
        # If we've been hit, we're invincible - check if it's time to reset
        if self.gs.player_invincible and self.state['active'] not in (DYING, DEAD):
            if pygame.time.get_ticks() - self.last_damage > self.invincibility_duration:
                self.gs.player_invincible = False

        # Making sure stomp is limited
        if self.gs.player_stomp_counter > PLAYER_STOMP:
            self.gs.player_stomp_counter = PLAYER_STOMP

        # updating hitbox location to follow player sprite
        self.rects['hitbox'].center = (self.rects['player'].centerx, self.rects['player'].centery) 

        # DYING
        if self.state['active'] == DYING:
            self.bouncing = False
            self.gs.player_invincible = True  # prevents monsters triggering events on our corpse
            if self.animation.on_last_frame:
                self.state['next'] = DEAD

        # WALKING, JUMPING and ATTACKING: player still moves (even if attacking )
        if self.state['active'] in (WALKING, JUMPING, ATTACKING):  
            if self.walking == 1:  # right
                dx += WALKING_SPEED
                self.turned = False
            elif self.walking == -1:  # left
                dx -= WALKING_SPEED
                self.turned = True

        # JUMPING: landed yet?
        if self.state['active'] == JUMPING and self.vel_y == 0:
            self.state['next'] = IDLE

          
        # STOMPING
        if self.state['active'] == STOMPING:
            if self.vel_y > 0:  # we're still airborne
                dy = STOMP_SPEED  # added straight to position, not going via velocity

            if not self.on_ground:
                x = self.hitbox_sprite.rect.left
                y = self.hitbox_sprite.rect.top

            if self.on_ground:
                self.state['next'] = IDLE
        

        
        # ATTACKING: make rect
        if self.state['active'] == ATTACKING:
            if self.turned:
                x = self.rects['player'].left
            else:
                x = self.rects['hitbox'].right

            self.rects['attack'] = pygame.Rect(x, self.rects['player'].top + 30, self.rects['player'].right - self.rects['hitbox'].right, 100) 
        
        # if we are NOT attacking, remove the rectangle
        else:
            self.rects['attack'] = None

        # CASTING - returning to idle after one run of animation
        if self.state['active'] == CASTING and self.animation.on_last_frame:
            self.state['next'] = IDLE


        # Gravity
        self.vel_y += GRAVITY

        if dy < STOMP_SPEED:  # we use the STOMP_SPEED as a speed limit
            dy += int(self.vel_y)

        # Bounce (in x-direction, y is handled by gravity)
        if self.bouncing:
            dx += self.vel_x

        # Watch screen boundaries (effectively world boundaries since the screen h_scrolls to world edges before player can get to end of screen)
        if self.rects['hitbox'].left + dx < 0:
            dx = - self.rects['player'].left
        if self.rects['hitbox'].right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rects['player'].right
        
        # Check collision with terrain
        (dx, dy) = self._check_collision(dx, dy, platforms)


        
         # Checking if we suddenly have a teleport destination and if so, we plonk straight over
        if self.destination:
            dx = -(self.world_x_pos - self.destination[0])  # horizontal distance between portals 
            dy = -(self.world_y_pos - self.destination[1])  # vertical distance between portals
            h_scroll = -dx
            v_scroll = -dy
            # TODO: we could center screen on player?
            self.destination = None

        """ Scrolling horizontally or vertically if player reaches either of the four scroll thresholds (left/right/top/bottom)
            These conditions should not be triggered by teleporting above
        """
        # Check if player has reached h_scroll threshold to the LEFT (and we're not on the far left) + we're walking left
        if dx < 0 and self.rects['player'].centerx <= H_SCROLL_THRESHOLD and self.world_x_pos > H_SCROLL_THRESHOLD + self.rects['hitbox'].width:
            h_scroll = -dx  # We h_scroll left by the opposite of the player's x movement
        
         # Check if player has reached h_scroll threshold to the right (and we're not on the far right) + we're walking right
        if dx > 0 and self.rects['player'].centerx >= SCREEN_WIDTH - H_SCROLL_THRESHOLD and self.world_x_pos < TILE_SIZE_SCREEN * self.level_data['size_x'] - H_SCROLL_THRESHOLD:
            h_scroll = -dx  # We h_scroll right by the opposite of the player's x movement

         # Check if player has reached v_scroll threshold on top of the screen (and we're not all the way to the top) + we're moving upwards
        if dy < 0 and self.rects['player'].centery <= V_SCROLL_THRESHOLD and self.world_y_pos > V_SCROLL_THRESHOLD + self.rects['hitbox'].height:
            v_scroll = -dy  # We scroll up by the opposite of the player's y movement

         # Check if player has reached v_scroll threshold at bottom of the screen (and we're not all the way down at the bottom) + we're moving downwards
        scroll_buffer_bottom = 320
        if dy > 0 and self.rects['player'].centery >= SCREEN_HEIGHT - V_SCROLL_THRESHOLD and \
            self.world_y_pos < TILE_SIZE_SCREEN * self.level_data['size_y']  - scroll_buffer_bottom:  # the very bottom
            v_scroll = -dy  # We h_scroll down by the opposite of the player's y movement

        # Update rectangle position
        self.rects['player'].x += dx + h_scroll
        self.rects['player'].y += dy + v_scroll

        self.world_x_pos += dx
        self.world_y_pos += dy
        #print(f"Player's centerY: {self.rects['player'].centery} and world_y_pos: {self.world_y_pos} - scroll threshold towards bottom is: {TILE_SIZE_SCREEN * self.level_data['size_y'] - V_SCROLL_THRESHOLD}, and death at {TILE_SIZE_SCREEN * self.level_data['size_y']}")

        # If we fall off the world we die
        if self.world_y_pos > TILE_SIZE_SCREEN * self.level_data['size_y']:
            self.state['next'] = DEAD
            logging.debug('DEAD: fell off the world')
            self._state_engine()  # we call the state engine to get an out-of-turn state update

        return h_scroll, v_scroll
    

    def get_anim_image(self) -> None:
        """ 
        Update the image of self, which is called by SpriteGroup.draw() method 
        """
        # Once animation points to the correct state animation, we have our image
        anim_frame = self.animation.get_image().convert_alpha()
        anim_frame = pygame.transform.flip( anim_frame, self.turned, False)
        
        self.image = pygame.Surface((self.width, self.height)).convert_alpha()
        self.image.fill((0, 0, 0, 0))

        x_adjustment = 25  # to center the player image in the sprite
        y_adjustment = 0
        
        self.image.blit(anim_frame, (x_adjustment, y_adjustment))

    def get_input(self) -> None:
        """ Registering keypresses and triggering state changes """
        if self.state['active'] not in (DYING, DEAD):  # we only do this if we're still alive
            if self.gs.user_input['right']:
                self.walking = 1  # right
                self.state['next'] = WALKING
                self.turned = False

            if self.gs.user_input['left']:
                self.walking = -1  # left
                self.state['next'] = WALKING
                self.turned = True

            else:
                self.walking = False
                self.state['next'] = IDLE

            if self.gs.user_input['up'] and self.on_ground:
                self.vel_y = - JUMP_HEIGHT

                self.state['next'] = JUMPING
                self.on_ground = False
                self.fx_jump.play()

            if self.gs.user_input['down'] and not self.on_ground and self.gs.player_stomp_counter == PLAYER_STOMP:
                self.vel_y = 3
                self.state['next'] = STOMPING
                self.fx_stomp.play()

            if self.gs.user_input['attack']:
                now = pygame.time.get_ticks()
                if now - self.last_attack > self.attack_delay:
                    self.state['next'] = ATTACKING
                    if not self.fx_attack_channel.get_busy():  # playing sound if not all channels busy
                        self.fx_attack_channel.play(self.fx_attack)
                    self.last_attack = now

            if self.gs.user_input['cast']:
                now = pygame.time.get_ticks()
                if now - self.last_cast > self.cast_delay:
                    self.state['next'] = CASTING
                    #if not self.fx_attack_channel.get_busy():  # playing sound if not all channels busy
                    #    self.fx_attack_channel.play(self.fx_attack)
                    self.last_cast = now
        
        if self.gs.user_input['quit']:
            logging.debug('Player quested quit - quitting...')
            pygame.quit()
            exit(0)

    def hazard_damage(self, damage: int, hits_per_second:int=0) -> None:
        """ Player has been in contact with enviromnmental damage, gets damage once or frequency per second """
        now = pygame.time.get_ticks()
        if now > self.last_env_damage + 1000 / hits_per_second:
            self.fx_hit.play()
            # Adjust health and bars
            self.gs.player_health -= damage
            self.gs.player_stomp_counter = 0  # reset stomp on hit
            if self.gs.player_health <= 0:
                self.gs.player_health = 0                                    
                self.state['next'] = DYING
                self._state_engine()  # we call the state engine to get an out-of-turn state update

            self.health_bar_length = int(SCREEN_WIDTH / 6 * self.gs.player_health / 1000)
            self.last_env_damage = now


    def heal(self, damage) -> None:
        """ Player is being healed """
        self.gs.player_health += damage
        if self.gs.player_health > self.gs.player_health_max:
            self.gs.player_health = self.gs.player_health_max
        self.health_bar_length = int(SCREEN_WIDTH / 6 * self.gs.player_health / 1000)

    def hit(self, damage: int, turned: bool, platforms: pygame.sprite.Group) -> None:
        """ Player has been hit by mob or projectile, gets damage and bounces backs"""
        if not self.gs.player_invincible:  # we have half a sec of invincibility after damage to avoid repeat damage
            if damage:  # we also use hits without damage to bump the player
                self._flash()
                self.fx_hit.play()
                self.gs.player_invincible = True  # we want 
                self.gs.player_hit = True
                self.last_damage = pygame.time.get_ticks()  
                self.gs.player_stomp_counter = 0  # reset stomp on hit
                # Adjust health and bars
                self.gs.player_health -= damage
                if self.gs.player_health <= 0:
                    self.gs.player_health = 0
                    self.state['next'] = DYING

                

                #self.health_bar_length = int(SCREEN_WIDTH / 6 * self.gs.player_health / 1000)

                self._state_engine()  # we call the state engine to get an out-of-turn state update

            if self.state['next'] != DYING:  # if we just got killed we skip the bounce
                self.bounce(5, -15, turned, platforms)

               

    def bounce(self, x: int, y: int, turned: bool, platforms: pygame.sprite.Group) -> None:
        direction = 1
        if turned:
            direction = -1

        # Bounce back
        x_bounce = x * direction
        y_bounce = y
        self.on_ground = False

        if not self.bouncing:
            self.vel_x = x_bounce
            self.vel_y = y_bounce
            self.bouncing = True

        # Prevent us getting bounced inside platforms
        for platform in platforms:
            if platform.rect.colliderect(self.rects['hitbox'].x + x_bounce, (self.rects['hitbox'].y + y_bounce), self.rects['hitbox'].width , self.rects['hitbox'].height):
                x_bounce = 0
                self.vel_x = 0


    def update(self, platforms) -> tuple:
        self.get_input()
        self._state_engine()
        self.rect = self.rects['player']
        h_scroll, v_scroll = self.actions(platforms)
        self.get_anim_image()
        return h_scroll, v_scroll
        

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
        
        self.image = pygame.Surface((TILE_SIZE_SCREEN, TILE_SIZE_SCREEN))  #  empty surface
        self.rect = self.image.get_rect(center=(x + TILE_SIZE_SCREEN/2, y + TILE_SIZE_SCREEN/2))

    def update(self, h_scroll, v_scroll) -> None:
        self.rect.centerx += h_scroll
        self.rect.centery += v_scroll