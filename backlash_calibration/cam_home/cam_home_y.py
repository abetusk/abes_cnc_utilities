#!/usr/bin/python
#
# use camera to home x axis
# assumes the 'end stop' is an all black
#  region on the strip that the camera points to
#
# bails out if we've gone past the gMinPos

import sys
import numpy
import cv2
import time

import grbl

grbl.setup()


gCurAxis = 'y'

gPosCur = 0
gPosMin = -10
gPosDel  = [-1, -.1, -0.01]
gPosDelLevel = 0

gShowWindowFlag = True
#gShowWindowFlag = False
gVerboseFlag  = True

gWidth = 640.0
gHeight = 480.0

if ( len(sys.argv) < 2 ):
  print "provide video device number"
  sys.exit(0)

video_number = int(sys.argv[1])

vc = cv2.VideoCapture(video_number)
if not vc.isOpened():
  print "failed to open video device", str(video_number)
  sys.exit(0)

if (gShowWindowFlag):
  cv2.namedWindow("webcam", 1)

if (gVerboseFlag):
  print "starting..."

flush_count=10
for i in range(flush_count):
  rval, frame = vc.read()
  if (gShowWindowFlag):
    cv2.imshow("webcam", frame)
    cv2.waitKey(1)

iteration_count = 0
homed = False
while (not homed):

  # read frame from camera
  flush_count=5
  for i in range(flush_count):
    rval, frame = vc.read()

  rval, frame = vc.read()
  frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


  # put through threshold
  # I'm finding the OTSU grabs too much white noise when in the black region.
  # I'm finding a hard coded threshold and tweeaking the light levels works better.
  #(thresh, frame_threshold) = cv2.threshold(frame_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
  (thresh, frame_threshold) = cv2.threshold( frame_gray, 127, 255, cv2.THRESH_BINARY )
   
  # calculate historgram, find number of white pixels and number of black pixels
  hist_item = cv2.calcHist( [frame_threshold], [0], None, [256], [0,256] )

  gBlackCount = hist_item[0]
  gWhiteCount = hist_item[255]
  gTotCount = gBlackCount + gWhiteCount
  gEndStopThreshold = 0.98
  gEndStopThresholdInt = int(gEndStopThreshold * float(gTotCount))

  if (gTotCount < 1):
    print "# ERROR! gTotCount< 1"
    sys.exit(0)

  gPercent = float(gBlackCount) / float(gTotCount)

  if (gVerboseFlag):
    print "# black pixel count:", str(gBlackCount), " white pixel count:", str(gWhiteCount), "(", str(gPercent), ")"

  if (gShowWindowFlag):
    cv2.imshow("webcam", frame_threshold)
    cv2.waitKey(1)


  # if we've reached the end stop
  if ( gBlackCount > gEndStopThresholdInt ):
    if (gVerboseFlag):
      print "# end stop reached"
    homed = True
    continue
  else:
    if (gVerboseFlag):
      print "# end stop not reached"
  
  iteration_count += 1
  if (gVerboseFlag):
    print "# iteration_count:", str(iteration_count)
    print "# gPosCur:", str(gPosCur)

  if (iteration_count > 10):
    homed = True

  gPosCur += 0.1
  grbl.send_command( "g1y" + str(gPosCur) )
  

if (homed):
  if (gVerboseFlag):
    print "now homed"
else:
  print "# NOT HOMED"



