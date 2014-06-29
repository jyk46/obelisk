#=========================================================================
# expedition.py
#=========================================================================
# One or more survivors are grouped into Expeditions, which are what is
# actually shown on the map. Expeditions have local inventories for food,
# material, and equipment.

import pygame, sys, os
from pygame.locals import *

import survivor
import inventory
import tile

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Expedition( pygame.sprite.Sprite ):

  # Constructor

  def __init__( self, start_tile, survivors, inv ):

    pygame.sprite.Sprite.__init__( self, self.containers )

    self.pos_tile    = start_tile
    self.survivors   = survivors
    self.inv         = inv
    self.move_route  = []

    # Set image and make background transparent

    self.img_path         = 'images/expedition/icon.png'
    self.surface          = pygame.image.load( self.img_path )
    self.surface.set_colorkey( self.surface.get_at( ( 0, 0 ) ), RLEACCEL )
    self.image            = self.surface.convert()
    self.img_rect         = self.image.get_rect()
    self.img_rect.topleft = self.pos_tile.pos_x * tile.WIDTH, \
                            self.pos_tile.pos_y * tile.HEIGHT

    # Set font for labeling icon

    self.font             = pygame.font.Font( 'fonts/default.ttf', 10 )
    self.text             = self.font.render( str( len( self.survivors ) ), True, (255,255,255) )
    self.text_rect        = self.text.get_rect()
    self.text_rect.center = self.img_rect.center

  # Update graphics

  def update( self ):

    # Handle movement based on calculated shortest path to destination

    if len( self.move_route ) > 0:

      # Move right

      if ( self.move_route[0].pos_x * tile.WIDTH ) > self.img_rect.left:
        self.img_rect.move_ip( 8, 0 )
        self.text_rect.move_ip( 8, 0 )

      # Move left

      elif ( self.move_route[0].pos_x * tile.WIDTH ) < self.img_rect.left:
        self.img_rect.move_ip( -8, 0 )
        self.text_rect.move_ip( -8, 0 )

      # Move down

      elif ( self.move_route[0].pos_y * tile.HEIGHT ) > self.img_rect.top:
        self.img_rect.move_ip( 0, 8 )
        self.text_rect.move_ip( 0, 8 )

      # Move up

      elif ( self.move_route[0].pos_y * tile.HEIGHT ) < self.img_rect.top:
        self.img_rect.move_ip( 0, -8 )
        self.text_rect.move_ip( 0, -8 )

      # Update position tile and route if at destination

      if ( ( self.move_route[0].pos_x * tile.WIDTH  ) == self.img_rect.left ) \
      or ( ( self.move_route[0].pos_y * tile.HEIGHT ) == self.img_rect.top  ):

        self.pos_tile = self.move_route[0]

        del self.move_route[0]

  # Split expedition

  def split( self, survivors, inv ):

    # Remove survivors and items from parent expedition

    for new_surv in survivors:
      for i, old_surv in enumerate( self.survivors ):
        if old_surv == new_surv:
          del self.survivors[i]
          break

    self.inv -= inv

    # Update label

    self.text             = self.font.render( str( len( self.survivors ) ), True, (255,255,255) )
    self.text_rect        = self.text.get_rect()
    self.text_rect.center = self.img_rect.center

    # Create and return child expedition

    return Expedition( self.pos_tile, survivors, inv )

  # Merge expeditions

  def merge( self, expd ):

    # Combine survivors and inventories

    self.survivors += expd.survivors
    self.inv       += expd.inv

    # Update label

    self.text             = self.font.render( str( len( self.survivors ) ), True, (255,255,255) )
    self.text_rect        = self.text.get_rect()
    self.text_rect.center = self.img_rect.center

    # Remove merged expedition

    expd.kill()
