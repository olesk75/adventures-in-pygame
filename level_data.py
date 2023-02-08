"""
Level data for all levels
Level 0 is a special test level and not part of the game normally
"""

import pygame

level_0 = {
    'size_x': 250,
    'size_y': 15,
    'pos_terrain': 'lvl/lvl 1 - mountains/level1_terrain.csv',
    'pos_decorations': 'lvl/lvl 1 - mountains/level1_decorations.csv',
    'pos_hazards':  'lvl/lvl 1 - mountains/level1_hazards.csv',
    'pos_pickups': 'lvl/lvl 1 - mountains/level1_pickups.csv',
    'pos_triggered_objects': 'lvl/lvl 1 - mountains/level1_triggered_objects.csv',
    'pos_monsters': 'lvl/lvl 1 - mountains/level1_monsters.csv',
    'pos_player': 'lvl/lvl 1 - mountains/level1_player.csv',
    'environmental_effect': 'leaves',
    'terrain_ts': 'assets/tile/tilesets/mountain-terrain-tileset.png',
    'background': {
        'near': 'assets/backgrounds/lvl1/near.png',
        'medium': 'assets/backgrounds/lvl1/medium.png',
        'further': 'assets/backgrounds/lvl1/further.png',
        'far': 'assets/backgrounds/lvl1/far.png',
        'clouds': 'assets/backgrounds/lvl1/clouds.png',
        'background_color': (130, 181, 255),
        'y_adjust': [0,150,400,450,0],
    },
    'tileset': 'mountain',
    'solid_tiles': range(32),  # the tiles that will keep a player or monster up
    'moving_horiz': [27],  #  moving platforms
    'moving_vert': [[3,11,19]],  # bobbing platforms (in one group)
    'music': None  # TODO: move music here
}

level_1 = {
    'pos_terrain': 'lvl/1/level1_terrain.csv',
    'pos_decorations': 'lvl/1/level1_decorations.csv',
    'pos_hazards':  'lvl/1/level1_hazards.csv',
    'pos_pickups': 'lvl/1/level1_pickups.csv',
    'pos_triggered_objects': 'lvl/1/level1_triggered_objects.csv',
    'pos_monsters': 'lvl/1/level1_monsters.csv',
    'pos_player': 'lvl/1/level1_player.csv',
    'environmental_effect': 'leaves',
    'background': {
        'near': 'assets/backgrounds/lvl1/near.png',
        'medium': 'assets/backgrounds/lvl1/medium.png',
        'further': 'assets/backgrounds/lvl1/further.png',
        'far': 'assets/backgrounds/lvl1/far.png',
        'clouds': 'assets/backgrounds/lvl1/clouds.png',
        'background_color': (130, 181, 210),
        'y_adjust': [0,150,400,450,0]
    }
}

level_2 = {
    'pos_terrain': 'lvl/2/level2_terrain.csv',
    'pos_decorations': 'lvl/2/level2_decorations.csv',
    'pos_hazards':  'lvl/2/level2_hazards.csv',
    'pos_pickups': 'lvl/2/level2_pickups.csv',
    'pos_triggered_objects': 'lvl/2/level2_triggered_objects.csv',
    'pos_monsters': 'lvl/2/level2_monsters.csv',
    'pos_player': 'lvl/2/level2_player.csv',
    'environmental_effect': 'leaves',
    'background': {
        'near': 'assets/backgrounds/lvl2/near.png',
        'medium': 'assets/backgrounds/lvl2/medium.png',
        'further': 'assets/backgrounds/lvl2/further.png',
        'far': 'assets/backgrounds/lvl2/far.png',
        'clouds': 'assets/backgrounds/lvl2/clouds.png',
        'background_color': (171, 106, 140),
        'y_adjust': [0,0,0,0,0]
    }
}


levels = {
    0: level_0,  # test level
	1: level_1,
	2: level_2,
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
        self.stomp_pickup_fx = pygame.mixer.Sound('assets/sound/objects/health_pickup.wav')
        self.mana_pickup_fx = pygame.mixer.Sound('assets/sound/objects/health_pickup.wav')

        # Game music
        if level == 2 or level == 1 or level == 0:
            self.music = pygame.mixer.music
            self.music.load("assets/music/Hidden-Agenda.mp3")
            pygame.mixer.music.set_volume(0.3)
