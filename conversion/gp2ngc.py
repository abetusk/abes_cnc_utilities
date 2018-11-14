#!/usr/bin/python

from __future__ import print_function
import os, sys, re, getopt, numpy as np, math, json

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

VERSION = "0.1.0"

ctx = {
  "units" : "mm", "epsilon" : 1.0/1024.0,
  "sort": False,
  "explicit_speed": False,
  "premul" : 1.0, "premul_x" : 1.0, "premul_y" : 1.0, "premul_z" : 1.0,
  "header" : "", "footer" : "",
  "g0speed" : "", "g1speed" : "",
  "z_active": False,
  "z_step" : 7.0, "z_height" : 5.0, "z_plunge" : -21.0, "z_0" : 0.0, "z_slow" : "", "z_rapid" : "",
  "tab_n" : 0, "tab_offset" : 0.0, "tab_length" : 50.0, "tab_height" : 5.0, "tab_slide_factor" : 1/8.0,
  "tab_default_n" : 4,
  "close_polygon": True
}

ctx_laser = {
  "units" : "mm", "epsilon" : 1.0/1024.0,
  "sort": False,
  "explicit_speed": False,
  "premul" : 1.0, "premul_x" : 1.0, "premul_y" : 1.0, "premul_z" : 1.0,
  "header" : "", "footer" : "",
  "g0speed" : "F5000", "g1speed" : "F3000",
  "z_active": False,
  "z_step" : 0.0, "z_height" : 0.0, "z_plunge" : 0.0, "z_0" : 0.0, "z_slow" : 0.0, "z_rapid" : 0.0,
  "tab_n" : 0, "tab_offset" : 0.0, "tab_length" : 2.5, "tab_height" : 0.0, "tab_slide_factor" : 1/8.0,
  "tab_default_n" : 4,
  "close_polygon": False
}

ctx_maslow = {
  "units" : "mm", "epsilon" : 1.0/(1024.0*1024.0),
  "sort": False,
  "explicit_speed": False,
  "premul" : 1.0, "premul_x" : 1.0, "premul_y" : 1.0, "premul_z" : 1.0,
  "header" : "", "footer" : "",
  #"g0speed" : 800.0, "g1speed" : 800.0,
  "g0speed" : "", "g1speed" : "",
  "z_active": True,
  "z_step" : 7.0, "z_height" : 5.0, "z_plunge" : -21.0, "z_0" : 0.0, "z_slow" : "", "z_rapid" : "",
  "tab_n" : 3, "tab_offset" : 0.0, "tab_length" : 50.0, "tab_height" : 3.0, "tab_slide_factor" : 1/8.0,
  "tab_default_n" : 3,
  "close_polygon": True
}

def usage():
  print("version:", VERSION)
  print("usage:")
  print("")
  print("    gp2ngc [options] <in-gnuplot> <out-ngc>")
  print("")
  print("  [--preset preset]      use preset tool context (options are 'maslow', 'laser')")
  print("  [-i infile]            input file ('-' for stdin, default)")
  print("  [-o outfile]           output file ('-' for stdout, default)")
  print("  [--header str]         string to print before any processing")
  print("  [--footer str]         string to print after any processing")
  print("  [--rapid str]          string to append at end of rapid motion (G0)")
  print("  [--slow str]           string to append at end of slow motion (G1)")
  print("  [--z-rapid str]        z rapid (default to rapid)")
  print("  [--z-slow str]         z rapid (default to rapid)")
  print("  [--z-step dz]          z step down per pass")
  print("  [--z-raise Z]          z height to raise z to for rapid motion")
  print("  [--z-plunge z]         z final plunge depth")
  print("  [--tab-n n]            insert n tabs per contour")
  print("  [--tab-length s]       tab length")
  print("  [--tab-height h]       tab height")
  print("  [--show-context]       show context information")
  print("")

def print_polygon_debug(pgn, ofp=sys.stdout):
  print("", file=ofp)
  for idx in range(len(pgn)):
    print("#", idx, pgn[idx]["t"], ":", pgn[idx]["x"], pgn[idx]["y"], pgn[idx]["s"], "n:", pgn[idx]["n"], file=ofp)

