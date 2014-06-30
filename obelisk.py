#=========================================================================
# obelisk.py
#=========================================================================
# Main program to execute game. Generates a random map with the map
# generator and feeds the map into the game engine.

import pygame, sys, os
from pygame.locals import *

import properties
import mapgen
import engine

#-------------------------------------------------------------------------
# Main Function
#-------------------------------------------------------------------------

def main():

  # Initialize pygame

  pygame.init()

  # Configure display

  pygame.display.set_mode( ( Properties.WIN_WIDTH, Properties.WIN_HEIGHT ) )

  # Set caption

  pygame.display.set_caption( 'Obelisk v.1.0' )

  # Generate random map

  mg = mapgen.MapGen( properties.MAP_SIZE )

  # Initialize game engine

  engine = engine.Engine( mg.map )

  # Start game engine

  engine.start()

# Execute main function

if __name__ == '__main__':
   main()
