#=========================================================================
# costbox.py
#=========================================================================
# Box overlay for selecting destination during exploration phase

import pygame, sys, os
from pygame.locals import *

import properties

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class CostBox:

  # Constructor

  def __init__( self ):

    # Member variable

    self.cost  = 0
    self.pos_x = 0
    self.pos_y = 0

    # Initialize image surface

    self.surface   = pygame.image.load( properties.EXPD_PATH + 'cost.png' )
    self.image     = self.surface.convert()
    self.rect      = self.image.get_rect()

    # Initialize font

    self.font      = pygame.font.Font( properties.DEFAULT_FONT, 14 )

  # Update graphics

  def update( self ):
    self.rect.bottomright = self.pos_x, self.pos_y

  # Aggregate draw function

  def draw( self, surface ):

    rect_updates = []

    # Only draw cost box if cursor is above valid tile

    if self.cost > 0:

      # Draw cost onto background

      self.image        = self.surface.convert()
      cost_surface      = self.font.render( str( self.cost ), 1, (255,255,255) )
      cost_rect         = cost_surface.get_rect()
      cost_rect.topleft = 12, 4
      rect_updates     += [ self.image.blit( cost_surface, cost_rect ) ]

      # Draw cost box onto main surface at mouse pointer tip

      rect_updates += [ surface.blit( self.image, self.rect ) ]

    return rect_updates
