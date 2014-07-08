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
import sidebarwindow
import explorewindow
import scavengewindow
import eventwindow
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

PHASE_FREE, PHASE_SCAV_SURV, PHASE_SCAV_DONE, \
PHASE_EXPL_SURV, PHASE_EXPL_INV, PHASE_EXPL_DEST, PHASE_EXPL_MOVE, \
PHASE_CRAFT_ITEM, PHASE_CRAFT_SURV, PHASE_REST, PHASE_STATUS, \
PHASE_NIGHT, PHASE_TRANSITION  = range( 13 )

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Engine:

  #.......................................................................
  # Constructor
  #.......................................................................

  def __init__( self ):

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
    self.key_esc     = False

    # Phase-specific variables

    self.menu_en     = False
    self.active_expd = None

    # Initialize sprite groups

    self.map_group  = pygame.sprite.RenderUpdates()
    self.expd_group = pygame.sprite.RenderUpdates()
    self.menu_group = pygame.sprite.RenderUpdates()

    # Assign default groups to sprite classes

    expedition.Expedition.groups = self.expd_group

    # Initialize menu graphics

    menu_pos_y = properties.MENU_OFFSET_Y

    for text in properties.MENU_TEXT:
      self.menu_group.add( [ button.Button( text, properties.MENU_OFFSET_X, menu_pos_y ) ] )
      menu_pos_y += properties.MENU_HEIGHT + properties.MENU_PADDING

    # Initialize window surfaces

    self.screen = pygame.display.get_surface()

    self.camera_window = window.Window(
      properties.CAMERA_WIDTH, properties.CAMERA_HEIGHT, \
      0, 0
    )

    self.sidebar_window = sidebarwindow.SidebarWindow(
      properties.SIDEBAR_WIDTH, properties.SIDEBAR_HEIGHT, \
      properties.CAMERA_WIDTH, 0, \
      properties.SIDEBAR_PATH + 'sidebar_bg.png',
      self.expeditions
    )

    self.status_window = statuswindow.StatusWindow(
      properties.ACTION_WIDTH, properties.ACTION_HEIGHT, \
      properties.MENU_WIDTH + 32, 32, \
      properties.ACTION_PATH + 'action_bg.png'
    )

    self.explore_window = explorewindow.ExploreWindow(
      properties.ACTION_WIDTH, properties.ACTION_HEIGHT, \
      properties.MENU_WIDTH + 32, 32, \
      properties.ACTION_PATH + 'action_bg.png'
    )

    self.scavenge_window = scavengewindow.ScavengeWindow(
      properties.ACTION_WIDTH, properties.ACTION_HEIGHT, \
      properties.MENU_WIDTH + 32, 32, \
      properties.ACTION_PATH + 'action_bg.png'
    )

    self.event_window = eventwindow.EventWindow(
      properties.EVENT_WIDTH, properties.EVENT_HEIGHT, \
      properties.MENU_WIDTH + 32, properties.CAMERA_HEIGHT / 2 - properties.EVENT_HEIGHT / 2, \
      properties.EVENT_PATH + 'event_bg.png'
    )

    # Adjust window scroll zones with absolute offset

    self.status_window.surv_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.status_window.surv_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.status_window.inv_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.status_window.inv_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )

    self.explore_window.old_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.explore_window.old_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.explore_window.new_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.explore_window.new_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )

    self.scavenge_window.old_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.scavenge_window.old_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.scavenge_window.new_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.scavenge_window.new_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )

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

    self.expeditions.append( expedition.Expedition( start_tile, survivors, inv, self.map ) )

  #.......................................................................
  # Update all sprites
  #.......................................................................

  def update_all( self ):

