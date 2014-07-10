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

    # Draw rest of survivor information

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

    # Draw rest of survivor information

    self.update( text_matrix )

  # Set survivor to display information about

  def set_survivor( self, _survivor ):

    # Text to display

    text_matrix = []

    text_matrix.append( [
      '**' + str( _survivor.name ),
      'AGE: ' + str( _survivor.age ),
      'STAM: ' + str( _survivor.stamina ),
      'PHYS: ' + str( _survivor.physical ),
      'MENT: ' + str( _survivor.mental ),
    ] )

    # Text for survivor attributes

    attributes_col = [ '', 'ATTRIBUTES:' ]

    for _attribute in _survivor.attributes:
      attributes_col.append( '* ' + _attribute.name )

    text_matrix.append( attributes_col )

    # Draw rest of survivor information

    self.update( text_matrix )

  # Set item to display information about

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

    # Draw rest of survivor information

    self.update( text_matrix )
