#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
================================================================================
 _________   ______   ______  ______  _    _  _____  ______  _______  ______
| | | | | \ | |  | | | |     | |     | |  | |  | |  | |  | |   | |   / |  | \
| | | | | | | |__| | | |     | |     | |--| |  | |  | |__| |   | |   | |  | |
|_| |_| |_| |_|  |_| |_|____ |_|____ |_|  |_| _|_|_ |_|  |_|   |_|   \_|__|_/

    Programmer ~ Noun: One who converts coffee into code.

--------------------------------------------------------------------------------

Welcome to Macchiato – A Simple and Scriptable Petri Nets Implementation
Version 1-4-6
(c) Dr. Mark James Wootton 2016-2021
mark.wootton@nottingham.ac.uk
================================================================================

This modules read and writes Petri Net structures to .mpn file, and when called
from the command line, integrates them.

"""

# Python Modules
import os
import sys
import math
import time
import argparse
import textwrap

# Note to user: Remember to add the directory of Macchiato to your Python Path
import PetriNet as PN

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

def read(file):
    """
    Reads Macchiato Petri Net (.mpn) files and returns structure in PetriNet object

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
        print('WARNING: Given file is not ".mpn"')
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
                pn = PN.PetriNet(name=name, units=units, runMode=runMode, dot=dot,
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
                    pn.trans[label].reset = info.split(':')
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
        if len(rp) == 7:
            wr += '\tmaxClock %g\n' % rp[0]
            wr += '\tmaxSteps %d\n' % rp[1]
            wr += '\tsimsFactor %g\n' % rp[2]
            wr += '\thistory %s\n' % rp[3]
            wr += '\tanalysisStep %f\n' % rp[4]
            wr += '\tfileOutput %s\n' % rp[5]
            wr += '\tendOnly %s\n' % rp[6]
        else:
            raise IndexError('rp should be of length, 7, received(%d)' % len(rp))
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
            wr += ' RESET'
            for p in pn.trans[t].reset:
                wr += ' %s' % p
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
        return "\n".join([textwrap.fill(line, width) for line in textwrap.indent(textwrap.dedent(text), indent).splitlines()])

def main():
    intro=f'''
    Macchiato – A Simple and Scriptable Petri Nets Implementation
    Version 1-4-6
    (c) Dr. Mark James Wootton 2016-2021
    mark.wootton@nottingham.ac.uk
    '''
    # Command line arguments and help text
    parser = argparse.ArgumentParser(prog='Macchiato', description=intro, formatter_class=RawFormatter,epilog=None)
    parser.add_argument('file', nargs=1, metavar='input_file', type=argparse.FileType('r'), help='*.mpn file containing a Petri Net')
    parser.add_argument('nSims', nargs='?', default=None, type=int, help='Set fixed number of simulations to run [optional]')
    parser.add_argument('-V', '--verbose', dest='verbose', action='store_true', help='Enable verbose mode (slow)')
    args = parser.parse_args()

    # Get Petri Net and simulation parameters
    pn, rp = read(args.file[0].name)

    # Run specified simulation
    lt = time.localtime()[:6]
    print('='*80 + '\nBeginning simulations (%04d/%02d/%02d %02d:%02d:%02d)\n' % (lt[0], lt[1], lt[2], lt[3], lt[4], lt[5]) + '='*80)
    if not args.verbose:
        blockPrint()
    wall = time.time()
    PN.repeat(pn, rp[0], maxSteps=rp[1], simsFactor=rp[2], fixedNumber=args.nSims, history=rp[3], analysisStep=rp[4], fileOutput=rp[5], endOnly=rp[6])
    if not args.verbose:
        enablePrint()
    lt = time.localtime()[:6]
    print('='*80 + '\nSimulations complete after %.2g hrs (%04d/%02d/%02d %02d:%02d:%02d)\n' % (float(time.time()-wall)/float(3600), lt[0], lt[1], lt[2], lt[3], lt[4], lt[5]) + '='*80)
    print(os.getcwd())

if __name__ == '__main__':
    main()
