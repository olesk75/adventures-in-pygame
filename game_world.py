import pygame, logging

from settings import *
from game_functions import *

from level import Level
from level_data import GameAudio  
from decor_and_effects import GamePanel

class GameState:
    """
    Used for sending keypresses and joystick input to player ++
    """
    def __init__(self) -> None:
        # --> Type declarations for all variables

        # Player variables
        self.user_input: dict
        self.player_health_max: int
        self.player_health: int
        self.player_dot: int  # damage over time, like being on fire, posion etc.
        self.player_invincible: bool
        self.player_hit: bool  # has the player been hit recently
        self.player_powers_max: int
        self.player_powers_current: int
        self.player_score: int
        self.player_stomp_counter: int
        self.player_inventory: list  # player inventory items

        # Level variables
        self.level_current: int
        self.level_max: int
        self.level_complete: bool
    
        # Game variables
        self.game_state: int  # One of the global GAME_STATE contants
        self.game_state_previous: int
        self.game_fade_counter: int
        self.game_fade_ready: bool
        self.game_fade_last_update: int

        # Specific arena variables to manually spawn monsters
        self.monster_spawn_queue: list
        
        self.reset()

    
    def reset(self) -> None:
        # --> Player variables
        self.user_input = {
             'left': False,
             'right': False,
             'up': False,
             'down': False,
             'attack': False,
             'cast': False,  
             'quit': False,
        }
        self.player_health_max = PLAYER_HEALTH
        self.player_health = PLAYER_HEALTH
        self.player_dot = False
        self.player_invincible = False
        self.player_hit = False
        self.player_powers_max = 1
        self.player_powers_current = self.player_powers_max
        self.player_score = 0
        self.player_stomp_counter = 0
        self.player_inventory = []

        # --> Level variables
        self.level_current = FIRST_LEVEL
        self.level_max = LAST_LEVEL
        self.level_complete = False

        # --> Game variables
        self.game_state = GS_WELCOME  # we start with the welcome screen
        self.game_state_previous = None
        self.game_fade_counter = 0
        self.game_fade_ready = False
        self.game_fade_last_update = 0

        # Specific arena variables to manually spawn monsters
        self.monster_spawn_queue = []
        
        

