#=========================================================================
# Attribute
#=========================================================================
# Describes stats or special bonuses that can be assigned to each
# survivor. Each attribute can positively or negatively affect a stat or
# action based on the table below.

import numpy
import random

#-------------------------------------------------------------------------
# Utility Tables
#-------------------------------------------------------------------------

# Job types

NONE, DOCTOR, ENGINEER, LEADER, SOLDIER, PROFESSOR, MYSTIC = range( 7 )

# Possible attributes

attr_table = [

  # prob  name           phys  ment  heal  cure  expl  scav  day   nigt  job

  [ 0.00, 'Empty',       0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, NONE ],
  [ 0.07, 'Athletic',    0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, NONE ],
  [ 0.07, 'Delicate',   -0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, NONE ],
  [ 0.07, 'Brilliant',   0.00, 0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, NONE ],
  [ 0.07, 'Ignorant',    0.00,-0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, NONE ],
  [ 0.07, 'Vigorous',    0.00, 0.00, 0.20, 0.00, 0.00, 0.00, 0.00, 0.00, NONE ],
  [ 0.07, 'Feeble',      0.00, 0.00,-0.20, 0.00, 0.00, 0.00, 0.00, 0.00, NONE ],
  [ 0.07, 'Resilient',   0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00, NONE ],
  [ 0.07, 'Sickly',      0.00, 0.00, 0.00, 0.10, 0.00, 0.00, 0.00, 0.00, NONE ],
  [ 0.07, 'Agile',       0.00, 0.00, 0.00, 0.00,-0.50, 0.00, 0.00, 0.00, NONE ],
  [ 0.07, 'Resourceful', 0.00, 0.00, 0.00, 0.00, 0.00, 0.50, 0.00, 0.00, NONE ],
  [ 0.07, 'Efficient',   0.00, 0.00, 0.00, 0.00, 0.00, 0.00,-0.20,-0.20, NONE ],
  [ 0.07, 'Night Owl',   0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,-0.50, NONE ],
  [ 0.04, 'Experienced', 0.00, 0.00, 0.00, 0.00, 0.20, 0.20,-0.20,-0.20, NONE ],
  [ 0.00, 'Youthful',    0.00, 0.00, 0.20, 0.20,-0.20, 0.00, 0.00, 0.00, NONE ],
  [ 0.00, 'Elderly',     0.00, 0.00,-0.20,-0.20, 0.20, 0.00, 0.00, 0.00, NONE ],

  [ 0.02, 'Doctor',      0.00, 0.10, 0.10, 0.00, 0.00, 0.00, 0.00, 0.00, DOCTOR    ],
  [ 0.02, 'Engineer',    0.00, 0.10, 0.00, 0.00, 0.00, 0.00, 0.10, 0.00, ENGINEER  ],
  [ 0.02, 'Leader',      0.00, 0.00, 0.00, 0.00, 0.10, 0.10, 0.00, 0.00, LEADER    ],
  [ 0.02, 'Soldier',     0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, SOLDIER   ],
  [ 0.02, 'Professor',   0.00, 0.10, 0.00, 0.00, 0.00, 0.10, 0.00, 0.00, PROFESSOR ],
  [ 0.02, 'Mystic',      0.00, 0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, MYSTIC    ],

]

# Opposites table for preventing bonuses that cancel

opp_table = {
  'Athletic'  : 'Delicate',
  'Delicate'  : 'Athletic',
  'Brilliant' : 'Ignorant',
  'Ignorant'  : 'Brilliant',
  'Vigorous'  : 'Feeble',
  'Feeble'    : 'Vigorous',
  'Resilient' : 'Sickly',
  'Sickly'    : 'Resilient',
}

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Attribute():

  # Stats bonuses

  name           = ''
  physical_bonus = 0.0
  mental_bonus   = 0.0
  heal_bonus     = 0.0
  cure_bonus     = 0.0
  explore_bonus  = 0.0
  scavenge_bonus = 0.0
  day_bonus      = 0.0
  night_bonus    = 0.0
  job            = NONE

  # Constructor

  def __init__( self, age, name='' ):

    # Request specific attribute

    if name != '':

      for attribute in attr_table:

        if attribute[1] == name:

          self.name           = attribute[1]
          self.physical_bonus = attribute[2]
          self.mental_bonus   = attribute[3]
          self.heal_bonus     = attribute[4]
          self.cure_bonus     = attribute[5]
          self.explore_bonus  = attribute[6]
          self.scavenge_bonus = attribute[7]
          self.day_bonus      = attribute[8]
          self.night_bonus    = attribute[9]
          self.job            = attribute[10]

          if name == 'Experienced':
            self.physical_bonus = max( age - 30, 0 ) * 0.02
            self.mental_bonus   = max( age - 30, 0 ) * 0.02

          return

      print 'Error: invalid attribute name, ', name

    # Randomly roll attribute

    else:

      prob = 0.0
      roll = random.random()

      for attribute in attr_table:

        if roll < ( prob + attribute[0] ):

          self.name           = attribute[1]
          self.physical_bonus = attribute[2]
          self.mental_bonus   = attribute[3]
          self.heal_bonus     = attribute[4]
          self.cure_bonus     = attribute[5]
          self.explore_bonus  = attribute[6]
          self.scavenge_bonus = attribute[7]
          self.day_bonus      = attribute[8]
          self.night_bonus    = attribute[9]
          self.job            = attribute[10]

          if name == 'Experienced':
            self.physical_bonus = max( age - 30, 0 ) * 0.02
            self.mental_bonus   = max( age - 30, 0 ) * 0.02

          return

        else:

          prob += attribute[0]

      print 'Error: incomplete attribute probability range'

  # Overload == operator to return true if two attributes have the same
  # name or both are special jobs or attributes are opposites

  def __eq__( self, attribute ):
    return ( self.name == attribute.name ) \
        or ( self.job != NONE and attribute.job != NONE ) \
        or ( self.name in opp_table and attribute.name == opp_table[self.name] )

  # Overload + operator to sum up individual bonuses

  def __add__( self, attribute ):

    tot_attribute = Attribute( 0 )

    tot_attribute.name           = self.name + '*'
    tot_attribute.physical_bonus = self.physical_bonus + attribute.physical_bonus
    tot_attribute.mental_bonus   = self.mental_bonus   + attribute.mental_bonus
    tot_attribute.heal_bonus     = self.heal_bonus     + attribute.heal_bonus
    tot_attribute.cure_bonus     = self.cure_bonus     + attribute.cure_bonus
    tot_attribute.explore_bonus  = self.explore_bonus  + attribute.explore_bonus
    tot_attribute.scavenge_bonus = self.scavenge_bonus + attribute.scavenge_bonus
    tot_attribute.day_bonus      = self.day_bonus      + attribute.day_bonus
    tot_attribute.night_bonus    = self.night_bonus    + attribute.night_bonus
    tot_attribute.job            = self.job

    return tot_attribute

  # Print debug information

  def debug( self ):

    print self.name, ': ', self.physical_bonus, ', ', self.mental_bonus, ', ', \
          self.heal_bonus, ', ', self.cure_bonus, ', ', self.explore_bonus, ', ', \
          self.scavenge_bonus, ', ', self.day_bonus, ', ', self.night_bonus
