#!/usr/bin/python
#

import cv
import sys

if (len(sys.argv) != 2):
  print "provide video number"
  sys.exit(0)

video_number = int(sys.argv[1])

cv.NamedWindow("webcam", 1)

cam0 = cv.CaptureFromCAM(video_number)

while True:
  feed = cv.QueryFrame(cam0)
  cv.ShowImage("webcam", feed)
  if (cv.WaitKey(1) > 0):
    break;

