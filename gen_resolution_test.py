#!/usr/bin/python

"""
generate PCB resolution test

"""

import math

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

def draw_line( l ):
  #x0, y0, x1, y1 ):
  x0 = l[0]
  y0 = l[1]
  x1 = l[2]
  y1 = l[3]
  print "g1 z" + str(z_up)
  print "g0 x" + str(x0) + " y" + str(y0)
  print "g1 z" + str(z_depth)
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


def draw_num_simple( num, x_start, y_start, height, width, space ):
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
      draw_line( [ l[0] + x_start, l[1] + y_start, l[2] + x_start, l[3] + y_start ] )
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
      draw_line( [ l[0] + x_start, l[1] + y_start, l[2] + x_start, l[3] + y_start ] )

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

print "( tool_offset in ", units, ":", tool_offset, ")"
print "( tool_width in ", units, ":", tool_width , ")"
print "( trace_width in ", units, ":", trace_width, ")"
print "( clearance in ", units, ":", clearance , ")"
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

tw_mil = [ 5, 8, 10, 15, 20 ]
#clr_mil = [ 5, 8, 10 ]
clr_mil = [ 15, 20]
#clr_mil = [ 5, 8, 10, 15 ]
#clr_mil = [ 5, 8, 10, 15, 20 ]

y = 0.0
for clearance_mil in clr_mil:

  x = 0.0
  for trace_width_mil in tw_mil:
    trace_width = float(trace_width_mil) / 1000.0
    clearance = float(clearance_mil) / 1000.0

    draw_test( tool_offset, trace_width, clearance, x, y, width_length, width,height_length, height,  5 )
    draw_num_simple( trace_width_mil , x + width_length, y + height_length/2.0, (width_length/2.0) - 0.01, (height_length/2.0) - 0.01, .1  )
    draw_num_simple( clearance_mil, x + width_length + (width_length/2.0), y, (width_length/2.0) - 0.01, (height_length/2.0) - 0.01, .1  )

    x += shift

  y += shift


