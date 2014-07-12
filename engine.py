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
import survivorwindow
import inventorywindow
import costbox
import eventwindow
import craftwindow
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

PHASE_FREE, PHASE_SCAVENGE0, PHASE_SCAVENGE1, \
PHASE_EXPLORE0, PHASE_EXPLORE1, PHASE_EXPLORE2, PHASE_EXPLORE3, \
PHASE_CRAFT, PHASE_REST, PHASE_STATUS, \
PHASE_NIGHT, PHASE_TRANSITION  = range( 12 )

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

    self.survivor_window = survivorwindow.SurvivorWindow(
      properties.ACTION_WIDTH, properties.ACTION_HEIGHT,
      properties.MENU_WIDTH + 32, 32,
      properties.ACTION_PATH + 'action_bg.png'
    )

    self.inventory_window = inventorywindow.InventoryWindow(
      properties.ACTION_WIDTH, properties.ACTION_HEIGHT,
      properties.MENU_WIDTH + 32, 32,
      properties.ACTION_PATH + 'action_bg.png'
    )

    self.event_window = eventwindow.EventWindow(
      properties.EVENT_WIDTH, properties.EVENT_HEIGHT,
      properties.MENU_WIDTH + 32,
      properties.CAMERA_HEIGHT / 2 - properties.EVENT_HEIGHT / 2,
      properties.EVENT_PATH + 'event_bg.png'
    )

    self.craft_window = craftwindow.CraftWindow(
      properties.ACTION_WIDTH, properties.ACTION_HEIGHT,
      properties.MENU_WIDTH + 32, 32,
      properties.ACTION_PATH + 'action_bg.png'
    )

    self.status_window = statuswindow.StatusWindow(
      properties.ACTION_WIDTH, properties.ACTION_HEIGHT,
      properties.MENU_WIDTH + 32, 32,
      properties.ACTION_PATH + 'action_bg.png'
    )

    # Initialize cost box for movement

    self.cost_box = costbox.CostBox()

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

    pos_tile = self.map[pos_x][pos_y]

    # Generate random set of starting survivors

    survivors = []

    for i in range( properties.NUM_START_SURVIVORS ):
      survivors.append( survivor.Survivor() )

    # Initialize starting inventory

    _inventory = inventory.Inventory(
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

    self.expeditions.append(
      expedition.Expedition( pos_tile, survivors, _inventory, self.map )
    )

    # Center camera on starting expedition

    self.center_camera( pos_tile )

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

    # Only scroll if within camera window

    if self.camera_window.rect.collidepoint( self.mouse_x, self.mouse_y ):

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

          # Reset all window state

          if self.phase == PHASE_EXPLORE0:
            self.survivor_window.free()
          elif self.phase == PHASE_EXPLORE1:
            self.survivor_window.free()
            self.inventory_window.reset()
          elif self.phase == PHASE_SCAVENGE0:
            self.survivor_window.free()
          elif self.phase == PHASE_REST:
            self.survivor_window.free()

          # Phase transition based on button click

          if button.text == 'EXPLORE' and ( len( self.active_expedition.get_free() ) > 0 ):
            self.phase                       = PHASE_EXPLORE0
            self.survivor_window.reset()
            self.survivor_window._expedition = self.active_expedition

          elif button.text == 'SCAVENGE' and ( len( self.active_expedition.get_free() ) > 0 ):
            self.phase                       = PHASE_SCAVENGE0
            self.survivor_window.reset()
            self.survivor_window._expedition = self.active_expedition

          elif button.text == 'CRAFT' and ( len( self.active_expedition.get_free() ) > 0 ):
            self.phase                    = PHASE_CRAFT
            self.craft_window.reset()
            self.craft_window._expedition = self.active_expedition

          elif button.text == 'REST' and ( len( self.active_expedition.get_free() ) > 0 ):
            self.phase                       = PHASE_REST
            self.survivor_window.reset()
            self.survivor_window._expedition = self.active_expedition

          elif button.text == 'STATUS':
            self.phase                     = PHASE_STATUS
            self.status_window.reset()
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
        _expedition.free_survivors()

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
      and self.camera_window.rect.collidepoint( self.mouse_x, self.mouse_y ):

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
      and self.camera_window.rect.collidepoint( self.mouse_x, self.mouse_y ):

      # Enable menu if expedition is clicked

      self.menu_en = False
      self.cam_en  = True

      if active_expedition != None:
        self.active_expedition = active_expedition
        self.menu_en           = True
        self.cam_en            = False

  #.......................................................................
  # PHASE_EXPLORE0 Handling
  #.......................................................................
  # Phase for selecting survivors to explore new tile

  def handle_phase_explore0( self ):

    # Process inputs

    next_phase = self.survivor_window.process_inputs(
      self.mouse_x, self.mouse_y, self.mouse_click, 1
    )

    # Go back to menu if ESC pressed

    if self.key_esc:

      self.phase   = PHASE_FREE
      self.menu_en = True
      self.cam_en  = False
      self.survivor_window.free()

    # Reset phase if clicked outside of context

    elif self.mouse_click \
      and not self.survivor_window.rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and self.camera_window.rect.collidepoint( self.mouse_x, self.mouse_y ):

      self.phase   = PHASE_FREE
      self.menu_en = False
      self.cam_en  = True
      self.survivor_window.free()

    # Move to next phase if next button is clicked and at least one
    # survivor was chosen.

    elif next_phase:

      # If all survivors explore, skip inventory selection and
      # automatically transfer all items and resources over to
      # explore party.

      if len( self.survivor_window._expedition.get_free() ) == 0:

        self.phase                        = PHASE_EXPLORE2
        self.menu_en                      = False
        self.cam_en                       = True
        self.inventory_window.reset()
        self.inventory_window._expedition = self.active_expedition
        self.inventory_window._inventory  = self.active_expedition._inventory
        self.active_expedition.calc_range( self.survivor_window.survivors )
        self.active_expedition.highlight_range()

      # Otherwise, go into inventory selection

      else:

        self.phase                        = PHASE_EXPLORE1
        self.inventory_window.reset()
        self.inventory_window._expedition = self.active_expedition

  #.......................................................................
  # PHASE_EXPLORE1 Handling
  #.......................................................................
  # Phase for selecting inventory for explore party

  def handle_phase_explore1( self ):

    # Process inputs

    next_phase = self.inventory_window.process_inputs(
      self.mouse_x, self.mouse_y, self.mouse_click
    )

    # Go back to menu if ESC pressed

    if self.key_esc:

      self.phase = PHASE_EXPLORE0
      self.inventory_window.free()

    # Reset phase if clicked outside of context

    elif self.mouse_click \
      and not self.inventory_window.rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and self.camera_window.rect.collidepoint( self.mouse_x, self.mouse_y ):

      self.phase   = PHASE_FREE
      self.menu_en = False
      self.cam_en  = True
      self.survivor_window.free()
      self.inventory_window.free()

    # Move to next phase if next button is clicked

    elif next_phase:

      self.phase                     = PHASE_EXPLORE2
      self.menu_en                   = False
      self.cam_en                    = True
      self.active_expedition.calc_range( self.survivor_window.survivors )
      self.active_expedition.highlight_range()

  #.......................................................................
  # PHASE_EXPLORE2 Handling
  #.......................................................................
  # Phase for selecting destination tile for explore party

  def handle_phase_explore2( self ):

    # Calculate current tile mouse is hovering over

    context_x = ( self.cam_x + self.mouse_x ) / properties.TILE_WIDTH
    context_y = ( self.cam_y + self.mouse_y ) / properties.TILE_HEIGHT

    self.sidebar_window._tile = None

    if ( context_x >= 0 ) and ( context_x < properties.MAP_SIZE ) \
      and ( context_y >= 0 ) and ( context_y < properties.MAP_SIZE ) \
      and self.camera_window.rect.collidepoint( self.mouse_x, self.mouse_y ):

      context_tile = self.map[context_x][context_y]

      # Sidebar terrain information (only show if revealed on map)

      if not context_tile.fog:
        self.sidebar_window._tile = context_tile

    # Reset cost box

    self.cost_box.cost = 0

    # Check if cursor is over a moveable tile

    for _tile, info in self.active_expedition.path_dic.iteritems():

      _tile.selected = False

      if _tile.rect.collidepoint( self.mouse_x, self.mouse_y ):

        # Highlight destination tile

        _tile.selected = True

        # Enable cost box with appropriate stamina cost

        self.cost_box.cost  = info[1]
        self.cost_box.pos_x = self.mouse_x
        self.cost_box.pos_y = self.mouse_y

        # Move to next phase if valid destination selected

        if self.mouse_click:

          self.phase  = PHASE_EXPLORE3
          self.cam_en = False

          # Keep old expedition's image if all survivors exploring

          all_explore = False

          if len( self.active_expedition.survivors ) == len( self.survivor_window.survivors ):
            all_explore = True
            img_idx     = self.active_expedition.img_roll
          else:
            img_idx = -1

          # Create new expedition

          _expedition = expedition.Expedition(
            self.active_expedition.pos_tile,
            self.survivor_window.survivors,
            self.inventory_window._inventory,
            self.map,
            img_idx
          )

          # Configure movement route, subtract cost

          move_route, cost = self.active_expedition.calc_path( _tile )

          _expedition.move_route = move_route
          _expedition.modify_stamina( -cost )
          _expedition.set_direction()
          _expedition.draw_animation()

          # Finalize changes and delete old expedition if all transferred

          self.active_expedition.unhighlight_range()
          self.active_expedition.commit()

          if all_explore:
            self.active_expedition.kill()
            self.expeditions.remove( self.active_expedition )

          # Assign new expedition as active

          self.active_expedition = _expedition
          self.expeditions.append( _expedition )

          # Free up transferred items

          self.active_expedition._inventory.free()

          break

    # Go back to menu if ESC pressed

    if self.key_esc:

      self.phase   = PHASE_EXPLORE1
      self.menu_en = True
      self.cam_en  = False
      self.active_expedition.unhighlight_range()

  #.......................................................................
  # PHASE_EXPLORE3 Handling
  #.......................................................................
  # Phase for actually moving explore party

  def handle_phase_explore3( self ):

    # Wait until movement animation is finished (if coming from explore
    # phase). Move to next phase once movement is done to display
    # scavenging results.

    if len( self.active_expedition.move_route ) == 0:

      self.phase = PHASE_SCAVENGE1

      # Configure event window for scavenging event

      self.event_window.reset()
      self.event_window._expedition = self.active_expedition
      self.event_window.survivors   = self.active_expedition.survivors
      self.event_window._tile       = self.active_expedition.pos_tile

      # Need to set a special flag so the scavenge phase knows not to
      # charge any stamina when coming from explore phase.

      self.explored = True

      # Merge expeditions if on same tile

      for _expedition in self.expeditions:
        if ( self.active_expedition != _expedition ) \
          and ( self.active_expedition.pos_tile == _expedition.pos_tile ):
          self.active_expedition.merge( _expedition )
          self.expeditions.remove( _expedition )
          self.event_window._expedition = self.active_expedition
          break

      # Roll for scavenging

      self.event_window.scavenge()

  #.......................................................................
  # PHASE_SCAVENGE0 Handling
  #.......................................................................
  # Phase for selecting survivors to scavenge current tile

  def handle_phase_scavenge0( self ):

    # Process inputs

    next_phase = self.survivor_window.process_inputs(
      self.mouse_x, self.mouse_y, self.mouse_click, properties.SCAVENGE_COST
    )

    # Go back to menu if ESC pressed

    if self.key_esc:

      self.phase   = PHASE_FREE
      self.menu_en = True
      self.cam_en  = False
      self.survivor_window.free()

    # Reset phase if clicked outside of context

    elif self.mouse_click \
      and not self.survivor_window.rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and self.camera_window.rect.collidepoint( self.mouse_x, self.mouse_y ):

      self.phase   = PHASE_FREE
      self.menu_en = False
      self.cam_en  = True
      self.survivor_window.free()

    # Move to next phase if next button is clicked and at least one
    # survivor was chosen.

    elif next_phase:

      self.phase                    = PHASE_SCAVENGE1
      self.event_window.reset()
      self.event_window._expedition = self.active_expedition
      self.event_window.survivors   = self.survivor_window.survivors
      self.event_window._tile       = self.active_expedition.pos_tile

      # Roll for scavenging

      self.event_window.scavenge()

  #.......................................................................
  # PHASE_SCAVENGE1 Handling
  #.......................................................................
  # Phase for displaying scavenge results

  def handle_phase_scavenge1( self ):

    # Process inputs

    next_phase = self.event_window.process_inputs(
      self.mouse_x, self.mouse_y, self.mouse_click
    )

    # Reset to free phase once okay button is clicked or ESC pressed

    if self.key_esc or next_phase:

      self.phase   = PHASE_FREE
      self.menu_en = False
      self.cam_en  = True

      # Transfer loot to expedition and subtract scavenge cost from
      # stamina (only if selecting from menu, if exploring, scavenge for
      # free).

      self.event_window.commit( self.explored )

      self.explored = False

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

    # Process inputs

    next_phase = self.survivor_window.process_inputs(
      self.mouse_x, self.mouse_y, self.mouse_click
    )

    # Go back to menu if ESC pressed

    if self.key_esc:

      self.phase   = PHASE_FREE
      self.menu_en = True
      self.cam_en  = False
      self.survivor_window.free()

    # Reset phase if clicked outside of context

    elif self.mouse_click \
      and not self.survivor_window.rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and self.camera_window.rect.collidepoint( self.mouse_x, self.mouse_y ):

      self.phase   = PHASE_FREE
      self.menu_en = False
      self.cam_en  = True
      self.survivor_window.free()

    # Move to next phase if next button is clicked and at least one
    # survivor was chosen.

    elif next_phase:

      self.phase   = PHASE_FREE
      self.menu_en = False
      self.cam_en  = True

      # Heal resting survivors based on age

      self.heal_survivors( self.survivor_window.survivors )

  #.......................................................................
  # PHASE_CRAFT Handling
  #.......................................................................
  # Phase for crafting items

  def handle_phase_craft( self ):

    # Process inputs

    next_phase = self.craft_window.process_inputs(
      self.mouse_x, self.mouse_y, self.mouse_click, properties.CRAFT_COST
    )

    # Go back to menu if ESC pressed

    if self.key_esc:

      if self.craft_window.selected:
        self.craft_window.half_reset()

      else:
        self.phase   = PHASE_FREE
        self.menu_en = True
        self.cam_en  = False

    # Reset phase if clicked outside of context

    elif self.mouse_click \
      and not self.craft_window.rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and self.camera_window.rect.collidepoint( self.mouse_x, self.mouse_y ):

      self.phase   = PHASE_FREE
      self.menu_en = False
      self.cam_en  = True

    # Craft item if necessary requirements met

    elif next_phase:

      self.craft_window.commit()

  #.......................................................................
  # PHASE_STATUS Handling
  #.......................................................................
  # Phase for displaying details about expedition

  def handle_phase_status( self ):

    # Process inputs

    next_phase = self.status_window.process_inputs(
      self.mouse_x, self.mouse_y, self.mouse_click
    )

    # Go back to menu if ESC pressed

    if self.key_esc:

      self.phase   = PHASE_FREE
      self.menu_en = True
      self.cam_en  = False

    # Reset phase if clicked outside of context

    elif self.mouse_click \
      and not self.status_window.rect.collidepoint( self.mouse_x, self.mouse_y ) \
      and self.camera_window.rect.collidepoint( self.mouse_x, self.mouse_y ):

      self.phase   = PHASE_FREE
      self.menu_en = False
      self.cam_en  = True

    # Go back to menu if okay button is clicked

    elif next_phase:

      self.phase   = PHASE_FREE
      self.menu_en = True
      self.cam_en  = False

  #.......................................................................
  # Update all sprites
  #.......................................................................

  def update_all( self ):

    self.map_group.update( self.cam_x, self.cam_y )
    self.expeditions_group.update( self.cam_x, self.cam_y, self.cam_en )
    self.sidebar_window.update()

    if self.phase == PHASE_EXPLORE0:
      self.survivor_window.update()
    elif self.phase == PHASE_EXPLORE1:
      self.inventory_window.update()
    elif self.phase == PHASE_EXPLORE2:
      self.cost_box.update()
    elif self.phase == PHASE_SCAVENGE0:
      self.survivor_window.update()
    elif self.phase == PHASE_SCAVENGE1:
      self.event_window.update()
    elif self.phase == PHASE_CRAFT:
      self.craft_window.update()
    elif self.phase == PHASE_REST:
      self.survivor_window.update()
    elif self.phase == PHASE_STATUS:
      self.status_window.update()

  #.......................................................................
  # Draw all sprites
  #.......................................................................

  def draw_all( self ):

    # Draw map and associated markers

    rect_updates =  self.map_group.draw( self.camera_window.image )
    rect_updates += self.expeditions_group.draw( self.camera_window.image )

    # Draw menu if enabled

    if self.menu_en:
      rect_updates += self.menu_group.draw( self.camera_window.image )

    # Draw all windows onto main screen

    rect_updates += self.camera_window.draw( self.screen )
    rect_updates += self.sidebar_window.draw( self.screen )

    # Draw phase-specific graphics

    if self.phase == PHASE_EXPLORE0:
      rect_updates += self.survivor_window.draw( self.screen )
    elif self.phase == PHASE_EXPLORE1:
      rect_updates += self.inventory_window.draw( self.screen )
    elif self.phase == PHASE_EXPLORE2:
      rect_updates += self.cost_box.draw( self.screen )
    elif self.phase == PHASE_SCAVENGE0:
      rect_updates += self.survivor_window.draw( self.screen )
    elif self.phase == PHASE_SCAVENGE1:
      rect_updates += self.event_window.draw( self.screen )
    elif self.phase == PHASE_CRAFT:
      rect_updates += self.craft_window.draw( self.screen )
    elif self.phase == PHASE_REST:
      rect_updates += self.survivor_window.draw( self.screen )
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

        elif self.phase == PHASE_EXPLORE0:
          self.handle_phase_explore0()

        elif self.phase == PHASE_EXPLORE1:
          self.handle_phase_explore1()

        elif self.phase == PHASE_EXPLORE2:
          self.handle_phase_explore2()

        elif self.phase == PHASE_EXPLORE3:
          self.handle_phase_explore3()

        elif self.phase == PHASE_SCAVENGE0:
          self.handle_phase_scavenge0()

        elif self.phase == PHASE_SCAVENGE1:
          self.handle_phase_scavenge1()

        elif self.phase == PHASE_CRAFT:
          self.handle_phase_craft()

        elif self.phase == PHASE_REST:
          self.handle_phase_rest()

        elif self.phase == PHASE_STATUS:
          self.handle_phase_status()

      # Update graphics

      self.update_all()
      self.draw_all()

      # Increment clock

      clock.tick( properties.FPS )
