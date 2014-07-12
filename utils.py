#=========================================================================
# utils.py
#=========================================================================
# Miscellaneous utility functions

import pygame, sys, os
from pygame.locals import *

import properties

#-------------------------------------------------------------------------
# Utility Lists
#-------------------------------------------------------------------------

BLACK  = (0,0,0)
WHITE  = (255,255,255)
RED    = (255,0,0)
GREEN  = (0,255,0)
BLUE   = (0,0,255)
PURPLE = (255,0,255)
YELLOW = (255,255,0)

#-------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------

# Create and return surface with text rendered using specified parameters

def gen_text( text, size, color=BLACK, bold=False ):

  # Configure font base

  font = pygame.font.Font( properties.DEFAULT_FONT, size )
  font.set_bold( bold )

  # Create text surface

  return font.render( text, 1, color )

# Above with rect coordinates specified

def gen_text_pos( text, size, pos_x, pos_y, color=BLACK, bold=False ):

  surface      = gen_text( text, size, color, bold )
  rect         = surface.get_rect()
  rect.topleft = pos_x, pos_y

  return surface, rect

# Draw text onto specified surface

def draw_text( dest, text, size, pos_x, pos_y, color=BLACK, bold=False ):

  surface, rect = gen_text_pos( text, size, pos_x, pos_y, color, bold )

  return [ dest.blit( surface, rect ) ]

# Automatically place text in center

def draw_text_center( dest, text, size, color=BLACK, bold=False ):

  pos_x       = dest.get_rect().width / 2
  pos_y       = dest.get_rect().height / 2
  surface     = gen_text( text, size, color, bold )
  rect        = surface.get_rect()
  rect.center = pos_x, pos_y

  return [ dest.blit( surface, rect ) ]
