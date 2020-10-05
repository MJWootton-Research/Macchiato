# Macchiato
## A Simple Petri Nets Implementation for Python 3
### Version 20200916

© Dr. Mark James Wootton 2020 <br>
[`mark.wootton@nottingham.ac.uk`](mailto:mark.wootton@nottingham.ac.uk)

## Dependencies
* [Python 3](https://www.python.org)
* [Graphiz](http://graphviz.org) — optional, required only for visualisations

## Installation
Cloning the repository via [Git](https://git-scm.com) is the recommended method for installing Macchiato. Check to see if you have Git installed and the current version by opening a command-line terminal and running:
```
git --version
```
If no Git installation is found, consult [this page](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) for further instructions. Furthermore, it is recommended to [create a SSH key](https://docs.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) and [add it to one’s GitHub account](https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account) to eliminate the need for password entry during push & push requests.

The following command will create a local instance of the repository in the current working directory:
```
git clone git@github.com:MJWootton-Resilience-Projects/Macchiato.git
```

## Usage
For now, consult [`Macchiato.pdf`](Macchiato.pdf), until I've published updated documentation. *Note that is assumed that the reader is already familiar with the basics of standard Petri Net modelling*<sup>[1](#r1)</sup>*.*

### Macchiato Petri Net Files (`*.mpn`)
Macchiato Petri Net structures are stored in `*.mpn` files. One may also create and manipulate Petri Net structures in a Python script, using the tools provided in the module `PetriNet.py`, see *Scripting Tools*.

Substituting the appropriate file paths into the following command will run a batch of `N` simulations.

```
$ python /path/to/Macchiato.py /path/to/PetriNet.mpn N
```

Note that regardless of the locations of Macchiato or the Petri Net file, the simulation output will be delivered within the current working directory. Depending on system step up, one may need to substitute `python3` for `python`. The default version of Python can be found via `python --version`.

If `N` is omitted from the above command, the simulations will continue until the total time simulated across all iterations reaches the product of `maxClock` and `simsFactor`, see *Simulation Parameters*. 

#### Simulation Parameters
name

:  The label given to the Petri Net and used in output directories

units

:  The units of time to be used by the Petri Net (Default is “hrs”

#### Structure
...
#### Timed Transitions
...
#### Special Arc Properties
...
#### Special Transition Properties
...

### Visualisation
...

### Analysis
...

### Scripting Tools
...

## Acknowledgements
Thanks to Dr Robert *"Larus"* Lee for the [MS Visio](https://www.microsoft.com/en/microsoft-365/visio/flowchart-software) graphic tools.

## References

<b id="r1">[1]</b> Carl  Adam  Petri. *Kommunikation  mit  Automaten*  (In  German).   PhD  thesis,  Technical University Darmstadt, 1962.
