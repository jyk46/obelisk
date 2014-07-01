#=========================================================================
# obelisk.py
#=========================================================================
# Main program to execute game. Generates a random map with the map
# generator and feeds the map into the game engine.

import pygame, sys, os
from pygame.locals import *

import properties
import engine

#-------------------------------------------------------------------------
# Main Function
#-------------------------------------------------------------------------

def main():

  # Initialize pygame

  pygame.init()

  # Configure display

  pygame.display.set_mode( ( properties.WINDOW_WIDTH, properties.WINDOW_HEIGHT ) )

  # Set caption

  pygame.display.set_caption( 'Obelisk v.1.0' )

  # Initialize game engine

  eng = engine.Engine()

  # Start game engine

  eng.start()

# Execute main function

if __name__ == '__main__':
   main()
