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

  def __add__( self, inv ):

    sum_inv = Inventory()

    sum_inv.food  = self.food  + inv.food
    sum_inv.wood  = self.wood  + inv.wood
    sum_inv.metal = self.metal + inv.metal
    sum_inv.ammo  = self.ammo  + inv.ammo
    sum_inv.items = self.items + inv.items

    return sum_inv

  # Overload - operator for splitting inventories

  def __sub__( self, inv ):

    assert( inv.food  <= self.food  )
    assert( inv.wood  <= self.wood  )
    assert( inv.metal <= self.metal )
    assert( inv.ammo  <= self.ammo  )

    diff_inv = Inventory()

    diff_inv.food  = self.food  - inv.food
    diff_inv.wood  = self.wood  - inv.wood
    diff_inv.metal = self.metal - inv.metal
    diff_inv.ammo  = self.ammo  - inv.ammo
    diff_inv.items = self.items

    for new_item in inv.items:
      for i, old_item in enumerate( diff_inv.items ):
        if old_item == new_item:
          del diff_inv.items[i]
          break

    return diff_inv

  # Merge resources only

  def merge_resources( self, inv ):

    self.food  += inv.food
    self.wood  += inv.wood
    self.metal += inv.metal
    self.ammo  += inv.ammo

  # Get number of unreserved items for explore phase

  def get_free( self ):

    free = []

    for it in self.items:
      if it.free:
        free.append( it )

    return free

  # Reset free state of all items

  def reset_free( self ):

    for it in self.items:
      it.free = True

  # Print debug information

  def debug( self ):

    print 'F' + str( self.food ), 'W' + str( self.wood ), \
          'M' + str( self.metal ), 'A' + str( self.ammo )

    for it in self.items:
      it.debug()
