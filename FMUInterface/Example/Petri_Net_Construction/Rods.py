import os
import sys

def main():
    m = int(sys.argv[1])
    a = ""
    b = "\tTSDS1:instant IN PSDS1:1 PSDSD:1 PSDS2US:1:inh OUT"
    c = ""
    for n in range(1,m+1):
        a += "\tPRIB%d 0\n"%n + "\tPRPSF%d 0\n"%n + "\tPRPSS%d 0\n"%n + "\tPRDLS%d 0\n"%n + "\tPRDLF%d 0\n"%n + "\tPRIF%d 0\n"%n + "\tPRACTF%d 0\n"%n + "\tPRACT%d 1\n"%n
        b += " PRIB%d:1"%n
        c += "\tTRDLS%d:delay:0.000277777777777778 IN PRPSS%d:1 PRACTF%d:1:inh OUT PRDLS%d:1\n" % (n,n,n,n)
        c += "\tTRPSF%d:uniform:1.068376068 IN PRIB%d:1 OUT PRPSF%d:1 PNRFT:1\n" % (n,n,n)
        c += "\tTRPSS%d:delay:0.000277777777777778 IN PRIB%d:1 OUT PRPSS%d:1\n" % (n,n,n)
        c += "\tTRDLFa%d:uniform:2.777777778 IN PRPSS%d:1 OUT PRDLF%d:1 PNRFT:1\n" % (n,n,n)
        c += "\tTRIS%d:delay:0.000277777777777778 IN PRDLS%d:1 OUT PNRIT:1\n" % (n,n)
        c += "\tTRIF%d:uniform:9.259259259 IN PRDLS%d:1 OUT PRIF%d:1 PNRFT:1\n" % (n,n,n)
        c += "\tTRACTF%d:weibull:625000:1.2 IN PRACT%d:1 OUT PRACTF%d:1\n" % (n,n,n)
        c += "\tTRACTR%d:delay:120 IN PRACTF%d:1 OUT PRACT%d:1\n" % (n,n,n)
        c += "\tTRDLFb%d:instant IN PRPSS%d:1 PRACTF%d:1 OUT PRDLF%d:1\n" % (n,n,n,n)
    outMPN = open(os.path.join(os.getcwd(), "Rods_%d.mpn"%m), "w")
    outMPN.write(a+"\n"+b+"\n"+c)
    outMPN.close

if __name__ == "__main__":
    main()
