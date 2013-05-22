#!/usr/bin/python

import sys
import cv2

if (len(sys.argv) != 2):
  print "provide video number"
  sys.exit(0)
              
cv2.namedWindow("webcam", 1)

video_number = int(sys.argv[1])
vc = cv2.VideoCapture(video_number)

while True:
  rval, frame = vc.read()
  cv2.imshow("webcam", frame)
  if (cv2.waitKey(1) > 0):
    break

