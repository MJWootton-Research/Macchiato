#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os, sys

def main():
    name = sys.argv[1]
    time = sys.argv[2]
    outdir = os.path.join(os.getcwd(), name+'_'+time)
    tags = ['Places', 'Trans', 'FireList']
    found = []
    for tag in tags:
        # print(os.path.join(os.getcwd(), name+'_'+tag+'_'+time))
        if os.path.isfile(os.path.join(os.getcwd(), name+'_'+tag+'_'+time+'.csv')):
            found.append(tag)
    if not len(found):
        sys.exit('No matching files found to split.')

    os.mkdir(outdir)

    for tag in found:
        n = 0
        with open(os.path.join(os.getcwd(), name+'_'+tag+'_'+time+'.csv'), 'r') as in_file:
            for line in in_file:
                if line.startswith('>>>>>'):
                    if n:
                        out_file.close()
                    n+=1
                    out_file = open(os.path.join(outdir, 'Macchiato_PetriNet_'+tag+f'_{n}.cvs'), 'w')
                    continue
                out_file.write(line)
            out_file.close()

if __name__ == '__main__':
    main()
