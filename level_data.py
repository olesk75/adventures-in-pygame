"""
Level data for all levels
Level 0 is a special test level and not part of the game normally
"""

import pygame

level_0 = {
}

level_1 = {
    'terrain': 'lvl/1/level1_terrain.csv',
    'decorations': 'lvl/1/level1_decorations.csv',
    'hazards':  'lvl/1/level1_hazards.csv',
    'pickups': 'lvl/1/level1_pickups.csv',
    'triggered_objects': 'lvl/1/level1_triggered_objects.csv',
    'monsters': 'lvl/1/level1_monsters.csv',
    'player': 'lvl/1/level1_player.csv',
    'environmental_effect': 'leaves',
    'background': {
        'near': 'assets/backgrounds/lvl1/near.png',
        'medium': 'assets/backgrounds/lvl1/medium.png',
        'far': 'assets/backgrounds/lvl1/far.png',
        'clouds': 'assets/backgrounds/lvl1/clouds.png',
        'background_color': (130, 181, 210),
    }
}


levels = {
    0: level_0,  # test level
	1: level_1,
	# 2: level_2,
	# 3: level_3,
	# 4: level_4,
	# 5: level_5
    }


class GameAudio():
    def __init__(self, level) -> None:

        # Initializing
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.mixer.init()
        pygame.init()

        # Load audio for player
        self.player = {
            'attack': pygame.mixer.Sound('assets/sound/player/attack.wav'),
            'jump': pygame.mixer.Sound('assets/sound/Jump/OGG/Jump 5 - Sound effects Pack 2.ogg'),
            'die': pygame.mixer.Sound('assets/sound/Lose/OGG/Lose 7 - Sound effects Pack 2.ogg'),
            'hit': pygame.mixer.Sound('assets/sound/Laser-weapon/OGG/Laser-weapon 8 - Sound effects Pack 2.ogg'),
            'stomp': pygame.mixer.Sound('assets/sound/player/stomp.flac')                            
        }

        # Load audio for world
        self.key_pickup_fx = pygame.mixer.Sound('assets/sound/objects/key_pickup.wav')
        self.health_pickup_fx = pygame.mixer.Sound('assets/sound/objects/health_pickup.wav')

        # Game music
        if level == 1:
            self.music = pygame.mixer.music
            self.music.load("assets/music/Hidden-Agenda.mp3")
            pygame.mixer.music.set_volume(0.3)

