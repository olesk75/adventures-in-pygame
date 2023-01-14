import pygame
import csv
from typing import NamedTuple
from game_data import MonsterAI
from game_data import monsters


# Game variables in a named tuple (new in Python 3.6)
class WorldData(NamedTuple):
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
    OBJECT_TYPES: int

class GameTile(pygame.sprite.Sprite):
    """
    Customized Sprite class which allows update with scroll value, which will be triggerd by spritegroup.update(scroll)
    """
    def __init__(self):
        super().__init__()
        
    def update(self, scroll):
        # Moves the rectangle of this sprite 
        self.rect.x += scroll
        #print(f'scrolling {self.dx}, new x_pos: {self.rect.left}')

class GameWorld():
    """
    All non-background tiles in the game (not player, not mobs)
    world_data: 2D matrix of all objects in game

    We return sprite groups of all objects    

    """
    def __init__(self, game_data):
        
        self.data = game_data
        self.rows = self.data.MAX_COLS
        self.columns = self.data.ROWS
        self.tile_size = self.data.TILE_SIZE

        self.platforms = [[-1]*self.columns] * self.rows
        self.pickups = [[-1]*self.columns]*self.rows
        self.decor = [[-1]*self.columns]*self.rows
        self.platforms_sprite_group = pygame.sprite.Group()
        self.pickups_sprite_group = pygame.sprite.Group()
        self.decor_sprite_group = pygame.sprite.Group()

        self.monster_import_list = []  # here we put all monsters from tile map, their type, x, y and AI properties

    def load(self, level_file):
        self.level_file = level_file
        img_list = []

        for x in range(self.data.TILE_TYPES):
            img = pygame.image.load(f'assets/tile/{x}.png').convert_alpha()
            img = pygame.transform.scale(img, (self.data.TILE_SIZE, self.data.TILE_SIZE))
            img_list.append(img)

        # Load world data
    
        with open(self.level_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter = ',')
            for y, row in enumerate(reader):
                for x, tile in enumerate(row):
                    # For each tile we create a sprite and add to the relevant group
                    if int(tile) != -1:
                        if int(tile) < self.data.TILE_TYPES:  # -1 means empty
                            sprite = GameTile()  # we must initialize every time, or we're only updating the same sprite over and over
                            sprite.image = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)  # Empty image with space for tiles
                            sprite.image.blit(img_list[int(tile)], (0, 0))  # we blit the right image onto the surface from top left
                            sprite.rect = sprite.image.get_rect()  # we get the rect for the sprite
                            sprite.rect.x = x * self.tile_size # we correct the x pos
                            sprite.rect.y = y * self.tile_size # we correct the y pos

                            if int(tile) <= 8:  # platforms
                                self.platforms_sprite_group.add(sprite)
                                #print(f'Added platform sprite to group with x: {x} and y: {y} and tile: {tile}, which now containts {len(self.platforms_sprite_group.sprites())} sprites\n')  # DEBUG

                            elif int(tile) >= 9:  # TODO: simplify for now
                                #self.decor[x][y] = int(tile)
                                self.decor_sprite_group.add(sprite)
                        elif int(tile) < self.data.TILE_TYPES + self.data.OBJECT_TYPES:
                            obj_type = int(tile) - self.data.TILE_TYPES
                            monster_type = monsters[obj_type]
                            x_pos = x * self.tile_size
                            y_pos = y * self.tile_size
                            
                            self.monster_import_list.append({'monster': monster_type, 'x': x_pos, 'y': y_pos, 'ai': MonsterAI(monster_type)})

        return(self.platforms_sprite_group, self.pickups_sprite_group, self.decor_sprite_group, self.monster_import_list)
