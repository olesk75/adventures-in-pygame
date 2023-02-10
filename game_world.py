"""
WorldData (dataclass)               : basic world information
GameTile (Sprite class)             : the background tiles, including platforms
GameTileAnimation (GameTile class)  : animated background tiles (flames, torches etc.)
GamePanel(class)                    : contans the player information for the screen - score, health etc.
"""


import pygame
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
    H_SCROLL_THRESHOLD: int
    ROWS: int
    MAX_COLS: int
    MAX_ROWS: int
    TILE_SIZE_SCREEN: int
    TILE_TYPES: int
    ANIMATION_TYPES: int
    OBJECT_TYPES: int

class GameTile(pygame.sprite.Sprite):
    """
    Customized Sprite class which allows update with scroll value, which will be triggerd by spritegroup.update(scroll)
    """
    def __init__(self) -> None:
        super().__init__()
        
    def update(self, h_scroll, v_scroll) -> None:
        # Moves the rectangle of this sprite 
        self.rect.x += h_scroll
        self.rect.y += v_scroll

class GameTileAnimation(GameTile):
    """
    Customized Sprite class which allows update with scroll value, which will be triggerd by spritegroup.update(scroll)
    """
    def __init__(self, animation) -> None:
        super().__init__()
        self.animation = animation
        self.X_CENTER = self.animation.image().get_width() // 2
        self.Y_CENTER = self.animation.image().get_height() // 2
        self.sprites = self.animation.sprites
        self.animation.active = True
        
    def update(self, h_scroll, v_scroll) -> None:
        # Moves the rectangle of this sprite 
        self.rect.x += h_scroll
        self.rect.y += v_scroll

        #print(f'scrolling {self.dx}, new x_pos: {self.rect.left}')
    
    def draw(self, screen) -> None:
        self.image = self.animation.image().convert_alpha()
        screen.blit(self.image, (self.rect.x, self.rect.y))