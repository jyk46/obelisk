#=========================================================================
# eventwindow.py
#=========================================================================
# Extended window class for displaying event information

import pygame, sys, os
from pygame.locals import *

import properties
import window
import button

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class EventWindow( window.Window ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, bg_path ):

    window.Window.__init__( self, width, height, pos_x, pos_y, bg_path )

    # Member variables

    self.expd       = None
    self.survivors  = []
    self.event_tile = None
    self.food       = 0
    self.wood       = 0
    self.metal      = 0
    self.ammo       = 0
    self.it         = None

    # Initialize sub-windows

    self.info_surface      = pygame.Surface( ( properties.EVENT_SUB_WIDTH, properties.EVENT_SUB_HEIGHT ) )
    self.info_rect         = self.info_surface.get_rect()
    self.info_rect.topleft = 16, 32

    # Initialize font and labels for sub-windows

    self.font                    = pygame.font.Font( properties.DEFAULT_FONT, 16 )
    self.font.set_bold( True )
    self.info_label_surface      = self.font.render( 'EVENT', 1, (0,0,0) )
    self.info_label_rect         = self.info_label_surface.get_rect()
    self.info_label_rect.topleft = 16, 3

    # Initialize okay button

    self.button_group = pygame.sprite.RenderUpdates()
    self.button_group.add( button.Button( 'OKAY', \
                             properties.EVENT_WIDTH / 2 - properties.MENU_WIDTH / 2, \
                             properties.EVENT_HEIGHT - 16 - properties.MENU_HEIGHT ) )

  # Roll for scavenge event

  def scavenge( self ):

    assert( self.event_tile != None )

    self.food, self.wood, self.metal, self.ammo \
      = self.event_tile.roll_resources( self.survivors )

    self.it = self.event_tile.roll_items( self.survivors )

  # Actually transfer rolled loot to expedition

  def commit_loot( self ):

    assert( self.expd != None )

    self.expd.inv.food  += self.food
    self.expd.inv.wood  += self.wood
    self.expd.inv.metal += self.metal
    self.expd.inv.ammo  += self.ammo

    if self.it != None:
      self.expd.inv.items.append( self.it )

  # Draw information onto window

  def draw_info( self ):

    rect_updates = []

    # Refresh black background for sub-windows

    self.info_surface.fill( (0,0,0) )

    # Event information

    font = pygame.font.Font( properties.DEFAULT_FONT, 14 )

    info_text_surface = font.render( 'The expedition found:', 1, (255,255,255) )
    rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 3 ) ) ]

    info_text_surface = font.render( '  ' + str( self.food ) + ' Food', 1, (255,255,255) )
    rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 32 + 3 ) ) ]

    info_text_surface = font.render( '  ' + str( self.wood ) + ' Wood', 1, (255,255,255) )
    rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 2 * 32 + 3 ) ) ]

    info_text_surface = font.render( '  ' + str( self.metal ) + ' Metal', 1, (255,255,255) )
    rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 3 * 32 + 3 ) ) ]

    info_text_surface = font.render( '  ' + str( self.ammo ) + ' Ammo', 1, (255,255,255) )
    rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 4 * 32 + 3 ) ) ]

    if self.it != None:
      info_text_surface = font.render( '  ' + self.it.name, 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 5 * 32 + 3 ) ) ]

    # Draw sub-windows onto status window

    rect_updates += [ self.image.blit( self.info_surface, self.info_rect ) ]

    # Draw labels onto status window

    rect_updates += [ self.image.blit( self.info_label_surface, self.info_label_rect ) ]

    # Draw okay button

    self.button_group.draw( self.image )

    return rect_updates

  # Overloaded aggregate draw function

  def draw( self, surface ):

    rect_updates  = self.draw_background()
    rect_updates += self.draw_info()
    rect_updates += window.Window.draw( self, surface )

    return rect_updates
