
# Player and monster state constants
IDLE = 0
WALKING = 1
JUMPING = 2
STOMPING = 3
ATTACKING = 4
CASTING = 5
DYING = 6
DEAD = 7

# Game state constants
GS_WELCOME = 0
GS_PLAYING = 1
GS_GAME_OVER = 2
GS_LEVEL_COMPLETE = 3
GS_QUIT = 5
GS_MAP_SCREEN = 6

# Color contants
WHITE    = (255, 255, 255)
BLACK    = (  0,   0,   0)
RED      = (255,   0,   0)
DARKGRAY = ( 20,  20,  20)

# General constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 960

# Pixels available is a quarter of that: 480x240, which is the native resolution

# Derived values for scaling
TILE_SIZE = 32  # x and y native resolution of standard tiles
TILE_SIZE_SCREEN = SCREEN_WIDTH // TILE_SIZE  # 60 tiles wide, 30 tiles high, with a TILE_SIZE of 32

LEVEL_WIDTH = 4
GRAVITY = 0.5
MAX_PLATFORMS = 10
JUMP_HEIGHT = 15
H_SCROLL_THRESHOLD = 400
V_SCROLL_THRESHOLD = 200     
ROWS = 16  # the number of rows we can see on screen at once
MAX_COLS = 250  # mac columns in the map 
MAX_ROWS = 32  # max rows in map (we can scroll)


SCALE_FACTOR = 1
TILE_TYPES = 18
ANIMATION_TYPES = 3
OBJECT_TYPES = 9
WALKING_SPEED = 5
ATTACK_SPEED = 1  # UNUSED
PLAYER_HEALTH = 3000
PLAYER_STOMP = 5  # monsters to kill before stop recharges
STOMP_SPEED = 50
MUSIC_ON = True
SOUNDS_ON = True
FIRST_LEVEL = 1  # where to start

# Debug settings
DEBUG_HITBOXES = False