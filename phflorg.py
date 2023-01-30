import pygame
import sys
import logging

from settings import * 
from level import Level
from level_data import GameAudio
from engine import GamePanel


FPS = 60

class Game:
    def __init__(self) -> None:

        # game attributes
        self.max_level = 1
        self.score = 0
        self.health_max = 1000
        self.health_current = self.health_max
        self.inventory = []  # player inventory items
        self.powers_max = 1
        self.powers_current = self.powers_max
        self.level_audio = None
        
        # user interface 
        self.panel = GamePanel(screen)
        self.panel.setup_bars(self.health_current, self.health_max)

        # damage overlay (red tendrils)
        self.damage_img = pygame.image.load('assets/panel/damage.png').convert_alpha()

        self.last_run = 0
        self.slowmo = False

    def create_level(self,current_level) -> None:
        """ Create each level """
        self.level = Level(current_level,screen, self.health_max)
        self.level_audio = GameAudio(current_level)
        self.level_audio.music.play(-1,0.0)
        self.level_audio.music.set_volume(0.4)
        

    def check_game_over(self) -> None:
        """ Check if out of health"""
        if self.health_current == 0 or self.level.player_dead:
            self.max_level = 1
            self.level_audio.music.stop()
            logging.debug('--- GAME OVER ---')
            logging.debug('     EXITING')
            exit(0)

    def check_damage_effects(self) -> None:
        """ Slow-motion effect after player loses health """
        global FPS
        if self.slowmo == True:
            screen.blit(self.damage_img, (0,0))
            if pygame.time.get_ticks() - self.last_run > 500:  # 1 second of slow-motion after a hit
                FPS = 60
                self.slowmo = False 
        elif self.health_current > self.level.player.health_current:
            FPS = 10
            self.slowmo = True
            self.last_run = pygame.time.get_ticks()

    def run(self) -> None:
        """ Run the game """
        self.level.run()
        self.check_damage_effects()
        self.health_current = self.level.player.health_current
        self.panel.inventory = self.level.player_inventory
        self.panel.draw(self.level.player_score, self.health_current) 
        
        self.check_game_over()

# Pygame setup
pygame.init()
#screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)  # OSX
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()
game = Game()
game.create_level(0)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
    #screen.fill('grey')
    game.run() 

    pygame.display.update()
    clock.tick(FPS)
