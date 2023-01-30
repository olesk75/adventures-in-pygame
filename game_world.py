"""
WorldData (dataclass)               : basic world information
GameTile (Sprite class)             : the background tiles, including platforms
GameTileAnimation (GameTile class)  : animated background tiles (flames, torches etc.)
GameWorld (class)                   : contains sprite groups and lists of sprites loaded from the level file
GamePanel(class)                    : contans the player information for the screen - score, health etc.
"""


import pygame
import csv
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
        self.X_CENTER = self.animation.image().get_width() // 2
        self.Y_CENTER = self.animation.image().get_height() // 2
        self.sprites = self.animation.sprites
        self.animation.active = True
        
    def update(self, scroll) -> None:
        # Moves the rectangle of this sprite 
        self.rect.x += scroll
        #print(f'scrolling {self.dx}, new x_pos: {self.rect.left}')
    
    def draw(self, screen) -> None:
        self.image = self.animation.image().convert_alpha()
        screen.blit(self.image, (self.rect.x, self.rect.y))



class GameWorld():
    """
    All non-background tiles in the game (not player, not mobs)
    world_data: 2D matrix of all objects in game

    We build sprite groups of all objects    

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
        self.anim_objects_sprite_list = []  # we need custom draw method due to the animations for the underlying sprites, so list, not sprite group (we could override the group draw method)
        #self.anim_spells_sprite_list = []  # we need custom draw method due to the animations for the underlying sprites, so list, not sprite group (we could override the group draw method)
        self.anim_spells_sprite_group = pygame.sprite.Group()


        self.monster_import_list = []  # here we put all monsters from tile map, their type, x, y and AI properties

    def load(self, level_file) -> None:
        self.level_file = level_file
        img_list = []

        # We null the list and sprite groups to avoid dupes when starting a new game without quitting
        self.monster_import_list = []
        self.platforms_sprite_group.empty()
        self.pickups_sprite_group.empty()
        self.decor_sprite_group.empty()

        for x in range(self.data.TILE_TYPES + self.data.ANIMATION_TYPES):
            img = pygame.image.load(f'assets/tile/{x}.png').convert_alpha()
            img = pygame.transform.scale(img, (self.data.TILE_SIZE, self.data.TILE_SIZE))
            img_list.append(img)

        
        from animation_data import animations  # we do this late, as we need to have display() up first

        with open(self.level_file, newline='') as csvfile:
            """
            Start loading the world from level file, adding all objects 
            """
            reader = csv.reader(csvfile, delimiter = ',')
            for y, row in enumerate(reader):
                for x, tile in enumerate(row):
                    # For each tile we create a sprite and add to the relevant group
                    if int(tile) != -1:
                        if int(tile) < self.data.TILE_TYPES:  # -1 means empty
                            """ Background tiles """
                            sprite = GameTile()  # we must initialize every time, or we're only updating the same sprite over and over
                            sprite.image = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)  # Empty image with space for tiles
                            sprite.image.blit(img_list[int(tile)], (0, 0))  # we blit the right image onto the surface from top left
                            sprite.rect = sprite.image.get_rect()  # we get the rect for the sprite
                            sprite.rect.x = x * self.tile_size # we correct the x pos
                            sprite.rect.y = y * self.tile_size # we correct the y pos

                            if int(tile) <= 8:
                                """ Platforms """
                                self.platforms_sprite_group.add(sprite)
                                #print(f'Added platform sprite to group with x: {x} and y: {y} and tile: {tile}, which now containts {len(self.platforms_sprite_group.sprites())} sprites\n')  # DEBUG

                            elif int(tile) >= 9:  # TODO simplify for now
                                """ Decor (rocks, grass, boxes etc. """
                                #self.decor[x][y] = int(tile)
                                self.decor_sprite_group.add(sprite)
                        
                        elif int(tile) < (self.data.ANIMATION_TYPES + self.data.TILE_TYPES):
                            """ Animated tiles (fires, birds etc.) """    
                            # SIMPLIFIED FOR NOW
                            if int(tile) - self.data.TILE_TYPES == 0:  # fire
                                animation = animations['fire']['fire-once']
                            sprite = GameTileAnimation(animation)  # -> GameTile -> pygame.sprite.Sprite
                            sprite.image = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)  # Empty image with space for tiles
                            sprite.image.blit(img_list[int(tile)], (0, 0))  # we blit the right image onto the surface from top left
                            sprite.rect = sprite.image.get_rect()  # we get the rect for the sprite
                            sprite.rect.x = x * self.tile_size # we correct the x pos
                            sprite.rect.y = y * self.tile_size # we correct the y pos
                            self.anim_objects_sprite_list.append(sprite)

                        else:
                            """ Monsters """
                            obj_type = int(tile) - (self.data.TILE_TYPES + self.data.ANIMATION_TYPES)
                            monster_type = monsters[obj_type]
                            x_pos = x * self.tile_size
                            y_pos = y * self.tile_size
                            
                            self.monster_import_list.append({'monster': monster_type, 'x': x_pos, 'y': y_pos, 'ai': MonsterData(monster_type)})


