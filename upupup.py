import pygame
import random
import pickle

from game_world import FloatPlatform as Platform  # "Platform" clashes with built-in type
from game_world import TiledPlatform, WorldData, PlatformLocations, GameItems
from animation import Animation
from spritesheet import SpriteSheet
from player import Player, PlayerData
from monsters import Monster

# Initializing
pygame.init()

# Patforms list TODO: FIX
# 
platform_list = [  # [x, y, width]
    [100,350,13],
    [200,500,14],
    [300,200,10],
    [800,700,20],
    [1500,600,15],

    [1300,1000,5],
    [1400,400,20],
    [1500,900,10],
    [2300,700,20],
    [2600,400,15],
]

monster_list = [  # [x, y, type, behaviour_num]
    [320, 400, 'm', 1],
    [850, 500, 'm', 1],
]

items_list = [  # [x, y, type, behaviour_num]
    [320, 400, 'diamond', 1],
    [120, 100, 'diamond', 1],
    [520, 500, 'diamond', 1],
    [620, 600, 'diamond', 1],

]


# Main window constants - 1080p for now
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Up!Ùp!Up!")

# Set frame rate
clock = pygame.time.Clock() 
FPS = 60

# Game variables in a named tuple (new in Python 3.6) - we pass this to instances who need it
upupup_world = WorldData(
    TOT_WIDTH = 20000,
    GRAVITY = 0.5,
    MAX_PLATFORMS = 10,
    JUMP_HEIGHT = 15,
    PLAYER_BOUNCING = False,
    SCROLL_THRESHOLD = SCREEN_WIDTH * 0.8,  # 400 in vertical scroll 
)
 
# Player state
player_state = PlayerData()

# Game state variables
scroll = 0
bg_scroll = 0
player_dying = False
game_over = False
fade_counter = 0

# Define colors
WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
RED   = (255,   0,   0)

# Define fonts
font_small = pygame.font.SysFont('Lucida Sans', 40)
font_big = pygame.font.SysFont('Lucida Sans', 60)

# Load images
bg_image = pygame.transform.scale(pygame.image.load('assets/bg - wide.png').convert_alpha(), (9000, 1080))
platform_image = pygame.image.load('assets/wood.png').convert_alpha()  # Scaled in each instance
tiled_platform_image = pygame.image.load('assets/wood_box.png').convert_alpha()

# Create items
items_sprite_sheet = SpriteSheet(pygame.image.load('assets/gems.png').convert_alpha(), 125,125, BLACK, 2)
items_anim = Animation(items_sprite_sheet, row=2, frames=2, speed=100)

# Create player animations
p_sprite_sheet = SpriteSheet(pygame.image.load('assets/character-sprites2.png').convert_alpha(), 64, 64, BLACK, 2)
p_sprite_sheet_oversize = SpriteSheet(pygame.image.load('assets/character-sprites2.png').convert_alpha(), 64*3, 64*3, BLACK, 2)
player_anim_walk = Animation(p_sprite_sheet, row=11, frames=10, speed=100)
player_anim_attack = Animation(p_sprite_sheet_oversize, row=10, frames=9, speed=50)
player_anim_death = Animation(p_sprite_sheet, row=20, frames=10, speed=500)


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
    screen.blit(bg_image, (-SCREEN_WIDTH + bg_scroll, 0))

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
    platform = TiledPlatform((SCREEN_WIDTH // 2) - 200 / 2, SCREEN_HEIGHT - 50, tiled_platform_image, 10)
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
    for i in items_list:
        if i[2] == 'diamond':
            items_group.add(GameItems(i[0], i[1], tiled_items_image))
    return items_group




"""
Defining instances
"""
# Player instance
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT -150 , upupup_world, screen, player_anim_walk, player_anim_attack, player_anim_death)

# Platforms
platform_group = add_platforms(platform_list)

# Monsters
monster_group = add_monsters(monster_list)

# Items
tiled_items_image = pygame.image.load('assets/gems.png').convert_alpha()

items_group = add_items(items_list, tiled_items_image)


# Load previous high score
high_score = load_high_score()



"""
Main game loop
"""
run = True
while run:
    clock.tick(FPS)
    
    if game_over == False:
        # check keypresses and update position (and get back scroll value if any)
        scroll, score_add = player.move(platform_group)
        player_state.score += score_add
        for m in monster_group:
            m.move(platform_group)

        # draw background
        bg_scroll += scroll
        if bg_scroll >= SCREEN_WIDTH:
            bg_scroll = 0
        draw_bg(bg_scroll)

        # Test sprites
        #screen.blit(items_sprite_sheet.image, (0,0))  # DEBUG: Show entire sprite sheet
        
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
        #minotaur_group.draw(screen)
        for m in monster_group:
            m.draw()

        # draw panel
        draw_panel()

        # check game over from falling
        if player.rect.top > SCREEN_HEIGHT:
            game_over = True
            print('!!!GAME OVER!!!')  # DEBUG

        # check interactions with monsters
        if player_dying == False:
            for mob in monster_group:
                # Can the monster detect the player
                if pygame.Rect.colliderect(player.rect, mob.get_detect()):
                    mob.attacking = True
                    #print(f'Monster {mob.name} attacking!')  # DEBUG
                else:
                    mob.attacking = False
                # Have we walked into a monster? --> DEATH
                if pygame.Rect.colliderect(player.rect, mob.rect) and mob.attacking and not mob.dead:  # Collision detection (we ignore player damage after mob is dead)
                    player_dying = True  # we start the death sequence
                    #print('Collision detected - player dying')  # DEBUG
                # Are we currently attacking? --> Check if attack connects
                if player.attacking:
                    attack_rect = player.get_attack_rect()
                    if pygame.Rect.colliderect(attack_rect, mob.rect):  # Collision detection
                        if not mob.dead:  # First time collision detected
                            mob.vel_y = -5
                            mob.direction  *= -1
                            player_state.score += 100
                        mob.dead = True
                        # On death - bounce backwards a bit
                        
                        
        else:
            game_over = player.die()
            #if game_over == True:
            #    pygame.time.delay(3000)
            


    else:  # Game over 
        if fade_counter < SCREEN_WIDTH / 2:
            fade_counter += 10
            pygame.draw.rect(screen, BLACK, (0,0, fade_counter, SCREEN_HEIGHT))
            pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        else:        
            

            draw_text('GAME OVER', font_big, WHITE, (SCREEN_WIDTH/2)-130,300)
            draw_text('SCORE: ' + str(player_state.score), font_big, WHITE, (SCREEN_WIDTH/2)-100, 400)
            if player_state.score > high_score:
                    high_score = player_state.score
                    draw_text('NEW HIGH SCORE: ' + str(high_score), font_big, WHITE, (SCREEN_WIDTH/2)-180, 500)
            else:
                draw_text('HIGH SCORE: ' + str(high_score), font_big, WHITE, (SCREEN_WIDTH/2)-150, 500)
            draw_text('Press space to play again', font_big, WHITE, (SCREEN_WIDTH/2)-250, 600)
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
                player_dying = False
                player.attacking = False

                player_state.score = 0
                scroll = 0
                
                # Reset player position
                player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
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