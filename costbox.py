#=========================================================================
# costbox.py
#=========================================================================
# Box overlay for selecting destination during exploration phase

import pygame, sys, os
from pygame.locals import *

import properties
import utils

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

    self.surface = pygame.image.load( properties.EXPD_PATH + 'cost.png' )
    self.image   = self.surface.convert()
    self.rect    = self.image.get_rect()

  # Update graphics

  def update( self ):

    self.rect.bottomright = self.pos_x, self.pos_y

  # Draw graphics

  def draw( self, surface ):

    rect_updates = []

    # Only draw cost box if cursor is above valid tile

    if self.cost > 0:

      # Reset background

      self.image = self.surface.convert()

      # Draw cost onto background

      rect_updates += utils.draw_text_center( self.image, str( self.cost ), 14, utils.WHITE )

      # Draw cost box onto main surface at mouse pointer tip

      rect_updates += [ surface.blit( self.image, self.rect ) ]

    return rect_updates
