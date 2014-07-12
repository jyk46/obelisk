#=========================================================================
# infotextbox.py
#=========================================================================
# Extended text box class to display survivor or item information

import pygame, sys, os
from pygame.locals import *

import properties
import utils
import textbox
import tile
import expedition
import survivor
import attribute
import inventory
import item

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class InfoTextBox( textbox.TextBox ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, offset_x, offset_y, size, color ):

    textbox.TextBox.__init__( self, width, height, pos_x, pos_y, offset_x, offset_y, size, color )

  # Set tile to display information about

  def set_tile( self, _tile ):

    # Text to display

    text_matrix = []

    text_matrix.append( [
      'TYPE: ' + _tile.terrain,
      'RISK: ' + _tile.risk,
      'YIELD: ' + _tile.get_yield(),
    ] )

    # Draw text box

    self.update( text_matrix )

  # Set expedition to display information about

  def set_expedition( self, _expedition ):

    # Text to display

    text_matrix = []

    text_matrix.append( [
      'SIZE: ' + str( len( _expedition.survivors ) ),
      'FOOD: ' + str( _expedition._inventory.food ),
      'WOOD: ' + str( _expedition._inventory.wood ),
      'METAL: ' + str( _expedition._inventory.metal ),
      'AMMO: ' + str( _expedition._inventory.ammo ),
    ] )

    # Draw text box

    self.update( text_matrix )

  # Set survivor to display information about

  def set_survivor( self, _survivor ):

    # Text to display

    text_matrix = []

    text_matrix.append( [
      '**' + str( _survivor.name ),
      'AGE: ' + str( _survivor.age ),
      'STAM: ' + str( _survivor.stamina ) + '/' + str( _survivor.max_stamina ),
      'PHYS: ' + str( _survivor.physical ),
      'MENT: ' + str( _survivor.mental ),
    ] )

    # Text for survivor attributes

    attributes_col = [ '', 'ATTRIBUTES:' ]

    for _attribute in _survivor.attributes:
      attributes_col.append( '* ' + _attribute.name )

    text_matrix.append( attributes_col )

    # Draw text box

    self.update( text_matrix )

  # Set item to display information about. Optionally display cost and
  # crafting requirements.

  def set_item( self, _item ):

    # Text to display

    text_matrix = []

    info_col = [ '**' + str( _item.name ) ]

    if _item.type == 'Weapon':
      info_col.append( 'DMG: ' + str( _item.dmg_min ) + '-' + str( _item.dmg_max ) )
      info_col.append( 'AMMO: ' + str( _item.ammo_cost ) )

    elif _item.type == 'Armor':
      info_col.append( 'ARM: ' + str( _item.armor ) )

    else:
      info_col.append( 'EFFECT:' )
      info_col += _item.effect

    text_matrix.append( info_col )

    # Draw text box

    self.update( text_matrix )

  # Display crafting requirements for a given item with current
  # resources. By default this information is displayed on the right half
  # of the inforamtion text box and is intended to be used in conjunction
  # with the set_items() function above.

  def set_craft( self, _item, survivors, inventory, mental ):

    text_matrix = []

    # Item information

    info_col = [ '**' + str( _item.name ) ]

    if _item.type == 'Weapon':
      info_col.append( 'DMG: ' + str( _item.dmg_min ) + '-' + str( _item.dmg_max ) )
      info_col.append( 'AMMO: ' + str( _item.ammo_cost ) )

    elif _item.type == 'Armor':
      info_col.append( 'ARM: ' + str( _item.armor ) )

    else:
      info_col.append( 'EFFECT:' )
      info_col += _item.effect

    text_matrix.append( info_col )

    # Resources cost

    info_col = []

    current_wood  = str( inventory.wood )
    current_metal = str( inventory.metal )

    if inventory.wood < _item.wood_cost:
      current_wood = '\R' + current_wood
    if inventory.metal < _item.metal_cost:
      current_metal = '\R' + current_metal

    info_col.append( 'WOOD: ' + current_wood + '/' + str( _item.wood_cost ) )
    info_col.append( 'METAL: ' + current_metal + '/' + str( _item.metal_cost ) )

    # Mental requirement

    current_mental = str( mental )

    if mental < _item.mental_req:
      current_mental = '\R' + current_mental

    info_col.append( 'MENTAL: ' + current_mental + '/' + str( _item.mental_req ) )

    text_matrix.append( info_col )

    # Draw text box

    self.update( text_matrix )
