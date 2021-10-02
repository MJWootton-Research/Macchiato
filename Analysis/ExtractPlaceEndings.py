#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import sys
import glob

def main():
    """
    Extracts all final states of a given place in a direction sys.argv[1], indicated by its label given by sys.argv[2].

    """
    nFiles = len(glob.glob1(os.path.join(os.getcwd(), sys.argv[1]),'Macchiato_PetriNet_Places_*.csv'))
    print('\nDiscovered %d files to inspect in "%s".\n' % (nFiles, sys.argv[1]))

    pListLab = sys.argv[2].split(':')
    searchP = open(os.path.join(os.getcwd(), sys.argv[1], 'Macchiato_PetriNet_Places_1.csv'))
    sp = 0
    pList = []
    for line in searchP:
        if sp == 0:
            sp+=1
        elif sp == 1:
            psline = line.strip('\n').split(',')
            for pl in pListLab:
                for i in range(len(psline)):
                    if pl == psline[i]:
                        pList.append(i)
                        break
            break
    searchP.close()
    print('Place columns found:')
    for i in range(len(pList)):
        print(pListLab[i],':',pList[i])
    print()

    # places = sys.argv[2].split(':')
    # pList = places
    ii = 0 if os.path.isfile(os.path.join(os.getcwd(), sys.argv[1], 'Macchiato_PetriNet_Places_0.csv')) else 1
    for p in range(len(pList)):
        ends = []
        place = pList[p]
        # placeN = int(place)
        for j in range(nFiles):
            i = j+ii
            inFile = open(os.path.join(os.getcwd(), sys.argv[1], 'Macchiato_PetriNet_Places_%d.csv' % (i+1)))
            ends.append(None)
            for line in inFile:
                if len(line) == 1:
                    ends[-1] = int(ends[-1])
                    break
                else:
                    try:
                        ends[-1] = line.split(',')[place]
                        # ends[-1] = line.split(',')[placeN]
                    except IndexError:
                        pass


        outFile = open(os.path.join(os.getcwd(), 'Endings_%s_%s.csv'%(os.path.split(os.path.dirname(os.path.join(os.getcwd(), sys.argv[1])))[1], pListLab[p])), 'w')
        for e in ends:
            outFile.write('%d\n'%e)

    inFile.close()
    outFile.close()

if __name__ == '__main__':
    main()