def print_polygon_debug2(pgn, ofp=sys.stdout):
  print("", file=ofp)
  for idx in range(len(pgn)):
    z = 0.0
    if pgn[idx]["t"] == "t": z = 1
    print(pgn[idx]["x"], pgn[idx]["y"], z, file=ofp)

    #if idx>0 and ((pgn[idx-1]["t"] == "." and pgn[idx]["t"] == "t") or (pgn[idx-1]["t"] == "t" and pgn[idx]["t"] == ".")):
    #  print( "\n", file=ofp)


def cmp_pgn_ele(a,b):
  if (len(a) == 0): return -1
  if (len(b) == 0): return 1

  s0 = math.sqrt(a[0][0]*a[0][0] + a[0][1]*a[0][1])
  s1 = math.sqrt(b[0][0]*b[0][0] + b[0][1]*b[0][1])

  if s0 < s1: return -1
  if s1 > s0: return  1
  return 0

def polygons_sort(pgns):
  pgns.sort(cmp_pgn_ele)


def print_polygon(pgn, ofp=sys.stdout):
  print("", file=ofp)
  for idx in range(len(pgn)):
    print(pgn[idx]["x"], pgn[idx]["y"], file=ofp)


def crossprodmag(u,v, eps=1.0/1024.0):
  ux = u["x"]
  uy = u["y"]
  us = math.sqrt(ux*ux + uy*uy)

  vx = v["x"]
  vy = v["y"]
  vs = math.sqrt(vx*vx + vy*vy)

  if (abs(us) < eps) or (abs(vs) < eps): return 0.0

  return ((ux*vy) - (uy*vx))/(us*vs)


def ingest_egest_orig(ctx, ifp = sys.stdin, ofp = sys.stdout):
  polygons = []
  polygon = []

  print(ctx["header"], file=ofp)

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
      sys.exit(1)

    try:
      x = float(r[0]) * ctx["premul"]
      y = float(r[1]) * ctx["premul"]
    except Exception, e:
      print(e, file=sys.stderr)
      sys.exit(1)

    polygon.append([x,y])

  for p in polygons:
    if len(p)==0: continue

    x0 = p[0][0]
    y0 = p[0][1]

    print("G0", "X" + "{:.10f}".format(x0), "Y" + "{:.10f}".format(y0), sfx_rapid, file=ofp)
    for xy in p:
      x = xy[0]
      y = xy[1]
      print("G1", "X" + "{:.10f}".format(x), "Y" + "{:.10f}".format(y), ctx["g1speed"], file=ofp)

    if ctx["close_polygon"]:
      print("G1", "X" + "{:.10f}".format(x0), "Y" + "{:.10f}".format(y0), ctx["g1speed"], file=ofp)

    print(file=ofp)

  print(sfx, file=ofp)

def ingest_egest(ctx, ifp = sys.stdin, ofp = sys.stdout):
  polygons = []
  polygon = []

  print(ctx["header"], file=ofp)

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
      sys.exit(1)

    try:
      x = float(r[0]) * ctx["premul"]
      y = float(r[1]) * ctx["premul"]
    except Exception, e:
      print(e, file=sys.stderr)
      sys.exit(1)

    polygon.append([x,y])

  if len(polygon)>0:
    polygons.append(polygon)

  if ctx["sort"]:
    polygons_sort(polygons)

  for p in polygons:
    if len(p)==0: continue

    x0 = p[0][0]
    y0 = p[0][1]

    print("G0", "X" + "{:.10f}".format(x0), "Y" + "{:.10f}".format(y0), ctx["g0speed"], file=ofp)

    nstep=1
    if ctx["z_active"]:
      print("G0", "Z" + "{:.10f}".format(ctx["z_height"]), ctx["z_rapid"], file=ofp)
      nstep = int(math.ceil(( abs(ctx["z_plunge"] - ctx["z_0"]) )/ctx["z_step"]))

    for s in range(nstep):

      if ctx["z_active"]:
        zh = ((ctx["z_plunge"] - ctx["z_0"]) * float(s+1)/float(nstep)) + ctx["z_0"]
        if zh < ctx["z_plunge"]:
          print(";#(CLAMPING)", file=ofp)
          zh = ctx["z_plunge"]

        print("G1", "Z" + "{:.10f}".format(zh), ctx["z_slow"], file=ofp)

      for xy in p:
        x = xy[0]
        y = xy[1]
        print("G1", "X" + "{:.10f}".format(x), "Y" + "{:.10f}".format(y), ctx["g0speed"], file=ofp)

      if ctx["close_polygon"]:
        print("G1", "X" + "{:.10f}".format(x0), "Y" + "{:.10f}".format(y0), ctx["g0speed"], file=ofp)

      print(file=ofp)

    if ctx["z_active"]:
      print("G0", "Z" + "{:.10f}".format(ctx["z_height"]), ctx["z_rapid"], file=ofp)

  print(ctx["footer"], file=ofp)

