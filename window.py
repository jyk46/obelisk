#=========================================================================
# window.py
#=========================================================================
# Sprite class for holding separate windows on the main display.

import pygame, sys, os
from pygame.locals import *

import math
import properties

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Window:

  # Constructor

  def __init__( self, width, height, pos_x, pos_y ):

    self.surface      = pygame.Surface( ( width, height ) )
    self.image        = self.surface.convert()
    self.rect         = self.image.get_rect()
    self.rect.topleft = pos_x, pos_y

  # Draw function

  def draw( self, surface ):

    return [ surface.blit( self.image, self.rect ) ]

  # Fill background with specified image

  def draw_background( self, img_path ):

    rect_updates = []

    bg_image = pygame.image.load( img_path )
    bg_rect  = bg_image.get_rect()

    for i in range( int( math.ceil( self.rect.width / float( bg_rect.width ) ) ) ):
      for j in range( int( math.ceil( self.rect.height / float( bg_rect.height ) ) ) ):
        rect_updates.append( self.image.blit( bg_image, ( i * bg_rect.width, j * bg_rect.height ) ) )

    return rect_updates
