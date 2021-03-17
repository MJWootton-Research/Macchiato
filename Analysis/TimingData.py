#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import re
import os
import sys
import math
import glob

import numpy as np
import matplotlib.pyplot as plt


'''
TimingData.py produces average simulation durations for simulations that end with specific token configurations, and the number of such simulations thereof, along with the overall average duration.
Command line arguments taken in order:
* Name of simulation results folder (run this script in the parent directory).
* Labels of the terminal places to count, separated by colons (eg, 'P1:P2:P3').

'''

def eDataToFile(eData, pLen):
    print(eData)
    # eFile = open(os.path.join(os.getcwd(), 'allTimes.csv'), 'w')
    pFile = open(os.path.join(os.getcwd(), 'percentiles.txt'), 'w')
    pFile.write('10th  90th\n')
    all = np.array([])
    for p in range(pLen):
        a = len(eData[p])
        for i in range(len(eData[p])):
            if eData[p][i] == 0.0:
                a = i
                break
            # eFile.write('%f,' % eData[p][i])
        # eFile.write('\n')
        if a:
            pFile.write('%f    %f\n' % (np.percentile(eData[p][:a], 10), np.percentile(eData[p][:a], 90)))
            all = np.concatenate((all, eData[p][:a]))
        else:
            pFile.write('-    -\n')
    if not len(all):
        raise RuntimeError('Results array is empty - Consider sanity checking results or simulation parameters')
    pFile.write('\nAll: %f    %f' % (np.percentile(all, 10), np.percentile(all, 90)))
    # eFile.close()
    pFile.close()

