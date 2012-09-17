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

### firmware:
code for atmega328(p?) to communicate through USB (using V-USB) to report whether there is a continuity condition

### commandlinetool:
command line tool to query the micro.


Code based off of V-USB's 'hid-data' example program
