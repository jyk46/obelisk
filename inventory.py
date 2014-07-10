#=========================================================================
# inventory.py
#=========================================================================
# Inventory of food, materials, and Items (equipment) corresponding to a
# unique Expedition.

import pygame, sys, os
from pygame.locals import *

import properties
import item

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Inventory():

  # Constructor

  def __init__( self, food=0, wood=0, metal=0, ammo=0, items=[] ):

    self.food  = food
    self.wood  = wood
    self.metal = metal
    self.ammo  = ammo
    self.items = items

    # Text graphics

    self.font         = pygame.font.Font( properties.DEFAULT_FONT, 14 )
    self.text         = 'FOOD: ' + str( self.food ) + ', '\
                      + 'WOOD: ' + str( self.wood ) + ', '\
                      + 'METAL: ' + str( self.metal ) + ', '\
                      + 'AMMO: ' + str( self.ammo )
    self.text_surface = self.font.render( self.text, 1, (0,0,0) )
    self.text_rect    = self.text_surface.get_rect()

  # Overload + operator for merging inventories

  def __add__( self, _inventory ):

    sum_inventory = Inventory()

    sum_inventory.food  = self.food  + _inventory.food
    sum_inventory.wood  = self.wood  + _inventory.wood
    sum_inventory.metal = self.metal + _inventory.metal
    sum_inventory.ammo  = self.ammo  + _inventory.ammo
    sum_inventory.items = self.items + _inventory.items

    return sum_inventory

  # Overload - operator for splitting inventories

  def __sub__( self, _inventory ):

    assert( _inventory.food  <= self.food  )
    assert( _inventory.wood  <= self.wood  )
    assert( _inventory.metal <= self.metal )
    assert( _inventory.ammo  <= self.ammo  )

    diff_inventory = Inventory()

    diff_inventory.food  = self.food  - _inventory.food
    diff_inventory.wood  = self.wood  - _inventory.wood
    diff_inventory.metal = self.metal - _inventory.metal
    diff_inventory.ammo  = self.ammo  - _inventory.ammo
    diff_inventory.items = self.items

    for new_item in _inventory.items:
      for i, old_item in enumerate( diff_inventory.items ):
        if old_item == new_item:
          del diff_inventory.items[i]
          break

    return diff_inventory

  # Merge resources only

  def merge_resources( self, _inventory ):

    self.food  += _inventory.food
    self.wood  += _inventory.wood
    self.metal += _inventory.metal
    self.ammo  += _inventory.ammo

  # Get number of unreserved items for explore phase

  def get_free( self ):

    free = []

    for _item in self.items:
      if _item.free:
        free.append( _item )

    return free

  # Reset free state of all items

  def reset_free( self ):

    for _item in self.items:
      _item.free = True

  # Print debug information

  def debug( self ):

    print 'F' + str( self.food ), 'W' + str( self.wood ), \
          'M' + str( self.metal ), 'A' + str( self.ammo )

    for _item in self.items:
      _item.debug()
