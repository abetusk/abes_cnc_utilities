#!/usr/bin/python
"""
get feed back from grbl and the cnc_pcb_height_probe to map 
the height of the pcb
"""
import serial
import time
import numpy

import commands
import re
import sys

def send_grbl_command( cmd ) :
  print "sending '" + cmd + "'"
  grbl_serial.write(cmd + "\r\n");
  grbl_out = grbl_serial.readline()
  print "  got :", grbl_out.strip()


grbl_dev = "/dev/ttyUSB0"
grbl_baud = 9600
grbl_serial = serial.Serial(grbl_dev, grbl_baud)


probe_cmd = " ./cnc_pcb_height_probe_query read | grep continuity"
def probe_serial( ):
  (ret, res) = commands.getstatusoutput( probe_cmd )
  if ( re.search('continuity: yes', res) ):
    return 1
  elif ( re.search('continuity: no', res) ):
    return 0
  sys.exit( probe_cmd + " error (" + str(ret) + ")" )




# everything in mm

z_max = 1.0
z_min = -2.0
z_del = 0.01

z_tic = int( round( ((z_max - z_min) / z_del) + 0.5 ) )


x_min = 0.0
x_max = 80.0
x_tic = 10

y_min = 0.0
y_max = 50.0
y_tic = 10


send_grbl_command( "\r\n" )
send_grbl_command( "g90" )
send_grbl_command( "g21" )

send_grbl_command( "g1z" + z_max )
send_grbl_command( "g0 x" + x_min + " y" + y_min )

height = {}


for x in numpy.linspace(x_min, x_max, x_tic):
  for y in numpy.linspace(y_min, y_max, y_tic):
    #print "starting probe for x", x, "y", y, "(z", z_max, ")"

    for z in numpy.linspace(z_max, z_min, z_tic):
      print "  z", z

    if (z <= z_min):
      sys.exit("ERROR: z_min (" + str(z_min) + ") reached")

    print str(x), str(y), str(z)

    height[ str(x) + "," + str(y) ] = z

#for xy in height:
#  print "xy", xy, ", ", height[xy]
    



