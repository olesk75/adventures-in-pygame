import pygame
import logging

# --- Imports sprite sheets for animatons
# SpriteSheet class
class SpriteSheet():
    def __init__(self, image, x_dim, y_dim, scale) -> None:
        self.image = image
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.scale = scale
       

    def get_image(self, row, frame) -> pygame.Surface:
        x_start = frame * self.x_dim
        y_start = row * self.y_dim

        image = pygame.Surface((self.x_dim, self.y_dim), pygame.SRCALPHA).convert_alpha()  # empty surface with alpha
        image.blit(self.image, (0,0), (x_start, y_start, self.x_dim, self.y_dim))  # Copy part of sheet on top of empty image
        image = pygame.transform.scale(image, (self.x_dim * self.scale, self.y_dim * self.scale))
        #image.set_colorkey(self.transp_color)
        
        return image



# Animation class
class Animation():
    """ Class which reads the sprite sheet and animates the images in sprites 
        Reads single rwo from the sprite sheet and builds list of images which
        is iterated through (and looped over if repeat==True)
    """

    # Getting a sprite sheet
    def __init__(self, sprite_sheet: pygame.Surface, row:int=0, frames:int=1, speed:int=100, repeat:bool=True) -> None:
        self.ss = sprite_sheet
        self.row = row
        self.frames = frames
        self.sprites = []
        self.speed = speed   # Effecticely the ms we wait for next animation frame - bigger means slower
        self.active = False  # We begin in the stopped state
        self.repeat = repeat  # should we run forever or just once

        [self.sprites.append(self.ss.get_image(row, frame)) for frame in range(frames)]
        
        self.frame_number = 0 
        self.on_last_frame = False  # gives way to check if animation is done (and ready to start over)
        self.last_run = 0
        self.repeat_start = 0  # ticks of time when we're done with one animation frame cycle
        self.first_done = False  # True when done one cycle of frames
        
    def get_image(self, repeat_delay=0) -> pygame.Surface:
        # Returns the next image in the animation when active
        now = pygame.time.get_ticks()
        time_since_last = now - self.last_run  # ticks since last run

        if now > self.repeat_start + repeat_delay:

            if self.active == True and time_since_last > self.speed:  # time for a new frame
                self.frame_number += 1
                
                if self.frame_number == self.frames -1:  # on the last frame
                    self.on_last_frame = True
                else:
                    self.on_last_frame = False

                if self.frame_number == self.frames:  # past the last frame
                    if not self.repeat:  # we disable if we're not repeating after first iteration
                        self.active = False 
                        self.frame_number -= 1   # we show the last frame forever
                    else:
                        self.frame_number = 0 
                        self.first_done = True
                        self.repeat_start = now
                    
                self.last_run = now
        try:
            image = self.sprites[self.frame_number].convert_alpha()
        except IndexError:
            logging.error(f'INDEX ERROR: unable to get frame (frame_number) {self.frame_number} from sprite sheet {self.ss}')
            exit(1)
        return image

    def start_over(self) -> None:
        self.frame_number = 0 