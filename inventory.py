#=========================================================================
# inventory.py
#=========================================================================
# Inventory of food, materials, and Items (equipment) corresponding to a
# unique Expedition.

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

  # Overload + operator for merging inventories

  def __add__( self, inv ):

    sum_inv = Inventory()

    sum_inv.food  = self.inv.food  + inv.food
    sum_inv.wood  = self.inv.wood  + inv.wood
    sum_inv.metal = self.inv.metal + inv.metal
    sum_inv.ammo  = self.inv.ammo  + inv.ammo
    sum_inv.items = self.inv.items + inv.items

    return sum_inv

  # Overload - operator for splitting inventories

  def __sub__( self, inv ):

    assert( inv.food  <= self.inv.food  )
    assert( inv.wood  <= self.inv.wood  )
    assert( inv.metal <= self.inv.metal )
    assert( inv.ammo  <= self.inv.ammo  )

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

  # Print debug information

  def debug( self ):

    print 'F' + str( self.food ), 'W' + str( self.wood ), \
          'M' + str( self.metal ), 'A' + str( self.ammo )

    for it in self.items:
      it.debug()
