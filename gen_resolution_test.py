#!/usr/bin/python

"""
generate PCB resolution test

"""

import sys
import math
import numpy

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

num_height = .35
def draw_num( num, x_start, y_start ):

  # use a big trace_width and clearance to make sure it's visible
  h_rect_x = [ 0.04, 0.12 ]
  h_rect_y = [ 0.0 , 0.20 ]

  v_rect_x = [ 0.0 , 0.20 ]
  v_rect_y = [ 0.04, 0.12 ]

  seg = [ [ h_rect_x[0], h_rect_y[0], h_rect_x[1], h_rect_y[1] ],
          [ v_rect_x[0], v_rect_y[0], v_rect_y[1], v_rect_y[1] ],
          [ v_rect_x[0] + .14, v_rect_y[0], v_rect_x[1] + .14, v_rect_y[1] ],
          [ h_rect_x[0], h_rect_y[0] + .14, h_rect_x[1], h_rect_y[1] + .14 ],
          [ v_rect_x[0], v_rect_y[0] + .18, v_rect_x[1], v_rect_y[1] + .18 ],
          [ v_rect_x[0] + .14, v_rect_y[0] + .18, v_rect_x[1] + .14, v_rect_y[1] + .18],
          [ h_rect_x[0], h_rect_y[0] + .28, h_rect_x[1], h_rect_y[1] + .28 ] ]

  num_seg = [ [ 1, 0, 2, 5, 6, 4 ],  # 0
              [ 2, 5],               # 1
              [ 0, 2, 3, 4, 6 ],     # 2
              [ 0, 2, 3, 5, 6 ],     # 3
              [ 1, 3, 2, 5 ],        # 4
              [ 0, 1, 3, 5, 6],      # 5
              [ 0, 1, 3, 5, 6, 4],   # 6
              [ 0, 2, 5 ],           # 7
              [ 0, 1, 2, 3, 4, 6, 5], # 8
              [ 2, 0, 1, 3, 5]      # 9
              ]

  while ( num > 0 ):
    digit = num % 10
    num /= 10

    for pos in num_seg[digit]:
      draw_rect( seg[ pos ] )


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
#  while ( num > 0 ):
#    digit = num % 10
#    num /= 10

    for pos in num_seg[digit]:
      l = seg[ pos ]
      draw_line( [ l[0] + x_start, l[1] + y_start, l[2] + x_start, l[3] + y_start ], break_segment )

    x_start += width + space



def draw_test( tool_offset, trace_width, clearance, x_start, y_start, width_length, width, height_length, height, n_lines ):

  dx = trace_width + clearance
  dy = trace_width + clearance

  pitch = trace_width + clearance

  h_start = width - width_length

  for l in range(n_lines):
    cur_x = x_start + (pitch*float(l)) - tool_offset
    cur_y = y_start 


    print "g1 z" + str(z_up)
    print "g0 x" + str(cur_x), "y" + str(cur_y)

    print "g1 z" + str(z_depth)

    cur_y = y_start + height_length 
    print "g1 x" + str(cur_x), "y" + str(cur_y)

    cur_x = x_start + width_length
    cur_y = y_start + height + tool_offset - (pitch * float(l))
    print "g1 x" + str(cur_x), "y" + str(cur_y)

    cur_x = x_start + width + tool_offset
    print "g1 x" + str(cur_x), "y" + str(cur_y)

    cur_y -= (2.0 * tool_offset) + trace_width
    print "g1 x" + str(cur_x), "y" + str(cur_y)

    cur_x = x_start + width_length
    print "g1 x" + str(cur_x), "y" + str(cur_y)

    cur_x = x_start + (pitch * float(l)) + tool_offset + trace_width
    cur_y = y_start + height_length
    print "g1 x" + str(cur_x), "y" + str(cur_y)

    cur_y = y_start - tool_offset
    print "g1 x" + str(cur_x), "y" + str(cur_y)

    cur_x = x_start + (pitch*float(l)) - tool_offset
    print "g1 x" + str(cur_x), "y" + str(cur_y)