## decorate the pgn array of objects with the cross product normal
## magnitude value 'n'
##
def polygon_decorate_n(pgn):
  if len(pgn) < 3:
    for idx in range(len(pgn)):
      pgn[idx]["n"] = 0.0
    return

  for idx in range(len(pgn)):
    prv_idx = (idx + len(pgn) - 1) % len(pgn)
    nxt_idx = (idx + 1) % len(pgn)
    v0 = { "x": pgn[prv_idx]["x"] - pgn[idx]["x"], "y" : pgn[prv_idx]["y"] - pgn[idx]["y"] }
    v1 = { "x": pgn[nxt_idx]["x"] - pgn[idx]["x"], "y" : pgn[nxt_idx]["y"] - pgn[idx]["y"] }
    pgn[idx]["n"] = crossprodmag(v0,v1)

## calculate the 'score' of the tab placed at path s-position 'tab_beg' with
## tab length 'tab_len'.
## This is length of each portion the tab falls on the line segment times the
## magnitude of the normal.
## Since the left and right segment use the same normal, and the normal is thus
## multiplied by itself, this score is strictly positive.
##
def polygon_curve_score(pgn, tab_beg, tab_len):
  score = 0.0
  if len(pgn) < 3: return score
  for idx in range(len(pgn)):

    prv_idx = (idx + len(pgn) - 1) % len(pgn)
    nxt_idx = (idx + 1) % len(pgn)

    if (tab_beg + tab_len) < pgn[idx]["s"]: return score
    if tab_beg > pgn[idx]["s"]: continue

    s0 = abs(max(pgn[prv_idx]["s"], tab_beg) - pgn[idx]["s"])
    s1 = abs(pgn[idx]["s"] - min(tab_beg + tab_len, pgn[nxt_idx]["s"]))

    score += s0*s1*pgn[idx]["n"]*pgn[idx]["n"]

  return score


## insert the tab into the 'pgn' array at s-position 'tab_beg' with
## 'tab_len'.
## This does not wrap around from the end to the beginning (though this
## might be upadted in the future).
## This constructs a new array and returns it.
##
def polygon_insert_tab_at(pgn, tab_beg, tab_len):
  ret_p = []

  prv_x = 0.0
  prv_y = 0.0
  prv_s = 0.0

  for pnt_idx in range(len(pgn)):
    p = pgn[pnt_idx]

    if pnt_idx==0:
      prv_x = p["x"]
      prv_y = p["y"]
      prv_s = p["s"]

    # take care of pathological case when line segment is 0 length
    #
    r = math.sqrt((prv_x - p["x"])*(prv_x - p["x"]) + (prv_y - p["y"])*(prv_y - p["y"]))
    if abs(r) < ctx["epsilon"]:
      prv_x = p["x"]
      prv_y = p["y"]
      prv_s = p["s"]
      r = 1.0

    # If the tab is completel to the 'left' of the current vertex, we can insert it
    # completely without needing to split the tab into segements.
    # Do so, making sure \to insert an extra 'down' entry so that if we are right
    # next to another tab in the list, we'll properly render the outline.
    #
    if (tab_beg <= p["s"]) and ((tab_beg + tab_len) < p["s"]):
      ds = tab_beg - prv_s
      x = (ds * (p["x"] - prv_x) / r) + prv_x
      y = (ds * (p["y"] - prv_y) / r) + prv_y
      ret_p.append( {"x": x, "y": y, "s": tab_beg, "t": "t", "n":0.0 } )

      ds = tab_beg + tab_len - prv_s
      x = (ds * (p["x"] - prv_x) / r) + prv_x
      y = (ds * (p["y"] - prv_y) / r) + prv_y
      ret_p.append( {"x": x, "y": y, "s": tab_beg + tab_len, "t": "t", "n":0.0 } )

      ret_p.append( {"x": x, "y": y, "s": tab_beg + tab_len, "t": ".", "n":0.0 } )

      ret_p += pgn[pnt_idx:]
      return ret_p

    pnt_type = p["t"]

    # The tab is split across the current vertex and entries to the right.
    # Shave off the head of the tab, add/modify the entries to create a 'tab'
    # entry in the 'pgn' list.
    #
    if (tab_beg <= p["s"]) and ((tab_beg + tab_len) > p["s"]):
      ds = tab_beg - prv_s
      x = (ds * (p["x"] - prv_x) / r) + prv_x
      y = (ds * (p["y"] - prv_y) / r) + prv_y
      ret_p.append( {"x": x, "y": y, "s": tab_beg, "t": "t", "n": 0.0 } )

      pnt_type = "t"

      tab_len -= (p["s"] - tab_beg)
      tab_beg = p["s"]

    ret_p.append( { "x" : p["x"], "y": p["y"], "s": p["s"], "t": pnt_type, "n": 0.0 })

    prv_x = p["x"]
    prv_y = p["y"]
    prv_s = p["s"]

  return ret_p


