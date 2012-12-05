#!/usr/bin/python
#
# I tried to get fancy and not assume the height map grid was uniform, but it's getting cumbersom
# ASSUMES HEIGHT MAP IS UNIFORM
#
# simple catmull-rom interpoloation of a gcode file (2 distinct depths) given a height map

import random
import sys
import operator
import math

import getopt
import re

# p_m1 previsou, p current
# P(0) = p_m1
# P(1) = p
def catmull_rom( s, p_m2, p_m1, p, p_1 ):
  tau = 0.5
  q = [0.0, 0.0, 0.0]

  s2 = s*s
  s3 = s2*s

  a = -(tau*s) + (2.0*tau*s2) - (tau*s3)
  b = 1.0 + (s2*(tau-3.0)) + (s3*(2.0-tau))
  c = (tau*s) + (s2*(3.0-(2.0*tau))) + (s3*(tau-2.0))
  d = -(tau*s2) + (s3*tau)

  q[0] = (a*p_m2[0]) + (b*p_m1[0]) + (c*p[0]) + (d*p_1[0])
  q[1] = (a*p_m2[1]) + (b*p_m1[1]) + (c*p[1]) + (d*p_1[1])
  q[2] = (a*p_m2[2]) + (b*p_m1[2]) + (c*p[2]) + (d*p_1[2])

  return q


# simple catmull-rom interpoloation
def scri( xy, g ):

  v = [ 0, 0, 0, 0 ]

  v[0] = catmull_rom( xy[0], g[0][0], g[1][0], g[2][0], g[3][0] )
  v[1] = catmull_rom( xy[0], g[0][1], g[1][1], g[2][1], g[3][1] )
  v[2] = catmull_rom( xy[0], g[0][2], g[1][2], g[2][2], g[3][2] )
  v[3] = catmull_rom( xy[0], g[0][3], g[1][3], g[2][3], g[3][3] )

  r = catmull_rom( xy[1], v[0], v[1], v[2], v[3] )
  return r


def usage():
  print "produce gcode from source gcode and height map by interpolating z co-ordinates from height map"
  print "usage:"
  print "  -g <gcode file>      gcode file"
  print "  -m <height map>      height map"
  print "  [-z <threshold>]     z threshold (default to 0)"
  print "  [-h|--help]          help (this screen)"

gcode_file = None
height_map_file = None

z_threshold = 0.0

try:
  opts, args = getopt.getopt(sys.argv[1:], "m:g:z:", ["help", "output="])
except getopt.GetoptError, err:
  # print help information and exit:
  print str(err) # will print something like "option -a not recognized"
  usage()
  sys.exit(2)
output = None
verbose = False
for o, a in opts:
  if o == "-g":
    gcode_file = a
  elif o in ("-h", "--help"):
    usage()
    sys.exit()
  elif o == "-m":
    height_map_file = a
  elif o == "-z":
    z_threshold = float(a)
  else:
    assert False, "unhandled option"

#print gcode_file, height_map_file

grid = {}

gc = open( gcode_file, "r" )


x_pnt, y_pnt  = {}, {}

f = open( height_map_file, "r" )
for line in f:
  v = line.rsplit()
  k = str(float(v[0])) + ":" + str(float(v[1]))
  grid[k] = [ float(v[0]), float(v[1]), float(v[2]) ]
  x_pnt[v[0]] = float(v[0])
  y_pnt[v[1]] = float(v[1])
f.close()

x_pnt_list = sorted(x_pnt.values())
y_pnt_list = sorted(y_pnt.values())

del_x = float(x_pnt_list[1]) - float(x_pnt_list[0])
del_y = float(y_pnt_list[1]) - float(y_pnt_list[0])

s = "( x:"
for x in x_pnt_list:
  s += " " + str(x)
s += ")"
print s

s = "( y:"
for y in y_pnt_list:
  s += " " + str(y)
s += ")"
print s


print "( del_x", str(del_x), ", del_y", str(del_y), ")"


