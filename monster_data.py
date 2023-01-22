"""
monsters[]          : list of known monsters in game
MonsterAI(class)    : contains monster data
"""

import random
import pygame

monsters = ['minotaur', 'ogre-archer', 'skeleton-boss', 'elven-caster']  # used to recognize tiles from level files - order must match tile numbering 

# State constants
WALKING = 1
ATTACKING = 2
CASTING = 3
DYING = 4

class MonsterData():
    """ Movement, detection and attack properties of monsters """
    def __init__(self, monster, movement_pattern=0) -> None:
        known_monsters = monsters
        if monster not in known_monsters:
            raise ValueError("Monster must be one of %r." % known_monsters)

        self.monster = monster

        if monster == 'minotaur':
            self.boss = False  # bosses have unique behaviour, not just wondering around
            self.caster = False
            self.direction = 1  # right
            self.speed_walking = 3
            self.speed_attacking = 3
            self.detection_range = 200
            self.detection_range_high = False
            self.attack_range = 50
            self.attack_jumper = False
            self.attack_instant_damage = True  # if the mob attacks, and the player is in range, player dies
            self.attack_delay = 0  # delay between attacks (ms)
            self.attack_damage = 100
            self.points_reward = 100
            self.random_turns = 0.0
            self.hitbox_width = 65 
            self.hitbox_height = 110
            self.sound_attack = False
            self.sound_death = pygame.mixer.Sound('assets/sound/monster/minotaur/death.ogg')

        if monster == 'ogre-archer':
            self.boss = False
            self.caster = False
            self.direction = 1  # right
            self.speed_walking = 1
            self.speed_attacking = 0
            self.detection_range = 400
            self.attack_jumper = False
            self.detection_range_high = False
            self.attack_range = 400
            self.attack_instant_damage = False  # the mob spawns an arrow wchi the player can evade
            self.attack_delay = 2000  # delay between attacks (ms)
            self.attack_damage = 600
            self.points_reward = 150
            self.random_turns = 0.15
            self.hitbox_width = 65 
            self.hitbox_height = 110
            self.sound_attack = False
            self.sound_death = False

        if monster == 'skeleton-boss':
            self.boss = True
            self.caster = True
            self.direction = 1  # right
            self.speed_walking = 4
            self.speed_attacking = 5
            self.detection_range = 400
            self.attack_jumper = True
            self.detection_range_high = True
            self.attack_range = 150
            self.attack_instant_damage = True
            self.attack_delay = 0  # delay between attacks (ms)
            self.attack_damage = 100
            self.points_reward = 500
            self.random_turns = 0.3
            self.hitbox_width = 65
            self.hitbox_height = 110
            self.sound_attack = pygame.mixer.Sound('assets/sound/monster/skeleton-boss/roar.mp3')
 
            # Boss specific
            self.boss_attacks = [('firewalker', 0.01)] 
            self.cast_delay = 2000
            self.item_drop = ['key', 'health']
            self.sound_cast = pygame.mixer.Sound('assets/sound/spell/fire-spell.aif')



    
                

            

