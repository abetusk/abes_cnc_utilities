#!/usr/bin/python

import sys
import math

if (len(sys.argv) < 2):
  sys.exit("provide filenames")

fn = {}
xy = {}
x_pnt = {}
y_pnt = {}

for f in sys.argv[1:]:
  fn[f] = {}

for f in fn:
  #print 
  #print f
  fp = open(f, "r")
  a = {}
  for line in fp:
    v = line.rsplit()
    k = str(float(v[0])) + ":" + str(float(v[1]))

    x = float(v[0])
    y = float(v[1])
    z = float(v[2])

    x_pnt[x] = x
    y_pnt[y] = y
    a[k] = z


    if (k not in xy):
      xy[k] = z

    #print 'got:', z, ", was", xy[k], "for", k

    if z < xy[k]:
      xy[k] = z
  fp.close()


  fn[f] = a

x_sorted = sorted( x_pnt.keys() )
y_sorted = sorted( y_pnt.keys() )
for x in x_sorted:
  for y in y_sorted:
    k = str(x) + ":" + str(y)
    print x, y, xy[k]