#    self.win_group.update()
    self.map_group.update( self.cam_x, self.cam_y )
    self.expd_group.update( self.cam_x, self.cam_y )
    self.explore_window.update()
    self.scavenge_window.update()
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
    rect_updates += self.sidebar_window.draw( self.screen )

    # Draw phase-specific graphics

    if self.phase == PHASE_EXPL_SURV:
      rect_updates += self.explore_window.draw( self.screen )
    elif self.phase == PHASE_EXPL_INV:
      rect_updates += self.explore_window.draw( self.screen )
    elif self.phase == PHASE_SCAV_SURV:
      rect_updates += self.scavenge_window.draw( self.screen )
    elif self.phase == PHASE_SCAV_DONE:
      rect_updates += self.event_window.draw( self.screen )
    elif self.phase == PHASE_STATUS:
      rect_updates += self.status_window.draw( self.screen )

    # Update the display

    pygame.display.update( rect_updates )

  #.......................................................................
  # Get inputs
  #.......................................................................

  def get_inputs( self ):

    self.mouse_click = False
    self.key_esc     = False

    for event in pygame.event.get():

      if event.type == MOUSEMOTION:
        self.mouse_x = event.pos[0]
        self.mouse_y = event.pos[1]

      elif event.type == MOUSEBUTTONDOWN:
        self.mouse_click = True

      elif ( event.type == KEYDOWN ) and ( event.key == K_ESCAPE ):
        self.key_esc = True

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

      for button in self.menu_group:
        if button.rect.collidepoint( self.mouse_x, self.mouse_y ):

          menu_used = True

          if button.text == 'EXPLORE':
            self.phase                     = PHASE_EXPL_SURV
            self.explore_window.expd       = self.active_expd
            self.explore_window.surv_phase = True
            self.explore_window.clear()

          elif button.text == 'SCAVENGE':
            self.phase                   = PHASE_SCAV_SURV
            self.scavenge_window.expd    = self.active_expd
            self.scavenge_window.clear()
            self.event_window.expd       = self.active_expd
            self.event_window.event_tile = self.active_expd.pos_tile

          elif button.text == 'CRAFT':
            self.phase = PHASE_CRAFT_ITEM

          elif button.text == 'REST':
            self.phase = PHASE_REST

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

    # Calculate current tile mouse is hovering over

    context_x = ( self.cam_x + self.mouse_x ) / properties.TILE_WIDTH
    context_y = ( self.cam_y + self.mouse_y ) / properties.TILE_HEIGHT

    if ( context_x >= 0 ) and ( context_x < properties.MAP_SIZE ) \
      and ( context_y >= 0 ) and ( context_y < properties.MAP_SIZE ) \
      and ( self.mouse_x >= 0 ) and ( self.mouse_x < properties.CAMERA_WIDTH ) \
      and ( self.mouse_y >= 0 ) and ( self.mouse_y < properties.CAMERA_HEIGHT ):

      context_tile = self.map[context_x][context_y]

      # Sidebar terrain information (only show if revealed on map)

      if not context_tile.fog:
        self.sidebar_window.terr = context_tile

      # Sidebar expedition information (only when menu is disabled)

      expd_active = False

      for expd in self.expeditions:
        if context_tile == expd.pos_tile:
          expd_active = True
          break

      if not self.menu_en:

        self.sidebar_window.expd = None

        if expd_active:
          self.sidebar_window.expd = expd

    else:

      self.expd_active         = False
      self.sidebar_window.terr = None
      self.sidebar_window.expd = None

    # Give priority to ESC key

    if self.key_esc:

      self.menu_en = False
      self.cam_en  = True

    # Check for mouse click

    elif self.mouse_click:

      # Enable menu if expedition is clicked

      self.menu_en = False
      self.cam_en  = True

      if expd_active:
        self.active_expd = expd
        self.menu_en     = True
        self.cam_en      = False

  #.......................................................................
  # PHASE_EXPL_SURV Handling
  #.......................................................................
  # Phase for selecting survivors to explore new tile

  def handle_phase_expl_surv( self ):

    # Set active information to display

    self.explore_window.surv = None

    for surv, pos in zip( self.explore_window.expd.get_free(), self.explore_window.old_pos ):
      surv_info_rect = pygame.rect.Rect(
        properties.MENU_WIDTH + 32 + self.explore_window.old_rect.left + pos[0] - 4, \
        32 + self.explore_window.old_rect.top + pos[1] - 3, \
        properties.ACTION_SUB_WIDTH, 32
      )
      if surv_info_rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.explore_window.surv = surv

        if self.mouse_click:
          surv.free = False
          self.explore_window.survivors.append( surv )

    for surv, pos in zip( self.explore_window.survivors, self.explore_window.new_pos ):
      surv_info_rect = pygame.rect.Rect(
        properties.MENU_WIDTH + 32 + self.explore_window.new_rect.left + pos[0] - 4, \
        32 + self.explore_window.new_rect.top + pos[1] - 3, \
        properties.ACTION_SUB_WIDTH, 32
      )
      if surv_info_rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.explore_window.surv = surv

        if self.mouse_click:
          surv.free = True
          self.explore_window.survivors.remove( surv )

    # Scroll old survivors panel

    if self.explore_window.old_scroll_up_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.explore_window.old_scroll > 0 ):
      self.explore_window.old_scroll -= properties.SCROLL_SPEED

    elif self.explore_window.old_scroll_down_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( ( self.explore_window.old_scroll + properties.ACTION_SUB_HEIGHT - 32 ) < self.explore_window.max_old_scroll ):
      self.explore_window.old_scroll += properties.SCROLL_SPEED

    # Scroll new survivors panel

    if self.explore_window.new_scroll_up_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.explore_window.new_scroll > 0 ):
      self.explore_window.new_scroll -= properties.SCROLL_SPEED

    elif self.explore_window.new_scroll_down_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( ( self.explore_window.new_scroll + properties.ACTION_SUB_HEIGHT - 32 ) < self.explore_window.max_new_scroll ):
      self.explore_window.new_scroll += properties.SCROLL_SPEED

    # Go back to menu if ESC pressed

    if self.key_esc:
      self.phase   = PHASE_FREE
      self.menu_en = True
      self.cam_en  = False
      self.explore_window.reset_expd()

    elif self.mouse_click:

      # Move to next phase if next button is clicked and at least one
      # survivor was chosen.

      for button in self.explore_window.button_group:

        button_rect = pygame.rect.Rect(
          properties.MENU_WIDTH + 32 + button.rect.left, \
          32 + button.rect.top, \
          button.rect.width, button.rect.height
        )

        if button_rect.collidepoint( self.mouse_x, self.mouse_y ) \
          and ( len( self.explore_window.survivors ) > 0 ):

          # If all survivors explore, skip inventory selection and
          # automatically transfer all items and resources over to
          # explore party.

          if len( self.explore_window.expd.get_free() ) == 0:

            self.phase                     = PHASE_EXPL_DEST
            self.explore_window.start_tile = None
            self.menu_en                   = False
            self.cam_en                    = True
            self.explore_window.expd.calc_range()
            self.explore_window.expd.highlight_range()

            self.explore_window.inv = self.explore_window.expd.inv

          # Otherwise, go into inventory selection

          else:

            self.phase                     = PHASE_EXPL_INV
            self.explore_window.inv        = inventory.Inventory( 0, 0, 0, 0, [] )
            self.explore_window.surv_phase = False
            self.explore_window.old_scroll = 0
            self.explore_window.new_scroll = 0

      # Reset phase if clicked outside of context

      if not self.explore_window.rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.phase   = PHASE_FREE
        self.menu_en = False
        self.cam_en  = True
        self.explore_window.reset_expd()

  #.......................................................................
  # PHASE_EXPL_INV Handling
  #.......................................................................
  # Phase for selecting inventory for explore party

  def handle_phase_expl_inv( self ):

    # Handle resource transfer to explore party

    self.explore_window.it = None

    inv_info_rect = pygame.rect.Rect(
      properties.MENU_WIDTH + 32 + self.explore_window.old_rect.left + self.explore_window.old_pos[0][0] - 4, \
      32 + self.explore_window.old_rect.top + self.explore_window.old_pos[0][1] - 3, \
      properties.ACTION_SUB_WIDTH, 32
    )

    if self.mouse_click and inv_info_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.explore_window.expd.inv.food > 0 ):
      self.explore_window.expd.inv.food -= 1
      self.explore_window.inv.food      += 1

    inv_info_rect = pygame.rect.Rect(
      properties.MENU_WIDTH + 32 + self.explore_window.old_rect.left + self.explore_window.old_pos[1][0] - 4, \
      32 + self.explore_window.old_rect.top + self.explore_window.old_pos[1][1] - 3, \
      properties.ACTION_SUB_WIDTH, 32
    )

    if self.mouse_click and inv_info_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.explore_window.expd.inv.wood > 0 ):
      self.explore_window.expd.inv.wood -= 1
      self.explore_window.inv.wood      += 1

    inv_info_rect = pygame.rect.Rect(
      properties.MENU_WIDTH + 32 + self.explore_window.old_rect.left + self.explore_window.old_pos[2][0] - 4, \
      32 + self.explore_window.old_rect.top + self.explore_window.old_pos[2][1] - 3, \
      properties.ACTION_SUB_WIDTH, 32
    )

    if self.mouse_click and inv_info_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.explore_window.expd.inv.metal > 0 ):
      self.explore_window.expd.inv.metal -= 1
      self.explore_window.inv.metal      += 1

    inv_info_rect = pygame.rect.Rect(
      properties.MENU_WIDTH + 32 + self.explore_window.old_rect.left + self.explore_window.old_pos[3][0] - 4, \
      32 + self.explore_window.old_rect.top + self.explore_window.old_pos[3][1] - 3, \
      properties.ACTION_SUB_WIDTH, 32
    )

    if self.mouse_click and inv_info_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.explore_window.expd.inv.ammo > 0 ):
      self.explore_window.expd.inv.ammo -= 1
      self.explore_window.inv.ammo      += 1

    # Set active information to display in old survivors panel

    for it, pos in zip( self.explore_window.expd.inv.get_free(), self.explore_window.old_pos[4:] ):
      inv_info_rect = pygame.rect.Rect(
        properties.MENU_WIDTH + 32 + self.explore_window.old_rect.left + pos[0] - 4, \
        32 + self.explore_window.old_rect.top + pos[1] - 3, \
        properties.ACTION_SUB_WIDTH, 32
      )
      if inv_info_rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.explore_window.it = it

        if self.mouse_click:
          it.free = False
          self.explore_window.inv.items.append( it )

    # Handle resource transfer to old survivors

    inv_info_rect = pygame.rect.Rect(
      properties.MENU_WIDTH + 32 + self.explore_window.new_rect.left + self.explore_window.new_pos[0][0] - 4, \
      32 + self.explore_window.new_rect.top + self.explore_window.new_pos[0][1] - 3, \
      properties.ACTION_SUB_WIDTH, 32
    )

    if self.mouse_click and inv_info_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.explore_window.inv.food > 0 ):
      self.explore_window.expd.inv.food += 1
      self.explore_window.inv.food      -= 1

    inv_info_rect = pygame.rect.Rect(
      properties.MENU_WIDTH + 32 + self.explore_window.new_rect.left + self.explore_window.new_pos[1][0] - 4, \
      32 + self.explore_window.new_rect.top + self.explore_window.new_pos[1][1] - 3, \
      properties.ACTION_SUB_WIDTH, 32
    )

    if self.mouse_click and inv_info_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.explore_window.inv.wood > 0 ):
      self.explore_window.expd.inv.wood += 1
      self.explore_window.inv.wood      -= 1

    inv_info_rect = pygame.rect.Rect(
      properties.MENU_WIDTH + 32 + self.explore_window.new_rect.left + self.explore_window.new_pos[2][0] - 4, \
      32 + self.explore_window.new_rect.top + self.explore_window.new_pos[2][1] - 3, \
      properties.ACTION_SUB_WIDTH, 32
    )

    if self.mouse_click and inv_info_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.explore_window.inv.metal > 0 ):
      self.explore_window.expd.inv.metal += 1
      self.explore_window.inv.metal      -= 1

    inv_info_rect = pygame.rect.Rect(
      properties.MENU_WIDTH + 32 + self.explore_window.new_rect.left + self.explore_window.new_pos[3][0] - 4, \
      32 + self.explore_window.new_rect.top + self.explore_window.new_pos[3][1] - 3, \
      properties.ACTION_SUB_WIDTH, 32
    )

    if self.mouse_click and inv_info_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.explore_window.inv.ammo > 0 ):
      self.explore_window.expd.inv.ammo += 1
      self.explore_window.inv.ammo      -= 1

    # Set active information to display in explore party panel

    for it, pos in zip( self.explore_window.inv.items, self.explore_window.new_pos[4:] ):
      inv_info_rect = pygame.rect.Rect(
        properties.MENU_WIDTH + 32 + self.explore_window.new_rect.left + pos[0] - 4, \
        32 + self.explore_window.new_rect.top + pos[1] - 3, \
        properties.ACTION_SUB_WIDTH, 32
      )
      if inv_info_rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.explore_window.it = it

        if self.mouse_click:
          it.free = True
          self.explore_window.inv.items.remove( it )

    # Scroll old inventory panel

    if self.explore_window.old_scroll_up_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.explore_window.old_scroll > 0 ):
      self.explore_window.old_scroll -= properties.SCROLL_SPEED

    elif self.explore_window.old_scroll_down_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( ( self.explore_window.old_scroll + properties.ACTION_SUB_HEIGHT - 32 ) < self.explore_window.max_old_scroll ):
      self.explore_window.old_scroll += properties.SCROLL_SPEED

    # Scroll new inventory panel

    if self.explore_window.new_scroll_up_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.explore_window.new_scroll > 0 ):
      self.explore_window.new_scroll -= properties.SCROLL_SPEED

    elif self.explore_window.new_scroll_down_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( ( self.explore_window.new_scroll + properties.ACTION_SUB_HEIGHT - 32 ) < self.explore_window.max_new_scroll ):
      self.explore_window.new_scroll += properties.SCROLL_SPEED

    # Go back to menu if ESC pressed

    if self.key_esc:
      self.phase                     = PHASE_EXPL_SURV
      self.explore_window.surv_phase = True
      self.explore_window.old_scroll = 0
      self.explore_window.new_scroll = 0
      self.explore_window.reset_inventory()

    elif self.mouse_click:

      # Move to next phase if next button is clicked

      for button in self.explore_window.button_group:

        button_rect = pygame.rect.Rect(
          properties.MENU_WIDTH + 32 + button.rect.left, \
          32 + button.rect.top, \
          button.rect.width, button.rect.height
        )

        if button_rect.collidepoint( self.mouse_x, self.mouse_y ):
          self.phase                     = PHASE_EXPL_DEST
          self.explore_window.start_tile = None
          self.menu_en                   = False
          self.cam_en                    = True
          self.explore_window.expd.calc_range()
          self.explore_window.expd.highlight_range()

      # Reset phase if clicked outside of context

      if not self.explore_window.rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.phase   = PHASE_FREE
        self.menu_en = False
        self.cam_en  = True
        self.explore_window.reset_expd()

  #.......................................................................
  # PHASE_EXPL_DEST Handling
  #.......................................................................
  # Phase for selecting destination tile for explore party

  def handle_phase_expl_dest( self ):

    # Check if cursor is over a moveable tile

    for ti in self.explore_window.expd.path_dic:

      ti.selected = False

      if ti.rect.collidepoint( self.mouse_x, self.mouse_y ):

        ti.selected = True

        # Destination selected, create new expedition

        if self.mouse_click:
          self.phase                     = PHASE_EXPL_MOVE
          self.explore_window.start_tile = self.explore_window.expd.pos_tile
          self.cam_en                    = False

          move_route, cost = self.explore_window.expd.calc_path( ti )

          new_expd = expedition.Expedition(
            self.explore_window.start_tile,
            self.explore_window.survivors,
            self.explore_window.inv,
            self.map
          )

          new_expd.move_route = move_route
          new_expd.modify_stamina( -cost )

          self.active_expd = new_expd

          self.expeditions.append( new_expd )

          self.explore_window.expd.commit_free()

          self.explore_window.expd.unhighlight_range()

          # Delete old expedition if no survivors left

          if len( self.explore_window.expd.get_free() ) == 0:
            self.explore_window.expd.kill()
            self.expeditions.remove( self.explore_window.expd )

    # Go back to menu if ESC pressed

    if self.key_esc:
      self.phase                     = PHASE_EXPL_INV
      self.menu_en                   = True
      self.cam_en                    = False
      self.explore_window.surv_phase = False
      self.explore_window.old_scroll = 0
      self.explore_window.new_scroll = 0
      self.explore_window.expd.unhighlight_range()

  #.......................................................................
  # PHASE_EXPL_MOVE Handling
  #.......................................................................
  # Phase for actually moving explore party

  def handle_phase_expl_move( self ):

    if len( self.active_expd.move_route ) == 0:
      self.phase                   = PHASE_SCAV_DONE
      self.event_window.expd       = self.active_expd
      self.event_window.survivors  = self.active_expd.survivors
      self.event_window.event_tile = self.active_expd.pos_tile

      # Roll for scavenging

      self.event_window.roll_scavenge()

  #.......................................................................
  # PHASE_SCAV_SURV Handling
  #.......................................................................
  # Phase for selecting survivors to scavenge current tile

  def handle_phase_scav_surv( self ):

    # Set active information to display

    self.scavenge_window.surv = None

    for surv, pos in zip( self.scavenge_window.expd.get_free(), self.scavenge_window.old_pos ):
      surv_info_rect = pygame.rect.Rect(
        properties.MENU_WIDTH + 32 + self.scavenge_window.old_rect.left + pos[0] - 4, \
        32 + self.scavenge_window.old_rect.top + pos[1] - 3, \
        properties.ACTION_SUB_WIDTH, 32
      )
      if surv_info_rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.scavenge_window.surv = surv

        if self.mouse_click:
          surv.free = False
          self.scavenge_window.survivors.append( surv )

    for surv, pos in zip( self.scavenge_window.survivors, self.scavenge_window.new_pos ):
      surv_info_rect = pygame.rect.Rect(
        properties.MENU_WIDTH + 32 + self.scavenge_window.new_rect.left + pos[0] - 4, \
        32 + self.scavenge_window.new_rect.top + pos[1] - 3, \
        properties.ACTION_SUB_WIDTH, 32
      )
      if surv_info_rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.scavenge_window.surv = surv

        if self.mouse_click:
          surv.free = True
          self.scavenge_window.survivors.remove( surv )

    # Scroll old survivors panel

    if self.scavenge_window.old_scroll_up_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.scavenge_window.old_scroll > 0 ):
      self.scavenge_window.old_scroll -= properties.SCROLL_SPEED

    elif self.scavenge_window.old_scroll_down_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( ( self.scavenge_window.old_scroll + properties.ACTION_SUB_HEIGHT - 32 ) < self.scavenge_window.max_old_scroll ):
      self.scavenge_window.old_scroll += properties.SCROLL_SPEED

    # Scroll new survivors panel

    if self.scavenge_window.new_scroll_up_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.scavenge_window.new_scroll > 0 ):
      self.scavenge_window.new_scroll -= properties.SCROLL_SPEED

    elif self.scavenge_window.new_scroll_down_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( ( self.scavenge_window.new_scroll + properties.ACTION_SUB_HEIGHT - 32 ) < self.scavenge_window.max_new_scroll ):
      self.scavenge_window.new_scroll += properties.SCROLL_SPEED

    # Go back to menu if ESC pressed

    if self.key_esc:
      self.phase   = PHASE_FREE
      self.menu_en = True
      self.cam_en  = False
      self.scavenge_window.reset_survivors()

    elif self.mouse_click:

      # Move to next phase if next button is clicked and at least one
      # survivor was chosen.

      for button in self.scavenge_window.button_group:

        button_rect = pygame.rect.Rect(
          properties.MENU_WIDTH + 32 + button.rect.left, \
          32 + button.rect.top, \
          button.rect.width, button.rect.height
        )

        if button_rect.collidepoint( self.mouse_x, self.mouse_y ) \
          and ( len( self.scavenge_window.survivors ) > 0 ):
          self.phase                  = PHASE_SCAV_DONE
          self.event_window.survivors = self.scavenge_window.survivors

          # Roll for scavenging

          self.event_window.roll_scavenge()

      # Reset phase if clicked outside of context

      if not self.explore_window.rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.phase   = PHASE_FREE
        self.menu_en = False
        self.cam_en  = True
        self.scavenge_window.reset_survivors()

  #.......................................................................
  # PHASE_SCAV_DONE Handling
  #.......................................................................
  # Phase for displaying scavenge results

  def handle_phase_scav_done( self ):

    # Reset to free phase once okay button is clicked

    if self.mouse_click:

      for button in self.event_window.button_group:

        button_rect = pygame.rect.Rect(
          properties.MENU_WIDTH + 32 + button.rect.left, \
          properties.CAMERA_HEIGHT / 2 - properties.EVENT_HEIGHT / 2 + button.rect.top, \
          button.rect.width, button.rect.height
        )

        if button_rect.collidepoint( self.mouse_x, self.mouse_y ):
          self.phase   = PHASE_FREE
          self.menu_en = False
          self.cam_en  = True

          # Transfer loot to expedition

          self.event_window.commit_loot()

  #.......................................................................
  # PHASE_STATUS Handling
  #.......................................................................
  # Phase for displaying details about expedition

  def handle_status( self ):

    # Set active information to display

    self.status_window.surv = None
    self.status_window.it   = None

    for surv, pos in zip( self.status_window.expd.survivors, self.status_window.surv_pos ):
      surv_info_rect = pygame.rect.Rect(
        properties.MENU_WIDTH + 32 + self.status_window.surv_rect.left + pos[0] - 4, \
        32 + self.status_window.surv_rect.top + pos[1] - 3, \
        properties.ACTION_SUB_WIDTH, 32
      )
      if surv_info_rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.status_window.surv = surv

    for it, pos in zip( self.status_window.expd.inv.items, self.status_window.inv_pos ):
      inv_info_rect = pygame.rect.Rect(
        properties.MENU_WIDTH + 32 + self.status_window.inv_rect.left + pos[0] - 4, \
        32 + self.status_window.inv_rect.top + pos[1] - 3, \
        properties.ACTION_SUB_WIDTH, 32
      )
      if inv_info_rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.status_window.it = it

    # Scroll survivor panel

    if self.status_window.surv_scroll_up_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.status_window.surv_scroll > 0 ):
      self.status_window.surv_scroll -= properties.SCROLL_SPEED

    elif self.status_window.surv_scroll_down_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( ( self.status_window.surv_scroll + properties.ACTION_SUB_HEIGHT ) < self.status_window.max_surv_scroll ):
      self.status_window.surv_scroll += properties.SCROLL_SPEED

    # Scroll inventory panel

    if self.status_window.inv_scroll_up_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.status_window.inv_scroll > 0 ):
      self.status_window.inv_scroll -= properties.SCROLL_SPEED

    elif self.status_window.inv_scroll_down_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( ( self.status_window.inv_scroll + properties.ACTION_SUB_HEIGHT ) < self.status_window.max_inv_scroll ):
      self.status_window.inv_scroll += properties.SCROLL_SPEED

    # Go back to menu if ESC pressed

    if self.key_esc:
      self.phase   = PHASE_FREE
      self.menu_en = True
      self.cam_en  = False

    # Reset phase if clicked outside of context

    elif self.mouse_click and not self.status_window.rect.collidepoint( self.mouse_x, self.mouse_y ):
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

        elif self.phase == PHASE_EXPL_INV:
          self.handle_phase_expl_inv()

        elif self.phase == PHASE_EXPL_DEST:
          self.handle_phase_expl_dest()

        elif self.phase == PHASE_EXPL_MOVE:
          self.handle_phase_expl_move()

        elif self.phase == PHASE_SCAV_SURV:
          self.handle_phase_scav_surv()

        elif self.phase == PHASE_SCAV_DONE:
          self.handle_phase_scav_done()

        elif self.phase == PHASE_CRAFT_ITEM:
          self.handle_phase_craft_item()

        elif self.phase == PHASE_STATUS:
          self.handle_status()

      # Update graphics

      self.update_all()
      self.draw_all()

      # Increment clock

      clock.tick( properties.FPS )
