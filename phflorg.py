import pygame
from pygame.locals import *

import sys
import logging

from settings import * 

from game_world import GameState, Game


FPS = 60
logging.basicConfig(level=logging.DEBUG)


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

gs = GameState()

# Checking for controllers/joysticks
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

if joysticks:
    logging.debug(f'Found {pygame.joystick.get_count()} available game controllers: {joysticks}')
    for n in range(pygame.joystick.get_count()):
        joys = pygame.joystick.Joystick(n)
        logging.debug(joys.get_name())
        logging.debug(joys.get_numaxes())
        logging.debug(joys.get_numhats())
        logging.debug(joys.get_numbuttons())
else:
    logging.debug(f'No game controllers found')

# Resolution and screen setup
current_screen = pygame.display.Info()
monitor_res = ( current_screen.current_w, current_screen.current_h)
width, height = SCREEN_WIDTH, SCREEN_HEIGHT
if current_screen.current_w < SCREEN_WIDTH or current_screen.current_h < SCREEN_HEIGHT:
    width  = SCREEN_WIDTH // 1.5
    height  = SCREEN_HEIGHT // 1.5
    print(width,height, monitor_res)
_screen = pygame.display.set_mode((width, height)) 
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()

game = Game(gs, screen)  # Here we pass the GameState instance to game, which will pass it to Level, which will pass it to Player
game.create_level(FIRST_LEVEL)


motion = [0, 0]
previous_state = gs.game_state

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Keyboard - key pressed
        if event.type == KEYDOWN:
            if event.key in(K_q, K_ESCAPE):
                gs.user_input['quit'] = True
            if event.key == K_RIGHT:
                gs.user_input['right'] = True
            if event.key == K_LEFT:
                gs.user_input['left'] = True
            if event.key == K_UP:
                gs.user_input['up'] = True
            if event.key == K_DOWN:
                gs.user_input['down'] = True
            if event.key == K_SPACE:
                gs.user_input['attack'] = True


        # Keyboard - key let go of
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                gs.user_input['right'] = False
            if event.key == K_LEFT:
                gs.user_input['left'] = False
            if event.key == K_UP:
                gs.user_input['up'] = False
            if event.key == K_DOWN:
                gs.user_input['down'] = False
            if event.key == K_SPACE:
                gs.user_input['attack'] = False

        if event.type == JOYBUTTONDOWN:
            if event.button == 0:
                gs.user_input['up'] = True
            if event.button == 2:
                gs.user_input['attack'] = True
        if event.type == JOYBUTTONUP:
            if event.button == 0:
                gs.user_input['up'] = False
            if event.button == 2:
                gs.user_input['attack'] = False
                
        if event.type == JOYAXISMOTION:
            #print(event)
            if event.axis == 0:
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
       pygame.quit()
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
        
    _screen.blit(pygame.transform.scale(screen, (width, height)), (0, 0))

    pygame.display.update()
    clock.tick(FPS)
