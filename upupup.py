import pygame
import random
import pickle

from game_world import TiledPlatform, WorldData, PlatformLocations, GameItem
from animation import Animation, StaticImage
from spritesheet import SpriteSheet
from player import Player, PlayerData
from monsters import Monster
from game_data import platform_list, monster_list, items_list


# Game variables in a named tuple (new in Python 3.6) - we pass this to instances who need it
upupup_world = WorldData(
    SCREEN_WIDTH = 1920,
    SCREEN_HEIGHT = 1080,
    TOT_WIDTH = 20000,
    GRAVITY = 0.5,
    MAX_PLATFORMS = 10,
    JUMP_HEIGHT = 15,
    PLAYER_BOUNCING = False,
    SCROLL_THRESHOLD = 400  # How far left/right of center player can be before we scroll the background
)

# Initializing
pygame.init()

# Create game window
screen = pygame.display.set_mode((upupup_world.SCREEN_WIDTH, upupup_world.SCREEN_HEIGHT))
pygame.display.set_caption("Up!Ùp!Up!")

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

# Load images
bg_image = pygame.transform.scale(pygame.image.load('assets/bg - wide.png').convert_alpha(), (9000, 1080))
tiled_platform_image = pygame.image.load('assets/wood_box.png').convert_alpha()

# Create static items
items_sprite_sheet = SpriteSheet(pygame.image.load('assets/gems.png').convert_alpha(), 125,125, BLACK, 2)
items_sprites = StaticImage(items_sprite_sheet, 2, 2)

# Create item animatios
flag_sprite_sheet = SpriteSheet(pygame.image.load('assets/flag.png').convert_alpha(), 103,135, BLACK, 1)
flag_amim = Animation(flag_sprite_sheet, row=0, frames=7 , speed=100)

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
    screen.blit(bg_image, (0 + bg_scroll, 0))
    screen.blit(bg_image, (-upupup_world.SCREEN_WIDTH + bg_scroll, 0))

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

