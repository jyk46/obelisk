#=========================================================================
# textbox.py
#=========================================================================
# Generic text box image for displaying information

import pygame, sys, os
from pygame.locals import *

import properties
import utils

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class TextBox:

  # Constructor

  def __init__( self, width, height, pos_x, pos_y, offset_x, offset_y, size, color ):

    # Initialize surface

    self.image        = pygame.Surface( ( width, height ) )
    self.rect         = self.image.get_rect()
    self.rect.topleft = pos_x, pos_y

    self.offset_x     = offset_x
    self.offset_y     = offset_y

    # Initialize scroll area rects

    self.surface_matrix  = []
    self.rect_matrix     = []

    self.scroll_y        = 0
    self.max_scroll_y    = 0

    self.scroll_up = pygame.rect.Rect(
      offset_x + self.rect.left,
      offset_y + self.rect.top,
      self.rect.width, properties.SCROLL_HEIGHT
    )

    self.scroll_down = pygame.rect.Rect(
      offset_x + self.rect.left,
      offset_y + self.rect.bottom - properties.SCROLL_HEIGHT,
      self.rect.width, properties.SCROLL_HEIGHT
    )

    # Store font parameters

    self.size  = size
    self.color = color

  # Scroll text if mouse is over scroll area

  def scroll_text( self, mouse_x, mouse_y ):

    if self.scroll_up.collidepoint( mouse_x, mouse_y ) \
      and ( self.scroll_y > 0 ):
      self.scroll_y -= properties.SCROLL_SPEED

    elif self.scroll_down.collidepoint( mouse_x, mouse_y ) \
      and ( ( self.scroll_y + self.rect.height ) < self.max_scroll_y ):
      self.scroll_y += properties.SCROLL_SPEED

  # Set text to display: text must be provided as a 2D array where the
  # first dimension specifies the column and the second dimension
  # specifies the vertical text within the column.
  #
  # [
  #   [               [               [               [
  #     'COL0_LINE0',   'COL1_LINE0',   'COL2_LINE0',   'COL3_LINE0',
  #     'COL0_LINE1',   'COL1_LINE1',   'COL2_LINE1',   'COL3_LINE1',
  #     'COL0_LINE2',   'COL1_LINE2',   'COL2_LINE2',   'COL3_LINE2',
  #     'COL0_LINE3',   'COL1_LINE3',   'COL2_LINE3',   'COL3_LINE3',
  #   ],              ],              ],              ],
  # ]
  #
  # Text to be bolded can be specified using the ** marker.

  def update( self, text_matrix=[['']] ):

    # Reset background

    self.image.fill( utils.BLACK )

    # Calculate column offsets

    col_offset = self.rect.width / len( text_matrix )

    # Iterate through text columns

    self.surface_matrix = []
    self.rect_matrix    = []
    col_idx             = 0

    for i, text_col in enumerate( text_matrix ):

      # Determine maximum number of rows in any column

      num_rows = len( text_col )

      if i == 0:
        self.max_scroll_y = num_rows
      elif num_rows > self.max_scroll_y:
        self.max_scroll_y = num_rows

      # Convert number of rows to pixels

      self.max_scroll_y *= properties.TEXT_HEIGHT

      # Draw all text for current column

      surface_col = []
      rect_col    = []
      row_idx     = 0

      for text in text_col:

        # Check if text should be bolded

        bold = False

        if '**' in text:
          bold = True
          text = text.replace( '**', '' )

        # Draw text

        surface, rect = utils.gen_text_pos(
          text, self.size,
          ( col_offset * col_idx ) + properties.TEXT_X_OFFSET,
          ( properties.TEXT_HEIGHT * row_idx ) + properties.TEXT_Y_OFFSET - self.scroll_y,
          self.color, bold
        )

        # Add text surface to column array

        surface_col.append( ( surface, rect ) )

        # Adjust text rects to absolute scale for processing inputs

        rect_col.append( rect.move( self.offset_x + self.rect.left, self.offset_y + self.rect.top ) )

        # Increment row index

        row_idx += 1

      # Add text surface to matrix array

      self.surface_matrix.append( surface_col )

      # Add detection rect to matrix array

      self.rect_matrix.append( rect_col )

      # Increment column index

      col_idx += 1

  # Draw text

  def draw_text( self ):

    rect_updates = []

    for surface_col in self.surface_matrix:
      for surface, rect in surface_col:
        rect_updates += [ self.image.blit( surface, rect ) ]

    return rect_updates

  # Draw graphics

  def draw( self, surface ):

    rect_updates  = self.draw_text()
    rect_updates += [ surface.blit( self.image, self.rect ) ]

    return rect_updates