## Process polygon and insert tabs.
##
def ingest_egest_with_tabs(ctx, ifp = sys.stdin, ofp = sys.stdout):
  polygons = []
  polygon = []

  print(ctx["header"], file=ofp)

  firstPoint = True
  prev_x = 0.0
  prev_y = 0.0

  line_no=0
  for line in ifp:
    line = line.strip()
    line_no += 1

    if (len(line)==0) or (line == ""):
      if len(polygon)>0:
        polygons.append(polygon)
      polygon = []
      firstPoint = True
      continue

    if line[0]=='#': continue

    r = re.split(r'\s+', line)

    if len(r)!=2:
      print("Error on line " + str(line_no) + ": number of arguments is not 2 (" + line + ")", file=sys.stderr)
      sys.exit(1)

    try:
      x = float(r[0]) * ctx["premul"]
      y = float(r[1]) * ctx["premul"]
    except Exception, e:
      print(e, file=sys.stderr)
      sys.exit(1)

    # record lenght of outline as we go
    #
    s = 0.0
    if not firstPoint:
      ds = math.sqrt( (prev_x - x)*(prev_x - x) + (prev_y - y)*(prev_y - y) )
      s = polygon[ len(polygon) - 1 ]["s"] + ds

    prev_x = x
    prev_y = y

    # '.' type ("T" field) represent simple contour whereas 't' type
    # represents tabs. Though space iniefficient, it's easier
    # to decorate entries with modifiers like this than do it a more
    # complicated but efficietn way.
    #
    polygon.append({ "x":x, "y":y, "s": s, "t": ".", "n":0.0 })
    firstPoint = False

  if len(polygon)!=0:
    polygons.append(polygon)

  if ctx["sort"]:
    polygons_sort(polygons)



  # decorate with 'n' cross product magnitude value for
  # score tab positioning heuristic.
  #
  for pgn_idx in range(len(polygons)):
    pgn = polygons[pgn_idx]
    if len(pgn)<3:
      for idx in range(len(pgn)):
        pgn[idx]["n"] = 0.0
      continue

    for idx in range(len(pgn)):
      prv_idx = (idx + len(pgn) - 1) % len(pgn)
      nxt_idx = (idx + 1) % len(pgn)
      v0 = { "x": pgn[prv_idx]["x"] - pgn[idx]["x"], "y" : pgn[prv_idx]["y"] - pgn[idx]["y"] }
      v1 = { "x": pgn[nxt_idx]["x"] - pgn[idx]["x"], "y" : pgn[nxt_idx]["y"] - pgn[idx]["y"] }
      pgn[idx]["n"] = crossprodmag( v0, v1 )

  _zheight = ctx["z_height"]
  _zplunge = ctx["z_plunge"]
  _zzero = ctx["z_0"]
  _zstep = ctx["z_step"]
  _g0speed = ctx["g0speed"]
  _g1speed = ctx["g1speed"]

  _tabheight = ctx["tab_height"]
  _ztabstart = _zplunge + _tabheight

  _tablen = ctx["tab_length"]
  _ntab = ctx["tab_n"]

  # a bit inefficient but construct tabs
  #
  for pidx in range(len(polygons)):
    p = polygons[pidx]
    if len(p)==0: continue

    polygon_decorate_n(polygons[pidx])

    clen = p[ len(p) - 1 ]["s"]

    s_window_len = (clen / (float(_ntab))) - _tablen

    if _tablen <= 0.0: continue
    if clen < (float(_ntab) * _tablen): continue
    for tabidx in range(_ntab):

      tab_s_offset = float(tabidx) * clen / float(_ntab)

      # this heuristic, for simplicity, only uses two scores, one at the original
      # offset and another at some distance away that doesn't overlap with the
      # other tab, to determine where the tab should be positioned.
      #
      n_tab_sample = 4
      score, min_score, min_idx = [], 0, 0
      for idx in range(n_tab_sample):
        tab_shift = float(idx) * s_window_len / float(n_tab_sample)
        score.append( polygon_curve_score(polygons[pidx], tab_s_offset + tab_shift , _tablen) )
        #print("#", tab_s_offset + tab_shift, score[idx])
        if idx==0:
          min_score = score[0]
          min_idx = 0
        elif min_score > score[idx]:
          min_score = score[idx]
          min_idx = idx
      #print("## min_score", min_score, ", min_idx", min_idx)

      tab_shift = float(min_idx) * s_window_len / float(n_tab_sample)
      polygons[pidx] = polygon_insert_tab_at(polygons[pidx], tab_s_offset + tab_shift, _tablen)

      #if score0 == min(score0, score1, score2):
      #  polygons[pidx] = polygon_insert_tab_at(polygons[pidx], tab_s_offset, _tablen)
      #elif score1 == min(score0, score1, score2):
      #  polygons[pidx] = polygon_insert_tab_at(polygons[pidx], tab_s_offset + s_window_len/2, _tablen)
      #else:
      #  polygons[pidx] = polygon_insert_tab_at(polygons[pidx], tab_s_offset + s_window_len, _tablen)

    #print_polygon_debug(polygons[pidx])

  for p in polygons:
    if len(p)==0: continue

    x0 = p[0]["x"]
    y0 = p[0]["y"]

    print("G0", "X" + "{:.10f}".format(x0), "Y" + "{:.10f}".format(y0), _g0speed, file=ofp)

    nstep=1
    if ctx["z_active"]:
      print("G0", "Z" + "{:.10f}".format(_zheight), _g0speed, file=ofp)
      nstep = int(abs(math.ceil((_zplunge - _zzero)/_zstep)))

    prev_entry_type = "."

    for s in range(nstep):

      if ctx["z_active"]:
        zh = ((_zplunge - _zzero) * float(s+1)/float(nstep)) + _zzero
        if zh < _zplunge:
          zh = _zplunge

        if (zh < _ztabstart) and (prev_entry_type == ".") and (xy["t"] == "t"):
            #print(";# up!", file=ofp)
            print("G1", "Z" + "{:.10f}".format(_ztabstart), _g1speed, file=ofp)
        else:
          print("G1", "Z" + "{:.10f}".format(zh), _g1speed, file=ofp)

      for xy in p:

        if ctx["z_active"] and (zh < _ztabstart):
          if (prev_entry_type == "t") and (xy["t"] == "."):

            #print(";# down!", file=ofp)
            print("G1", "Z" + "{:.10f}".format(zh), _g1speed, file=ofp)

        x = xy["x"]
        y = xy["y"]
        print("G1", "X" + "{:.10f}".format(x), "Y" + "{:.10f}".format(y), _g1speed, file=ofp)

        if ctx["z_active"]:
          if zh < _ztabstart:
            if (prev_entry_type == ".") and (xy["t"] == "t"):
              #print(";# up!", file=ofp)
              print("G1", "Z" + "{:.10f}".format(_ztabstart), _g1speed, file=ofp)

        prev_entry_type = xy["t"]

      #if ctx["z_active"]:
      if ctx["close_polygon"]:
        print("G1", "X" + "{:.10f}".format(x0), "Y" + "{:.10f}".format(y0), _g1speed, file=ofp)

      print(file=ofp)

    print("G0", "Z" + "{:.10f}".format(_zheight), _g0speed, file=ofp)

  print(ctx["footer"], file=ofp)


