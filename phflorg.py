import pygame
import random
import pickle

from game_world import GameWorld, WorldData
from animation import Animation
from spritesheet import SpriteSheet
from player import Player, PlayerData
from monsters import Monster
from game_data import monsters


# Game variables in a named tuple (new in Python 3.6) - we pass this to instances who need it
phflorg_data = WorldData(
    SCREEN_WIDTH = 1920,
    SCREEN_HEIGHT = 1080,
    LEVEL_WIDTH = 4,
    TOT_WIDTH = 20000,
    GRAVITY = 0.5,
    MAX_PLATFORMS = 10,
    JUMP_HEIGHT = 15,
    PLAYER_BOUNCING = False,
    SCROLL_THRESHOLD = 400,  # How far left/right of center player can be before we scroll the background
    ROWS = 16,
    MAX_COLS = 150,
    TILE_SIZE = 1080 // 16,
    TILE_TYPES = 21,
)

# Initializing
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.init()
pygame.init()

# Create game window
screen = pygame.display.set_mode((phflorg_data.SCREEN_WIDTH, phflorg_data.SCREEN_HEIGHT))
pygame.display.set_caption("Phflorg the Destroyer")

# Set frame rate
clock = pygame.time.Clock() 
FPS = 60

# Player state
player_state = PlayerData()

# Game state variables
scroll = 0
bg_scroll = 0
player_dying = False
game_over = False
fade_counter = 0

# Define colors
WHITE    = (255, 255, 255)
BLACK    = (  0,   0,   0)
RED      = (255,   0,   0)
DARKGRAY = ( 20,  20,  20)

# Define fonts
font_small = pygame.font.SysFont('Lucida Sans', 40)
font_big = pygame.font.SysFont('Lucida Sans', 60)

# Load audio for player
hit_fx = pygame.mixer.Sound('assets/sound/Hit/OGG/Hit 2 - Sound effects Pack 2.ogg')
jump_fx = pygame.mixer.Sound('assets/sound/Jump/OGG/Jump 5 - Sound effects Pack 2.ogg')
death_fx = pygame.mixer.Sound('assets/sound/Lose/OGG/Lose 7 - Sound effects Pack 2.ogg')
player_sound_effects = [hit_fx, jump_fx, death_fx]

# Load audio for world
item_pickup_fx = pygame.mixer.Sound('assets/sound/Power-up/OGG/Powerup 7 - Sound effects Pack 2.ogg')


#load images
pine1_img = pygame.image.load('assets/pine1.png').convert_alpha()
pine2_img = pygame.image.load('assets/pine2.png').convert_alpha()
mountain_img = pygame.image.load('assets/mountain.png').convert_alpha()
sky_img = pygame.image.load('assets/sky_cloud.png').convert_alpha()


level = 1  # TODO: placeholder

phflorg_world = GameWorld(phflorg_data)  # Loading all tiles in the world, less background, mobs and player

(platforms_sprite_group, pickups_sprite_group, decor_sprite_group) = phflorg_world.load(f'level{level}_data.csv')

# Create player animations
p_sprite_sheet = SpriteSheet(pygame.image.load('assets/character-sprites2.png').convert_alpha(), 64, 64, BLACK, 2)
p_sprite_sheet_oversize = SpriteSheet(pygame.image.load('assets/character-sprites2.png').convert_alpha(), 64*3, 64*3, BLACK, 2)
player_anim_walk = Animation(p_sprite_sheet, row=11, frames=10, speed=75)
player_anim_attack = Animation(p_sprite_sheet_oversize, row=10, frames=6, speed=100)
player_anim_death = Animation(p_sprite_sheet, row=20, frames=6, speed=500)

# Create monster animations
m_sprite_sheet = SpriteSheet(pygame.image.load('assets/minotaur-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
minotaur_anim_walk = Animation(m_sprite_sheet, row=11, frames=9, speed=100)
minotaur_anim_attack = Animation(m_sprite_sheet, row=7, frames=8, speed=100)

# Function for text output
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Funtion to draw score and life panel
def draw_panel():
    draw_text(f'SCORE: {player_state.score}', font_small, WHITE, 0, 0)

# Function for drawing the background
def draw_bg(bg_scroll):
    SKY_BLUE = (130, 181, 210)
    screen.fill(SKY_BLUE)
    width = sky_img.get_width()

    for x in range(phflorg_data.LEVEL_WIDTH):
        screen.blit(sky_img, ((x * width) + bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) + bg_scroll * 0.6, phflorg_data.SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) + bg_scroll * 0.7, phflorg_data.SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) + bg_scroll * 0.8, phflorg_data.SCREEN_HEIGHT - pine2_img.get_height()))


# Function to load hish score from file
def load_high_score():
    save_state = PlayerData
    with open('highscore.dat', 'rb') as high_score_file:
        try:
            high_score = pickle.load(high_score_file)
        except EOFError:  # In case file does not exist with valid high score already
            return(0)
    
    #print(f'Read high score from file: {high_score}')
    return(high_score)

# Function to save score to file
def save_high_score(high_score):
    with open('highscore.dat', 'wb') as save_file:
        pickle.dump(high_score, save_file)    

def add_monsters(mobs):
    # Monster instances (for loop later)
    minotaur_list = []
    for monster in mobs:
        if monster[2] == 'm':  # minotaur
            minotaur_list.append(Monster(monster[0], monster[1], minotaur_anim_walk, minotaur_anim_attack, monster[3]))

    return minotaur_list

monster_list = add_monsters(monsters)

