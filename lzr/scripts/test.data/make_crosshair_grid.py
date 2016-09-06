#!/usr/bin/python


#N=20
#M=20

N=3
M=3

sx=10
sy=10

dx=6.36
dy=6.35

cxh_dx=0.5
cxh_dy=0.5

feed=500

# home
#
print "G28"

for n in range(N):
  for m in range(M):

    x = sx + n*dx
    y = sy + m*dy

    tx = x - cxh_dx
    ty = y

    print "G0", "X" + str(x-cxh_dx), "Y" + str(y)
    print "G1", "X" + str(x+cxh_dx), "Y" + str(y), "F" + str(feed)

    print "G0", "X" + str(x), "Y" + str(y-cxh_dy)
    print "G1", "X" + str(x), "Y" + str(y+cxh_dy), "F" + str(feed)

print "G0", "X" + str(sx), "Y" + str(sy)

    


