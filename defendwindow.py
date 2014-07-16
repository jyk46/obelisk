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

#-------------------------------------------------------------------------
# Window Offsets
#-------------------------------------------------------------------------

ENEMY_X_OFFSET = 16
ENEMY_Y_OFFSET = 32

PIC_X_OFFSET = 64
PIC_Y_OFFSET = ENEMY_Y_OFFSET + 32 + 16

HIT_X_OFFSET = PIC_X_OFFSET + properties.DEFEND_PIC_WIDTH + 32
HIT_Y_OFFSET = PIC_Y_OFFSET + properties.DEFEND_HIT_HEIGHT

MSG_X_OFFSET = 16
MSG_Y_OFFSET = PIC_Y_OFFSET + properties.DEFEND_PIC_HEIGHT + 16

BUTTON_X_OFFSET = properties.DEFEND_WIDTH / 2 - properties.MENU_WIDTH / 2
BUTTON_Y_OFFSET = properties.DEFEND_HEIGHT - 16 - properties.MENU_HEIGHT

CARD_X_OFFSET = 0
CARD_Y_OFFSET = properties.CAMERA_HEIGHT - properties.CARD_HEIGHT

#-------------------------------------------------------------------------
# Properties
#-------------------------------------------------------------------------

PHASE_START, PHASE_DEFENSE, PHASE_ENEMY, PHASE_PLAYER0, \
PHASE_PLAYER1, PHASE_DONE = range( 6 )

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
    self.hit_bar_surface.fill( utils.RED )

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

  # Determine turn order based on speed

  def calc_turn_order( self ):

    assert( len( self.survivors ) > 0 )
    assert( self._enemy != None )

    self.turn_order = self.survivors + [ self._enemy ]

    # Sort both enemy and survivors in order of decreasing speed

    self.turn_order = sorted(
      self.turn_order, key=lambda unit: unit.get_speed(), reverse=True
    )

  # Scale hit bar to specified ratio

  def scale_hit_bar( self, ratio ):

    self.hit_bar_surface = pygame.transform.scale(
      self.hit_bar_surface,
      ( properties.DEFEND_HIT_WIDTH - 2 * properties.DEFEND_HIT_SPACE,
        int( ratio * ( properties.DEFEND_HIT_HEIGHT - 2 * properties.DEFEND_HIT_SPACE ) ) )
    )

    self.hit_bar_rect            = self.hit_bar_surface.get_rect()
    self.hit_bar_rect.bottomleft = HIT_X_OFFSET + properties.DEFEND_HIT_SPACE, HIT_Y_OFFSET - properties.DEFEND_HIT_SPACE

  # Initialize with new enemy and turn order for a new encounter

  def init( self ):

    # Reset to start phase

    self.phase = PHASE_START

    # Roll for enemy and determine turn order if valid enemy

    self._enemy = self._tile.roll_enemy()

    if self._enemy != None:
      self.calc_turn_order()
      self.pic_enemy_surface = pygame.image.load( self._enemy.img_path )
    else:
      self.pic_enemy_surface = pygame.Surface( ( 1, 1 ) )

    # Initialize images for this encounter

    self.pic_bg_surface    = pygame.image.load( self._tile.bg_path )
    self.pic_bg_rect       = self.pic_bg_surface.get_rect( topleft = ( 0, 0 ) )

    self.pic_enemy_surface.set_colorkey( self.pic_enemy_surface.get_at( ( 0, 0 ) ), RLEACCEL )
    self.pic_enemy_rect    = self.pic_enemy_surface.get_rect( center = self.pic_bg_rect.center )

    self.scale_hit_bar( 1.0 )

    # Initialize defender cards

    self.cards = []

    x_offset = CARD_X_OFFSET

    for _survivor in self.survivors:
      self.cards.append( defendcard.DefendCard( _survivor, x_offset, CARD_Y_OFFSET ) )
      x_offset += properties.CARD_WIDTH

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

      # Start phase

      if self.phase == PHASE_START:

        if self.turn_order[self.turn_idx] == self._enemy:
          self.phase = PHASE_ENEMY

        else:
          self.phase = PHASE_PLAYER0

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
        msg_text     = [[ self._enemy.name + ' attacks the survivors!' ]]

      self.enemy_tbox.update( enemy_text, enemy_health )
      self.msg_tbox.update( msg_text )

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
    rect_updates += [ self.pic_surface.blit( self.pic_enemy_surface, self.pic_enemy_rect ) ]
    rect_updates += [ self.image.blit( self.pic_surface, self.pic_rect ) ]

    # Draw hit bar

    rect_updates += [ self.image.blit( self.hit_surface, self.hit_rect ) ]
    rect_updates += [ self.image.blit( self.hit_bar_surface, self.hit_bar_rect ) ]

    # Draw labels

    rect_updates += [ self.image.blit( self.defend_label_surface, self.defend_label_rect ) ]

    # Draw button

    rect_updates += self.button_group.draw( self.image )

    return rect_updates

  # Overloaded aggregate draw function

  def draw( self, surface ):

    rect_updates  = self.draw_background()
    rect_updates += self.draw_info()

    for card in self.cards:
      card.draw( surface )

    rect_updates += window.Window.draw( self, surface )

    return rect_updates
