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
$ git --version
```
If no Git installation is found, consult [this page](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) for further instructions. Furthermore, it is recommended to [create a SSH key](https://docs.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) and [add it to one’s GitHub account](https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account) to eliminate the need for password entry during push & push requests.

The following command will create a local instance of the repository in the current working directory:
```
$ git clone git@github.com:MJWootton-Resilience-Projects/Macchiato.git
```

## Usage
For now, consult [`Macchiato.pdf`](Macchiato.pdf), until I've published updated documentation. *Note that is assumed that the reader is already familiar with the basics of standard Petri Net modelling*<sup>[1](#r1)</sup>*.*

### Macchiato Petri Net Files (`*.mpn`)
Macchiato Petri Net structures are stored in `*.mpn` files. One may also create and manipulate Petri Net structures in a Python script, using the tools provided in the module `PetriNet.py`, see *Scripting Tools*.

Substituting the appropriate file paths into the following command will run a batch of `N` simulations.

```
$ python /path/to/Macchiato.py /path/to/PetriNet.mpn N
```

Note that regardless of the locations of Macchiato or the Petri Net file, the simulation output will be delivered within the current working directory. Depending on system step up, one may need to substitute `python3` for `python`. The default version of Python can be found via `$ python --version`.

If `N` is omitted from the above command, the simulations will continue until the total time simulated across all iterations reaches the product of `maxClock` and `simsFactor`, see *Simulation Parameters*. 

#### Structure

An `*.mpn` should be comprised of three sections — the simulation parameters, the places list, and the transitions list. To mark the beginning of of the latter two, the lines `Places` and `Transitions` must respectively appear in the file. Lines beginning with `#` are treated as comments. Comments must be on a separate line to structural lines. An example file is seen in [`Example.mpn`](https://github.com/MJWootton-Resilience-Projects/Macchiato/blob/master/Example.mpn).

#### Simulation Parameters

If a parameter is not specified in the `*.mpn` file, it takes its default value. To set a parameter, add a line with its name, followed directly by a single space and the desired value.

`name`: The label given to the Petri Net and used in output directories

`units`: The units of time to be used by the Petri Net (Default is `hrs`)

`runMode`: The mode of integration to be used for simulation (Default is `schedule`). Don't play with this setting unless you know what you are doing.

`dot`: Toggle creation of snapshots of the Petri Net during simulation in `*.dot` format (Default is `False`).

`visualise`: The file format for images produced from snapshots. Supported formats include, but are not limited to, `sgv` (recommended),  `pdf`, and `png` (Default is `None`, which produces no images. Note that `dot` must also be set to `True`, otherwise `visualise` will have no effect). 

`details`: Toggles label with Petri Net name, step, and clock in visualisations (Default is `True`)

`useGroup`: Toggles use of place and transition groups in visualisation (Default is `True`)

`orientationOption` Orientation of Petri Net in visualisations.  Options are `LR`, `RL`, `TB`, and `BT`.

`debug`: Default is `False`.

**Important Note:** It is not recommended to use the `dot` or `visualise` options beyond testing and development of Petri Nets and performance is significantly affected. Instead, consider using the post-simulation tools provided by `...` and `...`.

`maxClock`: Greatest clock duration permitted in any one simulation (Default is 10<sup>6</sup> `units` of time)

`maxSteps`: Greatest number of steps permitted in anyone simulation (Default is 10<sup>12</sup>)

`simsFactor`: Parameterises the total number of simulations performed (Default is 1.5×10<sup>3</sup>).  Repetition of simulations ends once the total simulated time surpasses the product of `maxClock` and `simsFactor`.  If a set number of simulations is specified at the command line, `simsFactor` is overruled.

#### Places

The places section of the file begins following the line `Places`.  To add a place, simple add a new line with the desired name (spaces are not permitted). By default, a place's initial token count is zero, but a value may be specified after a space on the same line, e.g. `SomePlace 2` will add a place of name *SomePlace* with two tokens at the start of each simulation.

#### Transitions

The transitions section of the file begins following the line `Transitions`. A transition and its properties are specified with a line with the following format (do not include brackets):

```
{Name}:{Timing}:{Parameters} IN {places} OUT {places} VOTE {threshold} RESET {places}
```

`Timing` specifies the duration from the enabling of a transition to its firing, which may be instantaneous, of a fixed length, or generated from a stochastic distribution. Most options require one or multiple parameters, subsequently delimited by `:`. The following timing options are available:

`instant`:

`delay`:

`uniform`

`cyclic`

`weibull`

`lognorm`

`rate`

`beta`

#### Special Arc Properties
...
#### Special Transition Properties
...

#### Example

```
# Petri Net Parameters
	name Test
	units hrs
	runMode schedule
	visualise None
	dot False

# Run Parameters
	maxClock 1E3
	maxSteps 100
	simsFactor 1

# Build Petri Net
Places
	P0 2
	P1
	P2
	P3

Transitions
	T0:lognorm:1:1 IN P0 OUT P1 P3
	T1:weibull:1:0.5 IN P1 OUT P2:2
	T2:delay:2 IN P2:2 P3:inh OUT P1
	T3:rate:15 IN P3:5:pcn P1 OUT P2
	R:cyclic:7:1 IN P2 RESET P0:P1:P3
	V:beta:1:2:0.25 IN P0 P1 P3 OUT P2 VOTE 2
```

#### Graphical Petri Net Construction with Microsoft Visio

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
