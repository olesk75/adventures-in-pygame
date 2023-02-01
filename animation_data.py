import pygame
from engine import SpriteSheet
from animation import Animation

BLACK = (0,0,0)

""" Loading sprite sheets """
# Player
player_ss_walk = SpriteSheet(pygame.image.load('assets/spritesheets/player-walking.png').convert_alpha(), 64, 64, BLACK, 2)
player_ss_attack = SpriteSheet(pygame.image.load('assets/spritesheets/player-attacking.png').convert_alpha(), 64, 64, BLACK, 2)
player_ss_cast = SpriteSheet(pygame.image.load('assets/spritesheets/player-casting.png').convert_alpha(), 64, 64, BLACK, 2)
player_ss_die = SpriteSheet(pygame.image.load('assets/spritesheets/player-dying.png').convert_alpha(), 64, 64, BLACK, 2)


# Monsters
minotaur_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/minotaur-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
ogre_archer_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/ogre-archer-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
skeleton_boss_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/skeleton-boss-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
skeleton_boss_attack_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/skeleton-boss-sprites-attack.png').convert_alpha(), 64*3, 64*3, BLACK, 2)

# Drops and animated objects
health_potion_ss =  SpriteSheet(pygame.image.load('assets/spritesheets/objects/lifepotion.png').convert_alpha(), 16, 16, BLACK, 3)
key_ss = SpriteSheet(pygame.image.load('assets/spritesheets/objects/key.png').convert_alpha(), 32, 32, BLACK, 2)
door_ss = SpriteSheet(pygame.image.load('assets/spritesheets/objects/portcullis.png').convert_alpha(), 32, 32, BLACK, 4)

# Hazards
fire_ss = SpriteSheet(pygame.image.load('assets/spritesheets/hazards/fire-loop-sheet.png').convert_alpha(), 16,24, BLACK, 4)
spike_ss = SpriteSheet(pygame.image.load('assets/spritesheets/hazards/spikes.png').convert_alpha(), 32, 32, BLACK, 2)

# Spells
fire_spell_ss = SpriteSheet(pygame.image.load('assets/spritesheets/spells/fire-spell.png').convert_alpha(), 24,32, BLACK, 2)

# Environmental effects
leaves_ss = SpriteSheet(pygame.image.load('assets/spritesheets/env/leaf.png').convert_alpha(), 16,16, BLACK, 1)

# Effects
hit_indicator_ss = SpriteSheet(pygame.image.load('assets/spritesheets/effects/hit-star.png').convert_alpha(), 32,32, BLACK, 2)


""" Create main animation dict """
anim = {
    'player': {
        'walk': Animation(player_ss_walk, row=0, frames=9, speed=75), 
        'attack': Animation(player_ss_attack, row=0, frames=10, speed=30), 
        'death': Animation(player_ss_die, row=0, frames=6, speed=200),
        'cast': Animation(player_ss_cast, row=0, frames=7, speed=200),
        'idle': None
    },
    'minotaur': {
        'walk': Animation(minotaur_ss, row=11, frames=9, speed=50), 
        'attack': Animation(minotaur_ss, row=7, frames=8, speed=75),
        'death': Animation(minotaur_ss, row=20, frames=6, speed=100),
        'cast': None
    },
    'ogre-archer': {
        'walk': Animation(ogre_archer_ss, row=11, frames=9, speed=50),
        'attack': Animation(ogre_archer_ss, row=19, frames=13, speed=100),
        'death': Animation(ogre_archer_ss, row=20, frames=6, speed=100),
        'cast': None
    },
    'skeleton-boss': {
        'walk': Animation(skeleton_boss_ss, row=11, frames=9, speed=50), 
        'attack': Animation(skeleton_boss_attack_ss, row=3, frames=8, speed=75), 
        'death': Animation(skeleton_boss_ss, row=20, frames=6, speed=75), 
        'cast': Animation(skeleton_boss_ss, row=2, frames=7, speed=100)
    },
    'fire': {
        'fire-spell': Animation(fire_spell_ss, row=0, frames=17, speed=100),
        'fire-hazard': Animation(fire_ss, row=0, frames=8, speed=50)

    },
    'spikes': {
        'spike-trap': Animation(spike_ss, row=0, frames=2, speed=100)
    },
    'doors': {
        'end-of-level': Animation(door_ss, row=0, frames=22, speed=100, repeat=False),
    },
    'pickups': {
        'key': Animation(key_ss, row=0, frames=10, speed=50, repeat=True),
        'health-potion': Animation(health_potion_ss, row=0, frames=7, speed=150, repeat=True),
    },
    'environment': {
        'leaves': Animation(leaves_ss, row=0, frames=10, speed=100, repeat=True)
    },
    'effects': {
        'hit-indicator': Animation(hit_indicator_ss, row=0, frames=13, speed=20, repeat=False)
    }
    
}