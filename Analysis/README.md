# Analysis

*Scripts for data extraction from Macchiato simulation results*

Note: The current version of these scripts has not yet been updated for concatenate mode (version 1-8 onwards).

## Dependencies

* [Python 3](https://www.python.org/)
  * [NumPy](https://numpy.org/)
  * [Matplotlib](https://matplotlib.org/)

## Usage

### [`OutcomesData.py`](https://github.com/MJWootton-Research/Macchiato/tree/main/Analysis/OutcomesData.py)

This script will provide information on the proportion of simulations ending in particular outcomes and the average durations of those sets, with [standard error](https://en.wikipedia.org/wiki/Standard_error) given, as well as a separate file containing the 10<sup>th</sup> and 90<sup>th</sup> percentiles. This is achieved by inspection of the final states of a given list of places, with with labels delimited by `:`, e.g. `P1:P2:P3`. The script will also produce a set of image files containing histograms to represent the results, with the axis labelled *"Duration"* taking the same units as those specified in the simulated Petri Net.

Example:

```shell
python /path/to/OutcomesData.py /path/to/Results_Folder P1:P2:P3
```

### [`TransFireData.py`](https://github.com/MJWootton-Research/Macchiato/tree/main/Analysis/TransFireData.py)

This script produces statistics for transition firings, with [standard error](https://en.wikipedia.org/wiki/Standard_error) given. Simply provide the directory containing the results for inspection and a plain text file will be produced in the current working directory.

Example:

```shell
python /path/to/TransFireData.py /path/to/Results_Folder
```

### [`ExtractPlaceEndings.py`](https://github.com/MJWootton-Research/Macchiato/tree/main/Analysis/ExtractPlaceEndings.py)

This script will extract the final state of every instance of a given set of places (delimited by `:`) within a directory and write them to file.

Example:

```shell
python /path/to/ExtractPlaceEndings.py /path/to/Results_Folder P1:P2:P3
```

### [`Places_wrt_Time.py`](https://github.com/MJWootton-Research/Macchiato/tree/main/Analysis/Places_wrt_Time.py)

This script will give the average number of tokens in each of a given set of places, plus standard error, sampling the simulation results at a user specified time interval. The total number of simulations continuing to run up to that point is also given. Image files containing graphs to illustrate these results are produced.

Example:

```shell
python /path/to/Places_wrt_Time.py /path/to/Results_Folder max_time interval P1:P2:P3
```

where `max_time` is the greatest time up to which the script will sample, `interval` is the gap between samplings, and `:` delimits the list of places to sample given at the end.
