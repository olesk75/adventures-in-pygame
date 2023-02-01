import pygame
import random
import logging
import math

from random import randint
from level_data import *
from settings import *
from game_tiles import GameTileAnimation


class Sky():
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
    
    def update(self,bg_scroll) -> None:
        self.bg_scroll += bg_scroll
        print(self.bg_scroll)
    
    def draw(self, surface) -> None:
        surface.fill(self.bg_color)
        width = self.bg_clouds.get_width()
        
        for x in range(LEVEL_WIDTH + 300):
            surface.blit(self.bg_clouds, ((x * width) + self.bg_scroll * 0.4, 0))
            surface.blit(self.bg_further, ((x * width) + self.bg_scroll * 0.5, SCREEN_HEIGHT - self.bg_further.get_height() - 450))
            surface.blit(self.bg_far, ((x * width) + self.bg_scroll * 0.6, SCREEN_HEIGHT - self.bg_far.get_height() - 300))
            surface.blit(self.bg_medium, ((x * width) + self.bg_scroll * 0.7, SCREEN_HEIGHT - self.bg_medium.get_height() - 150))
            surface.blit(self.bg_near, ((x * width) + self.bg_scroll * 0.8, SCREEN_HEIGHT - self.bg_near.get_height()))

    # TODO: right now the parallax factor is hard coded; move to level_data.py to allow different factors for different levels

class EnvironmentalEffects(pygame.sprite.Group):
    def __init__(self, effect, screen) -> pygame.sprite.Group:
        super().__init__()
        from animation_data import anim
        self.anim = anim
        self.screen = screen
        self.wind = Wind(-1)  # blowing toward the left of the screen
        self.fall_from_top = 0
        self.last_leaf = 0
        self.last_update = 0 
        

    def _add_leaf(self) -> None:
        now = pygame.time.get_ticks() 
        if random.random() < 1/30: # making sure we've waited long enough
            leaf = GameTileAnimation(16,16,randint(SCREEN_WIDTH/2, SCREEN_WIDTH*2), randint(0, SCREEN_HEIGHT), self.anim['environment']['leaves'])
            leaf.x_vel = random.uniform(-4, -1)
            leaf.y_vel = random.randint(1, 2)
            leaf.animation.active = True
            self.add(leaf)
            self.last_leaf = now
    

    def update(self, scroll) -> None:
       
        for sprite in self.sprites():
            sprite.rect.centerx += scroll  # compensating for scrolling
            if random.random() < 0.01:  # one in 10 times
                sprite.y_vel = random.randint(1, 2)

            sprite.rect.centerx += int(sprite.x_vel)
            sprite.rect.centery += int(sprite.y_vel)
            if sprite.rect.centery > SCREEN_HEIGHT:
                sprite.kill()
            sprite.image = sprite.animation.get_image()
            
        if len(self.sprites()) < 100:
            self._add_leaf()

class Wind:
    """ Defines the wind speed both overall and at various heights, using sine waves
        Returns the added wind component to velocity in the x direction depending on height"""
    def __init__(self, baseline) -> None:
        self.wind_direction = baseline
        self.wind_speed = -1
        self.max_wind_speed = 3
        self.last_update = 0

        # Keep track of the wind speed change over time
        self.wind_speed_change = 0.001 

    def update_wind_speed(self) -> float:
        now = pygame.time.get_ticks()
        if now - self.last_update > 200:
            # Update the wind speed
            self.wind_speed += self.wind_speed_change
            if self.wind_speed > self.max_wind_speed or self.wind_speed < -self.max_wind_speed:  # too much speed, so we start reducing
                self.wind_speed_change = -self.wind_speed_change
            self.last_update = now
            return self.wind_speed

        # Reducing down to something that works on our scale
        print(self.wind_speed)
        return 0
        

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
        Values range between 0 and 100 
    """
    point_list = [] * points

    # Define the maximum amplitude of the wave
    amplitude = 50

    # Define the number of points to be plotted
    points = 1000

    # Define the start and end points along the x-axis
    start = math.pi /2
    end = (5 * math.pi /2) 

    # Define the step size for each point along the x-axis
    step = (end - start) / points

    # Calculate the x and y coordinates for each point
    for i in range(points):
        x = start + i * step
        y = amplitude * math.sin(x) + 150

        point_list.append(y-100)

    return point_list
