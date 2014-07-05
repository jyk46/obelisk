#=========================================================================
# sidebarwindow.py
#=========================================================================
# Extended window class for displaying sidebar information

import pygame, sys, os
from pygame.locals import *

import properties
import window
import button

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class SidebarWindow( window.Window ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, bg_path, expeditions ):

    window.Window.__init__( self, width, height, pos_x, pos_y, bg_path )

    # Initialize sub-windows

    self.terr_surface = pygame.Surface( ( properties.SIDEBAR_TERR_WIDTH, properties.SIDEBAR_TERR_HEIGHT ) )
    self.expd_surface = pygame.Surface( ( properties.SIDEBAR_EXPD_WIDTH, properties.SIDEBAR_EXPD_HEIGHT ) )

    self.terr_rect    = self.terr_surface.get_rect()
    self.expd_rect    = self.expd_surface.get_rect()

    self.terr_rect.topleft = 16, 96
    self.expd_rect.topleft = 16, 96 + properties.SIDEBAR_TERR_HEIGHT + 32

    # Initialize font and labels for sub-windows

    self.font               = pygame.font.Font( properties.DEFAULT_FONT, 16 )
    self.font.set_bold( True )
    self.terr_label_surface = self.font.render( 'TERRAIN INFO', 1, (0,0,0) )
    self.terr_label_rect    = self.terr_label_surface.get_rect()
    self.expd_label_surface = self.font.render( 'EXPEDITION INFO', 1, (0,0,0) )
    self.expd_label_rect    = self.expd_label_surface.get_rect()

    self.terr_label_rect.topleft = 16, 64 + 3
    self.expd_label_rect.topleft = 16, 96 + properties.SIDEBAR_TERR_HEIGHT + 3

    # Initialize done button

    self.button_group = pygame.sprite.RenderUpdates()
    self.button_group.add( button.Button( 'DONE', 64, properties.SIDEBAR_HEIGHT - 16 - properties.MENU_HEIGHT ) )

    # Member variables

    self.day_en     = True
    self.time_count = 1

    self.terr        = None
    self.expd        = None
    self.expeditions = expeditions

  # Get number of free survivors remaining on map

  def get_free( self ):

    count = 0

    if len( self.expeditions ) > 0:
      for expd in self.expeditions:
        count += expd.get_free()

    return count

  # Draw information onto window

  def draw_info( self ):

    rect_updates = []

    # Refresh black background for sub-windows

    self.terr_surface.fill( (0,0,0) )
    self.expd_surface.fill( (0,0,0) )

    # Populate terrain panel information

    font = pygame.font.Font( properties.DEFAULT_FONT, 14 )

    if self.terr != None:

      terr_type_surface = font.render( 'TYPE: ' + self.terr.terrain, 1, (255,255,255) )
      rect_updates += [ self.terr_surface.blit( terr_type_surface, ( 4, 3 ) ) ]

      terr_risk_surface = font.render( 'RISK: ' + self.terr.risk, 1, (255,255,255) )
      rect_updates += [ self.terr_surface.blit( terr_risk_surface, ( 4, 32 + 3 ) ) ]

      terr_yield_surface = font.render( 'YIELD: ' + self.terr.get_yield(), 1, (255,255,255) )
      rect_updates += [ self.terr_surface.blit( terr_yield_surface, ( 4, 2 * 32 + 3 ) ) ]

    # Populate expedition panel information

    if self.expd != None:

      expd_size_surface = font.render( 'SIZE: ' + str( len( self.expd.survivors ) ), 1, (255,255,255) )
      rect_updates += [ self.expd_surface.blit( expd_size_surface, ( 4, 3 ) ) ]

      food_color = (255,255,255)
      if len( self.expd.survivors ) > self.expd.inv.food:
        food_color = (255,0,0)

      expd_food_surface = font.render( 'FOOD: ' + str( self.expd.inv.food ), 1, food_color )
      rect_updates += [ self.expd_surface.blit( expd_food_surface, ( 4, 32 + 3 ) ) ]

      expd_wood_surface = font.render( 'WOOD: ' + str( self.expd.inv.wood ), 1, (255,255,255) )
      rect_updates += [ self.expd_surface.blit( expd_wood_surface, ( 4, 2 * 32 + 3 ) ) ]

      expd_metal_surface = font.render( 'METAL: ' + str( self.expd.inv.metal ), 1, (255,255,255) )
      rect_updates += [ self.expd_surface.blit( expd_metal_surface, ( 4, 3 * 32 + 3 ) ) ]

      expd_ammo_surface = font.render( 'AMMO: ' + str( self.expd.inv.ammo ), 1, (255,255,255) )
      rect_updates += [ self.expd_surface.blit( expd_ammo_surface, ( 4, 4 * 32 + 3 ) ) ]

    # Draw sub-windows onto sidebar window

    rect_updates += [ self.image.blit( self.terr_surface, self.terr_rect ) ]
    rect_updates += [ self.image.blit( self.expd_surface, self.expd_rect ) ]

    # Draw labels onto sidebar window

    font = pygame.font.Font( properties.DEFAULT_FONT, 40 )
    font.set_bold( True )

    time_str = 'DAY '
    if not self.day_en:
      time_str = 'NIGHT '
    time_str += str( self.time_count )

    time_surface = font.render( time_str, 1, (0,0,0) )

    rect_updates += [ self.image.blit( time_surface, ( 20, 6 ) ) ]
    rect_updates += [ self.image.blit( self.terr_label_surface, self.terr_label_rect ) ]
    rect_updates += [ self.image.blit( self.expd_label_surface, self.expd_label_rect ) ]

    free_surface = self.font.render( str( self.get_free() ) + ' FREE SURVIVORS', 1, (0,0,0) )
    rect_updates += [ self.image.blit( free_surface, \
                      ( 16, 96 + properties.SIDEBAR_TERR_HEIGHT + 32 \
                          + properties.SIDEBAR_EXPD_HEIGHT + 3 ) ) ]

    # Draw done button

    self.button_group.draw( self.image )

    return rect_updates

  # Overloaded aggregate draw function

  def draw( self, surface ):

    rect_updates  = self.draw_background()
    rect_updates += self.draw_info()
    rect_updates += window.Window.draw( self, surface )

    return rect_updates
