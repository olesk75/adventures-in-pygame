import pygame
import random
import math

from random import randint
from level_data import *
from settings import *

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
        self.bg_clouds = pygame.image.load(background['clouds']).convert_alpha()
        self.bg_color = background['background_color']

    def update(self,bg_scroll) -> None:
        self.bg_scroll = bg_scroll
    
    def draw(self, surface) -> None:
        surface.fill(self.bg_color)
        width = self.bg_clouds.get_width()
        
        for x in range(LEVEL_WIDTH + 300):
            surface.blit(self.bg_clouds, ((x * width) + self.bg_scroll * 0.5, 0))
            surface.blit(self.bg_far, ((x * width) + self.bg_scroll * 0.6, SCREEN_HEIGHT - self.bg_far.get_height() - 300))
            surface.blit(self.bg_medium, ((x * width) + self.bg_scroll * 0.7, SCREEN_HEIGHT - self.bg_medium.get_height() - 150))
            surface.blit(self.bg_near, ((x * width) + self.bg_scroll * 0.8, SCREEN_HEIGHT - self.bg_near.get_height()))

    # TODO: right now the parallax factor is hard coded; move to level_data.py to allow different factors for different levels

class EnvironmentalEffects(pygame.sprite.Group):
    def __init__(self, effect) -> pygame.sprite.Group:
        super().__init__()

        self.wind = Wind(-3)  # blowing toward the left of the screen
        self.fall_from_top = 0
        self.last_leaf = 0
        
        if effect == 'leaves':
            self.leaf_surface = pygame.image.load('assets/sprites/leaf.png').convert_alpha()
        
    def _add_leaf(self) -> None:
        now = pygame.time.get_ticks() 
        if random.random() < 1/30: # making sure we've waited long enough
            print('gos')
            leaf = pygame.sprite.Sprite()
            leaf.image = self.leaf_surface
            leaf.rect = pygame.rect.Rect((SCREEN_WIDTH, (randint(0, SCREEN_HEIGHT))), leaf.image.get_size())
            self.add(leaf)
            self.last_leaf = now

    def update(self, scroll) -> None:
        for sprite in self.sprites():
            sprite.rect.centerx += scroll  # compensating for scrolling

            sprite.rect.centery += 1
            if sprite.rect.centery > SCREEN_HEIGHT:
                sprite.kill()

            # Updating wind impact
            sprite.rect.centerx += self.wind.get_speed(sprite.rect.centery)


        if len(self.sprites()) < 10:
        #     print(f'leaves in the air: {len.self.sprites()}')
            self._add_leaf()

class Wind:
    """ Defines the wind speed both overall and at various heights, using sine waves
        Returns the added wind component to velocity in the x direction depending on height"""
    def __init__(self, baseline) -> None:
        self.baseline = 1  # the constant background speed
        self.wave_length = 200  # wavelength for sine function
        self.amplitude = 2
        self.last_baseline = pygame.time.get_ticks()
        self.counter = 0

    def _update_baseline(self) -> None:
        now = pygame.time.get_ticks()
        wind_baseline = 0  
        if now - self.last_baseline > 1000:
            wind_baseline = math.sin(self.counter/4000) * 1
            self.counter += 1
        print(wind_baseline)
        return wind_baseline
        

    def get_speed(self, y) -> int:
        baseline = self._update_baseline()
        # Returns the x speed at height y
        x = math.sin(y/self.wave_length) * self.amplitude # varies between 0 and 1
        print(x)
        x -= abs(baseline)
        return int(x)
        