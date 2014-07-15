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
import button

#-------------------------------------------------------------------------
# Window Offsets
#-------------------------------------------------------------------------

ENEMY_X_OFFSET = 16
ENEMY_Y_OFFSET = 32

PIC_X_OFFSET = 64
PIC_Y_OFFSET = ENEMY_Y_OFFSET + 32 + 16

HIT_X_OFFSET = PIC_X_OFFSET + properties.DEFEND_PIC_WIDTH + 32
HIT_Y_OFFSET = PIC_Y_OFFSET

MSG_X_OFFSET = 16
MSG_Y_OFFSET = PIC_Y_OFFSET + properties.DEFEND_PIC_HEIGHT + 16

BUTTON_X_OFFSET = properties.DEFEND_WIDTH / 2 - properties.MENU_WIDTH / 2
BUTTON_Y_OFFSET = properties.DEFEND_HEIGHT - 16 - properties.MENU_HEIGHT

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
    self.enemy       = None

    # Initialize sub-windows

    self.enemy_tbox = healthtextbox.HealthTextBox(
      properties.DEFEND_WIDTH - 32, 32,
      ENEMY_X_OFFSET, ENEMY_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    self.pic_surface      = pygame.Surface( ( properties.DEFEND_PIC_WIDTH, properties.DEFEND_PIC_HEIGHT ) )
    self.pic_rect         = self.pic_surface.get_rect()
    self.pic_rect.topleft = PIC_X_OFFSET, PIC_Y_OFFSET

    self.hit_surface      = pygame.Surface( ( properties.DEFEND_HIT_WIDTH, properties.DEFEND_HIT_HEIGHT ) )
    self.hit_rect         = self.hit_surface.get_rect()
    self.hit_rect.topleft = HIT_X_OFFSET, HIT_Y_OFFSET

    self.msg_tbox = textbox.TextBox(
      properties.DEFEND_WIDTH - 32, 32,
      MSG_X_OFFSET, MSG_Y_OFFSET, pos_x, pos_y, 14, utils.WHITE
    )

    # Initialize labels for sub-windows

    self.info_label_surface, self.info_label_rect = utils.gen_text_pos(
      'COMBAT', 16, ENEMY_X_OFFSET, properties.TEXT_Y_OFFSET, utils.BLACK, True
    )

    # Initialize button

    self.button_group = pygame.sprite.RenderUpdates()
    self.button_group.add( button.Button( 'OKAY', BUTTON_X_OFFSET, BUTTON_Y_OFFSET ) )

