#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import sys
import math
import time
import random
import numpy as np
import copy
# Third party libraries
# import matplotlib.pyplot as plt
from pyfmi import load_fmu
# Macchiato
import PetriNet as mpn
import Macchiato

class pnbg(object):
    def __init__(self, name, pn, fmuPath, inputs, wd=None, tMax=100.0, tStep=10.0):
        """
        Add documentation

        Parameters
        ----------
        name : string
            Name of model to use
        pn : string OR mpn.PetriNet
        * If given string, attempts to read as path to an .mpn file
        * If given mpn.PetriNet, sets self.pn to given object
        fmuPath : string
            Path to Bond Graph FMU file

        Attributes
        ----------
        ...
        ...
        ...

        """
        self.name = name
        self.pn = mpn.PetriNet(name)
        self.setPN(pn)
        if wd is not None:
            os.chdir(wd)

        # Bond Graph
        self.model = load_fmu(fmuPath)
        self.inputObj=(inputs, self.inputFunction)

        self.tMax = tMax
        self.tStep = tStep

        self.results = []

        self.pfile, self.tfile, self.tlist = self.pn.writeNetStart(self.pn.runMode)

    def inputFunction(self, t):
        """
        Control of Bond Graph by Petri Net status and time

        Returns
        ----------
        v1, v2, v3... : float
            Must return as many values as anticipated by the FMU

        """
        pass

    def netUpdate(self, t):
        """
        Effects changes to Petri Net based on status of the Bond Graph

        Parameters
        ----------
        t : float
            Clock time of updated net

        Returns
        ----------
        update : boolean
            Indicates if changes to the Petri Net have been made

        """
        update = False
        return update

    def newPN(self, pnNew):
        """
        Updates self.pn with accepted new verion of the Petri Net for next step and writes output

        Parameters
        ----------
        pnNew : mpn.PetriNet
            New version of the Petri Net object

        """
        self.pn = copy.deepcopy(pnNew)
        self.pn.writeNet(self.pfile, self.tfile, self.tlist, self.pn.runMode)

    def endfiles(self):
        """
        Ends Petri Net output file

        """
        self.pn.placesSummary(self.pn.runMode, tOut=True, pfile=self.pfile)
        self.pfile.close()
        self.tfile.close()
        self.tlist.close()

    def setPN(self, pn):
        """
        Sets up Petri Net object to interface with Bond Graph/FMU

        Parameters
        ----------
        pn : string OR mpn.PetriNet
        * If given string, attempts to read as path to an .mpn file
        * If given mpn.PetriNet, sets self.pn to given object

        """
        rpn = None
        if type(pn) is str:
            rpn, _ = Macchiato.read(pn)
        elif type(pn) is mpn.PetriNet:
            rpn = pn
        else:
            raise TypeError("pn is of unknown type: %r" % type(pn))
        if type(rpn) is not mpn.PetriNet:
            raise RuntimeError("Failed to properly set Petri Net")
        rpn.name = self.pn.name
        self.pn = rpn
        if self.pn.units not in ["seconds", "sec", "s"]:
            print("-"*80+"\nWarning: FMU integration uses seconds. Petri Net units are set to \"%s\", but values will be treated as seconds!\n"%(self.pn.units)+"-"*80)
            time.sleep(5)

    def processResults(self, lables):
        """
        Extracts and records results to file after simulations

        Parameters
        ----------
        labels : list of string objects
            The labels of system varriables to be extracted from the model, specified in the form in which they appear in Modelica

        """
        lables = ["time"] + lables
        pn = self.pn
        procRes = {}
        for name in lables:
            procRes[name] = np.array([])
            for r in range(len(self.results)):
                procRes[name] = np.append(procRes[name], self.results[r][name])

        path = os.path.join(os.getcwd(), pn.name, "%s_FMU_%d.csv" % (pn.name, pn.time))
        rfile = open(path, "w")
        rfile.write("Time")
        for n in range(1,len(lables)):
            rfile.write(",%s" % lables[n])
        rfile.write("\n")
        for i in range(len(procRes[lables[0]])):
            for n in range(len(lables)):
                rfile.write("%f," % procRes[lables[n]][i])
            rfile.write("\n")
        rfile.close()

    def run(self):
        """
        Runs model

        """
        begin = False
        big = False
        first = True
        transExit = False
        while True:
            t0 = self.pn.clock
            #print(self.pn.step)
            if t0 >= self.tMax:
                break
            #self.pn.time = self.pn.step
            pnNew = copy.deepcopy(self.pn)
            pnNew.run(1, verbose=False, fileOutput=False)
            t1 = pnNew.clock
            opts = self.model.simulate_options()
            if not t1 > t0:
                self.newPN(pnNew)
                continue
            ts0 = t0
            ts1 = ts0 + self.tStep
            while True:
                long = False
                if not first:
                    opts["initialize"] = False
                else:
                    first = False
                    long = True
                stop = False

                # Disabled for now
                # begin = False
                # self.cList[0].append(t0)
                # c = 1
                # for p in self.concern:
                #     self.cList[c].append(self.pn.places[p].tokens)
                #     if self.pn.places[p].tokens:
                #         begin = True
                #         # break
                #     c += 1
                begin = True

                tStep = copy.copy(self.tStep)
                if big:
                    tStep = copy.copy(self.bigstep)
                if begin:
                    if ts0+tStep < t1:
                        ts1 = ts0 + tStep
                    else:
                        ts1 = t1
                        stop = True
                else:
                    ts1 = t1
                    stop = True
                ### Feb 2020
                if long:
                    ts1 = t1
                ###
                transExit = pnNew.transExit
                placeExit = pnNew.placeExit
                if len(self.results):
                    if ts0 < 0.999999999*self.results[-1]["time"][-1] or ts0 > 1.000000001*self.results[-1]["time"][-1]:
                        raise RuntimeError("Petri Net/FMU clock mismatch (%.f vs %.f)" % (ts0, self.results[-1]["time"][-1]))
                lt = time.localtime()[:6]
                print("\nFMU simulation from %.3f to %.3f seconds (subsection of %.3f seconds from %.3f to %.3f seconds), commencing at %04d/%02d/%02d %02d:%02d:%02d." % (ts0, ts1, (t1-t0), t0, t1, lt[0], lt[1], lt[2], lt[3], lt[4], lt[5]))
                self.results.append(self.model.simulate(start_time=ts0, final_time=ts1, input=self.inputObj, options=opts))
                ts0 += tStep
                ### Feb 2020
                if long:
                    ts0 = t1
                ###
                pnChange = self.netUpdate(ts1)
                if pnChange:
                    self.pn.step += 1
                    self.pn.clock = ts1
                    self.pn.writeNet(self.pfile, self.tfile, self.tlist, self.pn.runMode)
                    break
                elif stop or long:
                    self.newPN(pnNew)
                    break

                # What was this for?
                # big = False
                # for imp in self.important:
                #     if abs((self.results[-1][imp][-1]-self.results[-1][imp][-2])/(self.results[-1]["time"][-1]-self.results[-1]["time"][-2])) < 1:
                #         big = True
                #         break

            if transExit or placeExit:
                print("Terminate conidition(s) activated in Petri Net")
                if transExit:
                    print("\t--Transition maximum fire count")
                if placeExit:
                    print("\t--Place token limit")
                break
            # if placeExit:
            #     print("")
            #     break
        self.endfiles()
