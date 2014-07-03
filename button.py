#=========================================================================
# button.py
#=========================================================================
# Class for generic buttons to be used in game, can overlay text on top
# of images and return the surface for drawing later.

import pygame, sys, os
from pygame.locals import *

import properties

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Button( pygame.sprite.Sprite ):

  # Constructor

  def __init__( self, text, pos_x, pos_y ):

    pygame.sprite.Sprite.__init__( self, self.groups )

    # Set button background image

    self.img_path     = properties.BUTTON_PATH
    self.image        = pygame.image.load( self.img_path )
    self.rect         = self.image.get_rect()
    self.pos_x        = pos_x
    self.pos_y        = pos_y
    self.rect.topleft = self.pos_x, self.pos_y

    # Set text overlay for button

    self.font             = pygame.font.Font( properties.DEFAULT_FONT, 14 )
    self.text             = text
    self.text_image       = self.font.render( self.text, 1, (0,0,0) )
    self.text_rect        = self.text_image.get_rect()
    self.text_rect.center = properties.MENU_WIDTH / 2, properties.MENU_HEIGHT / 2

    # Draw text on top of button

    self.image.blit( self.text_image, self.text_rect )
