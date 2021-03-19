#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import sys
import glob
import subprocess

def render(source, formats):
    for f in formats:
        assert source[-4:].lower() == ".dot"
        format = f.lower()
        subprocess.call('dot "%s" -T %s -O' % (source, format), shell=True)
        os.rename('%s.%s' % (source, format), '%s.%s' % (source[:-4], format))

def main(dir, formats):
    os.chdir(dir)
    print(os.getcwd())
    if not len(formats):
        sys.exit("\nCannot produce images. No file formats specifed.\n")
    for dFile in glob.glob1(os.getcwd(),"*.dot"):
        print(dFile)
        render(dFile, formats)

if __name__ == '__main__':
    main(os.path.join(sys.argv[1]), sys.argv[2:])
