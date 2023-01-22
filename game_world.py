"""
WorldData (dataclass)               : basic world information
GameTile (Sprite class)             : the background tiles, including platforms
GameTileAnimation (GameTile class)  : animated background tiles (flames, torches etc.)
GameWorld (class)                   : contains sprite groups and lists of sprites loaded from the level file
GamePanel(class)                    : contans the player information for the screen - score, health etc.
"""


import pygame
import csv
import random
from monster_data import MonsterData
from monster_data import monsters
from dataclasses import dataclass


@dataclass
class GameData:
    SCREEN_WIDTH: int
    SCREEN_HEIGHT: int
    LEVEL_WIDTH: int
    GRAVITY: int
    MAX_PLATFORMS: int
    JUMP_HEIGHT: int
    PLAYER_BOUNCING: bool
    SCROLL_THRESHOLD: int
    ROWS: int
    MAX_COLS: int
    TILE_SIZE: int
    TILE_TYPES: int
    ANIMATION_TYPES: int
    OBJECT_TYPES: int

class GameTile(pygame.sprite.Sprite):
    """
    Customized Sprite class which allows update with scroll value, which will be triggerd by spritegroup.update(scroll)
    """
    def __init__(self):
        super().__init__()
        
    def update(self, scroll) -> None:
        # Moves the rectangle of this sprite 
        self.rect.x += scroll

class GameTileAnimation(GameTile):
    """
    Customized Sprite class which allows update with scroll value, which will be triggerd by spritegroup.update(scroll)
    """
    def __init__(self, animation):
        super().__init__()
        self.animation = animation
        self.X_CENTER = self.animation.get_image().get_width() // 2
        self.Y_CENTER = self.animation.get_image().get_height() // 2
        self.sprites = self.animation.sprites
        self.animation.active = True
        
    def update(self, scroll) -> None:
        # Moves the rectangle of this sprite 
        self.rect.x += scroll
        self.image = self.animation.get_image().convert_alpha()