"""
Defining instances
"""
# Player instance
player = Player(phflorg_data.SCREEN_WIDTH // 2, phflorg_data.SCREEN_HEIGHT -150 , phflorg_data, \
    player_anim_walk, player_anim_attack, player_anim_death, player_sound_effects)

# Monsters
add_monsters(monsters)

# Load previous high score
high_score = load_high_score()


"""
Main game loop
"""
run = True
while run:
    clock.tick(FPS)
    
    if not game_over:
        # check keypresses and update position (and get back scroll value if any)
        scroll, score_add = player.move(platforms_sprite_group)
        player_state.score += score_add


         # Update tiles
        platforms_sprite_group.update(scroll)
        pickups_sprite_group.update(scroll)
        decor_sprite_group.update(scroll)
        
       
        # draw background
        bg_scroll += scroll
        if bg_scroll >= phflorg_data.SCREEN_WIDTH:
            bg_scroll = 0
        draw_bg(bg_scroll)



        # Draw all sprites, monsters and player
        platforms_sprite_group.draw(screen)
        pickups_sprite_group.draw(screen)
        decor_sprite_group.draw(screen)
        player.draw(screen)

        # Draw panel
        draw_panel()

        # check game over from falling
        if player.rect.top > phflorg_data.SCREEN_HEIGHT:
            game_over = True
            player.dead = True
            print('!!!GAME OVER!!!')  # DEBUG


        # If player has been hit and is dying, we skip checking for more hits
        if player.dying:
            game_over = player.check_game_over()  # if we're done dying, we're dead

    
        # TODO: we need a mechanism to track monsters when off-screen. They should be persistent, but also not need collision detection etc. 
        for mob in monster_list:
            mob.animation.active = True
            mob.update(scroll, platforms_sprite_group)
            mob.draw(screen)
            #pygame.draw.rect(screen, (0,0,255), mob.rect_detect, 2 )  # DEBUG: to see hitbox for detection (blue)
            
            # Mob detecting player
            if pygame.Rect.colliderect(player.rect, mob.rect_detect):
                mob.attacking = True
                #pygame.draw.rect(screen, (255,0,0), mob.rect_attack, 2 )  # DEBUG: to see hitbox for detection (red)
                #print(f'Monster {mob.name} attacking!')  # DEBUG
            else:  # Mob not detecting player
                mob.attacking = False  # if we move out of range, the mob will stop attacking
                mob.rect_attack = pygame.Rect(0,0,0,0)  # resetting attack rect
            
            # Mob attack: trigger player dying if a) collision with mob, b) mob is in attack mode and c) mob is not already dead
            if pygame.Rect.colliderect(player.rect, mob.rect_attack) and mob.attacking and not mob.dead:
                player.dying = True  # we start the death sequence
                player.death.anim_counter = 0  # Animation counter the death animation

            # Mob collision: trigger player dying if a) collision with mob, b) mob is not already dead
            if pygame.Rect.colliderect(player.rect, mob.rect) and not mob.dead:
                player.dying = True  # we start the death sequence
                player.death.anim_counter = 0  # Animation counter the death animation

            # If player is attacking, check if mob hit --> mob dead
            if player.attacking:
                if pygame.Rect.colliderect(player.get_attack_rect(), mob.rect): 
                    if not mob.dead:  # First time collision detected, we bump the mob back to indicate hit
                        mob.vel_y = -5
                        mob.direction  = -player.flip
                        player_state.score += 100
                    mob.dead = True  # we run through the death anim sequence
                        

    else:  # Game over 
        if fade_counter < phflorg_data.SCREEN_WIDTH / 2:
            fade_counter += 15
            pygame.draw.rect(screen, DARKGRAY, (0,0, fade_counter, phflorg_data.SCREEN_HEIGHT))
            pygame.draw.rect(screen, DARKGRAY, (phflorg_data.SCREEN_WIDTH - fade_counter, 0, phflorg_data.SCREEN_WIDTH, phflorg_data.SCREEN_HEIGHT))

        else:       
            draw_text('GAME OVER', font_big, WHITE, (phflorg_data.SCREEN_WIDTH/2)-130,300)
            draw_text('SCORE: ' + str(player_state.score), font_big, WHITE, (phflorg_data.SCREEN_WIDTH/2)-100, 400)
            if player_state.score > high_score:
                    high_score = player_state.score
                    draw_text('NEW HIGH SCORE: ' + str(high_score), font_big, WHITE, (phflorg_data.SCREEN_WIDTH/2)-180, 500)
            else:
                draw_text('HIGH SCORE: ' + str(high_score), font_big, WHITE, (phflorg_data.SCREEN_WIDTH/2)-150, 500)
            draw_text('Press space to play again', font_big, WHITE, (phflorg_data.SCREEN_WIDTH/2)-250, 600)
            key = pygame.key.get_pressed()
            if key[pygame.K_q]:
                exit(0)
            if key[pygame.K_SPACE]:
                # Save high score
                save_high_score(high_score)
                #print(f'wrote {player_state.score}')  # DEBUG

                # Reset all variables
                game_over = False
                player.alive = True
                player.dying = False
                player.dead = False
                player.attacking = False

                player_state.score = 0
                scroll = 0
                
                # Reset player position
                player.rect.center = (phflorg_data.SCREEN_WIDTH // 2, phflorg_data.SCREEN_HEIGHT - 150)
                # Reset platforms
                #platform_group.empty()
                # Create the starting platform
                #platform_group = add_platforms(platform_list)

                fade_counter = 0
                # Add monsters

                monster_list = add_monsters(monsters)

    # The main even handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Update display window
    pygame.display.update()

pygame.quit()