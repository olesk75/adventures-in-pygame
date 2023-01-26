import pygame
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