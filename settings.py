
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

# Color contants
WHITE    = (255, 255, 255)
BLACK    = (  0,   0,   0)
RED      = (255,   0,   0)
DARKGRAY = ( 20,  20,  20)

# General constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
LEVEL_WIDTH = 4
GRAVITY = 0.5
MAX_PLATFORMS = 10
JUMP_HEIGHT = 15
SCROLL_THRESHOLD = 400
ROWS = 16
MAX_COLS = 150
TILE_SIZE = 1080 // 16  #  67 pixels on that resolution
TILE_TYPES = 18
ANIMATION_TYPES = 3
OBJECT_TYPES = 9
WALKING_SPEED = 5
ATTACK_SPEED = 1  # UNUSED
PLAYER_HEALTH = 1000
PLAYER_STOMP = 10  # monsters to kill before stop recharges
STOMP_SPEED = 50

# Debug settings
DEBUG_HITBOXES = False