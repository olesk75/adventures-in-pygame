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
        self.active = False  # Determines if we're actually updating the animation counter 
        for frame in range(frames):
            self.sprites.append(sprite_sheet.get_sprite(row, frame))
        
        self.anim_counter = 0
        self.start_ticks = pygame.time.get_ticks()
        
    def image(self, repeat=True):
        sprite = self.sprites[self.anim_counter]
        self.repeat = repeat
        self.elapsed = pygame.time.get_ticks() - self.start_ticks
        if self.elapsed > self.speed: # animate every half second
            if self.active == True:
                self.anim_counter += 1
            if self.anim_counter >= len(self.sprites) - 1 and self.repeat == True:
                self.anim_counter = 0
            self.start_ticks = pygame.time.get_ticks()  # reset tick counter

        return sprite

    # Scale override is non-funtional
    def show_anim(self, screen, scale_override=False):
        self.screen = screen
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
            sprite = picture = pygame.transform.scale(sprite, (sprite_width, sprite_height)).convert_alpha()
            self.screen.blit(sprite, (frame_x + n * sprite_width, frame_y))  # draw sprites horisontally
            self.screen.blit(sprite, (frame_x, frame_y + n * sprite_height))
            n += 1

            

# Adds sprites on one long array
class StaticImage():
    def __init__(self, sprite_sheet, rows, columns):
        super().__init__()
        self.rows = rows
        self.columns = columns
        self.sprites = []
        for column in range(self.columns):
            for row in range(self.rows):
                self.sprites.append(sprite_sheet.get_sprite(column, row))
        
    def image(self, number):
        sprite = self.sprites[number]
        return sprite
