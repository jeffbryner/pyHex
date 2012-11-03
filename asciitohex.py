#! /usr/bin/env python

import sys
import binascii

def convert_hex(string):
    return ' '.join([hex(ord(character))[2:].upper().zfill(2) \
                     for character in string])

sys.stdout.write(convert_hex(sys.argv[1])+ "\n")


