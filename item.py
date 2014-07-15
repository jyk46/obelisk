#=========================================================================
# item.py
#=========================================================================
# Class for equipment (weapon, armor, misc) that can be held by the
# inventories of expeditions.

import pygame, sys, os
from pygame.locals import *

import properties

#-------------------------------------------------------------------------
# Utility Tables
#-------------------------------------------------------------------------

# Text for effects

effect_table = {

  'Binoculars' : [
    'Increases view range',
    'of expedition.',
  ],

  'First Aid' : [
    'Increases heal rate.',
  ],

  'Antibiotics' : [
    'Increases sickness',
    'cure rate.',
  ],

  'Analyzer' : [
    'Displays more',
    'information about',
    'terrain.',
  ],

  'Energy Drain' : [
    'Drain eldritch energy',
    'from ritual sites.',
  ],

  'Elder Sign' : [
    'Power to neutralize',
    'ancient forces.',
  ],

  'Pit Trap' : [
    'Deals minor damage',
    'to enemies before',
    'battle.',
  ],

  'Spike Trap' : [
    'Deals major damage',
    'to enemies before',
    'battle.',
  ],

  'Explosive Trap' : [
    'Chance to kill',
    'enemies before',
    'battle.',
  ],

  'Camouflage' : [
    'Reduces chance of',
    'detection at night.',
  ],

  'Bone Ward' : [
    'Greatly reduces',
    'chance of detection',
    'at night.',
  ],

  'Flashbang' : [
    'Stuns enemy; attack',
    'twice at start of',
    'battle.',
  ],

  'Barricade' : [
    'Blocks a small',
    'amount of enemy',
    'damage.',
  ],

  'Barbed Fence' : [
    'Blocks a large',
    'amount of enemy',
    'damage.',
  ],

}

# Possible items

item_table = {

  # name              wco mco men min max amm sta arm  type       craft

  'Binoculars'     : [ 99, 99, 99,  0,  0,  0,  0,  0, 'Tool',    False ],
  'First Aid'      : [ 99, 99, 99,  0,  0,  0,  0,  0, 'Tool',    False ],
  'Antibiotics'    : [ 99, 99, 99,  0,  0,  0,  0,  0, 'Tool',    False ],
  'Analyzer'       : [ 99, 99, 99,  0,  0,  0,  0,  0, 'Tool',    False ],
  'Energy Drain'   : [ 99, 99, 99,  0,  0,  0,  0,  0, 'Tool',    False ],
  'Elder Sign'     : [ 99, 99, 99,  0,  0,  0,  0,  0, 'Tool',    False ],

  'Pit Trap'       : [  2,  0,  2,  0,  0,  0,  0,  0, 'Defense', True  ],
  'Spike Trap'     : [  1,  1,  4,  0,  0,  0,  0,  0, 'Defense', True  ],
  'Explosive Trap' : [  2,  2,  8,  0,  0,  0,  0,  0, 'Defense', True  ],
  'Camouflage'     : [  2,  0,  2,  0,  0,  0,  0,  0, 'Defense', True  ],
  'Bone Ward'      : [ 99, 99, 99,  0,  0,  0,  0,  0, 'Defense', False ],
  'Flashbang'      : [ 99, 99, 99,  0,  0,  0,  0,  0, 'Defense', False ],
  'Barricade'      : [  4,  0,  4,  0,  0,  0,  0,  0, 'Defense', True  ],
  'Barbed Fence'   : [  2,  2,  8,  0,  0,  0,  0,  0, 'Defense', True  ],

  'Unarmed'        : [ 99, 99, 99,  1,  3,  0,  0,  0, 'Weapon',  False ],
  'Knife'          : [  0,  1,  1,  2,  5,  0,  0,  0, 'Weapon',  True  ],
  'Spear'          : [  1,  1,  2,  3,  6,  0,  0,  0, 'Weapon',  True  ],
  'Axe'            : [  2,  1,  4,  2, 10,  0,  0,  0, 'Weapon',  True  ],
  'Machete'        : [  1,  2,  4,  4,  7,  0,  0,  0, 'Weapon',  True  ],
  'Pistol'         : [  0,  2, 10,  5,  8,  1,  0,  0, 'Weapon',  True  ],
  'Rifle'          : [  0,  4, 20,  6, 12,  2,  0,  0, 'Weapon',  True  ],
  'Flame Thrower'  : [  0,  6, 40,  8, 14,  4,  0,  0, 'Weapon',  True  ],
  'Machine Gun'    : [  0,  8, 40,  6, 18,  4,  0,  0, 'Weapon',  True  ],
  'Jabberwocky'    : [ 99, 99, 99,  8, 14,  0,  0,  0, 'Weapon',  False ],
  'Eldritch Staff' : [ 99, 99, 99, 10, 16,  0,  1,  0, 'Weapon',  False ],
  'Infernal Skull' : [ 99, 99, 99, 14, 20,  0,  2,  0, 'Weapon',  False ],
  'Soul Scepter'   : [ 99, 99, 99, 20, 20,  0,  4,  0, 'Weapon',  False ],

  'Clothes'        : [ 99, 99, 99,  0,  0,  0,  0,  0, 'Armor',   False ],
  'Wooden Shield'  : [  1,  0,  1,  0,  0,  0,  0,  1, 'Armor',   True  ],
  'Tribal Garb'    : [  1,  1,  2,  0,  0,  0,  0,  2, 'Armor',   True  ],
  'C. Fiber Vest'  : [  0,  4,  6,  0,  0,  0,  0,  3, 'Armor',   True  ],
  'Body Armor'     : [  0,  8,  8,  0,  0,  0,  0,  4, 'Armor',   True  ],
  'Shaman Charm'   : [ 99, 99, 99,  0,  0,  0,  0,  5, 'Armor',   False ],
  'Yuggoth Cloak'  : [ 99, 99, 99,  0,  0,  0,  0, 10, 'Armor',   False ],

}

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Item:

  # Constructor

  def __init__( self, name ):

    assert( name in item_table )

    self.name       = name
    self.equipped   = False
    self.wood_cost  = item_table[self.name][0]
    self.metal_cost = item_table[self.name][1]
    self.mental_req = item_table[self.name][2]
    self.dmg_min    = item_table[self.name][3]
    self.dmg_max    = item_table[self.name][4]
    self.ammo_cost  = item_table[self.name][5]
    self.stam_cost  = item_table[self.name][6]
    self.armor      = item_table[self.name][7]
    self.type       = item_table[self.name][8]
    self.craftable  = item_table[self.name][9]
    self.free       = True

    # Assign effect text

    self.effect = []

    if self.name in effect_table:
      self.effect = effect_table[self.name]

  # Return average damage

  def get_avg_dmg( self ):

    return ( self.dmg_min + self.dmg_max ) / 2.0

  # Print debug information

  def debug( self ):

    print self.name, str( self.dmg_min ) + '-' + str( self.dmg_max ) + 'DMG', \
          str( self.armor ) + 'DEF', \
          '(' + str( self.wood_cost ) + ',' + str( self.metal_cost ) + ')', \
          '(' + str( self.ammo_cost ) + ',' + str( self.stam_cost ) + ')'
