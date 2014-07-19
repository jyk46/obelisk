#=========================================================================
# eventwindow.py
#=========================================================================
# Extended window class for displaying event information

import pygame, sys, os
from pygame.locals import *

import random
import properties
import utils
import window
import textbox
import button

#-------------------------------------------------------------------------
# Window Offsets
#-------------------------------------------------------------------------

INFO_X_OFFSET = 16
INFO_Y_OFFSET = 32

BUTTON_X_OFFSET = properties.EVENT_WIDTH / 2 - properties.MENU_WIDTH / 2
BUTTON_Y_OFFSET = properties.EVENT_HEIGHT - 16 - properties.MENU_HEIGHT

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class EventWindow( window.Window ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, bg_path ):

    window.Window.__init__( self, width, height, pos_x, pos_y, bg_path )

    # Member variables

    self._expedition = None
    self.survivors   = []
    self._tile       = None
    self.food        = 0
    self.wood        = 0
    self.metal       = 0
    self.ammo        = 0
    self._item       = None
    self.starved     = {}

    self.text_matrix = [['']]


    # Initialize sub-windows

    self.info_tbox = textbox.TextBox(
      properties.EVENT_SUB_WIDTH, properties.EVENT_SUB_HEIGHT,
      INFO_X_OFFSET, INFO_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    # Initialize labels for sub-windows

    self.info_label_surface, self.info_label_rect = utils.gen_text_pos(
      'EVENT', 16, INFO_X_OFFSET, properties.TEXT_Y_OFFSET, utils.BLACK, True
    )

    # Initialize okay button

    self.button_group = pygame.sprite.RenderUpdates()
    self.button_group.add( button.Button( 'OKAY', BUTTON_X_OFFSET, BUTTON_Y_OFFSET ) )

  # Actually transfer rolled loot to expedition

  def commit_scavenge( self, explored ):

    assert( self._expedition != None )

    self._expedition._inventory.food  += self.food
    self._expedition._inventory.wood  += self.wood
    self._expedition._inventory.metal += self.metal
    self._expedition._inventory.ammo  += self.ammo

    if self._item != None:
      self._expedition._inventory.items.append( self._item )

    # Do not subtract stamina cost if scavenging at the end of explore

    if not explored:
      for _survivor in self.survivors:
        _survivor.stamina -= max( properties.SCAVENGE_COST - _survivor.get_attributes().day_bonus, 0 )

  # Commit dead survivor due to starvation

  def commit_food( self ):

    self._expedition._inventory.food -= len( self._expedition.survivors )

    if self._expedition._inventory.food < 0:
      self._expedition._inventory.food = 0

    for _survivor in self.starved:
      if _survivor.stamina == 0:
        self._expedition.survivors.remove( _survivor )

  # Reset expedition to clean state

  def reset( self ):

    self._expedition = None
    self.survivors   = []
    self._tile       = None
    self.food        = 0
    self.wood        = 0
    self.metal       = 0
    self.ammo        = 0
    self._item       = None
    self.starved     = {}

    self.text_matrix = [['']]

  # Process inputs. Return true if okay button is clicked.

  def process_inputs( self, mouse_x, mouse_y, mouse_click ):

    # Adjust button coordinates to absolute scale

    rect = self.button_group.sprites()[0].rect.move( self.rect.left, self.rect.top )

    # Check for valid button click

    if mouse_click and rect.collidepoint( mouse_x, mouse_y ):
      return True
    else:
      return False

  # Generate text for scavenge

  def set_scavenge_text( self ):

    text_col = [
      'The expedition found:',
      '  ' + str( self.food ) + '  Food',
      '  ' + str( self.wood ) + '  Wood',
      '  ' + str( self.metal ) + '  Metal',
      '  ' + str( self.ammo ) + '  Ammo',
    ]

    if self._item != None:
      text_col.append( '  ' + self._item.name )

    self.text_matrix = [ text_col ]

  # Roll for scavenge event

  def scavenge( self ):

    assert( self._tile != None )

    self.food, self.wood, self.metal, self.ammo \
      = self._tile.roll_resources( self.survivors )

    self._item = self._tile.roll_items( self.survivors )

    self.set_scavenge_text()

  # Generate text for starvation

  def set_food_text( self ):

    text_col = []

    for _survivor, dmg in self.starved.iteritems():

      text = _survivor.name.split()[0]

      if _survivor.stamina == 0:
        text += ' starved to death!'
      else:
        text += ' starved for ' + str( dmg ) + ' damage...'

      text_col.append( text )

    self.text_matrix = [ text_col ]

  # Check if anyone starved in expedition

  def check_food( self ):

    assert( self._expedition._inventory.food < len( self._expedition.survivors ) )

    self.starved = {}

    num_starved = len( self._expedition.survivors ) - self._expedition._inventory.food

    # Randomly roll which survivors starved this turn

    for i in range( num_starved ):

      _survivor = random.choice( self._expedition.survivors )

      while _survivor in self.starved:
        _survivor = random.choice( self._expedition.survivors )

      # Calculate starvation damage as a percent of the max stamina

      dmg = int( properties.STARVE_RATE * _survivor.max_stamina )

      self.starved[_survivor] = dmg

      _survivor.stamina -= dmg

      if _survivor.stamina < 0:
        _survivor.stamina = 0

    self.set_food_text()

  # Generate text for new survivor

  def set_survivor_text( self, _survivor ):

    self.text_matrix = []

    self.text_matrix.append( [
      'Found a new survivor!',
      '**' + str( _survivor.name ),
      'AGE: ' + str( _survivor.age ),
      'STAM: ' + str( _survivor.stamina ) + '/' + str( _survivor.max_stamina ),
      'PHYS: ' + str( _survivor.physical ),
      'MENT: ' + str( _survivor.mental ),
    ] )

    attributes_col = [ '', '', 'ATTRIBUTES:' ]

    for _attribute in _survivor.attributes:
      attributes_col.append( '* ' + _attribute.name )

    self.text_matrix.append( attributes_col )

  # Update graphics

  def update( self ):

    # Populate information text box if necessary

    self.info_tbox.update( self.text_matrix )

  # Draw information onto window

  def draw_info( self ):

    # Draw text boxes

    rect_updates  = self.info_tbox.draw( self.image )

    # Draw labels

    rect_updates += [ self.image.blit( self.info_label_surface, self.info_label_rect ) ]

    # Draw next button

    rect_updates += self.button_group.draw( self.image )

    return rect_updates

  # Overloaded aggregate draw function

  def draw( self, surface ):

    rect_updates  = self.draw_background()
    rect_updates += self.draw_info()
    rect_updates += window.Window.draw( self, surface )

    return rect_updates
