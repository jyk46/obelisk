#=========================================================================
# sidebarwindow.py
#=========================================================================
# Extended window class for displaying sidebar information

import pygame, sys, os
from pygame.locals import *

import properties
import utils
import window
import infotextbox
import button

#-------------------------------------------------------------------------
# Window Offsets
#-------------------------------------------------------------------------

TIME_X_OFFSET = 20
TIME_Y_OFFSET = 6

TILE_X_OFFSET = 16
TILE_Y_OFFSET = 96

EXPD_X_OFFSET = 16
EXPD_Y_OFFSET = TILE_Y_OFFSET + properties.SIDEBAR_TILE_HEIGHT + 32

FREE_X_OFFSET = 16
FREE_Y_OFFSET = EXPD_Y_OFFSET + properties.SIDEBAR_EXPD_HEIGHT + properties.TEXT_Y_OFFSET

BUTTON_X_OFFSET = properties.SIDEBAR_WIDTH / 2 - properties.MENU_WIDTH / 2
BUTTON_Y_OFFSET = properties.SIDEBAR_HEIGHT - 16 - properties.MENU_HEIGHT

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class SidebarWindow( window.Window ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, bg_path, expeditions ):

    window.Window.__init__( self, width, height, pos_x, pos_y, bg_path )

    # Member variables

    self.day_en      = True
    self.time_count  = 1

    self._tile       = None
    self._expedition = None
    self.expeditions = expeditions

    self.time_str    = ''

    # Initialize sub-windows

    self.tile_tbox = infotextbox.InfoTextBox(
      properties.SIDEBAR_TILE_WIDTH, properties.SIDEBAR_TILE_HEIGHT,
      TILE_X_OFFSET, TILE_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    self.expedition_tbox = infotextbox.InfoTextBox(
      properties.SIDEBAR_EXPD_WIDTH, properties.SIDEBAR_EXPD_HEIGHT,
      EXPD_X_OFFSET, EXPD_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    # Initialize labels for sub-windows

    self.tile_label_surface, self.tile_label_rect = utils.gen_text_pos(
      'TERRAIN INFO', 16,
      TILE_X_OFFSET, TILE_Y_OFFSET - properties.TEXT_HEIGHT + properties.TEXT_Y_OFFSET,
      utils.BLACK, True
    )

    self.expedition_label_surface, self.expedition_label_rect = utils.gen_text_pos(
      'EXPEDITION INFO', 16,
      EXPD_X_OFFSET, EXPD_Y_OFFSET - properties.TEXT_HEIGHT + properties.TEXT_Y_OFFSET,
      utils.BLACK, True
    )

    # Initialize done button

    self.button_group = pygame.sprite.RenderUpdates()
    self.button_group.add( button.Button( 'DONE', BUTTON_X_OFFSET, BUTTON_Y_OFFSET ) )

  # Get number of free survivors remaining on map

  def get_free( self ):

    count = 0

    if len( self.expeditions ) > 0:
      for _expedition in self.expeditions:
        count += len( _expedition.get_free() )

    return count

  # Process inputs. Return true if done button is clicked and there are
  # no more free survivors left.

  def process_inputs( self, mouse_x, mouse_y, mouse_click ):

    # Adjust button coordinates to absolute scale

    rect = self.button_group.sprites()[0].rect.move( self.rect.left, self.rect.top )

    # Check for valid button click

    self.button_group.sprites()[0].image.set_alpha( 255 )

    if rect.collidepoint( mouse_x, mouse_y ):

      self.button_group.sprites()[0].image.set_alpha( 200 )

      if mouse_click and ( self.get_free() == 0 ):
        return True

    else:
      return False

  # Update graphics

  def update( self ):

    # Compute time count

    self.time_str = 'DAY '

    if not self.day_en:
      self.time_str = 'NIGHT '

    self.time_str += str( self.time_count )

    # Compute total number of free survivors

    self.free_str = str( self.get_free() ) + ' FREE SURVIVORS'

    # Populate text boxes

    if self._tile != None:
      self.tile_tbox.set_tile( self._tile )
    else:
      self.tile_tbox.update()

    if self._expedition != None:
      self.expedition_tbox.set_expedition( self._expedition )
    else:
      self.expedition_tbox.update()

  # Draw information onto window

  def draw_info( self ):

    # Draw text boxes

    rect_updates  = self.tile_tbox.draw( self.image )
    rect_updates += self.expedition_tbox.draw( self.image )

    # Draw labels

    rect_updates += utils.draw_text( self.image, self.time_str, 40, TIME_X_OFFSET, TIME_Y_OFFSET, utils.BLACK, True )
    rect_updates += [ self.image.blit( self.tile_label_surface, self.tile_label_rect ) ]
    rect_updates += [ self.image.blit( self.expedition_label_surface, self.expedition_label_rect ) ]

    # Draw number of free survivors left

    rect_updates += utils.draw_text( self.image, self.free_str, 16, FREE_X_OFFSET, FREE_Y_OFFSET, utils.BLACK, True )

    # Draw done button

    rect_updates += self.button_group.draw( self.image )

    return rect_updates

  # Overloaded aggregate draw function

  def draw( self, surface ):

    rect_updates  = self.draw_background()
    rect_updates += self.draw_info()
    rect_updates += window.Window.draw( self, surface )

    return rect_updates
