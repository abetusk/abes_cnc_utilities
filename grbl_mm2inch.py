#!/usr/bin/python

import re
import sys

for line in sys.stdin:
  li = line.rstrip()
  l = re.compile("([xyzXYZ]\s*-?\d+\.?\d*)").split(li)

  s = ''
  for w in l:
    if s != '':
      s += ' '
    if re.compile("^[xyzXYZ]").match(w):
      m = re.match("([xyzXYZ])\s*(.*)", w)
      s += m.group(1)
      s += str( format( float(m.group(2)) / 25.4, 'f' ).rstrip('0').rstrip('.') )
    else:
      s += w

  print s


