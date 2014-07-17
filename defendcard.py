#=========================================================================
# defendcard.py
#=========================================================================
# Health and equipment information card for defend phase

import pygame, sys, os
from pygame.locals import *

import properties
import utils

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class DefendCard:

  # Constructor

  def __init__( self, _survivor, pos_x, pos_y ):

    # Member variables

    self._survivor   = _survivor
    self.pos_x       = pos_x
    self.pos_y       = pos_y
    self.bg_path     = properties.DEFEND_PATH + 'card_bg.png'
    self.surface_col = []

    self.damaged     = False

    # Initialize surface

    self.image        = pygame.Surface( ( properties.CARD_WIDTH, properties.CARD_HEIGHT ) )
    self.rect         = self.image.get_rect()
    self.rect.topleft = pos_x, pos_y

  # Show card as pulled forward if active during defend phase

  def activate( self ):

    self.rect.topleft = self.pos_x, self.pos_y - 32

  # Reset card to normal position

  def deactivate( self ):

    self.rect.topleft = self.pos_x, self.pos_y

  # Update graphics

  def update( self ):

    # Fill out survivor information

    text_col = [
      '**' + self._survivor.name.split()[0],
      'STAM: ' + str( self._survivor.stamina ) + '/' + str( self._survivor.max_stamina ),
      self._survivor.weapon.name,
      self._survivor.armor.name,
    ]

    self.surface_col = []
    row_idx          = 0

    for text in text_col:

      bold = False

      if '**' in text:
        bold = True
        text = text.replace( '**', '' )

      surface, rect = utils.gen_text_pos(
        text, 14,
        4 + properties.TEXT_X_OFFSET,
        ( ( properties.TEXT_HEIGHT - 4 ) * row_idx ) + 4 + properties.TEXT_Y_OFFSET,
        utils.WHITE, bold
      )

      self.surface_col.append( ( surface, rect ) )

      row_idx += 1

    # Adjust survivor name position to give health bar some room

    name_rect = self.surface_col[0][1]
    name_rect.move_ip( 0, -2 )

    # Create max health bar overlay

    self.max_surface      = pygame.Surface( ( self.rect.width - 16, properties.HEALTH_HEIGHT ) )
    self.max_rect         = self.max_surface.get_rect()
    self.max_rect.topleft = name_rect.left, name_rect.bottom + 2
    self.max_surface.fill( utils.WHITE )

    # Create current health overlay

    health                    = float( self._survivor.stamina ) / self._survivor.max_stamina
    current_width             = int( health * ( self.rect.width - 16 ) )
    self.current_surface      = pygame.Surface( ( current_width, properties.HEALTH_HEIGHT ) )
    self.current_rect         = self.current_surface.get_rect()
    self.current_rect.topleft = name_rect.left, name_rect.bottom + 2

    if health >= 0.67:
      self.current_surface.fill( utils.GREEN )
    elif health >= 0.33:
      self.current_surface.fill( utils.YELLOW )
    else:
      self.current_surface.fill( utils.RED )

  # Draw text

  def draw_text( self ):

    rect_updates = []

    for surface, rect in self.surface_col:
      rect_updates += [ self.image.blit( surface, rect ) ]

#    rect_updates += [ self.image.blit( self.max_surface, self.max_rect ) ]
    rect_updates += [ self.image.blit( self.current_surface, self.current_rect ) ]

    return rect_updates

  # Draw background

  def draw_background( self ):

    bg_image        = pygame.image.load( self.bg_path )
    bg_rect         = bg_image.get_rect()
    bg_rect.topleft = 0, 0

    if self.damaged or ( self._survivor.stamina == 0 ):
      bg_image.fill( utils.RED )

    return [ self.image.blit( bg_image, bg_rect ) ]

  # Draw graphics

  def draw( self, surface ):

    rect_updates  = self.draw_background()
    rect_updates += self.draw_text()
    rect_updates += [ surface.blit( self.image, self.rect ) ]

    return rect_updates
