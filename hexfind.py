#!/usr/bin/python2
import os
import sys
from optparse import OptionParser
from StringIO import StringIO

def readChunk(data,start,end):
    data.seek(start)
    readdata=data.read(end)
    return readdata

#Hex dump code from:
# Author: Boris Mazic
# Date: 04.06.2012
#package rfid.libnfc.hexdump

def hexbytes(xs, group_size=1, byte_separator=' ', group_separator=' '):
    def ordc(c):
        return ord(c) if isinstance(c,str) else c
    
    if len(xs) <= group_size:
        s = byte_separator.join('%02X' % (ordc(x)) for x in xs)
    else:
        r = len(xs) % group_size
        s = group_separator.join(
            [byte_separator.join('%02X' % (ordc(x)) for x in group) for group in zip(*[iter(xs)]*group_size)]
        )
        if r > 0:
            s += group_separator + byte_separator.join(['%02X' % (ordc(x)) for x in xs[-r:]])
    return s.lower()



def hexprint(xs):
    def chrc(c):
        return c if isinstance(c,str) else chr(c)
    
    def ordc(c):
        return ord(c) if isinstance(c,str) else c
    
    def isprint(c):
        return ordc(c) in range(32,127) if isinstance(c,str) else c > 31
    
    return ''.join([chrc(x) if isprint(x) else '.' for x in xs])



def hexdump(xs, group_size=4, byte_separator=' ', group_separator='-', printable_separator='  ', address=0, address_format='%04X', line_size=16):
    if address is None:
        s = hexbytes(xs, group_size, byte_separator, group_separator)
        if printable_separator:
            s += printable_separator + hexprint(xs)
    else:
        r = len(xs) % line_size
        s = ''
        bytes_len = 0
        for offset in range(0, len(xs)-r, line_size):
            chunk = xs[offset:offset+line_size]
            bytes = hexbytes(chunk, group_size, byte_separator, group_separator)
            s += (address_format + ': %s%s\n') % (address + offset, bytes, printable_separator + hexprint(chunk) if printable_separator else '')
            bytes_len = len(bytes)
        
        if r > 0:
            offset = len(xs)-r
            chunk = xs[offset:offset+r]
            bytes = hexbytes(chunk, group_size, byte_separator, group_separator)
            bytes = bytes + ' '*(bytes_len - len(bytes))
            s += (address_format + ': %s%s\n') % (address + offset, bytes, printable_separator + hexprint(chunk) if printable_separator else '')
    
    return s

def convert_hex(string):
    return ''.join([hex(ord(character))[2:].upper().zfill(2) \
                     for character in string])

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-b", dest='bytes'  , default=16, type="int", help="number of bytes to show per line")
    parser.add_option("-s", dest='start' , default=0, type="int", help="starting byte")
    parser.add_option("-l", dest='length' , default=16, type="int", help="length in bytes to dump")     
    parser.add_option("-f", dest='input', default="stdin",help="input: stdin default, drive name, filename, etc")
    parser.add_option("-t", dest='text', default="",help="text string to search for")
    parser.add_option("-x", dest='hex', default="",help="hex string to search for")    
    parser.add_option("-c", dest='count', default=1 ,type="int",help="count of hits to find before stopping (0 for don't stop)")
    parser.add_option("-d", "--debug",action="store_true", dest="debug", default=False, help="turn on debugging output")    
    parser.add_option("-z", "--zero",action="store_true", dest="zero", default=False,help="when printing output, count from zero rather than position hit was found")    

    (options,args) = parser.parse_args()
    
    #check for nonsense
    if len(options.hex)>0 and len(options.text)>0:
        sys.stderr.write("Cannot search for text and hex simultaneously\n")
        sys.exit()

    if options.input=="stdin" or options.input == '-':
        src=sys.stdin.read()
        src=StringIO(src)
    else:
        if os.path.exists(options.input):
            src=file(options.input,'rb')
        else:
            sys.stderr.write(options.input)
            sys.stderr.write("No input file specified\n")
            sys.exit()

    data=readChunk(src,options.start,options.length)
    if options.debug:
        print("[*] position: %d"%(src.tell())) 
    count=0
    while data: 
        if len(options.text)>0 and options.text in data:
            #where is the string in this chunk of data
            dataPos=data.find(options.text)
            #where is the string in the file
            dataAddress=(src.tell()-options.length)+dataPos
            #what do we print in the hexoutput
            printAddress=dataAddress
            if options.zero:
                #used to carve out a portion of a stream and save it via xxd -r
                printAddress=0
            #backup, get the chunk of data requested starting at the search hit.
            data=readChunk(src,dataAddress,options.length)
            print(hexdump(data, byte_separator='', group_size=2, group_separator=' ', printable_separator='  ', address=printAddress, line_size=16,address_format='%07X'))
            count+=1
        if len(options.hex)>0 and options.hex.upper() in convert_hex(data):
            #where is the string in this chunk of data
            hexdata=convert_hex(data)
            dataPos=hexdata.find(options.hex.upper())/2
            #where is the string in the file
            dataAddress=(src.tell()-options.length)+dataPos
            #what do we print in the hexoutput
            printAddress=dataAddress
            if options.zero:
                #used to carve out a portion of a stream and save it via xxd -r
                printAddress=0
            #backup, get the chunk of data requested starting at the search hit.
            data=readChunk(src,dataAddress,options.length)            
            print(hexdump(data, byte_separator='', group_size=2, group_separator=' ', printable_separator='  ', address=printAddress, line_size=16,address_format='%07X'))
            count+=1

        if options.count <> 0 and options.count<=count:
            sys.exit()
        else:
            data=readChunk(src,src.tell(),options.length)
            if options.debug:
                print("[*] position: %d"%(src.tell()))

        
