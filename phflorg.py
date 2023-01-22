import pygame

from game_world import GameWorld, GameData
from player import Player
from monsters import Monster, Projectile, Spell, Drop

from engine import draw_text, load_high_score, save_high_score, BubbleMessage, GamePanel


# Flags for debug functionality
DEBUG_BOXES = False

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
FPS = 60

# Game state variables
level = 1
max_level = 1
scroll = 0
bg_scroll = 0
player_dying = False
game_over = False
wait_counter = FPS * 2  # after death, before we fade out
fade_counter = 0
arrow_damage = 600

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
attack_fx = pygame.mixer.Sound('assets/sound/player/attack.wav')
jump_fx = pygame.mixer.Sound('assets/sound/Jump/OGG/Jump 5 - Sound effects Pack 2.ogg')
death_fx = pygame.mixer.Sound('assets/sound/Lose/OGG/Lose 7 - Sound effects Pack 2.ogg')
hit_fx = pygame.mixer.Sound('assets/sound/Laser-weapon/OGG/Laser-weapon 8 - Sound effects Pack 2.ogg')
player_sound_effects = [attack_fx, jump_fx, death_fx, hit_fx]

# Load audio for world
key_pickup_fx = pygame.mixer.Sound('assets/sound/objects/key_pickup.wav')
health_pickup_fx = pygame.mixer.Sound('assets/sound/objects/health_pickup.wav')

# load background images
pine1_img = pygame.image.load('assets/backgrounds/day1_pine1.png').convert_alpha()
pine2_img = pygame.image.load('assets/backgrounds/day1_pine2.png').convert_alpha()
mountain_img = pygame.image.load('assets/backgrounds/day1_mountain.png').convert_alpha()
sky_img = pygame.image.load('assets/backgrounds/day1_sky_cloud.png').convert_alpha()

p_w = GameWorld(phflorg_data)  # Loading all tiles in the world, less background and player (phflorg_world = p_w)
p_w.load(f'lvl/level{level}_data.csv')

# load projectiles (no animation variety)
arrow_img = pygame.image.load('assets/arrow.png').convert_alpha()

# load panel images 
key_img = pygame.image.load('assets/panel/key.png').convert_alpha()



# Function for drawing a parallax background
def draw_bg(bg_scroll) -> None:
    SKY_BLUE = (130, 181, 210)
    screen.fill(SKY_BLUE)
    width = sky_img.get_width()

    for x in range(phflorg_data.LEVEL_WIDTH+ 300):
        screen.blit(sky_img, ((x * width) + bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) + bg_scroll * 0.6, phflorg_data.SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) + bg_scroll * 0.7, phflorg_data.SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) + bg_scroll * 0.8, phflorg_data.SCREEN_HEIGHT - pine2_img.get_height()))