class Game:
    """

    The main game class, which sets up the UI, starts new levels etc.
    
    """
    def __init__(self, game_state, screen) -> None:
        self.gs = game_state
        self.screen = screen
        
        self.level_audio = None
        self.faded = False
        
        # user interface 
        self.panel = GamePanel(self.screen, self.gs)
        self.panel.setup_bars() 
        self.font = pygame.font.Font("assets/font/Silver.ttf", 64)  

        # damage overlay (red tendrils)
        self.damage_img = pygame.image.load('assets/panel/damage.png').convert_alpha()

        # map screen background
        self.map_img = pygame.image.load('assets/map/map.png').convert_alpha()

        # welcome screen background
        self.welcome_img = pygame.image.load('assets/map/welcome-screen.png').convert_alpha()

        self.last_run = 0
        self.last_fade_update = 0
        self.slowmo = False

    def create_level(self,current_level) -> None:
        """ Create each level """
        self.gs.level_current = current_level
        self.level = Level(self.screen, self.gs)
        
        if MUSIC_ON:
            self.level_audio = GameAudio(current_level)
            self.level_audio.music.play(-1,0.0)
            self.level_audio.music.set_volume(0.4)

    def check_level_complete(self) -> None:
        """ Check if player has successfully reached end of the level """
        if self.gs.level_complete == True:
            self.gs.game_state = GS_LEVEL_COMPLETE
            logging.debug('GAME state: LEVEL COMPLETE ')
            
    def check_game_over(self) -> None:
        """ Check if player is DEAD """
        if self.level.player.state['active'] == DEAD:
            self.gs.level_max = 1
            if MUSIC_ON:
                self.level_audio.music.stop()

            self.gs.game_state = GS_GAME_OVER
            logging.debug('GAME state: GAME OVER ')

    def check_damage_effects(self) -> None:
        """ Slow-motion effect after player loses health """
        global FPS
        if self.slowmo == True:
            self.screen.blit(self.damage_img, (0,0))
            if pygame.time.get_ticks() - self.last_run > 500:  # 1 second of slow-motion after a hit
                FPS = 60
                self.slowmo = False 
        elif self.gs.player_hit:
            FPS = 10
            self.slowmo = True
            self.last_run = pygame.time.get_ticks()
            self.gs.player_hit = False
            # TODO: add slo-mo for stomp as well, and player boss death

    def game_over(self) -> None:
        """ Go to GAME OVER screen """
        if self.gs.game_fade_ready:
            fade_to_color(RED, self.screen, self.gs)  # fade to RED
        else:
            draw_text("GAME OVER", self.screen, WHITE, 0, 200, align='center', font=self.font)
            draw_text(f"SCORE : {self.gs.player_score}", self.screen, WHITE, 0, 300, align='center', font=self.font)
            draw_text(f"HIGH SCORE : 99999", self.screen, WHITE, 0, 400, align='center', font=self.font)
            draw_text("Press SPACE to try again,  Q to quit", self.screen, WHITE, 0, 500, align='center', font=self.font)

            keys = pygame.key.get_pressed()

            if keys[pygame.K_q]:
                self.gs.game_state = GS_QUIT
                
            if keys[pygame.K_SPACE]:
                self.gs.reset()
                self.gs.game_state = GS_PLAYING
                self.gs.player_health = self.gs.player_health_max
                self.create_level(FIRST_LEVEL)

    def level_complete(self) -> None:
        """ Go to LEVEL COMPLETE SCREEN """
        if self.gs.game_fade_ready:
            fade_to_color(BLACK, self.screen, self.gs)  # fade to black
        else:
            draw_text(f"LEVEL {self.gs.level_current} COMPLETE", self.screen, WHITE, 0, 200, align='center')
            draw_text(f"SCORE : {self.gs.player_score}", self.screen, WHITE, 0, 300, align='center')
            draw_text(f"HIGH SCORE : 99999", self.screen, WHITE, 0, 400, align='center')
            draw_text("Press ENTER to continue to the world map,  Q to quit", self.screen, WHITE, 0, 500, align='center')

            keys = pygame.key.get_pressed()

            if keys[pygame.K_q]:
                self.gs.game_state = GS_QUIT
                
            if keys[pygame.K_RETURN]:
                self.gs.game_state = GS_MAP_SCREEN

    def map_screen(self) -> None:
        """ Show the worldmap_img map screen """
        map_bg = pygame.transform.scale(self.map_img, (SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()

        self.screen.blit(map_bg,(0,0))                      

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            self.gs.game_state = GS_QUIT
            
        if keys[pygame.K_SPACE]:
            self.create_level(self.gs.level_current + 1)  # next level!
            self.gs.game_state = GS_PLAYING

    def welcome_screen(self) -> None:
        """ Show the welcome screen """
        welcome_bg = pygame.transform.scale(self.welcome_img, (SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
        
        self.screen.blit(welcome_bg,(0,0))                      

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            self.gs.game_state = GS_QUIT
            
        if keys[pygame.K_SPACE]:
            self.create_level(FIRST_LEVEL)
            self.gs.game_state = GS_PLAYING

        if keys[pygame.K_a]:
            # We're going to the arena
            self.create_level(0)
            logging.debug('Starting level 0 - the Arena')
            self.gs.game_state = GS_PLAYING


    def run(self) -> None:
        if self.gs.game_fade_ready:
            fade_to_color(BLACK, self.screen, self.gs)  # fade to black
        else:
            """ Run the game """
            self.level.run()
            self.check_damage_effects()
            self.panel.draw()
            self.check_level_complete()
            self.check_game_over()


class GameTile(pygame.sprite.Sprite):
    """
    Customized Sprite class which allows update with scroll value, which will be triggerd by spritegroup.update(scroll)
    """
    def __init__(self) -> None:
        super().__init__()
        
    def update(self, h_scroll, v_scroll) -> None:
        # Moves the rectangle of this sprite 
        self.rect.x += h_scroll
        self.rect.y += v_scroll


class GameTileAnimation(GameTile):
    """
    Customized Sprite class which allows update with scroll value, which will be triggerd by spritegroup.update(scroll)
    """
    def __init__(self, animation) -> None:
        super().__init__()
        self.animation = animation
        self.X_CENTER = self.animation.image().get_width() // 2
        self.Y_CENTER = self.animation.image().get_height() // 2
        self.sprites = self.animation.sprites
        self.animation.active = True
        
    def update(self, h_scroll, v_scroll) -> None:
        # Moves the rectangle of this sprite 
        self.rect.x += h_scroll
        self.rect.y += v_scroll

        #print(f'scrolling {self.dx}, new x_pos: {self.rect.left}')
    
    def draw(self, screen) -> None:
        self.image = self.animation.image().convert_alpha()
        screen.blit(self.image, (self.rect.x, self.rect.y))