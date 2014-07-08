#=========================================================================
# explorewindow.py
#=========================================================================
# Extended window class for handling explore phase selection

import pygame, sys, os
from pygame.locals import *

import properties
import window
import button
import expedition
import survivor
import inventory

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class ExploreWindow( window.Window ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, bg_path ):

    window.Window.__init__( self, width, height, pos_x, pos_y, bg_path )

    # Member variables

    self.expd       = None
    self.survivors  = []
    self.inv        = inventory.Inventory()
    self.start_tile = None
    self.surv_phase = True

    self.surv       = None
    self.it         = None

    # Initialize sub-windows

    self.info_surface = pygame.Surface( ( properties.ACTION_INFO_WIDTH, properties.ACTION_INFO_HEIGHT ) )
    self.old_surface  = pygame.Surface( ( properties.ACTION_SUB_WIDTH, properties.ACTION_SUB_HEIGHT - 32 ) )
    self.new_surface  = pygame.Surface( ( properties.ACTION_SUB_WIDTH, properties.ACTION_SUB_HEIGHT - 32 ) )

    self.info_rect    = self.info_surface.get_rect()
    self.old_rect     = self.old_surface.get_rect()
    self.new_rect     = self.new_surface.get_rect()

    self.info_rect.topleft = 16, 32
    self.old_rect.topleft = 16, 32 + properties.ACTION_INFO_HEIGHT + 32
    self.new_rect.topleft  = 16 + properties.ACTION_SUB_WIDTH + 16, 32 + properties.ACTION_INFO_HEIGHT + 32

    # Initialize font and labels for sub-windows

    self.font                   = pygame.font.Font( properties.DEFAULT_FONT, 16 )
    self.font.set_bold( True )
    self.info_label_surface     = self.font.render( 'INFORMATION', 1, (0,0,0) )
    self.info_label_rect        = self.info_label_surface.get_rect()
    self.old_surv_label_surface = self.font.render( 'SURVIVORS', 1, (0,0,0) )
    self.old_surv_label_rect    = self.old_surv_label_surface.get_rect()
    self.old_inv_label_surface  = self.font.render( 'INVENTORY', 1, (0,0,0) )
    self.old_inv_label_rect     = self.old_surv_label_surface.get_rect()
    self.new_label_surface      = self.font.render( 'EXPLORE PARTY', 1, (0,0,0) )
    self.new_label_rect         = self.new_label_surface.get_rect()

    self.info_label_rect.topleft     = 16, 3
    self.old_surv_label_rect.topleft = 16, 32 + properties.ACTION_INFO_HEIGHT + 3
    self.old_inv_label_rect.topleft  = 16, 32 + properties.ACTION_INFO_HEIGHT + 3
    self.new_label_rect.topleft      = 16 + properties.ACTION_SUB_WIDTH + 16, 32 + properties.ACTION_INFO_HEIGHT + 3

    # Initialize next button

    self.button_group = pygame.sprite.RenderUpdates()
    self.button_group.add( button.Button( 'NEXT', \
                             properties.ACTION_WIDTH / 2 - properties.MENU_WIDTH / 2, \
                             properties.ACTION_HEIGHT - 16 - properties.MENU_HEIGHT ) )

    # Scrollable area and indices

    self.old_scroll = 0
    self.new_scroll = 0

    self.old_scroll_up_rect = pygame.rect.Rect(
      self.old_rect.topleft[0], self.old_rect.topleft[1], \
      properties.ACTION_SUB_WIDTH, 16
    )

    self.old_scroll_down_rect = pygame.rect.Rect(
      self.old_rect.topleft[0], self.old_rect.topleft[1] + properties.ACTION_SUB_HEIGHT - 32 - 16, \
      properties.ACTION_SUB_WIDTH, 16
    )

    self.new_scroll_up_rect = pygame.rect.Rect(
      self.new_rect.topleft[0], self.new_rect.topleft[1], \
      properties.ACTION_SUB_WIDTH, 16
    )

    self.new_scroll_down_rect = pygame.rect.Rect(
      self.new_rect.topleft[0], self.new_rect.topleft[1] + properties.ACTION_SUB_HEIGHT - 32 - 16, \
      properties.ACTION_SUB_WIDTH, 16
    )

  # Clear selection information

  def clear( self ):
    self.survivors  = []
    self.inv        = inventory.Inventory( 0, 0, 0, 0, [] )
    self.start_tile = None

  # Reset expedition state to before explore selection

  def reset_survivors( self ):
    self.expd.reset_free_survivors()

  def reset_inventory( self ):
    self.expd.inv.merge_resources( self.inv )
    self.expd.reset_free_items()

  def reset_expd( self ):
    self.reset_survivors()
    self.reset_inventory()

  # Update graphics

  def update( self ):

    # Determine scroll position of both sub-windows

    self.old_pos = []
    self.new_pos = []

    if self.expd != None:

      # Survivor select phase

      if self.surv_phase:

        for i, surv in enumerate( self.expd.get_free() ):
          self.old_pos.append( ( 4, i * 32 + 3 - self.old_scroll ) )

        for i, surv in enumerate( self.survivors ):
          self.new_pos.append( ( 4, i * 32 + 3 - self.new_scroll ) )

        self.max_old_scroll = len( self.expd.get_free() ) * 32
        self.max_new_scroll = len( self.survivors ) * 32

      # Inventory select phase

      else:

        # Reserve slots for resources

        self.old_pos.append( ( 4, 3 - self.old_scroll ) )
        self.old_pos.append( ( 4, 32 + 3 - self.old_scroll ) )
        self.old_pos.append( ( 4, 2 * 32 + 3 - self.old_scroll ) )
        self.old_pos.append( ( 4, 3 * 32 + 3 - self.old_scroll ) )

        self.new_pos.append( ( 4, 3 - self.new_scroll ) )
        self.new_pos.append( ( 4, 32 + 3 - self.new_scroll ) )
        self.new_pos.append( ( 4, 2 * 32 + 3 - self.new_scroll ) )
        self.new_pos.append( ( 4, 3 * 32 + 3 - self.new_scroll ) )

        for i, it in enumerate( self.expd.inv.get_free() ):
          self.old_pos.append( ( 4, ( 4 + i ) * 32 + 3 - self.old_scroll ) )

        for i, it in enumerate( self.inv.items ):
          self.new_pos.append( ( 4, ( 4 + i ) * 32 + 3 - self.new_scroll ) )

        self.max_old_scroll = ( 4 + len( self.inv.get_free() ) ) * 32
        self.max_new_scroll = ( 4 + len( self.inv.items ) ) * 32

  # Draw information onto window

  def draw_info( self ):

    rect_updates = []

    # Refresh black background for sub-windows

    self.info_surface.fill( (0,0,0) )
    self.old_surface.fill( (0,0,0) )
    self.new_surface.fill( (0,0,0) )

    # Detailed survivor/item information

    font = pygame.font.Font( properties.DEFAULT_FONT, 14 )

    if self.surv_phase and ( self.surv != None ):

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

    elif not self.surv_phase and ( self.it != None ):

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

      info_text_surface = font.render( 'ARM: ' + str( self.it.armor ), 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( 4, 4 * 32 + 3 ) ) ]

      info_text_surface = font.render( 'EFFECTS:', 1, (255,255,255) )
      rect_updates += [ self.info_surface.blit( info_text_surface, ( properties.ACTION_INFO_WIDTH / 2 + 4, 32 + 3 ) ) ]

    # Draw survivor information

    if self.surv_phase:

      for surv, pos in zip( self.expd.get_free(), self.old_pos ):
        rect_updates += [ self.old_surface.blit( surv.text_surface, pos ) ]

      for surv, pos in zip( self.survivors, self.new_pos ):
        rect_updates += [ self.new_surface.blit( surv.text_surface, pos ) ]

    # Draw item information

    else:

      # Draw resources in inventory panel

      rsrc_text_surfaces = [
        font.render( 'Food (' + str( self.expd.inv.food ) + ')', 1, (255,255,255) ),
        font.render( 'Wood (' + str( self.expd.inv.wood ) + ')', 1, (255,255,255) ),
        font.render( 'Metal (' + str( self.expd.inv.metal ) + ')', 1, (255,255,255) ),
        font.render( 'Ammo (' + str( self.expd.inv.ammo ) + ')', 1, (255,255,255) ),
      ]

      for text_surface, pos in zip( rsrc_text_surfaces, self.old_pos[:4] ):
        rect_updates += [ self.old_surface.blit( text_surface, pos ) ]

      rsrc_text_surfaces = [
        font.render( 'Food (' + str( self.inv.food ) + ')', 1, (255,255,255) ),
        font.render( 'Wood (' + str( self.inv.wood ) + ')', 1, (255,255,255) ),
        font.render( 'Metal (' + str( self.inv.metal ) + ')', 1, (255,255,255) ),
        font.render( 'Ammo (' + str( self.inv.ammo ) + ')', 1, (255,255,255) ),
      ]

      for text_surface, pos in zip( rsrc_text_surfaces, self.new_pos[:4] ):
        rect_updates += [ self.new_surface.blit( text_surface, pos ) ]

      for it, pos in zip( self.expd.inv.get_free(), self.old_pos[4:] ):
        rect_updates += [ self.old_surface.blit( it.text_surface, pos ) ]

      for it, pos in zip( self.inv.items, self.new_pos[4:] ):
        rect_updates += [ self.new_surface.blit( it.text_surface, pos ) ]

    # Draw sub-windows onto status window

    rect_updates += [ self.image.blit( self.info_surface, self.info_rect ) ]
    rect_updates += [ self.image.blit( self.old_surface, self.old_rect ) ]
    rect_updates += [ self.image.blit( self.new_surface, self.new_rect ) ]

    # Draw labels onto status window

    rect_updates += [ self.image.blit( self.info_label_surface, self.info_label_rect ) ]

    if self.surv_phase:
      rect_updates += [ self.image.blit( self.old_surv_label_surface, self.old_surv_label_rect ) ]
    else:
      rect_updates += [ self.image.blit( self.old_inv_label_surface, self.old_inv_label_rect ) ]

    rect_updates += [ self.image.blit( self.new_label_surface, self.new_label_rect ) ]

    # Draw next button

    self.button_group.draw( self.image )

    return rect_updates

  # Overloaded aggregate draw function

  def draw( self, surface ):

    rect_updates  = self.draw_background()
    rect_updates += self.draw_info()
    rect_updates += window.Window.draw( self, surface )

    return rect_updates