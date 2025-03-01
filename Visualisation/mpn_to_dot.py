#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Takes Petri Net from *.mpn file and writes graph in *.dot format
"""
import os
import sys

import Macchiato
from Visualisation import dot_to_image as di

def main(pn=None, formats=None):
    if pn is None:
        target = os.path.join(os.getcwd(), sys.argv[1])
        if os.path.isfile(target):
            if target.endswith('.mpn'):
                pn, _ = Macchiato.read(target)
            else:
                sys.exit('ERROR: "%s" is not an "*.mpn" file.' % target)
        else:
            sys.exit('ERROR: "%s" is a directory.' % target)

    if len(formats) == 0:
        if len(sys.argv) > 2:
            formats = sys.argv[2:]

    pn.time = None
    source = pn.dot(mode=pn.runMode, visualise=None)

    if formats is not None:
        di.render(source, formats)


if __name__ == '__main__':
    main(formats=[])
