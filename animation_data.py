import pygame
from spritesheet import SpriteSheet
from animation import Animation

BLACK = (0,0,0)

# Create player animations
p_sprite_sheet = SpriteSheet(pygame.image.load('assets/spritesheets/character-sprites2.png').convert_alpha(), 64, 64, BLACK, 2)
p_sprite_sheet_oversize = SpriteSheet(pygame.image.load('assets/spritesheets/character-sprites2.png').convert_alpha(), 64*3, 64*3, BLACK, 2)
player_anim_walk = Animation(p_sprite_sheet, row=11, frames=9, speed=75)
player_anim_attack = Animation(p_sprite_sheet_oversize, row=10, frames=6, speed=30)
player_anim_death = Animation(p_sprite_sheet, row=20, frames=6, speed=800)

# Create monster animations
minotaur_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/minotaur-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
minotaur_anim_walk = Animation(minotaur_ss, row=11, frames=9, speed=50)
minotaur_anim_attack = Animation(minotaur_ss, row=7, frames=8, speed=75)
minotaur_anim_death = Animation(minotaur_ss, row=20, frames=6, speed=100)
ogre_archer_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/ogre-archer-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
ogre_anim_walk = Animation(ogre_archer_ss, row=11, frames=9, speed=50)
ogre_anim_attack = Animation(ogre_archer_ss, row=19, frames=13, speed=100)
ogre_anim_death = Animation(ogre_archer_ss, row=20, frames=6, speed=100)

# Create boss animations
skeleton_boss_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/skeleton-boss-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
skeleton_boss_attack_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/skeleton-boss-sprites-attack.png').convert_alpha(), 64*3, 64*3, BLACK, 2)
skeleton_boss_anim_walk = Animation(skeleton_boss_ss, row=11, frames=9, speed=50)
skeleton_boss_anim_attack = Animation(skeleton_boss_attack_ss, row=3, frames=8, speed=75)
skeleton_boss_anim_death = Animation(skeleton_boss_ss, row=20, frames=6, speed=75)
skeleton_boss_anim_cast = Animation(skeleton_boss_ss, row=2, frames=7, speed=100)

# load animation objects
fire_start = pygame.image.load('assets/objects/fire/burning_start_1.png').convert_alpha()
fire_loop = pygame.image.load('assets/objects/fire/burning_loop_1.png').convert_alpha()
fire_end = pygame.image.load('assets/objects/fire/burning_end_1.png').convert_alpha()
fire_spell = pygame.Surface((fire_start.get_width() + fire_loop.get_width() + fire_end.get_width(),fire_start.get_height())).convert_alpha()

health_potion_ss =  SpriteSheet(pygame.image.load('assets/objects/lifepotion.png').convert_alpha(), 16, 16, BLACK, 2)
health_potion_anim = Animation(health_potion_ss, row=0, frames=4, speed=100, repeat=True)

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
door_ss = SpriteSheet(pygame.image.load('assets/door-sprites - large.png'), 64, 61, BLACK, 2)
door_anim = Animation(door_ss, row=0, frames=4, speed=100, repeat=False)

# Creating pickup animations
key_ss = SpriteSheet(pygame.image.load('assets/objects/key.png'), 32, 32, BLACK, 2)
key_anim = Animation(key_ss, row=0, frames=10, speed=50, repeat=True)


""" Create main animation dict """
animations = {
    'player': {
        'walk': player_anim_walk, 
        'attack': player_anim_attack, 
        'death': player_anim_death
    },
    'minotaur': {
        'walk': minotaur_anim_walk, 
        'attack': minotaur_anim_attack,
        'death': minotaur_anim_death
    },
    'ogre-archer': {
        'walk': ogre_anim_walk,
        'attack': ogre_anim_attack,
        'death': ogre_anim_death
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
    },
    'drops': {
        'key': key_anim,
    },
    'objects': {
        'health-potion': health_potion_anim,
    }
}
