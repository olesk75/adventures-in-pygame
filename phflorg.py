import pygame
import random
import pickle

from game_world import GameWorld, WorldData, GamePanel
from animation import Animation
from spritesheet import SpriteSheet
from player import Player
from monsters import Monster, Projectile


# Flags for debug functionality
DEBUG_BOXES = False


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
    TILE_TYPES = 18,
    ANIMATION_TYPES = 3,
    OBJECT_TYPES = 9,
    ANIMATIONS_DICT = {}
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
wait_counter = FPS * 2  # after death, before we fade out
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
attack_fx = pygame.mixer.Sound('assets/sound/Hit/OGG/Hit 2 - Sound effects Pack 2.ogg')
jump_fx = pygame.mixer.Sound('assets/sound/Jump/OGG/Jump 5 - Sound effects Pack 2.ogg')
death_fx = pygame.mixer.Sound('assets/sound/Lose/OGG/Lose 7 - Sound effects Pack 2.ogg')
hit_fx = pygame.mixer.Sound('assets/sound/Laser-weapon/OGG/Laser-weapon 8 - Sound effects Pack 2.ogg')
player_sound_effects = [attack_fx, jump_fx, death_fx, hit_fx]

# Load audio for world
item_pickup_fx = pygame.mixer.Sound('assets/sound/Power-up/OGG/Powerup 7 - Sound effects Pack 2.ogg')

# load background images
pine1_img = pygame.image.load('assets/pine1.png').convert_alpha()
pine2_img = pygame.image.load('assets/pine2.png').convert_alpha()
mountain_img = pygame.image.load('assets/mountain.png').convert_alpha()
sky_img = pygame.image.load('assets/sky_cloud.png').convert_alpha()

# load animation objects
fire_start = pygame.image.load('assets/objects/fire/burning_start_1.png').convert_alpha()
fire_loop = pygame.image.load('assets/objects/fire/burning_loop_1.png').convert_alpha()
fire_end = pygame.image.load('assets/objects/fire/burning_end_1.png').convert_alpha()
fire = pygame.Surface((fire_start.get_width() + fire_loop.get_width() + fire_end.get_width(),fire_start.get_height())).convert_alpha()

# Adding the three fire sheets together into one sprite sheet
fire.blit(fire_start, (0, 0))
fire.blit(fire_loop, (fire_start.get_width(), 0))
fire.blit(fire_end, (fire_loop.get_width() + fire_start.get_width(), 0))
fire_ss = SpriteSheet(fire.convert_alpha(), 24,32, BLACK, 2)
fire_anim = Animation(fire_ss, row=0, frames=17, speed=100)
phflorg_data.ANIMATIONS_DICT['fire'] = fire_anim  # must be added before we load the world


level = 1  # TODO: placeholder

phflorg_world = GameWorld(phflorg_data)  # Loading all tiles in the world, less background and player
phflorg_world.load(f'level{level}_data.csv')

# Create player animations
p_sprite_sheet = SpriteSheet(pygame.image.load('assets/character-sprites2.png').convert_alpha(), 64, 64, BLACK, 2)
p_sprite_sheet_oversize = SpriteSheet(pygame.image.load('assets/character-sprites2.png').convert_alpha(), 64*3, 64*3, BLACK, 2)
player_anim_walk = Animation(p_sprite_sheet, row=11, frames=9, speed=75)
player_anim_attack = Animation(p_sprite_sheet_oversize, row=10, frames=6, speed=30)
player_anim_death = Animation(p_sprite_sheet, row=20, frames=6, speed=800)

