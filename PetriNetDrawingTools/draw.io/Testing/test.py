import os,sys
from collections import OrderedDict as OD
import xml.etree.ElementTree as ET
tree = ET.parse(sys.argv[1])
root = tree.getroot()

timings = ['delay','uniform','cyclic','weibull','rate','lognorm','beta']
placeIDs = OD()
transIDs = OD()
for item in root[0][0][0]:
    atrb = item.attrib
    if 'type' in atrb:
        iProp = ''
        # PLACES
        if atrb['type'] == 'place':
            placeIDs[atrb['name']] = atrb['id']
            iProp = 'Place: ' + atrb['name'] + ' ' + atrb['tokens']
            if atrb['min'].lower() != 'none':
                iProp += '    MIN ' + atrb['min']
            if atrb['max'].lower() != 'none':
                iProp += '    MAX ' + atrb['max']
            if atrb['limits'].lower() != 'none':
                iProp += '    LIM ' + atrb['limits']
        # TRANSITIONS
        if atrb['type'] == 'transition':
            transIDs[atrb['name']] = atrb['id']
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
        # PRINT
        if iProp:
            print(iProp)

for item in root[0][0][0]:
    atrb = item.attrib
    if 'type' in atrb:
        if atrb['type'] in ['std', 'inh', 'tst', 'pcn']:
            arcAtrb = item[0].attrib
            print(atrb['id'] + ': ' + arcAtrb['source'] + ' to ' + arcAtrb['target'] + ' with weight ')# + arcAtrb['weight'])
            # print(item[0].attrib)
            # print(atrb)
        # STANDARD ARCS
        # if atrb['type'] == 'std':
        # TEST ARCS
        # RESET ARCS
        # PLACE-CONDITIONAL ARCS
        # PRINT
        # if iProp:
        #     print(iProp)
