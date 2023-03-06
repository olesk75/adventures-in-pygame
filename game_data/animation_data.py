import pygame as pg
from animation import Animation, SpriteSheet

BLACK = (0,0,0)

""" Loading sprite sheets """
# Player (I call him Stabby, as he ... stabs a lot)
stabby_ss_walk = SpriteSheet(pg.image.load('assets/spritesheets/player/stabby-walking.png').convert_alpha(), 32, 32, 4)
stabby_ss_idle = SpriteSheet(pg.image.load('assets/spritesheets/player/stabby-idle.png').convert_alpha(), 32, 32, 4)
stabby_ss_attack = SpriteSheet(pg.image.load('assets/spritesheets/player/stabby-attack.png').convert_alpha(), 32, 32, 4)
stabby_ss_stomp = SpriteSheet(pg.image.load('assets/spritesheets/player/stabby-stomp.png').convert_alpha(), 32, 32, 4)
stabby_ss_death = SpriteSheet(pg.image.load('assets/spritesheets/player/stabby-death.png').convert_alpha(), 32, 32, 4)
stabby_ss_cast = SpriteSheet(pg.image.load('assets/spritesheets/player/stabby-casting.png').convert_alpha(), 32, 32, 4)

# Monsters
elven_archer_running_ss = SpriteSheet(pg.image.load('assets/spritesheets/monsters/elven-archer-running.png').convert_alpha(), 32, 32, 4)
elven_archer_attacking_ss = SpriteSheet(pg.image.load('assets/spritesheets/monsters/elven-archer-attacking.png').convert_alpha(), 32, 32, 4)
elven_archer_dying_ss = SpriteSheet(pg.image.load('assets/spritesheets/monsters/elven-archer-dying.png').convert_alpha(), 32, 32, 4)

skeleton_keybearer_walk_ss = SpriteSheet(pg.image.load('assets/spritesheets/monsters/skeleton-keybearer-walking.png').convert_alpha(), 64, 64, 4)
skeleton_keybearer_attack_ss = SpriteSheet(pg.image.load('assets/spritesheets/monsters/skeleton-keybearer-attacking.png').convert_alpha(), 128, 64, 4)
skeleton_keybearer_cast_ss = SpriteSheet(pg.image.load('assets/spritesheets/monsters/skeleton-keybearer-casting.png').convert_alpha(), 64, 64, 4)
skeleton_keybearer_die_ss = SpriteSheet(pg.image.load('assets/spritesheets/monsters/skeleton-keybearer-dying.png').convert_alpha(), 64, 64, 4)

beholder_ss_walk = SpriteSheet(pg.image.load('assets/spritesheets/monsters/beholder-walking.png').convert_alpha(), 32, 32, 4)
beholder_ss_attack = SpriteSheet(pg.image.load('assets/spritesheets/monsters/beholder-attacking.png').convert_alpha(), 32, 32, 4)
beholder_ss_death = SpriteSheet(pg.image.load('assets/spritesheets/monsters/beholder-dying.png').convert_alpha(), 32, 32, 4)

skeleton_warrior_ss_walk = SpriteSheet(pg.image.load('assets/spritesheets/monsters/skeleteon-warrior-walking.png').convert_alpha(), 32, 32, 4)
skeleton_warrior_ss_attack = SpriteSheet(pg.image.load('assets/spritesheets/monsters/skeleteon-warrior-attacking.png').convert_alpha(), 32, 32, 4)
skeleton_warrior_ss_hit = SpriteSheet(pg.image.load('assets/spritesheets/monsters/skeleteon-warrior-hit.png').convert_alpha(), 32, 32, 4)
skeleton_warrior_ss_death = SpriteSheet(pg.image.load('assets/spritesheets/monsters/skeleteon-warrior-death.png').convert_alpha(), 32, 32, 4)

# Drops and animated objects
health_potion_ss =  SpriteSheet(pg.image.load('assets/spritesheets/objects/lifepotion.png').convert_alpha(), 32, 32, 3)
stomp_potion_ss =  SpriteSheet(pg.image.load('assets/spritesheets/objects/stomppotion.png').convert_alpha(), 32, 32, 3)
mana_potion_ss =  SpriteSheet(pg.image.load('assets/spritesheets/objects/manapotion.png').convert_alpha(), 32, 32, 3)
key_ss = SpriteSheet(pg.image.load('assets/spritesheets/objects/key.png').convert_alpha(), 32, 32, 2)
door_left_ss = SpriteSheet(pg.image.load('assets/spritesheets/objects/door-left.png').convert_alpha(), 32, 64, 2)
door_right_ss = SpriteSheet(pg.image.load('assets/spritesheets/objects/door-right.png').convert_alpha(), 32, 64, 2)
chest_ss = SpriteSheet(pg.image.load('assets/spritesheets/objects/chest.png').convert_alpha(), 32, 32, 4)
portal_ss = SpriteSheet(pg.image.load('assets/spritesheets/objects/portal.png').convert_alpha(), 32, 32, 4)

