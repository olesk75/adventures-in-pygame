import pygame
from typing import NamedTuple

# Game variables in a named tuple (new in Python 3.6)
class WorldData(NamedTuple):
    GRAVITY: int
    TOT_WIDTH: int
    MAX_PLATFORMS: int
    JUMP_HEIGHT: int
    PLAYER_BOUNCING: bool
    SCROLL_THRESHOLD: int

# Game variables in a named tuple (new in Python 3.6)
class PlatformLocations(NamedTuple):
    x: int
    y: int
    width: int

class TiledPlatform(pygame.sprite.Sprite):
    """
    Since we inheritate from the Sprite class, draw etc. is also inherited
    """
    def __init__(self, x, y, tile_image, width):
        super().__init__()

        self.tile_size = 32
        self.image = pygame.Surface((self.tile_size * width, self.tile_size), pygame.SRCALPHA)  # Empty image with space for tiles

        for n in range(width):
            self.image.blit(tile_image, (n * self.tile_size, 0))

        self.rect = self.image.get_rect()
    
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        # update platform's vert pos
        self.rect.x += scroll

        # check if platform is off screen
        #if self.rect.top > pygame.display.get_window_size()[1]:
        #    self.kill()

class GameItem(pygame.sprite.Sprite):
    """
    Since we inheritate from the Sprite class, draw etc. is also inherited
    """
    def __init__(self, x, y, tile_image):
        super().__init__()
        self.sprite_size = 50
        self.image = pygame.transform.scale(tile_image, (self.sprite_size, self.sprite_size)).convert_alpha()  # 32x32px  tall hardcoded
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        # update platform's vert pos
        self.rect.x += scroll

        # check if platform is off screen
        #if self.rect.top > pygame.display.get_window_size()[1]:
        #    self.kill()

    def die(self):
        self.kill()