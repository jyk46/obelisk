#=========================================================================
# inventorywindow.py
#=========================================================================
# Extended window class for handling inventory selection

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
import inventory
import item

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

class InventoryWindow( window.Window ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, bg_path, type='All', limit=99 ):

    window.Window.__init__( self, width, height, pos_x, pos_y, bg_path )

    # Member variables

    self._expedition = None
    self._inventory  = inventory.Inventory()
    self._item       = None
    self.type        = type
    self.limit       = limit

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
      'INVENTORY', 16,
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
      self._expedition._inventory.merge_resources( self._inventory )
      self._expedition.free_inventory()

  # Reset scroll positions of text boxes

  def reset_scroll( self ):

    self.old_tbox.scroll_y = 0
    self.new_tbox.scroll_y = 0

  # Reset expedition to clean state

  def reset( self, type='All', limit=99 ):

    self._expedition = None
    self._inventory  = inventory.Inventory()
    self._item       = None
    self.type        = type
    self.limit       = limit

    self.reset_scroll()

  # Process inputs. Return true if next button is clicked and at least
  # one survivor was selected.

  def process_inputs( self, mouse_x, mouse_y, mouse_click ):

    self._item = None

    # Determine free item info to display

    if self.type == 'All':

      items = [ 'Food', 'Wood', 'Metal', 'Ammo', ] \
            + self._expedition._inventory.get_free()

    else:

      items = []

      for _item in self._expedition._inventory.get_free():
        if _item.type == self.type:
          items.append( _item )

    for _item, rect in zip( items, self.old_tbox.rect_matrix[0] ):

      # Determine if mouse is hovering over item

      if rect.collidepoint( mouse_x, mouse_y ) \
        and self.old_tbox.rect.move( self.rect.left, self.rect.top ).collidepoint( mouse_x, mouse_y ):

        if type( _item ) != str:
          self._item = _item

        # Transfer items if mouse is clicked

        if mouse_click:

          if _item == 'Food':
            if self._expedition._inventory.food > 0:
              self._expedition._inventory.food -= 1
              self._inventory.food             += 1

          elif _item == 'Wood':
            if self._expedition._inventory.wood > 0:
              self._expedition._inventory.wood -= 1
              self._inventory.wood             += 1

          elif _item == 'Metal':
            if self._expedition._inventory.metal > 0:
              self._expedition._inventory.metal -= 1
              self._inventory.metal             += 1

          elif _item == 'Ammo':
            if self._expedition._inventory.ammo > 0:
              self._expedition._inventory.ammo -= 1
              self._inventory.ammo             += 1

          elif len( self._inventory.items ) < self.limit:
            _item.free = False
            self._inventory.items.append( _item )

    # Determine selected item info to display

    items = self._inventory.items

    if self.type == 'All':
      items = [ 'Food', 'Wood', 'Metal', 'Ammo', ] + items

    for _item, rect in zip( items, self.new_tbox.rect_matrix[0] ):

      # Determine if mouse is hovering over item

      if rect.collidepoint( mouse_x, mouse_y ) \
        and self.new_tbox.rect.move( self.rect.left, self.rect.top ).collidepoint( mouse_x, mouse_y ):

        if type( _item ) != str:
          self._item = _item

        # Transfer items if mouse is clicked

        if mouse_click:

          if _item == 'Food':
            if self._inventory.food > 0:
              self._expedition._inventory.food += 1
              self._inventory.food             -= 1

          elif _item == 'Wood':
            if self._inventory.wood > 0:
              self._expedition._inventory.wood += 1
              self._inventory.wood             -= 1

          elif _item == 'Metal':
            if self._inventory.metal > 0:
              self._expedition._inventory.metal += 1
              self._inventory.metal             -= 1

          elif _item == 'Ammo':
            if self._inventory.ammo > 0:
              self._expedition._inventory.ammo += 1
              self._inventory.ammo             -= 1

          else:
            _item.free = True
            self._inventory.items.remove( _item )

    # Scroll text boxes if necessary

    self.old_tbox.scroll_text( mouse_x, mouse_y )
    self.new_tbox.scroll_text( mouse_x, mouse_y )

    # Adjust button coordinates to absolute scale

    rect = self.button_group.sprites()[0].rect.move( self.rect.left, self.rect.top )

    # Check for valid button click

    if mouse_click and rect.collidepoint( mouse_x, mouse_y ):
      return True
    else:
      return False

  # Generate text matrices for scrollable text boxes

  def get_text( self, _inventory, items ):

    if self.type == 'All':

      text_col = [
        'Food (' + str( _inventory.food ) + ')',
        'Wood (' + str( _inventory.wood ) + ')',
        'Metal (' + str( _inventory.metal ) + ')',
        'Ammo (' + str( _inventory.ammo ) + ')',
      ]

    else:
      text_col = []

    for _item in items:
      if ( self.type == 'All' ) or ( _item.type == self.type ):
        text_col.append( _item.name )

    return [ text_col ]

  # Update graphics

  def update( self ):

    # Populate information text box if necessary

    if self._item != None:
      self.info_tbox.set_item( self._item )
    else:
      self.info_tbox.update()

    # Populate old/new text boxes if a valid expedition is assigned

    if self._expedition != None:
      self.old_tbox.update( self.get_text( self._expedition._inventory, self._expedition._inventory.get_free() ) )
      self.new_tbox.update( self.get_text( self._inventory, self._inventory.items ) )

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
