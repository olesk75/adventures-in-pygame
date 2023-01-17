"""
monsters[]          : list of known monsters in game
MonsterAI(class)    : contains monster data
"""

import random

monsters = ['minotaur', 'ogre-archer', 'skeleton-boss']  # used to recognize tiles from level files


class MonsterData():
    """ Movement, detection and attack properties of monsters """
    def __init__(self, monster, movement_pattern=0) -> None:
        # TODO: movement patterns

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
            self.boss_attacks = [('firewalker', 0.01)]

    def boss_battle(self, boss, player) -> tuple:
        self.boss = boss  # Monster instance
        self.player = player

        self.casting_done = False

        dx = 0  # these are absolute moves, not speed 
        dy = 0  # speed equivalent
        
        def _casting(self, attack_type) -> None:
            attack = attack_type
            print(f'{attack}')

            if self.casting_done:
                self.boss.busy_casting = None

        # Casting puts everything else on hold
        if self.boss.busy_casting:
            _casting(self.boss.busy_casting)

        else:
            if self.monster ==  'skeleton-boss':
                if self.boss.attacking:
                    for attack in self.boss_attacks:
                        if attack[1] > random.random():
                            print(attack)
                            self.boss.busy_casting = attack[0]
                            _casting(attack[0])
                    
                    dx = self.speed_attacking
                
                    # Sometimes a jumping mob can jump if player is higher than the mob and mob is attacking
                    max_dist_centery = -7
                    player_above_mob = player.rect.centery -  (self.boss.rect.centery + max_dist_centery)
                    if self.attack_jumper and player_above_mob < 0 and self.boss.vel_y == 0:  # player is higher up and we're not already jumping
                        if 0.01  > random.random():  # hardcoded jump probability
                            self.boss.vel_y = -10
                else:
                        dx = self.speed_walking  #  we start at walking speed

                        # We throw in random cahnges in direction, different by mod type
                        if self.random_turns / 100  > random.random():
                            dx *= -1
                            self.direction *= -1
                            self.boss.turned = not self.boss.turned

        return (dx, dy)

                

            

