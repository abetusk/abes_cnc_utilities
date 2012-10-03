#!/usr/bin/python

import re
import sys

for line in sys.stdin:
  li = line.rstrip()
  l = re.compile("(\s*-?\d+\.?\d*)").split(li)

  s = ''
  for w in l:
    if s != '':
      s += ' '
    if re.match("^(\s*-?\d+\.?\d*)", w):
      m = re.match("^(\s*-?\d+\.?\d*)", w)
      s += str( format( float(m.group(1)) * 25.4, 'f').rstrip('0').rstrip('.') )
    else:
      s += w

  print s


