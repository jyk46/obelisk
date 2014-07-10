#=========================================================================
# survivorwindow.py
#=========================================================================
# Extended window class for handling survivor selection

import pygame, sys, os
from pygame.locals import *

import properties
import utils
import window
import textbox
import infotextbox
import button
import tile
import expedition
import survivor

#-------------------------------------------------------------------------
# Window Offsets
#-------------------------------------------------------------------------

INFO_X_OFFSET = 16
INFO_Y_OFFSET = 32

OLD_X_OFFSET  = 16
OLD_Y_OFFSET  = 32 + properties.ACTION_INFO_HEIGHT + 32

NEW_X_OFFSET  = 16 + properties.ACTION_SUB_WIDTH + 16
NEW_Y_OFFSET  = 32 + properties.ACTION_INFO_HEIGHT + 32

BUTTON_X_OFFSET = properties.ACTION_WIDTH / 2 - properties.MENU_WIDTH / 2
BUTTON_Y_OFFSET = properties.ACTION_HEIGHT - 16 - properties.MENU_HEIGHT

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class SurvivorWindow( window.Window ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, bg_path ):

    window.Window.__init__( self, width, height, pos_x, pos_y, bg_path )

    # Member variables

    self._expedition = None
    self.survivors   = []
    self._survivor   = None

    # Initialize sub-windows

    self.info_tbox = infotextbox.InfoTextBox(
      properties.ACTION_INFO_WIDTH, properties.ACTION_INFO_HEIGHT,
      INFO_X_OFFSET, INFO_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    self.old_tbox = textbox.TextBox(
      properties.ACTION_SUB_WIDTH, properties.ACTION_SUB_HEIGHT,
      OLD_X_OFFSET, OLD_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    self.new_tbox = textbox.TextBox(
      properties.ACTION_SUB_WIDTH, properties.ACTION_SUB_HEIGHT,
      NEW_X_OFFSET, NEW_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    # Initialize labels for sub-windows

    self.info_label_surface, self.info_label_rect = utils.gen_text_pos(
      'INFORMATION', 16, INFO_X_OFFSET, properties.TEXT_Y_OFFSET, utils.BLACK, True
    )

    self.old_label_surface, self.old_label_rect = utils.gen_text_pos(
      'SURVIVORS', 16,
      OLD_X_OFFSET, OLD_Y_OFFSET - properties.TEXT_HEIGHT + properties.TEXT_Y_OFFSET,
      utils.BLACK, True
    )

    self.new_label_surface, self.new_label_rect = utils.gen_text_pos(
      'SELECTED', 16,
      NEW_X_OFFSET, NEW_Y_OFFSET - properties.TEXT_HEIGHT + properties.TEXT_Y_OFFSET,
      utils.BLACK, True
    )

    # Initialize next button

    self.button_group = pygame.sprite.RenderUpdates()
    self.button_group.add( button.Button( 'NEXT', BUTTON_X_OFFSET, BUTTON_Y_OFFSET ) )

  # Free up inventory when canceling selection

  def free( self ):

    if self._expedition != None:
      self._expedition.free_survivors()

  # Reset scroll positions of text boxes

  def reset_scroll( self ):

    self.old_tbox.scroll_y = 0
    self.new_tbox.scroll_y = 0

  # Reset expedition to clean state

  def reset( self ):

    self._expedition = None
    self.survivors   = []
    self._survivor   = None

    self.free()
    self.reset_scroll()

  # Process inputs. Return true if next button is clicked and at least
  # one survivor was selected.

  def process_inputs( self, mouse_x, mouse_y, mouse_click ):

    self._survivor = None

    # Determine free survivor info to display

    for _survivor, rect in zip( self._expedition.get_free(), self.old_tbox.rect_matrix[0] ):

      # Determine if mouse is hovering over survivor

      if rect.collidepoint( mouse_x, mouse_y ) \
        and self.old_tbox.rect.collidepoint( mouse_x, mouse_y ):

        self._survivor = _survivor

        # Move selected survivors to selected column

        if mouse_click:
          _survivor.free = False
          self.survivors.append( _survivor )

    # Determine selected survivor info to display

    for _survivor, rect in zip( self.survivors, self.new_tbox.rect_matrix[0] ):

      # Determine if mouse is hovering over survivor

      if rect.collidepoint( mouse_x, mouse_y ) \
        and self.new_tbox.rect.collidepoint( mouse_x, mouse_y ):

        self._survivor = _survivor

        # Move deselected survivors to free column

        if mouse_click:
          _survivor.free = True
          self.survivors.remove( _survivor )

    # Scroll text boxes if necessary

    self.old_tbox.scroll_text( mouse_x, mouse_y )
    self.new_tbox.scroll_text( mouse_x, mouse_y )

    # Adjust button coordinates to absolute scale

    rect = self.button_group.sprites()[0].rect.move( self.rect.left, self.rect.top )

    # Check for valid button click

    if mouse_click and rect.collidepoint( mouse_x, mouse_y ) \
      and ( len( self.survivors ) > 0 ):
      return True
    else:
      return False

  # Generate text matrices for scrollable text boxes

  def get_text( self, survivors ):

    text_col = []

    for _survivor in survivors:
      text_col.append( _survivor.name )

    return [ text_col ]

  # Update graphics

  def update( self ):

    # Populate information text box if necessary

    if self._survivor != None:
      self.info_tbox.set_survivor( self._survivor )
    else:
      self.info_tbox.update()

    # Populate old/new text boxes if a valid expedition is assigned

    if self._expedition != None:
      self.old_tbox.update( self.get_text( self._expedition.get_free() ) )
      self.new_tbox.update( self.get_text( self.survivors ) )

    else:
      self.old_tbox.update()
      self.new_tbox.update()

  # Draw information onto window

  def draw_info( self ):

    # Draw text boxes

    rect_updates  = self.info_tbox.draw( self.image )
    rect_updates += self.old_tbox.draw( self.image )
    rect_updates += self.new_tbox.draw( self.image )

    # Draw labels

    rect_updates += [ self.image.blit( self.info_label_surface, self.info_label_rect ) ]
    rect_updates += [ self.image.blit( self.old_label_surface, self.old_label_rect ) ]
    rect_updates += [ self.image.blit( self.new_label_surface, self.new_label_rect ) ]

    # Draw next button

    rect_updates += self.button_group.draw( self.image )

    return rect_updates

  # Overloaded aggregate draw function

  def draw( self, surface ):

    rect_updates  = self.draw_background()
    rect_updates += self.draw_info()
    rect_updates += window.Window.draw( self, surface )

    return rect_updates

