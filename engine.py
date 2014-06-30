#=========================================================================
# engine.py
#=========================================================================
# Main engine for the game, contains logic for day/night phases and
# various actions: explore, craft/repair, heal, rest, camp, info.

import pygame, sys, os
from pygame.locals import *

import mapgen
import tile
import enemy
import survivor
import attribute
import inventory
import item

#-------------------------------------------------------------------------
# Properties
#-------------------------------------------------------------------------

PHASE_DAY_PLAN, PHASE_DAY_EXEC, PHASE_NIGHT_PLAN, PHASE_NIGHT_EXEC = range( 4 )

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Engine:

  # Constructor

  def __init__( self, map ):

    self.screen = pygame.display.get_surface()
    self.map    = map
    self.phase  = PHASE_DAY_PLAN
    self.cam_x  = 0
    self.cam_y  = 0

  # Draw map

  def draw_map( self ):

    self.background = pygame.Surface( ( Properties.CAM_WIDTH, Properties.CAM_HEIGHT ) )

    for i in range( properties.MAP_SIZE ):
      for j in range( properties.MAP_SIZE ):
        self.background.blit( map[i][j].image, map[i][j].img_rect )

    self.screen.blit( self.background, (0,0) )

  # Start game engine

  def start( self ):

    # Draw map

    self.draw_map()
    pygame.display.flip()

    # Initialize clock

    clock = pygame.time.Clock()

    # Main game loop

    while True:

      # Update graphics

      self.sprite_group.clear( self.screen, self.background )
      update_screen = self.sprite_group.draw( self.screen )
      pygame.display.update( update_screen )
      self.sprite_group.update()

      # Increment clock

      clock.tick(8)
