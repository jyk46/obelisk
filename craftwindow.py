#=========================================================================
# craftwindow.py
#=========================================================================
# Extended window class for handling survivor/inventory selection

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

class CraftWindow( window.Window ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, bg_path ):

    window.Window.__init__( self, width, height, pos_x, pos_y, bg_path )

    # Member variables

    self._expedition = None
    self.survivors   = []
    self._item       = None
    self.selected    = False

    # Construct list of craftable items

    self.items = []

    for name, info in item.item_table.iteritems():
      if info[9]:
        self.items.append( item.Item( name ) )

    # Initialize sub-windows

    self.info_tbox = infotextbox.InfoTextBox(
      properties.ACTION_INFO_WIDTH, properties.ACTION_INFO_HEIGHT,
      INFO_X_OFFSET, INFO_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    self.old_tbox = textbox.TextBox(
      properties.ACTION_SUB_WIDTH, properties.ACTION_SUB_HEIGHT,
      OLD_X_OFFSET, OLD_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    self.new_tbox = healthtextbox.HealthTextBox(
      properties.ACTION_SUB_WIDTH, properties.ACTION_SUB_HEIGHT,
      NEW_X_OFFSET, NEW_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    # Initialize labels for sub-windows

    self.info_label_surface, self.info_label_rect = utils.gen_text_pos(
      'INFORMATION', 16, INFO_X_OFFSET, properties.TEXT_Y_OFFSET, utils.BLACK, True
    )

    self.old_label_surface, self.old_label_rect = utils.gen_text_pos(
      'ITEM TO CRAFT', 16,
      OLD_X_OFFSET, OLD_Y_OFFSET - properties.TEXT_HEIGHT + properties.TEXT_Y_OFFSET,
      utils.BLACK, True
    )

    self.new_label_surface, self.new_label_rect = utils.gen_text_pos(
      'SURVIVORS', 16,
      NEW_X_OFFSET, NEW_Y_OFFSET - properties.TEXT_HEIGHT + properties.TEXT_Y_OFFSET,
      utils.BLACK, True
    )

    # Initialize craft button

    self.button_group = pygame.sprite.RenderUpdates()
    self.button_group.add( button.Button( 'CRAFT', BUTTON_X_OFFSET, BUTTON_Y_OFFSET ) )

  # Commit selected survivors and cost for crafting

  def commit( self ):

    assert( self._expedition != None )

    self._expedition._inventory.items.append( item.Item( self._item.name ) )

    self._expedition._inventory.wood  -= self._item.wood_cost
    self._expedition._inventory.metal -= self._item.metal_cost

    for _survivor in self.survivors:
      _survivor.free     = False
      _survivor.stamina -= properties.CRAFT_COST

    self.survivors = []

  # Reset scroll positions of text boxes

  def reset_scroll( self ):

    self.old_tbox.scroll_y = 0
    self.new_tbox.scroll_y = 0

  # Reset survivor selection

  def half_reset( self ):

    self.survivors = []
    self._item     = None
    self.selected  = False

  # Reset expedition to clean state

  def reset( self ):

    self._expedition = None
    self.survivors   = []
    self._item       = None
    self.selected    = False

    self.reset_scroll()

  # Get total mental bonus of currently selected survivors. Each survivor
  # adds one to the total by default.

  def get_current_mental( self ):

    mental = len( self.survivors )

    for _survivor in self.survivors:
      mental += _survivor.get_mental_bonus()

    return mental

  # Check if costs and requirements for item have been met

  def check_cost( self ):

    wood_check   = self._expedition._inventory.wood >= self._item.wood_cost
    metal_check  = self._expedition._inventory.metal >= self._item.metal_cost
    mental_check = self.get_current_mental() >= self._item.mental_req

    return wood_check and metal_check and mental_check

  # Process inputs. Return true if next button is clicked and at least
  # one survivor was selected.

  def process_inputs( self, mouse_x, mouse_y, mouse_click, cost=0 ):

    # Clear item info box if still selecting item to craft

    if not self.selected:
      self._item = None

    # Display list of craftable items

    for _item, rect in zip( self.items, self.old_tbox.rect_matrix[0] ):

      if rect.collidepoint( mouse_x, mouse_y ) \
        and self.old_tbox.rect.move( self.rect.left, self.rect.top ).collidepoint( mouse_x, mouse_y ):

        # Only do hover display if item is not selected already

        if not self.selected:
          self._item = _item

        # Select survivors once an item to craft is selected

        if mouse_click:

          if self.selected and ( _item == self._item ):
            self.half_reset()

          else:
            self._item     = _item
            self.survivors = []
            self.selected  = True

    # Display list of survivors available for crafting once item is chosen

    if self.selected:

      for _survivor, rect in zip( self._expedition.get_free(), self.new_tbox.rect_matrix[0] ):

        # Highlight selected survivors to update cost/req

        if mouse_click and rect.collidepoint( mouse_x, mouse_y ) \
          and self.new_tbox.rect.move( self.rect.left, self.rect.top ).collidepoint( mouse_x, mouse_y ):

          if _survivor in self.survivors:
            self.survivors.remove( _survivor )
          elif _survivor.stamina > cost:
            self.survivors.append( _survivor )

    # Scroll text boxes if necessary

    self.old_tbox.scroll_text( mouse_x, mouse_y )
    self.new_tbox.scroll_text( mouse_x, mouse_y )

    # Adjust button coordinates to absolute scale

    rect = self.button_group.sprites()[0].rect.move( self.rect.left, self.rect.top )

    # Check for valid button click

    if mouse_click and rect.collidepoint( mouse_x, mouse_y ) \
      and self.selected and self.check_cost():
      return True
    else:
      return False

  # Generate text matrices for scrollable text boxes

  def get_survivors_text( self, survivors ):

    text_col = []

    for _survivor in survivors:

      survivor_text = _survivor.name + ' '

      if _survivor in self.survivors:
        survivor_text = '\G' + survivor_text

      bonus = 1 + _survivor.get_mental_bonus()

      if bonus >= 0:
        survivor_text += '+'

      survivor_text += str( bonus )

      text_col.append( survivor_text )

    return [ text_col ]

  def get_items_text( self, items ):

    text_col = []

    for _item in items:
      if self.selected and ( _item == self._item ):
        text_col.append( '\G' + _item.name )
      else:
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

    if self._item != None:
      self.info_tbox.set_craft(
        self._item, self.survivors, self._expedition._inventory, self.get_current_mental()
      )
    else:
      self.info_tbox.update()

    # Populate old text box if valid expedition is assigned

    if self._expedition != None:
      self.old_tbox.update( self.get_items_text( self.items ) )
    else:
      self.old_tbox.update()

    # Populate new text box if ready to select survivors

    if self.selected:
      self.new_tbox.update(
        self.get_survivors_text( self._expedition.get_free() ),
        self.get_health( self._expedition.get_free() )
      )
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
