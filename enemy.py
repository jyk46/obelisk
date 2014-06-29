#=========================================================================
# enemy.py
#=========================================================================
# Class for spawnable enemies with damage, armor, stamina statistics.

#-------------------------------------------------------------------------
# Utility Tables
#-------------------------------------------------------------------------

enemy_table = {

  # name               sta arm min max

  'Bee Swarm'       : [  4,  0,  1,  3 ],
  'Wolf Pack'       : [  8,  0,  2,  4 ],
  'Panther'         : [ 12,  0,  3,  6 ],
  'Gorilla'         : [ 16,  1,  4,  8 ],
  'Raptor'          : [ 14,  1,  2, 10 ],
  'Native'          : [ 10,  0,  1,  5 ],
  'Cultist'         : [ 10,  1,  2,  8 ],
  'Apparition'      : [ 18,  2,  4, 12 ],
  'Giant'           : [ 20,  1,  4, 10 ],
  'Anaconda'        : [ 12,  0,  6,  8 ],
  'Mudman'          : [ 16,  3,  3,  9 ],
  'Deep One'        : [ 20,  2,  4, 16 ],
  'Dim. Shambler'   : [ 20,  4,  8, 14 ],
  'The Unspeakable' : [ 40, 10, 12, 20 ],

}

#-------------------------------------------------------------------------
# Main Class
#-------------------------------------------------------------------------

class Enemy():

  # Constructor

  def __init__( self, name ):

    assert( name in enemy_table )

    self.name        = name
    self.max_stamina = enemy_table[self.name][0]
    self.stamina     = self.max_stamina
    self.armor       = enemy_table[self.name][1]
    self.min_dmg     = enemy_table[self.name][2]
    self.max_dmg     = enemy_table[self.name][3]
