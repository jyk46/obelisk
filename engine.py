#=========================================================================
# engine.py
#=========================================================================
# Main engine for the game, contains logic for day/night phases and
# various actions: explore, craft/repair, heal, rest, camp, info.

import pygame, sys, os
from pygame.locals import *

import random
import properties
import window
import statuswindow
import mapgen
import button
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

PHASE_FREE, PHASE_SCAVENGE, \
PHASE_EXPL_SURV, PHASE_EXPL_INV, PHASE_EXPL_DEST, PHASE_EXPL_MOVE, \
PHASE_CRAFT_ITEM, PHASE_CRAFT_SURV, PHASE_REST, PHASE_STATUS, \
PHASE_NIGHT, PHASE_TRANSITION  = range( 12 )

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Engine:

  #.......................................................................
  # Constructor
  #.......................................................................

  def __init__( self ):

    # Initialize sprite groups

    self.map_group  = pygame.sprite.RenderUpdates()
    self.expd_group = pygame.sprite.RenderUpdates()
    self.menu_group = pygame.sprite.RenderUpdates()

    # Assign default groups to sprite classes

    expedition.Expedition.groups = self.expd_group
    button.Button.groups         = self.menu_group

    # Initialize menu graphics

    self.menu_buttons = []
    menu_pos_y   = properties.MENU_OFFSET_Y

    for text in properties.MENU_TEXT:
      self.menu_buttons.append( button.Button( text, properties.MENU_OFFSET_X, menu_pos_y ) )
      menu_pos_y += properties.MENU_HEIGHT + properties.MENU_PADDING

    # Initialize window surfaces

    self.screen         = pygame.display.get_surface()

    self.camera_window  = window.Window( properties.CAMERA_WIDTH, properties.CAMERA_HEIGHT, 0, 0 )
    self.sidebar_window = window.Window( properties.SIDEBAR_WIDTH, properties.SIDEBAR_HEIGHT, properties.CAMERA_WIDTH, 0 )
    self.status_window  = statuswindow.StatusWindow( properties.ACTION_WIDTH, properties.ACTION_HEIGHT, properties.MENU_WIDTH + 32, 32 )

    # Adjust window scroll zones with absolute offset

    self.status_window.surv_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.status_window.surv_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.status_window.inv_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.status_window.inv_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )

    # Initialize engine utility variables

    self.done        = False
    self.phase       = PHASE_FREE
    self.expeditions = []

    self.cam_en      = True
    self.cam_x       = 0
    self.cam_y       = 0
    self.mouse_x     = 0
    self.mouse_y     = 0
    self.mouse_click = False

    # Phase-specific variables

    self.menu_en     = False
    self.active_expd = None

  #.......................................................................
  # Initialize map and add tiles to group
  #.......................................................................

  def init_map( self, map ):

    self.map = map

    for i in range( properties.MAP_SIZE ):
      for j in range( properties.MAP_SIZE ):
        self.map_group.add( self.map[i][j] )

  #.......................................................................
  # Randomly generate starting expedition
  #.......................................................................

  def init_expedition( self ):

    # Randomly select starting tile (needs to be Field terrain)

    pos_x = random.randint( 0, properties.MAP_SIZE - 1 )
    pos_y = random.randint( 0, properties.MAP_SIZE - 1 )

    while self.map[pos_x][pos_y].terrain != 'Field':
      pos_x = random.randint( 0, properties.MAP_SIZE - 1 )
      pos_y = random.randint( 0, properties.MAP_SIZE - 1 )

    start_tile = self.map[pos_x][pos_y]

    # Generate random set of starting survivors

    survivors = []

    for i in range( properties.NUM_START_SURVIVORS ):
      survivors.append( survivor.Survivor() )

    # Initialize starting inventory

    inv = inventory.Inventory(
      properties.START_FOOD,
      properties.START_WOOD,
      properties.START_METAL,
      properties.START_AMMO,
      [
        item.Item( 'Knife' ),
        item.Item( 'Pistol' ),
      ],
    )

    # Create expedition

    self.expeditions.append( expedition.Expedition( start_tile, survivors, inv ) )

  #.......................................................................
  # Update all sprites
  #.......................................................................

  def update_all( self ):

