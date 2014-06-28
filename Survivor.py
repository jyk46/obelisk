#=========================================================================
# Survivor.py
#=========================================================================
# Class for survivor units with varying stats and attributes. One or more
# survivors are grouped into Expeditions, which are what is actually
# shown on the map.

import random
import Attribute

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
  'Janus Worthington',
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

class Survivor():

  # Stats

  name        = ''
  age         = 0
  max_stamina = 10
  stamina     = 10
  physical    = 10
  mental      = 10
  heal_rate   = 0.5
  cure_prob   = 0.5
  attributes  = []

  # Chance of rolling attribute

  attribute_prob = 0.30

  # Constructor

  def __init__( self ):

    # Roll random stats based on age

    self.name        = random.choice( name_table )
    self.age         = random.randint( 10, 59 )
    self.max_stamina = random.randint( stam_table[self.age/10][0], stam_table[self.age/10][1] )
    self.stamina     = self.max_stamina
    self.physical    = random.randint( phys_table[self.age/10][0], phys_table[self.age/10][1] )
    self.mental      = random.randint( ment_table[self.age/10][0], ment_table[self.age/10][1] )
    self.heal_rate   = heal_table[self.age/10]
    self.cure_prob   = cure_table[self.age/10]
    self.attributes  = []

    # Roll random attributes (up to three per survivor)

    for i in range( 3 ):

      # Special case age-based attributes

      if ( i == 0 ) and ( self.age < 20 ):
        self.attributes.append( Attribute.Attribute( self.age, 'Youthful' ) )

      elif ( i == 0 ) and ( self.age >= 50 ):
        self.attributes.append( Attribute.Attribute( self.age, 'Elderly' ) )

      # Common case

      elif random.random() < self.attribute_prob:

        attribute = Attribute.Attribute( self.age )

        # Ensure no duplicate attributes

        while attribute in self.attributes:
          attribute = Attribute.Attribute( self.age )

        self.attributes.append( attribute )

  # Return combined stats bonuses from all attributes

  def get_attributes( self ):

    tot_attribute = Attribute.Attribute( self.age, 'Empty' )

    for attribute in self.attributes:
      tot_attribute += attribute

    return tot_attribute

  # Return job type (assume only one job per survivor)

  def get_job( self ):

    for attribute in self.attributes:
      if attribute.job != Attribute.NONE:
        return attribute.job

    return Attribute.NONE

  # Print debug information

  def debug( self ):

    print 'NAME: ', self.name
    print 'AGE : ', self.age
    print 'STA : ', self.max_stamina
    print 'PHYS: ', self.physical
    print 'MENT: ', self.mental
    print 'CURE: ', self.cure_prob
    print 'ATTRIBUTES:'

    for attribute in self.attributes:
      attribute.debug()
