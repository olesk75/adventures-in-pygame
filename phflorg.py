import pygame
import sys
import logging

from settings import * 
from level import Level
from level_data import GameAudio
from decor_and_effects import GamePanel, fade_to_color


FPS = 60
logging.basicConfig(level=logging.DEBUG)

class Game:
    def __init__(self) -> None:
        self.state = GS_WELCOME  # we start with the welcome screen
        
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
        self.font = pygame.font.Font("assets/font/Silver.ttf", 64)  

        # damage overlay (red tendrils)
        self.damage_img = pygame.image.load('assets/panel/damage.png').convert_alpha()

        # map screen background
        self.map_img = pygame.image.load('assets/map/map.png').convert_alpha()

        # welcome screen background
        self.welcome_img = pygame.image.load('assets/map/welcome-screen.png').convert_alpha()

        self.last_run = 0
        self.slowmo = False

    def create_level(self,current_level) -> None:
        """ Create each level """
        self.level = Level(current_level,screen, self.health_max)
        if MUSIC_ON:
            self.level_audio = GameAudio(current_level)
            self.level_audio.music.play(-1,0.0)
            self.level_audio.music.set_volume(0.4)

    def check_level_complete(self) -> None:
        """ Check if player has successfully reached end of the level """
        if self.level.level_complete == True:
            self.state = GS_LEVEL_COMPLETE
            logging.debug('GAME state: LEVEL COMPLETE ')
            

    def check_game_over(self) -> None:
        """ Check if player is DEAD """
        if self.level.player.state['active'] == DEAD:
            self.max_level = 1
            if MUSIC_ON:
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
            # TODO: add slo-mo for stom as well, and player boss death

    def game_over(self) -> None:
        """ Go to GAME OVER screen """
        if not self.faded:
            fade_to_color(pygame.Color('red'))  # fade to red  # TODO: fix! doesn't work
            self.faded = True

        self.write_text("GAME OVER", WHITE, 0, 200, align='center')
        self.write_text(f"SCORE : {self.level.player_score}", WHITE, 0, 300, align='center')
        self.write_text(f"HIGH SCORE : 99999", WHITE, 0, 400, align='center')
        self.write_text("Press SPACE to try again,  Q to quit", WHITE, 0, 500, align='center')

        keys = pygame.key.get_pressed()

        if keys[pygame.K_q]:
            self.state = GS_QUIT
            
        if keys[pygame.K_SPACE]:
            self.create_level(1)  # starting at level 1
            fade_to_color(pygame.Color('black'))  # fade to black
            self.faded = False

    def level_complete(self) -> None:
        """ Go to LEVEL COMPLETE SCREEN """
        if not self.faded:
            fade_to_color(pygame.Color('black'))  # fade to black
            self.faded = True
            
        self.write_text(f"LEVEL {self.level.current_level} COMPLETE", WHITE, 0, 200, align='center')
        self.write_text(f"SCORE : {self.level.player_score}", WHITE, 0, 300, align='center')
        self.write_text(f"HIGH SCORE : 99999", WHITE, 0, 400, align='center')
        self.write_text("Press ENTER to continue to the world map,  Q to quit", WHITE, 0, 500, align='center')

        keys = pygame.key.get_pressed()

        if keys[pygame.K_q]:
            self.state = GS_QUIT
            
        if keys[pygame.K_RETURN]:
            self.faded = False
            fade_to_color(pygame.Color('white'))  # fade to white
            self.state = GS_MAP_SCREEN

    def map_screen(self) -> None:
        """ Show the worldmap_img map screen """
        map_bg = pygame.transform.scale(self.map_img, (SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()

        screen.blit(map_bg,(0,0))                      


        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            self.state = GS_QUIT
            
        if keys[pygame.K_SPACE]:
            game.create_level(self.level.current_level + 1)  # next level!
            fade_to_color(pygame.Color('black'))  # fade to black
            self.faded = False
            self.state = GS_PLAYING

    def welcome_screen(self) -> None:
        """ Show the welcome screen """
        welcome_bg = pygame.transform.scale(self.welcome_img, (SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()

        screen.blit(welcome_bg,(0,0))                      

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            self.state = GS_QUIT
            
        if keys[pygame.K_SPACE]:
            game.create_level(FIRST_LEVEL)  # next level!
            fade_to_color(pygame.Color('black'))  # fade to black
            self.faded = False
            self.state = GS_PLAYING


    def write_text(self, text: str, color: pygame.Color, x :int, y: int, align: str=None) -> None:
        """ Write text on screen """
        text_img = self.font.render(text, True, color)  # surface with the string 
        if align == 'center':  # we ignore x and calculate x based on length of string
            x = (SCREEN_WIDTH / 2) - (text_img.get_width() / 2)  # start half of the text length left of x center
        
        screen.blit(text_img, (x, y))
        pygame.display.update()  # force manual update  # TODO: fix


    def run(self) -> None:
        """ Run the game """
        self.level.run()
        self.check_damage_effects()
        self.health_current = self.level.player.health_current
        self.panel.inventory = self.level.player_inventory
        self.panel.draw(self.level.player_score, self.health_current, self.level.player.stomp_counter)
        self.check_level_complete()
        self.check_game_over()


# Command lind arguments
if len(sys.argv):
    if '--no-music' in sys.argv:
        MUSIC_ON = False
        logging.debug('Music is OFF')
    if '--no-sound' in sys.argv:
        SOUNDS_ON = False
        logging.debug('Sound effects are OFF')


# Pygame setup
pygame.init()

# Resolution and screen setup
current_screen = pygame.display.Info()
monitor_res = ( current_screen.current_w, current_screen.current_h)
width, height = SCREEN_WIDTH, SCREEN_HEIGHT
if current_screen.current_w < SCREEN_WIDTH or current_screen.current_h < SCREEN_HEIGHT:
    width  = SCREEN_WIDTH // 1.5
    height  = SCREEN_HEIGHT // 1.5
    print(width,height, monitor_res)
_screen = pygame.display.set_mode((width, height))  # , pygame.FULLSCREEN)
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

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

    if game.state == GS_MAP_SCREEN:
        game.map_screen()

    if game.state == GS_WELCOME:
        game.welcome_screen()
        
    _screen.blit(pygame.transform.scale(screen, (width, height)), (0, 0))

    #_screen.blit(screen, (0, 0))
    pygame.display.update()
    clock.tick(FPS)
