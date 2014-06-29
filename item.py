#=========================================================================
# item.py
#=========================================================================
# Class for equipment (weapon, armor, misc) that can be held by the
# inventories of expeditions.

#-------------------------------------------------------------------------
# Utility Tables
#-------------------------------------------------------------------------

# Special item types

NONE, CAMPINGKIT, BINOCULARS, FIRSTAID, ANTIBIOTICS = range( 5 )

# Possible items

item_table = {

  # name             wco mco min max amm sta arm  special

  'Camping Kit'   : [ 99, 99,  0,  0,  0,  0,  0, CAMPINGKIT  ],
  'Binoculars'    : [ 99, 99,  0,  0,  0,  0,  0, BINOCULARS  ],
  'First Aid'     : [ 99, 99,  0,  0,  0,  0,  0, FIRSTAID    ],
  'Antibiotics'   : [ 99, 99,  0,  0,  0,  0,  0, ANTIBIOTICS ],

  'Knife'         : [  0,  1,  2,  5,  0,  0,  0, NONE        ],
  'Spear'         : [  1,  1,  3,  6,  0,  0,  0, NONE        ],
  'Axe'           : [  2,  1,  2, 10,  0,  0,  0, NONE        ],
  'Machete'       : [  1,  2,  4,  7,  0,  0,  0, NONE        ],
  'Pistol'        : [  0,  2,  5,  8,  1,  0,  0, NONE        ],
  'Rifle'         : [  0,  4,  6, 12,  2,  0,  0, NONE        ],
  'Flame Thrower' : [  0,  6,  8, 14,  4,  0,  0, NONE        ],
  'Machine Gun'   : [  0,  8,  6, 18,  4,  0,  0, NONE        ],
  'Jabberwocky'   : [ 99, 99,  8, 14,  0,  0,  0, NONE        ],
  'Eldritch Staff': [ 99, 99, 10, 16,  0,  1,  0, NONE        ],
  'Infernal Skull': [ 99, 99, 14, 20,  0,  2,  0, NONE        ],
  'Soul Scepter'  : [ 99, 99, 20, 20,  0,  4,  0, NONE        ],

  'Wooden Shield' : [  1,  0,  0,  0,  0,  0,  1, NONE        ],
  'Tribal Garb'   : [  1,  1,  0,  0,  0,  0,  2, NONE        ],
  'C. Fiber Vest' : [  0,  4,  0,  0,  0,  0,  3, NONE        ],
  'Body Armor'    : [  0,  8,  0,  0,  0,  0,  4, NONE        ],
  'Shaman Charm'  : [ 99, 99,  0,  0,  0,  0,  5, NONE        ],
  'Yuggoth Cloak' : [ 99, 99,  0,  0,  0,  0, 10, NONE        ],

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
    self.wood_cost  = item_table[self.name][0]
    self.metal_cost = item_table[self.name][1]
    self.dmg_min    = item_table[self.name][2]
    self.dmg_max    = item_table[self.name][3]
    self.ammo_cost  = item_table[self.name][4]
    self.stam_cost  = item_table[self.name][5]
    self.armor      = item_table[self.name][6]
    self.special    = item_table[self.name][7]

  # Check if item is usable (i.e., fixed )

  def is_fixed( self ):
    return ( self.fixed == 100 )

  # Print debug information

  def debug( self ):

    print self.name, str( self.dmg_min ) + '-' + str( self.dmg_max ) + 'DMG', \
          str( self.armor ) + 'ARM', \
          '(' + str( self.wood_cost ) + ',' + str( self.metal_cost ) + ')', \
          '(' + str( self.ammo_cost ) + ',' + str( self.stam_cost ) + ')'
