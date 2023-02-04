import pygame
import random
import logging
import math

from random import randint
from level_data import *
from settings import *
from game_tiles import GameTileAnimation


# --- Show floating info bubbles ---
class BubbleMessage():
    """ Show floating info bubbles
        Meant to linger - 10 seconds between each message 
    """
    def __init__(self, screen: pygame.display, msg: str, ttl: int, start_delay: int, msg_type: str, player: pygame.sprite.Sprite) -> None:
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
        self.init_time = pygame.time.get_ticks()
        self.duration = ttl
        self.font_size = 48
        self.font = pygame.font.Font("assets/font/m5x7.ttf", self.font_size)  # 16, 32, 48
        #self.font = pygame.font.Font("assets/font/OldSchoolAdventures-42j9.ttf", self.font_size)  # 16, 32, 48

        self.bubble_bg = pygame.image.load('assets/panel/bubble.png').convert_alpha()
        
        self.half_screen = pygame.display.get_surface().get_size()[0] // 2

        self.msg_list = msg.splitlines()  # splitting the msg into a list of lines

        self.x_size = 10  # start padded
        self.y_size = 10
        y_padding = 10
        for line in self.msg_list:
            self.x_size += pygame.font.Font.size(self.font, line)[0]
            self.y_size += pygame.font.Font.size(self.font, line)[1]
            self.y_size += y_padding

    def _display_msg(self) -> None:
            # TODO: BLIT ONTO A SPRITE BIG ENOUGH FOR RECT AND CIRCLES FIRST, THEN WE CAN USE THE SPRITE TO MOVE THE BUBBLE OVER TIME
            # ALSO MAKE QUARTERR SIZE, SCALE UP, TO GET PIXEL ART EFFECT, OR REDUCE RESOLUTION EVERYWHERE AND SCALE UP!!
            padding_x = 30
            padding_y = 12

            white = (255,255,255)

            surf = pygame.transform.scale(self.bubble_bg,(self.x_size + int(self.x_size * 0.2), self.y_size))
            line_size = 3


            for row, msg_text in enumerate(self.msg_list):
                text_img = self.font.render(msg_text, True, white)
                surf.blit(text_img, (padding_x, padding_y + row * pygame.font.Font.size(self.font, msg_text)[1]))
            
            if self.player.rect.centerx < self.half_screen:
                self.screen.blit(surf, (self.player.rect.centerx, self.player.rect.top - self.y_size))    
            else:
                self.screen.blit(surf, (self.player.rect.centerx - self.x_size, self.player.rect.top - self.y_size))


    def show(self) -> None:
        # we compensate for scrolling
        now = pygame.time.get_ticks()
        if now - self.init_time > self.start_delay:
            # First we show the message and freeze for a brief moment
            if now > self.last_time + self.min_delay and not self.active:
                self._display_msg()
                self.active = True
                pygame.time.wait(50)
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

class ParallaxBackground():
    """ Class for showing and scrolling a multi-level parallax background """
    def __init__(self,level,screen) -> None:
        self.screen = screen
        background = levels[level]['background']
        self.bg_scroll = 0
        
        # load background images
        self.bg_near = pygame.image.load(background['near']).convert_alpha()
        self.bg_medium = pygame.image.load(background['medium']).convert_alpha()
        self.bg_far = pygame.image.load(background['far']).convert_alpha()
        self.bg_further = pygame.image.load(background['further']).convert_alpha()
        self.bg_clouds = pygame.image.load(background['clouds']).convert_alpha()
        self.bg_color = background['background_color']

        self.y_adjust = {
            'near': background['y_adjust'][0],
            'medium': background['y_adjust'][1],
            'far': background['y_adjust'][2],
            'further': background['y_adjust'][3],
            'bg': background['y_adjust'][4],
        }
    
    def update(self,bg_scroll) -> None:
        self.bg_scroll += bg_scroll
    
    def draw(self, surface) -> None:
        surface.fill(self.bg_color)
        width = self.bg_clouds.get_width()
        
        for x in range(LEVEL_WIDTH + 300):
            surface.blit(self.bg_clouds, ((x * width) + self.bg_scroll * 0.4, 0 - self.y_adjust['bg']))
            surface.blit(self.bg_further, ((x * width) + self.bg_scroll * 0.5, SCREEN_HEIGHT - self.bg_further.get_height() - self.y_adjust['further']))
            surface.blit(self.bg_far, ((x * width) + self.bg_scroll * 0.6, SCREEN_HEIGHT - self.bg_far.get_height() - self.y_adjust['far']))
            surface.blit(self.bg_medium, ((x * width) + self.bg_scroll * 0.7, SCREEN_HEIGHT - self.bg_medium.get_height() - self.y_adjust['medium']))
            surface.blit(self.bg_near, ((x * width) + self.bg_scroll * 0.8, SCREEN_HEIGHT - self.bg_near.get_height() - self.y_adjust['near']))

    # TODO: right now the parallax factor is hard coded; move to level_data.py to allow different factors for different levels

