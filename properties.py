#=========================================================================
# properties.py
#=========================================================================
# Global game parameters.

#-------------------------------------------------------------------------
# Performance
#-------------------------------------------------------------------------

FPS = 30

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
# Dimensions
#-------------------------------------------------------------------------

WINDOW_HEIGHT = 640

CAMERA_WIDTH  = 640
CAMERA_HEIGHT = WINDOW_HEIGHT

STATUS_WIDTH  = 200
STATUS_HEIGHT = WINDOW_HEIGHT

WINDOW_WIDTH  = CAMERA_WIDTH + STATUS_WIDTH

#-------------------------------------------------------------------------
# Paths
#-------------------------------------------------------------------------

FONT_PATH = 'fonts/'

TILE_PATH = 'images/tiles/'
EXPD_PATH = 'images/expedition/'