#    self.win_group.update()
    self.map_group.update( self.cam_x, self.cam_y )
    self.expd_group.update( self.cam_x, self.cam_y )
    self.status_window.update()

  #.......................................................................
  # Draw all sprites
  #.......................................................................

  def draw_all( self ):

    # Draw map and associated markers

    rect_updates =  self.map_group.draw( self.camera_window.image )
    rect_updates += self.expd_group.draw( self.camera_window.image )

    for expd in self.expeditions:
      expd_text = expd.get_text()
      rect_updates += [ self.camera_window.image.blit( expd_text[0], expd_text[1] ) ]

    # Draw menu if enabled

    if self.menu_en:
      rect_updates += self.menu_group.draw( self.camera_window.image )

    # Draw all windows onto main screen

    rect_updates += self.camera_window.draw( self.screen )
    rect_updates += self.sidebar_window.draw_background( properties.SIDEBAR_PATH + 'sidebar_bg.png' )
    rect_updates += self.sidebar_window.draw( self.screen )

    # Draw phase-specific graphics

    if self.phase == PHASE_STATUS:
      rect_updates += self.status_window.draw_background( properties.ACTION_PATH + 'action_bg.png' )
      rect_updates += self.status_window.draw_info()
      rect_updates += self.status_window.draw( self.screen )

    # Update the display

    pygame.display.update( rect_updates )

  #.......................................................................
  # Get inputs
  #.......................................................................

  def get_inputs( self ):

    self.mouse_click = False

    for event in pygame.event.get():

      if event.type == MOUSEMOTION:
        self.mouse_x = event.pos[0]
        self.mouse_y = event.pos[1]

      elif event.type == MOUSEBUTTONDOWN:
        self.mouse_click = True

  #.......................................................................
  # Scroll camera
  #.......................................................................

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

  #.......................................................................
  # Menu selection handler
  #.......................................................................

  def handle_menu( self ):

    menu_used = False

    if self.mouse_click:

      for button in self.menu_buttons:
        if ( button.rect.collidepoint( self.mouse_x, self.mouse_y ) ):

          menu_used = True

          if button.text == 'EXPLORE':
            self.phase     = PHASE_EXPL_SURV

          elif button.text == 'SCAVENGE':
            self.phase = PHASE_SCAVENGE

          elif button.text == 'CRAFT':
            self.phase     = PHASE_CRAFT_ITEM

          elif button.text == 'REST':
            self.phase     = PHASE_REST

          elif button.text == 'STATUS':
            self.phase              = PHASE_STATUS
            self.status_window.expd = self.active_expd

#          self.cam_en = False

          break

    return menu_used

  #.......................................................................
  # PHASE_FREE Handling
  #.......................................................................
  # Default free-look phase

  def handle_phase_free( self ):

    # Check for mouse click

    if self.mouse_click:

      click_x    = ( self.cam_x + self.mouse_x ) / properties.TILE_WIDTH
      click_y    = ( self.cam_y + self.mouse_y ) / properties.TILE_HEIGHT
      click_tile = self.map[click_x][click_y]

      # Enable menu if expedition is clicked

      self.menu_en = False
      self.cam_en  = True

      for expd in self.expeditions:
        if click_tile == expd.pos_tile:
          self.active_expd = expd
          self.menu_en     = True
          self.cam_en      = False
          break

  #.......................................................................
  # PHASE_EXPL_SURV Handling
  #.......................................................................
  # Phase for selecting survivors to explore new tile

  def handle_phase_expl_surv( self ):

    pass

  #.......................................................................
  # PHASE_STATUS Handling
  #.......................................................................
  # Phase for displaying details about expedition

  def handle_status( self ):

    # Scroll survivor panel

    if self.status_window.surv_scroll_up_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.status_window.surv_scroll > 0 ):
      self.status_window.surv_scroll -= properties.SCROLL_SPEED

    elif self.status_window.surv_scroll_down_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( ( self.status_window.surv_scroll + properties.SUBACTION_HEIGHT ) < self.status_window.max_surv_scroll ):
      self.status_window.surv_scroll += properties.SCROLL_SPEED

    # Scroll inventory panel

    if self.status_window.inv_scroll_up_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.status_window.inv_scroll > 0 ):
      self.status_window.inv_scroll -= properties.SCROLL_SPEED

    elif self.status_window.inv_scroll_down_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( ( self.status_window.inv_scroll + properties.SUBACTION_HEIGHT ) < self.status_window.max_inv_scroll ):
      self.status_window.inv_scroll += properties.SCROLL_SPEED

    # Reset phase if clicked outside of context

    if self.mouse_click and not self.status_window.rect.collidepoint( self.mouse_x, self.mouse_y ):
      self.phase   = PHASE_FREE
      self.menu_en = False
      self.cam_en  = True

  #.......................................................................
  # Start game engine
  #.......................................................................

  def start( self ):

    # Initialize clock

    clock = pygame.time.Clock()

    # Generate random map

    self.mg = mapgen.MapGen( properties.MAP_SIZE )
    self.init_map( self.mg.map )

    # Add starting expedition

    self.init_expedition()

    # Main game loop

    while not self.done:

      # Process inputs

      self.get_inputs()

      # Handle camera scrolling

      if self.cam_en:
        self.scroll_camera()

      # Handle menu selection

      menu_used = False

      if self.menu_en:
        menu_used = self.handle_menu()

      # Handle game phases

      if not menu_used:

        if self.phase == PHASE_FREE:
          self.handle_phase_free()

        elif self.phase == PHASE_EXPL_SURV:
          self.handle_phase_expl_surv()

        elif self.phase == PHASE_STATUS:
          self.handle_status()

      # Update graphics

      self.update_all()
      self.draw_all()

      # Increment clock

      clock.tick( properties.FPS )
