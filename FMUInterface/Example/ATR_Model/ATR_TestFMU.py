#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

###############################################################################
# This script will simulate one hour of reactor operation under ideal
# conditions for reference purposes.
#
# Command line arguments:
# [1] : Path to FMU
###############################################################################

# Inbuilt libraries
import os
import sys
import copy
import math
import time
import random
from pyfmi import load_fmu
import numpy as np
import matplotlib.pyplot as plt

def inputFunction(t):
    fuelThIn = (9.2E8)/(450*24) # W
    coolTR=4.444 # kg/s
    coolTin=530 # K
    fuelC=1.3475E+03 # J/K
    fuelToCladR=8.6877E-03 # K/W
    cladC=2.1845E+02 # J/K
    cladToCoolR=1.0148E-04 # K/W
    coolC=4.5049E+05 # J/K
    fuelToFuelR=2.6198E+01 # K/W
    cladToCladR=2.3613E+01 # K/W
    spCap=4182 # J/(kg*K)

    return fuelThIn, coolTR, coolTin, fuelC, fuelToCladR, cladC, cladToCoolR, coolC, fuelToFuelR, cladToCladR, spCap

def main():
    inputs = ['fuelThIn', 'coolTR', 'coolTin', 'fuelC', 'fuelToCladR', 'cladC', 'cladToCoolR', 'coolC', 'fuelToFuelR', 'cladToCladR', 'spCap']
    model = load_fmu(os.path.join(os.getcwd(), sys.argv[1]))
    inputObj=(inputs, inputFunction)
    opts = model.simulate_options()
    print('Beginning simulation')
    model.simulate(start_time=0, final_time=3600, input=inputObj, options=opts)
    print('Complete')

if __name__ == '__main__':
    main()
