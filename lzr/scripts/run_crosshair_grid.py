#!/usr/bin/python

import grbl

N=20
M=20

#N=3
#M=3

sx=10
sy=10

dx=6.36
dy=6.35

cxh_dx=0.5
cxh_dy=0.5

rapid_feed=4000
feed=500

grbl.setup()

CUT_GCODE = "G1"
debug=False
if debug:
  CUT_GCODE="G0"


# home
#
grbl.send_command("G28")

for n in range(N):
  for m in range(M):

    x = sx + n*dx
    y = sy + m*dy

    tx = x - cxh_dx
    ty = y

    grbl.send_command("G0" + "X" + str(x-cxh_dx) + "Y" + str(y) + " F" + str(rapid_feed))
    grbl.send_command( CUT_GCODE + "X" + str(x+cxh_dx)+ "Y" + str(y)+ " F" + str(feed))

    grbl.send_command( "G0"+ "X" + str(x)+ "Y" + str(y-cxh_dy) + " F" + str(rapid_feed))
    grbl.send_command( CUT_GCODE + "X" + str(x)+ "Y" + str(y+cxh_dy)+ " F" + str(feed))

grbl.send_command( "G0"+ "X" + str(sx)+ "Y" + str(sy) + " F" + str(rapid_feed))

grbl.teardown()
