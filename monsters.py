"""
Monster (pygame Sprite class)       : base class for all mobs
Projectile (pygame Sprite class)    : class for all projectiles (arrows etc.)
"""


import random
import pygame

# State constants
WALKING = 1
ATTACKING = 2
CASTING = 3
DYING = 4
DEAD = 5

DEBUG_BOXES = True

class Monster(pygame.sprite.Sprite):
    def __init__(self,x, y, walk_anim, attack_anim, mob_data, cast_anim = False):
        """
        The Player class constructor - note that x and y is only for initialization,
        the player position will be tracked by the rect
        """
        super().__init__()
        self.gravity = 0.5 
        self.data = mob_data  # a MonsterData() instance

        # Setting up walk animation
        self.walk_anim = walk_anim
        self.width = walk_anim.ss.x_dim * walk_anim.ss.scale
        self.height = walk_anim.ss.y_dim * walk_anim.ss.scale
        self.image = self.walk_anim.get_image()

        # Setting up attack and castr animations
        self.attack_anim = attack_anim
        self.cast_anim = cast_anim

        # Setting up death animation
        self.dead = False

        # Setting up sprite's rectangle
        self.X_ADJ = walk_anim.ss.scale * 44
        self.Y_ADJ = walk_anim.ss.scale * 18
        self.X_CENTER = 40
        self.Y_CENTER = 28
        self.rect = self.image.get_rect()
        self.rect.center = (x ,y)

        self.hitbox = pygame.Rect(0,0,0,0)
        self.rect_detect = pygame.Rect(0,0,0,0)
        self.rect_attack = pygame.Rect(0,0,0,0)
   
        self.vel_y = 0
        self.turned = False
        self.at_bottom = False
        self.state = WALKING  # we init in walking state
        self.last_attack = 0
        self.ready_to_attack = True  
        self.score_flag = False  # We can only add more score when this is True
        self.prev_y_lvl = self.rect.y  # Tracking vertical progress

        self.spells_list = None  # if the mob is busy casting, this is what it is casting
        self.cast_anim_list = []  # if the mob casts a spell, we creat animations here


    def _create_rects(self) -> None:
        # Updating the HITBOX collision rectangle
        self.hitbox = pygame.Rect(self.rect.left + 30, self.rect.top + 28, self.width - 60, self.rect.height - 30)

        # Creating a DETECTION rect where to mob will attack if the player rect collides
        x = self.hitbox.centerx
        y = self.hitbox.top + 30 + (self.data.detection_range_high * -100)
        

        width = self.data.detection_range
        height = self.height - 100 + (self.data.detection_range_high * 200)

        if self.turned:       
            self.rect_detect = pygame.Rect(x - width, y, width, height) 
        else:
            self.rect_detect = pygame.Rect(x, y,width, height) 

        # Creating an ATTACK rect 
        if self.state == ATTACKING:
            y = y + (self.data.detection_range_high * 100)
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
            if DEBUG_BOXES:
                pygame.draw.rect(pygame.display.get_surface(), (0,255,255), platform.rect, 2 )  # Debug show hitbox on screen (GREEN)
                pygame.draw.rect(pygame.display.get_surface(), (255,255,255), self.rect, 4 )  # Debug show rect on screen (WHITE)
                pygame.draw.rect(pygame.display.get_surface(), (0,255,0), self.hitbox, 2 )  # Debug show hitbox on screen (GREEN)

            # collision in the y direction only, using a collision rect indicating _next_ position (y + dy)
            moved_hitbox = self.hitbox.move(0, dy - 2)  # move in place - remove 2 to anchor the sprites on the ground properly
            if DEBUG_BOXES:
                pygame.draw.rect(pygame.display.get_surface(), (0,128,0), moved_hitbox, 2 )  # Debug show hitbox on screen (GREEN)
            if platform.rect.colliderect(moved_hitbox):  # we are standing on a platform essentially
                # Preventing falling through platforms
                if moved_hitbox.bottom > platform.rect.top:  # Is player above platform?
                    if self.vel_y > 0 and not self.dead:  # Is monster falling and not dead?
                        dy = 0
                        self.at_bottom = True                     
                        self.vel_y = 0

                

                # Preventing falling off left/right edge of platforms if there is NO collision (-1) to the side and down (and it's not a jumping mob
                moved_hitbox = self.hitbox.move(-self.hitbox.width, 40)  # checking left 
                if  moved_hitbox.collidelist(all_platforms) == -1 and not self.data.attack_jumper:
                    self.data.direction = 1
                    self.turned = False
                    if DEBUG_BOXES:
                        pygame.draw.rect(pygame.display.get_surface(), (0,128,0), moved_hitbox, 2 )  # Debug show hitbox on screen (GREEN)pygame.draw.rect(pygame.display.get_surface(), (255,192,200), moved_hitbox, 2 )  # Debug show hitbox on screen (PINK)
                moved_hitbox = self.hitbox.move(self.hitbox.width, 40)  #checking right
                if moved_hitbox.collidelist(all_platforms) == -1 and not self.data.attack_jumper:
                    self.data.direction = -1
                    self.turned = True
                    if DEBUG_BOXES:
                        pygame.draw.rect(pygame.display.get_surface(), (128,128,0), moved_hitbox, 2 )  # Debug show hitbox on screen (YELLOW)
                
                
                # Turning around if hitting a solid tile  
                moved_hitbox = self.hitbox.move(dx * 5 * self.data.direction, 20).inflate(0,-60)
            
                if DEBUG_BOXES:
                    pygame.draw.rect(pygame.display.get_surface(), (255,255,0), moved_hitbox, 1 )  # Debug show hitbox on screen

                if platform.rect.colliderect(moved_hitbox):
                    self.data.direction *= -1
                    self.rect.x += dx * 20  * self.data.direction # far enough to avoid re-triggering in an endless loop
                    self.turned = not self.turned


    def attack_start(self) -> None: 
        """ Called to set attack variables and keep track of attack timings for repeat attacks """                
        if self.ready_to_attack:
            self.state = ATTACKING
            self.attack_anim.active = True
            self.last_attack = pygame.time.get_ticks()
            new_rect = self.attack_anim.get_image().get_rect()  # we need to scale the rect for different size attack images
            new_rect.center = self.rect.center
            self.rect = new_rect


    def attack_stop(self) -> None: 
        self.state = WALKING 
        self.attack_anim.active = False
        self.rect_attack = pygame.Rect(0,0,0,0)
        self.rect = self.walk_anim.get_image()  # we need to scale back to walking image size after an attack
        

    def update(self, scroll, platforms_sprite_group, player) -> None:
        dx = 0
        dy = self.vel_y  # Newton would be proud!

        

        """ Boss battles have separate logic depending on each boss - if they cast anything, we get a list of animations back as well
            the boss_battle function updates self.vel_y directly and adds self.
        """
        if self.data.boss:
            dx, dy = self.data.boss_battle(self, player)
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
            else:
                dx = self.data.speed_walking  #  we start at walking speed

                # We throw in random cahnges in direction, different by mod type
                if self.data.random_turns / 100  > random.random():
                    dx *= -1
                    self.data.direction *= -1
                    self.turned = not self.turned


        # we compensate for scrolling
        self.scroll = scroll
        self.rect.x += scroll

        # we compensate for graivty
        self.vel_y += self.gravity  # allows us to let mobs fall (including during death)
        dy += self.vel_y
        
        # Update rectangle position
        self.rect.x += dx * self.data.direction
        self.rect.y += dy 

        # Checking detection, hitbox and attack rects as well as platform rects for collision
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

        if self.state == CASTING:
            self.image = self.cast_anim.get_image().convert_alpha()
            self.image = self.cast_anim.get_image(repeat_delay = self.data.cast_delay)
        elif self.state == ATTACKING:
            # If we have a diffent size attack sprites, we need to take scale into account
            self.image = self.attack_anim.get_image(repeat_delay = self.data.attack_delay).convert_alpha()
            

        elif self.state == DYING:
            # Spin sprite
            angle = 5
            orig_rect = self.image.get_rect()
            rot_image = pygame.transform.rotate(self.image, angle)
            rot_rect = orig_rect.copy()
            rot_rect.center = rot_image.get_rect().center
            self.image = rot_image.subsurface(rot_rect).copy()
            self.image = pygame.transform.flip(self.image, self.turned, False)
        elif self.state == WALKING:
            self.image = self.walk_anim.get_image()

        else:
            print(f'ERROR: illegal monster state "{self.state}"')
            exit(1)

        self.image = pygame.transform.flip(self.image, self.turned, False)        


class Projectile(pygame.sprite.Sprite):
    def __init__(self,x, y, image, turned, scale = 1):
        """
        The Projector class constructor - note that x and y is only for initialization,
        the projectile position will be tracked by the rect
        """
        super().__init__()
        self.image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))

        self.dead = False  
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
        self.scroll = scroll
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
    def __init__(self, x, y, anim, turned, scale = 1):
        """
        The Spell class constructor - note that x and y is only for initialization,
        the spell position will be tracked by the rect
        """
        super().__init__()
        self.anim = anim
        image = anim.get_image()
        self.gravity = 1

        self.image = pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))

        self.dead = False  
        self.speed = 10
        self.width = image.get_width()
        self.height = image.get_height()
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.turned = turned

        self.anim.active = True
        
    def update(self, scroll) -> None:
        # we compensate for scrolling
        self.scroll = scroll
        self.rect.x += scroll

        # Done with one cycle, as spell do not repeat (yet!)
        print (f'{self.anim.anim_counter=}')
        print(f'{self.anim.first_done=}')
        if self.anim.first_done:
            self.spells_list = False
            self.kill()

        # Ready for super.draw()
        self.image = pygame.transform.flip( self.image.convert_alpha(), self.turned, False)