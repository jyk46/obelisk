#=========================================================================
# healthtextbox.py
#=========================================================================
# Extended text box to display health below names.

import pygame, sys, os
from pygame.locals import *

import properties
import utils
import textbox

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class HealthTextBox( textbox.TextBox ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, offset_x, offset_y, size, color ):

    textbox.TextBox.__init__( self, width, height, pos_x, pos_y, offset_x, offset_y, size, color )

    self.max_matrix     = []
    self.current_matrix = []

  # Update graphics with health bars as well

  def update( self, text_matrix=[['']], health_matrix=None ):

    textbox.TextBox.update( self, text_matrix )

    # Exit if no health matrix is specified

    if health_matrix == None:
      return

    # Pair health bars with respective survivor names

    self.max_matrix     = []
    self.current_matrix = []

    for text_col, health_col in zip( self.surface_matrix, health_matrix ):

      max_col     = []
      current_col = []

      for text, health in zip( text_col, health_col ):

        # Adjust survivor name position to give health bar some room

        text[1].move_ip( 0, -2 )

        # Create max health bar overlay

        max_surface      = pygame.Surface( ( self.rect.width - 8, properties.HEALTH_HEIGHT ) )
        max_rect         = max_surface.get_rect()
        max_rect.topleft = text[1].left, text[1].bottom + 2
        max_surface.fill( utils.WHITE )

        max_col.append( ( max_surface, max_rect ) )

        # Create current health overlay

        current_width        = int( health * ( self.rect.width - 8 ) )
        current_surface      = pygame.Surface( ( current_width, properties.HEALTH_HEIGHT ) )
        current_rect         = current_surface.get_rect()
        current_rect.topleft = text[1].left, text[1].bottom + 2

        if health >= 0.67:
          current_surface.fill( utils.GREEN )
        elif health >= 0.33:
          current_surface.fill( utils.YELLOW )
        else:
          current_surface.fill( utils.RED )

        current_col.append( ( current_surface, current_rect ) )

      # Add health bar surfaces to matrix arrays

      self.max_matrix.append( max_col )
      self.current_matrix.append( current_col )

  # Draw health bars with text

  def draw_text( self ):

    rect_updates = textbox.TextBox.draw_text( self )

    for max_col in self.max_matrix:
      for surface, rect in max_col:
        rect_updates += [ self.image.blit( surface, rect ) ]

    for current_col in self.current_matrix:
      for surface, rect in current_col:
        rect_updates += [ self.image.blit( surface, rect ) ]

    return rect_updates
