#=========================================================================
# properties.py
#=========================================================================
# Global game parameters.

#-------------------------------------------------------------------------
# Performance
#-------------------------------------------------------------------------

FPS = 30

#-------------------------------------------------------------------------
# Survivors
#-------------------------------------------------------------------------

NUM_START_SURVIVORS = 5

START_FOOD  = 20
START_WOOD  = 5
START_METAL = 2
START_AMMO  = 5

EXPEDITION_SPEED = 16

#-------------------------------------------------------------------------
# Map
#-------------------------------------------------------------------------

MAP_SIZE    = 32

TILE_WIDTH  = 32
TILE_HEIGHT = 32

MAP_WIDTH   = MAP_SIZE * TILE_WIDTH
MAP_HEIGHT  = MAP_SIZE * TILE_HEIGHT

SCROLL_WIDTH = 32
SCROLL_SPEED = 16

NUM_MOUNTAIN    = 4
NUM_SWAMP       = 2
NUM_JUNGLE      = 4
NUM_FACILITY    = 1
NUM_WRECKAGE    = 5
NUM_RITUAL_SITE = 4

MOUNTAIN_RATE    = 0.15
CAVE_RATE        = 0.30
SWAMP_RATE       = 0.20
JUNGLE_RATE      = 0.10
DEEP_JUNGLE_RATE = 0.25
FACILITY_RATE    = 0.25

#-------------------------------------------------------------------------
# Menu
#-------------------------------------------------------------------------

MENU_TEXT = [
 'EXPLORE',
 'SCAVENGE',
 'CRAFT',
 'REST',
 'STATUS',
]

MENU_OFFSET_X = 16
MENU_OFFSET_Y = 16
MENU_PADDING  = 4

MENU_WIDTH    = 128
MENU_HEIGHT   = 32

#-------------------------------------------------------------------------
# Dimensions
#-------------------------------------------------------------------------

WINDOW_HEIGHT  = 640

CAMERA_WIDTH   = 640
CAMERA_HEIGHT  = WINDOW_HEIGHT

ACTION_WIDTH   = 448
ACTION_HEIGHT  = 576

SIDEBAR_WIDTH  = 192
SIDEBAR_HEIGHT = WINDOW_HEIGHT

WINDOW_WIDTH   = CAMERA_WIDTH + SIDEBAR_WIDTH

#-------------------------------------------------------------------------
# Paths
#-------------------------------------------------------------------------

FONT_PATH    = 'fonts/'
DEFAULT_FONT = FONT_PATH + 'default.ttf'

TILE_PATH    = 'images/tiles/'
EXPD_PATH    = 'images/expedition/'
SIDEBAR_PATH = 'images/sidebar/'
BUTTON_PATH  = 'images/menu/menu_bar.png'
ACTION_PATH  = 'images/action/'