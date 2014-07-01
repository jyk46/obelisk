#=========================================================================
# tile.py
#=========================================================================
# Tiles for the game map describing the terrain, enemy/item spawn, and
# event triggers. Used by the MapGenerator to construct a random map.

import pygame, sys, os
from pygame.locals import *

import properties

#-------------------------------------------------------------------------
# Utility Tables
#-------------------------------------------------------------------------

# Possible terrain

terrain_table = {

  # name      image       mv  val   camp

  'Field' : [ 'field.png', 1, True, True,

    [
      # prob  enemy
      [ 0.40, 'Wolf Pack' ],
      [ 0.20, 'Bee Swarm' ],
      [ 0.10, 'Panther'   ],
      [ 0.30, 'None'      ],
    ],

    [
      # prob min max
      [ 0.80,  1,  4 ], # food
      [ 0.20,  1,  2 ], # wood
      [ 0.00,  0,  0 ], # metal
      [ 0.00,  0,  0 ], # ammo
    ],

    [
      # prob  item
      [ 1.00, 'None' ],
    ],

  ],

  'Jungle' : [ 'jungle.png', 1, True, True,

    [
      # prob  enemy
      [ 0.20, 'Wolf Pack' ],
      [ 0.20, 'Bee Swarm' ],
      [ 0.10, 'Panther'   ],
      [ 0.10, 'Gorilla'   ],
      [ 0.20, 'Native'    ],
      [ 0.20, 'None'      ],
    ],

    [
      # prob min max
      [ 0.90,  2,  6 ], # food
      [ 0.50,  2,  4 ], # wood
      [ 0.00,  0,  0 ], # metal
      [ 0.05,  1,  2 ], # ammo
    ],

    [
      # prob  item
      [ 0.05, 'Pistol'  ],
      [ 0.10, 'Knife'   ],
      [ 0.10, 'Spear'   ],
      [ 0.75, 'None'    ],
    ],

  ],

  'Deep Jungle' : [ 'deep_jungle.png', 2, True, True,

    [
      # prob  enemy
      [ 0.22, 'Panther'     ],
      [ 0.22, 'Gorilla'     ],
      [ 0.20, 'Raptor'      ],
      [ 0.20, 'Native'      ],
      [ 0.10, 'Cultist'     ],
      [ 0.01, 'Apparition'  ],
      [ 0.05, 'None'        ],
    ],

    [
      # prob min max
      [ 1.00,  4,  8 ], # food
      [ 0.80,  4,  6 ], # wood
      [ 0.00,  0,  0 ], # metal
      [ 0.05,  1,  2 ], # ammo
    ],

    [
      # prob  item
      [ 0.04, 'Pistol'  ],
      [ 0.01, 'Rifle'   ],
      [ 0.10, 'Knife'   ],
      [ 0.10, 'Spear'   ],
      [ 0.05, 'Axe'     ],
      [ 0.05, 'Machete' ],
      [ 0.65, 'None'    ],
    ],

  ],

  'Mountain' : [ 'mountain.png', 2, True, True,

    [
      # prob  enemy
      [ 0.30, 'Wolf Pack' ],
      [ 0.10, 'Bee Swarm' ],
      [ 0.20, 'Native'    ],
      [ 0.30, 'Giant'     ],
      [ 0.10, 'None'      ],
    ],

    [
      # prob min max
      [ 0.50,  1,  4 ], # food
      [ 0.30,  1,  2 ], # wood
      [ 0.10,  1,  2 ], # metal
      [ 0.00,  0,  0 ], # ammo
    ],

    [
      # prob  item
      [ 0.10, 'Camping Kit'   ],
      [ 0.05, 'First Aid'     ],
      [ 0.05, 'Antibiotics'   ],
      [ 0.05, 'Pistol'        ],
      [ 0.75, 'None'          ],
    ],

  ],

  'Cave' : [ 'cave.png', 1, True, False,

    [
      # prob  enemy
      [ 0.20, 'Anaconda' ],
      [ 0.20, 'Native'   ],
      [ 0.20, 'Giant'    ],
      [ 0.40, 'None'     ],
    ],

    [
      # prob min max
      [ 0.50,  2,  4 ], # food
      [ 0.00,  0,  0 ], # wood
      [ 0.10,  2,  3 ], # metal
      [ 0.10,  2,  4 ], # ammo
    ],

    [
      # prob  item
      [ 0.20, 'Camping Kit'   ],
      [ 0.10, 'First Aid'     ],
      [ 0.10, 'Antibiotics'   ],
      [ 0.10, 'Pistol'        ],
      [ 0.05, 'Rifle'         ],
      [ 0.01, 'C. Fiber Vest' ],
      [ 0.44, 'None'          ],
    ],

  ],

  'Swamp' : [ 'swamp.png', 3, True, False,

    [
      # prob  enemy
      [ 0.40, 'Anaconda' ],
      [ 0.20, 'Mudman'   ],
      [ 0.20, 'Native'   ],
      [ 0.10, 'Deep One' ],
      [ 0.10, 'None'     ],
    ],

    [
      # prob min max
      [ 0.20,  1,  2 ], # food
      [ 0.10,  1,  2 ], # wood
      [ 0.00,  0,  0 ], # metal
      [ 0.10,  1,  2 ], # ammo
    ],

    [
      # prob  item
      [ 0.10, 'Pistol'         ],
      [ 0.07, 'Rifle'          ],
      [ 0.01, 'Jabberwocky'    ],
      [ 0.01, 'Eldritch Staff' ],
      [ 0.01, 'Shaman Charm'   ],
      [ 0.80, 'None'           ],
    ],

  ],

  'Wreckage' : [ 'wreckage.png', 1, True, False,

    [
      # prob  enemy
      [ 0.40, 'Wolf Pack'  ],
      [ 0.20, 'Native'     ],
      [ 0.20, 'Apparition' ],
      [ 0.20, 'None'       ],
    ],

    [
      # prob min max
      [ 0.80,  2,  6 ], # food
      [ 0.00,  0,  0 ], # wood
      [ 0.50,  1,  2 ], # metal
      [ 0.20,  2,  6 ], # ammo
    ],

    [
      # prob  item
      [ 0.30, 'Camping Kit'   ],
      [ 0.15, 'First Aid'     ],
      [ 0.10, 'Antibiotics'   ],
      [ 0.24, 'Pistol'        ],
      [ 0.09, 'Rifle'         ],
      [ 0.01, 'Flame Thrower' ],
      [ 0.01, 'C. Fiber Vest' ],
      [ 0.10, 'None'          ],
    ],

  ],

  'Facility' : [ 'facility.png', 1, True, False,

    [
      # prob  enemy
      [ 0.30, 'Native'        ],
      [ 0.25, 'Cultist'       ],
      [ 0.20, 'Apparition'    ],
      [ 0.05, 'Dim. Shambler' ],
      [ 0.20, 'None'          ],
    ],

    [
      # prob min max
      [ 0.04,  1,  3 ], # food
      [ 0.20,  0,  0 ], # wood
      [ 0.30,  2,  4 ], # metal
      [ 0.25,  2,  4 ], # ammo
    ],

    [
      # prob  item
      [ 0.25, 'Camping Kit'   ],
      [ 0.40, 'First Aid'     ],
      [ 0.20, 'Antibiotics'   ],
      [ 0.15, 'Pistol'        ],
      [ 0.06, 'Rifle'         ],
      [ 0.01, 'Flame Thrower' ],
      [ 0.01, 'Machine Gun'   ],
      [ 0.01, 'C. Fiber Vest' ],
      [ 0.01, 'Body Armor'    ],
      [ 0.10, 'None'          ],
    ],

  ],

  'Ritual Site' : [ 'ritual.png', 1, True, False,

    [
      # prob  enemy
      [ 0.30, 'Cultist'         ],
      [ 0.35, 'Apparition'      ],
      [ 0.30, 'Dim. Shambler'   ],
      [ 0.05, 'The Unspeakable' ],
    ],

    [
      # prob min max
      [ 0.00,  0,  0 ], # food
      [ 0.00,  0,  0 ], # wood
      [ 0.00,  0,  0 ], # metal
      [ 0.00,  0,  0 ], # ammo
    ],

    [
      # prob  item
      [ 0.02,  'Eldritch Staff' ],
      [ 0.01,  'Infernal Skull' ],
      [ 0.005, 'Soul Scepter'   ],
      [ 0.01,  'Shaman Charm'   ],
      [ 0.005, 'Yuggoth Cloak'  ],
      [ 0.95,  'None'           ],
    ],

  ],

  'Obelisk' : [ 'obelisk.png', 1, True, False,

    [
      # prob  enemy
      [ 0.05, 'Dim. Shambler'   ],
      [ 0.01, 'The Unspeakable' ],
      [ 0.94, 'None'            ],
    ],

    [
      # prob min max
      [ 0.00,  0,  0 ], # food
      [ 0.00,  0,  0 ], # wood
      [ 0.00,  0,  0 ], # metal
      [ 0.00,  0,  0 ], # ammo
    ],

    [
      # prob  item
      [ 1.00, 'None' ],
    ],

  ],

}

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Tile( pygame.sprite.Sprite ):

  # Constructor

  def __init__( self, terrain, pos_x, pos_y ):

    assert( terrain in terrain_table )

    pygame.sprite.Sprite.__init__( self )

    self.terrain  = terrain
    self.pos_x    = pos_x
    self.pos_y    = pos_y
    self.has_camp = False

    # Set image

    self.img_path     = properties.TILE_PATH + terrain_table[self.terrain][0]
    self.surface      = pygame.image.load( self.img_path )
    self.image        = self.surface.convert()
    self.rect         = self.image.get_rect()
    self.abs_x        = self.pos_x * properties.TILE_WIDTH
    self.abs_y        = self.pos_y * properties.TILE_HEIGHT
    self.rect.topleft = self.abs_x, self.abs_y

    # Terrain-specific information

    self.move_cost   = terrain_table[self.terrain][1]
    self.valid       = terrain_table[self.terrain][2]
    self.campable    = terrain_table[self.terrain][3]
    self.enemy_rates = terrain_table[self.terrain][4]
    self.mat_rates   = terrain_table[self.terrain][5]
    self.item_rates  = terrain_table[self.terrain][6]

  # Update graphics

  def update( self, cam_x, cam_y ):

    self.rect.top  = self.abs_y - cam_y
    self.rect.left = self.abs_x - cam_x

  # Overload hash operator to allow Tile objects to be used in dictionaries

#  def __hash__( self ):
#    return hash( ( self.pos_x, self.pos_y ) )

  # Overload == operator to return true if position matches

  def __eq__( self, ti ):
    return ( self.pos_x == ti.pos_x ) and ( self.pos_y == ti.pos_y )

  # Print debug information

  def debug( self ):

    print self.terrain, '(' + str( self.pos_x ) + ',' + str( self.pos_y ) + ')', \
          str( self.move_cost ) + '/' + str( self.valid ) + '/' + str( self.campable )

    print self.enemy_rates
    print self.mat_rates
    print self.item_rates
