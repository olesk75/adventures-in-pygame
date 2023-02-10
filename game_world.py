"""
WorldData (dataclass)               : basic world information
GameTile (Sprite class)             : the background tiles, including platforms
GameTileAnimation (GameTile class)  : animated background tiles (flames, torches etc.)
GamePanel(class)                    : contans the player information for the screen - score, health etc.
"""


import pygame

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