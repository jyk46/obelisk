#=========================================================================
# defendwindow.py
#=========================================================================
# Extended window class for facilitating combat

import pygame, sys, os
from pygame.locals import *

import properties
import utils
import window
import textbox
import healthtextbox
import defendcard
import button
import attribute

#-------------------------------------------------------------------------
# Window Offsets
#-------------------------------------------------------------------------

ENEMY_X_OFFSET = 16
ENEMY_Y_OFFSET = 32

PIC_X_OFFSET = 64
PIC_Y_OFFSET = ENEMY_Y_OFFSET + 32 + 16

HIT_X_OFFSET = PIC_X_OFFSET + properties.DEFEND_PIC_WIDTH + 32
HIT_Y_OFFSET = PIC_Y_OFFSET + properties.DEFEND_HIT_HEIGHT

LIMIT_X_OFFSET = HIT_X_OFFSET + properties.DEFEND_HIT_WIDTH + 2
LIMIT_Y_OFFSET = HIT_Y_OFFSET - properties.DEFEND_HIT_SPACE

MSG_X_OFFSET = 16
MSG_Y_OFFSET = PIC_Y_OFFSET + properties.DEFEND_PIC_HEIGHT + 16

BUTTON_X_OFFSET = properties.DEFEND_WIDTH / 2 - properties.MENU_WIDTH / 2
BUTTON_Y_OFFSET = properties.DEFEND_HEIGHT - 16 - properties.MENU_HEIGHT

CARD_X_OFFSET = 0
CARD_Y_OFFSET = properties.CAMERA_HEIGHT - properties.CARD_HEIGHT

#-------------------------------------------------------------------------
# Properties
#-------------------------------------------------------------------------

PHASE_START, PHASE_DEFENSE, PHASE_ENEMY, PHASE_PLAYER, PHASE_WIN, PHASE_LOSE = range( 6 )

