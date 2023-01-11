import pygame

# Animation class
class Animation():
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
