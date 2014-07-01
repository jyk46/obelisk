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
    expedition.Expedition.groups = self.expd_group

    # Initialize window surfaces

    self.screen        = pygame.display.get_surface()

    self.camera_window = window.Window( properties.CAMERA_WIDTH, properties.CAMERA_HEIGHT, 0, 0 )
    self.status_window = window.Window( properties.STATUS_WIDTH, properties.STATUS_HEIGHT, properties.CAMERA_WIDTH, 0 )

    # Initialize engine utility variables

    self.done        = False
    self.phase       = PHASE_DAY_PLAN
    self.cam_lock    = False
    self.cam_x       = 0
    self.cam_y       = 0
    self.mouse_x     = 0
    self.mouse_y     = 0
    self.mouse_click = False

  # Initialize map and add tiles to group

  def init_map( self, map ):

    self.map = map

    for i in range( properties.MAP_SIZE ):
      for j in range( properties.MAP_SIZE ):
        self.map_group.add( self.map[i][j] )

  # Update all sprites

  def update_all( self ):

#    self.win_group.update()
    self.map_group.update( self.cam_x, self.cam_y )
    self.expd_group.update()

  # Draw all sprites

  def draw_all( self ):

    rect_updates =  self.map_group.draw( self.camera_window.image )
    rect_updates += self.expd_group.draw( self.camera_window.image )

    rect_updates += self.win_group.draw( self.screen )

    pygame.display.update( rect_updates )

  # Get inputs

  def get_inputs( self ):

    for event in pygame.event.get():

      if event.type == MOUSEMOTION:
        self.mouse_x = event.pos[0]
        self.mouse_y = event.pos[1]

      elif event.type == MOUSEBUTTONDOWN:
        self.mouse_click = True

  # Scroll camera

  def scroll_camera( self ):

    # Scroll x-axis

    if ( self.mouse_x >= 0 ) and ( self.mouse_x < properties.SCROLL_WIDTH ) \
      and ( self.cam_x > 0 ):
      self.cam_x -= properties.SCROLL_SPEED

    elif ( self.mouse_x >= ( properties.CAMERA_WIDTH - properties.SCROLL_WIDTH ) ) \
      and ( self.mouse_x < properties.CAMERA_WIDTH ) \
      and ( ( self.cam_x + properties.CAMERA_WIDTH ) < properties.MAP_WIDTH ):
      self.cam_x += properties.SCROLL_SPEED

    # Scroll y-axis

    if ( self.mouse_y >= 0 ) and ( self.mouse_y < properties.SCROLL_WIDTH ) \
      and ( self.cam_y > 0 ):
      self.cam_y -= properties.SCROLL_SPEED

    elif ( self.mouse_y >= ( properties.CAMERA_HEIGHT - properties.SCROLL_WIDTH ) ) \
      and ( self.mouse_y < properties.CAMERA_HEIGHT ) \
      and ( ( self.cam_y + properties.CAMERA_HEIGHT ) < properties.MAP_HEIGHT ):
      self.cam_y += properties.SCROLL_SPEED

  # Start game engine

  def start( self ):

    # Initialize clock

    clock = pygame.time.Clock()

    # Generate random map

    self.mg = mapgen.MapGen( properties.MAP_SIZE )
    self.init_map( self.mg.map )

    # Main game loop

    while not self.done:

      # Process inputs

      self.get_inputs()

      # Handle camera scrolling

      if not self.cam_lock:
        self.scroll_camera()

      # Update graphics

      self.update_all()
      self.draw_all()

      # Increment clock

      clock.tick( properties.FPS )
