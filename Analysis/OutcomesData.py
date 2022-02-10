#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import sys
import math
import glob

import numpy as np
import matplotlib.pyplot as plt


def main():
    rName = sys.argv[1].strip('/').strip('\\')
    dir = os.path.join(os.getcwd(), rName)
    # Measure number of files to inspect in directory given by command line arguments
    nFiles = len(glob.glob1(dir,'Macchiato_PetriNet_Places_*.csv'))
    print(f'\nDiscovered {nFiles} files to inspect in "{rName}".\n')

    nan = float('NaN')

    last = 0.0
    # Get target places from command line arguments
    pListLab = sys.argv[2].split(':')
    searchP = open(os.path.join(dir, 'Macchiato_PetriNet_Places_1.csv'), 'r')
    sp = 0
    pList = []
    for line in searchP:
        if sp == 0:
            sp+=1
        elif sp == 1:
            psline = line.strip('\n').split(',')
            for pl in pListLab:
                found_pl_i = None
                for i in range(len(psline)):
                    if pl == psline[i]:
                        found_pl_i = i
                        break
                pList.append(found_pl_i)
            break
    searchP.close()
    print('Place columns found:')
    for i in range(len(pList)):
        print(pListLab[i],':',pList[i])
    print()
    if None in pList:
        raise KeyError('Ending place search string has unfound tag(s). Review command-line arguments')
    nP = len(pList)+1
    endings = []
    for e in range(nP):
        endings.append([])

    eData = np.zeros((nP,nFiles))
    eDC = [0]*nP

    # Loop over results files
    ii = 0 if os.path.isfile(os.path.join(dir, 'Macchiato_PetriNet_Places_0.csv')) else 1
    for j in range(nFiles):
        i = j+ii
        with open(os.path.join(dir, f'Macchiato_PetriNet_Places_{i}.csv'), 'r') as file:
            pStates = [False]*len(pList)
            l = 0
            # Skip over title lines
            for line in file:
                if l < 2:
                    l += 1
                    continue
                # done = False
                sLine = line.split(',')
                if len(sLine) > 1:
                    clock = float(sLine[1])
                    for p in range(len(pList)):
                        pp = int(pList[p])
                        if int(sLine[pp]):
                            pStates[p] = True
                        else:
                            pStates[p] = False
                else:
                    if True in pStates:
                        for p in range(len(pList)):
                            if pStates[p]:
                                eData[p][eDC[p]] = clock
                                eDC[p] += 1
                    else:
                        eData[-1][eDC[-1]] = clock
                        eDC[-1] += 1

                    break

    pListLab.append('None of the above')
    results = []
    all = []
    percentiles = []
    for p in range(len(pList)):
        slice = eData[p][0:eDC[p]]
        if len(slice):
            results.append([
                            np.mean(slice),
                            np.std(slice)/math.sqrt(eDC[p])
                           ])
            # all += slice
            percentiles.append([np.percentile(slice, 10), np.percentile(slice, 90)])
            for sl in slice:
                all.append(sl)
        else:
            results.append([nan,nan])
            percentiles.append(None)
    if eDC[-1]:
        slice = eData[-1][0:eDC[-1]]
        results.append([
                        np.mean(slice),
                        np.std(slice)/math.sqrt(eDC[p])
                       ])
        percentiles.append([np.percentile(slice, 10), np.percentile(slice, 90)])
        for sl in slice:
            all.append(sl)
    else:
        results.append([nan,nan])
        percentiles.append(None)
    resAll = [np.mean(all), np.std(slice)/math.sqrt(nFiles)]
    outputString = 'Outcome,N,Ratio,Ratio Error,Mean Time,Time Error,10th Percentile, 90th Percentile\n'
    for p in range(nP):
        r = float(eDC[p])/float(nFiles)
        rE = math.sqrt((r-r**2)/nFiles)
        outputString += f'{pListLab[p]},{eDC[p]},{r},{rE}'

        if percentiles[p]:
            pcString = f',{percentiles[p][0]},{percentiles[p][1]}'
        else:
            pcString = ',N/A,N/A'

        try:
            f = math.floor(math.log(results[p][0],10))
        except ValueError:
            f = float('NaN')
        if math.isnan(results[p][0]):
            outputString += ',N/A,N/A'
        else:
            outputString += ',%g,%g%s,,[(,%.2f,+/-,%.2f,)*10^,%d,]' % (results[p][0], results[p][1], pcString, results[p][0]/(10**f), results[p][1]/(10**f), f)
        outputString += '\n'

    f = math.floor(math.log(resAll[0],10))
    outputString += '\nAll,,,,%g,%g,%g,%g,,[(,%.2f,+/-,%.2f,)*10^,%d,]' % (resAll[0], resAll[1], np.percentile(all, 10), np.percentile(all, 90), resAll[0]/(10**f), resAll[1]/(10**f), f)
    outputString += '\n\nMedian\n%g\n' % np.median(all)

    # Output results
    with open(os.path.join(os.getcwd(), f'{rName}_TimingData.csv'), 'w') as outF:
        outF.write(outputString)
    print(outputString.replace(',', ' '))

    with open(os.path.join(os.getcwd(), f'{rName}_OutcomeTimes.csv'), 'w') as dsF:
        for p in range(len(pList)):
            slice = eData[p][0:eDC[p]]
            if len(slice):
                ds = f'{pListLab[p]},|'
                for ee in slice:
                    ds += ',%r' % ee
                # print(ds)
                dsF.write(f'{ds}\n')
                plt.hist(slice, bins=100)
                plt.title(pListLab[p])
                plt.xlabel('Duration')
                plt.ylabel('Count')
                plt.savefig(f'{rName}_{pListLab[p]}_end_histogram.png', bbox_inches="tight")
                plt.clf()

if __name__ == '__main__':
    main()
