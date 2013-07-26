#!/usr/bin/python
"""
use GRBL probe functionality to probe height of PCB
"""
import time
import numpy

import commands
import re
import sys
import math
import argparse

import grbl

verbose = False
debug = False

baud = 9600
device = "/dev/ttyUSB0"

x_start = 0.0
y_start = 0.0
x_end = 100.0
y_end = 40.0

z_down = -1.0
z_up = 0.0

tic = 5.0

parser = argparse.ArgumentParser(description= "Probe using GRBL's height probe functionality to find height of PCB.")
parser.add_argument("-B", "--baud", help="Set baud rate (default 9600)", nargs = 1, default=[baud], type=int)
parser.add_argument("-D", "--device", help="Set device (default /dev/ttyUSB0)", nargs = 1, default=[device] )
parser.add_argument("-v", "--verbose", help="Set verbose mode", default=False, action='store_true')
parser.add_argument("--debug", help="Set verbose mode", default=False, action='store_true')
parser.add_argument("-x", "--x_start", help="start of probe x (default 0)", nargs=1, default=[x_start] )
parser.add_argument("-X", "--x_end", help="end of probe x (default 0)", nargs=1, default=[x_end] )
parser.add_argument("-y", "--y_start", help="start of probe y (default 0)", nargs=1, default=[y_start] )
parser.add_argument("-Y", "--y_end", help="end of probe y (default 0)", nargs=1, default=[y_end] )
parser.add_argument("-z", "--z_down", help="lower bound of where z probe can go (default -1mm)", nargs=1, default=[z_down] )
parser.add_argument("-Z", "--z_up", help="safe distance to retract z probe to (default 0)", nargs=1, default=[z_up] )
parser.add_argument("-t", "--tic", help="delta length to move to (default 5mm)", nargs=1, default=[tic] )

args = parser.parse_args()

if hasattr(args, 'baud'):       baud = args.baud[0]
if hasattr(args, 'device'):     device = args.device[0]
if hasattr(args, 'verbose'):    verbose = args.verbose
if hasattr(args, 'debug'):      debug = args.debug
if hasattr(args, 'x_start'):    x_start = float(args.x_start[0])
if hasattr(args, 'x_end'):      x_end = float(args.x_end[0])
if hasattr(args, 'y_start'):    y_start = float(args.y_start[0])
if hasattr(args, 'y_end'):      y_end = float(args.y_end[0])
if hasattr(args, 'z_up'):       z_up = float(args.z_up[0])
if hasattr(args, 'z_down'):     z_down = float(args.z_down[0])
if hasattr(args, 'tic'):        tic = float(args.tic[0])

if verbose:
  print "# baud:", baud, "device:", device, "verbose:", verbose
  print "# x_start:", x_start, "x_end:", x_end, "y_start:", y_start, "y_end:", y_end, "z_up:", z_up, "z_down:", z_down
  print "# tic:", tic

if not debug:
  grbl.setup()

# setup absolute, in mm
if not debug:
  grbl.send_command( "" )
  grbl.send_command( "" )
  grbl.send_command( "g90" )
  grbl.send_command( "g21" )

  # position in 'home' position
  grbl.send_command( "g1z" + str(z_up) )
  grbl.send_command( "g0 x" + str(x_start) + " y" + str(y_start) )

  if verbose:
    print '# ?', str(z_down)

  # set lower z threshold
  grbl.send_command( "$25=" + str(z_down) )

  # enable probe functionality
  grbl.send_command( "$26=1" )


if verbose:
  print "# grbl setup done\n"
  print "# setup done\n"

if not debug:
  grbl.get_var_position( "Z" )


even_odd = 0

x_int_end = int( (x_end  - x_start) / tic )
x_dir = x_int_end / abs(x_int_end) 
x = x_start
x_i=0

while x_i != (x_int_end+x_dir):
  y_0 = float(y_start)
  y_1 = float(y_end)
  if (even_odd == 1):
    y_0 = float(y_end)
    y_1 = float(y_start)
  even_odd = 1-even_odd

  y_int_end = int( (y_1 - y_0) / tic )
  y_dir = y_int_end / abs(y_int_end)
  y = y_0
  y_i = 0

  while y_i != (y_int_end+y_dir):

    if verbose:
      print "# starting probe for x", x, "y", y, "(z", z_up, ")"

    if not debug:
      grbl.send_command( "g1 z" + str(z_up) )
      grbl.send_command( "g0 x" + str(x) + " y" + str(y) )

      grbl.wait_for_var_position("X", x)
      grbl.wait_for_var_position("Y", y)
      grbl.wait_for_var_position("Z", z_up)

      # probe
      grbl.send_command( "$P" )

      # get touched position
      probe_str = grbl.send_command("$S")

      if verbose:
        print "# probe_str:", probe_str

      m = re.search("contact_z:(-?\d+(\.\d+)?)", probe_str)
      if m:
        z = m.group(1)
      else:
        sys.exit("ERROR: couldn't get z contact, exiting")

      if (z <= z_down):
        sys.exit("ERROR: z_min (" + str(z_min) + ") reached")
    else:
      z = 0

    print str(x), str(y), str(z)
    sys.stdout.flush()

    y_i += y_dir
    y = y_0 + float(y_i)*tic

  x_i += x_dir
  x = x_start + float(x_i)*tic


if not debug:
  grbl.send_command( "g1z" + str(z_up) )
  grbl.send_command( "g0 x0 y0" )