# Create monster animations
minotaur_ss = SpriteSheet(pygame.image.load('assets/minotaur-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
minotaur_anim_walk = Animation(minotaur_ss, row=11, frames=9, speed=50)
minotaur_anim_attack = Animation(minotaur_ss, row=7, frames=8, speed=75)
ogre_archer_ss = SpriteSheet(pygame.image.load('assets/ogre-archer-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
ogre_anim_walk = Animation(ogre_archer_ss, row=11, frames=9, speed=50)
ogre_anim_attack = Animation(ogre_archer_ss, row=19, frames=13, speed=100)

# Create boss animations
skeleton_boss_ss = SpriteSheet(pygame.image.load('assets/skeleton-boss-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
skeleton_boss_oversize_ss = SpriteSheet(pygame.image.load('assets/skeleton-boss-sprites.png').convert_alpha(), 64*3, 64*3, BLACK, 2)
skeleton_boss_anim_walk = Animation(skeleton_boss_ss, row=11, frames=9, speed=50)
skeleton_boss_anim_attack = Animation(skeleton_boss_oversize_ss, row=10, frames=6, speed=75)
skeleton_boss_anim_death = Animation(skeleton_boss_ss, row=20, frames=6, speed=75)

# load projectiles (no animation variety)
arrow_img = pygame.image.load('assets/arrow.png').convert_alpha()


# Function for text output
def draw_text(text, font, text_col, x, y)-> None:
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function for drawing the background
def draw_bg(bg_scroll) -> None:
    SKY_BLUE = (130, 181, 210)
    screen.fill(SKY_BLUE)
    width = sky_img.get_width()

    for x in range(phflorg_data.LEVEL_WIDTH+ 300):
        screen.blit(sky_img, ((x * width) + bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) + bg_scroll * 0.6, phflorg_data.SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) + bg_scroll * 0.7, phflorg_data.SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) + bg_scroll * 0.8, phflorg_data.SCREEN_HEIGHT - pine2_img.get_height()))


# Function to load hish score from file
def load_high_score() -> int:
    with open('highscore.dat', 'rb') as high_score_file:
        try:
            high_score = pickle.load(high_score_file)
        except EOFError:  # In case file does not exist with valid high score already
            return(0)
    
    #print(f'Read high score from file: {high_score}')
    return(high_score)

# Function to save score to file
def save_high_score(high_score) -> None:
    with open('highscore.dat', 'wb') as save_file:
        pickle.dump(high_score, save_file)    


def load_monsters(phflorg_worldmonster_import_list) -> list:
    monster_list= []
    for mob in phflorg_worldmonster_import_list:
        if mob['monster'] == 'minotaur':
            monster_list.append(Monster(mob['x'], mob['y'], minotaur_anim_walk, minotaur_anim_attack, mob['ai']))
        if mob['monster'] == 'ogre-archer':
            monster_list.append(Monster(mob['x'], mob['y'], ogre_anim_walk, ogre_anim_attack, mob['ai']))
        if mob['monster'] == 'skeleton-boss':
            monster_list.append(Monster(mob['x'], mob['y'], skeleton_boss_anim_walk, skeleton_boss_anim_attack, mob['ai']))
    return monster_list


"""
Defining instances
"""
# Player instance
player = Player(phflorg_data.SCREEN_WIDTH // 2, phflorg_data.SCREEN_HEIGHT -150 , phflorg_data, phflorg_world, \
    player_anim_walk, player_anim_attack, player_anim_death, player_sound_effects)

# Monsters
monster_list = load_monsters(phflorg_world.monster_import_list)

# Projectiles 
projectile_group =  pygame.sprite.Group()
last_arrow = 0

# projectile_group.add(Projectile(800, 800, arrow_img))  # add arrow
# projectile_group.add(Projectile(900, 900, arrow_img))  # add arrow
# projectile_group.add(Projectile(1000, 1000, arrow_img))  # add arrow


# Load previous high score
high_score = load_high_score()

panel = GamePanel(screen, player)

"""
Main game loop
"""
run = True
while run:
    clock.tick(FPS)
    
    if not game_over:
        # check keypresses and update position (and get back scroll value if any)
        scroll, score_add = player.move()
        score += score_add

        # Update tiles and projectiles
        for sprite in phflorg_world.anim_objects_sprite_list:
            sprite.update(scroll)
        phflorg_world.platforms_sprite_group.update(scroll)
        phflorg_world.pickups_sprite_group.update(scroll)
        phflorg_world.decor_sprite_group.update(scroll)
        projectile_group.update(scroll, phflorg_world.platforms_sprite_group)

        # draw background
        bg_scroll += scroll
        draw_bg(bg_scroll)

        # Draw all sprites, monsters and player

        for sprite in phflorg_world.anim_objects_sprite_list:
            sprite.draw(screen)
        phflorg_world.platforms_sprite_group.draw(screen)
        phflorg_world.pickups_sprite_group.draw(screen)
        phflorg_world.decor_sprite_group.draw(screen)
        projectile_group.draw(screen)
      

        player.draw(screen)

        # Draw panel
        panel.draw()

        # Check animation imports
        # skeleton_boss_anim_attack._show_anim(screen)
        #skeleton_boss_anim_death._show_anim(screen) 

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
            mob.update(scroll, phflorg_world.platforms_sprite_group, player)
            mob.draw(screen)

            if not mob.dead:
                if DEBUG_BOXES:  pygame.draw.rect(screen, (0,0,255), mob.rect_detect, 2 )  # DEBUG: to see hitbox for detection (blue)
                now = pygame.time.get_ticks()
                
                # Mob detecting player and starting attack...
                if pygame.Rect.colliderect(player.rect, mob.rect_detect):
                    # attack_start_time = mob.last_attack + mob.data.attack_delay
                    # if now > attack_start_time:  # ...if enough time has passed
                    mob.attack_start()
                    if DEBUG_BOXES: pygame.draw.rect(screen, (255,0,0), mob.rect_attack, 2 )  # DEBUG: to see hitbox for detection (red)
                    
                else:  # Mob not detecting player
                    if mob.attacking:
                        mob.attack_stop()  # if we move out of range, the mob will stop attacking
                
                # Mob attack: trigger attack if a) collision with mob, b) mob is in attack mode and c) mob is not already dead
                if pygame.Rect.colliderect(player.rect, mob.rect_attack) and mob.attacking and not mob.dead:
                    if mob.data.attack_instant_damage:  # typically melee
                        player.hit(mob.data.attack_damage, mob.flip)
                        
                    elif now - last_arrow > mob.data.attack_delay:  # typically mob launching projectile
                        arrow = Projectile(mob.rect.centerx, mob.rect.centery, arrow_img, flip = mob.flip, scale = 2)

                        # WAIT UNTIL END OF ATTACK ANIMATION
                        if mob.attack_anim.anim_counter == 10:
                            projectile_group.add(arrow)
                            last_arrow = now


                # Mob collision: trigger player hit if a) collision with mob, b) mob is not already dead and c) player is not already dying
                if pygame.Rect.colliderect(player.rect, mob.rect) and not mob.dead and not player.dying:
                    player.hit(500, mob.flip)

                # Projectile collision: trigger player dying if a) collision with projectile and b) player is not already dying
                for projectile in projectile_group:
                    # Collision with player
                    if pygame.Rect.colliderect(player.rect, projectile) and not player.dying:
                        player.hit(100, projectile.flip)
                        projectile.kill()


                # If player is attacking
                if player.attacking:
                    # Check if mob hit
                    if pygame.Rect.colliderect(player.attack_rect, mob.rect): 
                        mob.vel_y = -5
                        mob.data.direction = -player.flip
                        score += 100
                        mob.dead = True  # we run through the death anim sequence
                    # Check if projectile hit
                    for projectile in projectile_group:
                        if pygame.Rect.colliderect(player.attack_rect, projectile) and not player.dying:
                            projectile.kill()
 

    else:  # Game over 
        if wait_counter:
            wait_counter -= 1
        elif fade_counter < phflorg_data.SCREEN_WIDTH / 2:
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
                player = Player(phflorg_data.SCREEN_WIDTH // 2, phflorg_data.SCREEN_HEIGHT -150 , phflorg_data, phflorg_world, \
                    player_anim_walk, player_anim_attack, player_anim_death, player_sound_effects)

                score = 0
                scroll = 0
                bg_scroll = 0
                
                # Reset player position
                
                #player.rect.center = (phflorg_data.SCREEN_WIDTH // 2, phflorg_data.SCREEN_HEIGHT - 150)
                phflorg_world.load(f'level{level}_data.csv')

                fade_counter = 0
                wait_counter = 0
                # Add monsters
                monster_list = load_monsters(phflorg_world.monster_import_list)


    # The main even handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Update display window
    pygame.display.update()

pygame.quit()