# closest to left
def get_list_index( p, a ):
  l = 0
  r = len(a)-1
  m = r/2
  while ( (r-l) > 1 ):
    if float(a[m]) == float(p):
      return m
    if float(a[m]) < float(p):
      l=m
    else:
      r=m
    m = l + ((r-l)/2)
  if float(a[r]) == float(p):
    return r
  return l 

def clamp(v, l, u):
  if v<l:
    return l
  if v>u:
    return u
  return v

for kv in grid.items():
  x, y = kv[0].rsplit(':')
  #print x, y, kv[1]


cur_x, cur_y, cur_z  = 0, 0, 0
z_pos = 'up'
z_threshold = 0.0

z_plunge = -0.002

for line in gc:
  l = line.rstrip('\n')
  m = re.match('^\s*\(', l)

  #print "( line: ", l, " )"
  if m:
    print l
    continue

  m = re.match('^\s*[gG]\s*(0*[01])[^\d]', l)
  if m:
    g01 = m.group(1)
    #print "g", g01, "match: ", l

    m = re.match('.*[xX]\s*(-?\d+(\.\d+)?)', l)
    if m:
      cur_x = m.group(1)
      #print "  got x match", cur_x

    m = re.match('.*[yY]\s*(-?\d+(\.\d+)?)', l)
    if m:
      cur_y = m.group(1)
      #print "  got y match", cur_y

    m = re.match('.*[zZ]\s*(-?\d+(\.\d+)?)', l)
    if m:
      cur_z = m.group(1)
      #print "  got z match", cur_z

      if ( float(cur_z) >= z_threshold ):
        #print "( z up )"
        z_pos = 'up'
      else:
        #print "( z down )"
        z_pos = 'down'

      #print "z_pos:", z_pos

    if (z_pos == 'up'):
      print l
    elif (z_pos == 'down'):
      x_ind = get_list_index( cur_x, x_pnt_list )
      y_ind = get_list_index( cur_y, y_pnt_list )

      subgrid = [ [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0] ]
      for i in range(0, 4):
        for j in range(0, 4):
          x_pos = clamp(x_ind + i - 1, 0, len(x_pnt_list)-1)
          x_val = x_pnt_list[ x_pos ]
            
          y_pos = clamp(y_ind + j - 1, 0, len(y_pnt_list)-1)
          y_val = y_pnt_list[ y_pos ]

          key = str(x_val) + ":" + str(y_val)
          val = grid[key]
          subgrid[i][j] = [ x_val, y_val, val[2] ]
          #print "#", subgrid[i][j]

      s_x = (float(cur_x) - float(x_pnt_list[x_ind]) ) / del_x
      s_y = (float(cur_y) - float(y_pnt_list[y_ind]) ) / del_y
      p = scri( [ s_x, s_y ], subgrid )
      interpolated_z = p[2]

      interpolated_z += z_plunge

      #x_formatted = "{0:.8f}".format(cur_x)
      #y_formatted = "{0:.8f}".format(cur_y)
      #z_formatted = "{0:.8f}".format(interpolated_z)
      x_f = float(cur_x)
      y_f = float(cur_y)


      #print "g" + g01, "x" + cur_x, "y" + cur_y, "z" + str(interpolated_z)
      print "g" + g01, "x{0:.8f}".format(x_f), "y{0:.8f}".format(y_f), "z{0:.8f}".format(interpolated_z)
      #print cur_x, cur_y, str(interpolated_z)
  else:
    print l


gc.close()




###################################
### TESTING
###################################


