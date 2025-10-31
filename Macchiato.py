#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
============================================================================
███╗   ███╗ █████╗  ██████╗ ██████╗██╗  ██╗ ██╗  █████╗ ████████╗ ██████╗
████╗ ████║██╔══██╗██╔════╝██╔════╝██║  ██║ ██║ ██╔══██╗╚══██╔══╝██╔═══██╗
██╔████╔██║███████║██║     ██║     ███████║ ██║ ███████║   ██║   ██║   ██║
██║╚██╔╝██║██╔══██║██║     ██║     ██╔══██║ ██║ ██╔══██║   ██║   ██║   ██║
██║ ╚═╝ ██║██║  ██║╚██████╗╚██████╗██║  ██║ ██║ ██║  ██║   ██║   ╚██████╔╝
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝╚═╝  ╚═╝ ╚═╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝

    Programmer ~ Noun: One who converts coffee into code.

----------------------------------------------------------------------------

Welcome to Macchiato – A Simple and Scriptable Petri Nets Implementation
Version 1-8
(c) Dr. Mark James Wootton 2016-2025
============================================================================

This file is comprised of two main sections. The former provides utilities
for file manipulation and running simulation batches. The functions and
object class definitions for the modelling itself are contained within the
latter.

"""

# Python Modules
import os
import re
import sys
import copy
import math
import time
import random
import shutil
from fnmatch import filter
import argparse
import textwrap
import subprocess
import collections
from platform import system
from builtins import print as speak

############################################################################
# File and Simulation Management Utilities
############################################################################
def main():
    intro=f'''
    Macchiato – A Simple and Scriptable Petri Nets Implementation
    Version 1-8
    (c) Dr. Mark James Wootton 2016-2025
    '''
    # Command line arguments and help text
    parser = argparse.ArgumentParser(prog='Macchiato', description=intro, formatter_class=RawFormatter,epilog=None)
    parser.add_argument('file', nargs=1, metavar='input_file', type=argparse.FileType('r'), help='*.mpn file containing a Petri Net')
    parser.add_argument('nSims', nargs='?', default=None, type=int, help='Set fixed number of simulations to run [optional]')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode (slow)')
    parser.add_argument('-c', '--concatenate', action='store_true', help='Simulation results are concatenated as a single set of three files for place, transition, and firings.')
    parser.add_argument('-p', '--places', nargs='*', default=[], help='Limit file output to a list of places. Format as P1:P2:P3 etc.')
    parser.add_argument('-t', '--trans', nargs='*', default=[], help='Limit file output to a list of transitions. Format as T1:T2:T3 etc.')
    args = parser.parse_args()

    # Get Petri Net and simulation parameters
    pn, rp = read(args.file[0].name)

    # Process place and transition print lists
    keyerr = ''
    keyerrP = ''
    keyerrT = ''
    for p in args.places:
        if p not in pn.places:
            keyerrP += f'"{p}", '
    for t in args.trans:
        if t not in pn.trans:
            keyerrT += f'"{t}", '
    if keyerrP and keyerrT:
        keyerr += f'A request for file output of non-existent places and transitions has been made:   -- Places: {keyerrP[:-2]}   -- Transitions: {keyerrT[:-2]}'
    elif keyerrP:
        keyerr += f'A request for file output of non-existent places has been made:   -- Places: {keyerrP[:-2]}'
    elif keyerrT:
        keyerr += f'A request for file output of non-existent transitions has been made:   -- Transitions: {keyerrT[:-2]}'
    if keyerr:
        raise KeyError(keyerr)
    pn.placesToPrint = args.places
    pn.transToPrint = args.trans

    # Run specified simulation
    lt = time.localtime()[:6]
    print('='*80 + '\nBeginning simulations (%04d-%02d-%02d %02d:%02d:%02d)\n' % (lt[0], lt[1], lt[2], lt[3], lt[4], lt[5]) + '='*80)
    if not args.verbose:
        blockPrint()
    wall = time.time()
    repeat(pn, rp[0], maxSteps=rp[1], simsFactor=rp[2], fixedNumber=args.nSims, history=rp[3], analysisStep=rp[4], fileOutput=rp[5], endOnly=rp[6], concatenate=args.concatenate)
    if not args.verbose:
        enablePrint()
    lt = time.localtime()[:6]
    print('='*80 + '\nSimulations complete after %.2g hrs (%04d-%02d-%02d %02d:%02d:%02d)\n' % (float(time.time()-wall)/float(3600), lt[0], lt[1], lt[2], lt[3], lt[4], lt[5]) + '='*80)
    print(os.getcwd())

def silence(*args):
    """
    Dummy function to replace print in low-verbosity mode
    """
    return

def blockPrint():
    """
    Silences textual output to terminal from Macchiato
    """
    global print
    print = silence

def enablePrint():
    """
    Reenables textual output to terminal from Macchiato
    """
    global print
    print = speak

def expandReset(pn, reset):
    """
    Uses glob-style filtering to expand reset place lists

    Parameters
    ----------
    pn : PetriNet object
        Petri net containing the place list to check
    reset : list
        Unexpanded reset relation place list

    Returns
    ----------
    newReset : list
        New list of places for the reset transition relation
    """
    if True in [globChar in ':'.join(reset) for globChar in ['?', '*', '[']]:
        newReset = []
        for rPlace in reset:
            expansion = filter(pn.places, rPlace)
            if not len(expansion):
                print(f'Warning: "{rPlace}" matches no places.')
            newReset += [expPlace for expPlace in expansion if expPlace not in newReset]
        for rPlace in newReset:
            assert rPlace in pn.places, (f'{rPlace} not found in places list -- cannot create reset relation.')
        print(reset)
        print(newReset)
        return newReset
    else:
        return reset

def read(file):
    """
    Reads Macchiato Petri Net (.mpn) files and returns structure in PetriNet
    object

    Parameters
    ----------
    file : string
        File path of .mpn file

    Returns
    ----------
    pn : PetriNet object
        Petri Net as described and parametised by .mpn file
    rp : list
        Parameters for repeated simulation execution

    """
    # Petri Net Parameters
    name = 'unnamed'
    units = 'hrs'
    runMode = 'schedule'
    dot = False
    visualise = None
    details = True
    useGroup = True
    orientation = None
    debug = False
    dotLoc = None

    # Run Parameters
    maxClock = 1E6
    maxSteps = 1E12
    simsFactor = 1.5E3
    history = False
    analysisStep = 1E2
    fileOutput = True
    endOnly = False

    mode = None

    # Check file type
    if not file.endswith('.mpn'):
        print('Warning: Given file is not ".mpn"')
        time.sleep(1)
    for line in open(file, 'r'):
        # Skip blank lines
        if not len(line.lstrip()):
            continue
        # Skip comment lines
        if line.lstrip()[0] == '#':
            continue
        # Ignore line-end comments
        line = line.split('#')[0]

        # Split line for analysis
        spln = line.split()

        # Cut white space characters from line for easy inclusion in error messages
        line = line.strip()

        if spln[0] in ['Places', 'Transitions']:
            # Create PetriNet object
            if mode is None:
                pn = PetriNet(name=name, units=units, runMode=runMode, dot=dot,
                              visualise=visualise, details=details, useGroup=useGroup,
                              orientation=orientation, debug=debug, dotLoc=dotLoc)
            mode = spln[0]
            continue

        if mode is None:
            # Petri Net Parameters
            if spln[0] == 'name':
                name = spln[1]
            elif spln[0] == 'units':
                units = spln[1]
            elif spln[0] == 'runMode':
                runMode = spln[1]
            elif spln[0] == 'dot':
                dot = (spln[1].upper() == 'TRUE')
            elif spln[0] == 'visualise':
                if spln[1] == 'None':
                    visualise = None
                else:
                    visualise = spln[1]
            elif spln[0] == 'details':
                details = (spln[1].upper() == 'TRUE')
            elif spln[0] == 'useGroup':
                useGroup = (spln[1].upper() == 'TRUE')
            elif spln[0] == 'orientation':
                if spln[1] == 'None':
                    orientation = None
                else:
                    orientation = spln[1]
            elif spln[0] == 'debug':
                debug = (spln[1].upper() == 'TRUE')
            elif spln[0] == 'dotLoc':
                dotLoc = spln[1]
                if len(spln) > 2:
                    for i in spln[2:]:
                        dotLoc += ' %s' % i
                elif spln[1] == 'None':
                    dotLoc = None

            # Run Parameters
            elif spln[0] == 'maxClock':
                maxClock = float(spln[1])
            elif spln[0] == 'maxSteps':
                maxSteps = float(spln[1])
            elif spln[0] == 'simsFactor':
                simsFactor = float(spln[1])
            elif spln[0] == 'history':
                history = (spln[1].upper() == 'TRUE')
            elif spln[0] == 'analysisStep':
                analysisStep = float(spln[1])
            elif spln[0] == 'fileOutput':
                fileOutput = (spln[1].upper() == 'TRUE')
            elif spln[0] == 'endOnly':
                endOnly = (spln[1].upper() == 'TRUE')

            else:
                raise KeyError('Unknown parameter')

        # Add places to Petri Net
        elif mode == 'Places':
            label = spln[0]
            tokens = 0
            group = None
            # Slightly odd code here for legacy reasons.
            if len(spln) > 1:
                if 'GROUP' in spln[-2]:
                    # print(spln)
                    group = int(spln[-1])
                    if len(spln) > 3:
                        tokens = int(spln[1])
                else:
                    tokens = int(spln[1])
            pn.addPlace(label, tokens=tokens, group=group)
        # Add transitions to Petri Net
        elif mode == 'Transitions':
            tMode = None
            label = ''
            type = 'instant'
            read = ''
            for info in spln:
                if info == 'IN':
                    tMode = 'IN'
                    continue
                elif info == 'OUT':
                    tMode = 'OUT'
                    continue
                elif info == 'RESET':
                    tMode = 'RESET'
                    continue
                elif info == 'MAX':
                    tMode = 'MAX'
                    continue
                elif info == 'VOTE':
                    tMode = 'VOTE'
                    continue
                elif info == 'GROUP':
                    tMode = 'GROUP'
                    continue

                # Get transition type
                if tMode == None:
                    read = info.split(':')
                    label = read[0]
                    try:
                        type = read[1]
                    except:
                        raise KeyError('Error reading transition type from: %r\n[%s]' % (read, line))
                    if type not in ['instant', 'rate', 'uniform', 'delay', 'weibull', 'beta', 'lognorm', 'cyclic']:
                        if not type:
                            raise KeyError('No type given for transition "%s"' % (label))
                        raise KeyError('Unrecognised type "%r" for transition "%s"' % (type, label))

                    try:
                        if type == 'instant':
                            pn.addTrans(label)
                        elif type == 'rate':
                            pn.addTrans(label, rate=float(read[2]))
                        elif type == 'uniform':
                            pn.addTrans(label, uniform=float(read[2]))
                        elif type == 'delay':
                            pn.addTrans(label, delay=float(read[2]))
                        elif type == 'weibull':
                            mt = float(read[2])
                            beta = float(read[3])
                            try:
                                sigma = float(read[4])
                            except:
                                sigma = 0.0
                            pn.addTrans(label, weibull=[mt, beta, sigma])
                        elif type == 'beta':
                            alpha = float(read[2])
                            beta = float(read[3])
                            try:
                                scale = float(read[4])
                            except:
                                scale = 1
                            pn.addTrans(label, beta=[alpha, beta, scale])
                        elif type == 'lognorm':
                            pn.addTrans(label, lognorm=[float(read[2]), float(read[3])])
                        elif type == 'cyclic':
                            pn.addTrans(label, cyclic=[float(read[2]), float(read[3])])
                    except ValueError:
                        sys.exit('ValueError creating transition "%s" with input: %r\n[%s]' % (label, read, line))
                    except KeyError:
                        sys.exit('KeyError creating transition "%s" with input: %r\n[%s] (posible duplicated name)' % (label, read, line))
                    except:
                        sys.exit('Miscellaneous error creating transition "%s" with input: %r\n[%s]' % (label, read, line))

                # Add incoming arcs to transition
                elif tMode == 'IN':
                    type = 'std'
                    weight = 1
                    if 'inh' in info:
                        type = 'inh'
                    elif 'pcn' in info or 'pch' in info: # 'pch' appears in Visio macro generated input files instead of 'pcn'
                        type = 'pcn'
                    read = info.split(':')
                    if len(read) > 1 and read[1] not in ['inh', 'pcn']:
                        if type not in ['pcn']:
                            weight = int(read[1])
                        else:
                            weight = float(read[1])
                    pn.trans[label].addInArc(read[0], weight=weight, type=type)
                # Add outgoing arcs to transition
                elif tMode == 'OUT':
                    weight = 1
                    read = info.split(':')
                    if len(read) > 1:
                        badArc = False
                        if 'inh' in info:
                            badArc = 'inhibit'
                        elif 'pcn' in info:
                            badArc = 'place conditional'
                        if badArc is not False:
                            raise ValueError('Attempt to create %s arc from transition, "%s", to place, "%s". Outgoing arcs may only be of standard type, and %s arcs can only run from a place to a transtion.' % (badArc, label, read[0], badArc))
                        weight = int(read[1])
                    pn.trans[label].addOutArc(read[0], weight=weight)
                # Assign places to reset on fire
                elif tMode == 'RESET':
                    pn.trans[label].reset = expandReset(pn, info.split(':'))
                # Set maxium number of times a transition can fire
                elif tMode == 'MAX':
                    pn.trans[label].maxFire = int(info)
                # Create voting threshold
                elif tMode == 'VOTE':
                    pn.trans[label].vote = int(info)
                # Assign grouping to transition
                elif tMode == 'GROUP':
                    pn.trans[label].group = int(info)

    # Return complete PetriNet and simulation run options
    return pn, [maxClock, maxSteps, simsFactor, history, analysisStep, fileOutput, endOnly]

def write(pn, overwrite=False, rp=None, altName=None, path=None):
    """
    Takes Petri Net structure and writes it out to .mpn file

    Parameters
    ----------
    pn : PetriNet object
        The Petri Net to write to .mpn file
    overwrite : boolean (Default: False)
        Allows the overwriting of existing file if True
    rp : list
        Run parameters, uses default values if None (Default: None)
    altName : string (Default: None)
        Provides alternative directory for file output (do not include '.mpn')
    path : string (Default: None)
        Path to save file. Uses current working directory+name if None

    """
    name = pn.name
    if type(altName) is str:
        name = altName
    elif altName is not None:
        raise TypeError('altName given "%r" is type "%r". String required ("%r").' % (altName, type(altName), str))

    # Set-up file path
    if path is None:
        path = os.path.join(os.getcwd(), '%s.mpn' % name)
    if os.path.isfile(path) and not overwrite:
        raise IOError('File "%s" exists, but overwriting is disabled' % path)

    # Create file content
    wr = '# Petri Net Parameters\n'
    wr += '\tname %s\n' % name
    wr += '\tunits %s\n' % pn.units
    wr += '\trunMode %s\n' % pn.runMode
    wr += '\tdot %s\n' % pn.savedot
    wr += '\tvisualise %s\n' % pn.visualise
    wr += '\tdetails %s\n' % pn.details
    wr += '\tuseGroup %s\n' % pn.useGroup
    wr += '\torientation %s\n' % pn.orientation
    wr += '\tdebug %s\n' % pn.debug
    wr += '\tdotLoc %s\n' % pn.dotLoc
    wr += '\n'
    wr += '# Run Parameters\n'
    if type(rp) is list:
        if len(rp) == 5:
            wr += '\tmaxClock %g\n' % rp[0]
            wr += '\tmaxSteps %d\n' % rp[1]
            wr += '\tsimsFactor %g\n' % rp[2]
            wr += '\thistory %s\n' % rp[3]
            wr += '\tanalysisStep %f\n' % rp[4]
            wr += '\tfileOutput %s\n' % rp[5]
            wr += '\tendOnly %s\n' % rp[6]
        else:
            raise IndexError('rp should be of length, 5, received(%d)' % len)
    elif rp is None:
        wr += '\tmaxClock %g\n' % 1E6
        wr += '\tmaxSteps %g\n' % 1E12
        wr += '\tsimsFactor %g\n' % 1.5E3
        wr += '\thistory %s\n' % False
        wr += '\tanalysisStep %g\n' % 1E2
        wr += '\tfileOutput %s\n' % True
        wr += '\tendOnly %s\n' % False
    else:
        raise TypeError('rp given "%r" is type "%r". List required ("%r").' % (altName, type(altName), list))
    wr += '\n'
    wr += '# Build Petri Net\n'
    wr += 'Places\n'
    for p in pn.places:
        wr += '\t%s' % p
        if pn.places[p].tokens:
            wr += ' %d' % pn.places[p].tokens
        if pn.places[p].group is not None:
            wr += ' GROUP %d' % pn.places[p].group
        wr += '\n'
    wr += '\n'
    wr += 'Transitions\n'
    for t in pn.trans:
        wr += '\t%s:' % t
        if pn.trans[t].rate is not None:
            wr += 'rate:%f' % pn.trans[t].rate
        elif pn.trans[t].uniform is not None:
            wr += 'uniform:%f' % pn.trans[t].uniform
        elif pn.trans[t].delay is not None:
            wr += 'delay:%f' % pn.trans[t].delay
        elif pn.trans[t].weibull is not None:
            wr += 'weibull:%f:%f:%f' % (pn.trans[t].weibull[0], pn.trans[t].weibull[1], pn.trans[t].weibull[2])
        elif pn.trans[t].beta is not None:
            wr += 'beta:%f:%f' % (pn.trans[t].beta[0], pn.trans[t].beta[1],pn.trans[t].beta[2])
        elif pn.trans[t].lognorm is not None:
            wr += 'lognorm:%f:%f' % (pn.trans[t].lognorm[0], pn.trans[t].lognorm[1])
        elif pn.trans[t].cyclic is not None:
            wr += 'cyclic:%f:%f' % (pn.trans[t].cyclic[0], pn.trans[t].cyclic[1])
        else:
            wr += 'instant'
        if len(pn.trans[t].inArcs):
            wr += ' IN'
            for p in pn.trans[t].inArcs:
                wr += ' %s' % p
                if pn.trans[t].inArcs[p].weight != 1:
                    wr += ':%r' % pn.trans[t].inArcs[p].weight
                if pn.trans[t].inArcs[p].type != 'std':
                    wr += ':%s' % pn.trans[t].inArcs[p].type
        if len(pn.trans[t].outArcs):
            wr += ' OUT'
            for p in pn.trans[t].outArcs:
                wr += ' %s' % p
                if pn.trans[t].outArcs[p].weight != 1:
                    wr += ':%r' % pn.trans[t].outArcs[p].weight
        if len(pn.trans[t].reset):
            wr += ' RESET '
            for p in pn.trans[t].reset:
                wr += '%s:' % p
            wr = wr[:-1]
        if pn.trans[t].vote is not None:
                wr += ' VOTE %d' % pn.trans[t].vote
        if pn.trans[t].maxFire is not None:
            wr += ' MAX %d' % pn.trans[t].maxFire
        if pn.trans[t].group is not None:
            wr += ' GROUP %d' % pn.trans[t].group
        wr += '\n'

    # Create .mpn file
    mpn = open(path, 'w')
    # Write content to file
    mpn.write(wr)
    # Close .mpn file
    mpn.close()

class RawFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, width, indent):
        return '\n'.join([textwrap.fill(line, width) for line in textwrap.indent(textwrap.dedent(text), indent).splitlines()])

############################################################################
# Petri Net Operational Objects and Methods
############################################################################
def labelCheck(label, ref=None, error=True):
    """
    Function to test object labels for problematic characters and print an
    appropriate warning or raise an exception.

    Parameters
    ----------
    label : string
        Label to test
    ref : string
        Information about object type for print-out
    error : boolean
        If False, a warning is printed with raising an exception (Default is
        True).

    """
    failed = ''
    if ' ' in label:
        failed += '"%s" is an invalid %s, spaces are not permitted\n' % (label, ref)
    if True in [globChar in label for globChar in ['?', '*', '[', ']']]:
        failed += '"%s" is an invalid %s, glob characters are not permitted\n' % (label, ref)
    # if '_' in label:
    #     failed += 'Warning: (%s) Underscores are permitted in %ss but will interfere with conversion to LaTeX\n' % (label, ref)
    # if '-' in label or '\" in label:
    #     failed += 'Warning: (%s) Hyphens and backslashes are permitted in %ss but will prevent rendering Graphviz files\n' % (label, ref)

    if len(failed):
        if error:
            raise ValueError(failed)
        else:
            print(failed)
            time.sleep(1)

def genID(label):
    id = label
    gID = label
    for c in ['-', ':']:
        # print(c, id)
        if c in id:
            id = re.sub(c, '_', id)
    if '_' in gID:
        gID = re.sub('_', '-', label)
    return id, gID

class PetriNet(object):
    """
    A Petri Net, composed of places and transitions, which are connected by arcs.

    Attributes
    ----------
    name : string
        Label for this Petri Net - only used in file output and visualisation
    time : integer
        By default, this is the UNIX timestamp when the Petri Net was
        created. It is also used a label for sequential simulations by the
        'repeat' method.
    units : string
        Unit of time to be used, essentially aesthetic (Default = 'hrs')
    savedot : boolean
        Write dot files (Default = False)
    visualise : string
        Toggle image output file type eg: png, svg... (Default = None for no
        images/.dots only)
    details : boolean
        Toggle simulation details on visualisation
    useGroup : boolean
        Toggle object grouping in visualisation, if a group label has been
        provided. Transitions and places have separte groups. The use of
        grouping has no effect on the simulation process.
    orientation : string
        'rankdir' option for Graphviz/dot, eg) 'LR' for left to right
        orientation. Default is top to bottom.
    runMode : string
    *  all : All non-conflicting transitions are fired simultaneously
    *  single : One transition is randomly selected and fired
    *  stochastic : One transition is selected for firing in proportion to
       its rates (plus instant and fixed delay transitions)
    *  schedule : Schedule based Monte Carlo integration (Default)
    runModes : list
        Permissible options for 'runMode'
    schedule : collections.OrderedDict
        Stores the transition firing scheudle for the 'scheudle' Monte Carlo
        simulation run mode
    debug : boolean
        Run PetriNet object in debug mode (Default = False)
    places : collections.OrderedDict
        All places in the PetriNet
    trans : collections.OrderedDict
        All transitions in the PetriNet
    ready : list
        List of transitions that are ready to fire
    connectivity : list
        Descibes the network of connections between places and transitions
        (not implemented)
    step : integer
        Number of steps taken
    clock : float
        Simulated time accrued
    transFiredTotal : integer
        Total number of transitions fired
    arcsVerified : boolean
        Indicates if all arcs have been checked to see if their places are
        valid
    placeExit : boolean
        Indictes if simulated ended due a place's token limit being exceeded
    transExit : boolean
        Indictes if simulated ended due a transition firing the maximum
        number of times
    history : history object
        Log of the firing history of the Petri Net
    dotLoc : string
        Path to Graphviz's dot.exe
    placesToPrint : list
        If a list of place labels is given, only those places will be
        included in output files
    transToPrint : list
        If a list of transition labels is given, only those transitions will
        be included in output files
    """
    def __init__(self, name=None, units='hrs', runMode='schedule', dot=False,
                 visualise=None, details=True, useGroup=True, orientation=None,
                 debug=False, dotLoc=None, placesToPrint=None,
                 transToPrint=None):
        self.time = int(time.time())
        self.name = str(name)
        if name is None:
            if debug:
                self.name = 'MacchiatoPetriNet-debug'
            else:
                self.name = 'MacchiatoPetriNet-%d' % self.time
        # elif ' ' in name:
        #     raise ValueError('"%s" is an invalid name, spaces are not permitted' % name)
        # if '_' in self.name:
        #     print('Warning: (%s) Underscores are permitted in names but will interfere with conversion to LaTeX' % name)
        #     time.sleep(1)
        # if '-' in self.name:
        #     print('Warning: (%s) Hyphens are permitted in names but will interfere with rendering Graphviz files!' % name)
        #     time.sleep(1)
        else:
            labelCheck(self.name, ref='Petri Net name')
            self.id, self.gID = genID(self.name)

        self.id, self.gID = genID(self.name)

        self.places = collections.OrderedDict()
        self.trans = collections.OrderedDict()
        self.ready = []
        self.connectivity = [] # not implemented
        self.units = units
        self.transFiredTotal = 0

        self.runMode = runMode
        self.runModes = ['all', 'single', 'stochastic', 'schedule']
        if runMode not in self.runModes:
            raise ValueError('"%s" does not refer to a valid run mode. Valid modes are: %r' % (runMode, self.runModes))
        self.savedot = dot
        self.visualise = visualise
        self.details = details
        self.useGroup = useGroup
        self.orientation = orientation
        self.debug = debug

        self.step = 0
        self.clock = 0.0

        self.schedule = collections.OrderedDict()

        self.arcsVerified = False

        self.placeExit = False
        self.transExit = False

        self.placesToPrint = placesToPrint if placesToPrint is not None else []
        self.transToPrint = transToPrint if transToPrint is not None else []

        self.history = History()
        # Location of Graphviz's dot.exe:
        # Dependant on operating system and personal set up
        # Requried for visualisation only
        self.dotLoc = None
        if visualise is not None:
            # if dotLoc is None:
            #     if os.path.exists(os.path.join('C:/', 'Program Files (x86)', 'Graphviz2.38', 'bin')):
            #         self.dotLoc = os.path.join('C:/', 'Program Files (x86)', 'Graphviz2.38', 'bin')
            #     elif os.path.exists(os.path.join('C:/', 'Program Files (x86)', 'Graphviz', 'bin')):
            #         self.dotLoc = os.path.join('C:/', 'Program Files (x86)', 'Graphviz', 'bin')
            #     elif os.path.exists(os.path.join('C:/', 'Program Files', 'Graphviz2.38', 'bin')):
            #         self.dotLoc = os.path.join('C:/', 'Program Files', 'Graphviz2.38', 'bin')
            #     elif os.path.exists(os.path.join('C:/', 'Program Files', 'Graphviz', 'bin')):
            #         self.dotLoc = os.path.join('C:/', 'Program Files', 'Graphviz', 'bin')
            #     else:
            #         print('Warning: Attempted to autmoatically discover Graphviz installation, but was unsuccessful.\nManual specification of self.dotLoc necessary if visualisation is required.')
            #         time.sleep(5)
            # elif os.path.exists(dotLoc):
            #     self.dotLoc = dotLoc
            # else:
            #     print('Warning: Graphviz installation not found at specifed location.\n"%s"\nCheck simulation parameter file if visualisation is required.' % dotLoc)
            #     time.sleep(5)

            if self.dotLoc is not None:
                if os.path.exists(dotLoc):
                    self.dotLoc = dotLoc
                else:
                    print('Warning: Graphviz installation not found at specifed location.\n"%s"\nCheck simulation parameter file if visualisation is required.' % dotLoc)
                    time.sleep(5)

            if self.dotLoc is not None:
                self.dotLoc = os.path.join(self.dotLoc, 'dot.exe')
        elif dotLoc is not None and self.dotLoc is None:
            if os.path.exists(dotLoc):
                self.dotLoc = os.path.join(dotLoc, 'dot.exe')
            else:
                print('Warning: Graphviz installation not found at specifed location.\n"%s"\nCheck simulation parameter file if visualisation is required.' % dotLoc)
                time.sleep(5)

    def updateTime(self):
        """
        Updates time attribute of PetriNet object
        """
        time.sleep(1)
        self.time = int(time.time())

    def addPlace(self, label, tokens=0, min=0, max=None, limits=None, group=None):
        """
        Creates a new place in the Petri Net

        Parameters
        ----------
        label : string
            Unique identifier of the new place
        tokens : integer
            Number of tokens to create place with (Default = 0)
        min : integer
            Minimum number of tokens that this place can hold (Default = 0)
        max : integer
            Maximum number of tokens that this place can hold (Default =
            inf, parsed as None)
        limits : list of length two
            Simulation is terminated if number of tokens is outside
            limits[0] to limits[1].
            Use 'None' entries for no bounds
        group : integer
            Grouping for visualisation purposes
        """
        if max is None:
            max = float('Inf')

        if not label in self.places:
            self.places[label] = Place(label, tokens=tokens, min=min, max=max, limits=limits, group=group)
        else:
            raise KeyError('Place with label, "%s", already exists' % label)
        # if ' ' in label:
        #     raise ValueError('"%s" is an invalid place label, spaces are not permitted' % label)
        # if '_' in label:
        #     print('Warning: (%s) Underscores are permitted in place lables but will interfere with conversion to LaTeX' % label)
        #     time.sleep(1)
        # if '-' in label:
        #     print('Warning: (%s) Hyphens are permitted in place lables but will interfere with rendering Graphviz files!' % label)
        #     time.sleep(1)
        labelCheck(label, ref='place label')

    def rmvPlace(self, label):
        """
        Removes place of given label from Petri Net and any connected arcs

        Parameters
        ----------
        label : string
            Unique identifier of the place to be removed
        """
        self.places.pop(label)
        for t in self.trans:
            trans = self.trans[t]
            if label in trans.inArcs:
                trans.rmInArc(label)
            if label in trans.outArcs:
                trans.rmOutArc(label)

    def addTrans(self, label, rate=None, uniform=None, delay=None, weibull=None, beta=None, lognorm=None, cyclic=None, maxFire=None, reset=None, vote=None, group=None):
        """
        Creates a new transition in the Petri Net

        Parameters
        ----------
        label : string
            Unique identifier of the new transition
        rate : float
            Mean rate of fire per unit time
        uniform : float
            Maximum wait for wait from 0 to 'uniform' (uniformly distributed)
        delay : float
            Wait time for fixed delay transitions
        weibull : list
            Length two or three list of parameters for a Weibull
            distribution (all floats), eta & beta, such that
            t = eta[-ln(X)]^-beta, and 0 < X < 1. Give a value for sigma to
            optionally include uncertainty in the data.
        beta : list
            Length two list of parameters for a Beta distribution (both
            floats), alpha & beta, with optional scale parameter
        lognorm : list
            Length two list of parameters for a Lognormal distribution (both
            floats), mu & sigma
        cyclic : list
            Length two list of parameters for a cyclic distribution (both
            floats), frequency and offset
        maxFire : integer
            Maximum number of times the transition is permitted to fire
        reset : list
            A list of places to reset on firing (*/? glob selection supported)
        group : integer
            Label used to group transitions for visualisation
        """
        if not label in self.trans:
            if reset is not None:
                if type(reset) is not list:
                    if ':' in reset:
                        reset = reset.split(':')
                    else:
                        reset = [reset]
                reset = expandReset(self, reset)
            self.trans[label] = Trans(label, rate=rate, uniform=uniform, delay=delay, weibull=weibull, beta=beta, lognorm=lognorm, cyclic=cyclic, maxFire=maxFire, reset=reset, vote=vote, group=group)
        else:
            raise KeyError('Transition with label, "%s", already exists' % label)
        # if ' ' in label:
        #     raise ValueError('"%s" is an invalid transition label, spaces are not permitted' % label)
        # if '_' in label:
        #     print('Warning: (%s) Underscores are permitted in transition lables but will interfere with conversion to LaTeX' % label)
        #     time.sleep(1)
        # if '-' in label:
        #     print('Warning: (%s) Hyphens are permitted in transition lables but will interfere with rendering Graphviz files!' % label)
        #     time.sleep(1)

        labelCheck(label, ref='transition label')
        if rate is not None and delay is not None:
            raise ValueError('Transition "%s" has both "rate" and "delay" specified -- Choose one or the other.' % label)

    def rmvTrans(self, label):
        """
        Removes transition of given label from Petri Net

        Parameters
        ----------
        label : string
            Unique identifier of the transition to be removed
        """
        self.trans.pop(label)

    def transSummary(self):
        """
        Print a summary of transition firing in the Petri Net
        """
        for t in self.trans:
            trans = self.trans[t]
            print('Transition "%s" fired %d times' % (t, trans.firedCount))
        print('Total transition firings: %d\n' % self.transFiredTotal)

    def placesSummary(self, mode, tOut=True, pfile=None):
        """
        Writes the Petri Net's places' state to file

        Parameters
        ----------
        pfile : filepointer
            Object indicating location to which place data is writen
        mode : string
        tOut : boolean
            Toggles terminal print out
        *  all : All non-conflicting transitions are fired simultaneously
        *  single : One transition is randomly selected and fired
        *  stochastic : One transition is selected for firing in proportion
           to its rates (plus instant and fixed delay transitions)
        *  schedule : Transitions whose requisites are met are assigned a
           firing time based on their timing distribution, and are fired in
           chronological order (timings are assinged when requisites are
           met, and persist until either it is fire, or requisites are
           withdrawn).
        """
        if tOut:
            for p in self.places:
                place = self.places[p]
                print('Place "%s": %d tokens in, %d tokens out. Net = %d. %d resets.' % (p, place.ins, place.outs, place.ins - place.outs, place.resetCount))
            print('')

        if pfile is not None:
            pfile.write('\n')
            line = ('In,')
            if mode in ['stochastic', 'schedule']:
                line += (',')
            for p in self.places:
                if self.placesToPrint and p not in self.placesToPrint:
                    continue
                line += ('%d,' % self.places[p].ins)
            pfile.write('%s\n' % line)
            line = ('Out,')
            if mode in ['stochastic', 'schedule']:
                line += (',')
            for p in self.places:
                if self.placesToPrint and p not in self.placesToPrint:
                    continue
                line += ('%d,' % self.places[p].outs)
            pfile.write('%s\n' % line)
            line = ('Net,')
            if mode in ['stochastic', 'schedule']:
                line += (',')
            for p in self.places:
                if self.placesToPrint and p not in self.placesToPrint:
                    continue
                line += ('%d,' % (self.places[p].ins - self.places[p].outs))
            pfile.write('%s\n' % line)
            line = ('Reset,')
            if mode in ['stochastic', 'schedule']:
                line += (',')
            for p in self.places:
                if self.placesToPrint and p not in self.placesToPrint:
                    continue
                line += ('%d,' % self.places[p].resetCount)
            pfile.write('%s\n' % line)

    def readyTrans(self, mode=None):
        """
        Lists transition that are ready to fire. Updates PetriNet.ready and Trans.waiting attributes.

        Parameters
        ----------
        mode : string
        *  all : All non-conflicting transitions are fired simultaneously
        *  single : One transition is randomly selected and fired
        *  stochastic : One transition is selected for firing in proportion
        to its rates (plus instant and fixed delay transitions)
        *  schedule : Transitions whose requisites are met are assigned a
        firing time based on their timing distribution, and are fired in
        chronological order (timings are assinged when requisites are met,
        and persist until either it is fire, or requisites are withdrawn).
        """
        if mode is None:
            mode = self.runMode

        # Loop over all transitions
        for t in self.trans:
            v = 0 # counter for voting transitions
            ready = True
            tt = self.trans[t]
            # Skip transitions without connections
            if not (len(tt.inArcs) + len(tt.outArcs)):
                continue
            # Loop over the transition's incoming arcs
            for i in tt.inArcs:
                ii = tt.inArcs[i]
                place = self.places[ii.start]
                # Standard arc
                if ii.type == 'std':
                    # Check if there are enough tokens to meet the arc weight
                    if place.tokens >= ii.weight:
                        # Chech that firing will not put place below minimum
                        if (place.tokens - ii.weight) < place.min:
                            ready = False
                            break
                        # Tally votes for voting transition
                        elif tt.vote is not None:
                            v += 1
                    else:
                        # All arcs must be considered for voting transition
                        if tt.vote is not None:
                            pass
                        # Only one unready arc need be found to establish that normal transition cannot fire
                        else:
                            ready = False
                            break
                # Inhibit arc
                elif ii.type == 'inh':
                    # If arc weight is met, transition cannot fire
                    if place.tokens >= ii.weight:
                        ready = False
                        # Enforcement of inhibition arcs for voting transitions
                        if tt.vote is not None:
                            v = 0
                        break

            # Check tally for voting transitions
            if tt.vote is not None:
                if v >= tt.vote:
                    ready = True
                else:
                    ready = False

            # Go to next transition if it cannot fire
            if ready == False:
                continue
            # Loop over the transition's outgoing arcs
            for o in tt.outArcs:
                oo = tt.outArcs[o]
                place = self.places[oo.end]
                # Check that firing will not result in a place exceeding its token limit
                if (place.tokens + oo.weight) > place.max:
                    ready = False
                    break
            # If all requirements for transition to fire are met, mark, and add to list
            if ready == True:
                tt.ready = True
                if tt.delay is not None and mode == 'stochastic':
                    if tt.waiting is None:
                        tt.waiting = [self.step, self.clock]
                    elif tt.waiting[0] == self.step + 1:
                        tt.waiting[0] += 1
                    elif tt.waiting[0] > self.step + 1:
                        tt.waiting = [self.step, self.clock]
                elif mode == 'schedule':
                    if tt.waiting is None:
                        tt.waiting = [self.step, self.clock]
                self.ready.append(tt)
            else:
                tt.waiting = None


    def resolveConflicts(self):
        """
        Removes ready to fire status from one of two conflicting transitions
        (chosen at random). Only used when runMode = 'all'.
        """
        # Incoming arcs
        # newList = []
        # Loop over transitions
        for a in range(len(self.ready)):
            tA = self.ready[a]
            # Skip transitions already discounted
            if not tA.ready:
                continue
            # Loop over transitions not yet compared with 'a'
            for b in range(a+1,len(self.ready)):
                tB = self.ready[b]
                # Skip transitions already discounted
                if not tB.ready:
                    continue
                aIn = []
                bIn = []
                # Create list of places on incoming arcs
                for ai in tA.inArcs:
                    aIn.append(tA.inArcs[ai].start)
                for bi in tB.inArcs:
                    bIn.append(tB.inArcs[bi].start)
                # Check for common members
                common = list(set(aIn) & set(bIn))
                if not len(common):
                    continue

                conflict = False
                # Get weights of arcs
                for p in range(len(common)):
                    place = self.places[common[p]]
                    arcAW = None
                    arcBW = None
                    for aa in tA.inArcs:
                        if tA.inArcs[aa].start == place.label and tA.inArcs[aa].type != 'inh':
                            arcAW = tA.inArcs[aa].weight
                            break
                    for bb in tB.inArcs:
                        if tB.inArcs[bb].start == place.label and tB.inArcs[bb].type != 'inh':
                            arcBW = tA.inArcs[bb].weight
                            break
                    # If firing both transitions would deplete the place, a conflict exists
                    if place.min > (place.tokens - arcAW - arcBW):
                        conflict = True
                        break

                # Select a transitions to deactivate, and add the other to the new ready list
                if conflict:
                    if random.randint(0,1): # Keep transition'a'
                        # newList.append(tA)
                        tB.ready = False
                    else:
                        # newList.append(tB) # Keep transition 'b'
                        tA.ready = False
                        # If 'a' is not selected, there is no need to continue looking for conflicts with it
                        break
                # # No conflict - keep both
                # else:
                #     newList.append(tA)
                #     newList.append(tB)

        # Update list of ready to fire transitions
        # self.ready = newList
        self.ready = []
        for t in self.trans:
            if self.trans[t].ready:
                self.ready.append(self.trans[t])

        # Outgoing arcs
        # newList = []
        for a in range(len(self.ready)):
            tA = self.ready[a]
            # Skip transitions already discounted
            if not tA.ready:
                continue
            # Loop over transitions not yet compared with 'a'
            for b in range(a+1,len(self.ready)):
                tB = self.ready[b]
                # Skip transitions already discounted
                if not tB.ready:
                    continue
                aOut = []
                bOut = []
                # Create list of places on outgoing arcs
                for ao in tA.outArcs:
                    aOut.append(tA.outArcs[ao].end)
                for bo in tB.outArcs:
                    bOut.append(tB.outArcs[bo].start)
                # Check for common members
                common = list(set(aOut) & set(bOut))
                if not len(common):
                    continue

                conflict = False
                # Get weights of arcs
                for p in range(len(common)):
                    place = self.places[common[p]]
                    arcAW = None
                    arcBW = None
                    for aa in range(len(tA.outArcs)):
                        if tA.outArcs[aa].start == place.label and tA.outArcs[aa].type != 'inh':
                            arcAW = tA.outArcs[aa].weight
                            break
                    for bb in range(len(tB.outArcs)):
                        if tB.outArcs[bb].end == place.label and tB.outArcs[bb].type != 'inh':
                            arcBW = tA.outArcs[bb].weight
                            break
                    # If firing both transitions would overpopulate the place, a conflict exists
                    if place.min > (place.tokens + arcAW + arcBW):
                        conflict = True
                        break

                # Select a transitions to deactivate, and add the other to the new ready list
                if conflict:
                    if random.randint(0,1): # Keep transition 'a'
                        # newList.append(tA)
                        tB.ready = False
                    else: # Keep transition 'b'
                        newList.append(tB)
                        # tA.ready = False
                        # If 'a' is not selected, there is no need to continue looking for conflicts with it
                        break

        # Update list of ready to fire transitions
        # self.ready = newList
        self.ready = []
        for t in self.trans:
            if self.trans[t].ready:
                self.ready.append(self.trans[t])

    def calcTokens(self, label):
        """
        Calculates the change in tokens from firing a given transition

        Parameters
        ----------
        label : string
            Unique identifier of the transition
        """
        trans = self.trans[label]
        assert trans.ready, ('Cannot fire! -- transition, "%s" is not ready' % label)
        print('Firing transition, "%s":' % label)
        # Update firedCount
        trans.firedCount += 1
        self.transFiredTotal += 1
        trans.waiting = None
        # Incoming arcs
        for i in trans.inArcs:
            ii = trans.inArcs[i]
            if ii.type != 'std':
                continue
            place = self.places[ii.start]
            if trans.vote is not None:
                if ii.weight > place.tokens:
                    continue
            print('Place, "%s", loses %d tokens' % (ii.start, ii.weight))
            place.tokenChange -= ii.weight
            place.outs += ii.weight
        # Outgoing arcs
        for o in trans.outArcs:
            oo = trans.outArcs[o]
            place = self.places[oo.end]
            test = False
            if trans.vote is not None:
                if oo.weight > place.tokens:
                    test = False
                    for i in trans.inArcs:
                        ii = trans.inArcs[i]
                        if ii.type == 'std' and ii.start == oo.end:
                            print('%s : %s' % (label,ii.start))
                            test = True
                            break
                    if test:
                        continue
            print('Place, "%s", receives %d tokens' % (oo.end, oo.weight))
            if test:
                sys.exit()
            place.tokenChange += oo.weight
            place.ins += oo.weight

    def updateTokens(self):
        """
        Updates places by tokenChange
        """
        for p in self.places:
            pp = self.places[p]
            pp.tokens += pp.tokenChange
            assert (pp.tokens >= pp.min and pp.tokens <= pp.max), 'Invalid token count, %d, on place, "%s". Change = %d. Min = %d. Max = %r.' % (pp.tokens, pp.label, pp.tokenChange, pp.min, pp.max)
            pp.tokenChange = 0

    def clearReady(self):
        """
        Removes ready to fire status after use
        """
        for t in self.ready:
            t.ready = False
        self.ready = []

    def buildConnectivity(self):
        """
        Constructs a matrix representing the connections between places and
        transitions
        """
        raise NotImplementedError('Method, "buildConnectivity" has not yet been constructed')

    def selection(self, mode):
        """
        Constructs a Monte Carlo event table for ready to fire transitions,
        according to run mode, and returns a transition.

        Parameters
        ----------
        mode : string
        *  single : Equal weighting to transitions
        *  stochastic : Weighting derivied from rates
        *  schedule : Next scheudled transition fires

        Returns
        ----------
        transition : Trans object
            The transition selected to fire
        time : float
            The clock advancement generated (only apllies to 'stochastic'
            mode)
        """
        table = []
        time = None
        total = 0.0
        transition = None

        # 'single' mode -  all transitions given equal weight
        if mode == 'single':
            total = float(len(self.ready))
            transition = self.ready[random.randint(0, len(self.ready)-1)]
        # 'stochastic' mode - transitions selected according to rate
        elif mode == 'stochastic':
            # Fire instant transitions fisrt
            delayOnly = []
            for t in self.ready:
                if t.rate is None and t.delay is None:
                    table.append(t)
                if t.rate is None and t.delay is not None:
                    delayOnly.append(t)
            if len(table):
                time = 0.0
                transition = table[random.randint(0, len(table)-1)]
                return transition, time
            else:
                # Create event table and sum rate total
                for t in self.ready:
                    if t.rate is None:
                        continue
                    elif t.rate <= 0:
                        raise ValueError('Transition "%s" has invalid rate (%r)' % (t.label, t.rate))
                    table.append([total, t])
                    total += t.rate
                if len(table):
                    table.append([total, None])
                    # Randomly select point on the table
                    event = random.uniform(0, total)
                    # Find corresponding transition
                    for i in range(len(table)):
                        if event >= table[i][0] and event < table[i+1][0]:
                            transition = table[i][1]
                            break
                    # Calculate clock advancement
                    mu = random.random()
                    time = -math.log(mu)/total

            # Compile list of fixed delay transitions that have been waiting to fire and select one
            # This might not work properly yet
            table = []
            try:
                minTime = delayOnly[0].waiting[1] + delayOnly[0].delay
            except IndexError:
                pass
            for t in delayOnly:
                minTime = min(t.waiting[1] + t.delay, minTime)
            for t in self.ready:
                if t.waiting is not None and time is not None:
                    if t.waiting[1] + t.delay < self.clock + time:
                        if t.waiting[1] + t.delay > minTime:
                            pass
                        else:
                            table.append(t)
                if t in delayOnly and t not in table:
                    if t.waiting[1] + t.delay > minTime:
                        pass
                    else:
                        table.append(t)
            if len(table):
                transition = table[random.randint(0, len(table)-1)]
                # Compute remaning time for fixed delay duration
                time = transition.delay - (self.clock - transition.waiting[1])
                assert time > 0.0, (time, transition.waiting, transition.delay)

        # 'schedule' mode - transition timings are calculated invidually to compose a Monte Carlo table
        elif mode == 'schedule':
            time = 0.0
            instants = []
            pcInst = []

            # Remove transitions from the schedule whose requisites are no longer met
            for s in list(self.schedule):
                if not self.trans[s].ready:
                    self.trans[s].pcnStatus = 1.0
                    self.schedule.pop(s)

            # Assign firing time for 'ready' transitions not yet in the schedule
            for trans in self.ready:
                if trans.rate is not None or trans.uniform is not None or trans.delay is not None or trans.weibull is not None or trans.beta is not None or trans.lognorm is not None or trans.cyclic is not None:
                    # Finite, non-zero delay transitions
                    if not trans.label in self.schedule:
                        self.schedule[trans.label] = self.clock + self.getWait(trans)
                    elif trans.pcn:
                        con = 1.0
                        for ia in trans.inArcs:
                            if trans.inArcs[ia].type == 'pcn':
                                con += trans.inArcs[ia].weight * self.places[ia].tokens
                        if con != trans.pcnStatus and trans.waiting is not None:
                            oldScdl = self.schedule[trans.label]
                            #print('>> con %f, status %f, waiting %r' % (con, trans.pcnStatus, trans.waiting))
                            self.schedule[trans.label] = max(self.clock, trans.waiting[1] + self.getWait(trans))
                            print('>> Rescheduling %s from %f %s to %f %s' % (trans.label, oldScdl, self.units, self.schedule[trans.label], self.units))
                else:
                    # Create list of instant transitions
                    instants.append(trans)
                if trans.pcn:
                    # zero weight place coniditional arcs fire timed transitions instantly
                    for i in trans.inArcs:
                        ii = trans.inArcs[i]
                        if ii.type == 'pcn' and not ii.weight and self.places[ii.start].tokens:
                            pcInst.append(trans)

            # Update schedule object to account for instance place coniditional effect
            for pci in range(len(pcInst)):
                for t in range(len(self.ready)):
                    if self.ready[t] == pcInst[pci]:
                        self.ready.pop(t)
                        self.schedule.pop(pcInst[pci].label)
                        break
            # Add place conditional instant firing transitions to instants list
            instants += pcInst

            # Instant transitions always fire first
            if len(instants):
                print('%d instant transitions ready to fire:' % len(instants))
                for t in instants:
                    print('\t%s' % t.label)
                return instants[random.randint(0,len(instants)-1)], 0.0

            # Create list of transitions that are next availible to fire
            nexts = []
            if len(self.schedule):
                next = float('Inf')
                print('Current transition firing schedule:')
                for s in self.schedule:
                    print('\t%s   %.3g %s' % (s, self.schedule[s], self.units))
                    next = min(self.schedule[s], next)
                for s in self.schedule:
                    if self.schedule[s] == next:
                        nexts.append(s)

                # If more than one transition is scheduled to fire next (i.e. at the same time), select one at random
                if len(nexts):
                    transition = self.trans[nexts[random.randint(0,len(nexts)-1)]]
                    time = self.schedule[transition.label] - self.clock
                    # Remove selected transition from the scheudle
                    self.schedule.pop(transition.label)

        # Return results
        return transition, time

    def getWait(self, trans):
        """
        Calculates the duration between the requisites of a transition being
        met and it firing, based on the specified probability distribution.

        Parameters
        ----------
        trans : Trans object
            The transition in question

        Returns
        ----------
        wait : float
            The duration until the transition fires
        """

        wait = 0.0
        con = 1.0 # Modifier for place conditionals
        if trans.pcn:
            for ia in trans.inArcs:
                if trans.inArcs[ia].type == 'pcn':
                    con += trans.inArcs[ia].weight * self.places[ia].tokens
            # if con == 0:
            #     con = 1
        if trans.rate is not None:
            # KMC-esque Stochastic firing
            wait += (-math.log(random.uniform(0,1)))/(trans.rate*con)
        if trans.uniform is not None:
            # Random uniform distribution
            wait += -random.uniform(-trans.uniform/con, 0.0) # gives wait in range of (0.0, uniform/con]
        if trans.delay is not None:
            # Fixed wait firing
            wait += trans.delay/con
        if trans.weibull is not None:
            #  Weibull distribution
            genMean = trans.weibull[0]
            if trans.weibull[2] > 0.0:
                genMean = max(random.normalvariate(genMean, trans.weibull[2]), 0.0)
            wait += (genMean/con)*((-math.log(1-random.uniform(0,1)))**(1.0/trans.weibull[1]))
        if trans.beta is not None:
            # Beta distribution
            wait += random.betavariate(trans.beta[0], trans.beta[1])*(trans.beta[2]/con)
            print(trans.beta, con, wait)
        if trans.lognorm is not None:
            # Lognormal
            wait += random.lognormvariate(trans.lognorm[0]/con, trans.lognorm[1])
        if trans.cyclic is not None:
            # Cyclic
            if con > 0.0:
                w = (trans.cyclic[0]/con) - ((self.clock-trans.cyclic[1]) % (trans.cyclic[0]/con))
                if w == trans.cyclic[0]/con:
                    w = 0.0
                if w < 0.0:
                    w += trans.cyclic[0]/con
                assert w >= 0.0
                assert w < trans.cyclic[0]/con
                if trans.lastFired == self.clock:
                    w += trans.cyclic[0]/con
                wait += w
            else:
                # Allows instant firing place conditional
                raise NotImplementedError('Conversion of PCN to instant not yet writen')
                pass
        if trans.pcn:
            trans.pcnStatus = con
        return wait

    def writeNetStart(self, mode):
        """
        Creates output file with header and writes initial state

        Parameters
        ----------
        mode : string
        *  all : All non-conflicting transitions are fired simultaneously
        *  single : One transition is randomly selected and fired
        *  stochastic : One transition is selected for firing in proportion
           to its rates (plus instant and fixed delay transitions)
        *  schedule : Transitions whose requisites are met are assigned a
           firing time based on their timing distribution, and are fired in
           chronological order (timings are assinged when requisites are
           met, and persist until either it is fire, or requisites are
           withdrawn).

        Returns
        ----------
        pfile : filepointer
            Object indicating location to which place data is writen
        tfile : filepointer
            Object indicating location to which transition data is writen
        tlist : filepointer
            Object indicating location to which list of transitions fired is
            writen
        """
        path = os.path.join(os.getcwd(), self.name)
        if not os.path.exists(path):
            os.mkdir(path)
        # Make places file
        name = 'Macchiato_PetriNet_Places_%d.csv' % self.time
        if self.debug:
            name = 'debug_Places.csv'
        pfile = open(os.path.join(os.getcwd(), path, name), 'w')
        header = '%s,Places,(Token Count),\nStep,'% self.name
        if mode in ['stochastic', 'schedule']:
            header += 'Time/%s,' % self.units
        for p in self.places:
            if self.placesToPrint and p not in self.placesToPrint:
                continue
            header += ('%s,' % self.places[p].label)
        pfile.write('%s\n' % header)
        # Make transitions file
        name = 'Macchiato_PetriNet_Trans_%d.csv' % self.time
        if self.debug:
            name = 'debug_Trans.csv'
        tfile = open(os.path.join(os.getcwd(), path, name), 'w')
        header = '%s,Transitions,(Fired Count),\nStep,'% self.name
        if mode in ['stochastic', 'schedule']:
            header += 'Time/%s,' % self.units
        for t in self.trans:
            if self.transToPrint and t not in self.transToPrint:
                continue
            header += ('%s,' % self.trans[t].label)
        tfile.write('%s\n' % header)
        # Transitions fired at each step
        name = 'Macchiato_PetriNet_FireList_%d.csv' % self.time
        if self.debug:
            name = 'debug_TransList.csv'
        tlist = open(os.path.join(os.getcwd(), path, name), 'w')
        header = '%s\nStep,' % self.name
        if mode in ['stochastic', 'schedule']:
            header += 'Time/%s,' % self.units
        header += 'Transition,'
        tlist.write('%s\n' % header)
        # Write 0th entry
        self.writeNet(pfile, tfile, tlist, mode)
        # Return file pointers
        return pfile, tfile, tlist

    def writeNet(self, pfile, tfile, tlist, mode, fireList=[]):
        """
        Writes Petri Net status at the end of a step

        Parameters
        ----------
        pfile : filepointer
            Object indicating location to which place data is writen
        tfile : filepointer
            Object indicating location to which transition data is writen
        tlist : filepointer
            Object indicating location to which list of transitions fired is
            writen
        mode : string
        *  all : All non-conflicting transitions are fired simultaneously
        *  single : One transition is randomly selected and fired
        *  stochastic : One transition is selected for firing in proportion
           to its rates (plus instant and fixed delay transitions)
        fireList : list
            Transitions firing on this step.
        """
        # Places
        line = ('%d,' % self.step)
        if mode in ['stochastic', 'schedule']:
            line += ('%f,' % self.clock)
        for p in self.places:
            if self.placesToPrint and p not in self.placesToPrint:
                continue
            line += ('%d,' % self.places[p].tokens)
        pfile.write('%s\n' % line)
        # Transitions
        line = ('%d,' % self.step)
        if mode in ['stochastic', 'schedule']:
            line += ('%f,' % self.clock)
        for t in self.trans:
            if self.transToPrint and t not in self.transToPrint:
                continue
            line += ('%d,' % self.trans[t].firedCount)
        tfile.write('%s\n' % line)
        # Transition List
        line = ('%d,' % self.step)
        if mode in ['stochastic', 'schedule']:
            line += ('%f,' % self.clock)
        for t in fireList:
            line += ('%s,' % t.label)
        tlist.write('%s\n' % line)
        # Visualisation
        if self.savedot:
            self.dot(mode=mode)

    def dot(self, mode='schedule', visualise=None):
        """
        Write net net Graphviz '*.dot' format and generates image file

        Parameters
        ----------
        mode : string
        *  all : All non-conflicting transitions are fired simultaneously
        *  single : One transition is randomly selected and fired (Default)
        *  stochastic : One transition is selected for firing in proportion
           to its rates (plus instant and fixed delay transitions)
        *  schedule : Transitions whose requisites are met are assigned a
           firing time based on their timing distribution, and are fired in
           chronological order (timings are assinged when requisites are
           met, and persist until either it is fire, or requisites are
           withdrawn).
        visualise : string
            Toggle image output file type eg: png, svg... (Default = None
            for no file output). Only use to override self.visualise format,
            but will not suppress file output.

        Returns
        ----------
        path : string
            Path to *.dot file

        # TODO: Rewrite with Graphviz Python interface.
        """
        # File and directory operations
        if not os.path.exists(os.path.join(os.getcwd(), self.name)):
            os.mkdir(os.path.join(os.getcwd(), self.name))
        if self.debug or self.time is None:
            rPath = os.path.join(os.getcwd(), self.name, 'Visualisation')
        else:
            rPath = os.path.join(os.getcwd(), self.name, 'Visualisation_%d' % self.time)
        if not os.path.exists(rPath):
            os.mkdir(rPath)
        path = os.path.join(rPath, '%d.dot' % self.step)
        out = open(path, 'w')
        # Output preamble
        out.write('digraph {\n\tnode [label="%s", fillcolor="#FFFFFF", fontcolor="#000000", style=filled];' % self.id)
        out.write('\n\t  edge [style="solid"];')
        if self.orientation is not None:
            out.write('\n\t  rankdir="%s";' % self.orientation)
        out.write('\n\t  graph [splines="true", overlap="false"];')
        # Step & time info
        if self.details:
            info = '%s\\nStep: %d' % (self.gID, self.step)
            if mode in ['stochastic', 'schedule']:
                info += '\\nClock: %.3g %s' % (self.clock, self.units)
            out.write('\n\tInfo')
            out.write('\n\t\t[')
            out.write('\n\t\t\tshape="rectangle"')
            out.write('\n\t\t\tid="%s"' % self.id)
            out.write('\n\t\t\ttooltip="%s status"' % self.id)
            out.write('\n\t\t\tlabel="%s"' % info)
            out.write('\n\t\t];')
        if self.useGroup:
            # Create places
            maxGroup = 0
            for p in self.places:
                try:
                    maxGroup = max(maxGroup, self.places[p].group)
                except TypeError:
                    pass
            for g in range(maxGroup+1):
                out.write('\n\tsubgraph cluster_P%d {' % g)
                out.write('\n\tstyle=filled;\n\tcolor=white;')
                for p in self.places:
                    if self.places[p].group == g:
                        self.dotPlaces(p, out)
                out.write('\n\t}')
            for p in self.places:
                if self.places[p].group is None:
                    self.dotPlaces(p, out)
            # Create transitions
            maxGroup = 0
            for t in self.trans:
                try:
                    maxGroup = max(maxGroup, self.trans[t].group)
                except TypeError:
                    pass
            for g in range(maxGroup+1):
                out.write('\n\tsubgraph cluster_T%d {' % g)
                out.write('\n\tstyle=filled;\n\tcolor=white;')
                for t in self.trans:
                    if self.trans[t].group == g:
                        self.dotTrans(t, out, mode)
                out.write('\n\t}')
            for t in self.trans:
                if self.trans[t].group is None:
                    self.dotTrans(t, out, mode)
        else:
            # Create places
            for p in self.places:
                self.dotPlaces(p, out)
            # Create transitions
            for t in self.trans:
                self.dotTrans(t, out, mode)
        for t in self.trans:
            # Create incoming arcs
            for i in self.trans[t].inArcs:
                ii = self.trans[t].inArcs[i]
                start = self.places[ii.start].id
                out.write('\n\t%s -> %s' % (start, self.trans[t].id))
                # out.write('\n\t%s -> %s' % (ii.start, t))
                out.write('\n\t\t[')
                if ii.type == 'pcn':
                    out.write('\n\t\t\tarrowhead="odot", style="dashed", color=Blue')
                    out.write('\n\t\t\tlabel="PC\\n[%d]"' % ii.weight)
                elif ii.type == 'inh':
                    out.write('\n\t\t\tarrowhead="dot", style="dashed", color=Red')
                    out.write('\n\t\t\tlabel="Inhibit\\n[%d]"' % ii.weight)
                else:
                    out.write('\n\t\t\tarrowhead="normal"')
                    out.write('\n\t\t\tlabel="[%d]"' % ii.weight)
                out.write('\n\t\t];')
            # Create outgoing arcs
            for o in self.trans[t].outArcs:
                oo = self.trans[t].outArcs[o]
                end = self.places[oo.end].id
                out.write('\n\t%s -> %s' % (self.trans[t].id, end))
                # out.write('\n\t%s -> %s' % (t, oo.end))
                out.write('\n\t\t[')
                out.write('\n\t\t\tarrowhead="normal"')
                out.write('\n\t\t\tlabel="[%d]"' % oo.weight)
                out.write('\n\t\t];')
        # End file
        out.write('\n}')
        out.close()
        # Visualisation
        if self.visualise is not None or visualise is not None:
            format = None
            if visualise is not None:
                format = visualise
            else:
                format = self.visualise
            oPath = os.path.join(rPath, '%d.%s' % (self.step, format))
            # Render dot file as image
            if self.dotLoc is not None:
                subprocess.call('"%s" %s -T %s -o "%s"'  % (self.dotLoc, path, format, oPath), shell=True)
            else:
                di.render(path, [format])

        return path

    def dotPlaces(self, p, out):
        """
        Write place to dot file

        Parameters
        ----------
        p : string
            Place label
        out : file pointer
            Dot file to which to write
        """
        out.write('\n\t%s' % self.places[p].id)
        # out.write('\n\t%s' % p)
        out.write('\n\t\t[')
        out.write('\n\t\t\tshape="ellipse"')
        out.write('\n\t\t\tid="%s"' % self.places[p].id)
        out.write('\n\t\t\ttooltip="%s"' % self.places[p].id)
        # out.write('\n\t\t\tid="%s"' % p)
        # out.write('\n\t\t\ttooltip="%s"' % p)
        string = ''
        if self.places[p].max < float('Inf'):
            string += '\\n[Max %d]' % self.places[p].max
        if self.places[p].min > 0:
            string += '\\n[Min %d]' % self.places[p].min
        out.write('\n\t\t\tlabel="%s\\n[%d]%s"' % (self.places[p].gID, self.places[p].tokens, string))
        # out.write('\n\t\t\tlabel="%s\\n[%d]%s"' % (p, self.places[p].tokens, string))
        out.write('\n\t\t];')

    def dotTrans(self, t, out, mode):
        """
        Write transition to dot file

        Parameters
        ----------
        t : string
            Transition label
        out : file pointer
            Dot file to which to write
        """
        out.write('\n\t%s' % self.trans[t].id)
        # out.write('\n\t%s' % t)
        out.write('\n\t\t[')
        if self.trans[t].vote is not None:
            out.write('\n\t\t\tshape="box3d"')
        else:
            out.write('\n\t\t\tshape="rectangle"')
        out.write('\n\t\t\tid="%s"' % self.trans[t].id)
        out.write('\n\t\t\ttooltip="%s"' % self.trans[t].id)
        # out.write('\n\t\t\tid="%s"' % t)
        # out.write('\n\t\t\ttooltip="%s"' % t)
        if mode in ['stochastic', 'schedule']:
            # out.write('\n\t\t\tlabel="%s\\nRate: %s/%s"' % (t, self.trans[t].rate, self.units))
            gID = self.trans[t].gID
            # if self.trans[t].vote is not None:
            #     gID += '\\nVOTE'
            if len(self.trans[t].reset):
                gID += '\\nRESET'
            if self.trans[t].rate is not None:
                if len('%s' % self.trans[t].rate) > 3:
                    out.write('\n\t\t\tlabel="%s\\n[Rate %.2e/%s]"' % (gID, self.trans[t].rate, self.units))
                    # out.write('\n\t\t\tlabel="%s\\n[Rate %.2e/%s]"' % (t, self.trans[t].rate, self.units))
                else:
                    out.write('\n\t\t\tlabel="%s\\n[Rate %s/%s]"' % (gID, self.trans[t].rate, self.units))
                    # out.write('\n\t\t\tlabel="%s\\n[Rate %s/%s]"' % (t, self.trans[t].rate, self.units))
            elif self.trans[t].uniform is not None:
                if len('%s' % self.trans[t].uniform) > 3:
                    out.write('\n\t\t\tlabel="%s\\n[Delay 0 to %.2e %s]"' % (gID, self.trans[t].uniform, self.units))
                    # out.write('\n\t\t\tlabel="%s\\n[Delay 0 to %.2e %s]"' % (t, self.trans[t].uniform, self.units))
                else:
                    out.write('\n\t\t\tlabel="%s\\n[Delay 0 to %s %s]"' % (gID, self.trans[t].uniform, self.units))
                    # out.write('\n\t\t\tlabel="%s\\n[Delay 0 to %s %s]"' % (t, self.trans[t].uniform, self.units))
            elif self.trans[t].delay is not None:
                if len('%s' % self.trans[t].delay) > 3:
                    out.write('\n\t\t\tlabel="%s\\n[Delay %.2e %s]"' % (gID, self.trans[t].delay, self.units))
                    # out.write('\n\t\t\tlabel="%s\\n[Delay %.2e %s]"' % (t, self.trans[t].delay, self.units))
                else:
                    out.write('\n\t\t\tlabel="%s\\n[Delay %s %s]"' % (gID, self.trans[t].delay, self.units))
                    # out.write('\n\t\t\tlabel="%s\\n[Delay %s %s]"' % (t, self.trans[t].delay, self.units))
            elif self.trans[t].weibull is not None:
                mt = '%s' % self.trans[t].weibull[0]
                beta = '%s' % self.trans[t].weibull[1]
                sigma = ''
                if len('%s' % self.trans[t].weibull[0]) > 3:
                    mt = '%.2e' % self.trans[t].weibull[0]
                if len('%s' % self.trans[t].weibull[1]) > 3:
                    beta = '%.2e' % self.trans[t].weibull[1]
                if self.trans[t].weibull[2] > 0.0:
                    if len('%s' % self.trans[2].weibull[1]) > 3:
                        sigma = ', %.2e' % self.trans[t].weibull[1]
                out.write('\n\t\t\tlabel="%s\\n[Weibull %s %s, %s%s]"' % (gID, mt, self.units, beta, sigma))
                # out.write('\n\t\t\tlabel="%s\\n[Weibull %s %s, %s]"' % (t, eta, self.units, beta))
            elif self.trans[t].beta is not None:
                alpha = '%s' % self.trans[t].beta[0]
                beta = '%s' % self.trans[t].beta[1]
                scale = '%s' % self.trans[t].beta[2]
                if len('%s' % self.trans[t].beta[0]) > 3:
                    eta = '%.2e' % self.trans[t].beta[0]
                if len('%s' % self.trans[t].beta[1]) > 3:
                    beta = '%.2e' % self.trans[t].beta[1]
                if len('%s' % self.trans[t].beta[2]) > 3:
                    beta = '%.2e' % self.trans[t].beta[2]
                out.write(u'\n\t\t\tlabel="%s\\n[Beta %s, %s, *%s]"' % (gID, alpha, beta, scale))
            elif self.trans[t].lognorm is not None:
                mu = '%s' % self.trans[t].lognorm[0]
                sigma = '%s' % self.trans[t].lognorm[1]
                if len('%s' % self.trans[t].lognorm[0]) > 3:
                    mu = '%.2e' % self.trans[t].lognorm[0]
                if len('%s' % self.trans[t].lognorm[1]) > 3:
                    sigma = '%.2e' % self.trans[t].lognorm[1]
                out.write('\n\t\t\tlabel="%s\\n[Lognorm %s %s, %s]"' % (gID, mu, self.units, sigma))
                # out.write('\n\t\t\tlabel="%s\\n[Lognorm %s %s, %s]"' % (t, mu, self.units, sigma))
            elif self.trans[t].cyclic is not None:
                frq = '%s' % self.trans[t].cyclic[0] # frequency
                off = '%s' % self.trans[t].cyclic[1] # offset
                if len('%s' % self.trans[t].cyclic[0]) > 3:
                    frq = '%.2e' % self.trans[t].cyclic[0]
                if len('%s' % self.trans[t].cyclic[1]) > 3:
                    off = '%.2e' % self.trans[t].cyclic[1]
                else:
                    out.write('\n\t\t\tlabel="%s\\n[Cyclic %s, %s %s]"' % (gID, frq, off, self.units))
                    # out.write('\n\t\t\tlabel="%s\\n[Cyclic %s, %s %s]"' % (t, frq, off, self.units))
            else:
                out.write('\n\t\t\tlabel="%s\\n[Instant]"' % (gID))
                # out.write('\n\t\t\tlabel="%s\\n[Instant]"' % (t))
        else:
            out.write('\n\t\t\tlabel="%s"' % gID)
            out.write('\n\t\t\tlabel="%s"' % t)
        out.write('\n\t\t];')

    def disconnectedPlaces(self):
        """
        Returns list of places without connecting arcs

        Returns
        ----------
        dcPlaces : list
            List containing the labels of places with no connecting arcs
        """

        dcPlaces = []
        for p in self.places:
            found = False
            for t in self.trans:
                if p in list(self.trans[t].inArcs.keys())+list(self.trans[t].outArcs.keys()):
                    found = True
                    break
            if not found:
                dcPlaces.append(p)

        return dcPlaces

    def disconnectedTrans(self):
        """
        Returns list of transitions without connecting arcs

        Returns
        ----------
        dcTrans : list
            List containing the labels of transitions with no connecting arcs
        """

        dcTrans = []
        for t in self.trans:
            if not len(self.trans[t].inArcs)+len(self.trans[t].outArcs):
                dcTrans.append(t)

        return dcTrans

    def verifyArcs(self):
        """
        Checks arcs to ensure all connect to real places
        """

        for t in self.trans:
            trans = self.trans[t]
            for i in trans.inArcs:
                ii = trans.inArcs[i]
                if not ii.start in self.places:
                    raise KeyError('Transition "%s" has ingoing arc to non-existant place "%s"' % (trans.label, ii.start))
            for o in trans.outArcs:
                oo = trans.outArcs[o]
                if not oo.end in self.places:
                    raise KeyError('Transition "%s" has outgoing arc to non-existant place "%s"' % (trans.label, oo.end))
        self.arcsVerified = True

    def fire(self, fireList):
        """
        Manages transition firing

        Parameters
        ----------
        fireList : list
            List of transitions to fire
        """
        for trans in fireList:
            self.calcTokens(trans.label)
            trans.lastFired = self.clock
        self.updateTokens()
        self.clearReady()
        for trans in fireList:
            trans.pcnStatus = 1.0
            if len(trans.reset):
                for p in trans.reset:
                    self.places[p].resetPlace()

    def updateTokenTime(self, time):
        """
        Updates time with tokens, 'totalTokenTime', attribute

        Parameters
        ----------
        time : float
            Step duration
        """
        if time is not None:
            for p in self.places:
                if self.places[p].tokens:
                    self.places[p].totalTokenTime += time

    def run(self, steps, maxClock=None, mode=None, history=False, fileOutput=True, endOnly=False, verbose=True):
        """
        Simulates Petri Net

        Parameters
        ----------
        steps : integer
            Number of steps to calculate
        maxClock : float
            Maximum clock time permitted
        mode : string
        *  all : All non-conflicting transitions are fired simultaneously
        *  single : One transition is randomly selected and fired
        *  stochastic : One transition is selected for firing in proportion
           to its rates (plus instant and fixed delay transitions)
        *  schedule : Transitions whose requisites are met are assigned a
           firing time based on their timing distribution, and are fired in
           chronological order (timings are assinged when requisites are
           met, and persist until either it is fire, or requisites are
           withdrawn).
        history : boolean
            Log state of Petri Net in history object
        fileOutput : boolean
            Toggles file output
        verbose : boolean
            Toggles amount of terminal print out

        Returns
        ----------
        lastFiles : list
            Path to last set of three output files if fileOutput enabled.
            Returns empty list otherwise.
        """
        # Check Petri Net has nodes
        if not len(self.places):
            raise RuntimeError('No places defined!')
        if not len(self.trans):
            raise RuntimeError('No transitions defined!')

        # Check validity of arcs
        if not self.arcsVerified:
            self.verifyArcs()

        # Create first entry in history object
        if history and not self.history.set:
            self.history.update(self)

        start = self.step

        # Get run mode
        if mode is None:
            mode = self.runMode
        if mode not in self.runModes:
            raise ValueError('"%s" does not refer to a valid run mode. Valid modes are: %r' % (mode, self.runModes))

        # Create file to record simulation
        if fileOutput:
            pfile, tfile, tlist = self.writeNetStart(mode)

        if not verbose:
            blockPrint()
        print ('='*80)
        if steps:
            while True:
                print ('Step %d of %d to %d' % (self.step + 1, start + 1, start + steps))
                # Transition(s) that will fire this step
                fireList = []
                time = None
                # self.buildConnectivity()

                # Get list of transitions whose requisites are met
                self.readyTrans()
                if len(self.ready):
                    if mode != 'schedule':
                        # Print transitions ready to fire
                        print('%d transitions ready to fire:' % len(self.ready))
                        for t in self.ready:
                            print('\t%s' % t.label)
                else:
                    print('No transitions ready to fire - End of integration\n')
                    break
                if mode == 'all':
                    self.resolveConflicts()
                    fireList = self.ready
                elif mode in ['single', 'stochastic', 'schedule']:
                    transition, time = self.selection(mode)
                    fireList.append(transition)

                # Update places' token holding time
                self.updateTokenTime(time)
                # Fire the transition(s)
                self.fire(fireList)
                # Advance step
                self.step += 1
                # Advance clock
                if time is not None:
                    self.clock += time
                    print('Advancing clock by %f %s to %f %s' % (time, self.units, self.clock, self.units))

                # Write state after this step to file
                if fileOutput and not endOnly:
                    self.writeNet(pfile, tfile, tlist, mode, fireList=fireList)
                # Update history object
                if history:
                    self.history.update(self)
                print('Completed step %d' % self.step)
                print ('-'*80)

                # Check places and transitions for terminate conditions
                endPlaces = False
                endTrans = False
                for p in self.places:
                    if self.places[p].checkLimits():
                        endPlaces = True
                for t in self.trans:
                    if self.trans[t].checkMax():
                        endTrans = True
                if endPlaces or endTrans:
                    if endPlaces:
                        print('Place token count has reached terminate condition. Ending simulation.')
                        self.placeExit = True
                    if endTrans:
                        print('Transition fire count has reached terminate condition. Ending simulation.')
                        self.transExit = True
                    if endOnly:
                        self.writeNet(pfile, tfile, tlist, mode, fireList=fireList)
                    break

                # End simulation if time limit is reached
                if time is not None and maxClock is not None:
                    if self.clock > maxClock:
                        print('%d steps simulated. Step %d reached. Max clock reached.' % (steps, self.step))
                        break
                if self.step >= start + steps:
                    print('%d steps simulated. Step %d reached. Simulation complete.' % (steps, self.step))
                    break

        else:
            if not verbose:
                enablePrint()
            print('Initial state rendered. No simulation conducted.')


        # Print end of step summary
        print('='*80+'\n')
        if steps:
            self.transSummary()
            self.placesSummary(mode, tOut=verbose, pfile=pfile if fileOutput else None)
            fin = '\nStep: %d' % self.step
            if self.clock is not None:
                fin += ' Clock: %.2e %s' % (self.clock, self.units)
            print('='*80+fin)
            print('='*80)
        lastFiles = []
        if fileOutput:
            for file in [pfile, tfile, tlist]:
                lastFiles.append(os.path.realpath(file.name))
                file.close()

        return lastFiles

class Place(object):
    """
    Place object to hold tokens

    Attributes
    ----------
    label : string
        Unique identifier given to the place
    tokens : integer
        Number of tokens held by place
    resetTokens : integer
        Number of tokens to held by the place if reset
    tokenChange : integer
        The net change in tokens the place experiences at a given step
    justReset : boolean
        Flags if place has just been reset
    min : integer
        Minimum number of tokens that this place can hold (Default = 0)
    max : integer
        Maximum number of tokens that this place can hold (Default = inf)
    limits : list of length two
        Simulation is terminated if number of tokens is outside limits[0] to
        limits[1]. Use 'None' entries for no bound
    ins : integer
        Number of tokens added to this place during simulation
    outs : integer
        Number of tokens removed from this place during simulation
    totalTokenTime : float
        Total duration for which the place has tokens
    group : integer
        Label used to group places for visualisation
    resetCount : integer
        Number of times the place has been reset
    """
    def __init__(self, label, tokens=0, min=0, max=None, limits=None, group=None):
        self.label = str(label)
        if ' ' in self.label:
            raise ValueError('"%s" is an invalid label, spaces are not permitted' % self.label)
        self.id, self.gID = genID(self.label)
        self.tokens = tokens
        self.resetTokens = tokens
        self.tokenChange = 0
        self.min = min
        self.max = max
        self.limits=limits
        if self.limits is None:
            self.limits = [None, None]
        assert len(self.limits) == 2, 'Invalid token range for place, "%s"' % self.label
        if self.limits[0] is not None and self.limits[1] is not None:
            assert self.limits[0] < self.limits[1], 'Place "%s" has invalid limits -- must be low to high'

        self.ins = 0
        self.outs = 0

        if group is not None:
            if group < 0:
                raise TypeError('Group designation must be positive (place "%s")' % self.label)
        self.totalTokenTime = 0.0
        self.group=group

        self.resetCount = 0
        self.justReset = False

    def checkLimits(self):
        """
        Returns true if the number of tokens is outside self.range

        Returns
        ----------
        status : boolean
            True if number of tokens is outside mandated limits, False
            otherwise
        """
        status = False
        if self.limits[0] is not None:
            if self.tokens < self.limits[0]:
                status = True
                print('Place "%s" has fewer tokens than its required limits' % self.label)
        if self.limits[1] is not None:
            if self.tokens > self.limits[1]:
                status = True
                print('Place "%s" has more tokens than its required limits' % self.label)
        return status

    def resetPlace(self):
        """
        Resets the place's token count to 'resetTokens'
        """
        print('Reseting place, "%s", from %d tokens to %d' % (self.label, self.tokens, self.resetTokens))
        self.tokens = self.resetTokens
        self.resetCount += 1
        self.justReset = True

    def changeTokens(self, n, safeMode=True):
        """
        Changes the number of tokens on a place while preserving ins and
        outs attributes -- To be used for changes made to the net outside of
        the normal simulation process

        Parameters
        ----------
        n : int
            Number of tokens to change place by
        safeMode : boolean
        * If True, token count cannot be set below zero (negative number
          default to zero).
        * If False, raises error

        Returns
        ----------
        status : boolean
            True if number of tokens is outside mandated limits, False
            otherwise
        """
        status = False
        new = self.tokens + n
        if n > 0:
            self.ins += n
        elif n < 0:
            if new < 0 and safeMode:
                new = 0
                self.outs += self.tokens
            else:
                self.outs += n
        self.tokens = new
        if not safeMode:
            assert(self.tokens-1), 'Token count, %d, on place "%s" has become invalid' % (self.tokens, self.label)
        if self.checkLimits():
            print('Call to changeTokens on place "%s" with n=%d has resulted in token limit being reached' % (self.label, n))
            status = True
        return status

class Trans(object):
    """
    Transition object to process tokens

    Attributes
    ----------
    label : string
        Unique identifier  given to the transition
    rate : float
        Mean rate of fire per unit time
    uniform : float
        Maximum wait for wait from 0 to 'uniform' (uniformly distributed)
    delay : float
        Wait time for fixed delay transitions
    weibull : list
        Length two or three list of parameters for a Weibull distribution
        (all floats), eta & beta, such that
        t = eta[-ln(X)]^-beta, and 0 < X < 1. Give a value for sigma to
        optionally include uncertainty in the data.
    beta : list
        Length two list of parameters for a Beta distribution (both floats)
        alpha & beta, with optional third scale parameter
    lognorm : list
        Length two list of parameters for a Lognormal distribution (both
        floats), mu & sigma
    cyclic : list
        Length two list of parameters for a cyclic distribution (both
        floats), frequency and offset
    maxFire : integer
        Maximum number of times the transition may fire before simulation is
        halted
    reset : list
        A list of places to reset on firing
    vote : integer
        Minimum number of incoming arcs required for voting behaviour
        (Default = None - i.e. no voting behaviour)
    waiting : list
        Step and clock time when the transition became ready to fire
    inArcs : dictionary
        Dictionary of incoming arcs
    outArcs: dictionary
        Dictionary of outgoing arcs
    pcn : boolean
        Indicates if transition has a place conditional input
    pcnStatus : float
        Indicates last 'con' (see getWait)
    ready : boolean
        Marks if the transition is capable of firing
    firedCount : integer
        Number of times this transition has been fired
    lastFired : integer
        Indicates the last step on which the transition was fired
    group : integer
        Label used to group transitions for visualisation
    """
    def __init__(self, label, rate=None, uniform=None, delay=None, weibull=None, beta=None, lognorm=None, cyclic=None, maxFire=None, reset=None, vote=None, group=None):
        self.label = str(label)
        if ' ' in self.label:
            raise ValueError('"%s" is an invalid label, spaces are not permitted' % self.label)
        self.id, self.gID = genID(self.label)
        self.rate = rate
        self.uniform = uniform
        self.delay = delay
        self.weibull = weibull
        if weibull is not None:
            if len(self.weibull) == 2:
                self.weibull.append(0.0)
            if len(self.weibull) != 3:
                raise ValueError('Weibull distribution requires list of two parameters, plus option uncertainty')
            # Adjust mean time to actual eta value for given beta
            self.weibull[0] = float(self.weibull[0]) / (math.gamma((1.0/self.weibull[1])+1.0))
        self.beta = beta
        if beta is not None:
            if len(self.beta) != 3:
                if len(self.beta) == 2:
                    self.beta.append(1.0)
                else:
                    raise ValueError('Beta distribution requires list of two parameters, plus optional scale parameter (transition "%s")' % self.label)
            if self.beta[0] <= 0.0 or self.beta[1] <= 0.0 or self.beta[2] <= 0.0:
                raise ValueError('Beta distribution must be positive & non-zero (transition "%s")' % self.label)
        self.lognorm = lognorm
        if lognorm is not None:
            if len(self.lognorm) != 2:
                raise ValueError('Lognormal distribution requires list of two parameters (transition "%s")' % self.label)
        self.cyclic = cyclic
        if cyclic is not None:
            if len(self.cyclic) != 2:
                raise ValueError('Cyclic distribution requires list of two parameters (transition "%s")' % self.label)
        self.maxFire = maxFire
        self.waiting = None
        self.inArcs = collections.OrderedDict()
        self.outArcs = collections.OrderedDict()
        self.pcn = False
        self.pcnStatus = 1.0
        self.ready = False
        self.firedCount = 0
        self.lastFired = None
        self.reset = reset if reset is not None else []
        if vote is not None:
            if type(vote) is not int:
                raise TypeError('Voting threshold (%r) must be positive integer (transition "%s")' % (vote, self.label))
            if vote < 1:
                raise ValueError('Voting threshold (%r) must be positive integer (transition "%s")' % (vote, self.label))
        self.vote = vote
        if group is not None:
            if type(group) is not int:
                raise TypeError('Group designation (%r) must be positive integer (transition "%s")' % (group, self.label))
            if group < 0:
                raise TypeError('Group designation (%r) must be positive integer (transition "%s")' % (group, self.label))
        self.group = group

    def addInArc(self, place, weight=1, type='std'):
        """
        Adds arc from 'place' to this transition

        Parameters
        ----------
        place : string
            Label of sending place
        weight : integer
            Weight assined to arc (becomes float for place conditional arcs)
        type : string
        Type of arc
        *  std : Standard Arc
        *  inh : Inhibit Arc
        *  pcn : Place Conditional Arc
        """
        # Check given type is valid
        valid = ['std', 'inh', 'pcn']
        if not type in valid:
            raise ValueError('"%s" is not a valid in arc type.\nValid arc types: %r' % valid)
        if not type == 'pcn' and weight < 1:
            raise ValueError('Non-place conditional arc from place, "%s", to transition, "%s" cannot be assined weight less than 1.' % (place, self.label))
        # Check that this arc does not already exist
        if not place in self.inArcs:
            self.inArcs[place] = Arc(place, self.label, weight=weight, type=type)
            if type == 'pcn':
                self.pcn = True
        else:
            raise KeyError('Arc from place, "%s", already exists on transition, "%s"' % (
                place, self.label))

    def rmInArc(self, place):
        """
        Removes an incoming arc of name, 'place', from a transition

        Parameters
        ----------
        place : string
            Label of sending place
        """
        count = 0 # Counter for number of place conditionals attached to this transition
        if self.pcn and self.inArcs[place].type == 'pcn':
            for iap in self.inArcs:
                if self.inArcs[iap] == 'pcn':
                    count += 1
            if count == 1:
                # Remove pcn flag if the last place conditional connection is severed
                self.pcn = False

        # Delete arc
        self.inArcs.pop(place)

    def addOutArc(self, place, weight=1):
        """
        Adds arc to 'place' from this transition

        Parameters
        ----------
        place : string
            Label of receiving place
        weight : integer
            Weight assined to arc
        type : string
        """
        # Check that this arc does not already exist
        if not place in self.outArcs:
            self.outArcs[place] = Arc(self.label, place, weight=weight)
        else:
            raise KeyError('Arc to place, "%s", already exists on transition, "%s"' % (place, self.label))

    def rmOutArc(self, place):
        """
        Removes an outgoing arc of name, 'place', from a transition

        Parameters
        ----------
        place : string
            Label of receiving place
        """
        self.outArcs.pop(place)

    def checkMax(self):
        """
        Returns true if the maximum number of firings of this transition has
        been reached

        Returns
        ----------
        See method description
        """
        if self.maxFire is not None:
            if self.firedCount >= self.maxFire:
                print('Transition "%s" has reached its maximum permitted fire count' % self.label)
                return True
        return False

class Arc(object):
    """
    Arc oject to connected places & transitions

    Attributes
    ----------
    start : string
        Lable of initital place/transition
    end : string
        Lable of initital transition/place
    weight : integer
        Number of tokens consumed/created by arc (becomes float for place
        conditional arcs)
    type : string
        *  std : Standard Arc
        *  inh : Inhibit Arc
        *  pnc : Place Conditional Arc
    """
    def __init__(self, start, end, weight=1, type='std'):
        self.type = type
        self.weight = weight
        self.start = start
        self.end = end

class History(object):
    """
    Records the history of the places and the transtions in a PetriNet

    Attributes
    ----------
    clock : list
       Gives the clock value at each step
    places : collections.OrderedDict
        History of places
    trans : collections.OrderedDict
        History of transitions
    set : boolean
        Indicates if update method has been run
    """
    def __init__(self):
        self.clock = []
        self.places = collections.OrderedDict()
        self.trans = collections.OrderedDict()
        self.set = False

    def update(self, pn):
        """
        Records a Petri Net's state to the history object

        Parameters
        ----------
        pn : PetriNet object
            The Petri Net whose state is to be recorded
        """
        # Get Petri Net clock state
        self.clock.append(pn.clock)
        # Record places
        for p in pn.places:
            if not self.set:
                self.places[p] = []
            self.places[p].append([pn.places[p].tokens, pn.places[p].resetCount])
        # Record transitions
        for t in pn.trans:
            if not self.set:
                self.trans[t] = []
            self.trans[t].append(pn.trans[t].firedCount)
        # Mark that lists for places and transitions have been created for this Petri Net structure
        self.set = True

def repeat(pn, maxClock, maxSteps=1E12, simsFactor=1.5E3, fixedNumber=None, history=True, fileOutput=True, endOnly=False, concatenate=False, analysisStep=1E2):#, log=True):
    """
    Automated repeated executions of a Petri Net

    Parameters
    ----------
    pn : PetriNet object
        The Petri Net structure to simulated
    maxClock : float
        The largest simulated time permitted in any one simulation
    maxSteps : float
        The largest number of simulation steps permitted in any one simulation
    simsFactor : float
        Parametises the number of simulations conducted. Repetition of
        simulations ends once the total simulated time supasses the product
        of maxClock and simsFactor.
    fixedNumber : integer (Default: None)
        Set exact number of simulations to perform, overruling simsFactor and
        maxClock parameters.
    history : boolean
        Collects and aggregates data if True
    analysisStep : float
        Time resolution of post-simulation analysis
    fileOutput : boolean (Default: True)
        Toggles whether results are written to file.
    endOnly : boolean (Default: False)
        Only the final stage of the Petri net is recorded when enabled.
    concatenate : boolean (Default: False)
        Condenses output files to one per type if enabled.
    # log : boolean
    #     Toggle log file
    """
    # Wall time log
    wall = int(time.time())
    # Back Petri Net structure
    backUp = copy.deepcopy(pn)

    i = 1
    summary = ''
    clock = 0.0
    histories = []
    stop = False
    # Set up record of place history
    pStats = collections.OrderedDict()
    for p in pn.places:
        pStats[p] = [0,0,0.0]
    # Set up record of transition history
    tStats = collections.OrderedDict()
    for t in pn.trans:
        tStats[t] = 0
    # Loop to run multiple simulations

    # if log:
    #     logF = open(os.path.join(os.getcwd(), 'log.txt'), 'w')
    while True:
        # if log:
        #     logF.write('%r >>> Beginning simulation %d\n' % (datetime.now().strftime('%d/%m/%Y %H:%M:%S'), i))
        print('\n'+'='*80+'\nBeginning simulation %d:' % i)
        pn.time = i
        # Run simulation
        lastFiles = pn.run(maxSteps, maxClock=maxClock, history=history, fileOutput=fileOutput, endOnly=endOnly)
        if fileOutput and concatenate:
            catResults(lastFiles, pn.name, pn.time, backUp.time)
        # Record place history
        for p in pn.places:
            pStats[p][0] += pn.places[p].ins
            pStats[p][1] += pn.places[p].outs
            pStats[p][2] += pn.places[p].totalTokenTime
        # Record transition history
        for t in pn.trans:
            tStats[t] += pn.trans[t].firedCount
        # Add to list of simulation histories
        if history:
            histories.append(copy.deepcopy(pn.history))
        # Update aggregated simulation time accrued
        clock += pn.clock
        # End loop if total time or simulation count limit has been reached
        if (clock >= maxClock*simsFactor and fixedNumber is None) or i == fixedNumber:
            # Print simulations' wall time
            wall = int(time.time() - wall)
            summary = '='*80 + '\n%d simulations, total clock: %.5g %s (%.5g %s per simulation)\nSimulation wall time: %d seconds\n' % (i, clock, pn.units, clock/float(i), pn.units, wall) + '='*80
            print('\n\n%s' % summary)
            break
        i += 1
        # Restore orginal Petri Net state for the next iteration
        pn = copy.deepcopy(backUp)
    # if log:
    #     logF.write('All simulations complete')
    #     logF.close()
    # Write summary of simulations to file
    file = open(os.path.join(os.getcwd(), '%s_Summary.txt' % pn.name) , 'w')
    file.write(summary)
    file.write('\n\nPlaces:\n')
    for p in pStats:
        file.write('%s %d in, %d out, Time with tokens: %.5g %s \n' % (p, pStats[p][0], pStats[p][1], pStats[p][2], pn.units))
    file.write('\nTransitions:\n')
    for t in tStats:
        file.write('%s fired %d Times\n' % (t, tStats[t]))
    file.close()

    # Amalgamate results -- may rewite this section in the future
    if history:
        # Record wall time
        wall = int(time.time())
        # Time section in the simulations that is being considered
        cTime = 0.0

        # Array-like objects to store data for places' tokens and resets and transitions' firing
        pDataT = collections.OrderedDict()
        pDataR = collections.OrderedDict()
        tData = collections.OrderedDict()
        pD = collections.OrderedDict()
        tD = collections.OrderedDict()

        # Summaries of data
        summaryPT = collections.OrderedDict()
        summaryPR = collections.OrderedDict()
        summaryT  = collections.OrderedDict()
        for p in pn.places:
            summaryPT[p] = []
            summaryPR[p] = []
        for t in pn.trans:
            summaryT[t] = []

        count = 0 # Number of entries
        first = False # Indicates first data point in an entry
        while True:
            # Array-like set-up
            for p in pn.places:
                pD[p] = []
                pDataT[p] = []
                pDataR[p] = []
            for t in pn.trans:
                tD[t] = []
                tData[t] = []
            for h in range(len(histories)):
                for p in pn.places:
                    pD[p] = []
                for t in pn.trans:
                    tD[t] = []
                first = False
                # Loop through histories
                for s in range(len(histories[h].clock)):
                    if not first:
                        first = True
                        # Record data points at start of time range
                        for p in pn.places:
                            pD[p].append([cTime, histories[h].places[p][s-1][0], histories[h].places[p][s-1][1]])
                        for t in pn.trans:
                            tD[t].append([cTime, histories[h].trans[t][s-1]])
                    # Record data points in time range
                    if histories[h].clock[s] >= cTime and histories[h].clock[s] < cTime+analysisStep:
                        for p in pn.places:
                            pD[p].append([histories[h].clock[s], histories[h].places[p][s][0], histories[h].places[p][s][1]])
                        for t in pn.trans:
                            tD[t].append([histories[h].clock[s], histories[h].trans[t][s]])
                    # Add final dummy data points when end of time range is reached and exit loop
                    elif histories[h].clock[s] >= cTime+analysisStep:
                        for p in pn.places:
                            pD[p].append([cTime+analysisStep, None, None])
                        for t in pn.trans:
                            tD[t].append([cTime+analysisStep, None])
                        first = False
                        break

                # Amalgamate data points in time range
                for p in pn.places:
                    vPT = 0
                    vPR = 0
                    if len(pD[p]) > 1:
                        for i in range(len(pD[p])-1):
                            # print(p,pD[p][i][0],pD[p][i][1],pD[p][i][1])
                            vPT += (pD[p][i+1][0]-pD[p][i][0])*pD[p][i][1]
                            vPR += (pD[p][i+1][0]-pD[p][i][0])*pD[p][i][2]
                        # print('')
                        pDataT[p].append(float(vPT)/float(analysisStep))
                        pDataR[p].append(float(vPR)/float(analysisStep))
                for t in pn.trans:
                    vT = 0
                    if len(tD[t]) > 1:
                        for i in range(len(tD[t])-1):
                            # print(t, tD[t][i])
                            vT += (tD[t][i+1][0]-tD[t][i][0])*tD[t][i][1]
                        tData[t].append(float(vT)/float(analysisStep))

            # Summarise place data
            for p in pn.places:
                nn = len(pDataT[p])
                assert nn == len(pDataR[p])
                n = float(nn)
                xPT = 0.0
                xPR = 0.0
                sPT = 0.0
                sPR = 0.0
                # Calculate the mean and its standard error
                if n:
                    for i in range(nn):
                        xPT += pDataT[p][i]
                        xPR += pDataR[p][i]
                    xPT /= n
                    xPR /= n
                    for i in range(nn):
                        sPT += (pDataT[p][i] - xPT)**2
                        sPR += (pDataR[p][i] - xPR)**2
                    if nn > 1:
                        sPT /= (n-1)
                        sPR /= (n-1)
                        sPT = math.sqrt(sPT)/math.sqrt(n)
                        sPR = math.sqrt(sPR)/math.sqrt(n)

                summaryPT[p].append([xPT, sPT, n])
                summaryPR[p].append([xPR, sPR, n])

            # Summarise transition data
            for t in pn.trans:
                nn = len(tData[t])
                n = float(len(tData[t]))
                xT = 0.0
                sT = 0.0
                # Calculate the mean and its standard error
                if n:
                    for i in range(nn):
                        xT += tData[t][i]
                    xT /= n
                    for i in range(nn):
                        sT += (tData[t][i] - xT)**2
                    if nn > 1:
                        sT /= (n-1)
                        sT = math.sqrt(sT)/math.sqrt(n)

                summaryT[t].append([xT, sT, n])

            # Advance clock and counter
            cTime += analysisStep
            count += 1
            # Break loop when clock limit is reached
            if cTime > maxClock:
                break

        # Write results to file
        writeTime = int(time.time())
        writeRepeatStats(summaryPT, analysisStep, count, '%s_tokenStats' % pn.name, writeTime)
        writeRepeatStats(summaryPR, analysisStep, count, '%s_resetStats' % pn.name, writeTime)
        writeRepeatStats(summaryT, analysisStep, count, '%s_transStats' % pn.name, writeTime)

        # Print wall time
        wall = int(time.time()) - wall
        print('Analysis wall time: %d seconds' % wall)

def catResults(lastFiles, name, ref, time):
    """
    Appends last output files to concatenated file

    Parameters
    ----------
    lastFiles : list
        Paths of the files to process
    name : string
        Petri Net label
    ref : integer
        Marker for current file-set
    time : integer
        UNIX timestamp of Petri Net
    """
    dir = os.path.dirname(lastFiles[0])
    for path, info in zip(lastFiles, ['Places', 'Trans', 'FireList']):
        # inter = ('>'*5+','+os.path.basename(path)+','+'<'*5+'\n').encode('utf-8')
        # inter = (('>'*5+',')*3+'\n').encode('utf-8')
        inter = ('>'*5+f',{ref},'+'<'*5+'\n').encode('utf-8')
        with open(os.path.join(dir, f'{name}_{info}_{time}.csv'), 'ab') as allFile:
            allFile.write(inter)
            with open(path, 'rb') as lastFile:
                shutil.copyfileobj(lastFile, allFile)
        # Delete  path
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


def writeRepeatStats(summary, analysisStep, count, name, time):
    """
    Writes statistical data from repeat method to .csv file

    Parameters
    ----------
    summary : list
        Statistical data from Petri Net simulations to write to file
    analysisStep : float
        Time resolution of post-simulation analysis
    count : integer
        Number of data points
    time : integer
        UNIX timestamp to use in filename
    """
    # Create file
    path = os.path.join(os.getcwd(), '%s_%d.csv' % (name, time))
    file = open(path, 'w')
    # Write first two column headers
    file.write('Step,Clock')
    # Write column headers for relevant Petri Nodes
    for l in summary:
        file.write(',%s av,%s se,%s n' % (l,l,l))
    file.write('\n')
    # Write data
    for i in range(count):
        line = '%d,%f' % (i, i*analysisStep)
        for l in summary:
            for a in range(3):
                line += ',%f' % summary[l][i][a]
        file.write('%s\n' % line)
    # Close file
    file.close()

############################################################################

if system() == 'Windows':
    # Windows doesn't let us have nice things in our docstrings
    __doc__ = __doc__.replace('█', '#')
    __doc__ = __doc__.replace('–', '--')
    for r in '╗╔═║╝╚':
        __doc__ = __doc__.replace(r, ' ')

if __name__ == '__main__':
    main()
