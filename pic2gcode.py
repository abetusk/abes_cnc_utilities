#!/usr/bin/python

import sys
import Image

if len(sys.argv) < 2:
  sys.exit("Provide image file to convert")


im = Image.open(sys.argv[1])

a = im.size

print '( got height', a[0], 'width', a[1], ")"

bottom_pixel = im.getpixel( (0, 0) )

min_x = a[0]
min_y = a[1]
max_x = 0
max_y = 1

for y in range(0, a[1]-1):
  for x in range(0, a[0]-1):
    p = im.getpixel( (x, y) )
    if (p != bottom_pixel):
      if (x < min_x):
        min_x = x
      if (x > max_x):
        max_x = x
      if (y < min_y):
        min_y = y
      if (y > max_y):
        max_y = y

print "( max", max_x, max_y, "min", min_x, min_y, ")"

bound_lu = (min_x - 20, min_y - 20)
bound_rd = (max_x + 20, max_y + 20)

#print bound_lu, bound_rd


units = "inches"
bit_size = 0.01
width_units = 3.0
pixel_per_unit = (max_x - min_x) / width_units
height_units = (max_y - min_y) / pixel_per_unit


print "( x[min,max] [", min_x, max_x, "] [", str(max_x-min_x), "], y[min,max] [", min_y, max_y, "] [", str(max_y-min_y), "] )"
print "( pixel_per_unit", pixel_per_unit, ")"
print "( width, height [in", units, "]", width_units, height_units, ")"

pixel_per_bit = bit_size * pixel_per_unit

print "( pixel_per_bit", pixel_per_bit, " )"

stride = int(0.9 * pixel_per_bit)
if (stride < 1):
  stride = 1

print "( increments in", stride, "pixel increments )"

x0 = min_x - 2*stride
x1 = max_x + 2*stride
y0 = min_y - 2*stride
y1 = max_y + 2*stride

z_up = 0.25
z_zero = 0.0
z_down = -0.05

if units == "inches":
  print "g20"
elif units == "mm":
  print "g21"

print "g0 f100"
print "g1 f50"

start_left = 1
cur_x = 0.0
cur_y = 0.0

for y in range(y1, y0, -stride):
  zpos = 0.0
  print "g0 z" + str(z_up)
  #print "g0 x" + str( (x - x0) / pixel_per_unit ) + " y0"
  print "g0 x" + str(cur_x) + " y" + str( (y1 - y) / pixel_per_unit ) 

  z_state = "up"

  if (start_left):

    for x in range(x0, x1, stride):
      p = im.getpixel( (x, y) )
      if ( p != bottom_pixel ):
        #(x_unit, y_unit) = ( (x - x0) / pixel_per_unit, (y - y0) / pixel_per_unit )
        x_unit, y_unit =  (x - x0) / pixel_per_unit, (y1 - y) / pixel_per_unit 

        cur_x = x_unit
        cur_y = y_unit

        start_left = 0

        if z_state == "up":
          print "g0 x" + str(x_unit) + " y" + str(y_unit)
          print "g1 z" + str(z_down)
        elif z_state == "down":
          #print "g1 x" + str(x_unit) + " y" + str(y_unit)
          pass

        z_state = "down"

      elif z_state == "down":
        print "g1 x" + str(cur_x) + " y" + str(cur_y)
        print "g1 z" + str(z_up)
        z_state = "up"

  else:

    for x in range(x1, x0, -stride):
      p = im.getpixel( (x, y) )
      if ( p != bottom_pixel ):
        #(x_unit, y_unit) = ( (x - x0) / pixel_per_unit, (y - y0) / pixel_per_unit )
        x_unit, y_unit =  (x - x0) / pixel_per_unit, (y1 - y) / pixel_per_unit 

        cur_x = x_unit
        cur_y = y_unit

        start_left = 1

        if z_state == "up":
          print "g0 x" + str(x_unit) + " y" + str(y_unit)
          print "g1 z" + str(z_down)
        elif z_state == "down":
          #print "g1 x" + str(x_unit) + " y" + str(y_unit)
          pass

        z_state = "down"

      elif z_state == "down":
        print "g1 x" + str(cur_x) + " y" + str(cur_y)
        print "g1 z" + str(z_up)
        z_state = "up"








