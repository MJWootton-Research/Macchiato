#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os, sys
from math import sqrt
from math import pi
import numpy as np
from fnmatch import filter

def main():
    tag = sys.argv[2]
    total = 0
    count = []
    sim = None
    with open(os.path.join(os.getcwd(), sys.argv[1]), 'r') as file:
        for line in file:
            if line.startswith('>'*5):
                if sim is not None:
                    count.append(sim)
                sim = 0
                continue
            if len(filter([line.split(',')[2]], tag)):
                sim += 1
                total += 1
        count.append(sim)
    nSims = len(count)
    std = np.std(count)
    prop = np.sum([1 if cc else 0 for cc in count])/nSims
    propEr = sqrt((prop-prop**2)/nSims)
    mean = np.mean(count)
    meanEr = std/sqrt(nSims)
    medn = np.median(count)
    mednEr = std*sqrt(pi/2*nSims)
    print(f'{tag} found {total} times in {nSims} simulations, {total/nSims} per simulation')
    print(f'Proportion in which occuring: {prop}±{propEr}')
    print(f'Mean: {mean}±{meanEr}')
    print(f'Median: {medn}±{mednEr}')

    non_zero = [cc for cc in count if cc]
    nSims = len(non_zero)
    mean = np.mean(non_zero)
    meanEr = std/sqrt(nSims)
    medn = np.median(non_zero)
    mednEr = std*sqrt(pi/2*nSims)
    print(f'Mean of non-zero: {mean}±{meanEr}')
    print(f'Median of non-zero: {medn}±{mednEr}')


if __name__ == '__main__':
    main()
