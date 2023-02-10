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
    'terrain_ts': 'assets/tile/tilesets/terrain-tileset-mountain-16x16.png',
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
    'sloping_tiles': {  # all the tiles that are non-flat (which the player can walk on)
        'down_in_1': [6],  # the steepest, gets down in one tile (45 degree)
        'down_in_2': [20,21],
        'up_in_1': [7],
        'up_in_2': [22,23],
    },  
    'moving_horiz': [27],  #  moving platforms
    'moving_vert': [[3,11,19]],  # bobbing platforms (in one group)
    'music': None  # TODO: move music here
}

level_1 = {
    'size_x': 250,
    'size_y': 15,
    'pos_terrain': 'lvl/lvl 1 - mountains/level1_terrain.csv',
    'pos_decorations': 'lvl/lvl 1 - mountains/level1_decorations.csv',
    'pos_hazards':  'lvl/lvl 1 - mountains/level1_hazards.csv',
    'pos_pickups': 'lvl/lvl 1 - mountains/level1_pickups.csv',
    'pos_triggered_objects': 'lvl/lvl 1 - mountains/level1_triggered_objects.csv',
    'pos_monsters': 'lvl/lvl 1 - mountains/level1_monsters.csv',
    'pos_player': 'lvl/lvl 1 - mountains/level1_player.csv',
    'environmental_effect': None,
    #'terrain_ts': 'assets/tile/tilesets/terrain-tileset-mountain-16x16.png',
    'terrain_ts': 'assets/tile/tilesets/mountain-tileset.png',
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
    'sloping_tiles': {  # all the tiles that are non-flat (which the player can walk on)
        'down_in_1': [6],  # the steepest, gets down in one tile (45 degree)
        'down_in_2': [20,21],
        'up_in_1': [7],
        'up_in_2': [22,23],
    },  
    'moving_horiz': [27],  #  moving platforms
    'moving_vert': [[3,11,19]],  # bobbing platforms (in one group)
    'music': None  # TODO: move music here
}

level_2 = {
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
    'terrain_ts': 'assets/tile/tilesets/mountain-tileset.png',
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
    'sloping_tiles': {  # all the tiles that are non-flat (which the player can walk on)
        'down_in_1': [6],  # the steepest, gets down in one tile (45 degree)
        'down_in_2': [20,21],
        'up_in_1': [7],
        'up_in_2': [22,23],
    },  
    'moving_horiz': [27],  #  moving platforms
    'moving_vert': [[3,11,19]],  # bobbing platforms (in one group)
    'music': None  # TODO: move music here
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
