
monsters = ['minotaur', 'ogre-archer']


class MonsterAI():
    def __init__(self, monster, movement_pattern=0) -> None:
        # movement pattern==0 means default

        known_monsters = {'minotaur', 'ogre-archer'}
        if monster not in known_monsters:
            raise ValueError("Monster must be one of %r." % known_monsters)

        self.monster = monster

        if monster == 'minotaur':
            # DEFAULT: back and forth continuously
            self.direction = 1  # right
            self.speed_walking = 3
            self.speed_attacking = 5
            self.detection_range = 200
            self.attack_range = 75

        if monster == 'ogre-archer':
            #self.pattern == 2:  # Faster walking, full stop when attacking with bow
            self.direction = 1  # right
            self.speed_walking = 1
            self.speed_attacking = 0
            self.detection_range = 400
            self.attack_range = 400
        

