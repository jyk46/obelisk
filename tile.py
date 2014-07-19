#=========================================================================
# tile.py
#=========================================================================
# Tiles for the game map describing the terrain, enemy/item spawn, and
# event triggers. Used by the MapGenerator to construct a random map.

import pygame, sys, os
from pygame.locals import *

import random
import copy
import properties
import item
import enemy

#-------------------------------------------------------------------------
# Utility Tables
#-------------------------------------------------------------------------

# Possible terrain

terrain_table = {

  # name      image       mv  val   risk

  'Field' : [ 'field.png', 1, True, 'Low',

    [
      # prob  enemy
      [ 0.40, 'Wolf Pack' ],
      [ 0.20, 'Bee Swarm' ],
      [ 0.10, 'Panther'   ],
    ],

    [
      # prob min max
      [ 0.80,  1,  2 ], # food
      [ 0.20,  1,  2 ], # wood
      [ 0.00,  0,  0 ], # metal
      [ 0.00,  0,  0 ], # ammo
      [ 0.00,  0,  0 ], # item
    ],

    [
    ],

  ],

  'Jungle' : [ 'jungle.png', 1, True, 'Medium',

    [
      # prob  enemy
      [ 0.20, 'Wolf Pack' ],
      [ 0.20, 'Bee Swarm' ],
      [ 0.10, 'Panther'   ],
      [ 0.10, 'Gorilla'   ],
      [ 0.20, 'Native'    ],
    ],

    [
      # prob min max
      [ 0.90,  1,  2 ], # food
      [ 0.50,  1,  2 ], # wood
      [ 0.00,  0,  0 ], # metal
      [ 0.05,  1,  2 ], # ammo
      [ 0.10,  0,  0 ], # item
    ],

    [
      # prob  item
      [ 0.10, 'Pistol'  ],
      [ 0.50, 'Knife'   ],
      [ 0.30, 'Spear'   ],
      [ 0.10, 'Flashbang' ],
    ],

  ],

  'Deep Jungle' : [ 'deep_jungle.png', 2, True, 'High',

    [
      # prob  enemy
      [ 0.22, 'Panther'     ],
      [ 0.22, 'Gorilla'     ],
      [ 0.20, 'Raptor'      ],
      [ 0.20, 'Native'      ],
      [ 0.10, 'Cultist'     ],
      [ 0.01, 'Apparition'  ],
    ],

    [
      # prob min max
      [ 1.00,  2,  4 ], # food
      [ 0.80,  2,  4 ], # wood
      [ 0.00,  0,  0 ], # metal
      [ 0.05,  1,  2 ], # ammo
      [ 0.20,  0,  0 ], # item
    ],

    [
      # prob  item
      [ 0.04, 'Pistol'  ],
      [ 0.01, 'Rifle'   ],
      [ 0.40, 'Knife'   ],
      [ 0.25, 'Spear'   ],
      [ 0.10, 'Axe'     ],
      [ 0.05, 'Machete' ],
      [ 0.10, 'Flashbang' ],
      [ 0.05, 'Bone Ward' ],
    ],

  ],

  'Mountain' : [ 'mountain.png', 2, True, 'Medium',

    [
      # prob  enemy
      [ 0.30, 'Wolf Pack' ],
      [ 0.10, 'Bee Swarm' ],
      [ 0.20, 'Native'    ],
      [ 0.30, 'Giant'     ],
    ],

    [
      # prob min max
      [ 0.50,  1,  2 ], # food
      [ 0.30,  1,  2 ], # wood
      [ 0.10,  1,  1 ], # metal
      [ 0.00,  0,  0 ], # ammo
      [ 0.10,  0,  0 ], # item
    ],

    [
      # prob  item
      [ 0.75, 'Pistol'    ],
      [ 0.05, 'Rifle'     ],
      [ 0.10, 'Flashbang' ],
      [ 0.05, 'Bone Ward' ],
    ],

  ],

  'Cave' : [ 'cave.png', 1, True, 'Medium',

    [
      # prob  enemy
      [ 0.20, 'Anaconda' ],
      [ 0.20, 'Native'   ],
      [ 0.20, 'Giant'    ],
    ],

    [
      # prob min max
      [ 0.50,  1,  4 ], # food
      [ 0.00,  0,  0 ], # wood
      [ 0.10,  1,  2 ], # metal
      [ 0.10,  2,  4 ], # ammo
      [ 0.20,  0,  0 ], # item
    ],

    [
      # prob  item
      [ 0.50, 'Pistol'        ],
      [ 0.15, 'Rifle'         ],
      [ 0.05, 'C. Fiber Vest' ],
      [ 0.20, 'Flashbang'     ],
      [ 0.10, 'Bone Ward'     ],
    ],

  ],

  'Swamp' : [ 'swamp.png', 3, True, 'Medium',

    [
      # prob  enemy
      [ 0.40, 'Anaconda' ],
      [ 0.20, 'Mudman'   ],
      [ 0.20, 'Native'   ],
      [ 0.10, 'Deep One' ],
    ],

    [
      # prob min max
      [ 0.20,  1,  2 ], # food
      [ 0.10,  1,  2 ], # wood
      [ 0.10,  1,  2 ], # metal
      [ 0.10,  1,  2 ], # ammo
      [ 0.25,  0,  0 ], # item
    ],

    [
      # prob  item
      [ 0.80, 'Pistol'         ],
      [ 0.10, 'Rifle'          ],
      [ 0.01, 'Jabberwocky'    ],
      [ 0.05, 'Eldritch Staff' ],
      [ 0.04, 'Shaman Charm'   ],
    ],

  ],

  'Wreckage' : [ 'wreckage.png', 1, True, 'Low',

    [
      # prob  enemy
      [ 0.40, 'Wolf Pack'  ],
      [ 0.20, 'Native'     ],
      [ 0.20, 'Apparition' ],
    ],

    [
      # prob min max
      [ 0.80,  2,  4 ], # food
      [ 0.00,  0,  0 ], # wood
      [ 0.50,  1,  2 ], # metal
      [ 0.20,  2,  4 ], # ammo
      [ 0.30,  0,  0 ], # item
    ],

    [
      # prob  item
      [ 0.20, 'Binoculars'    ],
      [ 0.45, 'Pistol'        ],
      [ 0.10, 'Rifle'         ],
      [ 0.05, 'Flame Thrower' ],
      [ 0.05, 'C. Fiber Vest' ],
      [ 0.10, 'Flashbang'     ],
      [ 0.05, 'Bone Ward'     ],
    ],

  ],

  'Facility' : [ 'facility.png', 1, True, 'High',

    [
      # prob  enemy
      [ 0.30, 'Native'        ],
      [ 0.25, 'Cultist'       ],
      [ 0.20, 'Apparition'    ],
      [ 0.05, 'Dim. Shambler' ],
    ],

    [
      # prob min max
      [ 0.50,  1,  4 ], # food
      [ 0.00,  0,  0 ], # wood
      [ 0.30,  2,  4 ], # metal
      [ 0.25,  2,  6 ], # ammo
      [ 0.20,  0,  0 ], # item
    ],

    [
      # prob  item
      [ 0.45, 'Pistol'        ],
      [ 0.20, 'Rifle'         ],
      [ 0.05, 'Flame Thrower' ],
      [ 0.05, 'Machine Gun'   ],
      [ 0.05, 'C. Fiber Vest' ],
      [ 0.05, 'Body Armor'    ],
      [ 0.10, 'Flashbang'     ],
      [ 0.05, 'Bone Ward'     ],
    ],

  ],

  'Ritual Site' : [ 'ritual.png', 1, True, 'Very High',

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
      [ 0.10,  0,  0 ], # item
    ],

    [
      # prob  item
      [ 0.50, 'Eldritch Staff' ],
      [ 0.20, 'Infernal Skull' ],
      [ 0.05, 'Soul Scepter'   ],
      [ 0.20, 'Shaman Charm'   ],
      [ 0.05, 'Yuggoth Cloak'  ],
    ],

  ],

  'Obelisk' : [ 'obelisk.png', 1, True, '????',

    [
      # prob  enemy
      [ 0.05, 'Dim. Shambler'   ],
      [ 0.01, 'The Unspeakable' ],
    ],

    [
      # prob min max
      [ 0.00,  0,  0 ], # food
      [ 0.00,  0,  0 ], # wood
      [ 0.00,  0,  0 ], # metal
      [ 0.00,  0,  0 ], # ammo
      [ 0.00,  0,  0 ], # item
    ],

    [
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

    # Set image

    self.img_path     = properties.TILE_PATH + terrain_table[self.terrain][0]
    self.surface      = pygame.image.load( self.img_path )
    self.image        = self.surface.convert()
    self.rect         = self.image.get_rect()
    self.abs_x        = self.pos_x * properties.TILE_WIDTH
    self.abs_y        = self.pos_y * properties.TILE_HEIGHT
    self.rect.topleft = self.abs_x, self.abs_y

    self.bg_path      = properties.BG_PATH + terrain_table[self.terrain][0]

    # Terrain-specific information

    self.move_cost   = terrain_table[self.terrain][1]
    self.valid       = terrain_table[self.terrain][2]
    self.risk        = terrain_table[self.terrain][3]
    self.enemy_rates = terrain_table[self.terrain][4]
    self.rsrc_rates  = copy.deepcopy( terrain_table[self.terrain][5] )
    self.item_rates  = terrain_table[self.terrain][6]

    self.has_survivor = False

    # Overlays for movement

    self.moveable = False
    self.selected = False
    self.fog      = True

    self.move_surface      = pygame.image.load( properties.TILE_PATH + 'blue.png' )
    self.move_surface.set_alpha( 128 )
    self.move_rect         = self.move_surface.get_rect()
    self.move_rect.topleft = 0, 0

    self.sel_surface      = pygame.image.load( properties.TILE_PATH + 'red.png' )
    self.sel_surface.set_alpha( 128 )
    self.sel_rect         = self.sel_surface.get_rect()
    self.sel_rect.topleft = 0, 0

    self.fog_surface      = pygame.image.load( properties.TILE_PATH + 'black.png' )
    self.fog_rect         = self.fog_surface.get_rect()
    self.fog_rect.topleft = 0, 0
    self.fog_surface.set_alpha( 255 )

    # Overlay for rescuable survivor

    self.step_count = 0
    self.draw_count = 0

    self.survivor_img_path     = properties.TILE_PATH + 'fire'
    self.survivor_surface      = pygame.image.load( self.survivor_img_path + '0.png' )
    self.survivor_surface.set_colorkey( self.survivor_surface.get_at( ( 0, 0 ) ), RLEACCEL )
    self.survivor_surface      = self.survivor_surface.convert()
    self.survivor_rect         = self.survivor_surface.get_rect()
    self.survivor_rect.center  = self.fog_rect.center

  # Roll for enemy spawned during defend phase. Currently only one enemy
  # is spawned per encounter. If no enemy is spawned, None is returned.

  def roll_enemy( self, bonus ):

    roll = random.random()
    prob = 0.0

    for _enemy in self.enemy_rates:

      prob += _enemy[0] * bonus

      if roll < prob:
        return enemy.Enemy( _enemy[1] )

    return None

  # Roll for resources. One try per survivor who is in the scavenge
  # party. The base scavenge probability for each resource is modified by
  # the rolling survivor's mental bonus.

  def roll_resources( self, survivors ):

    loot = [ 0, 0, 0, 0 ]

    for _survivor in survivors:

      for i, rsrc in enumerate( self.rsrc_rates[:-1] ):

        roll = random.random()
        prob = rsrc[0] + ( _survivor.get_mental_bonus() * properties.RSRC_BONUS_MULT )

        prob *= ( 1.00 + _survivor.get_attributes().scavenge_bonus )

        if roll < prob:

          loot[i] += random.randint( rsrc[1], rsrc[2] )

    # Reduce the probability of scavenging resources if the scavenge was
    # successful for a given resource. This is to prevent camping one
    # safe tile for infinite resources.

    for i in range( len( self.rsrc_rates[:-1] ) ):

      if loot[i] > 0:
        self.rsrc_rates[i][0] *= properties.RSRC_REDUC_RATE

    return loot

  # Roll for items. Unlike rolling for resources, only one item can be
  # found per scavenge party instead of one per survivor in the
  # party. The combined mental bonuses of the survivors is used to modify
  # the item find probability.

  def roll_items( self, survivors ):

    tot_bonus       = 0
    attribute_bonus = 0.0

    for _survivor in survivors:
      tot_bonus       += _survivor.get_mental_bonus()
      attribute_bonus  = max( attribute_bonus, _survivor.get_attributes().scavenge_bonus )

    get_roll = random.random()
    get_prob = self.rsrc_rates[-1][0] + ( tot_bonus * properties.ITEM_BONUS_MULT )

    get_prob *= ( 1.00 + attribute_bonus )

    if get_roll < get_prob:

      item_roll = random.random()
      item_prob = 0.0

      for _item in self.item_rates:

        item_prob += _item[0]

        if item_roll < item_prob:
          return item.Item( _item[1] )

    return None

  # Calculate chance of finding materials during scavenge

  def get_yield( self ):

    prob_nothing = 1.00

    for rate in self.rsrc_rates:
      prob_nothing *= 1.00 - rate[0]

    prob_something = 1.00 - prob_nothing

    return '%.1f' % ( prob_something * 100 ) + '%'

  # Update graphics

  def update( self, cam_x, cam_y ):

    # Update position relative to camera

    self.rect.top  = self.abs_y - cam_y
    self.rect.left = self.abs_x - cam_x

    # Draw campfire if night and there is a rescuable survivor here

    if not self.fog and ( self.fog_surface.get_alpha() > properties.NIGHT_ALPHA - 10 ) \
      and ( self.fog_surface.get_alpha() < 255 ) and self.has_survivor:

      if self.step_count == properties.FRAME_SWITCH:

        self.survivor_surface = pygame.image.load( self.survivor_img_path + str( self.draw_count ) + '.png' )
        self.survivor_surface.set_colorkey( self.survivor_surface.get_at( ( 0, 0 ) ), RLEACCEL )
        self.survivor_surface = self.survivor_surface.convert()

        self.draw_count += 1
        if self.draw_count > 3:
          self.draw_count = 0

        self.step_count = 0

      else:
        self.step_count += 1

  # Draw overlays if necessary

  def draw_overlay( self ):

    rect_updates = []

    self.image = self.surface.convert()

    if self.fog or ( self.fog_surface.get_alpha() < 255 ):
      rect_updates += [ self.image.blit( self.fog_surface, self.fog_rect ) ]

    if self.moveable:
      if self.selected:
        rect_updates += [ self.image.blit( self.sel_surface, self.sel_rect ) ]
      else:
        rect_updates += [ self.image.blit( self.move_surface, self.move_rect ) ]

    # Draw campfire if night and there is a rescuable survivor here

    if not self.fog and ( self.fog_surface.get_alpha() > properties.NIGHT_ALPHA - 10 ) \
      and ( self.fog_surface.get_alpha() < 255 ) and self.has_survivor:

      rect_updates += [ self.image.blit( self.survivor_surface, self.survivor_rect ) ]

    return rect_updates

  # Draw graphics

  def draw( self, surface ):

    rect_updates  = self.draw_overlay()
    rect_updates += [ surface.blit( self.image, self.rect ) ]

    return rect_updates

  # Overload == operator to return true if position matches

  def __eq__( self, _tile ):
    return ( self.pos_x == _tile.pos_x ) and ( self.pos_y == _tile.pos_y )

  # Print debug information

  def debug( self ):

    print self.terrain, '(' + str( self.pos_x ) + ',' + str( self.pos_y ) + ')', \
          str( self.move_cost ) + '/' + str( self.valid )

    print self.enemy_rates
    print self.rsrc_rates
    print self.item_rates
