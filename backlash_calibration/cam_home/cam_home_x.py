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

import serial



grbl_dev = "/dev/ttyUSB0"
grbl_baud = 9600
grbl_serial = serial.Serial(grbl_dev, grbl_baud)



gCurAxis = 'x'

gPosCur = 0
gPosMin = -10
gPosDel  = [-1, -.1, -0.01]
gPosDelLevel = 0

gShowWindowFlag = True
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

iteration_count = 0
homed = False
while (not homed):

  # read frame from camera
  rval, frame = vc.read()
  frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

  # put through threshold
  (thresh, frame_threshold) = cv2.threshold(frame_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

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

  # if we've reached the end stop
  if ( gBlackCount > gEndStopThresholdInt ):
    if (gVerboseFlag):
      print "# end stop reached"
    homed = True
  else:
    if (gVerboseFlag):
      print "# end stop not reached"
  
  if (gVerboseFlag):
    print "# black pixel count:", str(gBlackCount), " white pixel count:", str(gWhiteCount), "(", str(gPercent), ")"

  #cv2.imwrite("out.png", frame_threshold)
  #if (gVerboseFlag):
  #  print "done, output in out.png"

  if (gShowWindowFlag):
    cv2.imshow("webcam", frame_threshold)
    cv2.waitKey(0)

  iteration_count += 1
  if (gVerboseFlag):
    print "# iteration_count:", str(iteration_count)

  if (iteration_count > 10):
    homed = True

if (homed):
  if (gVerboseFlag):
    print "now homed"
else:
  print "# NOT HOMED"



