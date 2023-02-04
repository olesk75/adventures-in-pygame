import pygame
from engine import SpriteSheet
from animation import Animation

BLACK = (0,0,0)

""" Loading sprite sheets """
# Player (I call him Stabby, as he ... stabs a lot)
stabby_ss_walk = SpriteSheet(pygame.image.load('assets/spritesheets/stabby-walking.png').convert_alpha(), 32, 32, pygame.Color('#969696'), 4)
stabby_ss_idle = SpriteSheet(pygame.image.load('assets/spritesheets/stabby-idle.png').convert_alpha(), 32, 32, pygame.Color('#969696'), 4)
stabby_ss_attack = SpriteSheet(pygame.image.load('assets/spritesheets/stabby-attack.png').convert_alpha(), 32, 32, pygame.Color('#969696'), 4)
stabby_ss_stomp = SpriteSheet(pygame.image.load('assets/spritesheets/stabby-stomp.png').convert_alpha(), 32, 32, pygame.Color('#969696'), 4)
stabby_ss_death = SpriteSheet(pygame.image.load('assets/spritesheets/stabby-death.png').convert_alpha(), 32, 32, pygame.Color('#969696'), 4)
stabby_ss_cast = SpriteSheet(pygame.image.load('assets/spritesheets/stabby-casting.png').convert_alpha(), 32, 32, pygame.Color('#969696'), 4)

# Monsters
brenda_ss_walk = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/Brenda-walking.png').convert_alpha(), 32, 32, pygame.Color('#c5c7f8'), 4)
minotaur_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/minotaur-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
ogre_archer_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/ogre-archer-sprites.png').convert_alpha(), 64, 64, BLACK, 2)
skeleton_boss_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/skeleton-boss-sprites.png').convert_alpha(), 64, 64, BLACK, 4)
skeleton_boss_attack_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/skeleton-boss-sprites-attack.png').convert_alpha(), 64*3, 64*3, BLACK, 4)
beholder_ss_walk = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/beholder-walking.png').convert_alpha(), 32, 32, pygame.Color('#3e3c40'), 4)

# Drops and animated objects
health_potion_ss =  SpriteSheet(pygame.image.load('assets/spritesheets/objects/lifepotion.png').convert_alpha(), 32, 32, BLACK, 3)
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
        'walk': Animation(stabby_ss_walk, row=0, frames=8, speed=75), 
        'attack': Animation(stabby_ss_attack, row=0, frames=5, speed=50), 
        'death': Animation(stabby_ss_death, row=0, frames=8, speed=150, repeat=False),
        'cast': Animation(stabby_ss_cast, row=0, frames=8, speed=100, repeat=False),
        'idle': Animation(stabby_ss_idle, row=0, frames=8, speed=50), 
        'stomp': Animation(stabby_ss_stomp, row=0, frames=5, speed=30, repeat=False), 
    },
    'minotaur': {
        'walk': Animation(brenda_ss_walk, row=0, frames=8, speed=100), 
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
    'beholder': {
        'walk': Animation(beholder_ss_walk, row=0, frames=8, speed=100), 
        'attack': Animation(beholder_ss_walk, row=0, frames=8, speed=75),
        'death': Animation(beholder_ss_walk, row=0, frames=8, speed=100),
        'cast': None
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
        'health-potion': Animation(health_potion_ss, row=0, frames=7, speed=100, repeat=True),
    },
    'environment': {
        'leaves': Animation(leaves_ss, row=0, frames=10, speed=100, repeat=True)
    },
    'effects': {
        'hit-indicator': Animation(hit_indicator_ss, row=0, frames=13, speed=20, repeat=False)
    }
    
}