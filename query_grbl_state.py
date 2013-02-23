#!/usr/bin/python

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

grbl_serial.write("?");
grbl_out = grbl_serial.readline()
print grbl_out

m = re.search( "^<([^,]*),MPos:([^,]*),([^,]*),([^,]*),", grbl_out)
if ( m ):
  state = m.group(1)
  x = float(m.group(2))
  y = float(m.group(3))
  z = float(m.group(4))

  print "matched:", m.group(0)
  print "got state:", state, ", x:", x, ", y:", y, ", z:", z
