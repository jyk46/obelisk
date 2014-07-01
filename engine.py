#=========================================================================
# engine.py
#=========================================================================
# Main engine for the game, contains logic for day/night phases and
# various actions: explore, craft/repair, heal, rest, camp, info.

import pygame, sys, os
from pygame.locals import *

import properties
import window
import mapgen
import tile
import enemy
import expedition
import survivor
import attribute
import inventory
import item

#-------------------------------------------------------------------------
# Properties
#-------------------------------------------------------------------------

PHASE_DAY_PLAN, PHASE_DAY_EXEC, PHASE_NIGHT_PLAN, PHASE_NIGHT_EXEC = range( 4 )

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Engine:

  # Constructor

  def __init__( self ):

    # Initialize sprite groups

    self.win_group  = pygame.sprite.RenderUpdates()
    self.map_group  = pygame.sprite.RenderUpdates()
    self.expd_group = pygame.sprite.RenderUpdates()

    # Assign default groups to sprite classes

    window.Window.groups         = self.win_group
    tile.Tile.groups             = self.map_group
    expedition.Expedition.groups = self.expd_group

    # Initialize window surfaces

    self.screen        = pygame.display.get_surface()

    self.camera_window = window.Window( properties.CAMERA_WIDTH, properties.CAMERA_HEIGHT, 0, 0 )
    self.status_window = window.Window( properties.STATUS_WIDTH, properties.STATUS_HEIGHT, properties.CAMERA_WIDTH, 0 )

    # Initialize engine utility variables

    self.phase  = PHASE_DAY_PLAN
    self.cam_x  = 0
    self.cam_y  = 0

  # Update all sprites

  def update_all( self ):

#    self.win_group.update()
    self.map_group.update()
    self.expd_group.update()

  # Draw all sprites

  def draw_all( self ):

    rect_updates =  self.map_group.draw( self.camera_window.image )
    rect_updates += self.expd_group.draw( self.camera_window.image )

    rect_updates += self.win_group.draw( self.screen )

    pygame.display.update( rect_updates )

  # Start game engine

  def start( self ):

    # Initialize clock

    clock = pygame.time.Clock()

    # Generate random map

    self.mg  = mapgen.MapGen( properties.MAP_SIZE )
    self.map = self.mg.map

    # Main game loop

    while True:

      # Update graphics

      self.update_all()
      self.draw_all()

      pygame.event.wait()

      # Increment clock

      clock.tick( properties.FPS )
