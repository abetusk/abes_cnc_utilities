#!/usr/bin/python

import sys
import math
import re

if (len(sys.argv) < 3):
  sys.exit("provide filenames");


height0 = {}
height1 = {}

x_pnt = {}
y_pnt = {}

f0 = open(sys.argv[1], "r");
for line in f0:
  if re.match('^\s*#', line):
    continue
  if re.match('^\s*$', line):
    continue
  v = line.rsplit()
  k = str(float(v[0])) + ":" + str(float(v[1]))
  height0[k] = v[2]
  x_pnt[v[0]] = v[0]
  y_pnt[v[1]] = v[1]
f0.close()

f1 = open(sys.argv[2], "r");
for line in f1:
  if re.match('^\s*#', line):
    continue
  if re.match('^\s*$', line):
    continue
  v = line.rsplit()
  k = str(float(v[0])) + ":" + str(float(v[1]))
  height1[k] = v[2]
  x_pnt[v[0]] = v[0]
  y_pnt[v[1]] = v[1]
f1.close()

freq = {}
count = 0
var = 0.0
mean = 0.0
max_d = 0.0
min_d = 10.0
for x in x_pnt:
  for y in y_pnt:
    k = str(float(x)) + ":" + str(float(y))
    d = float(height0[k]) - float(height1[k])
    count += 1
    mean += d
    var += d*d
    if ( math.fabs(d) > max_d ):
      max_d = math.fabs(d)
    if ( math.fabs(d) < min_d ):
      min_d = math.fabs(d)
    s = str( math.fabs(d) )
    if s in freq:
      freq[s] += 1
    else:
      freq[s] = 1

mean /= float(count)
var /= float(count)
    
print "mean:", str( mean )
print "var:", str( var - (mean*mean) )
print "max:", str( max_d )
print "min:", str( min_d )

print
print "frequency:"
sorted_key = sorted( freq.keys() )
for k in sorted_key:
  print k, freq[k]

