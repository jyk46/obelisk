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

  def __init__( self, width, height, pos_x, pos_y, bg_path=None ):

    self.surface      = pygame.Surface( ( width, height ) )
    self.image        = self.surface.convert()
    self.rect         = self.image.get_rect()
    self.rect.topleft = pos_x, pos_y

    self.bg_path      = bg_path

    if bg_path == None:
      self.bg_image = pygame.Surface( ( width, height ) )
    else:
      self.bg_image = pygame.image.load( self.bg_path )

    self.bg_rect      = self.bg_image.get_rect( topleft = ( 0, 0 ) )

  # Fill background with specified image

  def draw_background( self ):

    rect_updates = []

    for i in range( int( math.ceil( self.rect.width / float( self.bg_rect.width ) ) ) ):
      for j in range( int( math.ceil( self.rect.height / float( self.bg_rect.height ) ) ) ):
        rect_updates.append( self.image.blit( self.bg_image, ( i * self.bg_rect.width, j * self.bg_rect.height ) ) )

    return rect_updates

  # Draw function

  def draw( self, surface ):

    return [ surface.blit( self.image, self.rect ) ]
