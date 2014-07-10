#=========================================================================
# button.py
#=========================================================================
# Class for generic buttons to be used in game, can overlay text on top
# of images and return the surface for drawing later.

import pygame, sys, os
from pygame.locals import *

import properties
import utils

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Button( pygame.sprite.Sprite ):

  # Constructor

  def __init__( self, text, pos_x, pos_y ):

    pygame.sprite.Sprite.__init__( self )

    # Set button background image

    self.img_path     = properties.BUTTON_PATH
    self.image        = pygame.image.load( self.img_path )
    self.rect         = self.image.get_rect()
    self.pos_x        = pos_x
    self.pos_y        = pos_y
    self.rect.topleft = self.pos_x, self.pos_y

    # Draw text on top of button

    self.text = text

    utils.draw_text_center( self.image, self.text, 14 )
