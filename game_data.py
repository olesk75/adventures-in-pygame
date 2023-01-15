
monsters = ['minotaur', 'ogre-archer', 'skeleton-boss']  # used to recognize tiles from level files


class MonsterAI():
    """ Movement, detection and attack properties of monsters """
    def __init__(self, monster, movement_pattern=0) -> None:
        # TODO: movement patterns

        known_monsters = monsters
        if monster not in known_monsters:
            raise ValueError("Monster must be one of %r." % known_monsters)

        self.monster = monster

        if monster == 'minotaur':
            # DEFAULT: back and forth continuously
            self.direction = 1  # right
            self.speed_walking = 3
            self.speed_attacking = 3
            self.detection_range = 200
            self.attack_range = 50
            self.attack_instadeath = True  # if the mob attacks, and the player is in range, player dies
            self.attack_delay = 0  # delay between attacks (ms)
            self.attack_damage = 100

        if monster == 'ogre-archer':
            #self.pattern == 2:  # Faster walking, full stop when attacking with bow
            self.direction = 1  # right
            self.speed_walking = 1
            self.speed_attacking = 0
            self.detection_range = 400
            self.attack_range = 400
            self.attack_instadeath = False  # the mob spawns an arrow wchi the player can evade
            self.attack_delay = 2500  # delay between attacks (ms)
            self.attack_damage = 400

        if monster == 'skeleton-boss':
            #self.pattern == 2:  # Faster walking, full stop when attacking with bow
            self.direction = 1  # right
            self.speed_walking = 1
            self.speed_attacking = 5
            self.detection_range = 400
            self.attack_range = 150
            self.attack_instadeath = True
            self.attack_delay = 0  # delay between attacks (ms)
            self.attack_damage = 1000


