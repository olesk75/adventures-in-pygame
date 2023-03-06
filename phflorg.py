import pygame as pg
from pygame.locals import *

import sys
import logging

from game_data.settings import * 
from game_world import GameState, Game


FPS = 60
logging.basicConfig(level=logging.DEBUG)


# Command line arguments
if len(sys.argv):
    if '--no-music' in sys.argv:
        MUSIC_ON = False
        logging.debug('Music is OFF')
    if '--no-sound' in sys.argv:
        SOUNDS_ON = False
        logging.debug('Sound effects are OFF')

# pg setup
# Initializing
pg.mixer.pre_init(44100, -16, 2, 512)
pg.init()
pg.mixer.init()

gs = GameState()

# Checking for controllers/joysticks
joysticks = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]

if joysticks:
    logging.debug(f'Found {pg.joystick.get_count()} available game controllers: {joysticks}')
    for n in range(pg.joystick.get_count()):
        joys = pg.joystick.Joystick(n)
        logging.debug(joys.get_name())
        logging.debug(joys.get_numaxes())
        logging.debug(joys.get_numhats())
        logging.debug(joys.get_numbuttons())
else:
    logging.debug('No game controllers found')

# Resolution and screen setup
current_screen = pg.display.Info()
monitor_res = ( current_screen.current_w, current_screen.current_h)
width, height = SCREEN_WIDTH, SCREEN_HEIGHT

  
logging.debug(f'Screen resolution : width: {width}, height:{height}, {monitor_res})')
flags = SCALED
_screen = pg.display.set_mode((width, height), flags) 
screen = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pg.time.Clock()

game = Game(gs, screen)  # Here we pass the GameState instance to game, which will pass it to Level, which will pass it to Player

motion = [0, 0]
previous_state = gs.game_state

font = pg.font.Font(None, 36)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # Keyboard - key pressed
        if event.type == KEYDOWN:
            match event.key:
                case pg.K_q | pg.K_ESCAPE: gs.user_input['quit'] = True
                case pg.K_RIGHT: gs.user_input['right'] = True
                case pg.K_LEFT: gs.user_input['left'] = True
                case pg.K_UP: gs.user_input['up'] = True
                case pg.K_DOWN: gs.user_input['down'] = True
                case pg.K_SPACE: gs.user_input['attack'] = True

            # Additionally, if we're in the arena we have additional shortcuts
            if gs.level_current == 0:
                match event.key:
                    case pg.K_1: gs.monster_spawn_queue.append(1)
                    case pg.K_2: gs.monster_spawn_queue.append(2)
                    case pg.K_3: gs.monster_spawn_queue.append(3)
                    case pg.K_4: gs.monster_spawn_queue.append(4)
                    case pg.K_5: gs.monster_spawn_queue.append(5)

        # Keyboard - key let go of
        if event.type == KEYUP:
            match event.key:
                case pg.K_RIGHT: gs.user_input['right'] = False
                case pg.K_LEFT: gs.user_input['left'] = False
                case pg.K_UP: gs.user_input['up'] = False
                case pg.K_DOWN: gs.user_input['down'] = False
                case pg.K_SPACE: gs.user_input['attack'] = False

        if event.type == JOYBUTTONDOWN:
            match event.button:
                case 0: gs.user_input['up'] = True
                case 1: gs.user_input['cast'] = True
                case 2: gs.user_input['attack'] = True

        if event.type == JOYBUTTONUP:
            match event.button:
                case 0: gs.user_input['up'] = False
                case 1: gs.user_input['cast'] = False
                case 2: gs.user_input['attack'] = False
                
        if event.type == JOYAXISMOTION and event.axis == 0:
                if event.value < -0.1:
                    gs.user_input['left'] = True
                elif event.value > 0.1:
                    gs.user_input['right'] = True
                else:
                    gs.user_input['left'] = False
                    gs.user_input['right'] = False

        if event.type == JOYHATMOTION:
            #print(event)
            pass

    
    if gs.game_state == GS_PLAYING:
        game.run() 
    
    if gs.game_state == GS_GAME_OVER:
        game.game_over()

    if gs.game_state == GS_QUIT:
       pg.quit()
       sys.exit()

    if gs.game_state == GS_LEVEL_COMPLETE:
        game.level_complete()

    if gs.game_state == GS_MAP_SCREEN:
        game.map_screen()

    if gs.game_state == GS_WELCOME:
        game.welcome_screen()

    if previous_state != gs.game_state:
        previous_state = gs.game_state
        gs.game_fade_ready = True
        
    
    if SHOW_FPS:
        fps_text = font.render(f'FPS: {clock.get_fps():.2f}', True, (255, 255, 0))
        screen.blit(fps_text, (10, 100))

    #_screen.blit(pg.transform.scale(screen, (width, height)), (0, 0))
    _screen.blit(screen, (0, 0))

    pg.display.update()
    clock.tick(FPS)


