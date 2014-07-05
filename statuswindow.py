#=========================================================================
# statuswindow.py
#=========================================================================
# Extended window class for displaying expedition's status information

import pygame, sys, os
from pygame.locals import *

import properties
import window
import expedition

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class StatusWindow( window.Window ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, bg_path ):

    window.Window.__init__( self, width, height, pos_x, pos_y, bg_path )

    # Member variables

    self.expd = None
    self.surv = None
    self.it   = None

    # Initialize sub-windows

    self.info_surface = pygame.Surface( ( properties.ACTION_INFO_WIDTH, properties.ACTION_INFO_HEIGHT ) )
    self.surv_surface = pygame.Surface( ( properties.ACTION_SUB_WIDTH, properties.ACTION_SUB_HEIGHT ) )
    self.inv_surface  = pygame.Surface( ( properties.ACTION_SUB_WIDTH, properties.ACTION_SUB_HEIGHT ) )

    self.info_rect    = self.info_surface.get_rect()
    self.surv_rect    = self.surv_surface.get_rect()
    self.inv_rect     = self.inv_surface.get_rect()

    self.info_rect.topleft = 16, 32
    self.surv_rect.topleft = 16, 32 + properties.ACTION_INFO_HEIGHT + 32
    self.inv_rect.topleft  = 16 + properties.ACTION_SUB_WIDTH + 16, 32 + properties.ACTION_INFO_HEIGHT + 32

    # Initialize font and labels for sub-windows

    self.font               = pygame.font.Font( properties.DEFAULT_FONT, 16 )
    self.font.set_bold( True )
    self.info_label_surface = self.font.render( 'INFORMATION', 1, (0,0,0) )
    self.info_label_rect    = self.info_label_surface.get_rect()
    self.surv_label_surface = self.font.render( 'SURVIVORS', 1, (0,0,0) )
    self.surv_label_rect    = self.surv_label_surface.get_rect()
    self.inv_label_surface  = self.font.render( 'INVENTORY', 1, (0,0,0) )
    self.inv_label_rect     = self.inv_label_surface.get_rect()

    self.info_label_rect.topleft = 16, 3
    self.surv_label_rect.topleft = 16, 32 + properties.ACTION_INFO_HEIGHT + 3
    self.inv_label_rect.topleft  = 16 + properties.ACTION_SUB_WIDTH + 16, 32 + properties.ACTION_INFO_HEIGHT + 3

