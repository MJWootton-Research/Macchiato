#!/usr/bin/python
# Inbuilt libraries
import os
import sys
import copy
import math
import time
import random
# Third party libraries
import numpy as np
# import matplotlib.pyplot as plt
from pyfmi import load_fmu
# Macchiato modules
import Macchiato
import PetriNet
import FMUInterface.FMUInterface as fmui

class atr(fmui.pnfmu):
    def __init__(self, name, pn, fmuPath, inputs, wd=None, tMax=3600.0, tStep=10.0):
        fmui.pnfmu.__init__(self, name, pn, fmuPath, inputs, wd, tMax, tStep)

        # Critical Values
        self.fuelMelted = False
        self.fuelMeltedWhen = None
        self.coolant_freeze = 273.15 # K
        self.uo2_melt = 3138.0 # K [PubChem]
        self.zr2_melt = 2122.0 # K [Whitmarsh 1962]
        self.damageThreshold_uo2 = self.uo2_melt
        #   NB: this is the temperature of Zr-2 exothermic reactions
        #       --> unrealistic to simulate above this temperature
        # self.damageThreshold_zr2 = 1200+273.15 # K [KfK 3973, Erbacher & Leistikow 1985]
        self.usnrcClad = 1477 # K [U.S. Nuclear Regulatory Commission]
        self.damageThreshold_zr2 = 1500


        # Parameters
        self.fuelThIn = (9.2E8)/(450*24) # W
        self.coolTR=4.444 # kg/s
        self.coolTin=530 # K
        self.fuelC=1.3475E+03 # J/K
        self.fuelToCladR=8.6877E-03 # K/W
        self.cladC=2.1845E+02 # J/K
        self.cladToCoolR=1.0148E-04 # K/W
        self.coolC=4.5049E+05 # J/K
        self.fuelToFuelR=2.6198E+01 # K/W
        self.cladToCladR=2.3613E+01 # K/W
        self.spCap=4182 # J/(kg*K)

        # Actions
        self.highPressureBegin = None
        self.lowPressureBegin = None
        self.reactorShutdownBegin = None
        self.highPressureFlow = self.coolTR*(4.67/100.0)
        self.lowPressureFlow = self.coolTR*(1.40/100.0)

        self.shutdownP0 = 0.06
        self.shutdownLamba = math.log(4)/3600.0

    # def inputFunction(t):
    #     fuelThIn = (9.2E8)/(450*24)
    #     coolTR=4.444
    #     coolTin=530
    #     fuelC=1.3475E+03
    #     fuelToCladR=8.6877E-03
    #     cladC=2.1845E+02
    #     cladToCoolR=1.0148E-04
    #     coolC=4.5049E+05
    #     fuelToFuelR=2.6198E+01
    #     cladToCladR=2.3613E+01
    #     spCap=4182
    #
    #     return fuelThIn, coolTR, coolTin, fuelC, fuelToCladR, cladC, cladToCoolR, coolC, fuelToFuelR, cladToCladR, spCap

    def inputFunction(self, t):
        """
        Control of Bond Graph by Petri Net status and time

        Returns
        ----------
        cvFIn : float
            Reactor Bond Graph coolant volume Flow in
        cvEOut : float
            Reactor Bond Graph coolant volume Effort out
        ctFIn : float
            Reactor Bond Graph coolant temperature Flow in
        ftFIn : float
            Reactor Bond Graph fuel temperature Flow in

        """
        place = self.pn.places

        # Variable
        fuelThIn_def = self.fuelThIn # Fuel thermal power
        coolTR_def = self.coolTR # Coolant mass transfer rate
        coolTin_def = self.coolTin # Coolant incoming temperature
        fuelThIn = 0.0

        # System parameters
        spCap = self.spCap # Specific heat of water
        fuelC = self.fuelC # Fuel thermal capacity
        cladC = self.cladC # Cladding thermal capacity
        coolC = self.coolC # Coolant thermal capacity
        fuelToCladR = self.fuelToCladR # Fuel to cladding thermal transfer
        cladToCoolR = self.cladToCoolR # Cladding to coolant thermal transfer
        fuelToFuelR = self.fuelToFuelR # Fuel to fuel thermal transfer
        cladToCladR = self.cladToCladR # Cladding to cladding thermal transfer

        # Coolant
        coolTR = coolTR_def*((4.0-place['PCCN'].tokens)/4.0)*(1.0-(place['PIH2'].tokens*0.25))*(1.0-(place['PRCC2'].tokens*0.25))
        coolTin = coolTin_def
        # Not in shutdown condensation
        if not place['PTIVC1'].tokens+place['PTIVC2'].tokens:
            coolTR *= 0.5**(place['PPTF'].tokens+(1-place['PTB1'].tokens)+(1-place['PCD1'].tokens))
            onlinePumps = place['PFPRN1'].tokens + place['PFPRN2'].tokens + place['PFPRN3'].tokens
            if onlinePumps == 1:
                coolTR /= 2.0
            elif onlinePumps == 0:
                coolTR /= 1000.0
        # In shutdown condensation
        else:
            coolTR *= 0.006
            coolTR *= (8.0-place['PSCFT'].tokens)/8.0
            if not place['POHP'].tokens:
                coolTR /= 1000.0
            # coolTin = self.shutdownCondensationTemp

        if place['PPASA'].tokens and self.highPressureBegin is None:
            self.highPressureBegin = t
        if self.highPressureBegin is not None and self.lowPressureBegin is None:
            coolTR += (place['PPASA'].tokens/8.0)*self.highPressureFlow
        if (place['PLPRDO1'].tokens or place['PLPRDP1'].tokens) and self.lowPressureBegin is None:
            self.lowPressureBegin = t
        if self.lowPressureBegin is not None:
            coolTR += (place['PLPRDO1'].tokens + 0.5*place['PLPRDP1'].tokens)*self.lowPressureFlow

        # Fuel
        fuelThIn = fuelThIn_def
        if (place['PSDS1C'].tokens or place['PSDS2C'].tokens or place['PSDS2US'].tokens) and self.reactorShutdownBegin is None:
            self.reactorShutdownBegin = t
        if self.reactorShutdownBegin is not None:
            fuelThIn = fuelThIn_def*self.shutdownP0*math.exp(self.shutdownLamba*(self.reactorShutdownBegin-t))

        return fuelThIn, coolTR, coolTin, fuelC, fuelToCladR, cladC, cladToCoolR, coolC, fuelToFuelR, cladToCladR, spCap

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
        place = self.pn.places
        update = False

        # Overheating check
        for i in range(1,25):
            # Fuel temperature
            if self.results[-1]['Fuel%d.e' % i][-1] > self.damageThreshold_uo2:
                if not place['PFuelOverheat'].tokens:
                    place['PFuelOverheat'].changeTokens(1)
                    update = True
            # Cladding temperature
            if self.results[-1]['Cladding%d.e' % i][-1] > self.damageThreshold_zr2:
                if not place['PCladOverheat'].tokens:
                    place['PCladOverheat'].changeTokens(1)
                    update = True

            if self.results[-1]['Cladding%d.e' % i][-1] > self.usnrcClad:
                if not place['PCladTempShutdown'].tokens:
                    place['PCladTempShutdown'].changeTokens(1)
                    update = True

        if place['PFuelOverheat'].tokens+place['PCladOverheat'].tokens:
            self.pn.placeExit = True

        return update

    def processResults(self, lables):
        """
        Extracts and records results to file after simulations

        Parameters
        ----------
        labels : list of string objects
            The labels of system varriables to be extracted from the model, specified in the form in which they appear in Modelica

        """
        lables = ['time'] + lables # Yes, I know about the spelling mistake
        pn = self.pn
        procRes = {}
        for name in lables:
            procRes[name] = np.array([])
            for r in range(len(self.results)):
                procRes[name] = np.append(procRes[name], self.results[r][name])

        path = os.path.join(os.getcwd(), pn.name, '%s_FMU_%d.csv' % (pn.name, pn.time))

        all = ['fuelThIn', 'coolTR', 'coolTin']
        mm = ['Coolant', 'Cladding', 'Fuel']

        data = 'Time'
        for wr in all:
            data += ','+wr
        for wr in mm:
            for ap in ['min', 'max']:
                data += ','+wr+'.'+ap
        data += '\n'
        for i in range(len(procRes[lables[0]])):
            data += f'{procRes["time"][i]}'
            for label in all:
                data += f',{procRes[label][i]}'
            for mLabel in mm:
                mData = []
                for lLabel in lables:
                    if mLabel in lLabel:
                        mData.append(procRes[lLabel][i])
                data += f',{np.min(mData)},{np.max(mData)}'
            data += '\n'
        # rfile = open(path, 'w')
        # rfile.write('Time')
        # for n in range(1,len(lables)):
        #     rfile.write(',%s' % lables[n])
        # rfile.write('\n')
        # for i in range(len(procRes[lables[0]])):
        #     for n in range(len(lables)):
        #         rfile.write('%f,' % procRes[lables[n]][i])
        #     rfile.write('\n')

        rfile = open(path, 'w')
        rfile.write(data)
        rfile.close()

