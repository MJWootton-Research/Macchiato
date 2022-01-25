import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import matplotlib.ticker as mtick

conversion = 8766.0 # Mean year in hours

data = []

dataFile = open(os.path.join(os.getcwd(), sys.argv[1]))
for line in dataFile:
    data.append(line.strip().split(","))
dataFile.close()

w = 0
for d in data:
    w += len(d)-2

for d in data:
    for dd in range(len(d[2:])):
        d[dd+2] = float(d[dd+2])/conversion
    ymax = None
    if len(sys.argv) > 2:
        if "%" in sys.argv[2]:
            ymax = float(sys.argv[2][:-1])
        else:
            for dd in range(len(d)-1, 1, -1):
                if float(d[dd]) > float(sys.argv[2])/conversion:
                    d.pop(dd)
    print(d[0])
    plt.title(d[0])
    plt.ylabel("Proportion Predicted")
    plt.xlabel("Time [years]")
    h, _, _ = plt.hist(d[2:], bins=100, weights=np.ones(len(d[2:]))/(w/100.0), color="grey")
    print(np.max(h))
    n = False
    hmax = np.max(h)
    tot = 0
    for hh in h:
        if hh == hmax:
            # n = hh
            n = True
        if n:
            tot += hh

    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    # yticks = mtick.FormatStrFormatter('%.0f%%')
    # yticks = mtick.FormatStrFormatter('%.1f%%')
    # yticks = mtick.FormatStrFormatter('%.2f%%')
    yticks = mtick.FormatStrFormatter('%.3f%%')
    # yticks = mtick.FormatStrFormatter('%.4f%%')

    plt.gca().yaxis.set_major_formatter(yticks)

    if ymax is not None:
        plt.ylim(0,ymax)
    # plt.ylim(0,0.01)
    for type in ["png", "eps", "svg"]:
        plt.savefig("%s.%s" % (d[0],type), bbox_inches="tight") # TODO: remove " ", "[]", "()", "_"
    plt.clf()