def main():
    # Measure number of files to inspect in directory given by command line arguments
    nFiles = len(glob.glob1(os.path.join(os.getcwd(), sys.argv[1]),'Macchiato_PetriNet_Places_*.csv'))
    print('\nDiscovered %d files to inspect in \'%s\'.\n' % (nFiles, sys.argv[1]))

    # # Get runmode from command line arguments
    # if len(sys.argv) > 3:
    #     errorAnalysis = (sys.argv[3] == 'E')
    #     if not errorAnalysis:
    #         raise RuntimeError('Unknown command line option \'%s\'' % sys.argv[3])
    #     else:
    #         try:
    #             import numpy as np
    #         except:
    #             sys.exit('Failed to import NumPy -- required for error analysis')
    # else:
    #     errorAnalysis = False
    errorAnalysis = True

    last = 0.0
    # Get target places from command line arguments
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
    nP = len(pList)+1
    endings = []
    for e in range(nP):
        endings.append([])


    # Set-up data objects
    eData = None
    if errorAnalysis:
        eData = np.zeros((nP,nFiles))
        #pNums = np.zeros(nP)
    data = []
    for p in range(nP):
        data.append([0.0, 0])

    # Loop over results files
    for i in range(nFiles):
        file = open(os.path.join(os.getcwd(), sys.argv[1], 'Macchiato_PetriNet_Places_%d.csv' % (i+1)))
        l = 0
        # Skip over title lines
        for line in file:
            if l < 2:
                l += 1
                continue
            done = False
            sLine = line.split(',')
            for p in range(len(pList)):
                pp = int(pList[p])
                # Seek data from final step
                if len(sLine) > 1:
                    # Record data
                    if int(sLine[pp]) == 1:
                        if errorAnalysis:
                            eData[p][data[p][1]] = float(sLine[1])
                        data[p][0] += float(sLine[1])
                        data[p][1] += 1
                        done = True
                        endings[p].append(i+1)
                        break
                else:
                    # Record simulations that have timed-out
                    data[-1][0] += last
                    data[-1][1] += 1
                    done = True
                    endings[-1].append(i+1)
                    break
            if l > 2:
                last = float(sLine[1])
            else:
                last = 0.0
            if done:
                break
    file.close()

    outDir = sys.argv[1]
    while True:
        if outDir[-1] in ['\\', '/']:
            outDir = outDir[:-1]
        else:
            break
    ends = open(os.path.join(os.getcwd(), '%s_Endings.txt' % sys.argv[1]), 'w')
    for e in range(nP):
        if e < nP-1:
            ends.write('Ending [%d]:\n' % int(pList[e]))
        else:
            ends.write('Timeouts:\n')
        for f in endings[e]:
            ends.write('%d\n' %f)
        ends.write('\n')
    ends.close()

    # Organise data
    if errorAnalysis:
        ed = np.zeros((nP-1,2))
        allD = np.array([])
        allE = [0.0,0.0]
        # Error analysis (subsets)
        if errorAnalysis:
            eDataToFile(eData, len(pList))
        for p in range(nP-1):
            if len(eData[p][0:data[p][1]]):
                ed[p][0] = np.mean(eData[p][0:data[p][1]])
                ed[p][1] = np.std(eData[p][0:data[p][1]])/math.sqrt(data[p][1])
                allD = np.concatenate((allD, eData[p][0:data[p][1]]))
            else:
                ed[p][0] = float('nan')
                ed[p][1] = float('nan')
            # if not math.isnan(ed[p][0]):
            #     print('%g +/- %g' % (ed[p][0], ed[p][1]))
            # else:
            #     print('N/A')
        # Check data integrity
        assert(len(allD)+data[-1][1] == nFiles), 'Data object mismatches with number of files.'
        # Error analysis (all)
        allE[0] = np.mean(allD)
        allE[1] = np.std(allD)/math.sqrt(nFiles)
        # Compile string for file output
        outputString = ',N,Ratio,Ratio_Error,Mean_Time,Time_Error\n'
        pListLab.append('Timeout')
        for p in range(nP):
            r = float(data[p][1])/float(nFiles)
            rE = math.sqrt((r-r**2)/nFiles)
            outputString += '[%s],%d,%f,%f' % (pListLab[p],data[p][1], r, rE)
            if p < nP-1:
                try:
                    f = math.floor(math.log(ed[p][0],10))
                except ValueError:
                    f = float('NaN')
                if math.isnan(ed[p][0]):
                    outputString += '0'
                else:
                    outputString += ',%g,%g,,[(,%.2f,+/-,%.2f,)*10^,%d,]' % (ed[p][0], ed[p][1], ed[p][0]/(10**f), ed[p][1]/(10**f), f)
            outputString += '\n'
        f = math.floor(math.log(allE[0],10))
        outputString += '[All],,,,%g,%g,,[(,%.2f,+/-,%.2f,)*10^,%d,]\n' % (allE[0], allE[1], allE[0]/(10**f), allE[1]/(10**f), f)
    else:
        outputString = 'N,Mean_Time\n'
        for d in data:
            dt = '_'
            if d[1] > 0.0:
                dt = '%g' % (d[0]/float(d[1]))
            #print(d[1], dt)
            outputString += '%d,%s\n' % (d[1], dt)

    #Median
    if errorAnalysis:
        outputString += 'Median\n%g\n' % np.median(allD)

    # Output results
    outF = open(os.path.join(os.getcwd(), '%s_TimingData.csv' % sys.argv[1]), 'w')
    outF.write(outputString)
    outF.close()
    print('\n   %s' % re.sub(',', ' ', outputString))

# New
    # for d in data:
    dsF = open(os.path.join(os.getcwd(), 'ds_%s.csv' % outDir), 'w')
    for p in range(len(pList)):
        if len(eData[p][0:data[p][1]]):
            ds = '%s,|' % pListLab[p]
            for ee in eData[p][0:data[p][1]]:
                ds += ',%r' % ee
            # print(ds)
            dsF.write('%s\n' % ds)
            plt.hist(eData[p][0:data[p][1]], bins=100)
            plt.xlabel('Duration')
            plt.ylabel('Count')
            plt.savefig('%s_%s_end_histogram.png' % (sys.argv[1], pListLab[p]))
            plt.clf()
    dsF.close()

if __name__ == '__main__':
    main()
