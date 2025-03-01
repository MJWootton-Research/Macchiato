#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import re
import os
import sys
import math
import glob

import numpy as np

"""
TransFireFrequency.py creates a list of the number of times that each transition fired with error analysis.
Command line arguments taken in order:
* Name of simulation results folder (run this script in the parent directory).

"""

def main():
    # Measure number of files to inspect in directory given by command line arguments
    nFiles = len(glob.glob1(os.path.join(os.getcwd(), sys.argv[1]),'Macchiato_PetriNet_Trans_*.csv'))
    print('\nDiscovered %d files to inspect in "%s".\n' % (nFiles, sys.argv[1]))

    # # Get runmode from command line arguments
    # if len(sys.argv) > 2:
    #     errorAnalysis = (sys.argv[2] == 'E')
    #     if not errorAnalysis:
    #         raise RuntimeError('Unknown command line option "%s"' % sys.argv[2])
    #     else:
    #         try:
    #             import numpy as np
    #         except:
    #             sys.exit('Failed to import NumPy -- required for error analysis')
    # else:
    #     errorAnalysis = False
    errorAnalysis = True

    # Set-up data objects
    namesSet = False
    data = []
    eData = None

    # Loop over results files
    ii = 0 if os.path.isfile(os.path.join(os.getcwd(), sys.argv[1], 'Macchiato_PetriNet_Trans_0.csv')) else 1
    for j in range(nFiles):
        i = j+ii
        file = open(os.path.join(os.getcwd(), sys.argv[1], 'Macchiato_PetriNet_Trans_%d.csv' % (i)), 'r')
        l = False
        for line in file:
            # Skip over title lines
            if l is False:
                l = True
                continue
            # Find transitions' labels
            elif namesSet is False:
                data = line.split(',')[2:-1]
                if errorAnalysis:
                    eData = np.zeros((len(data),nFiles))
                for d in range(len(data)):
                    data[d] = [data[d], 0]
                namesSet = True
                continue
        # Record data
        d = 0
        for k in line.split(',')[2:-1]:
            data[d][1] += int(k)
            if errorAnalysis:
                eData[d][j] = int(k)
            d+=1
    file.close()

    # Write results
    outDir = sys.argv[1]
    while True:
        if outDir[-1] in ['\\', '/']:
            outDir = outDir[:-1]
        else:
            break
    out = open(os.path.join(os.getcwd(), '%s_TransFireAverage.csv' % os.path.split(outDir)[1]), 'w')
    head = 'Transition,Times_fired,Fires_Per_Simulation'
    if errorAnalysis:
        head += ',Error'
    out.write('%s\n' % head)
    # Organise data and (optionally) perform error analysis
    for d in range(len(data)):
        if errorAnalysis:
            r = np.mean(eData[d])
            # print(type(r), '%g' % r, r)
            rE = np.std(eData[d])/math.sqrt(nFiles)
            rEs = ',%g' % rE
            pm = '+\-'
        else:
            r = data[d][1]/float(nFiles)
            rEs = ''
            pm = ''
        print('%s, %d, %g%s%s' % (data[d][0], data[d][1], r, pm, rEs))
        out.write('%s,%d,%g%s\n' % (data[d][0], data[d][1], r, rEs))
    out.close()

if __name__ == '__main__':
    main()
