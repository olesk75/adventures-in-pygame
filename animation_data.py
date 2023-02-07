import pygame
from animation import Animation, SpriteSheet

BLACK = (0,0,0)

""" Loading sprite sheets """
# Player (I call him Stabby, as he ... stabs a lot)
stabby_ss_walk = SpriteSheet(pygame.image.load('assets/spritesheets/stabby-walking.png').convert_alpha(), 32, 32, 4)
stabby_ss_idle = SpriteSheet(pygame.image.load('assets/spritesheets/stabby-idle.png').convert_alpha(), 32, 32, 4)
stabby_ss_attack = SpriteSheet(pygame.image.load('assets/spritesheets/stabby-attack.png').convert_alpha(), 32, 32, 4)
stabby_ss_stomp = SpriteSheet(pygame.image.load('assets/spritesheets/stabby-stomp.png').convert_alpha(), 32, 32, 4)
stabby_ss_death = SpriteSheet(pygame.image.load('assets/spritesheets/stabby-death.png').convert_alpha(), 32, 32, 4)
stabby_ss_cast = SpriteSheet(pygame.image.load('assets/spritesheets/stabby-casting.png').convert_alpha(), 32, 32, 4)

# Monsters
brenda_ss_walk = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/Brenda-walking.png').convert_alpha(), 32, 32, 4)
minotaur_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/minotaur-sprites.png').convert_alpha(), 64, 64, 2)

elven_archer_running_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/elven-archer-running.png').convert_alpha(), 32, 32, 4)
elven_archer_attacking_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/elven-archer-attacking.png').convert_alpha(), 32, 32, 4)
elven_archer_dying_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/elven-archer-dying.png').convert_alpha(), 32, 32, 4)

skeleton_boss_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/skeleton-boss-sprites.png').convert_alpha(), 64, 64, 4)
skeleton_boss_attack_ss = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/skeleton-boss-sprites-attack.png').convert_alpha(), 64*3, 64*3, 4)
beholder_ss_walk = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/beholder-walking.png').convert_alpha(), 32, 32, 4)
beholder_ss_attack = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/beholder-attacking.png').convert_alpha(), 32, 32, 4)
beholder_ss_death = SpriteSheet(pygame.image.load('assets/spritesheets/monsters/beholder-dying.png').convert_alpha(), 32, 32, 4)

# Drops and animated objects
health_potion_ss =  SpriteSheet(pygame.image.load('assets/spritesheets/objects/lifepotion.png').convert_alpha(), 32, 32, 3)
stomp_potion_ss =  SpriteSheet(pygame.image.load('assets/spritesheets/objects/stomppotion.png').convert_alpha(), 32, 32, 3)
mana_potion_ss =  SpriteSheet(pygame.image.load('assets/spritesheets/objects/manapotion.png').convert_alpha(), 32, 32, 3)
key_ss = SpriteSheet(pygame.image.load('assets/spritesheets/objects/key.png').convert_alpha(), 32, 32, 2)
door_ss = SpriteSheet(pygame.image.load('assets/spritesheets/objects/portcullis.png').convert_alpha(), 32, 32, 4)

# Hazards
fire_ss = SpriteSheet(pygame.image.load('assets/spritesheets/hazards/fire-loop-sheet.png').convert_alpha(), 16,24, 4)
spike_ss = SpriteSheet(pygame.image.load('assets/spritesheets/hazards/spikes.png').convert_alpha(), 32, 32, 2)

# Spells
fire_spell_ss = SpriteSheet(pygame.image.load('assets/spritesheets/spells/fire-spell.png').convert_alpha(), 24,32, 2)

# Environmental effects
leaves_ss = SpriteSheet(pygame.image.load('assets/spritesheets/env/leaf.png').convert_alpha(), 16,16, 1)

# Effects
dust_ss = SpriteSheet(pygame.image.load('assets/spritesheets/effects/dust-landing.png').convert_alpha(), 52,16, 2)

# Decor
heart_ss = SpriteSheet(pygame.image.load('assets/spritesheets/decor/heart-beating.png').convert_alpha(), 16, 16, 2)
stomp_ss = SpriteSheet(pygame.image.load('assets/spritesheets/decor/boot-stomping.png').convert_alpha(), 16, 16, 2)

""" Create main animation dict """
anim = {
    'player': {
        'walk': Animation(stabby_ss_walk, frames=8, speed=75), 
        'attack': Animation(stabby_ss_attack, frames=5, speed=50), 
        'death': Animation(stabby_ss_death, frames=8, speed=150, repeat=False),
        'cast': Animation(stabby_ss_cast, frames=8, speed=100, repeat=False),
        'idle': Animation(stabby_ss_idle, frames=8, speed=50), 
        'stomp': Animation(stabby_ss_stomp, frames=5, speed=30, repeat=False), 
    },
    'minotaur': {
        'walk': Animation(brenda_ss_walk, frames=8, speed=100), 
        'attack': Animation(minotaur_ss, row=7, frames=8, speed=75),
        'death': Animation(minotaur_ss, row=20, frames=6, speed=100, repeat=False),
        'cast': None
    },
    'elven-archer': {
        'walk': Animation(elven_archer_running_ss, frames=8, speed=50),
        'attack': Animation(elven_archer_attacking_ss, frames=8, speed=100),
        'death': Animation(elven_archer_dying_ss, frames=7, speed=100, repeat=False),
        'cast': None
    },
    'skeleton-boss': {
        'walk': Animation(skeleton_boss_ss, row=11, frames=9, speed=50), 
        'attack': Animation(skeleton_boss_attack_ss, row=3, frames=8, speed=75), 
        'death': Animation(skeleton_boss_ss, row=20, frames=6, speed=75, repeat=False), 
        'cast': Animation(skeleton_boss_ss, row=2, frames=7, speed=100)
    },
    'beholder': {
        'walk': Animation(beholder_ss_walk, frames=8, speed=100), 
        'attack': Animation(beholder_ss_attack, frames=8, speed=75),
        'death': Animation(beholder_ss_death, frames=8, speed=100, repeat=False),
        'cast': None
    },
    'fire': {
        'fire-spell': Animation(fire_spell_ss, frames=17, speed=100),
        'fire-hazard': Animation(fire_ss, frames=8, speed=50)

    },
    'spikes': {
        'spike-trap': Animation(spike_ss, frames=2, speed=100)
    },
    'doors': {
        'end-of-level': Animation(door_ss, frames=22, speed=100, repeat=False),
    },
    'pickups': {
        'key': Animation(key_ss, frames=10, speed=50, repeat=True),
        'health-potion': Animation(health_potion_ss, frames=7, speed=100, repeat=True),
        'stomp-potion': Animation(stomp_potion_ss, frames=7, speed=100, repeat=True),
        'mana-potion': Animation(mana_potion_ss, frames=7, speed=100, repeat=True),
    },
    'environment': {
        'leaves': Animation(leaves_ss, frames=10, speed=100, repeat=True)
    },
    'effects': {
        'dust-landing': Animation(dust_ss, frames=5, speed=50, repeat=False),
    },
    'decor': {
        'beating-heart': Animation(heart_ss, frames=8, speed=50),
        'stomping-foot': Animation(stomp_ss, frames=8, speed=50)
    }
    
}