import pygame
import pickle
import glob
import re
import logging
import math

from csv import reader

from settings import *

# --- Draw on screen ---
def draw_text(text, surface, font, text_col, x, y)-> None:
    """ Output text on screen """
    img = font.render(text, True, text_col)
    surface.blit(img, (x, y))

# -- Fades to a specific color
def fade_to_color(color: pygame.color.Color) -> None:
    # Fades to color (and pauses game while doing so!)
    
    screen = pygame.display.get_surface()
    rect = screen.get_rect()
    rectsurf = pygame.Surface(rect.size,pygame.SRCALPHA)
    color.a = 1
    for _ in range(0,255):
        pygame.time.wait(1)
        rectsurf.fill(color)
        screen.blit(rectsurf,(0,0))
        pygame.display.update()

# --- Import CSV data ---
def import_csv_layout(path :str) -> list:
    # Reads the map CSV files
    terrain_map = []
    with open (path) as map:
        level = reader(map, delimiter = ',')
        for row in level:
            terrain_map.append(list(row))
    return terrain_map
    
# --- Reads all tiles of a certain category, in numerical order, and returns list
def import_tile_graphics(path :str) -> list:
    tiles = []
    
    tile_files = glob.glob(path, recursive=False)

    # sort files by numer, meaning 10.png comes after 9.png, not alphabetically
    tile_files.sort(key=lambda var:[int(x) if x.isdigit() else x for x in re.findall(r'\D|\D+', var)])

    for filename in tile_files:  # read tile files sorted by name
        tiles.append(pygame.image.load(filename).convert_alpha())
   
    return tiles

# --- Reads all tiles of a certain category, in numerical order, and returns list
def import_tile_sheet_graphics(ss_file :str) -> list:
    """ Import tiles from a tilset file - calculating row and columns based on size, given TILE_SIZE """
    from animation import SpriteSheet

    tiles = []
    ss_image = pygame.image.load(ss_file).convert_alpha()
    ss_tile_rows = int(ss_image.get_height() / TILE_SIZE)  # get number of columns
    ss_tile_cols = int(ss_image.get_width() / TILE_SIZE)  # get number of tiles in row

    tiles_terrain_ss = SpriteSheet(ss_image, TILE_SIZE, TILE_SIZE, 1)

    for row in range(ss_tile_rows):
        for column in range(ss_tile_cols):
            tiles.append(tiles_terrain_ss.get_image(row, column))  # row 0, as it's all in one row

    logging.debug(f'Loaded {ss_file}, containing {ss_tile_cols} columns of sprites in {ss_tile_rows} rows')

    return tiles

# --- Load high scores ---
def load_high_score() -> int:
    """ Load high score from file """
    with open('highscore.dat', 'rb') as high_score_file:
        try:
            high_score = pickle.load(high_score_file)
        except EOFError:  # In case file does not exist with valid high score already
            return(0)
    return(high_score)

# --- Save high score
def save_high_score(high_score :int) -> None:
    """ Save high score to file """
    with open('highscore.dat', 'wb') as save_file:
        pickle.dump(high_score, save_file)    

# --- Produces list of sine wave y values
def sine_wave(points=100)-> list:
    """ Produces the points in a sine wave
        Values range between 0 and 100, with max value of 1 in the middle and 0 at both ends of the list
    """
    point_list = [] * points

    # Define the maximum amplitude of the wave
    amplitude = 50

    # Define the start and end points along the x-axis
    start = math.pi /2
    end = (5 * math.pi /2) 

    # Define the step size for each point along the x-axis
    step = (end - start) / points

    # Calculate the x and y coordinates for each point
    for i in range(points):
        x = start + i * step
        y = amplitude * math.sin(x) + 150

        point_list.append(1-(y-100)/100)

    return point_list
