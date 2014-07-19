#=========================================================================
# expedition.py
#=========================================================================
# One or more survivors are grouped into Expeditions, which are what is
# actually shown on the map. Expeditions have local inventories for food,
# material, and equipment.

import pygame, sys, os
from pygame.locals import *

import random
import properties
import utils
import survivor
import inventory
import tile

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Expedition( pygame.sprite.Sprite ):

  # Return modified view range

  def get_view_range( self ):

    bonus = 0

    for _item in self._inventory.items:
      if _item.name == 'Binoculars':
        bonus = 2
        break

    return self.view_range + bonus

  # Clear map fog around expedition tile

  def unfog( self ):

    visited  = []
    frontier = [ self.pos_tile ]

    self.pos_tile.fog = False

    # Iterate over frontiers until maximum cost is reached

    for i in range( self.get_view_range() ):

      next_frontier = []

      # Search all tiles in the current frontier

      for ti in frontier:

        # Unfog neighboring tiles within map bounds

        if ti.pos_y > 0:
          if ( self.map[ti.pos_x][ti.pos_y-1] not in visited ) \
            and ( self.map[ti.pos_x][ti.pos_y-1] not in next_frontier ):
            self.map[ti.pos_x][ti.pos_y-1].fog = False
            next_frontier.append( self.map[ti.pos_x][ti.pos_y-1] )

        if ti.pos_x < ( properties.MAP_SIZE - 1 ):
          if self.map[ti.pos_x+1][ti.pos_y] not in visited \
            and ( self.map[ti.pos_x+1][ti.pos_y] not in next_frontier ):
            self.map[ti.pos_x+1][ti.pos_y].fog = False
            next_frontier.append( self.map[ti.pos_x+1][ti.pos_y] )

        if ti.pos_y < ( properties.MAP_SIZE - 1 ):
          if self.map[ti.pos_x][ti.pos_y+1] not in visited \
            and ( self.map[ti.pos_x][ti.pos_y+1] not in next_frontier ):
            self.map[ti.pos_x][ti.pos_y+1].fog = False
            next_frontier.append( self.map[ti.pos_x][ti.pos_y+1] )

        if ti.pos_x > 0:
          if self.map[ti.pos_x-1][ti.pos_y] not in visited \
            and ( self.map[ti.pos_x-1][ti.pos_y] not in next_frontier ):
            self.map[ti.pos_x-1][ti.pos_y].fog = False
            next_frontier.append( self.map[ti.pos_x-1][ti.pos_y] )

        # Mark tile in frontier as visited

        visited.append( ti )

      # Swap frontiers when all tiles in current frontier are processed

      frontier = next_frontier

  # Constructor

  def __init__( self, pos_tile, survivors, _inventory, map, img_idx=-1 ):

    pygame.sprite.Sprite.__init__( self, self.groups )

    self.pos_tile    = pos_tile
    self.survivors   = survivors
    self._inventory  = _inventory
    self.map         = map
    self.path_dic    = {}
    self.move_route  = []
    self.view_range  = 4
    self.direction   = 'south'
    self.step_count  = 0
    self.draw_count  = 0

    # Unfog initial starting area

    self.unfog()

    # Set image and make background transparent

    if img_idx < 0:
      self.img_roll = random.randint( 0, 3 )
    else:
      self.img_roll = img_idx

    self.img_path     = properties.EXPD_PATH + 'hero' + str( self.img_roll ) + '_'
    self.surface      = pygame.image.load( self.img_path + self.direction + str( self.draw_count ) + '.png' )
    self.surface.set_colorkey( self.surface.get_at( ( 0, 0 ) ), RLEACCEL )
    self.image        = self.surface.convert()
    self.rect         = self.image.get_rect()
    self.abs_x        = self.pos_tile.pos_x * properties.TILE_WIDTH
    self.abs_y        = self.pos_tile.pos_y * properties.TILE_HEIGHT
    self.rect.topleft = self.pos_tile.rect.topleft

  # Return list of free survivors which can take orders

  def get_free( self ):

    free = []

    for _survivor in self.survivors:
      if _survivor.free:
        free.append( _survivor )

    return free

  # Reset all survivors free state

  def free_survivors( self ):

    for _survivor in self.survivors:
      _survivor.free = True

  # Reset all items free state

  def free_inventory( self ):

    self._inventory.free()

  # Set direction for animation

  def set_direction( self ):

    if self.move_route[0].pos_y > self.pos_tile.pos_y:
      self.direction = 'south'
    elif self.move_route[0].pos_x > self.pos_tile.pos_x:
      self.direction = 'east'
    elif self.move_route[0].pos_y < self.pos_tile.pos_y:
      self.direction = 'north'
    elif self.move_route[0].pos_x < self.pos_tile.pos_x:
      self.direction = 'west'

  # Draw animation

  def draw_animation( self ):

    img_path   = self.img_path + self.direction + str( self.draw_count ) + '.png'
    surface    = pygame.image.load( img_path )
    surface.set_colorkey( surface.get_at( ( 0, 0 ) ), RLEACCEL )
    self.image = surface.convert()

  # Update graphics

  def update( self, cam_x, cam_y, cam_en ):

    # Adjust position relative to camera

    if cam_en:
      self.rect.top  = self.abs_y - cam_y
      self.rect.left = self.abs_x - cam_x

    # Switch animation frame when necessary

    do_draw = False

    if self.step_count == properties.FRAME_SWITCH:

      self.draw_count += 1
      if self.draw_count > 1:
        self.draw_count = 0

      self.step_count = 0

      do_draw = True

    else:
      self.step_count += 1

    # Handle movement based on calculated shortest path to destination

    if len( self.move_route ) > 0:

      # Move right

      if ( self.move_route[0].rect.left ) > self.rect.left:
        self.rect.move_ip( properties.EXPD_SPEED, 0 )

      # Move left

      elif ( self.move_route[0].rect.left ) < self.rect.left:
        self.rect.move_ip( -properties.EXPD_SPEED, 0 )

      # Move down

      elif ( self.move_route[0].rect.top ) > self.rect.top:
        self.rect.move_ip( 0, properties.EXPD_SPEED )

      # Move up

      elif ( self.move_route[0].rect.top ) < self.rect.top:
        self.rect.move_ip( 0, -properties.EXPD_SPEED )

      # Update position tile and route if at destination

      if ( self.move_route[0].rect.left == self.rect.left ) \
        and ( self.move_route[0].rect.top == self.rect.top ):

        self.pos_tile = self.move_route[0]
        self.abs_x    = self.pos_tile.pos_x * properties.TILE_WIDTH
        self.abs_y    = self.pos_tile.pos_y * properties.TILE_HEIGHT

        del self.move_route[0]

        # Determine new direction

        if len( self.move_route ) > 0:
          self.set_direction()
        else:
          self.direction = 'south'

        self.step_count = 0
        self.draw_count = 0

        do_draw = True

        # Unfog new area

        self.unfog()

    # Draw animation

    if do_draw:
      self.draw_animation()

  # Calculate the minimum current stamina across all survivors usable by
  # expedition for exploration.

  def calc_min_stamina( self, survivors ):

    min_stamina = 99

    for _survivor in survivors:
      if _survivor.stamina < min_stamina:
        min_stamina = _survivor.stamina

    assert( min_stamina < 99 )

    return min_stamina

  # Path finding, populates a dictionary of all possible tiles reachable
  # by selected expedition with the specified maximum cost.

  def calc_range( self, survivors ):

    # Use Dijkstra's algorithm to find the shortest path from source to
    # destination. A dictionary is used for tracking the shortest path to
    # a given location (each tile remembers the tile leading to it in the
    # shortest path as well as the cost to get there). A list of
    # locations at the current frontier is updated after every super-step
    # of the algorithm.

    self.path_dic = { self.pos_tile: [self.pos_tile,0] }
    frontier      = [ self.pos_tile ]

    min_stamina = self.calc_min_stamina( survivors )

    # Iterate over frontiers until maximum cost is reached

    while len( frontier ) > 0:

      next_frontier = []

      # Search all tiles in the current frontier

      for _tile in frontier:

        # Determine which neighbors are within map bounds

        neighbors = []

        if _tile.pos_y > 0:
          neighbors.append( self.map[_tile.pos_x][_tile.pos_y-1] )

        if _tile.pos_x < ( properties.MAP_SIZE - 1 ):
          neighbors.append( self.map[_tile.pos_x+1][_tile.pos_y] )

        if _tile.pos_y < ( properties.MAP_SIZE - 1 ):
          neighbors.append( self.map[_tile.pos_x][_tile.pos_y+1] )

        if _tile.pos_x > 0:
          neighbors.append( self.map[_tile.pos_x-1][_tile.pos_y] )

        for next_tile in neighbors:

          next_cost = self.path_dic[_tile][1] + next_tile.move_cost

          if ( ( next_cost < min_stamina ) and ( next_tile not in self.path_dic ) ) \
            or ( ( next_tile in self.path_dic ) and ( next_cost < self.path_dic[next_tile][1] ) ):
            self.path_dic[next_tile] = [ _tile, next_cost ]
            next_frontier.append( next_tile )

      # Swap frontiers when all tiles in current frontier are processed

      frontier = next_frontier

  # Calculate shortest path to destination tile. Path dictionary must be
  # populated before calling this method using the calc_range() method
  # above. Returns the cost to reach the destination.

  def calc_path( self, dest_tile ):

    assert( dest_tile in self.path_dic )

    route = []

    route.append( dest_tile )

    _tile = dest_tile

    while _tile != self.pos_tile:
      _tile = self.path_dic[_tile][0]
      route.append( _tile )

    route.reverse()

    return route[1:], self.path_dic[dest_tile][1]

  # (Un)Highlight moveable tiles in range

  def highlight_range( self ):

    for _tile in self.path_dic:
      _tile.moveable = True

  def unhighlight_range( self ):

    for _tile in self.path_dic:
      _tile.moveable = False
      _tile.selected = False

  # Split expedition

  def split( self, survivors, _inventory ):

    # Remove transferred survivors

    tmp_survivors = []

    for _survivor in self.survivors:
      if _survivor not in survivors:
        tmp_survivors.append( _survivor )

    self.survivors = tmp_survivors

    # Remove transferred items

    tmp_items = []

    for _item in self._inventory.items:
      if _item not in _inventory.items:
        tmp_items.append( _item )

    self._inventory.items = tmp_items

  # Merge expeditions

  def merge( self, _expedition ):

    # Combine survivors and inventories

    self.survivors  += _expedition.survivors
    self._inventory += _expedition._inventory

    # Remove merged expedition

    _expedition.kill()

  # Print debug information

  def debug( self ):

    print 'Expedition:'
    self.pos_tile.debug()

    for _survivors in self.survivors:
      _survivors.debug()

    self._inventory.debug()
