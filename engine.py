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
import costbox
import survivorwindow
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
    self.key_space   = False

    # Phase-specific variables

    self.menu_en           = False
    self.active_expedition = None
    self.explored          = False

    # Initialize sprite groups

    self.map_group         = pygame.sprite.RenderUpdates()
    self.expeditions_group = pygame.sprite.RenderUpdates()
    self.menu_group        = pygame.sprite.RenderUpdates()

    # Assign default groups to sprite classes

    expedition.Expedition.groups = self.expeditions_group

    # Initialize menu graphics

    menu_pos_y = properties.MENU_OFFSET_Y

    for text in properties.MENU_TEXT:
      self.menu_group.add( [ button.Button( text, properties.MENU_OFFSET_X, menu_pos_y ) ] )
      menu_pos_y += properties.MENU_HEIGHT + properties.MENU_PADDING

    # Initialize window surfaces

    self.screen = pygame.display.get_surface()

    self.camera_window = window.Window(
      properties.CAMERA_WIDTH, properties.CAMERA_HEIGHT,
      0, 0
    )

    self.sidebar_window = sidebarwindow.SidebarWindow(
      properties.SIDEBAR_WIDTH, properties.SIDEBAR_HEIGHT,
      properties.CAMERA_WIDTH, 0,
      properties.SIDEBAR_PATH + 'sidebar_bg.png',
      self.expeditions
    )

    self.explore_window = explorewindow.ExploreWindow(
      properties.ACTION_WIDTH, properties.ACTION_HEIGHT,
      properties.MENU_WIDTH + 32, 32,
      properties.ACTION_PATH + 'action_bg.png'
    )

    self.scavenge_window = survivorwindow.SurvivorWindow(
      properties.ACTION_WIDTH, properties.ACTION_HEIGHT,
      properties.MENU_WIDTH + 32, 32,
      properties.ACTION_PATH + 'action_bg.png',
      'SCAVENGING PARTY'
    )

    self.event_window = eventwindow.EventWindow(
      properties.EVENT_WIDTH, properties.EVENT_HEIGHT,
      properties.MENU_WIDTH + 32,
      properties.CAMERA_HEIGHT / 2 - properties.EVENT_HEIGHT / 2,
      properties.EVENT_PATH + 'event_bg.png'
    )

    self.rest_window = survivorwindow.SurvivorWindow(
      properties.ACTION_WIDTH, properties.ACTION_HEIGHT,
      properties.MENU_WIDTH + 32, 32, \
      properties.ACTION_PATH + 'action_bg.png',
      'RESTING PARTY'
    )

    self.status_window = statuswindow.StatusWindow(
      properties.ACTION_WIDTH, properties.ACTION_HEIGHT,
      properties.MENU_WIDTH + 32, 32,
      properties.ACTION_PATH + 'action_bg.png'
    )

    # Initialize cost box for movement

    self.cost_box = costbox.CostBox()

    # Adjust window scroll zones with absolute offset

    self.status_window.surv_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.status_window.surv_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.status_window.inv_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.status_window.inv_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )

    self.scavenge_window.old_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.scavenge_window.old_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.scavenge_window.new_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.scavenge_window.new_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )

    self.rest_window.old_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.rest_window.old_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.rest_window.new_scroll_up_rect.move_ip( properties.MENU_WIDTH + 32, 32 )
    self.rest_window.new_scroll_down_rect.move_ip( properties.MENU_WIDTH + 32, 32 )

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

    # Center camera on starting expedition

    self.center_camera( start_tile )

  #.......................................................................
  # Find next expedition with free survivors
  #.......................................................................

  def get_next_expedition( self ):

    for _expedition in self.expeditions:
      if len( _expedition.get_free() ) > 0:
        return _expedition

    return None

  #.......................................................................
  # Get inputs
  #.......................................................................

  def get_inputs( self ):

    self.mouse_click = False
    self.key_esc     = False
    self.key_space   = False

    for event in pygame.event.get():

      if event.type == MOUSEMOTION:
        self.mouse_x = event.pos[0]
        self.mouse_y = event.pos[1]

      elif event.type == MOUSEBUTTONDOWN:
        self.mouse_click = True

      elif ( event.type == KEYDOWN ) and ( event.key == K_ESCAPE ):
        self.key_esc = True

      elif ( event.type == KEYDOWN ) and ( event.key == K_SPACE ):
        self.key_space = True

  #.......................................................................
  # Center camera around given tile
  #.......................................................................

  def center_camera( self, tile ):

    # Define limits of camera range

    camera_limit = pygame.rect.Rect(
      0, 0,
      properties.MAP_WIDTH - properties.CAMERA_WIDTH,
      properties.MAP_HEIGHT - properties.CAMERA_HEIGHT
    )

    # Determine camera center coordinates

    center_x = tile.pos_x * properties.TILE_WIDTH + properties.TILE_WIDTH / 2
    center_y = tile.pos_y * properties.TILE_HEIGHT + properties.TILE_HEIGHT / 2

    self.cam_x = center_x - properties.CAMERA_WIDTH / 2
    self.cam_y = center_y - properties.CAMERA_HEIGHT / 2

    # Adjust camera coordinates if outside of camera limits

    if self.cam_x < 0:
      self.cam_x = camera_limit.left
    elif self.cam_x > camera_limit.right:
      self.cam_x = camera_limit.right

    if self.cam_y < 0:
      self.cam_y = camera_limit.top
    elif self.cam_y > camera_limit.bottom:
      self.cam_y = camera_limit.bottom

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

    if self.mouse_click:

      for button in self.menu_group:
        if button.rect.collidepoint( self.mouse_x, self.mouse_y ):

          # Assign active terrain to display on sidebar

          self.sidebar_window._tile = self.active_expedition.pos_tile

          # Reset survivors/inventory free state

          self.explore_window.reset_expedition()
          self.scavenge_window.reset_survivors()
          self.rest_window.reset_survivors()

          # Phase transition based on button click

          if button.text == 'EXPLORE':
            self.phase                      = PHASE_EXPL_SURV
            self.explore_window._expedition = self.active_expedition
            self.explore_window.start_phase = True
            self.explore_window.clear()
            self.scavenge_window.clear()
            self.rest_window.clear()

          elif button.text == 'SCAVENGE':
            self.phase                       = PHASE_SCAV_SURV
            self.scavenge_window._expedition = self.active_expedition
            self.scavenge_window.clear()
            self.explore_window.clear()
            self.rest_window.clear()
            self.event_window._expedition    = self.active_expedition
            self.event_window.event_tile     = self.active_expedition.pos_tile

          elif button.text == 'CRAFT':
            self.phase = PHASE_CRAFT_ITEM

          elif button.text == 'REST':
            self.phase                   = PHASE_REST
            self.rest_window._expedition = self.active_expedition
            self.explore_window.clear()
            self.scavenge_window.clear()
            self.rest_window.clear()

          elif button.text == 'STATUS':
            self.phase                     = PHASE_STATUS
            self.status_window._expedition = self.active_expedition

          return True

    return False

  #.......................................................................
  # Handle done button for moving onto next day
  #.......................................................................

  def handle_done( self ):

    # Process inputs

    next_phase = self.sidebar_window.process_inputs(
      self.mouse_x, self.mouse_y, self.mouse_click
    )

    # Move onto night phase if done button is clicked in the free look
    # phase and there are no more free survivors.

    if next_phase and ( self.phase == PHASE_FREE ):

      self.phase     = PHASE_FREE
      self.menu_en   = False
      self.cam_en    = True

      # Increment day counter

      self.sidebar_window.time_count += 1

      # Reset all survivors to be free

      for _expedition in self.expeditions:
        _expedition.reset_free_survivors()

      return True

    return False

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
        self.sidebar_window._tile = context_tile

      # Sidebar expedition information (only when menu is disabled)

      active_expedition = None

      for _expedition in self.expeditions:
        if context_tile == _expedition.pos_tile:
          active_expedition = _expedition
          break

      if not self.menu_en:
        self.sidebar_window._expedition = active_expedition

    else:

      active_expedition               = None
      self.sidebar_window._tile       = None
      self.sidebar_window._expedition = None

    # Center camera on next expedition if space pressed

    if self.key_space:

      next_expedition = self.get_next_expedition()

      if next_expedition != None:
        self.center_camera( next_expedition.pos_tile )

    # Escape menu if ESC key pressed

    elif self.key_esc:

      self.menu_en = False
      self.cam_en  = True

    # Check for mouse click

    elif self.mouse_click \
      and ( self.mouse_x >= 0 ) and ( self.mouse_x < properties.CAMERA_WIDTH ) \
      and ( self.mouse_y >= 0 ) and ( self.mouse_y < properties.CAMERA_HEIGHT ):

      # Enable menu if expedition is clicked

      self.menu_en = False
      self.cam_en  = True

      if active_expedition != None:
        self.active_expedition = active_expedition
        self.menu_en           = True
        self.cam_en            = False

  #.......................................................................
  # PHASE_EXPL_SURV Handling
  #.......................................................................
  # Phase for selecting survivors to explore new tile

  def handle_phase_expl_surv( self ):

    # Process inputs

    next_phase = self.explore_window.process_inputs(
      self.mouse_x, self.mouse_y, self.mouse_click
    )

    # Go back to menu if ESC pressed

    if self.key_esc:

      self.phase   = PHASE_FREE
      self.menu_en = True
      self.cam_en  = False
      self.explore_window.reset_expedition()

    # Reset phase if clicked outside of context

    elif self.mouse_click \
      and not self.explore_window.rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.mouse_x >= 0 ) and ( self.mouse_x < properties.CAMERA_WIDTH ) \
      and ( self.mouse_y >= 0 ) and ( self.mouse_y < properties.CAMERA_HEIGHT ):

      self.phase   = PHASE_FREE
      self.menu_en = False
      self.cam_en  = True
      self.explore_window.reset_expedition()

    # Move to next phase if next button is clicked and at least one
    # survivor was chosen.

    elif next_phase:

      # If all survivors explore, skip inventory selection and
      # automatically transfer all items and resources over to
      # explore party.

      if len( self.explore_window._expedition.get_free() ) == 0:

        self.phase                     = PHASE_EXPL_DEST
        self.explore_window.pos_tile   = None
        self.menu_en                   = False
        self.cam_en                    = True
        self.explore_window._expedition.calc_range( self.explore_window.survivors )
        self.explore_window._expedition.highlight_range()
        self.explore_window._inventory = self.explore_window._expedition._inventory

      # Otherwise, go into inventory selection

      else:

        self.phase                      = PHASE_EXPL_INV
        self.explore_window._inventory  = inventory.Inventory( 0, 0, 0, 0, [] )
        self.explore_window.start_phase = False
        self.explore_window.reset_scroll()

  #.......................................................................
  # PHASE_EXPL_INV Handling
  #.......................................................................
  # Phase for selecting inventory for explore party

  def handle_phase_expl_inv( self ):


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
          self.explore_window.expd.calc_range( self.explore_window.survivors )
          self.explore_window.expd.highlight_range()

      # Reset phase if clicked outside of context

      if not self.explore_window.rect.collidepoint( self.mouse_x, self.mouse_y ) \
        and ( self.mouse_x >= 0 ) and ( self.mouse_x < properties.CAMERA_WIDTH ) \
        and ( self.mouse_y >= 0 ) and ( self.mouse_y < properties.CAMERA_HEIGHT ):
        self.phase   = PHASE_FREE
        self.menu_en = False
        self.cam_en  = True
        self.explore_window.reset_expedition()

  #.......................................................................
  # PHASE_EXPL_DEST Handling
  #.......................................................................
  # Phase for selecting destination tile for explore party

  def handle_phase_expl_dest( self ):

    # Calculate current tile mouse is hovering over

    context_x = ( self.cam_x + self.mouse_x ) / properties.TILE_WIDTH
    context_y = ( self.cam_y + self.mouse_y ) / properties.TILE_HEIGHT

    self.sidebar_window._tile = None

    if ( context_x >= 0 ) and ( context_x < properties.MAP_SIZE ) \
      and ( context_y >= 0 ) and ( context_y < properties.MAP_SIZE ) \
      and ( self.mouse_x >= 0 ) and ( self.mouse_x < properties.CAMERA_WIDTH ) \
      and ( self.mouse_y >= 0 ) and ( self.mouse_y < properties.CAMERA_HEIGHT ):

      context_tile = self.map[context_x][context_y]

      # Sidebar terrain information (only show if revealed on map)

      if not context_tile.fog:
        self.sidebar_window._tile = context_tile

    # Reset cost box

    self.cost_box.cost = 0

    # Check if cursor is over a moveable tile

    for ti, info in self.explore_window.expd.path_dic.iteritems():

      ti.selected = False

      if ti.rect.collidepoint( self.mouse_x, self.mouse_y ):

        # Highlight destination tile

        ti.selected = True

        # Enable cost box with appropriate stamina cost

        self.cost_box.cost  = info[1]
        self.cost_box.pos_x = self.mouse_x
        self.cost_box.pos_y = self.mouse_y

        # Destination selected, create new expedition

        if self.mouse_click:
          self.phase                     = PHASE_EXPL_MOVE
          self.explore_window.start_tile = self.explore_window.expd.pos_tile
          self.cam_en                    = False

          move_route, cost = self.explore_window.expd.calc_path( ti )

          # Keep old expedition's image if all survivors exploring

          if len( self.explore_window.expd.get_free() ) == 0:
            new_expd_img_idx = self.explore_window.expd.img_roll
          else:
            new_expd_img_idx = -1

          new_expd = expedition.Expedition(
            self.explore_window.start_tile,
            self.explore_window.survivors,
            self.explore_window.inv,
            self.map,
            new_expd_img_idx
          )

          new_expd.move_route = move_route
          new_expd.modify_stamina( -cost )
          new_expd.set_direction()
          new_expd.draw_animation()

          self.active_expedition = new_expd

          self.expeditions.append( new_expd )

          self.explore_window.expd.commit_free()
          new_expd.inv.reset_free()

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

    if len( self.active_expedition.move_route ) == 0:
      self.phase = PHASE_SCAV_DONE

      # Configure event window for scavenging event

      self.event_window.expd       = self.active_expedition
      self.event_window.survivors  = self.active_expedition.survivors
      self.event_window.event_tile = self.active_expedition.pos_tile

      self.explored = True

      # Merge expeditions if on same tile

      for expd in self.expeditions:
        if ( self.active_expedition != expd ) \
          and ( self.active_expedition.pos_tile == expd.pos_tile ):
          expd.merge( self.active_expedition )
          self.expeditions.remove( self.active_expedition )
          self.event_window.expd = expd
          break

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

        if self.mouse_click and ( surv.stamina > properties.SCAVENGE_COST ):
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

      if not self.explore_window.rect.collidepoint( self.mouse_x, self.mouse_y ) \
        and ( self.mouse_x >= 0 ) and ( self.mouse_x < properties.CAMERA_WIDTH ) \
        and ( self.mouse_y >= 0 ) and ( self.mouse_y < properties.CAMERA_HEIGHT ):
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

          # Subtract scavenge cost from stamina (only if selecting from
          # menu, if exploring, scavenge for free)

          if self.explored:
            self.explored = False
          else:
            for surv in self.event_window.survivors:
              surv.stamina -= properties.SCAVENGE_COST

          # Clean up selection windows

          self.explore_window.clear()
          self.scavenge_window.clear()
          self.rest_window.clear()

  #.......................................................................
  # Heal survivors in rest phase
  #.......................................................................

  def heal_survivors( self, survivors ):

    for _survivor in survivors:

      heal_rate = _survivor.heal_rate

      # Roll for curing sickness. If not cured, the healing rate is
      # decreased by the sickness healing multiplier.

      if _survivor.sick:

        roll = random.random()

        if roll < _survivor.cure_rate:
          _survivor.sick = False

        else:
          heal_rate *= properties.SICK_HEAL_MULT

      # Heal survivor based on age. Note that the healing rate goes back
      # to normal on the same turn the sickness is cured.

      _survivor.stamina += int( _survivor.max_stamina * heal_rate )

      if _survivor.stamina > _survivor.max_stamina:
        _survivor.stamina = _survivor.max_stamina

  #.......................................................................
  # PHASE_REST Handling
  #.......................................................................
  # Phase for selecting survivors to rest

  def handle_phase_rest( self ):

    # Set active information to display

    self.rest_window.surv = None

    for surv, pos in zip( self.rest_window.expd.get_free(), self.rest_window.old_pos ):
      surv_info_rect = pygame.rect.Rect(
        properties.MENU_WIDTH + 32 + self.rest_window.old_rect.left + pos[0] - 4, \
        32 + self.rest_window.old_rect.top + pos[1] - 3, \
        properties.ACTION_SUB_WIDTH, 32
      )
      if surv_info_rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.rest_window.surv = surv

        if self.mouse_click:
          surv.free = False
          self.rest_window.survivors.append( surv )

    for surv, pos in zip( self.rest_window.survivors, self.rest_window.new_pos ):
      surv_info_rect = pygame.rect.Rect(
        properties.MENU_WIDTH + 32 + self.rest_window.new_rect.left + pos[0] - 4, \
        32 + self.rest_window.new_rect.top + pos[1] - 3, \
        properties.ACTION_SUB_WIDTH, 32
      )
      if surv_info_rect.collidepoint( self.mouse_x, self.mouse_y ):
        self.rest_window.surv = surv

        if self.mouse_click:
          surv.free = True
          self.rest_window.survivors.remove( surv )

    # Scroll old survivors panel

    if self.rest_window.old_scroll_up_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.rest_window.old_scroll > 0 ):
      self.rest_window.old_scroll -= properties.SCROLL_SPEED

    elif self.rest_window.old_scroll_down_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( ( self.rest_window.old_scroll + properties.ACTION_SUB_HEIGHT - 32 ) < self.rest_window.max_old_scroll ):
      self.rest_window.old_scroll += properties.SCROLL_SPEED

    # Scroll new survivors panel

    if self.rest_window.new_scroll_up_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.rest_window.new_scroll > 0 ):
      self.rest_window.new_scroll -= properties.SCROLL_SPEED

    elif self.rest_window.new_scroll_down_rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( ( self.rest_window.new_scroll + properties.ACTION_SUB_HEIGHT - 32 ) < self.rest_window.max_new_scroll ):
      self.rest_window.new_scroll += properties.SCROLL_SPEED

    # Go back to menu if ESC pressed

    if self.key_esc:
      self.phase   = PHASE_FREE
      self.menu_en = True
      self.cam_en  = False
      self.rest_window.reset_survivors()

    elif self.mouse_click:

      # Move to next phase if next button is clicked and at least one
      # survivor was chosen.

      for button in self.rest_window.button_group:

        button_rect = pygame.rect.Rect(
          properties.MENU_WIDTH + 32 + button.rect.left, \
          32 + button.rect.top, \
          button.rect.width, button.rect.height
        )

        if button_rect.collidepoint( self.mouse_x, self.mouse_y ) \
          and ( len( self.rest_window.survivors ) > 0 ):
          self.phase   = PHASE_FREE
          self.menu_en = False
          self.cam_en  = True

          # Heal resting survivors based on age

          self.heal_survivors( self.rest_window.survivors )

          # Clean up selection windows

          self.explore_window.clear()
          self.scavenge_window.clear()
          self.rest_window.clear()

      # Reset phase if clicked outside of context

      if not self.explore_window.rect.collidepoint( self.mouse_x, self.mouse_y ) \
        and ( self.mouse_x >= 0 ) and ( self.mouse_x < properties.CAMERA_WIDTH ) \
        and ( self.mouse_y >= 0 ) and ( self.mouse_y < properties.CAMERA_HEIGHT ):
        self.phase   = PHASE_FREE
        self.menu_en = False
        self.cam_en  = True
        self.rest_window.reset_survivors()

  #.......................................................................
  # PHASE_STATUS Handling
  #.......................................................................
  # Phase for displaying details about expedition

  def handle_phase_status( self ):

    # Set active information to display

    self.status_window._survivor = None
    self.status_window._item     = None

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

    elif self.mouse_click and not self.status_window.rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and ( self.mouse_x >= 0 ) and ( self.mouse_x < properties.CAMERA_WIDTH ) \
      and ( self.mouse_y >= 0 ) and ( self.mouse_y < properties.CAMERA_HEIGHT ):
      self.phase   = PHASE_FREE
      self.menu_en = False
      self.cam_en  = True

  #.......................................................................
  # Update all sprites
  #.......................................................................

  def update_all( self ):

    self.map_group.update( self.cam_x, self.cam_y )
    self.expd_group.update( self.cam_x, self.cam_y, self.cam_en )
    self.sidebar_window.update()
    self.explore_window.update()
    self.cost_box.update()
    self.scavenge_window.update()
    self.rest_window.update()
    self.status_window.update()

  #.......................................................................
  # Draw all sprites
  #.......................................................................

  def draw_all( self ):

    # Draw map and associated markers

    rect_updates =  self.map_group.draw( self.camera_window.image )
    rect_updates += self.expd_group.draw( self.camera_window.image )

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
    elif self.phase == PHASE_EXPL_DEST:
      rect_updates += self.cost_box.draw( self.screen )
    elif self.phase == PHASE_SCAV_SURV:
      rect_updates += self.scavenge_window.draw( self.screen )
    elif self.phase == PHASE_SCAV_DONE:
      rect_updates += self.event_window.draw( self.screen )
    elif self.phase == PHASE_REST:
      rect_updates += self.rest_window.draw( self.screen )
    elif self.phase == PHASE_STATUS:
      rect_updates += self.status_window.draw( self.screen )

    # Update the display

    pygame.display.update( rect_updates )

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

      # Handle done selection

      done_used = self.handle_done()

      # Handle menu selection

      menu_used = False

      if self.menu_en:
        menu_used = self.handle_menu()

      # Handle game phases

      if not done_used and not menu_used:

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

        elif self.phase == PHASE_REST:
          self.handle_phase_rest()

        elif self.phase == PHASE_STATUS:
          self.handle_phase_status()

      # Update graphics

      self.update_all()
      self.draw_all()

      # Increment clock

      clock.tick( properties.FPS )
