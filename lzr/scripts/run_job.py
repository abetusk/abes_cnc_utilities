#!/usr/bin/python

import sys
import grbl
import re
import time

debug=False
#debug=True

if not debug:
  grbl.setup()


sx = 0
sy = 0
rapid_feed = 4000

# home
#
if not debug:
  grbl.send_command("M999")
  grbl.send_command("G28")
else:
  print "G28"

#SLEEPY=20
SLEEPY=0
count=0
for line in sys.stdin:
  line = line.strip()
  if not line: continue
  if not debug:
    grbl.send_command( line )
  else:
    print line

  count += 1
  if (SLEEPY>0) and ((count%SLEEPY)==0):
    print "sleeping..."
    time.sleep(1)

if not debug:
  grbl.send_command( "G0"+ "X" + str(sx)+ "Y" + str(sy) + " F" + str(rapid_feed))
  grbl.teardown()
else:
  print "G0"+ "X" + str(sx)+ "Y" + str(sy) + " F" + str(rapid_feed)
