#! /usr/bin/env python

import sys
import binascii
hexin=""

for c in sys.argv[1::]:
    hexin+=c
sys.stdout.write(binascii.a2b_hex(hexin)+ "\n")
