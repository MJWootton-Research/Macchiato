import os,sys
from collections import OrderedDict as OD
import xml.etree.ElementTree as ET
tree = ET.parse(sys.argv[1])
root = tree.getroot()

import Macchiato as mc

timings = ['delay','uniform','cyclic','weibull','rate','lognorm','beta']
placeIDs = OD()
transIDs = OD()

name = None
units = 'hrs'
maxClock = None
maxSteps = None
simsFactor = None
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
            if atrb['min'].lower() != 'none':
                iProp += '    MIN ' + atrb['min']
            if atrb['max'].lower() != 'none':
                iProp += '    MAX ' + atrb['max']
            if atrb['limits'].lower() != 'none':
                iProp += '    LIM ' + atrb['limits']

            ##########
            pn.addPlace(
                atrb['name'],
                int(atrb['tokens']),
                min=0 if atrb['min'].lower() == 'none' else atrb['min'],
                max=None if atrb['max'].lower() == 'none' else atrb['max'],
                limits=None if atrb['limits'].lower() == 'none' else atrb['limits'].split(':'),
            )
        # TRANSITIONS
        elif atrb['type'] == 'transition':
            transIDs[atrb['id']] = atrb['name']
            for tm in timings:
                if tm in atrb:
                    iProp += '  ' + tm + ':' + atrb[tm]
            if not iProp:
                iProp = '  instant'
            if atrb['reset'].lower() != 'none':
                iProp += '    RESET ' + atrb['reset']
            if atrb['maxFire'].lower() != 'none':
                iProp += '    MAX ' + atrb['maxFire']
            iProp = 'Trans: ' + atrb['name'] + ':' + iProp

            ##########
            # pn.addTrans()
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

            source = placeIDs[arcAtrb['source']] if arcAtrb['source'] in placeIDs else transIDs[arcAtrb['source']]
            target = placeIDs[arcAtrb['target']] if arcAtrb['target'] in placeIDs else transIDs[arcAtrb['target']]
            print(arcID + ': ' + source + ' to ' + target + f' with weight {weight}, type {arcT}')

        # STANDARD ARCS
        # if atrb['type'] == 'std':
        # TEST ARCS
        # RESET ARCS
        # PLACE-CONDITIONAL ARCS
        # PRINT
        # if iProp:
        #     print(iProp)

# print(placeIDs)
# print(transIDs)
