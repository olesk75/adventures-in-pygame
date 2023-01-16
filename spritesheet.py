import pygame

# SpriteSheet class
class SpriteSheet():
    def __init__(self, image, x_dim, y_dim, transp_color, scale):
        self.image = image
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.scale = scale
        self.transp_color = transp_color

    def get_image(self, row, frame) -> pygame.Surface:
        x_start = frame * self.x_dim
        y_start = row * self.y_dim

        image = pygame.Surface((self.x_dim, self.y_dim)).convert_alpha()  # empty surface with alpha
        image.blit(self.image, (0,0), (x_start, y_start, self.x_dim, self.y_dim))  # Copy part of sheet on top of empty image
        image = pygame.transform.scale(image, (self.x_dim * self.scale, self.y_dim * self.scale))
        image.set_colorkey(self.transp_color)
        
        return image
