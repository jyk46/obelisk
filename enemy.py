#=========================================================================
# enemy.py
#=========================================================================
# Class for spawnable enemies with damage, armor, stamina statistics.

import random
import properties

#-------------------------------------------------------------------------
# Utility Tables
#-------------------------------------------------------------------------

enemy_table = {

  # name               sta arm min max spd  img

  'Bee Swarm'       : [  4,  0,  1,  3,  2, 'swarm.png' ],
  'Wolf Pack'       : [  8,  0,  2,  4,  0, 'wolf.png' ],
  'Panther'         : [ 12,  0,  3,  6,  2, 'panther.png' ],
  'Gorilla'         : [ 16,  1,  4,  8, -1, 'gorilla.png' ],
  'Raptor'          : [ 14,  1,  2, 10,  4, 'raptor.png' ],
  'Native'          : [ 10,  0,  1,  5,  1, 'native.png' ],
  'Cultist'         : [ 10,  1,  2,  8,  0, 'cultist.png' ],
  'Apparition'      : [ 18,  2,  4, 12,  6, 'apparition.png' ],
  'Giant'           : [ 20,  1,  4, 10, -2, 'giant.png' ],
  'Anaconda'        : [ 12,  0,  6,  8,  0, 'anaconda.png' ],
  'Mudman'          : [ 16,  3,  3,  9,  0, 'mudman.png' ],
  'Deep One'        : [ 20,  2,  4, 16,  4, 'deep.png' ],
  'Dim. Shambler'   : [ 20,  4,  8, 14,  8, 'shambler.png' ],
  'The Unspeakable' : [ 40, 10, 12, 20, 10, 'unspeakable.png' ],

}

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Enemy:

  # Constructor

  def __init__( self, name ):

    assert( name in enemy_table )

    self.name        = name
    self.max_stamina = enemy_table[self.name][0]
    self.stamina     = self.max_stamina
    self.armor       = enemy_table[self.name][1]
    self.min_dmg     = enemy_table[self.name][2]
    self.max_dmg     = enemy_table[self.name][3]
    self.speed       = enemy_table[self.name][4]
    self.img_path    = properties.ENEMY_PATH + enemy_table[self.name][5]

  # Return speed to determine turn order. This function would not
  # normally be necessary but having the same function name for returning
  # the speed for both enemies and survivors makes turn order sorting
  # much cleaner.

  def get_speed( self ):

    return self.speed

  # Determine to which survivor and how much damage the enemy deals
  # during the defend phase. Enemy-specific AI can be added here, but
  # currently all enemies attack randomly.

  def attack( self, survivors ):

    # Determine survivor to attack

    _survivor = random.choice( survivors )

    while _survivor.stamina == 0:
      _survivor = random.choice( survivors )

    # Calculate damage

    raw_dmg = random.randint( self.min_dmg, self.max_dmg )
    dmg     = max( raw_dmg - _survivor.armor.armor, 0 )

    return _survivor, dmg
