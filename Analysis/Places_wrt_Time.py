import os
import sys
import glob
import math

import numpy as np
import matplotlib.pyplot as plt

def main():
    """
    Produces average token count for given places of Petri Net simulation set
    Command line arguments:
    1 : Directory of simulations
    2 : Time limit to measure up to (make a few time steps larger than longest simulation)
    3 : Interval between measurements
    4 : List of codes of places of interest separated by ":", eg) P1:P2:P3
    5 : Optional - attemtps to stretch the ends state of completed simulations below their termination if set to True. Use with cautoin. Default value is False.

    """
    # Measure number of files to inspect in directory given by command line arguments
    nFiles = len(glob.glob1(os.path.join(os.getcwd(), sys.argv[1]),"Macchiato_PetriNet_Places_*.csv"))
    print("\nDiscovered %d files to inspect in \"%s\".\n" % (nFiles, sys.argv[1]))

    TMax = float(sys.argv[2])
    deltaT = float(sys.argv[3])
    pList = sys.argv[4].split(":")
    endStretch = False
    try:
        endStretch = (sys.argv[5] == "True")
    except:
        pass

    tSteps = int(TMax/deltaT)
    if tSteps*deltaT < TMax:
        tSteps += 1

    for P in pList:
        print("\nAnalysising place \"%s\"" % P)
        B = []
        for i in range(tSteps+1):
            B.append([])

        columnFound = False
        col = None

        for i in range(nFiles):
            file = open(os.path.join(os.getcwd(), sys.argv[1], "Macchiato_PetriNet_Places_%d.csv" % (i+1)))
            l = -1
            A = []
            for line in file:
                l += 1
                sLine = line.split(",")
                if l == 0:
                    continue
                if l == 1:
                    if not columnFound:
                        for sl in range(len(sLine)):
                            if sLine[sl] == P:
                                col = sl
                                print("\t>>Place found at column %d" % col)
                                columnFound = True
                                break
                else:
                    if len(sLine) == 1:
                        break
                    elif not columnFound:
                        sys.exit("Error: Specifed place \"%s\" not found!" % P)
                    # print(col, sLine[col])
                    A.append([float(sLine[1]), int(sLine[col])])
            # if l > 1:
            #     start = 0
            #     for t in range(tSteps):
            #         T = deltaT*t
            #         if T == 0.0:
            #             B[t].append(A[0][1])
            #             continue
            #         for s in range(start,len(A)):
            #             if s < start:
            #                 continue
            #             print(s,start)
            #             if A[s][0] > T:
            #                 start = s
            #                 if len(A)-1 == s:
            #                     if endStretch:
            #                         B[t].append(A[-1][1])
            #                     continue
            #                     break
            #                 B[t].append(A[s-1][1])
            #                 # print(s-1, A[s-1][1])
            #                 break
            #     if endStretch is True:
            #         B[-1].append(A[-1][1])
            # # print(B[-1])
            t = 0
            T = 0.0
            #B[0].append(A[0][1])
            for a in range(1,len(A)):
                if A[a][0] >= T:
                    while True:
                        t += 1
                        T += deltaT
                        if T <= TMax:
                            # print(t,T,A[a][0],A[a][1])
                            B[t-1].append(A[a-1][1])
                        else:
                            break
                        if A[a][0] <= T:
                            break
            if endStretch:
                t += 1
                T += deltaT
                while True:
                    t += 1
                    T += deltaT
                    if T <= TMax:
                        B[t].append(A[-1][1])
                    else:
                        break

        results = []
        t = 0.0
        output = open(os.path.join(os.getcwd(), "%s_%s_averages.csv" % (os.path.split(os.path.dirname(os.path.join(os.getcwd(), sys.argv[1])))[1], P)), "w")
        output.write("time,simulations running,mean,std error\n")
        for b in range(len(B)):
            C = 0.0
            Ce = 0.0
            for c in B[b]:
                C+=c
            if len(B[b]) == 0:
                assert C==0
                C = results[-1][0]
                Ce = results[-1][1]
            else:
                C /= len(B[b])
                Ce = np.std(B[b])/math.sqrt(len(B[b]))
            print("%r\t| %.3f\t| %r\t\t| %r +/- %r |" % (b,t,len(B[b]),C,Ce))
            output.write("%f,%d,%r,%r\n" % (t,len(B[b]),C,Ce))
            results.append([C,Ce,t])
            t+=deltaT

        rr = []
        cc = []
        ee = []
        for r in results:
            rr.append(r[2])
            cc.append(r[0])
            ee.append(r[1])
        plt.errorbar(rr,cc,yerr=ee)
        plt.title(P)
        plt.xlabel('Time')
        plt.ylabel('Average Tokens')
        plt.savefig('%s_%s_averages.png' % (sys.argv[1], P))
        plt.clf()

    output.close()


if __name__ == "__main__":
    main()
