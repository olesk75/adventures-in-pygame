import pygame
import pickle

from game_world import GameWorld, GameData, GamePanel
from player import Player
from monsters import Monster, Projectile, Spell


# Flags for debug functionality
DEBUG_BOXES = True


# Game variables in a named tuple (new in Python 3.6) - we pass this to instances who need it
phflorg_data = GameData(
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
)

# Initializing
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()
pygame.init()

# Create game window
screen = pygame.display.set_mode((phflorg_data.SCREEN_WIDTH, phflorg_data.SCREEN_HEIGHT))
pygame.display.set_caption("Phflorg the Destroyer")

from animation_data import animations  # late import as we need display to be active for convert() 


# Set frame rate
clock = pygame.time.Clock() 
FPS = 30

# Player state
score = 0

# Game state variables
scroll = 0
bg_scroll = 0
player_dying = False
game_over = False
wait_counter = FPS * 2  # after death, before we fade out
fade_counter = 0

# State constants
WALKING = 1
ATTACKING = 2
CASTING = 3
DYING = 4
DEAD = 5

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
pine1_img = pygame.image.load('assets/backgrounds/day1_pine1.png').convert_alpha()
pine2_img = pygame.image.load('assets/backgrounds/day1_pine2.png').convert_alpha()
mountain_img = pygame.image.load('assets/backgrounds/day1_mountain.png').convert_alpha()
sky_img = pygame.image.load('assets/backgrounds/day1_sky_cloud.png').convert_alpha()

level = 1  # TODO: placeholder

p_w = GameWorld(phflorg_data)  # Loading all tiles in the world, less background and player (phflorg_world = p_w)
p_w.load(f'level{level}_data.csv')



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

# TODO: move this over to standard sprite group
def load_monsters(phflorg_worldmonster_import_list) -> list:
    print(phflorg_worldmonster_import_list)
    monsters_sprite_group = pygame.sprite.Group()
    for mob in phflorg_worldmonster_import_list:
        if mob['monster'] == 'minotaur':
            monsters_sprite_group.add(Monster(mob['x'], mob['y'], animations['minotaur']['walk'], animations['minotaur']['attack'], mob['ai']))
        if mob['monster'] == 'ogre-archer':
            monsters_sprite_group.add(Monster(mob['x'], mob['y'], animations['ogre-archer']['walk'], animations['ogre-archer']['attack'], mob['ai']))
        if mob['monster'] == 'skeleton-boss':
            monsters_sprite_group.add(Monster(mob['x'], mob['y'], animations['skeleton-boss']['walk'], animations['skeleton-boss']['attack'], mob['ai'], cast_anim=animations['skeleton-boss']['cast']))
    return monsters_sprite_group

"""
Defining instances
"""
# Player instance
player = Player(phflorg_data.SCREEN_WIDTH // 2, phflorg_data.SCREEN_HEIGHT -170 , phflorg_data, p_w, \
    animations['player']['walk'], animations['player']['attack'], animations['player']['death'], player_sound_effects)

# Monsters
monsters_sprite_group = load_monsters(p_w.monster_import_list)

