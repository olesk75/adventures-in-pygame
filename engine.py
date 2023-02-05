import pygame
import pickle
import glob
import re
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