DAMAGED_TIME = 300
DAMAGE_SPEED = 1
HIT_SPEED    = 0.05
WIN_SPEED    = 8

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class DefendWindow( window.Window ):

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, bg_path ):

    window.Window.__init__( self, width, height, pos_x, pos_y, bg_path )

    # Member variables

    self._expedition = None
    self.survivors   = []
    self.defenses    = []
    self._tile       = None
    self._enemy      = None
    self.turn_order  = []
    self.turn_idx    = 0
    self.phase       = PHASE_START
    self.cards       = []

    self.do_draw          = True
    self.animation_active = False
    self.timer            = 0
    self.step_count       = 0

    # Phase variables

    self.target_survivor = None
    self.target_dmg      = 0
    self.target_stamina  = 0
    self.target_card     = None

    self.hit_active      = False
    self.hit_bar_ratio   = 0.00
    self.hit_bar_speed   = HIT_SPEED
    self.hit_bar_limit   = 0.00

    self.enemy_damaged   = False
    self.no_ammo         = False
    self.no_stamina      = False
    self.curse_stamina   = 0

    self.defense_dmg     = 0.0
    self.defense_spawn   = 1.0
    self.defense_stun    = 0
    self.defense_armor   = 0

    # Initialize sub-windows

    self.enemy_tbox = healthtextbox.HealthTextBox(
      properties.DEFEND_WIDTH - 32, 32,
      ENEMY_X_OFFSET, ENEMY_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    self.pic_surface      = pygame.Surface( ( properties.DEFEND_PIC_WIDTH, properties.DEFEND_PIC_HEIGHT ) )
    self.pic_rect         = self.pic_surface.get_rect()
    self.pic_rect.topleft = PIC_X_OFFSET, PIC_Y_OFFSET

    self.hit_surface         = pygame.Surface( ( properties.DEFEND_HIT_WIDTH, properties.DEFEND_HIT_HEIGHT ) )
    self.hit_rect            = self.hit_surface.get_rect()
    self.hit_rect.bottomleft = HIT_X_OFFSET, HIT_Y_OFFSET

    self.hit_bar_surface         = pygame.Surface( ( properties.DEFEND_HIT_WIDTH - 2 * properties.DEFEND_HIT_SPACE,
                                                     properties.DEFEND_HIT_HEIGHT - 2 * properties.DEFEND_HIT_SPACE ) )
    self.hit_bar_rect            = self.hit_bar_surface.get_rect()
    self.hit_bar_rect.bottomleft = HIT_X_OFFSET + properties.DEFEND_HIT_SPACE, HIT_Y_OFFSET - properties.DEFEND_HIT_SPACE

    self.hit_og_surface          = pygame.Surface( ( properties.DEFEND_HIT_WIDTH - 2 * properties.DEFEND_HIT_SPACE,
                                                     properties.DEFEND_HIT_HEIGHT - 2 * properties.DEFEND_HIT_SPACE ) )
    self.hit_og_surface.fill( utils.RED )

    self.hit_limit_surface      = pygame.Surface( ( properties.DEFEND_HIT_WIDTH, 3 ) )
    self.hit_limit_rect         = self.hit_limit_surface.get_rect()
    self.hit_limit_rect.left    = HIT_X_OFFSET
    self.hit_limit_rect.centery = LIMIT_Y_OFFSET
    self.hit_limit_surface.fill( utils.RED )

    self.hit_text_surface, self.hit_text_rect = utils.gen_text_pos(
      'HIT', 14, LIMIT_X_OFFSET, LIMIT_Y_OFFSET, utils.RED, True
    )

    self.msg_tbox = textbox.TextBox(
      properties.DEFEND_WIDTH - 32, 32,
      MSG_X_OFFSET, MSG_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    # Initialize labels for sub-windows

    self.defend_label_surface, self.defend_label_rect = utils.gen_text_pos(
      'COMBAT', 16, ENEMY_X_OFFSET, properties.TEXT_Y_OFFSET, utils.BLACK, True
    )

    # Initialize button

    self.button_group = pygame.sprite.RenderUpdates()
    self.button_group.add( button.Button( 'OKAY', BUTTON_X_OFFSET, BUTTON_Y_OFFSET ) )

  # Check if all survivors are dead

  def check_dead( self ):

    for _survivor in self.survivors:
      if _survivor.stamina > 0:
        return False

    return True

  # Determine turn order based on speed

  def calc_turn_order( self ):

    assert( len( self.survivors ) > 0 )
    assert( self._enemy != None )

    self.turn_order = self.survivors + [ self._enemy ]

    # Sort both enemy and survivors in order of decreasing speed

    self.turn_order = sorted(
      self.turn_order, key=lambda unit: unit.get_speed(), reverse=True
    )

  # Increment turn index to the next living unit

  def increment_turn( self ):

    self.turn_idx += 1
    if self.turn_idx == len( self.turn_order ):
      self.turn_idx = 0

    while self.turn_order[self.turn_idx].stamina == 0:
      self.turn_idx += 1
      if self.turn_idx == len( self.turn_order ):
        self.turn_idx = 0

  # Set target survivor card

  def set_target_card( self ):

    for card in self.cards:
      if card._survivor == self.target_survivor:
        self.target_card = card
        break

  # Scale hit bar to specified ratio

  def scale_hit_bar( self ):

    self.hit_bar_surface = pygame.transform.scale(
      self.hit_og_surface,
      ( properties.DEFEND_HIT_WIDTH - 2 * properties.DEFEND_HIT_SPACE,
        int( self.hit_bar_ratio * ( properties.DEFEND_HIT_HEIGHT - 2 * properties.DEFEND_HIT_SPACE ) ) )
    )

    self.hit_bar_rect            = self.hit_bar_surface.get_rect()
    self.hit_bar_rect.bottomleft = HIT_X_OFFSET + properties.DEFEND_HIT_SPACE, HIT_Y_OFFSET - properties.DEFEND_HIT_SPACE

    red   = 255 * ( 1.00 - max( ( self.hit_bar_ratio - 0.6 ) / 0.6, 0.0 ) )
    green = 255 * min( self.hit_bar_ratio / 0.8, 1.0 )

    self.hit_bar_surface.fill( ( red, green, 0 ) )

  # Oscillate hit bar for player attack

  def increment_hit_bar( self ):

    if self.hit_bar_ratio == 1.00:
      self.hit_bar_ratio = 0.00

    else:

      self.hit_bar_ratio += self.hit_bar_speed

      if self.hit_bar_ratio > 1.00:
        self.hit_bar_ratio = 1.00

  # Adjust position of hit limit indicator

  def set_hit_bar_limit( self, limit ):

    # Mental bonus of survivor wielding weapon lowers limit

    self.hit_bar_limit = limit - ( self.target_survivor.get_mental_bonus() * 0.02 )

    self.hit_limit_rect.centery = LIMIT_Y_OFFSET \
      - int( limit * ( properties.DEFEND_HIT_HEIGHT - 2 * properties.DEFEND_HIT_SPACE ) )

    self.hit_text_rect.top = self.hit_limit_rect.centery

  # Initialize with new enemy and turn order for a new encounter

  def init( self ):

    # Reset to start phase

    self.phase    = PHASE_START
    self.do_draw  = True
    self.turn_idx = 0

    # Register defenses

    self.defense_dmg   = 0.0
    self.defense_spawn = 1.0
    self.defense_stun  = 0
    self.defense_armor = 0

    for defense in self.defenses:

      if defense.name == 'Pit Trap':
        self.defense_dmg += 0.25

      elif defense.name == 'Spike Trap':
        self.defense_dmg += 0.50

      elif defense.name == 'Explosive Trap':
        self.defense_dmg += 0.75

      elif defense.name == 'Camouflage':
        self.defense_spawn = min( 0.5, self.defense_spawn )

      elif defense.name == 'Bone Ward':
        self.defense_spawn = min( 0.01, self.defense_spawn )

      elif defense.name == 'Flashbang':
        self.defense_stun += 1

      elif ( defense.name == 'Barricade' ) or ( defense.name == 'Barbed Fence' ):
        self.defense_armor = defense.armor

    # Roll for enemy and determine turn order if valid enemy

    self._enemy = self._tile.roll_enemy( self.defense_spawn )

    if self._enemy != None:
      self.calc_turn_order()
      self.pic_enemy_surface = pygame.image.load( self._enemy.img_path )
      self.hit_bar_speed     = HIT_SPEED + ( self._enemy.speed * 0.02 )
    else:
      self.pic_enemy_surface = pygame.Surface( ( 1, 1 ) )

    # Initialize images for this encounter

    self.pic_bg_surface    = pygame.image.load( self._tile.bg_path )
    self.pic_bg_rect       = self.pic_bg_surface.get_rect( topleft = ( 0, 0 ) )

    self.pic_enemy_surface.set_colorkey( self.pic_enemy_surface.get_at( ( 0, 0 ) ), RLEACCEL )
    self.pic_enemy_rect    = self.pic_enemy_surface.get_rect( center = self.pic_bg_rect.center )

    self.hit_bar_ratio     = 0.00
    self.scale_hit_bar()

    # Initialize defender cards

    self.cards = []

    x_offset = CARD_X_OFFSET

    for _survivor in self.survivors:
      self.cards.append( defendcard.DefendCard( self._expedition, _survivor, x_offset, CARD_Y_OFFSET ) )
      x_offset += properties.CARD_WIDTH

  # Commit dead survivors and used up defenses

  def commit( self ):

    # Handle dead survivors

    survivors = []

    for _survivor in self._expedition.survivors:
      if _survivor.stamina > 0:
        survivors.append( _survivor )

    self._expedition.survivors = survivors

    # Handle used up defenses

    for defense in self.defenses:
      self._expedition._inventory.items.remove( defense )

  # Reset to clean slate

  def reset( self ):

    self._expedition = None
    self.survivors   = []
    self.defenses    = []
    self._tile       = None
    self._enemy      = None
    self.turn_order  = []
    self.turn_idx    = 0
    self.phase       = PHASE_START
    self.cards       = []

  # Process inputs

  def process_inputs( self, mouse_x, mouse_y, mouse_click ):

    # Adjust button coordinates to absolute scale

    rect = self.button_group.sprites()[0].rect.move( self.rect.left, self.rect.top )

    # Button click effect changes with phase

    if mouse_click and rect.collidepoint( mouse_x, mouse_y ):

      #...................................................................
      # Start phase
      #...................................................................

      if self.phase == PHASE_START:

        # If no enemy spawned, exit phase

        if self._enemy == None:
          return True

        # If traps set, trigger them

        if self.defense_dmg > 0.0:

          self.phase            = PHASE_DEFENSE
          self.do_draw          = True

          self.target_dmg       = int( self.defense_dmg * self._enemy.max_stamina )
          self.target_stamina   = max( self._enemy.stamina - self.target_dmg, 0 )
          self.enemy_damaged    = True
          self.animation_active = True
          self.timer            = pygame.time.get_ticks()

        # First turn to enemy

        elif self.turn_order[self.turn_idx] == self._enemy:

          self.phase           = PHASE_ENEMY
          self.do_draw         = True

          attack_info              = self._enemy.attack( self.survivors )
          self.target_survivor     = attack_info[0]
          self.target_dmg          = max( attack_info[1] - self.defense_armor, 0 )
          self.target_stamina      = max( self.target_survivor.stamina - self.target_dmg, 0 )
          self.set_target_card()

          # No animation for 0 damage

          if self.target_dmg == 0:

            self.animation_active = False
            self.increment_turn()

            self.msg_tbox.update( [[
              self._enemy.name + ' did no damage!'
            ]] )

          # Enemy is stunned

          elif self.defense_stun > 0:

            self.target_stamina   = self.target_survivor.stamina
            self.animation_active = False
            self.increment_turn()

          # Otherwise show damage animation

          else:

            self.target_card.damaged = True
            self.animation_active    = True
            self.timer               = pygame.time.get_ticks()

        # First turn to survivor

        else:

          self.phase           = PHASE_PLAYER
          self.do_draw         = True
          self.target_survivor = self.turn_order[self.turn_idx]
          self.set_target_card()
          self.target_card.activate()
          self.hit_active      = True
          self.hit_bar_ratio   = 0.00
          self.set_hit_bar_limit( self.target_survivor.weapon.difficulty )

      #...................................................................
      # Defense phase
      #...................................................................

      elif self.phase == PHASE_DEFENSE:

        # Wait for animation to finish

        if not self.animation_active:

          # Check if enemy is dead

          if self._enemy.stamina == 0:

            self.phase            = PHASE_WIN
            self.do_draw          = True
            self.animation_active = True

          # Otherwise move onto the next unit's turn

          elif self.turn_order[self.turn_idx] == self._enemy:

            self.phase           = PHASE_ENEMY
            self.do_draw         = True

            attack_info              = self._enemy.attack( self.survivors )
            self.target_survivor     = attack_info[0]
            self.target_dmg          = max( attack_info[1] - self.defense_armor, 0 )
            self.target_stamina      = max( self.target_survivor.stamina - self.target_dmg, 0 )
            self.set_target_card()

            # No animation for 0 damage

            if self.target_dmg == 0:

              self.animation_active = False
              self.increment_turn()

              self.msg_tbox.update( [[
                self._enemy.name + ' did no damage!'
              ]] )

            # Enemy is stunned

            elif self.defense_stun > 0:

              self.target_stamina   = self.target_survivor.stamina
              self.animation_active = False
              self.increment_turn()

            # Otherwise show damage animation

            else:

              self.target_card.damaged = True
              self.animation_active    = True
              self.timer               = pygame.time.get_ticks()
              self.hit_bar_ratio       = 0.00
              self.scale_hit_bar()

          else:

            self.phase           = PHASE_PLAYER
            self.do_draw         = True
            self.target_survivor = self.turn_order[self.turn_idx]
            self.set_target_card()
            self.target_card.activate()
            self.hit_active      = True
            self.hit_bar_ratio   = 0.00
            self.set_hit_bar_limit( self.target_survivor.weapon.difficulty )

      #...................................................................
      # Enemy phase
      #...................................................................

      elif self.phase == PHASE_ENEMY:

        # Wait for animation to finish

        if not self.animation_active:

          # All defenders are dead, end phase

          if self.check_dead():

            self.phase   = PHASE_LOSE
            self.do_draw = True

          # Otherwise move onto the next unit's turn

          else:

            self.phase           = PHASE_PLAYER
            self.do_draw         = True
            self.target_survivor = self.turn_order[self.turn_idx]
            self.set_target_card()
            self.target_card.activate()
            self.hit_active      = True
            self.hit_bar_ratio   = 0.00
            self.set_hit_bar_limit( self.target_survivor.weapon.difficulty )

      #...................................................................
      # Player phase
      #...................................................................

      elif self.phase == PHASE_PLAYER:

        # Handle hit bar detection

        if self.hit_active:

          self.hit_active = False
          self.do_draw    = True

          # If attacker is military, then halve the ammo cost

          ammo_cost = self.target_survivor.weapon.ammo_cost

          if self.target_survivor.job == attribute.SOLDIER:
            ammo_cost = max( int( ammo_cost * 0.5 ), 1 )

          # Consume ammo if using a gun

          self.no_ammo = False

          if self._expedition._inventory.ammo < ammo_cost:
            self.no_ammo = True

          elif ammo_cost > 0:
            self._expedition._inventory.ammo -= ammo_cost

          # If attacker is mystic, then halve the stamina cost

          stamina_cost = self.target_survivor.weapon.stam_cost

          if self.target_survivor.job == attribute.MYSTIC:
            stamina_cost = max( int( stamina_cost * 0.5 ), 1 )

          # Consume stamina if using cursed weapon

          self.no_stamina    = False
          self.curse_stamina = self.target_survivor.stamina

          if self.target_survivor.stamina <= stamina_cost:
            self.no_stamina = True

          elif stamina_cost > 0:
            self.curse_stamina -= stamina_cost

          # Direct hit to enemy

          if self.hit_bar_ratio >= self.hit_bar_limit:

            critical = False
            if self.hit_bar_ratio == 1.00:
              critical = True

            self.target_dmg     = self.target_survivor.attack( self._enemy, critical, self.no_ammo or self.no_stamina )
            self.target_stamina = max( self._enemy.stamina - self.target_dmg, 0 )

            # No animation for 0 damage

            if self.target_dmg == 0:

              self.curse_stamina    = self.target_survivor.stamina
              self.animation_active = False
              self.increment_turn()

              text = self.target_survivor.name.split()[0] + ' did no damage!'

              if self.no_ammo:
                text = 'No ammo! ' + text
              elif self.no_stamina:
                text = 'Ugh... ' + text

              self.msg_tbox.update( [[ text ]] )

            # Otherwise show damage animation

            else:

              self.enemy_damaged    = True
              self.animation_active = True
              self.timer            = pygame.time.get_ticks()

          # Missed the enemy

          else:

            self.target_stamina   = self._enemy.stamina
            self.curse_stamina    = self.target_survivor.stamina
            self.animation_active = False
            self.increment_turn()

            self.msg_tbox.update( [[
              self.target_survivor.name.split()[0] + ' misses!'
            ]] )

        # Wait for animation to finish

        elif not self.animation_active:

          self.target_card.deactivate()

          # Check if enemy is dead

          if self._enemy.stamina == 0:

            self.phase            = PHASE_WIN
            self.do_draw          = True
            self.animation_active = True

          # Otherwise move onto the next unit's turn

          elif self.turn_order[self.turn_idx] == self._enemy:

            self.phase           = PHASE_ENEMY
            self.do_draw         = True

            attack_info              = self._enemy.attack( self.survivors )
            self.target_survivor     = attack_info[0]
            self.target_dmg          = max( attack_info[1] - self.defense_armor, 0 )
            self.target_stamina      = max( self.target_survivor.stamina - self.target_dmg, 0 )
            self.set_target_card()

            # No animation for 0 damage

            if self.target_dmg == 0:

              self.animation_active = False
              self.increment_turn()

              self.msg_tbox.update( [[
                self._enemy.name + ' did no damage!'
              ]] )

            # Enemy is stunned

            elif self.defense_stun > 0:

              self.target_stamina   = self.target_survivor.stamina
              self.animation_active = False
              self.increment_turn()

            # Otherwise show damage animation

            else:

              self.target_card.damaged = True
              self.animation_active    = True
              self.timer               = pygame.time.get_ticks()
              self.hit_bar_ratio       = 0.00
              self.scale_hit_bar()

          else:

            self.phase           = PHASE_PLAYER
            self.do_draw         = True
            self.target_survivor = self.turn_order[self.turn_idx]
            self.set_target_card()
            self.target_card.activate()
            self.hit_active      = True
            self.hit_bar_ratio   = 0.00
            self.set_hit_bar_limit( self.target_survivor.weapon.difficulty )

      #...................................................................
      # Done phases
      #...................................................................

      elif ( self.phase == PHASE_WIN ) or ( self.phase == PHASE_LOSE ):

        # Complete defend phase when animation is done

        if not self.animation_active:
          self.commit()
          return True

    return False

  # Update graphics

  def update( self ):

    # Start phase

    if self.phase == PHASE_START:

      if self._enemy == None:
        enemy_text   = [[ '' ]]
        enemy_health = [[ 0.0 ]]
        msg_text     = [[ 'The night passes peacefully...' ]]
      else:
        enemy_text   = [[ self._enemy.name ]]
        enemy_health = [[ 1.0 ]]
        msg_text     = [[ self._enemy.name + ' appears!' ]]

      self.enemy_tbox.update( enemy_text, enemy_health )
      self.msg_tbox.update( msg_text )

    # Defense phase

    elif self.phase == PHASE_DEFENSE:

      self.msg_tbox.update( [[
        'Traps deal ' + str( self.target_dmg ) + ' damage!'
      ]] )

      # Show red background for damaged enemy

      if self.enemy_damaged:

        timestamp = pygame.time.get_ticks()

        if ( timestamp - self.timer ) >= DAMAGED_TIME:
          self.do_draw       = True
          self.enemy_damaged = False
          self.step_count    = 0

      # Rolling stamina damage animation

      elif self._enemy.stamina > self.target_stamina:

        self.do_draw = True

        if self.step_count == 0:
          self._enemy.stamina -= 1

        self.step_count += 1

        if self.step_count == DAMAGE_SPEED:
          self.step_count = 0

        # Mark animation as done and update turn order

        if self._enemy.stamina == self.target_stamina:
          self.animation_active = False

        self.enemy_tbox.update( [[ self._enemy.name ]], [[ float( self._enemy.stamina ) / self._enemy.max_stamina ]] )

    # Enemy phase

    elif self.phase == PHASE_ENEMY:

      if self.defense_stun > 0:

        self.defense_stun -= 1

        self.msg_tbox.update( [[ self._enemy.name + ' is stunned!' ]] )

      else:

        self.msg_tbox.update( [[
          self._enemy.name + ' deals ' + str( self.target_dmg ) + ' damage!'
        ]] )

      # Show red background for damaged defender card

      if self.target_card.damaged:

        timestamp = pygame.time.get_ticks()

        if ( timestamp - self.timer ) >= DAMAGED_TIME:
          self.do_draw             = True
          self.target_card.damaged = False
          self.step_count          = 0

      # Rolling stamina damage animation

      elif ( self.target_survivor.stamina > self.target_stamina ):

        self.do_draw = True

        if self.step_count == 0:
          self.target_survivor.stamina -= 1

        self.step_count += 1

        if self.step_count == DAMAGE_SPEED:
          self.step_count = 0

        # Mark animation as done and update turn order

        if self.target_survivor.stamina == self.target_stamina:

          self.animation_active = False
          self.increment_turn()

    # Player phase

    elif self.phase == PHASE_PLAYER:

      # Handle hit bar detection

      if self.hit_active:

        self.do_draw = True

        self.msg_tbox.update( [[
          self.target_survivor.name.split()[0] + '\'s turn to attack!'
        ]] )

        self.increment_hit_bar()
        self.scale_hit_bar()

      # Handle player attack animation

      elif self.enemy_damaged:

        text = self.target_survivor.name.split()[0] + ' deals ' + str( self.target_dmg ) + ' damage!'

        if self.no_ammo:
          text = 'No ammo! ' + text
        elif self.no_stamina:
          text = 'Ugh... ' + text
        elif self.target_survivor.stamina > self.curse_stamina:
          text += ' CURSED!'

        self.msg_tbox.update( [[ text ]] )

        # Show red background for damaged enemy

        timestamp = pygame.time.get_ticks()

        if ( timestamp - self.timer ) >= DAMAGED_TIME:
          self.do_draw       = True
          self.enemy_damaged = False
          self.step_count    = 0

      # Rolling stamina damage animation

      elif self._enemy.stamina > self.target_stamina:

        self.do_draw = True

        if self.step_count == 0:
          self._enemy.stamina -= 1

        self.step_count += 1

        if self.step_count == DAMAGE_SPEED:
          self.step_count = 0

        # Mark animation as done and update turn order

        if ( self._enemy.stamina == self.target_stamina ) \
          and ( self.target_survivor.stamina == self.curse_stamina ):

          self.animation_active = False
          self.increment_turn()

        self.enemy_tbox.update( [[ self._enemy.name ]], [[ float( self._enemy.stamina ) / self._enemy.max_stamina ]] )

      # Animate curse damage

      elif self.target_survivor.stamina > self.curse_stamina:

        self.do_draw = True

        if self.step_count == 0:
          self.target_survivor.stamina -= 1

        self.step_count += 1

        if self.step_count == DAMAGE_SPEED:
          self.step_count = 0

        # Mark animation as done and update turn order

        if self.target_survivor.stamina == self.curse_stamina:

          self.animation_active = False
          self.increment_turn()

    # Win phase

    elif self.phase == PHASE_WIN:

      self.msg_tbox.update( [[
        self._enemy.name + ' was defeated!'
      ]] )

      if self.pic_enemy_rect.top < properties.DEFEND_PIC_HEIGHT:

        self.do_draw = True

        self.pic_enemy_rect.top += WIN_SPEED

        # Mark animation as done

        if self.pic_enemy_rect.top >= properties.DEFEND_PIC_HEIGHT:
          self.animation_active = False

    # Lose phase

    elif self.phase == PHASE_LOSE:

      self.msg_tbox.update( [[
        'Defenders were annihilated!'
      ]] )

    # Always update defender cards

    for card in self.cards:
      card.update()

  # Draw information onto window

  def draw_info( self ):

    # Draw text boxes

    rect_updates  = self.enemy_tbox.draw( self.image )
    rect_updates += self.msg_tbox.draw( self.image )

    # Draw enemy picture

    rect_updates += [ self.pic_surface.blit( self.pic_bg_surface, self.pic_bg_rect ) ]

    if self.enemy_damaged:
      self.pic_surface.fill( utils.RED )

    if self._enemy != None:
      rect_updates += [ self.pic_surface.blit( self.pic_enemy_surface, self.pic_enemy_rect ) ]

    rect_updates += [ self.image.blit( self.pic_surface, self.pic_rect ) ]

    # Draw hit bar

    rect_updates += [ self.image.blit( self.hit_surface, self.hit_rect ) ]
    rect_updates += [ self.image.blit( self.hit_bar_surface, self.hit_bar_rect ) ]

    if ( self.phase == PHASE_PLAYER ):
      rect_updates += [ self.image.blit( self.hit_limit_surface, self.hit_limit_rect ) ]
      rect_updates += [ self.image.blit( self.hit_text_surface, self.hit_text_rect ) ]

    # Draw labels

    rect_updates += [ self.image.blit( self.defend_label_surface, self.defend_label_rect ) ]

    # Draw button

    rect_updates += self.button_group.draw( self.image )

    return rect_updates

  # Overloaded aggregate draw function

  def draw( self, surface ):

    rect_updates = []

    if self.do_draw:

      rect_updates += self.draw_background()
      rect_updates += self.draw_info()

      self.do_draw = False

    for card in self.cards:
      card.draw( surface )

    rect_updates += window.Window.draw( self, surface )

    return rect_updates
