import pygame as pg
from random import random, randint

from random import randint
from level_data import *
from settings import *
from game_tiles import GameTileAnimation
from game_functions import *


# --- Show floating info bubbles ---
class BubbleMessage:
    """ Show floating info bubbles
        Meant to linger - 10 seconds between each message 
    """
    def __init__(self, screen: pg.display, msg: str, ttl: int, start_delay: int, msg_type: str, player: pg.sprite.Sprite) -> None:
        # Arguments:
        # ttl : durtaion of bubble in ms
        # msg_type: type of message, to avoid dupes
        # player: player instance
        self.msg_type = msg_type
        self.screen = screen
        self.msg = msg
        self.player = player

        self.start_delay = start_delay

        self.active = False  
        self.shutting_down = False
        self.shutdown_counter = 25  # 5 steps to remove the bubble
        self.expired = False

        self.min_delay = 1000*10  # 10 seconds
        self.last_time = -self.min_delay  # just to make sure we run the first time without delay
        self.start_time = 0
        self.init_time = pg.time.get_ticks()
        self.duration = ttl
        self.font_size = 64
        
        self.font = pg.font.Font("assets/font/Silver.ttf", self.font_size)  # 16, 32, 48

        self.bubble_bg = pg.image.load('assets/panel/bubble.png').convert_alpha()
        
        self.half_screen = screen.get_size()[0] // 2

        self.msg_list = msg.splitlines()  # splitting the msg into a list of lines

        self.x_size = 10  # start padded
        self.y_size = 10
        y_padding = 10
        for line in self.msg_list:
            self.x_size += pg.font.Font.size(self.font, line)[0]
            self.y_size += pg.font.Font.size(self.font, line)[1]
            self.y_size += y_padding

    def _display_msg(self) -> None:
            padding_x = 30
            padding_y = 12


            surf = pg.transform.scale(self.bubble_bg,(self.x_size + int(self.x_size * 0.2), self.y_size))

            for row, msg_text in enumerate(self.msg_list):
                text_img = self.font.render(msg_text, True, WHITE)
                
            if self.player.rect.centerx < self.half_screen:  # On the left side of the screen we flip the bubble and move it right of the player
                surf = pg.transform.flip(surf, True, False)
                surf.blit(text_img, (padding_x, padding_y + row * pg.font.Font.size(self.font, msg_text)[1]))
                self.screen.blit(surf , (self.player.rect.centerx - self.x_size // 5 , self.player.rect.top - self.y_size))
            else:
                surf.blit(text_img, (padding_x, padding_y + row * pg.font.Font.size(self.font, msg_text)[1]))
                self.screen.blit(surf, (self.player.rect.centerx - self.x_size, self.player.rect.top - self.y_size))


    def show(self) -> None:
        # we compensate for scrolling
        now = pg.time.get_ticks()
        if now - self.init_time > self.start_delay:
            # First we show the message and freeze for a brief moment
            if now > self.last_time + self.min_delay and not self.active:
                self._display_msg()
                self.active = True
                pg.time.wait(50)
                self.last_time = now
                self.start_time = now

            elif self.active and now < self.start_time + self.duration:
                self._display_msg()
            else:
                self.shutting_down = True

            if self.shutting_down:
                self.y_size = self.y_size - int((self.y_size / self.shutdown_counter))  # we shrink the height a little each time
                self._display_msg()

                self.shutdown_counter -=1 
                if self.shutdown_counter == 0:
                    self.active = False
                    self.expired = True


# --- Various environmental effects
class EnvironmentalEffects(pg.sprite.Group):
    """
    Class for adding non-interactive environmental effects, like blowing leaves, snow, raid etc.
    """
    def __init__(self, effect, screen) -> pg.sprite.Group:
        super().__init__()
        from animation_data import leaves_ss
        from animation import Animation
        self.Anim = Animation
        self.ss = leaves_ss
        self.effect = effect  # 'leaves', 'snow', all found in level_data for each level
        self.screen = screen
        self.base_wind = -1  # blowing toward the left of the screen
        self.gust_strength = 1
        self.wind = Wind(self.base_wind)  
        self.fall_from_top = 0
        self.last_leaf = 0
        self.last_update = 0 
        if self.effect == 'leaves':
            self.inertia = 0.5  # % of wind speed to remove
        
        self.last_run = 0
        self.last_gust_change = 0
        self.frequency = 10  # times per second we update the environmental effects

    def _add_leaf(self) -> None:
        now = pg.time.get_ticks() 
        if random.random() < 1/30: # making sure we've waited long enough
            leaf = GameTileAnimation(16,16,randint(SCREEN_WIDTH, SCREEN_WIDTH*3), randint(0, SCREEN_HEIGHT/4), self.Anim(self.ss, frames=10, speed=100, repeat=True))  # TODO: They ALL use the SAME Animation instance, so all animate identically
            leaf.x_vel = random.uniform(-4, -1)  # starting horisontal speed
            leaf.y_vel = GRAVITY * 2
            leaf.animation.active = True
            leaf.animation.frame_number = randint(0,leaf.animation.frames -1 )
            self.add(leaf)
            
            self.last_leaf = now
            
    

    def update(self, h_scroll, v_scroll) -> None:
        # Here we set the x_vel for each sprite to match the wind at their respective vertical position
        # Each particle is assumed to float in the wind, minus the enertia for each category (snow less than leaves etc.)
        now = pg.time.get_ticks()
        if now - self.last_run >  1000 / self.frequency:
            if now - self.last_gust_change > 1000 * 10:
                self.gust_strength = randint(1,3)  # every 10 seconds we change the wind gust speed 
                self.last_gust_change = now

            # The wind provides a list of wind speed 
            wind_field = self.wind.update(self.gust_strength)

            for sprite in self.sprites():
                # Compensate for wind
                list_pos = int((sprite.rect.centery / SCREEN_HEIGHT) * 100)  # position in list depending on y position of sprite
                sprite.x_vel = self.base_wind - wind_field[list_pos]  # we add the wind component for our current height (vertical sine wave)


                # Compensating for inertia which alsways tries to slow the sprite down
                if sprite.x_vel < self.base_wind:  # always the case at first
                    sprite.x_vel -= sprite.x_vel * self.inertia
                if sprite.x_vel > self.base_wind:
                    sprite.x_vel += sprite.x_vel * self.inertia

                sprite.update(h_scroll, v_scroll)
                
                # Removing sprites that have gone off screen
                if sprite.rect.centery > SCREEN_HEIGHT:
                    sprite.kill()
                sprite.image = sprite.animation.get_image()
            
            # Here we add the leaves
            if len(self.sprites()) < 100 and self.effect == 'leaves':
                self._add_leaf()


# --- Expanding circle effects for spells
class ExpandingCircle:
    def __init__(self, x: int, y: int, color: pg.Color, thickness: int, radius_max: int, frame_delay: int) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.wide = thickness
        self.width = 0
        self.radius_max = radius_max
        self.radius = 0
        self.frame_delay = frame_delay

        self.last_update = 0  # for timing
        self.done = False

    def update(self, h_scroll, v_scroll) -> None:
        # It's fire-and-forget
        self.x += h_scroll
        self.y += v_scroll
        now = pg.time.get_ticks()

        if now - self.last_update > self.frame_delay:
            self.radius += 3
            self.width = int((self.radius/self.radius_max) * self.wide)  # scaling width with radius
            self.last_update = now
            if self.radius >= self.radius_max:
                self.done = True

    def draw(self, screen) -> None:
        if not self.done:
            pg.draw.circle(screen, (self.color), (self.x,self.y), self.radius, width=self.width)


# --- Shows panel on top of screen with score and inventory
class GamePanel:
    """ Class to show a panel on top left corner of the screen """
    def __init__(self, screen: pg.display, game_state)-> None:
        from animation_data import anim
        self.heart_anim = anim['decor']['beating-heart']
        self.heart_anim.active = False
        self.stomp_anim = anim['decor']['stomping-foot']
        self.heart_anim.active = False

        self.gs = game_state

        self.screen = screen
        self.window_size = pg.display.get_window_size()# screen.get_window_size()
        
        self.inventory = []

        # Define fonts
        self.font_small = pg.font.Font("assets/font/Silver.ttf", 36)

        self.blink_counter = 0
        self.blink = False
        self.last_health = 0
        self.old_inv = []  # track changes in player in ventory to highlight
        
        # Panel background image
        self.panel_bg = pg.image.load('assets/panel/game-panel.png').convert_alpha()

    def setup_bars(self) -> None:
        # Health bars + stompometer
        self.health_bar_length = int(SCREEN_WIDTH / 6 * self.gs.player_health / 1000)  # grows when max health grows
        self.health_bar_max_length = int(SCREEN_WIDTH / 6 * self.gs.player_health_max / 1000)  # grows when max health grows

    def _blink_bar(self, duration) -> None:
        # Blinks the frame around the health bar red
        if self.blink == True:
            if self.blink_counter < duration:
                self.blink_counter += 1
                pg.draw.rect(self.screen, (255,0,0), (20,40,self.health_bar_max_length+4,20) ,2 )
            else:
                self.blink_counter = 0
                self.blink = False
        else:
            if self.gs.player_health < self.last_health: 
                self.blink = True

    def _flash_show(self, img, x,y) -> None:
        # Flashes the health bar when hit

        # Play sound effect
        audio_highlight = pg.mixer.Sound('assets/sound/game/panel_highlight.wav')
        audio_highlight.play()

        opacity = 128
        img2 = img
        img2.fill((100, 100, 100, 0), special_flags=pg.BLEND_RGBA_ADD)
        
        surf = pg.Surface(pg.display.get_window_size())
        surf.set_alpha(opacity)  
        surf.fill((0,0,0)) # fill the entire surface
        self.screen.blit(surf, (0,0))  # blit to screen
        pg.display.update()
        screen_cpy = self.screen.copy()
        pg.time.wait(250)     

        for _ in range(10):
            self.screen.blit(img2, (x,y))
            pg.display.update()
            pg.time.wait(75)

            self.screen.blit(screen_cpy, (0,0))  # starting over
            pg.display.update()
            pg.time.wait(75)
        
    def draw(self) -> None:


        self.health_bar_length = int(SCREEN_WIDTH / 6 * self.gs.player_health / 1000)
        
        # --> Panel background
        self.screen.blit(self.panel_bg, (0,0))

        # --> Health bar, white and semi transparent
        health_bar_frame = pg.Surface((self.health_bar_max_length+4,20), pg.SRCALPHA)   # per-pixel alpha
        health_bar_frame.fill((255,255,255,128))  # with alpha
        self.screen.blit(health_bar_frame, (20,40))
        self._blink_bar(10)  # blink if we should
        ratio = self.health_bar_length / self.health_bar_max_length
        GREEN = 255 * ratio
        RED = 255 * (1-ratio)
        BLUE = 0
        health_bar = pg.Surface((self.health_bar_length,16), pg.SRCALPHA)   # per-pixel alpha
        health_bar.fill((RED,GREEN,BLUE,200))                         # notice the alpha value in the color
        self.screen.blit(health_bar, (22,42))     
        self.last_health = self.gs.player_health

        # --> Heart decoration for health bar
        self.screen.blit(self.heart_anim.get_image(), (5, 33))
        if self.gs.player_health < PLAYER_HEALTH // 4:
            self.heart_anim.active = True
        else:
            self.heart_anim.active = False
            self.heart_anim.frame_number = 4

        # --> Stomp bar (we reuse the health surface)
        stomp_bar_length = SCREEN_WIDTH // 6
        stomp_bar_frame = pg.Surface((stomp_bar_length + 4 ,20), pg.SRCALPHA)
        stomp_bar_frame.fill((255,255,255,128))  # notice the alpha value in the color
        self.screen.blit(stomp_bar_frame, (SCREEN_WIDTH - stomp_bar_length -20,40))
        ORANGE = pg.Color('#f7b449')


        if self.gs.player_stomp_counter > PLAYER_STOMP:  # max
            self.gs.player_stomp_counter = PLAYER_STOMP

        stomp_bar_length = (stomp_bar_length /PLAYER_STOMP) * self.gs.player_stomp_counter
        stomp_bar = pg.Surface((stomp_bar_length,16), pg.SRCALPHA)
        stomp_bar.fill(ORANGE)
        self.screen.blit(stomp_bar, (SCREEN_WIDTH - stomp_bar_length -18,42))     
        
         # --> The score
        WHITE = (255, 255, 255)
        draw_text(f'SCORE: {self.gs.player_score}', self.screen, WHITE, self.window_size[0]/100, self.window_size[1]/100, font=self.font_small)  # score
        
        # --> Boot decoration for stomp 
        self.screen.blit(self.stomp_anim.get_image(), (SCREEN_WIDTH - 38, 33))
        if self.gs.player_stomp_counter == PLAYER_STOMP:
            self.stomp_anim.active = True
        else:
            self.stomp_anim.active = False
            self.stomp_anim.frame_number = 1

        # --> Player inventory, top right
        key_x = self.window_size[0] * 0.75
        key_y = self.window_size[1] * 0.02

        for items in self.inventory:
            if items[0] == 'key':
                img = pg.transform.scale(items[1], (40,50))
                self.screen.blit(img, (key_x,key_y))

        if len(self.inventory) > len(self.old_inv):  # new items! 
            new_items = [x for x in self.inventory if x not in self.old_inv]
            for items in new_items:
                if items[0] == 'key':
                    img = pg.transform.scale(items[1], (40,50))
                    self._flash_show(img, key_x, key_y)

            self.old_inv = self.inventory


# --- Shows info pop-up over doors etc.
class InfoPopup(pg.sprite.Sprite):
    def __init__(self, msg_text, x, y) -> None:
        super().__init__()

        font = pg.font.Font("assets/font/Silver.ttf", 48)  # 16, 32, 48

        self.image = pg.Surface((TILE_SIZE_SCREEN * 4,TILE_SIZE_SCREEN), pg.SRCALPHA)
        self.image.fill((0, 0, 0, 0)) # Set the surface to be completely transparent
        self.full_image = pg.Surface((TILE_SIZE_SCREEN * 4,TILE_SIZE_SCREEN), pg.SRCALPHA)
        self.full_image.fill((0, 0, 0, 0)) 

        pg.draw.line(self.full_image, WHITE, (1,10), (10,1), width=5)  # diagonal line
        pg.draw.line(self.full_image, WHITE, (10,1), (200,1), width=5)  # horizontal line
        text_img = font.render(msg_text, True, WHITE)
        self.full_image.blit(text_img, (25,5))

        self.rect = pg.Rect(x, y - TILE_SIZE_SCREEN, TILE_SIZE_SCREEN * 4,TILE_SIZE_SCREEN)
        self.ticks_since_last = 0
        self.x = x
        self.y = y

        self.name = 'info-popup'

        self.state = 'roll-out'  # we start in init
        self.roll_count = 0  # keeping track of how far "rolled out/in" the message is

    def change_state(self, state) -> None:
        self.state = state

    def update(self, h_scroll, v_scroll) -> None:
        self.rect.centerx += h_scroll
        self.rect.centery += v_scroll
        
        if self.state == 'roll-out':
            direction = 1
        if self.state == 'roll-in':
            direction = -1
        
        now = pg.time.get_ticks()
        if now - self.ticks_since_last > 10:
            if self.state in ('roll-in', 'roll-out'):
                self.image.fill((0, 0, 0, 0)) # Set the surface to be completely transparent
                self.image.blit(self.full_image, (0,0), (TILE_SIZE_SCREEN * 4 - self.roll_count, 0, self.roll_count, TILE_SIZE_SCREEN))
                if self.roll_count < TILE_SIZE_SCREEN * 4 and self.roll_count > -1:  # used to vount both up and down
                    print(self.roll_count)
                    self.roll_count += 10 * direction

            self.ticks_since_last = now

    # draw() in super
        

# --- Stomp splash effect
class LightEffect1(pg.sprite.Sprite):
    """
    Class which gives light effect consisting of vertical lines shooting up from the ground
    """
    def __init__(self, x, y) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.steps_total = 50  # now: 1 step per segment
        self.steps_in = 0  # keeping track of progress towards self.steps_total
        self.step_direction = 1
        self.last_run = 0 
        self.step_delay = 10

        self.done = False
        
        self.line_numbers = 50
        self.line_width = 4
        self.line_max_height = 200
        self.line_seg_height = 4
        self.max_segments = self.line_max_height // self.line_seg_height

        self.image = pg.Surface((self.line_width * self.line_numbers, self.line_max_height)).convert_alpha()
        self.working_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.firelines = []  # list or columns, with list of segments for each column

        self.start_x = self.x - (self.line_numbers / 2 ) * self.line_width


        for column in range(self.line_numbers):
            # each line varies in length from 1/3 to the full max_height
            # we pre-calculte as much as possible to not put work in the loop
            self.line_height = randint(self.line_max_height//3, self.line_max_height)
            self.line_x = self.start_x + column * self.line_width
            color_segments  = int((self.line_height / self.line_seg_height) // 4) # how may segments in each color
            padding = self.max_segments - color_segments * 4 + 4  # the last 4 is just to wipe any remaining non-black pixels when moving down

            # We add the segments in reverse order, so we start with the top
            segment_list = [pg.Color('#000000')] * padding + [pg.Color('#df7126')] * color_segments + [pg.Color('#fbf236') ] * color_segments \
                            + [pg.Color('#fffa8c')] * color_segments + [pg.Color('#ffffff')] * color_segments 
            
            self.firelines.append(segment_list)

        # We create a working surface were we plot the final result and the h_scroll that upwards onto self.image
        for step in range (self.steps_total):
                for count, line in enumerate(self.firelines):     
                    image_x =  count * self.line_width
                    image_y = step * self.line_seg_height 
                    pg.draw.rect(self.working_image, line[step], (image_x, image_y, self.line_width, self.line_seg_height))
        
    def update(self, h_scroll, v_scroll) -> None:
        now = pg.time.get_ticks()
        self.start_x += h_scroll
                        
        if now - self.last_run > self.step_delay:
 
            self.image.blit(self.working_image, (0,self.line_max_height - self.steps_in * self.line_seg_height))

            self.steps_in += 4 * self.step_direction  # this is the progress counter, updates 

            if self.steps_in >= self.steps_total:
                self.step_direction = -1
            if self.step_direction == -1 and self.steps_in == 0:
                self.done = True
            self.last_run = now  

            self.image.set_colorkey(BLACK)
            self.image.set_alpha(128)
            # We use the super draw method, so rect needs to be updated
            self.rect.centerx = self.x
            self.rect.centery = self.y - 50


# --- Various particles
class ParticleSystem:
    def __init__(self) -> None:
        """ Particle system with pixel art extension """
        self.all_particles = []
        self.particle = {
                'center': list,
                'velocity': list,
                'radius': float,
                'color':pg.Color,
            }
        self.last_run = 0
        self.update_delay = 15
        
    def add(self, particle) -> None:
        self.all_particles.append(particle)
        
    def update(self, h_scroll, v_scroll) -> None:
        now = pg.time.get_ticks()
        if now - self.last_run > self.update_delay:
            for particle in self.all_particles:
                # Updating velocities
                particle['velocity'][1] += GRAVITY * 2  # adding gravity to the velocity (looks better if we add some more gravity/)

                # Updating coordinates as funtion of velocities
                particle['center'][0] += h_scroll + particle['velocity'][0] # x
                particle['center'][1] += v_scroll + particle['velocity'][1]  # y

                # Shrinking the circle radius
                particle['radius'] -= 0.3
                if particle['radius'] < 1:
                    self.all_particles.remove(particle)
            
            self.last_run = now


    def draw(self, screen) -> None:
        for particle in self.all_particles:
            side = int(particle['radius'] * 4)
            x = int(particle['center'][0] - side/2)
            y = int(particle['center'][1] - side/2)
            pg.draw.rect(screen, particle['color'], pg.Rect(x, y, side, side ))


# --- Shows the multilevel parallax background
class ParallaxBackground:
    """ Class for showing and scrolling a multi-level parallax background """
    def __init__(self,level,screen) -> None:
        self.screen = screen
        background = levels[level]['background']
        self.bg_scroll = 0
        self.level_width = levels[level]['size_x'] * TILE_SIZE

        self.env_effect = levels[level]['environmental_effect']
        if self.env_effect == 'lightning storm':
            logging.debug(f'Active environmental effect: {self.env_effect}')
            self.last_lighting = 0
            self.lightning_timer = 3000

        self.only_bg_color = check_none_values(background)  # if there are one or more maps missing

        if self.only_bg_color:
            self.bg_color = background['background_color']
        else:
            # We find the scaling factor based only on height, as images cvan be wider than the screen - using cloud texture for this
            self.bg_clouds = pg.image.load(background['clouds']).convert_alpha()
            scale = SCREEN_HEIGHT / self.bg_clouds.get_height()
            x_size = self.bg_clouds.get_width() * scale

            self.bg_clouds = pg.transform.scale(self.bg_clouds, (x_size, SCREEN_HEIGHT))
            self.bg_white = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_white.fill(WHITE)

            self.bg_sky = self.bg_clouds  # we can replace this to create effects
        
            self.bg_near = pg.transform.scale(pg.image.load(background['near']).convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_medium = pg.transform.scale(pg.image.load(background['medium']).convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_further = pg.transform.scale(pg.image.load(background['further']).convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg_far = pg.transform.scale(pg.image.load(background['far']).convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            self.cloud_width = self.bg_clouds.get_width()  # clouds are potentially much larger
            self.width = self.bg_near.get_width()

            self.y_adjust = {
                'near': background['y_adjust'][0],
                'medium': background['y_adjust'][1],
                'far': background['y_adjust'][2],
                'further': background['y_adjust'][3],
                'bg': background['y_adjust'][4],
            }

            self.cloud_drift =  background['cloud_drift']
            self.cloud_timer = 0
            self.cloud_movement = 0
    
    def update(self,bg_scroll) -> None:
        if not self.only_bg_color:
            self.bg_scroll += bg_scroll
            now = pg.time.get_ticks()

            if now - self.cloud_timer > self.cloud_drift:
                self.cloud_movement += 1
                self.cloud_timer = now
            
            # We replace the sky tecture with a bright white surface to indicate lightning
            if self.env_effect == 'lightning storm':
                if now - self.last_lighting > self.lightning_timer + randint(5000, 15000):
                    self.bg_sky = self.bg_white
                    self.last_lighting = now
                else:
                    self.bg_sky = self.bg_clouds

    
    def draw(self, surface) -> None:
        if self.only_bg_color:
            surface.fill(self.bg_color)  
        
        else:
            # for x in range((self.level_width // self.width) + 1) :
            for x in range(-1, 3):
                surface.blit(self.bg_sky,  ((x * self.cloud_width) + self.cloud_movement, 0))  # clouds are special  
                surface.blit(self.bg_far,     ((x * self.width) + self.bg_scroll * 0.05, 0))
                surface.blit(self.bg_further, ((x * self.width) + self.bg_scroll * 0.1,  0))
                surface.blit(self.bg_medium,  ((x * self.width) + self.bg_scroll * 0.3,  0))
                surface.blit(self.bg_near,    ((x * self.width) + self.bg_scroll * 0.7,  0))

    # TODO: right now the parallax factor is hard coded; move to level_data.py to allow different factors for different levels


class Weather():
    """ We do not use sprites for weather, but rather draw the rain/snow/whatever using pygame's draw function"""
    def __init__(self, weather) -> None:
        super().__init__()
        self.started = False

        self.weather_timer = 0


        self.weather_type = None

        if weather in ('lightning storm', 'rain'):
            self.weather_type = 'rain'
            self.weather_delay = 100
            self.drops_on_screen = 60
            self.drops = []
            # Movement used both for initial line values and for later animations (x>0 means right, y>0 means down)
            self.x_movement = -3
            self.y_movement =  15
            
            for _ in range(self.drops_on_screen):
                x1 = randint(0, SCREEN_WIDTH)
                y1 = randint(0, SCREEN_HEIGHT)
                x2 = x1 + self.x_movement
                y2 = y1 + self.y_movement
                color = WHITE
                width = 3
                
                self.drops.append({'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'color': color, 'width': width})

    def update_and_draw(self, h_scroll, v_scroll, surface) -> None:
        if not v_scroll:  # we wait until the player is done with the initial scrolling upon starting a new level
            self.started = True

        if self.weather_type == 'rain' and self.started:
            now = pg.time.get_ticks()
            if now - self.weather_timer > self.weather_delay:

                for i, particle in enumerate(self.drops):
                    #print(particle['x1'])
                    pg.draw.line(surface, particle['color'], (particle['x1'], particle['y1']), \
                                    (particle['x2'], particle['y2']), particle['width'])
                    self.drops[i]['x1'] += self.x_movement + h_scroll
                    self.drops[i]['y1'] += self.y_movement + v_scroll
                    self.drops[i]['x2'] += self.x_movement + h_scroll
                    self.drops[i]['y2'] += self.y_movement + v_scroll

                    # Checking if the particle is out of bounds and we need to spawn a new one
                    if not (0 < self.drops[i]['x2'] < SCREEN_WIDTH) or not (0 < self.drops[i]['y2'] < SCREEN_HEIGHT):
                        if len(self.drops) <= self.drops_on_screen:
                            x1 = randint(0, SCREEN_WIDTH)
                            y1 = 0
                            x2 = x1 + self.x_movement
                            y2 = y1 + self.y_movement
                            color = WHITE
                            width = 3
                            
                            self.drops[i] = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'color': color, 'width': width}
                        else:
                            self.drops.remove(self.drops[i])

        

# --- Speed line effect, used by player stomp
class SpeedLines:
    def __init__(self, rect: pg.rect.Rect, frame_delay: int=100) -> None:
        self.rect = rect
        self.x_start = self.rect.left
        self.y_start = self.rect.top
        self.max_width = self.rect.width
        self.height = 0

        self.previous_y = 0

        self.margin = 5

        self.frame_delay = frame_delay
        self.color = WHITE

        self.last_update = 0  # for timing
        self.done = False

    def update(self, h_scroll, v_scroll) -> None:
        self.x_start += h_scroll
        self.y_start += v_scroll
        self.new_y_pos = self.rect.top
        if self.previous_y == self.new_y_pos:  # the eagle has landed
            self.done = True
        self.previous_y = self.new_y_pos

        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_delay:
            self.height = self.new_y_pos - self.y_start 
            if self.height > self.margin:
                self.height -= self.margin

    def draw(self, screen) -> None:
        width = 4
        if not self.done and self.height > 10:
            for n in range (self.max_width // width):
                height = randint(0, self.height)
                pg.draw.rect(screen, WHITE, ((self.x_start + width * n, self.new_y_pos - height), (width, height)))


# --- Wind, used by particles and environmental effects
class Wind:
    """
    Class which simulates wind based on sine waves and returns a list of the wind direction in each vertical lines from 0 to SCREEN_HEIGHT
    """
    def __init__(self, base_wind) -> None:
        self.wind_field = []
        self.base_wind = base_wind

    def update(self, gust_strength) -> list:
        # Returns a list of values from 0 to gust_strength. 0 on both ends, just_strength in the middle
        field = [wind_point * gust_strength for wind_point in sine_wave(points=101)]  # 101 to make sure we have list indices from 0-100 (not 99), which ius easier to work with

        return field      

