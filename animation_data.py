import pygame
from spritesheet import SpriteSheet
from animation import Animation

BLACK = (0,0,0)

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
skeleton_boss_anim_cast = Animation(skeleton_boss_ss, row=2, frames=7, speed=100)

# load animation objects
fire_start = pygame.image.load('assets/objects/fire/burning_start_1.png').convert_alpha()
fire_loop = pygame.image.load('assets/objects/fire/burning_loop_1.png').convert_alpha()
fire_end = pygame.image.load('assets/objects/fire/burning_end_1.png').convert_alpha()
fire_spell = pygame.Surface((fire_start.get_width() + fire_loop.get_width() + fire_end.get_width(),fire_start.get_height())).convert_alpha()

# Adding the three fire sheets together into one sprite sheet
fire_spell.blit(fire_start, (0, 0))
fire_spell.blit(fire_loop, (fire_start.get_width(), 0))
fire_spell.blit(fire_end, (fire_loop.get_width() + fire_start.get_width(), 0))
fire_spell_ss = SpriteSheet(fire_spell.convert_alpha(), 24,32, BLACK, 2)
fire_spell_anim = Animation(fire_spell_ss, row=0, frames=17, speed=100)

# Creating fire hazard animation
fire_ss = SpriteSheet(fire_loop.convert_alpha(), 24,32, BLACK, 4)
fire_anim = Animation(fire_ss, row=0, frames=8, speed=50)

# Creating spike hazard animation
spike_ss = SpriteSheet(pygame.image.load('assets/spikes.png').convert_alpha(), 32, 32, BLACK, 2)
spike_anim = Animation(spike_ss, row=0, frames=2, speed=100)

# Creating door animation
door_ss = SpriteSheet(pygame.image.load('assets/door-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
door_anim = Animation(spike_ss, row=0, frames=4, speed=100)


""" Create main animation dict """
animations = {
    'player': {
        'walk': player_anim_walk, 
        'attack': player_anim_attack, 
        'death': player_anim_death
    },
    'minotaur': {
        'walk': minotaur_anim_walk, 
        'attack': minotaur_anim_attack
    },
    'ogre-archer': {
        'walk': ogre_anim_walk,
        'attack': ogre_anim_attack
    },
    'skeleton-boss': {
        'walk': skeleton_boss_anim_walk, 
        'attack': skeleton_boss_anim_attack, 
        'death': skeleton_boss_anim_death, 
        'cast': skeleton_boss_anim_cast
    },
    'fire': {
        'fire-spell': fire_spell_anim,
        'fire-hazard': fire_anim
    },
    'spikes': {
        'spike-trap': spike_anim
    },
    'doors': {
        'end-of-level': door_anim,
    }
}
