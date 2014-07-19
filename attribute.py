#=========================================================================
# attribute.py
#=========================================================================
# Describes stats or special bonuses that can be assigned to each
# survivor. Each attribute can positively or negatively affect a stat or
# action based on the table below.

import random

#-------------------------------------------------------------------------
# Utility Tables
#-------------------------------------------------------------------------

# Job types

NONE, DOCTOR, ENGINEER, LEADER, SOLDIER, MYSTIC = range( 6 )

# Possible attributes

attr_table = [

  # prob  name           phys  ment  heal  cure  expl  scav  day nigt job

  [ 0.00, 'Empty',       0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0,  0,   NONE ],
  [ 0.14, 'Athletic',    0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0,  0,   NONE ],
#  [ 0.07, 'Delicate',   -0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0,  0,   NONE ],
  [ 0.14, 'Brilliant',   0.00, 0.20, 0.00, 0.00, 0.00, 0.00, 0,  0,   NONE ],
#  [ 0.07, 'Ignorant',    0.00,-0.20, 0.00, 0.00, 0.00, 0.00, 0,  0,   NONE ],
  [ 0.14, 'Vigorous',    0.00, 0.00, 0.20, 0.00, 0.00, 0.00, 0,  0,   NONE ],
#  [ 0.07, 'Feeble',      0.00, 0.00,-0.20, 0.00, 0.00, 0.00, 0,  0,   NONE ],
#  [ 0.14, 'Resilient',   0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0,  0,   NONE ],
#  [ 0.07, 'Sickly',      0.00, 0.00, 0.00, 0.10, 0.00, 0.00, 0,  0,   NONE ],
  [ 0.14, 'Agile',       0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0,  0,   NONE ],
  [ 0.14, 'Resourceful', 0.00, 0.00, 0.00, 0.00, 0.00, 0.50, 0,  0,   NONE ],
  [ 0.14, 'Efficient',   0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1,  0,   NONE ],
#  [ 0.07, 'Night Owl',   0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0,  0,   NONE ],
  [ 0.06, 'Experienced', 0.00, 0.00, 0.00, 0.00, 0.25, 0.20, 1,  0,   NONE ],
  [ 0.00, 'Youthful',    0.00, 0.00, 0.20, 0.20, 0.50, 0.00, 0,  0,   NONE ],
#  [ 0.00, 'Elderly',     0.00, 0.00,-0.20,-0.20, 0.20, 0.00, 0,  0,   NONE ],

  [ 0.02, 'Doctor',      0.00, 0.10, 0.00, 0.00, 0.00, 0.00, 0,  0,   DOCTOR    ],
  [ 0.02, 'Engineer',    0.00, 0.10, 0.00, 0.00, 0.00, 0.00, 1,  0,   ENGINEER  ],
  [ 0.02, 'Leader',      0.00, 0.00, 0.00, 0.00, 0.50, 0.20, 0,  0,   LEADER    ],
  [ 0.02, 'Soldier',     0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0,  0,   SOLDIER   ],
  [ 0.02, 'Mystic',      0.00, 0.20, 0.00, 0.00, 0.00, 0.00, 0,  0,   MYSTIC    ],

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

class Attribute:

  # Constructor

  def __init__( self, age, name='' ):

    # Request specific attribute

    if name != '':

      for attr in attr_table:

        if attr[1] == name:

          self.name           = attr[1]
          self.physical_bonus = attr[2]
          self.mental_bonus   = attr[3]
          self.heal_bonus     = attr[4]
          self.cure_bonus     = attr[5]
          self.explore_bonus  = attr[6]
          self.scavenge_bonus = attr[7]
          self.day_bonus      = attr[8]
          self.night_bonus    = attr[9]
          self.job            = attr[10]

          if name == 'Experienced':
            self.physical_bonus = max( age - 30, 0 ) * 0.02
            self.mental_bonus   = max( age - 30, 0 ) * 0.02

          return

      print 'Error: invalid attribute name, ', name

    # Randomly roll attribute

    else:

      prob = 0.0
      roll = random.random()

      for attr in attr_table:

        if roll < ( prob + attr[0] ):

          self.name           = attr[1]
          self.physical_bonus = attr[2]
          self.mental_bonus   = attr[3]
          self.heal_bonus     = attr[4]
          self.cure_bonus     = attr[5]
          self.explore_bonus  = attr[6]
          self.scavenge_bonus = attr[7]
          self.day_bonus      = attr[8]
          self.night_bonus    = attr[9]
          self.job            = attr[10]

          if name == 'Experienced':
            self.physical_bonus = max( age - 30, 0 ) * 0.02
            self.mental_bonus   = max( age - 30, 0 ) * 0.02

          return

        else:

          prob += attr[0]

      print 'Error: incomplete attribute probability range'

  # Overload == operator to return true if two attributes have the same
  # name or both are special jobs or attributes are opposites

  def __eq__( self, attr ):
    return ( self.name == attr.name ) \
        or ( self.job != NONE and attr.job != NONE ) \
        or ( self.name in opp_table and attr.name == opp_table[self.name] )

  # Overload + operator to sum up individual bonuses

  def __add__( self, attr ):

    tot_attr = Attribute( 0, 'Empty' )

    tot_attr.name           = self.name + '*'
    tot_attr.physical_bonus = self.physical_bonus + attr.physical_bonus
    tot_attr.mental_bonus   = self.mental_bonus   + attr.mental_bonus
    tot_attr.heal_bonus     = self.heal_bonus     + attr.heal_bonus
    tot_attr.cure_bonus     = self.cure_bonus     + attr.cure_bonus
    tot_attr.explore_bonus  = self.explore_bonus  + attr.explore_bonus
    tot_attr.scavenge_bonus = self.scavenge_bonus + attr.scavenge_bonus
    tot_attr.day_bonus      = self.day_bonus      + attr.day_bonus
    tot_attr.night_bonus    = self.night_bonus    + attr.night_bonus
    tot_attr.job            = self.job

    return tot_attr

  # Print debug information

  def debug( self ):

    print self.name, ': ', self.physical_bonus, ', ', self.mental_bonus, ', ', \
          self.heal_bonus, ', ', self.cure_bonus, ', ', self.explore_bonus, ', ', \
          self.scavenge_bonus, ', ', self.day_bonus, ', ', self.night_bonus
