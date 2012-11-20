#!/usr/bin/python

"""
generate PCB resolution test

"""

import sys
import math
import numpy
import random

units = "inches"

# height steps are in .01 mm \approx .39 mil
# if ? is the variability of the copper
# and we're considering 1 oz/ft^2 copper (1.4 mil height)
# | depth | < 1.4 + .4 + ? = 1.8 + ? < 2 (hopefully)
z_depth = -0.002  
z_up = 0.01

def draw_rect( l ):
  #x0, y0, x1, y1 ):
  x0 = l[0]
  y0 = l[1]
  x1 = l[2]
  y1 = l[3]
  print "g1 z" + str(z_up)
  print "g0 x" + str(x0) + " y" + str(y0)
  print "g1 z" + str(z_depth)
  print "g1 x" + str(x0) + " y" + str(y1)
  print "g1 x" + str(x1) + " y" + str(y1)
  print "g1 x" + str(x1) + " y" + str(y0)
  print "g1 x" + str(x0) + " y" + str(y0)
  print "g1 z" + str(z_up)

def draw_line( l, break_segment_length = 0.1 ):
  #x0, y0, x1, y1 ):
  x0 = l[0]
  y0 = l[1]
  x1 = l[2]
  y1 = l[3]
  print "g1 z" + str(z_up)
  print "g0 x" + str(x0) + " y" + str(y0)
  print "g1 z" + str(z_depth)

  dx = x1 - x0
  dy = y1 - y0

  dl = math.sqrt( (dx*dx) + (dy*dy) ) 

  n_segment = dl / break_segment_length

  for v in numpy.linspace(0, dl, n_segment):
    x = ( (x1-x0)*v / dl ) + x0
    y = ( (y1-y0)*v / dl ) + y0
    print "g1 x" + str(x) + " y" + str(y)

  print "g1 x" + str(x1) + " y" + str(y1)
  print "g1 z" + str(z_up)

def draw_num_simple( num, x_start, y_start, height, width, space, break_segment = 0.1 ):
  #   .66666.
  #   4     5
  #   4     5
  #   4     5
  #   .33333.
  #   1     2
  #   1     2
  #   1     2
  #   .00000.
  seg = [ [ 0.0, 0.0, width, 0.0 ],                         # 0
          [ 0.0, 0.0, 0.0, height/2.0 ],                    # 1
          [ width, 0.0, width, height/2.0 ],                # 2
          [ 0.0, height/2.0, width, height/2.0 ],           # 3
          [ 0.0, height/2.0, 0.0, height ],                 # 4
          [ width, height/2.0, width, height ],             # 5
          [ 0.0, height, width, height ]                    # 6
          ]

  num_seg = [ [ 0, 2, 5, 6, 4, 1 ],  # 0
              [ 2, 5],               # 1
              [ 0, 1, 3, 5, 6 ],     # 2
              [ 0, 2, 3, 5, 6 ],     # 3
              [ 2, 3, 4, 5 ],        # 4
              [ 0, 2, 3, 4, 6],      # 5
              [ 0, 2, 3, 4, 6, 1],   # 6
              [ 2, 5, 6 ],           # 7
              [ 0, 1, 4, 6, 5, 2, 3], # 8
              [ 2, 3, 4, 6, 5]      # 9
              ]

  if num == 0:
    for pos in num_seg[0]:
      l = seg[ pos ]
      draw_line( [ l[0] + x_start, l[1] + y_start, l[2] + x_start, l[3] + y_start ], break_segment )
    return

  s = ''
  while num > 0:
    digit = num % 10
    s = str(digit) + s
    num /= 10

  for c in s:
    digit = int(c)

    for pos in num_seg[digit]:
      l = seg[ pos ]
      draw_line( [ l[0] + x_start, l[1] + y_start, l[2] + x_start, l[3] + y_start ], break_segment )

    x_start += width + space