class EnvironmentalEffects(pygame.sprite.Group):
    """
    Class for adding non-interactive environmental effects, like blowing leaves, snow, raid etc.
    """
    def __init__(self, effect, screen) -> pygame.sprite.Group:
        super().__init__()
        from animation_data import anim
        self.effect = effect  # 'leaves', 'snow', all found in level_data for each level
        self.anim = anim
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
        now = pygame.time.get_ticks() 
        if random.random() < 1/30: # making sure we've waited long enough
            leaf = GameTileAnimation(16,16,randint(SCREEN_WIDTH, SCREEN_WIDTH*3), randint(0, SCREEN_HEIGHT/4), self.anim['environment']['leaves'])  # TODO: They ALL use the SAME Animation instance, so all animate identically
            leaf.x_vel = random.uniform(-4, -1)  # starting horisontal speed
            leaf.y_vel = GRAVITY * 2
            leaf.animation.active = True
            leaf.animation.frame_number = randint(0,leaf.animation.frames -1 )
            self.add(leaf)
            
            self.last_leaf = now
            
    

    def update(self, scroll) -> None:
        # Here we set the x_vel for each sprite to match the wind at their respective vertical position
        # Each particle is assumed to float in the wind, minus the enertia for each category (snow less than leaves etc.)
        now = pygame.time.get_ticks()
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

                sprite.update(scroll)
                
                # Removing sprites that have gone off screen
                if sprite.rect.centery > SCREEN_HEIGHT:
                    sprite.kill()
                sprite.image = sprite.animation.get_image()
            
            # Here we add the leaves
            if len(self.sprites()) < 100 and self.effect == 'leaves':
                self._add_leaf()


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

class ExpandingCircle:
    def __init__(self, x: int, y: int, color: pygame.Color, thickness: int, radius_max: int, frame_delay: int) -> None:
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

    def update(self, scroll) -> None:
        # It's fire-and-forget
        self.x += scroll
        now = pygame.time.get_ticks()

        if now - self.last_update > self.frame_delay:
            self.radius += 3
            self.width = int((self.radius/self.radius_max) * self.wide)  # scaling width with radius
            self.last_update = now
            if self.radius >= self.radius_max:
                self.done = True

    def draw(self, screen) -> None:
        if not self.done:
            pygame.draw.circle(screen, (self.color), (self.x,self.y), self.radius, width=self.width)

class LightEffect1(pygame.sprite.Sprite):
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

        self.image = pygame.Surface((self.line_width * self.line_numbers, self.line_max_height)).convert_alpha()
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
            segment_list = [pygame.Color('#000000')] * padding + [pygame.Color('#df7126')] * color_segments + [pygame.Color('#fbf236') ] * color_segments \
                            + [pygame.Color('#fffa8c')] * color_segments + [pygame.Color('#ffffff')] * color_segments 
            
            self.firelines.append(segment_list)

        # We create a working surface were we plot the final result and the scroll that upwards onto self.image
        for step in range (self.steps_total):
                for count, line in enumerate(self.firelines):     
                    image_x =  count * self.line_width
                    image_y = step * self.line_seg_height 
                    pygame.draw.rect(self.working_image, line[step], (image_x, image_y, self.line_width, self.line_seg_height))
        
    def update(self, scroll) -> None:
        now = pygame.time.get_ticks()
        self.start_x += scroll
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


"""
Functions
"""

def fade_to_color(color: pygame.color.Color) -> None:
    # Fades to color (and pauses game while doing so!)
    
    screen = pygame.display.get_surface()
    rect = screen.get_rect()
    rectsurf = pygame.Surface(rect.size,pygame.SRCALPHA)
    color.a = 1
    for _ in range(0,255):
        pygame.time.wait(1)
        rectsurf.fill(color)
        screen.blit(rectsurf,(0,0))
        pygame.display.update()


def sine_wave(points=100)-> list:
    """ Produces the points in a sine wave
        Values range between 0 and 100, with max value of 1 in the middle and 0 at both ends of the list
    """
    point_list = [] * points

    # Define the maximum amplitude of the wave
    amplitude = 50

    # Define the start and end points along the x-axis
    start = math.pi /2
    end = (5 * math.pi /2) 

    # Define the step size for each point along the x-axis
    step = (end - start) / points

    # Calculate the x and y coordinates for each point
    for i in range(points):
        x = start + i * step
        y = amplitude * math.sin(x) + 150

        point_list.append(1-(y-100)/100)

    return point_list
