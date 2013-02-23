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

verbose = 1

def send_grbl_command( cmd ) :
  if verbose:
    print "# sending '" + cmd + "'"
  grbl_serial.write(cmd + "\n")
  grbl_out = grbl_serial.readline()
  if verbose:
    #print "#  got. :", grbl_out.strip()
    pass
  while ( not re.search("ok", grbl_out) ):
    if verbose:
      print "#  got :", grbl_out.strip()
    grbl_out = grbl_serial.readline()
  if verbose:
    print "#", grbl_out

send_grbl_command( "" )
send_grbl_command( "" )

send_grbl_command( "$" )
send_grbl_command( "$?" )