def draw_hor_test( pitch, x_start, y_start, length, n_lines, n_dashes, break_segment_length = 0.1 ):

  x_offset = length / float(n_dashes + 1)
  segments = []

  for n in range(n_lines + 1):

    prev_x = x_start
    cur_y = y_start + ( pitch * float(n) )

    for m in range(1, n_dashes + 1):

      final_x = x_start + ( float(m) * x_offset )
      final_y = cur_y

      segments.append( [ prev_x, cur_y, final_x, cur_y ] )

      prev_x = final_x


  p = range(0, len(segments))
  while len(p) > 0:
    rand_pos = random.randrange(0, len(p))
    pos = p.pop(rand_pos)

    seg = segments.pop(rand_pos)

    cur_x = seg[0]
    cur_y = seg[1]
    final_x = seg[2]
    final_y = seg[3]

    n_segment = int( abs((final_x - cur_x) / break_segment_length) ) + 1

    print "g1 z" + str(z_up)
    print "g0 x" + str(cur_x), "y", str(cur_y)
    print "g1 z" + str(z_depth)

    prev_x = cur_x
    for x in numpy.linspace(cur_x, final_x, n_segment):
      print "g1 x" + str(x), "y" + str(cur_y)
    print "g1 x" + str(final_x), "y" + str(cur_y)

    print "g1 z" + str(z_up)


def draw_ver_test( pitch, x_start, y_start, length, n_lines, n_dashes, break_segment_length = 0.1 ):

  y_offset = length / float(n_dashes + 1)
  segments = []

  for n in range(n_lines + 1):

    prev_y = y_start
    cur_x = x_start + ( pitch * float(n) )

    for m in range(1, n_dashes + 1):

      final_x = cur_x
      final_y = y_start + ( float(m) * y_offset )

      segments.append( [ cur_x, prev_y, cur_x, final_y] )

      prev_y = final_y


  p = range(0, len(segments))
  while len(p) > 0:
    rand_pos = random.randrange(0, len(p))
    pos = p.pop(rand_pos)

    seg = segments.pop(rand_pos)

    cur_x = seg[0]
    cur_y = seg[1]
    final_x = seg[2]
    final_y = seg[3]

    n_segment = int( abs((final_y - cur_y) / break_segment_length) ) + 1

    print "g1 z" + str(z_up)
    print "g0 x" + str(cur_x), "y", str(cur_y)
    print "g1 z" + str(z_depth)

    prev_y = cur_y
    for y in numpy.linspace(cur_y, final_y, n_segment):
      print "g1 x" + str(cur_x), "y" + str(y)
    print "g1 x" + str(cur_x), "y" + str(final_y)

    print "g1 z" + str(z_up)


  
#pitches_mil = [ 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 ]
#pitches_mil = [ 5, 6, 7, 8, 9, 10, 11, 12 ]
#pitches_mil = [ 13, 14, 15, 16, 17, 18, 19, 20 ]
pitches_mil = [ 20, 20, 20, 20, 20, 20, 20, 20 ]

random.seed(100)

n_lines = 10
n_dashes = 3
length = 0.5
num_size = 0.125
num_space = 0.05

start_x = 0.0
start_y = 0.0

break_segment = 0.1

print "g20"
print "( g0 f100 )"
print "( g1 f20 )"

#pitch = 20.0 / 1000.0
#pitch_mil = int(pitch * 1000.0)

count=0
count_vertical = 0
#count_mod = 4
count_mod = 2

###DEBUG
#pitch = float(pitches_mil[0]) / 1000.0
#draw_hor_test( pitch, 0.0, 0.0, length, n_lines, n_dashes, break_segment )
#sys.exit(0)
###DEBUG

for pitch_mil in pitches_mil:

  pitch = float(pitch_mil) / 1000.0

  print
  print "( vertical test block: pitch", str(pitch_mil), ", start_x", str(start_x), ", start_y", str(start_y), ", length", str(length), ", n_lines", str(n_lines), ", break_segment", str(break_segment) , ")"
  draw_ver_test( pitch, start_x, start_y, length, n_lines, n_dashes, break_segment )

  start_x += (float(n_lines) * pitch) + 0.1

  print
  print "( horizontal test block: pitch", str(pitch_mil), ", start_x", str(start_x), ", start_y", str(start_y), ", length", str(length), ", n_lines", str(n_lines), ", break_segment", str(break_segment), ")"
  draw_hor_test( pitch, start_x, start_y, length, n_lines, n_dashes, break_segment )

  print
  print "( draw number:", str(pitch_mil), ")"
  draw_num_simple( pitch_mil, start_x, start_y + length - num_size, num_size, num_size, num_space, break_segment )

  start_x += length + 0.1

  count += 1
  if ( (count % count_mod ) == 0 ):
    count_vertical += 1
    start_y = float(count_vertical * (length + 0.1) )
    start_x = 0.0