def run(params):
    # Path to FMU
    fmu = params[2]
    # Start and end simulation indicies
    if ':' in params[3]:
        m = int(params[3].split(':')[0])
        n = int(params[3].split(':')[1])
    else:
        m = 0
        n = int(params[3])

    if m >= n:
        raise ValueError('Start point (%d) must be greater than end point (%d)' % (m,n))

    print('Executing %d simulations (%d to %d)' % (n-m, m, n-1))

    # Optional working directory change
    if len(params) == 5:
        wd = params[-1]
        os.chdir(wd)
    wd = os.getcwd()

    # Get Petri Net
    if type(params[1]) is str:
        pn, _ = Macchiato.read(params[1])
    elif type(params[1]) is PetriNet.PetriNet:
        pn = params[1]
    else:
        raise TypeError('Invalid type for Petri Net (%r)' % type(params[1]))

    # Add additional objects to Petri Net to facilitate interaction with FMU
    pn.trans['TUnsafe'].maxFire = None
    pn.addTrans('TUnsafeCounter', delay=25.0, maxFire=1)
    pn.trans['TUnsafeCounter'].addInArc('PUnsafe')
    pn.trans['TUnsafeCounter'].addOutArc('PUnsafe')
    pn.addPlace('PFuelOverheat')
    pn.addPlace('PCladOverheat')
    pn.addTrans('TFuelOverheat', maxFire=1)
    pn.addTrans('TCladOverheat', maxFire=1)
    pn.trans['TFuelOverheat'].addInArc('PFuelOverheat')
    pn.trans['TFuelOverheat'].addOutArc('PFuelOverheat')
    pn.trans['TCladOverheat'].addInArc('PCladOverheat')
    pn.trans['TCladOverheat'].addOutArc('PCladOverheat')

    pn.addPlace('PCladTempShutdown')
    pn.addPlace('PCladTempShutdownLock')
    pn.addTrans('TCladTempShutdown')
    pn.trans['TCladTempShutdown'].addInArc('PCladTempShutdown')
    pn.trans['TCladTempShutdown'].addOutArc('PCladTempShutdown')
    pn.trans['TCladTempShutdown'].addInArc('PCladTempShutdownLock', type='inh')
    pn.trans['TCladTempShutdown'].addOutArc('PCladTempShutdownLock')
    pn.trans['TCladTempShutdown'].addOutArc('PTIVD0')

    # Convert units from seconds from hours
    for t in pn.trans:
        if pn.trans[t].uniform is not None:
            pn.trans[t].uniform *= 3600.0
        if pn.trans[t].delay is not None:
            pn.trans[t].delay *= 3600.0
        if pn.trans[t].weibull is not None:
            pn.trans[t].weibull[0] *= 3600.0
            if len(pn.trans[t].weibull) == 3:
                pn.trans[t].weibull[2] *= 3600.0
        if pn.trans[t].cyclic is not None:
            pn.trans[t].cyclic[0] *= 3600.0
            pn.trans[t].cyclic[1] *= 3600.0
    pn.units = 'sec'

    # List of input variables
    inputs = [
              'fuelThIn',
              'coolTR',
              'coolTin',
              'fuelC',
              'fuelToCladR',
              'cladC',
              'cladToCoolR',
              'coolC',
              'fuelToFuelR',
              'cladToCladR',
              'spCap'
             ]
    # Set up variables of interest for analysis
    interest = ['fuelThIn', 'coolTR', 'coolTin']
    for i in ['Coolant', 'Cladding', 'Fuel']:
        for j in range(1,25):
            interest.append('%s%d.e' % (i,j))
    # Record time at which simulation bach begins
    beginTime = time.time()
    # Loop over required simulations
    for i in range(m,n):
        lt = time.localtime()[:6]
        print('%d: %04d/%02d/%02d %02d:%02d:%02d' % (i, lt[0], lt[1], lt[2], lt[3], lt[4], lt[5]))
        pn.time = i # Used as label, not anything to do with actual time
        # Set up new instance of hybrid model
        model = atr(pn.name,
                    pn,
                    fmu,
                    inputs,
                    wd=wd,
                    tMax=4.0*365.25*24*3600.0,
                    tStep=8766.0*3600.0)
        # Run hyprid simulation
        model.run()
        # Results processing
        model.processResults(interest)
    # Record end time of simulation bach
    endTime = time.time()
    duration = (endTime-beginTime)/3600.0
    print('%d simulations complete in duration of %.3g hours (%.3g mintues per simulation)' % (n-m,duration,(duration/(n-m))*60.0))

def main():
    # Command line arguments:
    #   [1] path to MPN input file
    #   [2] path to FMU input file
    #   [3] end point (n), or start and end point (m:n)
    #   [4] reset working directory (optional, but necessary if running in directory differnt to location of this file)
    run(sys.argv)

if __name__ == '__main__':
    main()