def main(argv):
  global ctx
  ifn, ofn = "-", "-"
  ifp, ofp = sys.stdin, sys.stdout

  long_opt_list = [ "help", "preset=", "show-context", "z", "explicit-speed", "premul=", "epsilon=", "header=", "footer=", "rapid=", "slow=",
                    "z-rapid=", "z-slow=", "z-step=", "z-raise=", "z-plunge=",
                    "tab", "tab-n=", "tab-length=", "tab-height=", "notab",
                    "close-polygon", "open-polygon",
                    "sort"]

  try:
    #opts,args = getopt.getopt(argv,"hi:o:",["sfx-final=", "pfx=", "sfx-rapid=","sfx-slow=", "premul=", "z-step", "z-raise", "z-plunge"])
    opts,args = getopt.getopt(argv,"hi:o:",long_opt_list)
  except getopt.GetoptError:
    usage()
    sys.exit(2)

  if len(args) >= 1:
    ifn = args[0]
    if len(args) >= 2:
      ofn = args[1]

  for opt, arg in opts:
    if opt == "--preset":
      if arg.lower() in ("maslow", "maslowcnc"):
        ctx = ctx_maslow
      elif arg.lower() in ("laser"):
        ctx = ctx_laser
      else:
        print("WARNING: no preset found, using default", file=sys.stderr)

  show_context = False

  for opt, arg in opts:

    if opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt in ("--show-context"): show_context = True

    elif opt in ("-i", "--ifile"): ifn = arg
    elif opt in ("-o", "--ofile"): ofn = arg

    elif opt in ("--premul"): ctx["premul"] = float(arg)

    elif opt in ("--rapid"):
      ctx["g0speed"] = arg
      ctx["explicit_speed"] = True
    elif opt in ("--slow"):
      ctx["g1speed"] = arg
      ctx["explicit_speed"] = True
    elif opt in ("--explicit-speed"): ctx["explicit_speed"] = True

    elif opt in ("--header"):     ctx["header"] = arg.decode('unicode_escape')
    elif opt in ("--footer"):  ctx["footer"] = arg.decode('unicode_escape')

    elif opt in ("--close-polygon"): ctx["close_polygon"] = True
    elif opt in ("--open-polygon"): ctx["close_polygon"] = False

    elif opt in ("--z"):        ctx["z_active"] = True
    elif opt in ("--z-slow"):   ctx["z_slow"] = float(arg)
    elif opt in ("--z-rapid"):  ctx["z_rapid"] = float(arg)
    elif opt in ("--z-step"):   ctx["z_step"] = float(arg)
    elif opt in ("--z-raise"):  ctx["z_height"] = float(arg)
    elif opt in ("--z-plunge"):
      ctx["z_active"] = True
      ctx["z_plunge"] = float(arg)

    elif opt in ("--notab"):  ctx["tab_n"] = 0
    elif opt in ("--tab"):    ctx["tab_n"] = ctx["tab_default_n"]
    elif opt in ("--tab-n"):  ctx["tab_n"] = int(arg)
    elif opt in ("--tab-length"): ctx["tab_length"] = float(arg)
    elif opt in ("--tab-height"): ctx["tab_height"] = float(arg)

    elif opt in ("--sort"): ctx["sort"] = True

  if show_context:
    print(json.dumps(ctx, indent=2))
    sys.exit(0)

  if ifn != "-": ifp = open(ifn,"r")
  if ofn != "-": ofp = open(ofn, "w")

  if ctx["tab_n"] > 0 : ingest_egest_with_tabs(ctx, ifp, ofp)
  else:                 ingest_egest(ctx, ifp, ofp)

  if ifp!=sys.stdin:  ifp.close()
  if ofp!=sys.stdout: ofp.close()

if __name__ == "__main__":
  main(sys.argv[1:])
