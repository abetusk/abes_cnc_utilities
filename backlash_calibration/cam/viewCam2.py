#!/usr/bin/python

import sys
import cv2

snap_fn = "snap.png"

if (len(sys.argv) != 2):
  print "provide video number"
  sys.exit(0)
              
cv2.namedWindow("webcam", 1)

video_number = int(sys.argv[1])
vc = cv2.VideoCapture(video_number)

while True:
  rval, frame = vc.read()
  cv2.imshow("webcam", frame)
  key = cv2.waitKey(30) & 0xff
  if (key == ord('q')) or (key == 27):
    break
  if (key == ord('s')):
    print "saving fram to", snap_fn
    cv2.imwrite(snap_fn, frame)


