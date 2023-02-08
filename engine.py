import pygame
import pickle
import glob
import re
import logging

from csv import reader

from settings import *

# --- Draw on screen ---
def draw_text(text, font, text_col, x, y)-> None:
    """ Output text on screen """
    img = font.render(text, True, text_col)
    pygame.display.get_surface().blit(img, (x, y))

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
    tile_files.sort(key=lambda var:[int(x) if x.isdigit() else x for x in re.findall(r'[^0-9]|[0-9]+', var)])

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



