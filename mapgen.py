#=========================================================================
# mapgen.py
#=========================================================================
# Random map generator for game map. Each map must have at least one of
# each of the following terrains: mountain, swamp, jungle,
# facility. Default tile is the field. Each special terrain area has a
# ritual ground. Chance to spawn caves in mountains. Wreckages spawn
# randomly.

import random
import tile

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class MapGen():

  # Generate random area of special terrain

  def gen_terrain( self, terrains, rates ):

    # Designate seed coordinates

    seed_x = random.randint( 0, self.size - 1 )
    seed_y = random.randint( 0, self.size - 1 )

    # Convert seed tile into specified terrain

    self.map[seed_x][seed_y] = tile.Tile( terrains[0], seed_x, seed_y )

    # If multiple terrains are specified, iteratively generate tiers of
    # terrains with each layer starting with 1.0 probability.

    visited  = []
    frontier = [ self.map[seed_x][seed_y] ]

    for terrain, rate in zip( terrains, rates ):

      prob = 1.0

      # Iterate through frontiers in BFS-manner with probability of
      # generating the same terrain decreasing with each super-step.

      while True: #len( frontier ) > 0:

        next_frontier = []

        for i, ti in enumerate( frontier ):

          # Chance to convert north neighbor to terrain

          if ti.pos_y > 0:

            next_ti = self.map[ti.pos_x][ti.pos_y-1]

            if ( random.random() < prob ) and ( next_ti not in visited ):
              self.map[ti.pos_x][ti.pos_y-1] = tile.Tile( terrain, ti.pos_x, ti.pos_y - 1 )
              next_frontier.append( next_ti )

          # Chance to convert east neighbor to terrain

          if ti.pos_x < ( self.size - 1 ):

            next_ti = self.map[ti.pos_x+1][ti.pos_y]

            if ( random.random() < prob ) and ( next_ti not in visited ):
              self.map[ti.pos_x+1][ti.pos_y] = tile.Tile( terrain, ti.pos_x + 1, ti.pos_y )
              next_frontier.append( next_ti )

          # Chance to convert south neighbor to terrain

          if ti.pos_y < ( self.size - 1 ):

            next_ti = self.map[ti.pos_x][ti.pos_y+1]

            if ( random.random() < prob ) and ( next_ti not in visited ):
              self.map[ti.pos_x][ti.pos_y+1] = tile.Tile( terrain, ti.pos_x, ti.pos_y + 1 )
              next_frontier.append( next_ti )

          # Chance to convert west neighbor to terrain

          if ti.pos_x > 0:

            next_ti = self.map[ti.pos_x-1][ti.pos_y]

            if ( random.random() < prob ) and ( next_ti not in visited ):
              self.map[ti.pos_x-1][ti.pos_y] = tile.Tile( terrain, ti.pos_x - 1, ti.pos_y )
              next_frontier.append( next_ti )

          # Mark tile in frontier as visited

          visited.append( ti )

        # Swap frontiers when all tiles in current frontier are processed

        if len( next_frontier ) == 0:
          break

        frontier = next_frontier

        # Reduce spawn probability for next frontier

        prob -= rate

  # Spawn random terrain (no spread)

  def gen_random( self, terrain, num ):

    placed = []

    for i in range( num ):

      seed_x = random.randint( 0, self.size - 1 )
      seed_y = random.randint( 0, self.size - 1 )

      while self.map[seed_x][seed_y] in placed:
        seed_x = random.randint( 0, self.size - 1 )
        seed_y = random.randint( 0, self.size - 1 )

      self.map[seed_x][seed_y] = tile.Tile( terrain, seed_x, seed_y )

  # Constructor

  def __init__( self, size ):

    self.size = size
    self.map  = []

    self.num_mountain = 8
    self.num_swamp    = 4
    self.num_jungle   = 8
    self.num_facility = 2

    # Populate map array with default terrain with given dimensions

    for i in range( self.size ):

      self.map.append( [] )

      for j in range( self.size ):
        self.map[i].append( tile.Tile( 'Field', i, j ) )

    # Add mountains

    for i in range( self.num_mountain ):
      self.gen_terrain( ['Cave', 'Mountain'], [0.3, 0.1] )

    # Add swamp

    for i in range( self.num_swamp ):
      self.gen_terrain( ['Swamp'], [0.15] )

    # Add jungle

    for i in range( self.num_jungle ):
      self.gen_terrain( ['Deep Jungle', 'Jungle'], [0.2, 0.1] )

    # Add facility

    for i in range( self.num_facility ):
      self.gen_terrain( ['Facility'], [0.3] )

    # Add wreckage

    self.gen_random( 'Wreckage', 10 )

    # Add ritual sites

    self.gen_random( 'Ritual Site', 4 )

  # Print debug information

  def debug( self ):

    for j in range( self.size ):

      for i in range( self.size ):
        print self.map[i][j].terrain[:1],

      print ''
