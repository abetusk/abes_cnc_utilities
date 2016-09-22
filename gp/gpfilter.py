#!/usr/bin/python

from __future__ import print_function
import os, sys, re, getopt, math

#MIN_PERIM = -1.0
MIN_PERIM = -1.0
MAX_PERIM = -1.0

def usage():
  print("usage:")
  print("  [-i infile]              input file ('-' for stdin, default)")
  print("  [-o outfile]             output file ('-' for stdout, default)")
  print("  [-m min_perim]           minimum perimeter")
  print("  [-M max_perim]           maximum perimeter")

def len2d(p, q):
  a = (p[0]-q[0])*(p[0]-q[0])
  b = (p[1]-q[1])*(p[1]-q[1])
  return math.sqrt(a + b)

def ingest_egest(ifp, ofp):
  polygons = []
  polygon = []

  prev_pnt = []
  perim = 0.0
  line_no=0
  #for line in sys.stdin:
  for line in ifp:
    line = line.strip()
    line_no += 1

    if (len(line)==0) or (line == ""):
      if len(polygon)>0:

        if len(prev_pnt)>1:
          perim += len2d(prev_pnt, [x,y])

        if (perim > MIN_PERIM) and ((MAX_PERIM < 0.0) or (perim < MAX_PERIM)):
          polygons.append(polygon)
      perim = 0.0
      prev_pnt = []
      polygon = []
      continue

    if line[0]=='#': continue

    r = re.split(r'\s+', line)

    if len(r)!=2:
      print("Error on line " + str(line_no) + ": number of arguments is not 2 (" + line + ")", file=sys.stderr)
      os.exit(1)

    try:
      x = float(r[0])
      y = float(r[1])
    except Exception, e:
      print(e, file=sys.stderr)
      os.exit(1)

    if len(prev_pnt)>0:
      perim += len2d(prev_pnt, [x,y])

    prev_pnt = [x,y]
    polygon.append([x,y])

  for p in polygons:
    if len(p)==0: continue

    for xy in p:
      print("{:.10f}".format(xy[0]), "{:.10f}".format(xy[1]), file=ofp)
    print(file=ofp)


def main(argv):
  global MIN_PERIM, MAX_PERIM
  ifp = sys.stdin
  ofp = sys.stdout
  try:
    opts,args = getopt.getopt(argv,"hi:o:m:M:",["ifile=", "ofile="])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt == "-h":
      usage()
      sys.exit()
    elif opt in ("-i", "--ifile"):
      ifn = arg
      if ifn != "-":
        ifp = open(ifn,"r")
    elif opt in ("-o", "--ofile"):
      ofn = arg
      if ofn != "-":
        ofp = open(ofn, "w")

    elif opt in ("-m", "--min-prefix"):
      MIN_PERIM = float(arg)

    elif opt in ("-M", "--max-prefix"):
      MAX_PERIM = float(arg)

  ingest_egest(ifp, ofp)

  if ifp!=sys.stdin:
    ifp.close()

  if ofp!=sys.stdout:
    ofp.close()




if __name__ == "__main__":
  main(sys.argv[1:])
