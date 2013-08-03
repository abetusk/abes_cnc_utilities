#!/usr/bin/python
#
# remember to setup path properly, for example:
# export $PYTHONPATH="$PTYHONPATH:../.."
#

import sys
import numpy
import cv2

import grbl

gCurAxis = 'x'

gCurPos = 0
gMaxPos = 0
gMinPos = 0

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

homed = False
while (!homed):

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
    print "error, total count < 1"
    sys.exit(0)

  gPercent = float(gBlackCount) / float(gTotCount)

  # if we've reached the end stop
  if ( gBlackCount > gEndStopThresholdInt ):
    if (gVerboseFlag):
      print "end stop reached"
    homed = True
  else:
    if (gVerboseFlag):
      print "end stop not reached"
  
  if (gVerboseFlag):
    print "black pixel count:", str(gBlackCount), " white pixel count:", str(gWhiteCount), "(", str(gPercent), ")"

  #cv2.imwrite("out.png", frame_threshold)



  if (gShowWindowFlag):
    cv2.imshow("webcam", frame_threshold)
    cv2.waitKey(0)



  if (gVerboseFlag):
    print "done, output in out.png"