def draw_hor_test( pitch, x_start, y_start, length, n_lines, break_segment_length = 0.1 ):

  for n in range(n_lines):
    if ( n % 2 ):
      cur_x = x_start + length
      cur_y = y_start + ( pitch * float(n) )
    else:
      cur_x = x_start
      cur_y = y_start + ( pitch * float(n) )

    print "g1 z" + str(z_up)
    print "g0 x" + str(cur_x), "y" + str(cur_y)

    print "g1 z" + str(z_depth)

    final_x = cur_x
    if (n % 2):
      final_x -= length
    else:
      final_x += length

    n_segment = int( abs((final_x - cur_x) / break_segment_length) ) + 1

    for x in numpy.linspace(cur_x, final_x, n_segment):
      print "( hor, x", str(x), ", y", str(cur_y), ")"
      print "g1 x" + str(x), "y" + str(cur_y)
    print "g1 x" + str(final_x), "y" + str(cur_y)

  # outline the traces
  print "g1 z" + str(z_up)
  print "g0 x" + str(x_start), "y" + str(y_start)

  print "g1 z" + str(z_depth)
  print "g1 x" + str(x_start), "y" + str(y_start + (pitch * (n_lines - 1)))

  print "g1 z" + str(z_up)
  print "g0 x" + str(x_start + length), "y" + str(y_start + (pitch * (n_lines - 1)))

  print "g1 z" + str(z_depth)
  print "g1 x" + str(x_start + length), "y" + str(y_start)

  print "g1 z" + str(z_up)
  print "g1 x" + str(x_start), "y" + str(y_start)


def draw_ver_test( pitch, x_start, y_start, length, n_lines, break_segment_length = 0.1 ):

  for n in range(n_lines):

    if (n % 2):
      cur_x = x_start + ( pitch * float(n) )
      cur_y = y_start + length
    else:
      cur_x = x_start + ( pitch * float(n) )
      cur_y = y_start

    print "g1 z" + str(z_up)
    print "g0 x" + str(cur_x), "y" + str(cur_y)

    print "g1 z" + str(z_depth)

    final_y = cur_y
    if (n % 2):
      final_y -= length
    else:
      final_y += length

    n_segment = int( abs((final_y - cur_y) / break_segment_length) ) + 1
    print "( ver, final_y", str(final_y), ", cur_y", str(cur_y), ", break_segment_length", str(break_segment_length), ", n_segment", str(n_segment), ")"

    for y in numpy.linspace(cur_y, final_y, n_segment):
      print "( ver , x", str(cur_x), ", y", str(y), ")"
      print "g1 x" + str(cur_x), "y" + str(y)
    print "g1 x" + str(cur_x), "y" + str(final_y)

  # outline the traces
  print "g1 z" + str(z_up)
  print "g0 x" + str(x_start), "y" + str(y_start)

  print "g1 z" + str(z_depth)
  print "g1 x" + str(x_start + (pitch * (n_lines - 1))), "y" + str(y_start)

  print "g1 z" + str(z_up)
  print "g0 x" + str(x_start + (pitch * (n_lines - 1))), "y" + str(y_start + length)

  print "g1 z" + str(z_depth)
  print "g1 x" + str(x_start), "y" + str(y_start + length)

  print "g1 z" + str(z_up)
  print "g0 x" + str(x_start), "y" + str(y_start)

pitches_mil = [ 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 ]

n_lines = 10
length = 0.5
num_size = 0.125
num_space = 0.05

start_x = 0.0
start_y = 0.0

break_segment = 0.1

print "g0 f100"
print "g1 f100"

#pitch = 20.0 / 1000.0
#pitch_mil = int(pitch * 1000.0)

count=0
count_vertical = 0
count_mod = 4

