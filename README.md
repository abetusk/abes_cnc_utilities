abes_cnc_utilities
==================

cnc tools, programs, scripts


pic2gcode
---------

usage:
pic2gcode.py <filename>

Converts an image file to gcode.  Asumes white is back ground, or z position high, and anything else is z position low.
Must specify units, bit sizes, etc.  Autoscales to region of interest.


cnc_pcb_height_probe
--------------------

Code based off of V-USB's 'hid-data' example program

### firmware:
code for atmega328(p?) to communicate through USB (using V-USB) to report whether there is a continuity condition

### commandlinetool:
command line tool to query the micro.


scri.py
-------

usage:
scri.py -g <gcode file> -m <height file> [-z <threshold>] [-h|--help]

outputs new gcode based on gcode file and height map  to produce an interpolated z-height for all heights under <threshold> (default to 0).


gen_resolution_test.py
----------------------

generate a some resolution tests.  Hard coded values for now

