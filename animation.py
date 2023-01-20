import pygame

# Animation class
class Animation():
    # Getting a sprite sheet
    def __init__(self, sprite_sheet, row, frames, speed):
        self.ss = sprite_sheet
        self.row = row
        self.frames = frames
        self.sprites = []
        self.speed = speed   # Effecticely the ms we wait for next animation frame - bigger means slower
        self.active = False  # We begin in the stopped state

        [self.sprites.append(sprite_sheet.get_image(row, frame)) for frame in range(frames)]
        
        self.anim_counter = 0
        self.last_run = 0
        self.repeat_start = 0  # ticks when we're done with one animation frame cycle
        self.first_done = False  # True when done one cycle of frames
        
    def get_image(self, repeat_delay=0):
        now = pygame.time.get_ticks()
        time_since_last = now - self.last_run  # ticks since last run
        if now > self.repeat_start + repeat_delay:

            if self.active == True and time_since_last > self.speed:  # time for a new frame
                self.anim_counter += 1
                if self.anim_counter == len(self.sprites):    
                    self.anim_counter = 0
                    self.first_done = True
                    self.repeat_start = now

                self.last_run = now
        
        image = self.sprites[self.anim_counter].convert_alpha()
        return image


    # Scale override is non-funtional
    def _show_anim(self, scale_override=False):
        """This function is only to display every frame of an animation in a grid on screen for testing """
        self.screen = pygame.display.get_surface()
        if scale_override:
            scale = scale_override
        else:
            scale = self.ss.scale
        frame_x = 10  # frames around all sprites to get space between sprites and screen edge
        frame_y = 10
        sprite_width = self.ss.x_dim * scale
        sprite_height = self.ss.y_dim * scale
        border_radius = 1
        GRAY = (75,75,75)

        n = 0
        for sprite in self.sprites:
            pygame.draw.rect(self.screen, GRAY, (frame_x + n * sprite_width, frame_y, sprite_width, sprite_height), border_radius)
            pygame.draw.rect(self.screen, GRAY, (frame_x, frame_y + n * sprite_height , sprite_width, sprite_height), border_radius)
            sprite  = pygame.transform.scale(sprite, (sprite_width, sprite_height)).convert_alpha()
            self.screen.blit(sprite, (frame_x + n * sprite_width, frame_y))  # draw sprites horisontally
            self.screen.blit(sprite, (frame_x, frame_y + n * sprite_height))
            n += 1