for pitch_mil in pitches_mil:

  pitch = float(pitch_mil) / 1000.0

  draw_ver_test( pitch, start_x, start_y, length, n_lines, break_segment )

  start_x += (float(n_lines) * pitch) + 0.1
  draw_hor_test( pitch, start_x, start_y, length, n_lines, break_segment )

  draw_num_simple( pitch_mil, start_x, start_y + length - num_size, num_size, num_size, num_space, break_segment )

  start_x += length + 0.1

  count += 1
  if ( (count % count_mod ) == 0 ):
    count_vertical += 1
    start_y = float(count_vertical * (length + 0.1) )
    start_x = 0.0

sys.exit(0)




# a angle
#
#          l
#        ------
#        |   /
# z mil  |  /
#        |a/
#        |/
#
#  tan( a * pi / 180 ) = l / 2 -> l = 2 * tan( a * pi / 180 )
#  

angle = 20.0
tool_offset = -z_depth * math.tan( math.pi * (angle/2.0) / 180.0 ) 
tool_width = 2.0 * tool_offset

if units == "inches":
  pass
elif units == "mm":
  pass


trace_width = 20.0 / 1000.0
clearance = 20.0 / 1000.0

trace_width_mil = int(trace_width * 1000.0)
clearance_mil = int(clearance * 1000.0)

x = 0.0
y = 0.0

# everything in mm
#height_length = 5.0
#height = 10.0
#width_length = 5.0
#width = 10.0

height_length = 0.25
height = 0.5
width_length = 0.25
width = 0.5

pitch = trace_width + clearance

print "( tool angle: ", angle, " degrees)"
print "( tool_offset in ", units, ":", tool_offset, ")"
print "( tool_width in ", units, ":", tool_width , ")"
print "( trace_width in ", units, ":", trace_width, ")"
print "( trace_width_mil :", trace_width_mil, ")"
print "( clearance in ", units, ":", clearance , ")"
print "( clearance_mil :", clearance_mil , ")"
print "( height_length in ", units, ":", height_length, ")"
print "( height in ", units, ":", height , ")"
print "( width_length in ", units, ":", width_length, ")"
print "( width in ", units, ":", width , ")"
print "( x,y in ", units, ":", x, y, ")"

print "g0 f100"
print "g1 f100"

#for i in range(0, 10):
#  draw_num_simple( i, float(i)*20.0, 0.0, 10.0, 10.0  )

#draw_num_simple( 9876543210, 0.0, 0.0, height_length, width_length, 2  )
#draw_num_simple( trace_width_mil, height, width, 10.0, 10.0  )
#draw_num_simple( clearance_mil, height, width, 10.0, 10.0  )
shift = 1.0

tw_mil = [ 5, 10, 15, 20 ]
clr_mil = [ 5, 10 ]

#tw_mil = [ 5, 10, 15, 20 ]
#clr_mil = [ 15, 20 ]

#tw_mil = [ 5, 10, 15, 20 ]
#clr_mil = [ 8 ]

#tw_mil = [ 8 ]
#clr_mil = [ 5, 8, 10, 15, 20 ]

## all
#tw_mil = [ 5, 10, 15, 20 ]
#clr_mil = [ 5, 8, 10, 15, 20 ]

x_mod = 4
x_counter = 0

y = 0.0
x = 0.0
for clearance_mil in clr_mil:

  for trace_width_mil in tw_mil:
    trace_width = float(trace_width_mil) / 1000.0
    clearance = float(clearance_mil) / 1000.0

    draw_test( tool_offset, trace_width, clearance, x, y, width_length, width,height_length, height,  5 )
    draw_num_simple( trace_width_mil , x + width_length, y + height_length/2.0, (width_length/2.0) - 0.01, (height_length/2.0) - 0.01, .1  )
    draw_num_simple( clearance_mil, x + width_length + (width_length/2.0), y, (width_length/2.0) - 0.01, (height_length/2.0) - 0.01, .1  )

    x_counter += 1
    if ( (x_counter % x_mod) == 0):
      y += shift
      x = 0.0
    else:
      x += shift

