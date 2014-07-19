#=========================================================================
# equipwindow.py
#=========================================================================
# Extended window class for handling gear equipment

import pygame, sys, os
from pygame.locals import *

import properties
import utils
import window
import textbox
import infotextbox
import healthtextbox
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

class EquipWindow( window.Window ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, bg_path ):

    window.Window.__init__( self, width, height, pos_x, pos_y, bg_path )

    # Member variables

    self._expedition = None
    self.survivors   = []
    self._survivor   = None
    self._item       = None
    self.selected    = False

    # Initialize sub-windows

    self.info_tbox = infotextbox.InfoTextBox(
      properties.ACTION_INFO_WIDTH, properties.ACTION_INFO_HEIGHT,
      INFO_X_OFFSET, INFO_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    self.old_tbox = healthtextbox.HealthTextBox(
      properties.ACTION_SUB_WIDTH, properties.ACTION_SUB_HEIGHT,
      OLD_X_OFFSET, OLD_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    self.new_tbox = textbox.TextBox(
      properties.ACTION_SUB_WIDTH, properties.ACTION_SUB_HEIGHT,
      NEW_X_OFFSET, NEW_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    # Initialize labels for sub-windows

    self.info_label_surface, self.info_label_rect = utils.gen_text_pos(
      'EQUIP DEFENDERS', 16, INFO_X_OFFSET, properties.TEXT_Y_OFFSET, utils.BLACK, True
    )

    self.old_label_surface, self.old_label_rect = utils.gen_text_pos(
      'DEFENDERS', 16,
      OLD_X_OFFSET, OLD_Y_OFFSET - properties.TEXT_HEIGHT + properties.TEXT_Y_OFFSET,
      utils.BLACK, True
    )

    self.new_label_surface, self.new_label_rect = utils.gen_text_pos(
      'EQUIPMENT', 16,
      NEW_X_OFFSET, NEW_Y_OFFSET - properties.TEXT_HEIGHT + properties.TEXT_Y_OFFSET,
      utils.BLACK, True
    )

    # Initialize ready button

    self.button_group = pygame.sprite.RenderUpdates()
    self.button_group.add( button.Button( 'READY', BUTTON_X_OFFSET, BUTTON_Y_OFFSET ) )

  # Free up items and reset equipment

  def free( self ):

    for _item in self._expedition._inventory.items:
      if ( _item == 'Weapon' ) or ( _item == 'Armor' ):
        _item.free = True

    for _survivor in self.survivors:
      _survivor.weapon = item.Item( 'Unarmed' )
      _survivor.armor  = item.Item( 'Clothes' )

  # Reset scroll positions of text boxes

  def reset_scroll( self ):

    self.old_tbox.scroll_y = 0
    self.new_tbox.scroll_y = 0

  # Reset survivor selection

  def half_reset( self ):

    self._survivor = None
    self._item     = None
    self.selected  = False

  # Reset expedition to clean state

  def reset( self ):

    self._expedition = None
    self.survivors   = []
    self._survivor   = None
    self._item       = None
    self.selected    = False

    self.reset_scroll()

  # Process inputs. Return true if ready button is clicked.

  def process_inputs( self, mouse_x, mouse_y, mouse_click ):

    # Clear survivor info box

    self._item = None

    if not self.selected:
      self._survivor = None

    # Display list of defenders

    for _survivor, rect in zip( self.survivors, self.old_tbox.rect_matrix[0] ):

      if rect.collidepoint( mouse_x, mouse_y ) \
        and self.old_tbox.rect.move( self.rect.left, self.rect.top ).collidepoint( mouse_x, mouse_y ):

        # Only do hover display if survivor is not selected yet

        if not self.selected:
          self._survivor = _survivor

        # Show equipment once a survivor is selected

        if mouse_click:

          if self.selected and ( _survivor == self._survivor ):
            self.half_reset()

          else:
            self._survivor = _survivor
            self.selected  = True

    # Display list of available equipment once survivor is chosen

    if self.selected:

      items = [ 'Unequip Weapon', 'Unequip Armor', ]

      for _item in self._expedition._inventory.get_free():
        if ( _item.type == 'Weapon' ) or ( _item.type == 'Armor' ):
          items.append( _item )

      for _item, rect in zip( items, self.new_tbox.rect_matrix[0] ):

        if rect.collidepoint( mouse_x, mouse_y ) \
          and self.new_tbox.rect.move( self.rect.left, self.rect.top ).collidepoint( mouse_x, mouse_y ):

          # Show equipment stats difference on hover

          if type( _item ) != str:
            self._item = _item

          # Assign new equipment to survivor

          if mouse_click:

            if _item == 'Unequip Weapon':
              self._survivor.weapon.free = True
              self._survivor.weapon      = item.Item( 'Unarmed' )

            elif _item == 'Unequip Armor':
              self._survivor.armor.free = True
              self._survivor.armor      = item.Item( 'Clothes' )

            elif ( _item != self._survivor.weapon ) \
              and ( _item != self._survivor.armor ):

              _item.free = False

              if _item.type == 'Weapon':
                self._survivor.weapon.free = True
                self._survivor.weapon      = _item

              elif _item.type == 'Armor':
                self._survivor.armor.free = False
                self._survivor.armor      = _item

    # Scroll text boxes if necessary

    self.old_tbox.scroll_text( mouse_x, mouse_y )
    self.new_tbox.scroll_text( mouse_x, mouse_y )

    # Adjust button coordinates to absolute scale

    rect = self.button_group.sprites()[0].rect.move( self.rect.left, self.rect.top )

    # Check for valid button click

    self.button_group.sprites()[0].image.set_alpha( 255 )

    if rect.collidepoint( mouse_x, mouse_y ):

      self.button_group.sprites()[0].image.set_alpha( 200 )

      if mouse_click:
        return True

    else:
      return False

  # Generate text matrices for scrollable text boxes

  def get_survivors_text( self, survivors ):

    text_col = []

    for _survivor in survivors:
      if self.selected and ( _survivor == self._survivor ):
        text_col.append( '\G' + _survivor.name )
      else:
        text_col.append( _survivor.name )

    return [ text_col ]

  def get_items_text( self, items ):

    text_col = [ 'Unequip Weapon', 'Unequip Armor', ]

    for _item in items:
      if ( _item.type == 'Weapon' ) or ( _item.type == 'Armor' ):
        text_col.append( _item.name )

    return [ text_col ]

  # Generate health ratios for text boxes

  def get_health( self, survivors ):

    health_col = []

    for _survivor in survivors:
      health_col.append( float( _survivor.stamina ) / _survivor.max_stamina )

    return [ health_col ]

  # Update graphics

  def update( self ):

    # Populate information text box if necessary

    if self._survivor != None:
      self.info_tbox.set_defender( self._survivor, self._item )
    else:
      self.info_tbox.update()

    # Populate old text box if valid expedition is assigned

    if self._expedition != None:
      self.old_tbox.update(
        self.get_survivors_text( self.survivors ),
        self.get_health( self.survivors )
      )
    else:
      self.old_tbox.update()

    # Populate new text box if survivor selected for equipping

    if self.selected:
      self.new_tbox.update( self.get_items_text( self._expedition._inventory.get_free() ) )
    else:
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

    # Draw craft button

    rect_updates += self.button_group.draw( self.image )

    return rect_updates

  # Overloaded aggregate draw function

  def draw( self, surface ):

    rect_updates  = self.draw_background()
    rect_updates += self.draw_info()
    rect_updates += window.Window.draw( self, surface )

    return rect_updates