# TODO: get this to world loading module
def load_monsters(phflorg_worldmonster_import_list) -> pygame.sprite.Group():
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
Defining player and monster instances
"""
# Player instance
player = Player(phflorg_data.SCREEN_WIDTH // 2, phflorg_data.SCREEN_HEIGHT -170 , phflorg_data, p_w, \
    animations['player']['walk'], animations['player']['attack'], animations['player']['death'], player_sound_effects)

# Monsters
monsters_sprite_group = load_monsters(p_w.monster_import_list)

"""
Local sprite groups
"""
# Projectiles 
projectile_sprite_group =  pygame.sprite.Group()
last_arrow = 0  # timer to limit attack speed

# Item drops
drops_sprite_group = pygame.sprite.Group()

# Player inventory 


"""
High score, bubble messages and status panel
"""
high_score = load_high_score()
panel = GamePanel(screen, player)
bubble_list = []

"""
Main game loop
"""
run = True
while run:
    clock.tick(FPS)
    
    if not game_over:
        # check keypresses and update position (and get back scroll value if any)
        scroll = player.move()

        # Update tiles and projectiles
        p_w.anim_objects_sprite_group.update(scroll)
        p_w.platforms_sprite_group.update(scroll)
        p_w.pickups_sprite_group.update(scroll)
        p_w.trigger_anim_sprite_group.update(scroll)
        p_w.decor_sprite_group.update(scroll)
        p_w.hazards_sprite_group.update(scroll)
        p_w.anim_spells_sprite_group.update(scroll)
        drops_sprite_group.update(scroll)
        projectile_sprite_group.update(scroll, p_w.platforms_sprite_group)
        player.update()

        # Draw background
        bg_scroll += scroll
        draw_bg(bg_scroll)

        # Draw all sprite groups
        p_w.platforms_sprite_group.draw(screen)
        p_w.pickups_sprite_group.draw(screen)
        p_w.trigger_anim_sprite_group.draw(screen)
        p_w.decor_sprite_group.draw(screen)
        p_w.anim_objects_sprite_group.draw(screen)
        p_w.hazards_sprite_group.draw(screen)
        p_w.anim_spells_sprite_group.draw(screen)
        drops_sprite_group.draw(screen)
        projectile_sprite_group.draw(screen)
        player.draw()
        panel.draw()

        # Check animation imports
        # skeleton_boss_anim_attack _show_anim(screen)

        # check game over from falling
        if player.rect.top > phflorg_data.SCREEN_HEIGHT:
            game_over = True
            player.dead = True
            print('!!!GAME OVER!!!')  # DEBUG
 

        # If player has been hit and is dying, we skip checking for more hits
        if player.state == DYING:
            game_over = player.check_game_over()  # if we're done dying, we're dead

        """ We check if the player has touched any animated triggers """
        for t_anim_sprite in p_w.trigger_anim_sprite_group.sprites():
            if pygame.Rect.colliderect(player.rect, t_anim_sprite) and player.state != DYING:
                if any('key' in sublist for sublist in player.inventory):  # do we have key?
                    t_anim_sprite.animation.active = True
                    bubble_list.append(BubbleMessage(screen, 'Level complete! Congratualations!', player.rect.top, player.rect.left))
                    

                else:
                    player.hit(0, -1)
                    bubble_list.append(BubbleMessage(screen, 'Come back when you have a key!', player.rect.top, player.rect.left))
    

                
        """ We step through every single mob in the level """
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
                            x, y = spell[1:3]
                            p_w.anim_spells_sprite_group.add(Spell(x,y, animations['fire']['fire-spell'], False, scale=1))

                    mob.cast_anim_list = []

                # Mob detecting player and starting attack unless we're already in the process of casting (only bosses)
                if pygame.Rect.colliderect(player.rect, mob.rect_detect):
                    if mob.state == WALKING:
                        mob.state_change(ATTACKING)
                    if DEBUG_BOXES: pygame.draw.rect(screen, (255,0,0), mob.rect_attack, 2 )  # DEBUG: to see hitbox for detection (red)
                    
                else:  # Mob not detecting player
                    if mob.state == ATTACKING:
                        mob.state_change(WALKING)  # if we move out of range, the mob will stop attacking
                
                # Mob attack: trigger attack if a) collision with mob, b) mob is in attack mode and c) mob is not already dead
                if pygame.Rect.colliderect(player.rect, mob.rect_attack) and mob.state == ATTACKING and not mob.dead:
                    if mob.data.attack_instant_damage:  # typically melee
                        player.hit(mob.data.attack_damage, mob.turned)
                        
                    elif now - last_arrow > mob.data.attack_delay:  # typically mob launching projectile
                        arrow = Projectile(mob.hitbox.centerx, mob.hitbox.centery, arrow_img, turned = mob.turned, scale = 2)

                        # WAIT UNTIL END OF ATTACK ANIMATION
                        if mob.attack_anim.anim_counter == 10:
                            projectile_sprite_group.add(arrow)
                            last_arrow = now

                # Mob collision: trigger player hit if a) collision with mob, b) mob is not already dead and c) player is not already dying
                if pygame.Rect.colliderect(player.rect, mob.hitbox) and not mob.dead and player.state != DYING:
                    player.hit(500, mob.turned)

                # Projectile collision
                for projectile in projectile_sprite_group:
                    # Collision with player
                    if pygame.Rect.colliderect(player.rect, projectile) and player.state != DYING:
                        player.hit(arrow_damage, projectile.turned)
                        projectile.kill()
                
                # Spell collision
                for spell in p_w.anim_spells_sprite_group:
                    # Collision with player
                    if pygame.Rect.colliderect(player.rect, spell) and player.state != DYING:
                        player.take_damage(100, hits_per_second=2)

                # Hazards collision  TODO: change to group collision check
                for hazard in p_w.hazards_sprite_group:
                    # Collision with player
                    if pygame.Rect.colliderect(player.rect, hazard) and player.state != DYING:
                        player.take_damage(100, hits_per_second=10)

                # Drops pickup / collision
                for drop_item in drops_sprite_group.sprites():
                    if pygame.Rect.colliderect(player.rect, drop_item) and player.state != DYING:
                        if drop_item.drop_type == 'key':
                            player.inventory.append(('key', key_img))  # inventory of items and their animations
                            key_pickup_fx.play()            
                            drop_item.kill()
                        if drop_item.drop_type == 'health potion':
                            health_pickup_fx.play()()
                            player.health_current += 500
                            if player.health_current > player.health_max:
                                player.health_current = player.health_max


                # PLAYER ATTACK
                if player.state == ATTACKING:
                    # Check if mob hit
                    if pygame.Rect.colliderect(player.attack_rect, mob.hitbox): 
                        mob.state_change(DYING)
                        mob.data.direction = -player.turned
                        player.score += 100
                        """ Adding drops from player death """
                        # skeleton-boss is a key carrier
                        if mob.data.monster == 'skeleton-boss':
                        # if mob.data.monster == 'ogre-archer':
                            drop_key = Drop( mob.hitbox.centerx, mob.hitbox.centery - 25 , animations['drops']['key'], turned = False, scale = 2, drop_type='key',)
                            drops_sprite_group.add(drop_key)

                    # Check if projectile hit
                    for projectile in projectile_sprite_group:
                        if pygame.Rect.colliderect(player.attack_rect, projectile) and player.state != DYING:
                            projectile.kill()

                # PLAYER END OF LEVEL (WIN!)
                if player.world_x_pos > (phflorg_data.TILE_SIZE * phflorg_data.MAX_COLS) - player.width:
                    print('win!')
                    player.score += 1000

                
                for bubble in bubble_list:
                    bubble.show()



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
            draw_text('SCORE: ' + str(player.score), font_big, WHITE, (phflorg_data.SCREEN_WIDTH/2)-100, 400)
            if player.score > high_score:
                    high_score = player.score
                    draw_text('NEW HIGH SCORE: ' + str(high_score), font_big, WHITE, (phflorg_data.SCREEN_WIDTH/2)-180, 500)
                    save_high_score(high_score)
            else:
                draw_text('HIGH SCORE: ' + str(high_score), font_big, WHITE, (phflorg_data.SCREEN_WIDTH/2)-150, 500)
            draw_text('Press space to play again', font_big, WHITE, (phflorg_data.SCREEN_WIDTH/2)-250, 600)
            key = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        pygame.quit()
                        exit(0)
                    if event.key == pygame.K_SPACE:
                        # Reset all variables
                        game_over = False
                        player = Player(phflorg_data.SCREEN_WIDTH // 2, phflorg_data.SCREEN_HEIGHT -170 , phflorg_data, p_w, \
                            animations['player']['walk'], animations['player']['attack'], animations['player']['death'], player_sound_effects)

                        scroll = 0
                        bg_scroll = 0

                        if level < max_level:
                            level += 1

                        p_w.load(f'lvl/level{level}_data.csv')

                        fade_counter = 0
                        wait_counter = 0
                        monsters_sprite_group.empty()
                        # Add monsters
                        monster_list = load_monsters(p_w.monster_import_list)


    pygame.display.update()

pygame.quit()