# Projectiles 
projectile_group =  pygame.sprite.Group()
last_arrow = 0

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
        [sprite.update(scroll) for sprite in p_w.anim_objects_sprite_list]
        p_w.platforms_sprite_group.update(scroll)
        p_w.pickups_sprite_group.update(scroll)
        p_w.decor_sprite_group.update(scroll)
        projectile_group.update(scroll, p_w.platforms_sprite_group)
        #[sprite.update(scroll, p_w.platforms_sprite_group) for sprite in p_w.anim_spells_sprite_list]
        p_w.anim_spells_sprite_group.update(scroll)
        player.update()


        # draw background
        bg_scroll += scroll
        draw_bg(bg_scroll)

        # Draw all sprites, monsters and player

        [sprite.draw(screen) for sprite in p_w.anim_objects_sprite_list]
        p_w.platforms_sprite_group.draw(screen)
        p_w.pickups_sprite_group.draw(screen)
        p_w.decor_sprite_group.draw(screen)
        projectile_group.draw(screen)
        #[sprite.draw(screen) for sprite in p_w.anim_spells_sprite_list]
        p_w.anim_spells_sprite_group.draw(screen)

        player.draw()

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
        if player.state == DYING:
            game_over = player.check_game_over()  # if we're done dying, we're dead


        for mob in monsters_sprite_group:
            mob.walk_anim.active = True
            mob.update(scroll, p_w.platforms_sprite_group, player)

            if not mob.dead:
                if DEBUG_BOXES:  pygame.draw.rect(screen, (0,0,255), mob.rect_detect, 2 )  # DEBUG: to see hitbox for detection (blue)
                now = pygame.time.get_ticks()
                
                # Check if mob has triggered spells somewhere, if so, add them and empty list
                if mob.cast_anim_list:
                    for spell in mob.cast_anim_list:
                       if spell[0] == 'fire':
                            print('FIRE!')
                            x, y = spell[1:3]
                            animation = animations['fire']['fire-once']
                            p_w.anim_spells_sprite_group.add(Spell(x,y, animation, False, scale=1))
                            # TODO: fix! Fails while our custom methods for drawing fails?

                    mob.cast_anim_list = []

                # Mob detecting player and starting attack...
                if pygame.Rect.colliderect(player.rect, mob.rect_detect):
                    # attack_start_time = mob.last_attack + mob.data.attack_delay
                    # if now > attack_start_time:  # ...if enough time has passed
                    mob.attack_start()
                    if DEBUG_BOXES: pygame.draw.rect(screen, (255,0,0), mob.rect_attack, 2 )  # DEBUG: to see hitbox for detection (red)
                    
                else:  # Mob not detecting player
                    if mob.state == ATTACKING:
                        mob.attack_stop()  # if we move out of range, the mob will stop attacking
                
                # Mob attack: trigger attack if a) collision with mob, b) mob is in attack mode and c) mob is not already dead
                if pygame.Rect.colliderect(player.rect, mob.rect_attack) and mob.state == ATTACKING and not mob.dead:
                    if mob.data.attack_instant_damage:  # typically melee
                        player.hit(mob.data.attack_damage, mob.turned)
                        
                    elif now - last_arrow > mob.data.attack_delay:  # typically mob launching projectile
                        arrow = Projectile(mob.hitbox.centerx, mob.hitbox.centery, arrow_img, turned = mob.turned, scale = 2)

                        # WAIT UNTIL END OF ATTACK ANIMATION
                        if mob.attack_anim.anim_counter == 10:
                            projectile_group.add(arrow)
                            last_arrow = now

                # Mob collision: trigger player hit if a) collision with mob, b) mob is not already dead and c) player is not already dying
                if pygame.Rect.colliderect(player.rect, mob.hitbox) and not mob.dead and player.state != DYING:
                    player.hit(500, mob.turned)

                # Projectile collision: trigger player dying if a) collision with projectile and b) player is not already dying
                for projectile in projectile_group:
                    # Collision with player
                    if pygame.Rect.colliderect(player.rect, projectile) and player.state != DYING:
                        player.hit(100, projectile.turned)
                        projectile.kill()

                # If player is attacking
                if player.state == ATTACKING:
                    # Check if mob hit
                    if pygame.Rect.colliderect(player.attack_rect, mob.hitbox): 
                        mob.vel_y = -5
                        mob.data.direction = -player.turned
                        score += 100
                        mob.dead = True  # we run through the death anim sequence
                    # Check if projectile hit
                    for projectile in projectile_group:
                        if pygame.Rect.colliderect(player.attack_rect, projectile) and player.state != DYING:
                            projectile.kill()


            """ EVENTS PROCESSING ------------------------------------------------------------------------------------------- """
            if player.state not in (DYING, DEAD):
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            exit(0)
                        if event.key == pygame.K_LEFT:
                            player.walking = -1  # left
                            player.state = WALKING
                            if player.on_ground == True:
                                player.animation.active = True
                            
                        if event.key == pygame.K_RIGHT: 
                            player.walking = 1  # right
                            player.state = WALKING
                            if player.on_ground == True:
                                player.animation.active = True

                        if event.key == pygame.K_UP:  # jump!
                            if player.on_ground:
                                player.vel_y = - player.world_data.JUMP_HEIGHT
                                player.animation.active = False
                                player.state = WALKING
                                player.on_ground = False
                                player.fx_jump.play()

                        if event.key == pygame.K_SPACE:  # attack!        
                            player.state = ATTACKING
                            if not player.fx_attack_channel.get_busy():  # playing sound if not all channels busy
                                player.fx_attack_channel.play(player.fx_attack)

                    if event.type == pygame.KEYUP:  # mostly to handle repetition of left and right
                        if event.key == pygame.K_LEFT and player.walking == -1:
                            player.walking = False
                        
                        if event.key == pygame.K_RIGHT and player.walking == 1:
                            player.walking = False
                            
        monsters_sprite_group.draw(screen)  # draw them all
        
        
        
    else:
        """ --- GAME OVER ----"""
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
                player = Player(phflorg_data.SCREEN_WIDTH // 2, phflorg_data.SCREEN_HEIGHT -170 , phflorg_data, phflorg_world, \
                     animations['player']['walk'], animations['player']['attack'], animations['player']['death'], player_sound_effects)

                score = 0
                scroll = 0
                bg_scroll = 0

                p_w.load(f'level{level}_data.csv')

                fade_counter = 0
                wait_counter = 0
                # Add monsters
                monster_list = load_monsters(p_w.monster_import_list)


    # The main even handler
    # for event in pygame.event.get():
    #     scroll, score_add = player.move()
    #     score += score_add
    #     if event.type == pygame.QUIT:
    #         run = False

    # Update display window
    pygame.display.update()

pygame.quit()