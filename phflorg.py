import pygame
import random
import pickle

from game_world import GameWorld, WorldData
from animation import Animation
from spritesheet import SpriteSheet
from player import Player
from monsters import Monster, Projectile


# Game variables in a named tuple (new in Python 3.6) - we pass this to instances who need it
phflorg_data = WorldData(
    SCREEN_WIDTH = 1920,
    SCREEN_HEIGHT = 1080,
    LEVEL_WIDTH = 4,
    GRAVITY = 0.5,
    MAX_PLATFORMS = 10,
    JUMP_HEIGHT = 15,
    PLAYER_BOUNCING = False,
    SCROLL_THRESHOLD = 400,  # How far left/right of center player can be before we scroll the background
    ROWS = 16,
    MAX_COLS = 150,
    TILE_SIZE = 1080 // 16,
    TILE_TYPES = 21,
    OBJECT_TYPES = 9
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
score = 0

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

# load background images
pine1_img = pygame.image.load('assets/pine1.png').convert_alpha()
pine2_img = pygame.image.load('assets/pine2.png').convert_alpha()
mountain_img = pygame.image.load('assets/mountain.png').convert_alpha()
sky_img = pygame.image.load('assets/sky_cloud.png').convert_alpha()


level = 1  # TODO: placeholder

phflorg_world = GameWorld(phflorg_data)  # Loading all tiles in the world, less background and player

(platforms_sprite_group, pickups_sprite_group, decor_sprite_group, monster_import_list) = phflorg_world.load(f'level{level}_data.csv')

# Create player animations
p_sprite_sheet = SpriteSheet(pygame.image.load('assets/character-sprites2.png').convert_alpha(), 64, 64, BLACK, 2)
p_sprite_sheet_oversize = SpriteSheet(pygame.image.load('assets/character-sprites2.png').convert_alpha(), 64*3, 64*3, BLACK, 2)
player_anim_walk = Animation(p_sprite_sheet, row=11, frames=9, speed=75)
player_anim_attack = Animation(p_sprite_sheet_oversize, row=10, frames=6, speed=100)
player_anim_death = Animation(p_sprite_sheet, row=20, frames=6, speed=500)

# Create monster animations
minotaur_ss = SpriteSheet(pygame.image.load('assets/minotaur-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
minotaur_anim_walk = Animation(minotaur_ss, row=11, frames=9, speed=50)
minotaur_anim_attack = Animation(minotaur_ss, row=7, frames=8, speed=50, attack_anim=True)
ogre_archer_ss = SpriteSheet(pygame.image.load('assets/ogre-archer-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
ogre_anim_walk = Animation(ogre_archer_ss, row=11, frames=9, speed=50)
ogre_anim_attack = Animation(ogre_archer_ss, row=19, frames=13, speed=100, attack_anim=True)

# load projectiles (no animation variety)
arrow_img = pygame.image.load('assets/arrow.png').convert_alpha()

# Function for text output
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Funtion to draw score and life panel
def draw_panel():
    draw_text(f'SCORE: {score}', font_small, WHITE, 0, 0)

# Function for drawing the background
def draw_bg(bg_scroll):
    SKY_BLUE = (130, 181, 210)
    screen.fill(SKY_BLUE)
    width = sky_img.get_width()

    for x in range(phflorg_data.LEVEL_WIDTH+ 300):
        screen.blit(sky_img, ((x * width) + bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) + bg_scroll * 0.6, phflorg_data.SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) + bg_scroll * 0.7, phflorg_data.SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) + bg_scroll * 0.8, phflorg_data.SCREEN_HEIGHT - pine2_img.get_height()))


# Function to load hish score from file
def load_high_score():
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


def load_monsters(monster_import_list):
    for mob in monster_import_list:
        if mob['monster'] == 'minotaur':
            monster_list.append(Monster(mob['x'], mob['y'], minotaur_anim_walk, minotaur_anim_attack, mob['ai']))
        if mob['monster'] == 'ogre-archer':
            monster_list.append(Monster(mob['x'], mob['y'], ogre_anim_walk, ogre_anim_attack, mob['ai']))
    return monster_list





"""
Defining instances
"""
# Player instance
player = Player(phflorg_data.SCREEN_WIDTH // 2, phflorg_data.SCREEN_HEIGHT -150 , phflorg_data, \
    player_anim_walk, player_anim_attack, player_anim_death, player_sound_effects)

# Monsters
monster_list= []
monster_list = load_monsters(monster_import_list)

# Projectiles 
projectile_group =  pygame.sprite.Group()
last_arrow = 0

# projectile_group.add(Projectile(800, 800, arrow_img))  # add arrow
# projectile_group.add(Projectile(900, 900, arrow_img))  # add arrow
# projectile_group.add(Projectile(1000, 1000, arrow_img))  # add arrow


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
        score += score_add

        # Update tiles and projectiles
        platforms_sprite_group.update(scroll)
        pickups_sprite_group.update(scroll)
        decor_sprite_group.update(scroll)

        projectile_group.update(scroll, platforms_sprite_group)

        # draw background
        bg_scroll += scroll
        draw_bg(bg_scroll)

        # Draw all sprites, monsters and player
        platforms_sprite_group.draw(screen)
        pickups_sprite_group.draw(screen)
        decor_sprite_group.draw(screen)
        projectile_group.draw(screen)
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

    
        for mob in monster_list:
            mob.walk_anim.active = True
            mob.update(scroll, platforms_sprite_group)
            mob.draw(screen)

            if not mob.dead:
                pygame.draw.rect(screen, (0,0,255), mob.rect_detect, 2 )  # DEBUG: to see hitbox for detection (blue)
                now = pygame.time.get_ticks()
                
                # Mob detecting player and starting attack...
                if pygame.Rect.colliderect(player.rect, mob.rect_detect):
                    # attack_start_time = mob.last_attack + mob.ai.attack_delay
                    # if now > attack_start_time:  # ...if enough time has passed
                    mob.attack_start()
                    pygame.draw.rect(screen, (255,0,0), mob.rect_attack, 2 )  # DEBUG: to see hitbox for detection (red)
                    
                else:  # Mob not detecting player
                    mob.attack_stop()  # if we move out of range, the mob will stop attacking
                
                # Mob attack: trigger attack if a) collision with mob, b) mob is in attack mode and c) mob is not already dead
                if pygame.Rect.colliderect(player.rect, mob.rect_attack) and mob.attacking and not mob.dead:
                    if mob.ai.attack_instadeath:  # typically melee
                        player.die()
                        #mob.attack_stop()
                    elif now - last_arrow > mob.ai.attack_delay:  # typically mob launching projectile
                        arrow = Projectile(mob.rect.centerx, mob.rect.centery, arrow_img)

                        #arrow.direction = mob.direction
                        arrow.flip = mob.flip
                        # WAIT UNTIL END OF ATTACK ANIMATION
                        if mob.attack_anim.anim_counter == 10:
                            projectile_group.add(arrow)
                            last_arrow = now


                # Mob collision: trigger player dying if a) collision with mob, b) mob is not already dead and c) player is not already dying
                if pygame.Rect.colliderect(player.rect, mob.rect) and not mob.dead and not player.dying:
                    player.die()

                # Projectile collision: trigger player dying if a) collision with projectile and b) player is not already dying
                for projectile in projectile_group:
                    if pygame.Rect.colliderect(player.rect, projectile) and not player.dying:
                        player.die()
                        projectile.kill()

                # If player is attacking
                if player.attacking:
                    # Check if mob hit
                    if pygame.Rect.colliderect(player.attack_rect, mob.rect): 
                        mob.vel_y = -5
                        mob.ai.direction = -player.flip
                        score += 100
                        mob.dead = True  # we run through the death anim sequence
                    # Check if projectile hit
                    for projectile in projectile_group:
                        if pygame.Rect.colliderect(player.attack_rect, projectile) and not player.dying:
                            projectile.kill()
                    


                        

    else:  # Game over 
        if fade_counter < phflorg_data.SCREEN_WIDTH / 2:
            fade_counter += 15
            pygame.draw.rect(screen, DARKGRAY, (0,0, fade_counter, phflorg_data.SCREEN_HEIGHT))
            pygame.draw.rect(screen, DARKGRAY, (phflorg_data.SCREEN_WIDTH - fade_counter, 0, phflorg_data.SCREEN_WIDTH, phflorg_data.SCREEN_HEIGHT))

        else:       
            draw_text('GAME OVER', font_big, WHITE, (phflorg_data.SCREEN_WIDTH/2)-130,300)
            draw_text('SCORE: ' + str(score), font_big, WHITE, (phflorg_data.SCREEN_WIDTH/2)-100, 400)
            if score > high_score:
                    high_score = score
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
                #print(f'wrote {score}')  # DEBUG

                # Reset all variables
                game_over = False
                player.alive = True
                player.dying = False
                player.dead = False
                player.attacking = False

                score = 0
                scroll = 0
                bg_scroll = 0
                
                # Reset player position
                player.rect.center = (phflorg_data.SCREEN_WIDTH // 2, phflorg_data.SCREEN_HEIGHT - 150)
                # Reset platforms
                #platform_group.empty()
                # Create the starting platform
                #platform_group = add_platforms(platform_list)

                fade_counter = 0
                # Add monsters

                monster_list = []
                monster_list = load_monsters(monster_import_list)


    # The main even handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Update display window
    pygame.display.update()

pygame.quit()