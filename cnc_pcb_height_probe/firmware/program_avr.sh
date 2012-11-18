#!/bin/bash

#chipcode="t13"
chipcode="m328p"

if [ "$1" = '' ]; then echo provide hex file; exit; fi
echo running "avrdude -c usbtiny -p $chipcode -U flash:w:$1"
avrdude -c usbtiny -p $chipcode -U flash:w:$1
