import os,sys
from collections import OrderedDict as OD
import xml.etree.ElementTree as ET
tree = ET.parse(sys.argv[1])
root = tree.getroot()

import Macchiato as mc

nothing = ['', 'none']
timings = ['delay','uniform','cyclic','weibull','rate','lognorm','beta']
placeIDs = OD()
transIDs = OD()

name = None
units = 'hrs'
maxClock = None
maxSteps = None
simsFactor = 1.5E3
history = False
analysisStep = 1E2
fileOutput = True
endOnly = False
for item in root[0][0][0]:
    atrb = item.attrib
    if 'type' in atrb:
        # Petri Net Properties
        if atrb['type'] == 'properties':
            if name is not None:
                raise RuntimeError('Multiple properties object found')
            else:
                name = atrb['name']
            print('Name:', atrb['name'])
            print('units:', atrb['units'])
            print('maxClock:', atrb['maxClock'])
            print('maxSteps:', atrb['maxSteps'])
            print('simsFactor:', atrb['simsFactor'])
            maxClock = float(atrb['maxClock'])
            maxSteps = float(atrb['maxSteps'])
            simsFactor = float(atrb['simsFactor'])
print()
pn = mc.PetriNet(
    name=name,
    units=units,
)

for item in root[0][0][0]:
    atrb = item.attrib
    if 'type' in atrb:
        iProp = ''
        # PLACES
        if atrb['type'] == 'place':
            placeIDs[atrb['id']] = atrb['name']
            iProp = 'Place: ' + atrb['name'] + ' ' + atrb['tokens']
            if atrb['min'].lower() not in nothing:
                iProp += '    MIN ' + atrb['min']
            if atrb['max'].lower() not in nothing:
                iProp += '    MAX ' + atrb['max']
            if atrb['limits'].lower() not in nothing:
                iProp += '    LIM ' + atrb['limits']

            ##########
            pn.addPlace(
                atrb['name'],
                tokens=int(atrb['tokens']),
                min=0 if atrb['min'].lower() in nothing else atrb['min'],
                max=None if atrb['max'].lower() in nothing else atrb['max'],
                limits=None if atrb['limits'].lower() in nothing else atrb['limits'].split(':'),
            )
        # TRANSITIONS
        elif atrb['type'] == 'transition':
            transIDs[atrb['id']] = atrb['name']
            for tm in timings:
                if tm in atrb:
                    iProp += '  ' + tm + ':' + atrb[tm]
            if not iProp:
                iProp = '  instant'
            if atrb['reset'].lower() not in nothing:
                iProp += '    RESET ' + atrb['reset']
            if atrb['maxFire'].lower() not in nothing:
                iProp += '    MAX ' + atrb['maxFire']
            iProp = 'Trans: ' + atrb['name'] + ':' + iProp

            ##########
            maxFire = None if atrb['maxFire'].lower() in nothing else int(atrb['maxFire'])
            reset = None if atrb['reset'].lower() in nothing else atrb['reset']
            vote = None if atrb['vote'].lower() in nothing else int(atrb['vote'])
            instant = True
            for tm in timings:
                if tm in atrb:
                    instant = False
                    exec(f"pn.addTrans(atrb['name'], {tm}={[float(atm) for atm in atrb[tm].split(':')] if ':' in atrb[tm] else float(atrb[tm])}, maxFire={maxFire}, reset={reset}, vote={vote})")
                    break
            if instant:
                pn.addTrans(atrb['name'], maxFire=maxFire, reset=reset, vote=vote)
        # PRINT
        if iProp:
            print(iProp)

for item in root[0][0][0]:
    atrb = item.attrib
    if 'type' in atrb:
        if atrb['type'] in ['std', 'inh', 'tst', 'pcn']:
            arcT = atrb['type']
            arcAtrb = item[0].attrib
            arcID = atrb['id']
            for itemW in root[0][0][0]:
                try:
                    a = itemW[0]
                except IndexError:
                    continue
                if 'parent' in itemW[0].attrib:
                    if itemW[0].attrib['parent'] == arcID:
                        weight = itemW.attrib['weight'] if itemW.attrib['weight'] else 1

            weight = float(weight) if arcT == 'pcn' else int(weight)
            source = placeIDs[arcAtrb['source']] if arcAtrb['source'] in placeIDs else transIDs[arcAtrb['source']]
            target = placeIDs[arcAtrb['target']] if arcAtrb['target'] in placeIDs else transIDs[arcAtrb['target']]
            print(arcID + ': ' + source + ' to ' + target + f' with weight {weight}, type {arcT}')

            if arcAtrb['source'] in placeIDs and arcAtrb['target'] in placeIDs:
                raise RuntimeError(f'Cannot create arc from place to place ({placeIDs[arcAtrb["source"]]} & {placeIDs[arcAtrb["target"]]})')
            elif arcAtrb['source'] in transIDs and arcAtrb['target'] in transIDs:
                raise RuntimeError(f'Cannot create arc from transition to transition ({transIDs[arcAtrb["source"]]} & {transIDs[arcAtrb["target"]]})')

            if source in pn.trans:
                if arcT not in ['std', 'tst']:
                    raise TypeError(f'Outgoing arc must be standard (std/tst) type. Check transition {source}')
                pn.trans[source].addOutArc(target, weight=weight)
                if arcT == 'tst':
                    pn.trans[source].addInArc(target, weight=weight)
            elif target in pn.trans:
                pn.trans[target].addInArc(source, weight=weight, type=arcT if arcT != 'tst' else 'std')
                if arcT == 'tst':
                    pn.trans[target].addOutArc(source, weight=weight)
            else:
                print(pn.places.keys())
                print(pn.trans.keys())
                print(source, target)
                raise RuntimeError('This should not be possible')
mc.write(
    pn,
    overwrite=True,
    rp=[
        maxClock,
        maxSteps,
        simsFactor,
        history,
        analysisStep,
        fileOutput,
        endOnly,
    ]
)
