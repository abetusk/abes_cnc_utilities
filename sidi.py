#!/usr/bin/python
#
# simple inverse distance interpolation

#!/usr/bin/python

import sys
import os
import numpy
import random

class sidi:

  def __init__(self, points_xyz):
    self.x = []
    self.y = []
    self.z = []
    self.point = []

    for xyz in points_xyz:
      self.x.append( xyz[0] )
      self.y.append( xyz[1] )
      self.z.append( xyz[2] )
      self.point.append( [ xyz[0], xyz[1] ] )

  def debug(self):

    print "## len(point):", len(self.point), "(", len(self.x), len(self.y), len(self.z), ")"
    for k in range(len(self.point)):
      #print "##", self.point[k]
      print "#", self.x[k], self.y[k], self.z[k]

  def f(self, pnt, e=2.0, eps=0.00001):

    dist = []

    R = 0.0
    for x,y in self.point:

      dx = float(pnt[0]-x)
      dy = float(pnt[1]-y)
      d = numpy.sqrt( dx*dx + dy*dy )

      if d <= eps:
        return x,y

      d_me = 1.0 / d**e

      #R += 1.0 / d**e
      #dist.append( d )
      R += d_me
      dist.append( d_me )

    interpolated_z = 0.0
    for k, d_me in enumerate(dist):
      #v = 1.0 / d**e
      interpolated_z += d_me * self.z[k] / R

    return interpolated_z

  def interpolate(self, x, y, e=2.0, eps=0.00001 ):

    if type(x) != list:
      return self.f( [x, y], e, eps )

    z_rop = []
    for k in range(len(x)):
      u = x[k]
      v = y[k]

      z_rop.append( self.f( [u,v], e, eps ) )

    return z_rop


pnts = []
n = 10
m = 15

sx = 0.0
sy = 0.0

w = float(n)
h = float(m)

for i in range(n):
  for j in range(m):
    x = sx + i + random.random()/2.0 - 0.5
    y = sy + j + random.random()/2.0 - 0.5
    z = random.random()
    pnts.append( [ x, y, z ] )


p = 0
for i in range(n):
  for j in range(m):
    print "#_ ", pnts[p][0], pnts[p][1], pnts[p][2]
    p+=1
  print "#_ "


si = sidi( pnts )

#si.debug()
#sys.exit(0)

n_sample = 40
m_sample = 40
for i in range(n_sample):
  for j in range(m_sample):
    x = sx + w*float(i)/float(n_sample)
    y = sy + h*float(j)/float(m_sample)
    print x, y, si.interpolate(x, y)

  print