class GameWorld():
    """
    All non-background tiles in the game (not player, not mobs)
    world_data: 2D matrix of all objects in game

    We build sprite groups of all objects    

    """
    def __init__(self, game_data) -> None:

        self.tile_types = {
            'platforms': [0,1,2,3,4,5,6,7,8],
            'objects': [9,10,11,12,13,14,15],
            'animated_objects': [16,17],
            'hazards': [18,19,20],
            'monsters': [21,22,23,24,25,26,27],
            'trigg_anims': [28,29,30]
        }
        
        self.data = game_data
        self.rows = self.data.MAX_COLS
        self.columns = self.data.ROWS
        self.tile_size = self.data.TILE_SIZE

        self.platforms = [[-1]*self.columns] * self.rows
        self.pickups = [[-1]*self.columns]*self.rows
        self.decor = [[-1]*self.columns]*self.rows
        self.platforms_sprite_group = pygame.sprite.Group()
        self.decor_sprite_group = pygame.sprite.Group()
        self.anim_objects_sprite_group = pygame.sprite.Group()
        self.hazards_sprite_group = pygame.sprite.Group()
        self.anim_spells_sprite_group = pygame.sprite.Group()
        self.trigger_anim_sprite_group = pygame.sprite.Group()
        self.triggered_anim_list = []  # we trigger these when touched


        self.monster_import_list = []  # here we put all monsters from tile map, their type, x, y and AI properties

    def load(self, level_file) -> None:
        self.level_file = level_file
        img_list = []

        # We null the list and sprite groups to avoid dupes when starting a new game without quitting
        self.monster_import_list = []
        self.platforms_sprite_group.empty()
        self.decor_sprite_group.empty()

        for x in range(sum([len(self.tile_types[x]) for x in self.tile_types if isinstance(self.tile_types[x], list)])):
            img = pygame.image.load(f'assets/tile/{x}.png').convert_alpha()
            img = pygame.transform.scale(img, (self.data.TILE_SIZE, self.data.TILE_SIZE))
            img_list.append(img)

        
        from animation_data import animations  # we do this late, as we need to have display() up first

        with open(self.level_file, newline='') as csvfile:
            """
            Start loading the world from level file, creating sprites for each tile if value is not -1
            All sprites are then added to a SpriteGroup, which the main game loop calls .update() and .draw() on
            """
            reader = csv.reader(csvfile, delimiter = ',')
            for y, row in enumerate(reader):
                for x, tile in enumerate(row):
                    if int(tile) != -1:  # -1 is empty
                        if int(tile) in self.tile_types['platforms'] or int(tile) in self.tile_types['objects']:
                            """ Platform and object tiles both - must be 32x32 as we do no scaling here """
                            sprite = GameTile()
                            sprite.image = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)  # empty surface
                            sprite.image.blit(img_list[int(tile)], (0, 0)) 
                            sprite.rect = sprite.image.get_rect() 
                            sprite.rect.x = x * self.tile_size 
                            sprite.rect.y = y * self.tile_size

                            if int(tile) in self.tile_types['platforms']:
                                # ---> Platforms 
                                self.platforms_sprite_group.add(sprite)
                            elif int(tile) in self.tile_types['objects']:
                                # ---> Decor (rocks, grass, boxes etc.
                                self.decor_sprite_group.add(sprite)

                        if int(tile) in self.tile_types['animated_objects'] or int(tile) in self.tile_types['hazards']:
                            """ Animated objects - can be arbitrary size as we scale the sprites """
                            # ---> Animated objects
                            if int(tile) == self.tile_types['animated_objects'][0]:  # health potion
                                animation = animations['objects']['health-potion']
                                hazard = False
                            
                            # --->  Animated hazards
                            if int(tile) == self.tile_types['hazards'][0]:  # fire
                                animation = animations['fire']['fire-hazard']
                                hazard = True    
                            elif int(tile) == self.tile_types['hazards'][1]:  # spikes
                                animation = animations['spikes']['spike-trap'] 
                                hazard = True                            
                            else:
                                # --->  Animated tiles (fires, birds etc.) 
                                pass

                            sprite = GameTileAnimation(animation)  # -> GameTile -> pygame.sprite.Sprite
                            sprite.animation.anim_counter = random.randint(0, sprite.animation.frames -1)
                            image_height = sprite.sprites[0].get_height()  # height of the images in the animation
                            image_width = sprite.sprites[0].get_width()  # height of the images in the animation
                            sprite.image = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)  # Empty image with space for tiles
                            sprite.image.blit(img_list[int(tile)], (0, 0))  # we blit the right image onto the surface from top left
                            sprite.rect = sprite.image.get_rect()  # we get the rect for the sprite
                            sprite.rect.x = x * self.tile_size - (image_width - self.tile_size) / 2 # we correct the x pos by removeing the part of the image that's larger than the tile
                            sprite.rect.y = ((y + 1)  * self.tile_size) - image_height # we correct the y pos
                            if hazard:
                                self.hazards_sprite_group.add(sprite)
                            else:
                                self.anim_objects_sprite_group.add(sprite)

                        if int(tile) in self.tile_types['monsters']:
                            """ Monsters """
                            obj_type = self.tile_types['monsters'][int(tile)-21]-21
                            monster_type = monsters[obj_type]
                            x_pos = x * self.tile_size
                            y_pos = y * self.tile_size
                            
                            self.monster_import_list.append({'monster': monster_type, 'x': x_pos, 'y': y_pos, 'ai': MonsterData(monster_type)})

                        if int(tile) in self.tile_types['trigg_anims']:
                            """ Triggered animations """
                            if int(tile) == self.tile_types['trigg_anims'][2]: 
                                animation = animations['doors']['end-of-level'] 

                            sprite = GameTileAnimation(animation)  # -> GameTile -> pygame.sprite.Sprite
                            image_height = sprite.sprites[0].get_height()  # height of the images in the animation
                            image_width = sprite.sprites[0].get_width()  # height of the images in the animation
                            sprite.image = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)  # Empty image with space for tiles
                            sprite.image.blit(img_list[int(tile)], (0, 0))  # we blit the right image onto the surface from top left
                            sprite.rect = sprite.image.get_rect()  # we get the rect for the sprite
                            sprite.rect.x = x * self.tile_size - (image_width - self.tile_size) / 2 # we correct the x pos by removeing the part of the image that's larger than the tile
                            sprite.rect.y = ((y + 1)  * self.tile_size) - image_height # we correct the y pos

                            if sprite.animation == animations['doors']['end-of-level']:   # the last triggered animation is a door 
                                self.triggered_anim_list.append(['doors', sprite])
                                sprite.animation.active = False  # we trigger this in the main loop

                            self.trigger_anim_sprite_group.add(sprite)



