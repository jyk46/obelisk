#=========================================================================
# properties.py
#=========================================================================
# Global game parameters.

#-------------------------------------------------------------------------
# Performance
#-------------------------------------------------------------------------

FPS          = 20
SPS          = 4         # steps or animation frames per second
FRAME_SWITCH = FPS / SPS # number of frames to hold one animation frame

#-------------------------------------------------------------------------
# Survivors
#-------------------------------------------------------------------------

NUM_START_SURVIVORS = 4
NUM_MAP_SURVIVORS   = 20

START_FOOD  = 10
START_WOOD  = 5
START_METAL = 2
START_AMMO  = 5

EXPD_SPEED = 2

ATTRIBUTE_PROB = 0.25

RSRC_BONUS_MULT = 0.01
ITEM_BONUS_MULT = 0.01
RSRC_REDUC_RATE = 0.90

SCAVENGE_COST = 1
CRAFT_COST    = 2

SICK_HEAL_MULT = 0.5

HEALTH_WIDTH  = 200
HEALTH_HEIGHT = 4

DEFENSE_LIMIT  = 3
DEFENDER_LIMIT = 4

STARVE_RATE = 0.25

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

MOUNTAIN_RATE    = 0.2 #0.15
CAVE_RATE        = 0.4 #0.30
SWAMP_RATE       = 0.3 #0.20
JUNGLE_RATE      = 0.2 #0.10
DEEP_JUNGLE_RATE = 0.3 #0.25
FACILITY_RATE    = 0.4 #0.25

NIGHT_ALPHA = 160

#-------------------------------------------------------------------------
# Menu
#-------------------------------------------------------------------------

DAY_MENU_TEXT = [
  'EXPLORE',
  'SCAVENGE',
  'CRAFT',
  'REST',
  'STATUS',
]

NIGHT_MENU_TEXT = [
  'DEFEND',
  'STATUS',
]

MENU_OFFSET_X = 16
MENU_OFFSET_Y = 16
MENU_PADDING  = 4

MENU_WIDTH    = 128
MENU_HEIGHT   = 32

#-------------------------------------------------------------------------
# Text
#-------------------------------------------------------------------------

TEXT_Y_OFFSET = 3
TEXT_X_OFFSET = 4
TEXT_HEIGHT   = 32

SCROLL_HEIGHT = 16

#-------------------------------------------------------------------------
# Dimensions
#-------------------------------------------------------------------------

WINDOW_HEIGHT  = 640

CAMERA_WIDTH   = 640
CAMERA_HEIGHT  = WINDOW_HEIGHT

ACTION_WIDTH   = 464
ACTION_HEIGHT  = 576

ACTION_INFO_WIDTH  = 432
ACTION_INFO_HEIGHT = 160

ACTION_SUB_WIDTH  = 208
ACTION_SUB_HEIGHT = 288

COST_WIDTH  = 36
COST_HEIGHT = 36

EVENT_WIDTH  = 448
EVENT_HEIGHT = 288

EVENT_SUB_WIDTH  = 416
EVENT_SUB_HEIGHT = 192

DEFEND_WIDTH  = 384
DEFEND_HEIGHT = 384

DEFEND_PIC_WIDTH  = 192
DEFEND_PIC_HEIGHT = 192

DEFEND_HIT_WIDTH  = 32
DEFEND_HIT_HEIGHT = 192

DEFEND_HIT_SPACE = 4

CARD_WIDTH  = 160
CARD_HEIGHT = 128

SIDEBAR_WIDTH  = 256
SIDEBAR_HEIGHT = WINDOW_HEIGHT

SIDEBAR_TILE_WIDTH  = 224
SIDEBAR_TILE_HEIGHT = 96

SIDEBAR_EXPD_WIDTH  = 224
SIDEBAR_EXPD_HEIGHT = 160

WINDOW_WIDTH = CAMERA_WIDTH + SIDEBAR_WIDTH

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
EVENT_PATH   = 'images/event/'
DEFEND_PATH  = 'images/defend/'
ENEMY_PATH   = 'images/enemy/'
BG_PATH      = 'images/bg/'
