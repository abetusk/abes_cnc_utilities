#!/bin/bash

sudo avrdude -c usbtiny -p m328p -U lfuse:w:0xf7:m
