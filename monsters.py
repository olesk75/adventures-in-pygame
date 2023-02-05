"""
Monster (pygame Sprite class)       : base class for all mobs
Projectile (pygame Sprite class)    : class for all projectiles (arrows etc.)
Spell (pygame Sprite class)         : class for spells - player and monster spells both
Drop (pygame Sprite class)          : dropped items, like keys dropped by bosses
"""


import random
import pygame
import logging
import copy

from settings import *
from monster_data import MonsterData


class Monster(pygame.sprite.Sprite):
    def __init__(self,x, y, surface, monster_type) -> None:
        """
        The Player class constructor - note that x and y is only for initialization,
        the player position will be tracked by the rect
        """
        super().__init__()
        self.gravity = 0.5 
        self.data = MonsterData(monster_type)
        self.screen = surface

        from animation_data import anim

        # Setting up state animations

        # Setting up animations
        self.animations = {
            'idle': None,  # TODO
            'walk': copy.copy(anim[monster_type]['walk']),
            'attack': copy.copy(anim[monster_type]['attack']),
            'death': copy.copy(anim[monster_type]['death']),
            'cast': copy.copy(anim[monster_type]['cast'])
        }

        self.cast_player_pos = ()

        self.animation = self.animations['walk']  # setting active animation
        self.animation.active = True

        self.image = self.animations['walk'].get_image()
        self.width = self.animations['walk'].ss.x_dim * self.animations['walk'].ss.scale
        self.height = self.animations['walk'].ss.y_dim * self.animations['walk'].ss.scale

        # Setting up sprite's rectangle
        self.X_ADJ = self.animations['walk'].ss.scale * 44
        self.Y_ADJ = self.animations['walk'].ss.scale * 18
        self.rect = self.image.get_rect()
        self.rect.center = (x ,y)

        # Hitbox rect and sprite
        self.hitbox = pygame.Rect(x,y, self.width - self.X_ADJ, self.height - self.Y_ADJ)
        
        self.rect_detect = pygame.Rect(0,0,0,0)
        self.rect_attack = pygame.Rect(0,0,0,0)
   
        self.vel_y = 0
        self.turned = False
        self.at_bottom = False
        self.state = WALKING  # we init in walking state
        self.last_attack = 0
        self.last_arrow = 0
        self.ready_to_attack = True  
        self.score_flag = False  # We can only add more score when this is True
        self.prev_y_lvl = self.rect.y  # Tracking vertical progress

        self.currently_casting = None  # if the mob is busy casting, this is what it is casting
        self.cast_anim_list = []  # if the mob casts a spell, we creat animations here


    def create_rects(self) -> None:
        """
        Creating rects for monster hitbox, detection range and attack damage range
        To cater for monster sprites of various sizes (including walk/attack/cast being different), 
        we always draw from sprite centerx and centery as reference.
        """
        # Updating the HITBOX collision rectangle
        self.hitbox = pygame.Rect(self.rect.centerx - self.data.hitbox_width / 2, self.rect.centery - self.data.hitbox_height / 2, \
            self.data.hitbox_width, self.data.hitbox_height)

        # Creating a DETECTION rect where to mob will attack if the player rect collides
        x = self.rect.centerx
        y = self.rect.centery - (self.data.detection_range_high * self.rect.height / 2)  # top of rect depends if we have high detection range True or not

        width = self.data.detection_range
        height = self.rect.height / 2
        if self.data.detection_range_high:
            height = self.rect.height

        if self.turned:       
            self.rect_detect = pygame.Rect(x - width, y, width, height) 
        else:
            self.rect_detect = pygame.Rect(x, y,width, height) 
        
        # Creating an ATTACK rect 
        if self.state == ATTACKING:
            x = self.rect.centerx
            y = self.rect.centery
            height = self.height / 2
            if self.turned:
                self.rect_attack = pygame.Rect(x - self.data.attack_range, y, self.data.attack_range, height) 
            else:
                self.rect_attack = pygame.Rect(x , y, self.data.attack_range, height) 

    def _check_platform_collision(self, dx, dy, platforms_sprite_group) -> None:
         #
        # Checking platform collision to prevent falling and to turn when either at end of platform or hitting a solid tile
        #
        all_platforms = platforms_sprite_group.sprites()
        for platform in all_platforms:
            if platform.solid == True:
                # collision in the y direction only, using a collision rect indicating _next_ position (y + dy)
                moved_hitbox = self.hitbox.move(0, dy - 2)  # move in place - remove 2 to anchor the sprites on the ground properly
            
                if platform.rect.colliderect(moved_hitbox):  # we are standing on a platform essentially
                    # Preventing falling through platforms
                    if moved_hitbox.bottom > platform.rect.top:  # Is player above platform?
                        if self.vel_y > 0:
                            dy = 0
                            self.at_bottom = True                     
                            self.vel_y = 0

                    if self.state != DEAD:  # Corpses should not fall through platforms, but also won't move to the rest here is pointless for the dead
                        # Preventing falling off left/right edge of platforms if there is NO collision (-1) to the side and down (and it's not a jumping mob
                        moved_hitbox = self.hitbox.move(-self.hitbox.width, 40)  # checking left 
                        if  moved_hitbox.collidelist(all_platforms) == -1 and not self.data.attack_jumper:
                            self.data.direction = 1
                            self.turned = False

                        moved_hitbox = self.hitbox.move(self.hitbox.width, 40)  #checking right
                        if moved_hitbox.collidelist(all_platforms) == -1 and not self.data.attack_jumper:
                            self.data.direction = -1
                            self.turned = True
                    
                        # Turning around if hitting a solid tile  
                        moved_hitbox = self.hitbox.move(dx * 5 * self.data.direction, 20).inflate(0,-60)

                        if platform.rect.colliderect(moved_hitbox):
                            self.data.direction *= -1
                            self.rect.x += dx * 20  * self.data.direction # far enough to avoid re-triggering in an endless loop
                            self.turned = not self.turned

    def _boss_battle(self, player) -> tuple:
        """ Movement and attacks for specific bosess 
            returns: dx and dy for mob (replaces the normal walking/bumping dx/dy for regular mobs)
        """
        dx = 0  # these are absolute moves, not speed 
        dy = 0  # speed equivalent
        
        def _casting() -> None:
            sprite_size = 32
            if self.animation.on_last_frame:  # on last cast animation frame, trigger the spell
                if self.currently_casting == 'firewalker':
                    attack_width = 12
                    for a in range(attack_width):
                        player_center_x = self.cast_player_pos[0]
                        player_bottom_y = self.cast_player_pos[1]

                        self.cast_anim_list.append(['fire', player_center_x - sprite_size * a/2, player_bottom_y - sprite_size * 2])    
                        self.cast_anim_list.append(['fire', player_center_x + sprite_size * a/2, player_bottom_y - sprite_size * 2])

                    self.state_change(WALKING)
                    self.currently_casting = ''

        if self.data.monster ==  'skeleton-boss':
            if self.state == ATTACKING:
                # Random transitions from ATTACKING to CASTING
                for attack in self.data.boss_attacks:
                    attack_type = attack[0]
                    attack_prob = attack[1]
                    if attack_prob > random.random() and not player.vel_y and not self.vel_y:  # Random roll, if neither player nor mob is not in the air
                        self.state_change(CASTING, attack_type=attack_type, player_pos=(player.rect.centerx, player.rect.bottom))
                        dx = 0  # we stop to cast
                    else:
                        dx = self.data.speed_attacking  # if not, we just keep the attack speed
            
                        # Sometimes a jumping mob can jump if player is higher than the mob and mob is attacking
                        max_dist_centery = -7
                        player_above_mob = player.rect.centery -  (self.rect.centery + max_dist_centery)
                        if self.data.attack_jumper and player_above_mob < 0 and self.vel_y == 0:  # player is higher up and we're not already jumping
                            if 0.01  > random.random():  # hardcoded jump probability
                                self.vel_y = -10

            elif self.state == CASTING:
                _casting()

            elif self.state == WALKING:
                    dx = self.data.speed_walking  #  we start at walking speed

                    # We throw in random changes in direction, different by mod type
                    if self.data.random_turns / 100  > random.random():
                        dx *= -1
                        self.data.direction *= -1
                        self.turned = not self.turned

            elif self.state == DYING:
                self.hitbox = pygame.Rect(0,0,0,0)
                if self.animation.on_last_frame:
                    logging.debug(f'BOSS {self.data.monster} dies')
                    self.state = DEAD

            else:
                print(f'ERROR, wrong state for monster in boss fight: {self.state}')
                exit(1)

        return dx, dy

    def state_change(self, new_state:int, attack_type:str=None, player_pos:tuple=None) -> None:
        """
        Manages all state changes for mobs, betweeh ATTACKING, WALKING and CASTING
        Can take attack type and player position if we're switching into CASTING
        (we need player pos to fire a spell at where the player was once we started casting)
        """
        if new_state != self.state:  # only do something if we have a _change_ in state
            self.state = new_state
            if new_state == ATTACKING:
                if self.ready_to_attack:  # if previous attack is done
                    self.animation = self.animations['attack']
                    self.animation.active = True

                    self.last_attack = pygame.time.get_ticks()  # recording time of last attack

                    if self.data.sound_attack:
                        self.data.sound_attack.set_volume(self.data.sound_attack_volume)
                        self.data.sound_attack.play()

            elif new_state == WALKING:
                    self.animation = self.animations['walk']
                    self.animation.active = True
                    self.rect_attack = pygame.Rect(0,0,0,0)  # disabling attack rect

            elif new_state == CASTING:
                    self.animation = self.animations['cast']
                    self.animation.active = True
                    
                    self.currently_casting = attack_type
                    self.cast_player_pos = player_pos

                    if self.data.caster:
                        self.data.sound_cast.play()

            elif new_state == DYING:
                    self.animation = self.animations['death']
                    self.animation.active = True
                    self.animation.frame_number = 0
                    self.rect_attack = pygame.Rect(0,0,0,0)
                    self.rect_detect = pygame.Rect(0,0,0,0)
                    self.hitbox = pygame.Rect(0,0,0,0)

            elif new_state == DEAD:
                    print('DEAD')
                    self.animation.active = False
                    self.animation.frame_number = 0  # make ready for next death from same monster, as we reuse the same animation instance
                    self.image = self.animation.frame[-1]

                    if self.data.sound_death:
                        self.data.sound_death.set_volume(self.data.sound_death_volume)
                        self.data.sound_death.play()

            new_rect = self.animation.get_image().get_rect()  # we need to scale back to walking image size after an attack
            new_rect.center = self.rect.center
            self.rect = new_rect

    def update(self, scroll, platforms_sprite_group, player) -> None:
        dx = 0
        dy = self.vel_y  # Newton would be proud!

        """ Boss battles have separate logic depending on each boss - if they cast anything, we get a list of animations back as well
            the boss_battle function updates self.vel_y directly and adds self.
        """
        if self.data.boss:
            dx, dy = self._boss_battle(player)
        else:
        # Regular mobs simply walk around mostly

            if self.state == ATTACKING:
                dx = self.data.speed_attacking
            
                # Sometimes a jumping mob can jump if player is higher than the mob and mob is attacking
                #print(f'player.rect.centery: {player.rect.centery}, self.rect.center: {self.rect.centery }')
                max_dist_centery = -7
                player_above_mob = player.rect.centery -  (self.rect.centery + max_dist_centery)
                #print(f'player is this much above attacking mob: {player_above_mob}')

                if self.data.attack_jumper and player_above_mob < 0 and self.vel_y == 0:  # player is higher up and we're not already jumping
                    if 0.01  > random.random():  # hardcoded jump probability
                        self.vel_y = -10
            if self.state == WALKING:
                dx = self.data.speed_walking  #  we start at walking speed

                # We throw in random cahnges in direction, different by mod type
                if self.data.random_turns / 100  > random.random():
                    dx *= -1
                    self.data.direction *= -1
                    self.turned = not self.turned


        # we compensate for scrolling
        self.rect.x += scroll

        # we compensate for graivty
        self.vel_y += self.gravity  # allows us to let mobs fall
        dy += self.vel_y
        
        # Update rectangle position
        self.rect.x += dx * self.data.direction
        self.rect.y += dy 

        # Checking detection, hitbox and attack rects as well as platform rects for collision
        self.create_rects()
        self._check_platform_collision(dx, dy, platforms_sprite_group)
        if self.state in (DEAD, DYING):
            self.rect_attack = None
            self.rect_detect = None
            self.hitbox = None
        
        # Dying, waiting for anim to run to the end
        if self.state == DYING and self.animation.on_last_frame:
            self.state = DEAD


        # Updating the ready_to_attack flag 
        now = pygame.time.get_ticks()
        if now - self.last_attack > self.data.attack_delay:
            self.ready_to_attack = True
        else:
            self.ready_to_attack = False


        # Get the correct image for the SpriteGroup.update()
        if self.state == CASTING:
            self.image = self.animations['cast'].get_image().convert_alpha()
            self.image = self.animations['cast'].get_image(repeat_delay = self.data.cast_delay)
        elif self.state == ATTACKING:
            # If we have a diffent size attack sprites, we need to take scale into account
            self.image = self.animations['attack'].get_image(repeat_delay = self.data.attack_delay).convert_alpha()
        elif self.state == DYING:
            self.image = self.animation.get_image()
        elif self.state == WALKING:
            self.image = self.animation.get_image()
        elif self.state == DEAD:
            self.image = self.animation.get_image()
            
        self.image = pygame.transform.flip(self.image, self.turned, False)        

        if DEBUG_HITBOXES:
            pygame.draw.rect(pygame.display.get_surface(), (255,255,255), self.rect, 4 )  # self.rect - WHITE
            if self.hitbox:
                pygame.draw.rect(pygame.display.get_surface(), (128,128,128), self.hitbox, 2 )  # Hitbox rect (grey)
            if self.rect_attack:
                pygame.draw.rect(pygame.display.get_surface(), (255, 0, 0), self.rect_attack, 4 )  # attack rect - RED
            if self.rect_detect:
                pygame.draw.rect(pygame.display.get_surface(), (0,0,128), self.rect_detect, 2 )  # Detection rect - BLUE


