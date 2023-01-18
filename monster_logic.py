"""
monsters[]          : list of known monsters in game
MonsterAI(class)    : contains monster data
"""

import random

monsters = ['minotaur', 'ogre-archer', 'skeleton-boss']  # used to recognize tiles from level files


class MonsterData():
    """ Movement, detection and attack properties of monsters """
    def __init__(self, monster, movement_pattern=0) -> None:
        
 

        known_monsters = monsters
        if monster not in known_monsters:
            raise ValueError("Monster must be one of %r." % known_monsters)

        self.monster = monster

        if monster == 'minotaur':
            self.boss = False  # bosses have unique behaviour, not just wondering around
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

        if monster == 'ogre-archer':
            self.boss = False
            self.direction = 1  # right
            self.speed_walking = 1
            self.speed_attacking = 0
            self.detection_range = 400
            self.attack_jumper = False
            self.detection_range_high = False
            self.attack_range = 400
            self.attack_instant_damage = False  # the mob spawns an arrow wchi the player can evade
            self.attack_delay = 2000  # delay between attacks (ms)
            self.attack_damage = 400
            self.points_reward = 150
            self.random_turns = 0.15

        if monster == 'skeleton-boss':
            self.boss = True
            self.direction = 1  # right
            self.speed_walking = 4
            self.speed_attacking = 5
            self.detection_range = 400
            self.attack_jumper = True
            self.detection_range_high = True
            self.attack_range = 150
            self.attack_instant_damage = True
            self.attack_delay = 0  # delay between attacks (ms)
            self.attack_damage = 1
            self.points_reward = 500
            self.random_turns = 0.3
            
            # Boss specific
            self.boss_attacks = [('firewalker', 0.01)]
            self.cast_delay = 2000


    def boss_battle(self, boss, player) -> tuple:
        """ Movement and attacks for specific bosess 
            returns: dx and dy for mob (replaces the normal walking/bumping dx/dy for regular mobs)
        """
        # State constants
        WALKING = 1
        ATTACKING = 2
        CASTING = 3
        DYING = 4
        
        self.boss = boss  # Monster instance
        self.player = player

        self.dx = 0  # these are absolute moves, not speed 
        self.dy = 0  # speed equivalent
        
        def _casting(attack_type) -> None:
            sprite_size = 32
            if self.boss.cast_anim.anim_counter == self.boss.cast_anim.frames - 1:  # on last cast animation frame, trigger the spell
                if attack_type == 'firewalker':
                    self.boss.cast_anim_list.append(['fire', self.boss.rect.left - sprite_size * 3, self.boss.rect.bottom - sprite_size * 2])
                    self.boss.cast_anim_list.append(['fire', self.boss.rect.left - sprite_size * 3.5, self.boss.rect.bottom - sprite_size * 2])
                    self.boss.cast_anim_list.append(['fire', self.boss.rect.left - sprite_size * 4, self.boss.rect.bottom - sprite_size * 2])
                    self.boss.cast_anim_list.append(['fire', self.boss.rect.left - sprite_size * 4.5, self.boss.rect.bottom - sprite_size * 2])
                    self.boss.cast_anim_list.append(['fire', self.boss.rect.left - sprite_size * 5, self.boss.rect.bottom - sprite_size * 2])

                    self.boss.cast_anim_list.append(['fire', self.boss.rect.right + sprite_size, self.boss.rect.bottom - sprite_size * 2])
                    self.boss.cast_anim_list.append(['fire', self.boss.rect.right + sprite_size * 1.5, self.boss.rect.bottom - sprite_size * 2])
                    self.boss.cast_anim_list.append(['fire', self.boss.rect.right + sprite_size * 2, self.boss.rect.bottom - sprite_size * 2])
                    self.boss.cast_anim_list.append(['fire', self.boss.rect.right + sprite_size * 2.5, self.boss.rect.bottom - sprite_size * 2])
                    self.boss.cast_anim_list.append(['fire', self.boss.rect.right + sprite_size * 3, self.boss.rect.bottom - sprite_size * 2])
                    self.boss.state = WALKING
                    self.boss.spells_list = []
                    self.dx = self.speed_walking

        # Casting puts everything else on hold
        if self.boss.spells_list:
            _casting(self.boss.spells_list)

        else:
            if self.monster ==  'skeleton-boss':
                if self.boss.state == ATTACKING:
                    for attack in self.boss_attacks:
                        if attack[1] > random.random():
                            self.boss.cast_anim.active = True  # we start the casting animation
                            self.boss.spells_list = attack[0]
                            self.boss.state = CASTING
                            _casting(attack[0])
                            self.dx = 0  # we stop to cast
                        else:
                            self.dx = self.speed_attacking
                
                    # Sometimes a jumping mob can jump if player is higher than the mob and mob is attacking
                    max_dist_centery = -7
                    player_above_mob = player.rect.centery -  (self.boss.rect.centery + max_dist_centery)
                    if self.attack_jumper and player_above_mob < 0 and self.boss.vel_y == 0:  # player is higher up and we're not already jumping
                        if 0.01  > random.random():  # hardcoded jump probability
                            self.boss.vel_y = -10
                else:
                        self.dx = self.speed_walking  #  we start at walking speed

                        # We throw in random cahnges in direction, different by mod type
                        if self.random_turns / 100  > random.random():
                            self.dx *= -1
                            self.direction *= -1
                            self.boss.turned = not self.boss.turned

        return self.dx, self.dy

                

            
