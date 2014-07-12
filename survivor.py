#=========================================================================
# survivor.py
#=========================================================================
# Class for survivor units with varying stats and attributes.

import pygame, sys, os
from pygame.locals import *

import random
import properties
import utils
import attribute

#-------------------------------------------------------------------------
# Utility Tables
#-------------------------------------------------------------------------

# Possible names for survivors

name_table = [
  'John Robinson',
  'Christina Taylor',
  'Kenneth Laker',
  'Saleem Kassam',
  'Santosh Venkatesh',
  'Roch Guren',
  'Sue Ellen Goodwin',
  'Zachary Redding',
  'Anton Epstein',
  'Lauren Blake',
  'Alyssa Chapman',
  'Ashley Dougherty',
  'Stephanie Griffin',
  'Janus Worthing',
  'Hyun-woo Kim',
  'Seo-yeon Lee',
  'Wei Wang',
  'Xiao Ying Zhang',
  'Akira Konno',
  'Yoshiko Yamada',
  'Juan Martinez',
  'Mercedes Garcia',
  'Gabriel Laurent',
  'Chloe Dubois',
  'Lucas Schmidt',
  'Anna Muller',
  'Mahmoud Assaf',
  'Farida Nazari',
  'Yosef Ovitz',
  'Talia Mizrahi',
  'Ivan Petrov',
  'Sofya Ivanov',
  'Hugo Johansson',
  'Elsa Lindholm',
  'Dagur Scheving',
  'Rakel Briem',
  'Biruk Bekele',
  'Qali Worku',
]

# Stats range based on age

stam_table = [
  [  5, 10 ],
  [ 10, 15 ],
  [ 15, 20 ],
  [ 12, 17 ],
  [  8, 13 ],
  [  5, 10 ],
]

phys_table = [
  [  4, 10 ],
  [  8, 16 ],
  [ 10, 20 ],
  [ 10, 16 ],
  [  8, 14 ],
  [  6, 12 ],
]

ment_table = [
  [  4, 10 ],
  [  6, 12 ],
  [  8, 14 ],
  [ 10, 16 ],
  [ 12, 18 ],
  [ 14, 20 ],
]

heal_table = [
  0.90,
  0.80,
  0.70,
  0.60,
  0.50,
  0.40,
]

cure_table = [
  0.75,
  0.75,
  0.60,
  0.40,
  0.30,
  0.20,
]

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Survivor:

  # Constructor

  def __init__( self ):

    # Roll random stats based on age

    self.name        = random.choice( name_table )
    name_table.remove( self.name )
    self.age         = random.randint( 10, 59 )
    self.max_stamina = random.randint( stam_table[self.age/10][0], stam_table[self.age/10][1] )
    self.stamina     = self.max_stamina
    self.physical    = random.randint( phys_table[self.age/10][0], phys_table[self.age/10][1] )
    self.mental      = random.randint( ment_table[self.age/10][0], ment_table[self.age/10][1] )
    self.heal_rate   = heal_table[self.age/10]
    self.cure_prob   = cure_table[self.age/10]
    self.attributes  = []
    self.free        = True
    self.sick        = False

    # Text graphics

    self.text_surface, self.text_rect = utils.gen_text_pos( self.name, 14, 0, 0, utils.WHITE )

    # Roll random attributes (up to three per survivor)

    for i in range( 3 ):

      # Special case age-based attributes

      if ( i == 0 ) and ( self.age < 20 ):
        self.attributes.append( attribute.Attribute( self.age, 'Youthful' ) )

#      elif ( i == 0 ) and ( self.age >= 50 ):
#        self.attributes.append( attribute.Attribute( self.age, 'Elderly' ) )

      # Common case

      elif random.random() < properties.ATTRIBUTE_PROB:

        attr = attribute.Attribute( self.age )

        # Ensure no duplicate attributes

        while attr in self.attributes:
          attr = attribute.Attribute( self.age )

        self.attributes.append( attr )

  # Overload == operator to return true if names match (assume only
  # unique names per play-through)

  def __eq__( self, _survivor ):
    return ( self.name == _survivor.name )

  # Return physical bonus

  def get_physical_bonus( self ):

    return ( self.physical - 10 ) / 2

  # Return mental bonus

  def get_mental_bonus( self ):

    return ( self.mental - 10 ) / 2

  # Return combined stats bonuses from all attributes

  def get_attributes( self ):

    tot_attr = attribute.Attribute( self.age, 'Empty' )

    for attr in self.attributes:
      tot_attr += attr

    return tot_attr

  # Return job type (assume only one job per survivor)

  def get_job( self ):

    for attr in self.attributes:
      if attr.job != attribute.NONE:
        return attr.job

    return attribute.NONE

  # Print debug information

  def debug( self ):

    print 'NAME: ', self.name
    print 'AGE : ', self.age
    print 'STA : ', self.max_stamina
    print 'PHYS: ', self.physical
    print 'MENT: ', self.mental
    print 'CURE: ', self.cure_prob
    print 'ATTRIBUTES:'

    for attr in self.attributes:
      attr.debug()
