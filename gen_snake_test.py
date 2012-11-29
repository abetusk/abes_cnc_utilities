#!/usr/bin/python

import sys
import numpy

n_tracks = 50
#n_tracks = 10
mil = 20
odd_even = 1

z_up = 0.01
z_plunge = -0.002

y_start = 0.0
y_start_p_mil = y_start + float(mil)/1000.0

y_end = y_start + 2.0
#y_end = y_start + 0.5
y_end_m_mil = y_end - float(mil)/1000.0

pad_width = 100.0
connection_length = 20.0

x_start = (pad_width + connection_length)/1000.0
x_end = x_start + float(n_tracks)*mil/1000.0

x = x_start

print "g20"
print

debug=1
if (debug):
  print "g0 f100"
  print "g1 f20"
  print

print "( start at home )"
print "g1 z" + str(z_up)
print "g0 x0 y0"
print

print "( left pad )"
print "g0 x" + str((pad_width + connection_length)/1000.0), "y" + str(y_end)
print "g1 z" + str(z_plunge)
print "g1 x0.0", "y" + str(y_end)
print "g1 x0.0", "y" + str(y_end - pad_width/1000.0)
print "g1 x" + str(pad_width/1000.0), "y" + str(y_end - pad_width/1000.0)
print "g1 x" + str(pad_width/1000.0), "y" + str(y_end - mil/1000.0)
print "g1 x" + str(x_start), "y" + str(y_end - mil/1000.0)

print "g1 z" + str(z_up)
print "g0 x" + str(x), "y" + str(y_end_m_mil)
print 

for i in range(n_tracks):

  print "( channel", str(i), "of", str(n_tracks), ")"
  print "g1 z" + str(z_plunge)

  if (i%2):
    print "g1 x" + str(x), "y" + str(y_end)
  else:
    print "g1 x" + str(x), "y" + str(y_start)

  print "g1 z" + str(z_up)

  x = float(i+1)*mil/1000.0 + x_start

  if (i%2):
    print "g0 x" + str(x), "y" + str(y_end_m_mil)
  else:
    print "g0 x" + str(x), "y" + str(y_start_p_mil)

  print

print
print "( last channel )"
print "g1 z" + str(z_plunge)
if (n_tracks%2):
  print "g1 x" + str(x), "y" + str(y_end)
else:
  print "g1 x" + str(x), "y" + str(y_start)
print


if (n_tracks%2):
  print "( top row )"
  print "g1 x" + str(x_start), "y" + str(y_end)

  print
  print "g1 z" + str(z_up)
  print

  print "( bottom row )"
  print "g0 x" + str(x_start), "y" + str(y_start)
  print "g1 z" + str(z_plunge)
  print "g1 x" + str(x_end), "y" + str(y_start)

else:
  print "( bottom row )"
  print "g1 x" + str(x_start), "y" + str(y_start)

  print
  print "g1 z" + str(z_up)
  print

  print "( top row )"
  print "g0 x" + str(x_start), "y" + str(y_end)
  print "g1 z" + str(z_plunge)
  print "g1 x" + str(x_end), "y" + str(y_end)

print 
print "g1 z" + str(z_up)
print

print "( right pad )"

if (n_tracks%2):
  print "g0 x" + str(x_end), "y" + str(y_start)
  print "g1 z" + str(z_plunge)
  print "g1 x" + str(x_end + (pad_width + connection_length)/1000.0), "y" + str(y_start)
  print "g1 x" + str(x_end + (pad_width + connection_length)/1000.0), "y" + str(y_start + pad_width/1000.0)
  print "g1 x" + str(x_end + connection_length/1000.0), "y" + str(y_start + pad_width/1000.0)
  print "g1 x" + str(x_end + connection_length/1000.0), "y" + str(y_start + mil/1000.0)
  print "g1 x" + str(x_end), "y" + str(y_start + mil/1000.0)
else:
  print "g0 x" + str(x_end), "y" + str(y_end)
  print "g1 z" + str(z_plunge)
  print "g1 x" + str(x_end + (pad_width + connection_length)/1000.0), "y" + str(y_end)
  print "g1 x" + str(x_end + (pad_width + connection_length)/1000.0), "y" + str(y_end - pad_width/1000.0)
  print "g1 x" + str(x_end + connection_length/1000.0), "y" + str(y_end - pad_width/1000.0)
  print "g1 x" + str(x_end + connection_length/1000.0), "y" + str(y_end - mil/1000.0)
  print "g1 x" + str(x_end), "y" + str(y_end - mil/1000.0)

print


# go home
print "( go home )"
print "g1 z" + str(z_up)
print "g0 x0.0 y0.0"


"""
print "g0 x" + x, "y" + y_start
print "g1 z" + z_down
print "g1 x" + x_start

print "g1 z" + z_up
print "g0 x" + x_start, "y" + y_end
print "g1 z" + z_down
print "g1 x" + x_end
"""

