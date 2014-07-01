#=========================================================================
# window.py
#=========================================================================
# Sprite class for holding separate windows on the main display.

import pygame, sys, os
from pygame.locals import *

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Window( pygame.sprite.Sprite ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y ):

    pygame.sprite.Sprite.__init__( self, self.groups )

    self.surface      = pygame.Surface( ( width, height ) )
    self.image        = self.surface.convert()
    self.rect         = self.image.get_rect()
    self.rect.topleft = pos_x, pos_y