class Projectile(pygame.sprite.Sprite):
    def __init__(self,x, y, image, turned, scale = 1) -> None:
        """
        The Projector class constructor - note that x and y is only for initialization,
        the projectile position will be tracked by the rect
        NOTE: no animation - one image only!
        """
        super().__init__()
        self.image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))

        self.speed = 10
        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.turned = turned
        
    def update(self, scroll, platforms_sprite_group) -> None:
        
        # we set start speeds for x and y
        dx = self.speed
        if self.turned:
            dx = -self.speed
            
        dy = 0  # projectiles have no gravity

        # we compensate for scrolling
        self.rect.x += scroll

        # Update rectangle position
        self.rect.x += dx 
        self.rect.y += dy 

        # Collision with platform
        if pygame.sprite.spritecollideany(self, platforms_sprite_group):
            self.kill()
        
        # Ready for super.draw()
        self.image = pygame.transform.flip( self.image.convert_alpha(), self.turned, False)


class Spell(pygame.sprite.Sprite):
    def __init__(self, x, y, anim, turned, scale = 1) -> None:
        """
        The Spell class constructor - note that x and y is only for initialization,
        the spell position will be tracked by the rect
        NOTE: Animation, but only _one_ animation cycle
        """
        super().__init__()
        self.anim = anim
        self.anim.active = True
        self.anim.counter = 0
        image = anim.get_image()

        self.image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))

        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.turned = turned

        self.anim.first_done = False
        
    def update(self, scroll) -> None:
        self.rect.x += scroll  # we compensate for scrolling

        # Done with one cycle, as spell do not repeat (yet!)
        if self.anim.first_done:
            self.currently_casting = False
            self.kill()

        self.image = pygame.transform.flip( self.anim.get_image().convert_alpha(), self.turned, False)


class Drop(pygame.sprite.Sprite):
    def __init__(self, x, y, anim, turned= False, scale = 1, drop_type=None):
        """
        The Drop class constructor - object animates in place until kill()
        NOTE: continious animation
        """
        super().__init__()
        self.scale = scale
        self.drop_type = drop_type  # key, health potion etc.
        self.anim = anim
        self.anim.active = True
        self.anim.counter = 0
        image = anim.get_image()

        self.image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))

        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.turned = turned
        
    def update(self, scroll) -> None:
        self.rect.x += scroll # we compensate for scrolling

        self.image = pygame.transform.flip( self.anim.get_image().convert_alpha(), self.turned, False) 
        #self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.scale, self.image.get_height() * self.scale))
        
