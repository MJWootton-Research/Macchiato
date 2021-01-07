import os
import sys
import glob

def main():
    """
    Extracts all final states of a given place in a direction sys.argv[1], indicated by results file column given by sys.argv[2].

    """
    nFiles = len(glob.glob1(os.path.join(os.getcwd(), sys.argv[1]),"Macchiato_PetriNet_Places_*.csv"))
    print("\nDiscovered %d files to inspect in \"%s\".\n" % (nFiles, sys.argv[1]))
    
    places = sys.argv[2].split(':')
    ends = []
    for place in places:
        placeN = int(place)
        for i in range(nFiles):
            inFile = open(os.path.join(os.getcwd(), sys.argv[1], "Macchiato_PetriNet_Places_%d.csv" % (i+1)))
            ends.append(None)
            for line in inFile:
                if len(line) == 1:
                    ends[-1] = int(ends[-1])
                    break
                else:
                    try:
                        ends[-1] = line.split(',')[placeN]
                    except IndexError:
                        pass


        outFile = open(os.path.join(os.getcwd(), '[%d].csv'%placeN), 'w')
        for e in ends:
            outFile.write('%d\n'%e)

    inFile.close()
    outFile.close()

if __name__ == '__main__':
    main()
