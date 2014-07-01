#=========================================================================
# expedition.py
#=========================================================================
# One or more survivors are grouped into Expeditions, which are what is
# actually shown on the map. Expeditions have local inventories for food,
# material, and equipment.

import pygame, sys, os
from pygame.locals import *

import properties
import survivor
import inventory
import tile

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Expedition( pygame.sprite.Sprite ):

  # Constructor

  def __init__( self, start_tile, survivors, inv ):

    pygame.sprite.Sprite.__init__( self, self.groups )

    self.pos_tile    = start_tile
    self.survivors   = survivors
    self.inv         = inv
    self.path_dic    = {}
    self.move_route  = []

    # Set image and make background transparent

    self.img_path     = properties.EXPD_PATH + 'icon.png'
    self.surface      = pygame.image.load( self.img_path )
    self.surface.set_colorkey( self.surface.get_at( ( 0, 0 ) ), RLEACCEL )
    self.image        = self.surface.convert()
    self.rect         = self.image.get_rect()
    self.abs_x        = self.pos_tile.pos_x * properties.TILE_WIDTH
    self.abs_y        = self.pos_tile.pos_y * properties.TILE_HEIGHT
    self.rect.topleft = self.abs_x, self.abs_y

    # Set font for labeling icon

    self.font = pygame.font.Font( properties.DEFAULT_FONT, 8 )

  # Return surface and rect of text overlay for expedition icon

  def get_text( self ):

    surface     = self.font.render( str( len( self.survivors ) ), 1, (0,0,0) )
    rect        = surface.get_rect()
    rect.center = self.rect.center[0], self.rect.center[1] + 2

    return surface, rect

  # Update graphics

  def update( self, cam_x, cam_y ):

    # Adjust position relative to camera

    self.rect.top  = self.abs_y - cam_y
    self.rect.left = self.abs_x - cam_x

    # Handle movement based on calculated shortest path to destination

    if len( self.move_route ) > 0:

      # Move right

      if ( self.move_route[0].pos_x * properties.TILE_WIDTH ) > self.rect.left:
        self.rect.move_ip( properties.EXPEDITION_SPEED, 0 )

      # Move left

      elif ( self.move_route[0].pos_x * properties.TILE_WIDTH ) < self.rect.left:
        self.rect.move_ip( -properties.EXPEDITION_SPEED, 0 )

      # Move down

      elif ( self.move_route[0].pos_y * properties.TILE_HEIGHT ) > self.rect.top:
        self.rect.move_ip( 0, properties.EXPEDITION_SPEED )

      # Move up

      elif ( self.move_route[0].pos_y * properties.TILE_HEIGHT ) < self.rect.top:
        self.rect.move_ip( 0, -properties.EXPEDITION_SPEED )

      # Update position tile and route if at destination

      if ( ( self.move_route[0].pos_x * properties.TILE_WIDTH  ) == self.rect.left ) \
      or ( ( self.move_route[0].pos_y * properties.TILE_HEIGHT ) == self.rect.top  ):

        self.pos_tile = self.move_route[0]
        self.abs_x    = self.pos_tile.pos_x * properties.TILE_WIDTH
        self.abs_y    = self.pos_tile.pos_y * properties.TILE_HEIGHT

        del self.move_route[0]

  # Calculate the minimum current stamina across all survivors usable by
  # expedition for exploration.

  def calc_min_stamina( self ):

    min_stamina = 99

    for surv in survivors:
      if surv.stamina < min_stamina:
        min_stamina = surv.stamina

    assert( min_stamina < 99 )

    return min_stamina

  # Path finding, populates a dictionary of all possible tiles reachable
  # by selected expedition with the specified maximum cost.

  def calc_range( self, map ):

    # Use Dijkstra's algorithm to find the shortest path from source to
    # destination. A dictionary is used for tracking the shortest path to
    # a given location (each tile remembers the tile leading to it in the
    # shortest path as well as the cost to get there). A list of
    # locations at the current frontier is updated after every super-step
    # of the algorithm.

    self.path_dic = { self.pos_tile: [self.pos_tile,0] }
    frontier      = [ self.pos_tile ]

    avail_stamina = self.calc_min_stamina()

    # Iterate over frontiers until maximum cost is reached

    while len( frontier ) > 0:

      next_frontier = []

      # Search all tiles in the current frontier

      for ti in frontier:

        # Determine which neighbors are within map bounds

        neighbors = []

        if ti.pos_y > 0:
          neighbors.append( map[ti.pos_x][ti.pos_y-1] )

        if ti.pos_x < ( properties.MAP_SIZE - 1 ):
          neighbors.append( map[ti.pos_x+1][ti.pos_y] )

        if ti.pos_y < ( properties.MAP_SIZE - 1 ):
          neighbors.append( map[ti.pos_x][ti.pos_y+1] )

        if ti.pos_x > 0:
          neighbors.append( map[ti.pos_x-1][ti.pos_y] )

        for next_ti in neighbors:

          next_cost = self.path_dic[ti][1] + next_ti.move_cost

          if ( ( next_cost < avail_stamina ) and ( next_ti not in self.path_dic ) ) \
            or ( next_cost < self.path_dic[next_ti][1] ):
            self.path_dic[next_ti] = [ ti, next_cost ]
            next_frontier.append( next_ti )

      # Swap frontiers when all tiles in current frontier are processed

      frontier = next_frontier

  # Calculate shortest path to destination tile. Path dictionary must be
  # populated before calling this method using the calc_range() method
  # above. Returns the cost to reach the destination.

  def calc_path( self, dest_tile ):

    assert( dest_tile in self.path_dic )

    self.move_route.append( dest_tile )

    ti = dest_tile

    while ti != self.pos_tile:
      ti = self.path_dic[ti][0]
      self.move_route.append( ti )

    self.move_route.reverse()[1:]

    return self.path_dic[dest_tile][1]

  # Split expedition

  def split( self, survivors, inv ):

    # Remove survivors and items from parent expedition

    for new_surv in survivors:
      for i, old_surv in enumerate( self.survivors ):
        if old_surv == new_surv:
          del self.survivors[i]
          break

    self.inv -= inv

    # Create and return child expedition

    return Expedition( self.pos_tile, survivors, inv )

  # Merge expeditions

  def merge( self, expd ):

    # Combine survivors and inventories

    self.survivors += expd.survivors
    self.inv       += expd.inv

    # Remove merged expedition

    expd.kill()

  # Print debug information

  def debug( self ):

    print 'Expedition:'
    self.pos_tile.debug()

    for surv in self.survivors:
      surv.debug()

    self.inv.debug()
