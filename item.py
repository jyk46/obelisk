#=========================================================================
# item.py
#=========================================================================
# Class for equipment (weapon, armor, misc) that can be held by the
# inventories of expeditions.

#-------------------------------------------------------------------------
# Utility Tables
#-------------------------------------------------------------------------

# Possible items

item_table = {

  # name             wco mco min max amm sta arm

  'Knife'         : [  0,  1,  2,  5,  0,  0,  0, ],
  'Spear'         : [  1,  1,  3,  6,  0,  0,  0, ],
  'Axe'           : [  2,  1,  2, 10,  0,  0,  0, ],
  'Machete'       : [  1,  2,  4,  7,  0,  0,  0, ],
  'Pistol'        : [  0,  2,  5,  8,  1,  0,  0, ],
  'Rifle'         : [  0,  4,  6, 12,  2,  0,  0, ],
  'FireThrower'   : [  0,  6,  8, 14,  4,  0,  0, ],
  'MachineGun'    : [  0,  8,  6, 18,  4,  0,  0, ],
  'Jabberwocky'   : [ 99, 99,  8, 14,  0,  0,  0, ],
  'EldritchStaff' : [ 99, 99, 10, 16,  0,  1,  0, ],
  'InfernalSkull' : [ 99, 99, 14, 20,  0,  2,  0, ],
  'SoulScepter'   : [ 99, 99, 20, 20,  0,  4,  0, ],

  'WoodenShield'  : [  1,  0,  0,  0,  0,  0,  1, ],
  'TribalGarb'    : [  1,  1,  0,  0,  0,  0,  2, ],
  'CFiberVest'    : [  0,  4,  0,  0,  0,  0,  3, ],
  'BodyArmor'     : [  0,  8,  0,  0,  0,  0,  4, ],
  'ShamanCharm'   : [ 99, 99,  0,  0,  0,  0,  5, ],
  'YuggothCloak'  : [ 99, 99,  0,  0,  0,  0, 10, ],

}

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Item():

  # Constructor

  def __init__( self, name, fixed=100 ):

    assert( name in item_table )

    self.name       = name
    self.equipped   = False
    self.fixed      = fixed
    self.wood_cost  = item_table[name][0]
    self.metal_cost = item_table[name][1]
    self.dmg_min    = item_table[name][2]
    self.dmg_max    = item_table[name][3]
    self.ammo_cost  = item_table[name][4]
    self.stam_cost  = item_table[name][5]
    self.armor      = item_table[name][6]

  # Check if item is usable (i.e., fixed )

  def is_fixed( self ):
    return ( self.fixed == 100 )
