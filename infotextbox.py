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

    if _expedition._inventory.food < len( _expedition.survivors ):
      text_matrix[0][1] = '\R' + text_matrix[0][1]

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
      info_col.append( 'DEF: ' + str( _item.armor ) )

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

  def set_craft( self, _item, survivors, inventory, mental, bonus=1.0 ):

    text_matrix = []

    # Item information

    info_col = [ '**' + str( _item.name ) ]

    if _item.type == 'Weapon':
      info_col.append( 'DMG: ' + str( _item.dmg_min ) + '-' + str( _item.dmg_max ) )
      info_col.append( 'AMMO: ' + str( _item.ammo_cost ) )

    elif _item.type == 'Armor':
      info_col.append( 'DEF: ' + str( _item.armor ) )

    else:
      info_col.append( 'EFFECT:' )
      info_col += _item.effect

    text_matrix.append( info_col )

    # Resources cost

    info_col = []

    current_wood  = str( inventory.wood )
    current_metal = str( inventory.metal )

    if inventory.wood < max( int( _item.wood_cost * bonus ), 1 ):
      current_wood = '\R' + current_wood
    if inventory.metal < max( int( _item.metal_cost * bonus ), 1 ):
      current_metal = '\R' + current_metal

    info_col.append( 'WOOD: ' + current_wood + '/' + str( max( int( _item.wood_cost * bonus ), 1 ) ) )
    info_col.append( 'METAL: ' + current_metal + '/' + str( max( int( _item.metal_cost * bonus ), 1 ) ) )

    # Mental requirement

    current_mental = str( mental )

    if mental < _item.mental_req:
      current_mental = '\R' + current_mental

    info_col.append( 'MENTAL: ' + current_mental + '/' + str( _item.mental_req ) )

    text_matrix.append( info_col )

    # Draw text box

    self.update( text_matrix )

  # Show more defense info for survivors

  def set_defender( self, _survivor, _item=None ):

    # Text to display

    text_matrix = []

    text_col = [
      '**' + str( _survivor.name ),
    ]

    # Handle weapon damage

    if ( _item != None ) and ( _item.type == 'Weapon' ) \
      and ( _survivor.weapon != _item ):

      old_dmg = _survivor.calc_avg_dmg()
      new_dmg = _survivor.calc_avg_dmg( _item )

      if new_dmg > old_dmg:
        color = '\G'
      elif new_dmg < old_dmg:
        color = '\R'
      else:
        color = ''

      text_col.append( color + 'WEAPON: ' + _item.name )
      text_col.append( color + 'DMG: ' + '%.1f' % new_dmg )

    else:
      text_col.append( 'WEAPON: ' + _survivor.weapon.name )
      text_col.append( 'DMG: ' + '%.1f' % _survivor.calc_avg_dmg() )

    # Handle armor defense

    if ( _item != None ) and ( _item.type == 'Armor' ) \
      and ( _survivor.armor != _item ):

      old_def = _survivor.armor.armor
      new_def = _item.armor

      if new_def > old_def:
        color = '\G'
      elif new_def < old_def:
        color = '\R'
      else:
        color = ''

      text_col.append( color + 'ARMOR: ' + _item.name )
      text_col.append( color + 'DMG: ' + str( new_def ) )

    else:
      text_col.append( 'ARMOR: ' + _survivor.armor.name )
      text_col.append( 'DEF: ' + str( _survivor.armor.armor ) )

    text_matrix.append( text_col )

    # Text for survivor attributes

    attributes_col = [ '', 'ATTRIBUTES:' ]

    for _attribute in _survivor.attributes:
      attributes_col.append( '* ' + _attribute.name )

    text_matrix.append( attributes_col )

    # Draw text box

    self.update( text_matrix )
