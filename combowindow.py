#=========================================================================
# combowindow.py
#=========================================================================
# Extended window class for handling survivor/inventory selection

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

class ComboWindow( window.Window ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, bg_path ):

    window.Window.__init__( self, width, height, pos_x, pos_y, bg_path )

    # Member variables

    self._expedition = None
    self.survivors   = []
    self._inventory  = inventory.Inventory()
    self.start_phase = True

    self._survivor   = None
    self._item       = None

    # Initialize sub-windows

    self.info_tbox = infotextbox.InfoTextBox(
      properties.ACTION_INFO_WIDTH, properties.ACTION_INFO_HEIGHT,
      INFO_X_OFFSET, INFO_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    self.old_tbox = textbox.TextBox(
      properties.ACTION_SUB_WIDTH, properties.ACTION_SUB_HEIGHT - 32,
      OLD_X_OFFSET, OLD_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    self.new_tbox = textbox.TextBox(
      properties.ACTION_SUB_WIDTH, properties.ACTION_SUB_HEIGHT - 32,
      NEW_X_OFFSET, NEW_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    # Initialize labels for sub-windows

    self.info_label_surface, self.info_label_rect = utils.gen_text_pos(
      'INFORMATION', 16, INFO_X_OFFSET, properties.TEXT_Y_OFFSET, utils.BLACK, True
    )

    self.old0_label_surface, self.old0_label_rect = utils.gen_text_pos(
      'SURVIVORS', 16,
      OLD_X_OFFSET, OLD_Y_OFFSET - properties.TEXT_HEIGHT + properties.TEXT_Y_OFFSET,
      utils.BLACK, True
    )

    self.old1_label_surface, self.old1_label_rect = utils.gen_text_pos(
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

  # Free up survivors and inventory when canceling selection

  def free_survivors( self ):

    if self._expedition != None:
      self._expedition.free_survivors()

  def free_inventory( self ):

    if self._expedition != None:
      self._expedition._inventory.merge_resources( self._inventory )
      self._expedition.free_inventory()

  def free( self ):

    self.free_survivors()
    self.free_inventory()

  # Reset scroll positions of text boxes

  def reset_scroll( self ):

    self.old_tbox.scroll_y = 0
    self.new_tbox.scroll_y = 0

  # Reset expedition to clean state

  def reset( self ):

    self._expedition = None
    self.survivors   = []
    self._inventory  = inventory.Inventory( 0, 0, 0, 0, [] )
    self.start_phase = True
    self._survivor   = None
    self._item       = None

    self.free()
    self.reset_scroll()

  # Process inputs. Return true if next button is clicked and at least
  # one survivor was selected.

  def process_inputs( self, mouse_x, mouse_y, mouse_click ):

    self._survivor = None
    self._item     = None

    # Determine survivor info to display

    if self.start_phase:

      # Free survivors

      for _survivor, rect in zip( self._expedition.get_free(), self.old_tbox.rect_matrix[0] ):

        # Determine if mouse is hovering over survivor

        if rect.collidepoint( mouse_x, mouse_y ):

          self._survivor = _survivor

          # Move selected survivors to selected column

          if mouse_click:
            _survivor.free = False
            self.survivors.append( _survivor )

      # Selected survivors

      for _survivor, rect in zip( self.survivors, self.new_tbox.rect_matrix[0] ):

        # Determine if mouse is hovering over survivor

        if rect.collidepoint( mouse_x, mouse_y ):

          self._survivor = _survivor

          # Move deselected survivors to free column

          if mouse_click:
            _survivor.free = True
            self.survivors.remove( _survivor )

    # Determine item info to display

    else:

      # Free items

      items = [ 'Food', 'Wood', 'Metal', 'Ammo', ] * 4 \
            + self._expedition._inventory.get_free()

      for _item, rect in zip( items, self.old_tbox.rect_matrix[0] ):

        # Determine if mouse is hovering over item

        if rect.collidepoint( mouse_x, mouse_y ):

          if type( _item ) == item.Item:
            self._item = _item

          # Transfer items if mouse is clicked

          if mouse_click:

            if ( _item == 'Food' ) and ( self._expedition._inventory.food > 0 ):
              self._expedition._inventory.food -= 1
              self._inventory.food             += 1

            elif ( _item == 'Wood' ) and ( self._expedition._inventory.wood > 0 ):
              self._expedition._inventory.wood -= 1
              self._inventory.wood             += 1

            elif ( _item == 'Metal' ) and ( self._expedition._inventory.metal > 0 ):
              self._expedition._inventory.metal -= 1
              self._inventory.metal             += 1

            elif ( _item == 'Ammo' ) and ( self._expedition._inventory.ammo > 0 ):
              self._expedition._inventory.ammo -= 1
              self._inventory.ammo             += 1

            else:
              _item.free = False
              self._inventory.items.append( _item )

      # Selected items

      items = [ 'Food', 'Wood', 'Metal', 'Ammo', ] * 4 \
            + self._inventory.items

      for _item, rect in zip( items, self.new_tbox.rect_matrix[0] ):

        # Determine if mouse is hovering over item

        if rect.collidepoint( mouse_x, mouse_y ):

          if type( _item ) == item.Item:
            self._item = _item

          # Transfer items if mouse is clicked

          if mouse_click:

            if ( _item == 'Food' ) and ( self._inventory.food > 0 ):
              self._expedition._inventory.food += 1
              self._inventory.food             -= 1

            elif ( _item == 'Wood' ) and ( self._inventory.wood > 0 ):
              self._expedition._inventory.wood += 1
              self._inventory.wood             -= 1

            elif ( _item == 'Metal' ) and ( self._inventory.metal > 0 ):
              self._expedition._inventory.metal += 1
              self._inventory.metal             -= 1

            elif ( _item == 'Ammo' ) and ( self._inventory.ammo > 0 ):
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

    if mouse_click and rect.collidepoint( mouse_x, mouse_y ) \
      and ( not self.start_phase or ( len( self.survivors ) > 0 ) ):
      return True
    else:
      return False

  # Generate text matrices for scrollable text boxes

  def get_survivors_text( self, survivors ):

    text_col = []

    for _survivor in survivors:
      text_col.append( _survivor.name )

    return [ text_col ]

  def get_inventory_text( self, _inventory, items ):

    text_col = [
      'Food (' + str( _inventory.food ) + ')',
      'Wood (' + str( _inventory.wood ) + ')',
      'Metal (' + str( _inventory.metal ) + ')',
      'Ammo (' + str( _inventory.ammo ) + ')',
    ]

    for _item in items:
      text_col.append( _item.name )

    return [ text_col ]

  # Update graphics

  def update( self ):

    # Populate information text box if necessary

    if self._survivor != None:
      self.info_tbox.set_survivor( self._survivor )
    elif self._item != None:
      self.info_tbox.set_item( self._item )
    else:
      self.info_tbox.update()

    # Populate old/new text boxes if a valid expedition is assigned

    if self._expedition != None:

      # Display free survivors and selected survivors

      if self.start_phase:
        self.old_tbox.update( self.get_survivors_text( self._expedition.get_free() ) )
        self.new_tbox.update( self.get_survivors_text( self.survivors ) )

      # Display free items and selected items

      else:
        self.old_tbox.update( self.get_inventory_text( self._expedition._inventory, self._expedition._inventory.get_free() ) )
        self.new_tbox.update( self.get_inventory_text( self._inventory, self_inventory.items ) )

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

    if self.start_phase:
      rect_updates += [ self.image.blit( self.old0_label_surface, self.old0_label_rect ) ]
    else:
      rect_updates += [ self.image.blit( self.old1_inv_label_surface, self.old1_label_rect ) ]

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
