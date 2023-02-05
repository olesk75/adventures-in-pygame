import pygame
import sys
import logging

from settings import * 
from level import Level
from level_data import GameAudio
from decor_and_effects import GamePanel, fade_to_color


FPS = 60

class Game:
    def __init__(self) -> None:
        self.state = GS_PLAYING  # we start with the welcome screen
        
        # game attributes
        self.max_level = 2
        self.score = 0
        self.health_max = PLAYER_HEALTH
        self.health_current = self.health_max
        self.inventory = []  # player inventory items
        self.powers_max = 1
        self.powers_current = self.powers_max
        self.level_audio = None
        self.faded = False
        
        # user interface 
        self.panel = GamePanel(screen)
        self.panel.setup_bars(self.health_current, self.health_max) 
        self.font = pygame.font.Font("assets/font/OldSchoolAdventures-42j9.ttf", 32)  

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
    
    def check_level_complete(self) -> None:
        if self.level.level_complete == True:
            self.state = GS_LEVEL_COMPLETE
            logging.debug('GAME state: LEVEL COMPLETE ')
            

    def check_game_over(self) -> None:
        """ Check if out of health"""
        if self.level.player.state['active'] == DEAD:
            self.max_level = 1
            self.level_audio.music.stop()

            self.state = GS_GAME_OVER
            logging.debug('GAME state: GAME OVER ')
            

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

    def game_over(self) -> None:
        if not self.faded:
            fade_to_color(pygame.Color('red'))  # fade to red
            self.faded = True

        self.write_text("GAME OVER", WHITE, 0, 200, align='center')
        self.write_text(f"SCORE : {self.level.player_score}", WHITE, 0, 300, align='center')
        self.write_text(f"HIGH SCORE : 99999", WHITE, 0, 400, align='center')
        self.write_text("Press SPACE to try again, Q to quit", WHITE, 0, 500, align='center')

        keys = pygame.key.get_pressed()

        if keys[pygame.K_q]:
            self.state = GS_QUIT
            
        if keys[pygame.K_SPACE]:
            game.create_level(1)  # starting at level 1
            fade_to_color(pygame.Color('black'))  # fade to red
            self.faded = False
            self.state = GS_PLAYING

    def level_complete(self) -> None:
        if not self.faded:
            fade_to_color(pygame.Color('black'))  # fade to black
            self.faded = True
            
        self.write_text(f"LEVEL {self.level.current_level} COMPLETE", WHITE, 0, 200, align='center')
        self.write_text(f"SCORE : {self.level.player_score}", WHITE, 0, 300, align='center')
        self.write_text(f"HIGH SCORE : 99999", WHITE, 0, 400, align='center')
        self.write_text("Press SPACE to continue to the next level Q to quit", WHITE, 0, 500, align='center')

        keys = pygame.key.get_pressed()

        if keys[pygame.K_q]:
            self.state = GS_QUIT
            
        if keys[pygame.K_SPACE]:
            game.create_level(self.level.current_level + 1)  # next level!
            self.faded = False
            self.state = GS_PLAYING
            fade_to_color(pygame.Color('white'))  # fade to white


    def write_text(self, text: str, color: pygame.Color, x :int, y: int, align: str=None) -> None:
        text_img = self.font.render(text, True, color)  # surface with the string 
        if align == 'center':  # we ignore x and calculate x based on length of string
            x = (SCREEN_WIDTH / 2) - (text_img.get_width() / 2)  # start half of the text length left of x center
        

        screen.blit(text_img, (x, y))
        pygame.display.update()
            
            
        #self.screen.blit(surf, (self.player.rect.centerx, self.player.rect.top - self.y_size))    


    def run(self) -> None:
        """ Run the game """
        self.level.run()
        self.check_damage_effects()
        self.health_current = self.level.player.health_current
        self.panel.inventory = self.level.player_inventory
        self.panel.draw(self.level.player_score, self.health_current, 10)  # TODO: fox stomp
        self.check_level_complete()
        self.check_game_over()

# Pygame setup
pygame.init()
#screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)  # OSX
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()
game = Game()
game.create_level(1)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
    if game.state == GS_PLAYING:
        game.run() 
    
    if game.state == GS_GAME_OVER:
        game.game_over()

    if game.state == GS_QUIT:
       pygame.quit()
       sys.exit()

    if game.state == GS_LEVEL_COMPLETE:
        game.level_complete()
        

    pygame.display.update()
    clock.tick(FPS)
