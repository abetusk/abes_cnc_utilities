#!/usr/bin/python

from __future__ import print_function
import os, sys, re, getopt

pfx = ""
sfx_rapid = ""
sfx_slow = ""
sfx = ""

def usage():
  print("usage:")
  print("  [-i infile]              input file ('-' for stdin, default)")
  print("  [-o outfile]             output file ('-' for stdout, default)")
  print("  [--pfx str]              string to print before any processing")
  print("  [--sfx-rapid str]        string to append at end of rapid motion (G0)")
  print("  [--sfx-slow str]         string to append at end of slow motion (G1)")
  print("  [--sfx str]              string to print after any processing")

def ingest_egest(ifp, ofp):
  polygons = []
  polygon = []

  print(pfx, file=ofp)

  line_no=0
  #for line in sys.stdin:
  for line in ifp:
    line = line.strip()
    line_no += 1

    if (len(line)==0) or (line == ""):
      if len(polygon)>0:
        polygons.append(polygon)
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

    polygon.append([x,y])

  for p in polygons:
    if len(p)==0: continue

    print("G0", "X" + "{:.10f}".format(p[0][0]), "Y" + "{:.10f}".format(p[0][1]), sfx_rapid, file=ofp)
    for xy in p:
      print("G1", "X" + "{:.10f}".format(xy[0]), "Y" + "{:.10f}".format(xy[1]), sfx_slow, file=ofp)
    print("G1", "X" + "{:.10f}".format(p[0][0]), "Y" + "{:.10f}".format(p[0][1]), sfx_slow, file=ofp)
    print(file=ofp)

  print(sfx, file=ofp)


def main(argv):
  global sfx_slow, sfx_rapid, sfx, pfx
  ifp = sys.stdin
  ofp = sys.stdout
  try:
    opts,args = getopt.getopt(argv,"hi:o:",["sfx-final=", "pfx=", "sfx-rapid=","sfx-slow="])
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
    elif opt in ("--sfx-rapid"):
      sfx_rapid = arg
    elif opt in ("--sfx-slow"):
      sfx_slow = arg
    elif opt in ("--pfx"):
      pfx = arg.decode('unicode_escape')
    elif opt in ("--sfx-final"):
      sfx = arg.decode('unicode_escape')

  ingest_egest(ifp, ofp)

  if ifp!=sys.stdin:
    ifp.close()

  if ofp!=sys.stdout:
    ofp.close()




if __name__ == "__main__":
  main(sys.argv[1:])