"""

random.seed(10000)

grid = {}

n_x = 5
n_y = 5

for x in range(0, n_x):
  for y in range(0, n_y):
    k = str(x) + ":" + str(y)
    grid[k] = [ 2.0*float(x), 2.0*float(y), random.random() + 1.0 ]

for y in range(0, n_y):
  k = "-1:" + str(y)
  kk = "0:" + str(y)
  grid[k] = [ 2.0*-1.0, 2.0*float(y), grid[kk][2] ]

  k = str(n_x) + ":" + str(y)
  kk =  str(n_x-1) + ":" + str(y)
  grid[k] = [ 2.0*float(n_x), 2.0*float(y), grid[kk][2] ]

for x in range(0, n_x):
  k =  str(x) + ":-1"
  kk = str(x) + ":0"
  grid[k] = [ 2.0*float(x), 2.0*-1.0, grid[kk][2] ]

  k =  str(x) + ":" + str(n_y)
  kk = str(x) + ":" + str(n_y-1)
  grid[k] = [ 2.0*float(x), 2.0*float(n_y), grid[kk][2] ]

grid[ "-1:-1" ]                     = [ 2.0*float(-1), 2.0*float(-1), grid[ "0:0" ][2] ]
grid[ "-1:" + str(n_y) ]            = [ 2.0*float(-1), 2.0*float(n_y), grid[ "0:" + str(n_y-1) ][2] ]
grid[ str(n_x) + ":-1" ]            = [ 2.0*float(n_x), 2.0*float(-1), grid[ str(n_x-1) + ":0" ][2] ]
grid[ str(n_x) + ":" + str(n_y) ]   = [ 2.0*float(n_x), 2.0*float(n_y), grid[ str(n_x-1) + ":" + str(n_y-1) ][2] ]
"""


"""
for x in range(-1, n_x+1):
  for y in range(-1, n_y+1):
    k = str(x) + ":" + str(y)
    v = grid[k]
    print "#", k
    print v[0], v[1], v[2]

sys.exit(0)
"""

"""
division = 8.0

### TEST
for x in range(0, n_x-1):
  for y in range(0, n_y-1):

    subgrid = [ [0,0,0,0], [0,0,0,0],[0,0,0,0],[0,0,0,0] ]
    for i in range(0, 4):
      for j in range(0, 4):
        kk = str(x + i - 1) + ":" + str(y + j - 1)
        subgrid[i][j] = grid[kk]


    xy = [0.0, 0.0]

    while xy[0] < 1.0:
      xy[1] = 0.0
      while xy[1] < 1.0:
        r = scri( xy, subgrid )


        #print xy[0], xy[1], r[0], r[1], r[2]
        print r[0], r[1], r[2]
        xy[1] += 1.0/division
      xy[0] += 1.0/division





sys.exit(0)


## FINE GRID 
finegrid = {}
x_pnt = {}
y_pnt = {}


for x in range(0, n_x-1):
  for y in range(0, n_y):

    k = str(x) + ":" + str(y)
    #print grid[k][0], grid[k][1], grid[k][2]

    cur = 0
    p = [0, 0, 0, 0]

    for xx in range( x-1, x+3 ):
      kk = str(xx) + ":" + str(y)
      p[cur] = grid[kk]
      cur += 1

    s_x = 0.0
    finegrid[ str(float(x)) + ":" + str(y) ] = grid[k]

    #print str(float(x)) + ":" + str(y)

    while s_x < 1.0:
      v = catmull_rom( s_x, p[0], p[1], p[2], p[3] )
      s_x += 1.0/division
      #print v[0], v[1], v[2]

      x_pnt[ str(v[0]) ] = str(v[0])

      finegrid[ str(v[0]) + ":" + str(y) ] = v

x_sorted = sorted(x_pnt.iteritems(), key=operator.itemgetter(1))

for i in range(1, len(x_sorted)-2):
  for y in range(1, n_y-2):
    print "#", x_sorted[i][0]

    k = str(x_sorted[i][0]) + ":" + str(y)
    #print finegrid[k][0], finegrid[k][1], finegrid[k][2]

    cur = 0
    p = [0, 0, 0, 0]

    for yy in range( y-1, y+3 ):
      kk = str(x_sorted[i][0]) + ":" + str(yy)
      p[cur] = finegrid[kk]
      cur += 1

    s_y = 0.0
    while s_y < 1.0:
      print "#", p[0], p[1], p[2], p[3]
      v = catmull_rom( s_y, p[0], p[1], p[2], p[3] )
      s_y += 1.0/division

      y_pnt[ str(v[0]) ] = str(v[0])
      print v[0], v[1], v[2]

"""
