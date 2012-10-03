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
import math

grbl_dev = "/dev/ttyUSB0"
grbl_baud = 9600
grbl_serial = serial.Serial(grbl_dev, grbl_baud)

probe_cmd = " ./probe read | grep continuity"

# everything in mm

z_max = 0.1
z_min = -1.0
z_del = 0.01

z_tic = int( round( ((z_max - z_min) / z_del) + 0.5 ) )

x_min = 0.0
#x_max = 80.0
x_max = 100.0
x_tic = 20 + 1

y_min = 0.0
#y_max = 40.0
y_max = 60.0
y_tic = 12 + 1

verbose = 0

def probe_continuity( ):
  (ret, res) = commands.getstatusoutput( probe_cmd )
  if ( re.search('continuity: yes', res) ):
    return 1
  elif ( re.search('continuity: no', res) ):
    return 0
  sys.exit( probe_cmd + " error (" + str(ret) + ")" )


def send_grbl_command( cmd ) :
  if verbose:
    print "# sending '" + cmd + "'"
  grbl_serial.write(cmd + "\n")
  grbl_out = grbl_serial.readline()
  if verbose:
    print "#  got :", grbl_out.strip()
  while ( not re.search("ok", grbl_out) ):
    if verbose:
      print "#  got :", grbl_out.strip()
    grbl_out = grbl_serial.readline()
  if verbose:
    print "#", grbl_out

def get_grbl_var_position( var_name ):
  var_seen = 0
  var_pos = 0.0
  grbl_serial.write("$?\n")
  grbl_out = grbl_serial.readline()

  if verbose:
    print "#  get_grbl_var_position(", var_name, "): got :", grbl_out.strip()

  m = re.search( var_name + ".*=\s*(.*)", grbl_out) 
  if ( m ):

    if verbose:
      print "#", m.group(1)

    var_seen = 1
    var_pos = float(m.group(1))

  while ( not re.search("ok", grbl_out) ):
    grbl_out = grbl_serial.readline()

    if verbose:
      print "#  get_grbl_var_position(", var_name, "): got :", grbl_out.strip()

    m = re.search( var_name + ".*=\s*(.*)", grbl_out) 
    if ( m ):

      if verbose:
        print "#", m.group(1)

      var_seen = 1
      var_pos = float(m.group(1))
  if (not var_seen):
    sys.exit("error, didn't see '" + var_name + "' in get_grbl_var_position()")
  return var_pos

def wait_for_var_position( var_name, var_val ):
  sleepy = 0.05
  var_epsilon = 0.001
  cur_val = get_grbl_var_position( var_name )
  if verbose:
    print "#", str(var_val), " var_epsilon", str(x_epsilon), "cur_x", str(cur_val)
  while (math.fabs(var_val - cur_val) > var_epsilon):
    if verbose:
      print "# cur_val", str(cur_val), ", waiting for ", var_name, str(var_val)
    time.sleep(sleepy)
    cur_val = get_grbl_var_position( var_name )

send_grbl_command( "" )
send_grbl_command( "" )
send_grbl_command( "g90" )
send_grbl_command( "g21" )

send_grbl_command( "g1z" + str(z_max) )
send_grbl_command( "g0 x" + str(x_min) + " y" + str(y_min) )

send_grbl_command( "$" )
send_grbl_command( "$?" )

if verbose:
  print "# grbl setup done\n"
  print "probe continuity: ", str(probe_continuity())
  print "setup done\n"

get_grbl_var_position( "Z" )

height = {}

even_odd = 0

for x in numpy.linspace(x_min, x_max, x_tic):
  y_start = y_min
  y_end = y_max

  if (even_odd == 1):
    y_start = y_max
    y_end = y_min

  even_odd = 1-even_odd

#  for y in numpy.linspace(y_min, y_max, y_tic):
  for y in numpy.linspace(y_start, y_end, y_tic):
    #time.sleep(.1)
    time.sleep(.05)
    if verbose:
      print "# starting probe for x", x, "y", y, "(z", z_max, ")"
    send_grbl_command( "g1z" + str(z_max) )
    send_grbl_command( "g0 x" + str(x) + " y" + str(y) )

    wait_for_var_position("X", x)
    wait_for_var_position("Y", y)
    wait_for_var_position("Z", z_max)

    for z in numpy.linspace(z_max, z_min, z_tic):
      if verbose:
        print "#  positioning z", z
      send_grbl_command( "g1z"+str(z) )


      if verbose:
        print "# waiting for z", str(z)
      wait_for_var_position("Z", z)
      c = probe_continuity()
      if verbose:
        print "# got c ", str(c)
      if ( probe_continuity() ):
        if verbose:
          print "# yep!\n"
        break;
      else:
        if verbose:
          print "# nope\n"
        pass

    if (z <= z_min):
      sys.exit("ERROR: z_min (" + str(z_min) + ") reached")

    print str(x), str(y), str(z)
    sys.stdout.flush()

    height[ str(x) + "," + str(y) ] = z

#for xy in height:
#  print "xy", xy, ", ", height[xy]

send_grbl_command( "g1z" + str(z_max) )
send_grbl_command( "g0x0y0" )


