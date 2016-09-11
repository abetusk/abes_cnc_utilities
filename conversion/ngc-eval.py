#!/usr/bin/python
#
# The motivation for this script is that the output of
# a 'pstoedit' conversion (from a .ps file, say) to
# gcode creates an ngc file that might not be able to
# be given by some controllers.  Instead, it would be nice
# to evaluate the variables and expressions to create a simple
# gcode file.
#
# This script does a simple evaluation of NGC (rs274?) to convert
# to a 'simple' gcode file.  That is, try and evaluate
# and 'normalize' expressions to get rid of any references
# to variable names.
#
# This uses simple regexp to do the matching and replacement.
# A better version of this would actually build the AST and
# parse correctly.  This is also surely not very robust
# since it makes a call to python's "eval" function to
# evaluate the inner expression.
#
# usage:
#
#  cat inp.ngc | ./ngc-eval.py > out.gcode
#

import sys
import re

var_map = {}

# variable decleration
#
var_decl_pat = re.compile( r'\s*#(\d+)\s*=\s*([^\s]+)\s*(\([^\)]*\))?\s*$' )

# not [], [], not []
#
expr_pat = re.compile( r'([^\[]*)\[([^\]]*)\]([^\[]*)' )

# not #*, #\d+, not #*
#
var_sub_pat = re.compile( r'([^#]*)(#\d+)([^#]*)' )

# consider comments separately to avoid matching '#' and
# other special characters
#
comment_pat = re.compile( r'\([^\)]*\)' )

line_no = 0

for line in sys.stdin:
  line_no += 1

  line = line.rstrip()
  #print line

  comments = ""
  for (comment) in re.findall(comment_pat, line):
    comments = comments + comment

  line = re.sub(comment_pat, '', line)
  #print(">>>", line, comments)

  #m = re.match( r'\s*#(\d+)\s*=\s*([^\s]+)\s*(\([^\)]*\))?\s*$', line)
  m = re.match(var_decl_pat, line)
  if m:
    #print ">>", m.group(1), m.group(2)
    var_map[ "#" + str(m.group(1)) ] = str(m.group(2))
    continue


  #vs = re.search(var_sub_pat, line)
  #print "vs:", vs

  varsub_line = ""
  for (pfx, var_subs, sfx) in re.findall(var_sub_pat, line):
    if var_subs in var_map:
      pass
    else:
      print " ERROR on line", line_no, ", no variable mapping for", var_subs
      sys.exit(1)
      continue

    varsub_line += pfx
    varsub_line += var_map[var_subs]
    varsub_line += sfx

  if varsub_line == "":
    varsub_line = line

  #print "  :" + varsub_line

  xpr_match = re.search(expr_pat, varsub_line)
  if not xpr_match:
    print varsub_line + comments
    continue


  cur_line = ""
  for (pfx, xpr, sfx) in re.findall(expr_pat, varsub_line):
    xpr_val = eval(xpr)
    cur_line += pfx + str(xpr_val) + sfx

  print cur_line +  comments