#    # Position of materials information
#
#    self.mats_pos = 16, 32 + properties.ACTION_SUB_HEIGHT + 2

    # Scrollable area and indices

    self.surv_scroll = 0
    self.inv_scroll  = 0

    self.surv_scroll_up_rect = pygame.rect.Rect(
      self.surv_rect.topleft[0], self.surv_rect.topleft[1], \
      properties.ACTION_SUB_WIDTH, 16
    )

    self.surv_scroll_down_rect = pygame.rect.Rect(
      self.surv_rect.topleft[0], self.surv_rect.topleft[1] + properties.ACTION_SUB_HEIGHT - 16, \
      properties.ACTION_SUB_WIDTH, 16
    )

    self.inv_scroll_up_rect = pygame.rect.Rect(
      self.inv_rect.topleft[0], self.inv_rect.topleft[1], \
      properties.ACTION_SUB_WIDTH, 16
    )

    self.inv_scroll_down_rect = pygame.rect.Rect(
      self.inv_rect.topleft[0], self.inv_rect.topleft[1] + properties.ACTION_SUB_HEIGHT - 16, \
      properties.ACTION_SUB_WIDTH, 16
    )

  # Update graphics

  def update( self ):

    # Determine scroll position of both sub-windows

    self.surv_pos = []
    self.inv_pos  = []

    if self.expd != None:

      for i, surv in enumerate( self.expd.survivors ):
        self.surv_pos.append( ( 4, i * 32 + 3 - self.surv_scroll ) )

      for i, it in enumerate( self.expd.inv.items ):
        self.inv_pos.append( ( 4, i * 32 + 3 - self.inv_scroll ) )

      # Maximum scroll limit

      self.max_surv_scroll = len( self.expd.survivors ) * 32
      self.max_inv_scroll  = len( self.expd.inv.items ) * 32

  # Draw information onto window

  def draw_info( self ):

    rect_updates = []

    # Refresh black background for sub-windows

    self.info_surface.fill( (0,0,0) )
    self.surv_surface.fill( (0,0,0) )
    self.inv_surface.fill( (0,0,0) )

    # Detailed survivor/item information

    font = pygame.font.Font( properties.DEFAULT_FONT, 14 )

    if self.surv != None:

      font.set_bold( True )
      info_text_surface = font.render( self.surv.name, 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 3 ) ) ]
      font.set_bold( False )

      info_text_surface = font.render( 'AGE: ' + str( self.surv.age ), 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 32 + 3 ) ) ]

      info_text_surface = font.render( 'STAM: ' + str( self.surv.stamina ) + '/' + str( self.surv.max_stamina ), 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 2 * 32 + 3 ) ) ]

      info_text_surface = font.render( 'PHYS: ' + str( self.surv.physical ), 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 3 * 32 + 3 ) ) ]

      info_text_surface = font.render( 'MENT: ' + str( self.surv.mental ), 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 4 * 32 + 3 ) ) ]

      info_text_surface = font.render( 'ATTRIBUTES:', 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( properties.ACTION_INFO_WIDTH / 2 + 4, 32 + 3 ) ) ]

      for i, attr in enumerate( self.surv.attributes ):
        info_text_surface = font.render( '* ' + attr.name, 1, (255,255,255) )
        rect_updates += [ self.info_surface.blit( info_text_surface, ( properties.ACTION_INFO_WIDTH / 2 + 4, ( i + 2 ) * 32 + 3 ) ) ]

    elif self.it != None:

      font.set_bold( True )
      info_text_surface = font.render( self.it.name, 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 3 ) ) ]
      font.set_bold( False )

      info_text_surface = font.render( 'TYPE: ' + self.it.type, 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 32 + 3 ) ) ]

      info_text_surface = font.render( 'DMG: ' + str( self.it.dmg_min ) + '-' + str( self.it.dmg_max ), 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 2 * 32 + 3 ) ) ]

      info_text_surface = font.render( 'AMMO: ' + str( self.it.ammo_cost ), 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 3 * 32 + 3 ) ) ]

      info_text_surface = font.render( 'DEF: ' + str( self.it.armor ), 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 4 * 32 + 3 ) ) ]

      info_text_surface = font.render( 'EFFECTS:', 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( properties.ACTION_INFO_WIDTH / 2 + 4, 32 + 3 ) ) ]

    # Populate sub-windows with information

    for surv, pos in zip( self.expd.survivors, self.surv_pos ):
      rect_updates += [ self.surv_surface.blit( surv.text_surface, pos ) ]

    for it, pos in zip( self.expd.inv.items, self.inv_pos ):
      rect_updates += [ self.inv_surface.blit( it.text_surface, pos ) ]

    # Draw sub-windows onto status window

    rect_updates += [ self.image.blit( self.info_surface, self.info_rect ) ]
    rect_updates += [ self.image.blit( self.surv_surface, self.surv_rect ) ]
    rect_updates += [ self.image.blit( self.inv_surface, self.inv_rect ) ]

#    # Draw materials information below sub-windows
#
#    rect_updates += [ self.image.blit( self.expd.inv.text_surface, self.mats_pos ) ]

    # Draw labels onto status window

    rect_updates += [ self.image.blit( self.info_label_surface, self.info_label_rect ) ]
    rect_updates += [ self.image.blit( self.surv_label_surface, self.surv_label_rect ) ]
    rect_updates += [ self.image.blit( self.inv_label_surface, self.inv_label_rect ) ]

    return rect_updates

  # Overloaded aggregate draw function

  def draw( self, surface ):

    rect_updates  = self.draw_background()
    rect_updates += self.draw_info()
    rect_updates += window.Window.draw( self, surface )

    return rect_updates