# Hazards
fire_ss = SpriteSheet(pg.image.load('assets/spritesheets/hazards/fire-loop-sheet.png').convert_alpha(), 16,24, 4)
spike_ss = SpriteSheet(pg.image.load('assets/spritesheets/hazards/spikes.png').convert_alpha(), 32, 32, 2)

# Spells
fire_spell_ss = SpriteSheet(pg.image.load('assets/spritesheets/spells/fire-spell.png').convert_alpha(), 24,32, 2)

# Environmental effects
leaves_ss = SpriteSheet(pg.image.load('assets/spritesheets/env/leaf.png').convert_alpha(), 16,16, 2)

# Effects
dust_ss = SpriteSheet(pg.image.load('assets/spritesheets/effects/dust-landing.png').convert_alpha(), 52,16, 2)

# Decor
heart_ss = SpriteSheet(pg.image.load('assets/spritesheets/decor/heart-beating.png').convert_alpha(), 16, 16, 2)
stomp_ss = SpriteSheet(pg.image.load('assets/spritesheets/decor/boot-stomping.png').convert_alpha(), 16, 16, 2)

""" Create main animation dict 
    Note: this creates ONE animation for each situation. So two objects being assigned the same animation will have 
    pointers to exactly the _same_ animation object (so will be completely in sync always).
    The only way to get unique copies is to use copy.copy() or make a manual Animation object for each use case
"""
anim = {
    'player': {
        'walk': Animation(stabby_ss_walk, frames=8, speed=75), 
        'attack': Animation(stabby_ss_attack, frames=5, speed=30), 
        'death': Animation(stabby_ss_death, frames=8, speed=150, repeat=False),
        'cast': Animation(stabby_ss_cast, frames=8, speed=100, repeat=False),
        'idle': Animation(stabby_ss_idle, frames=8, speed=50), 
        'stomp': Animation(stabby_ss_stomp, frames=5, speed=30, repeat=False), 
    },
    'elven-archer': {
        'walk': Animation(elven_archer_running_ss, frames=8, speed=50),
        'attack': Animation(elven_archer_attacking_ss, frames=8, speed=80),
        'death': Animation(elven_archer_dying_ss, frames=7, speed=50, repeat=False),
        'cast': None
    },
    'skeleton-keybearer': {
        'walk': Animation(skeleton_keybearer_walk_ss, frames=9, speed=50), 
        'attack': Animation(skeleton_keybearer_attack_ss, frames=8, speed=75), 
        'death': Animation(skeleton_keybearer_die_ss, frames=5, speed=75, repeat=False),
        'idle': None,
        'cast': Animation(skeleton_keybearer_cast_ss, frames=7, speed=100)
    },
    'beholder': {
        'walk': Animation(beholder_ss_walk, frames=10, speed=25), 
        'attack': Animation(beholder_ss_attack, frames=8, speed=50),
        'death': Animation(beholder_ss_death, frames=8, speed=50, repeat=False),
        'idle': None,
        'cast': None
    },
    'skeleton-warrior': {
        'walk': Animation(skeleton_warrior_ss_walk, frames=8, speed=50), 
        'attack': Animation(skeleton_warrior_ss_attack, frames=7, speed=100),
        'death': Animation(skeleton_warrior_ss_death, frames=10, speed=50, repeat=False),
        'hit': Animation(skeleton_warrior_ss_hit, frames=1, speed=50, repeat=False),
        'idle': None,
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
        'left-wood': Animation(door_left_ss, frames=2, speed=1, repeat=False),
        'right-wood': Animation(door_right_ss, frames=2, speed=1, repeat=False),
    },
    'pickups': {
        'key': Animation(key_ss, frames=10, speed=50, repeat=True),
        'health-potion': Animation(health_potion_ss, frames=7, speed=100, repeat=True),
        'stomp-potion': Animation(stomp_potion_ss, frames=7, speed=100, repeat=True),
        'mana-potion': Animation(mana_potion_ss, frames=7, speed=100, repeat=True),
    },
    'objects': {
        'chest': Animation(chest_ss, frames=9, speed=100, repeat=False),
        'portal': Animation(portal_ss, frames=5, speed=100, repeat=True),
    },
    'environment': {
        'leaves': Animation(leaves_ss, frames=10, speed=100, repeat=True)  # NOT IN USE - WE NEED INDIVIDUAL NAIMATIONS FFOR EACH INSTANCE
    },
    'effects': {
        'dust-landing': Animation(dust_ss, frames=5, speed=50, repeat=False),
    },
    'decor': {
        'beating-heart': Animation(heart_ss, frames=8, speed=50),
        'stomping-foot': Animation(stomp_ss, frames=8, speed=50)
    }
    
}