# Fuintion to add platforms
def add_platforms(platform_list):
    # Sprite group for platforms
    platform_group = pygame.sprite.Group()

    # Create the starting platform
    platform = TiledPlatform((upupup_world.SCREEN_WIDTH // 2) - 200 / 2, upupup_world.SCREEN_HEIGHT - 50, tiled_platform_image, 10)
    platform_group.add(platform)

    # generate platforms TODO: FIX
    for p in platform_list:
        platform = TiledPlatform(p[0], p[1], tiled_platform_image, p[2])
        platform_group.add(platform)
    
    return platform_group

def add_monsters(monster_list):
    # Monster instances (for loop later)
    minotaur_group = pygame.sprite.Group()
    for m in monster_list:
        if m[2] == 'm':  # minotaur
            minotaur_group.add(Monster('Minotaur', upupup_world, m[0], m[1], screen, minotaur_anim_walk, minotaur_anim_attack, move_pattern=m[3]))
    return minotaur_group


def add_items(items_list, tiled_items_image):
    # Items in the game world [x, y, type, behaviour_num]
    items_group = pygame.sprite.Group()
    items_rect_group = []  # list of rectangles for collision detection
    game_sprite_list = []  # list of all the game item sprites (not sprite group, just plain list)

    for i in items_list:
        if i[2] == 'diamond':
            item_image = items_sprites.image(3)  # 3 is diamond
        elif i[2] == 'ruby':
            item_image = items_sprites.image(2)  # 2 is ruby
            
        game_sprite = GameItem(i[0], i[1], item_image)
        items_group.add(game_sprite)
        game_sprite_list.append(game_sprite)
        items_rect_group.append(game_sprite.rect)
                  
    return items_group, items_rect_group, game_sprite_list



"""
Defining instances
"""
# Player instance
player = Player(upupup_world.SCREEN_WIDTH // 2, upupup_world.SCREEN_HEIGHT -150 , upupup_world, screen, player_anim_walk, player_anim_attack, player_anim_death)

# Platforms
platform_group = add_platforms(platform_list)

# Monsters
monster_group = add_monsters(monster_list)

# Items
tiled_items_image = pygame.image.load('assets/gems.png').convert_alpha()

(items_group, items_rect_group, game_sprite_list) = add_items(items_list, tiled_items_image)

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
        scroll, score_add = player.move(platform_group)
        player_state.score += score_add
        for m in monster_group:
            m.move(platform_group)

        # draw background
        bg_scroll += scroll
        if bg_scroll >= upupup_world.SCREEN_WIDTH:
            bg_scroll = 0
        draw_bg(bg_scroll)

        #player_anim_walk.show(10,10)
  
        # draw temporary scroll threshold
        #pygame.draw.line(screen, WHITE, (upupup_world.SCROLL_THRESHOLD, 0), (upupup_world.SCROLL_THRESHOLD, SCREEN_HEIGHT)

        # update platforms
        platform_group.update(scroll)
        items_group.update(scroll)
        monster_group.update(scroll)

        # draw sprites
        platform_group.draw(screen)
        items_group.draw(screen)
        player.draw()

        # draw monsters
        for m in monster_group:
            m.draw()

        # draw panel
        draw_panel()

        ###############################################
        #flag_amim.show_anim(screen, scale_override=2)
        #player_anim_death.show_anim(screen)
        #player_anim_attack.show_anim(screen)
        
        screen.blit( flag_amim.image(), (400, 70))
        flag_amim.active = True


        ########################


        # check game over from falling
        if player.rect.top > upupup_world.SCREEN_HEIGHT:
            game_over = True
            player.dead = True
            print('!!!GAME OVER!!!')  # DEBUG


        # If player has been hit and is dying, we skip checking for more hits
        if player.dying:
            game_over = player.check_game_over()  # if we're done dying, we're dead
            if game_over:
                print('waiting')
                pygame.time.delay(3000)  # we wait a bit to let the death sink in before going to GAME OVER screen
            next

        # Check if player is finding any items
        item_collision = player.rect.collidelist(items_rect_group)
        if item_collision != -1:  # We hit something
            if  items_list[item_collision][2] == 'diamond':
                player_state.score += 500 
            elif items_list[item_collision][2] == 'ruby':
                player_state.score += 300
            else:
                print(f'ERROR: unknown item "{items_list[item_collision][2]}"')

            items_rect_group[item_collision] = pygame.Rect(0, 0, 0, 0)  # Replacing rectange with empty one to avoid collision detection
            game_sprite_list[item_collision].kill()  # remove sprite from sprite list


        # TODO: we need a mechanism to track monsters when off-screen. They should be persistent, but also not need collision detection etc. 
        for mob in monster_group:
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
        if fade_counter < upupup_world.SCREEN_WIDTH / 2:
            fade_counter += 15
            pygame.draw.rect(screen, DARKGRAY, (0,0, fade_counter, upupup_world.SCREEN_HEIGHT))
            pygame.draw.rect(screen, DARKGRAY, (upupup_world.SCREEN_WIDTH - fade_counter, 0, upupup_world.SCREEN_WIDTH, upupup_world.SCREEN_HEIGHT))

        else:       
            draw_text('GAME OVER', font_big, WHITE, (upupup_world.SCREEN_WIDTH/2)-130,300)
            draw_text('SCORE: ' + str(player_state.score), font_big, WHITE, (upupup_world.SCREEN_WIDTH/2)-100, 400)
            if player_state.score > high_score:
                    high_score = player_state.score
                    draw_text('NEW HIGH SCORE: ' + str(high_score), font_big, WHITE, (upupup_world.SCREEN_WIDTH/2)-180, 500)
            else:
                draw_text('HIGH SCORE: ' + str(high_score), font_big, WHITE, (upupup_world.SCREEN_WIDTH/2)-150, 500)
            draw_text('Press space to play again', font_big, WHITE, (upupup_world.SCREEN_WIDTH/2)-250, 600)
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
                player.rect.center = (upupup_world.SCREEN_WIDTH // 2, upupup_world.SCREEN_HEIGHT - 150)
                # Reset platforms
                platform_group.empty()
                # Create the starting platform
                platform_group = add_platforms(platform_list)

                fade_counter = 0
                # Add monsters
                minotaur = []
                monster_group = add_monsters(monster_list)


    # The main even handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Update display window
    pygame.display.update()

pygame.quit()