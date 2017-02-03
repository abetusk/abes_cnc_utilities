#!/usr/bin/python

import os

# everything in mm

rapid_feed = 4000

start_feed = 500
del_feed = 50
cur_feed = start_feed

fish_width = 20
fish_height = 20

row_fish = 5
col_fish = 8

space_fish_h = 15
space_fish_w = 15


# absolute
#
print "G90"

# metric units
#
print "G21"

Y = 0
for r in range(row_fish):
  X = 0
  for c in range(col_fish):


    path = [[X,Y-fish_height/2],
            [X,Y+fish_height/2],
            [X-fish_width/2, Y+fish_height/2],
            [X-fish_width/2, Y],
            [X+fish_width/2, Y]]

    print "G0" + "X" + str(path[0][0]) + "Y" + str(path[0][1]) + "F" + str(rapid_feed)
    for idx in range(1,len(path)):
      print "G1" + "X" + str(path[idx][0]) + "Y" + str(path[idx][1]) + "F" + str(cur_feed)



    X += space_fish_w + fish_width/2

    cur_feed += del_feed

  Y += space_fish_h + fish_height/2


