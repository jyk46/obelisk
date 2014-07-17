#=========================================================================
# defendtest.py
#=========================================================================
# Standalone unit tester for defend phase of game

import pygame, sys, os
from pygame.locals import *

import properties
import utils
import defendwindow
import tile
import survivor
import inventory
import item
import expedition

#-------------------------------------------------------------------------
# Utility functions
#-------------------------------------------------------------------------

def get_inputs( mouse_x, mouse_y ):

  mouse_click = False

  for event in pygame.event.get():

    if event.type == MOUSEMOTION:
      mouse_x = event.pos[0]
      mouse_y = event.pos[1]

    elif event.type == MOUSEBUTTONDOWN:
      mouse_click = True

  return mouse_x, mouse_y, mouse_click

#-------------------------------------------------------------------------
# Main Function
#-------------------------------------------------------------------------

def main():

  # Initialize pygame

  pygame.init()

  # Configure display

  pygame.display.set_mode( ( properties.WINDOW_WIDTH, properties.WINDOW_HEIGHT ) )

  screen = pygame.display.get_surface()

  # Initialize defend window

  defend_window = defendwindow.DefendWindow(
    properties.DEFEND_WIDTH, properties.DEFEND_HEIGHT,
    128, 64, properties.DEFEND_PATH + 'defend_bg.png'
  )

  # Set up dummy map

  map = []

  for i in range( properties.MAP_SIZE ):

    map.append( [] )

    for j in range( properties.MAP_SIZE ):
      map[i].append( tile.Tile( 'Field', i, j ) )

  # Set up sample expedition

  expeditions_group            = pygame.sprite.RenderUpdates()
  expedition.Expedition.groups = expeditions_group

  survivors = []
  for i in range( 4 ):
    survivors.append( survivor.Survivor() )

  survivors[0].weapon = item.Item( 'Knife' )
  survivors[1].weapon = item.Item( 'Rifle' )
  survivors[3].weapon = item.Item( 'Flame Thrower' )

  _tile       = tile.Tile( 'Field', 0, 0 )
  _inventory  = inventory.Inventory( 10, 10, 10, 10 )
  _expedition = expedition.Expedition( _tile, survivors, _inventory, map )

  defend_window._expedition = _expedition
  defend_window.survivors   = _expedition.survivors
  defend_window.defenses    = _inventory.items
  defend_window._tile       = _tile

  # Start defend phase

  defend_window.init()

  # Initialize clock

  clock = pygame.time.Clock()

  # Main loop

  done = False

  mouse_x = 0
  mouse_y = 0

  while not done:

    mouse_x, mouse_y, mouse_click = get_inputs( mouse_x, mouse_y )

    done = defend_window.process_inputs(
      mouse_x, mouse_y, mouse_click
    )

    defend_window.update()

    screen.fill( utils.BLACK )
    defend_window.draw( screen )

    pygame.display.update()

    clock.tick( properties.FPS )

# Execute main function

if __name__ == '__main__':
   main()
