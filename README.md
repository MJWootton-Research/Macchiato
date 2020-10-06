# Macchiato
## A Simple Petri Nets Implementation for Python 3
### Version 1-4

© Dr. Mark James Wootton 2020 <br>
[`mark.wootton@nottingham.ac.uk`](mailto:mark.wootton@nottingham.ac.uk)

## Dependencies
* [Python 3](https://www.python.org)
* [Graphiz](http://graphviz.org) — only required by visualisation
* [NumPy](https://numpy.org/) — only required by analysis scripts
* [Matplotlib](https://matplotlib.org/) — only required by analysis scripts

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
For now, consult [`Macchiato.pdf`](Macchiato.pdf), until I've published updated documentation. *Note that is assumed that the reader is already familiar with the basics of standard Petri Net modelling*<sup>[[1]](#r1)</sup>*.*

### Macchiato Petri Net Files (`*.mpn`)
Macchiato Petri Net structures are stored in `*.mpn` files. One may also create and manipulate Petri Net structures in a Python script, using the tools provided in the module `PetriNet.py`, see [*Scripting Tools*](#scripting-tools).

Substituting the appropriate file paths into the following command will run a batch of `N` simulations.

```
$ python /path/to/Macchiato.py /path/to/PetriNet.mpn N
```

Note that regardless of the locations of Macchiato or the Petri Net file, the simulation output will be delivered within the current working directory. Depending on system step up, one may need to substitute `python3` for `python`. The default version of Python can be found via `$ python --version`.

If `N` is omitted from the above command, the simulations will continue until the total time simulated across all iterations reaches the product of `maxClock` and `simsFactor`, see [*Simulation Parameters*](#simulation-parameters). Additional terminal output can be activated by placing `V` at the end of the above command, but be aware that this will impact performance.

#### Structure

An `*.mpn` should be comprised of three sections — the simulation parameters, the places list, and the transitions list. To mark the beginning of of the latter two, the lines `Places` and `Transitions` must respectively appear in the file. Lines beginning with `#` are treated as comments. Comments must be on a separate line to structural lines. An example file is seen in [`Example.mpn`](https://github.com/MJWootton-Resilience-Projects/Macchiato/blob/master/Example.mpn).

#### Simulation Parameters

If a parameter is not specified in the `*.mpn` file, it takes its default value. To set a parameter, add a line with its name, followed directly by a single space and the desired value.

`name` — The label given to the Petri Net and used in output directories

`units` — The units of time to be used by the Petri Net (Default is `hrs`)

`runMode` — The mode of integration to be used for simulation (Default is `schedule`). Don't play with this setting unless you know what you are doing.

`dot` — Toggle creation of snapshots of the Petri Net during simulation in `*.dot` format (Default is `False`).

`visualise` — The file format for images produced from snapshots. Supported formats include, but are not limited to, `sgv` (recommended),  `pdf`, and `png` (Default is `None`, which produces no images. Note that `dot` must also be set to `True`, otherwise `visualise` will have no effect). 

`details` — Toggles label with Petri Net name, step, and clock in visualisations (Default is `True`)

`useGroup`: Toggles use of place and transition groups in visualisation (Default is `True`)

`orientationOption` — Orientation of Petri Net in visualisations.  Options are `LR`, `RL`, `TB`, and `BT`.

`debug` — Default is `False`.

`maxClock` — Greatest clock duration permitted in any one simulation (Default is 10<sup>6</sup> `units` of time)

`maxSteps` — Greatest number of steps permitted in anyone simulation (Default is 10<sup>12</sup>)

`simsFactor` — Parameterises the total number of simulations performed (Default is 1.5×10<sup>3</sup>).  Repetition of simulations ends once the total simulated time surpasses the product of `maxClock` and `simsFactor`.  If a set number of simulations is specified at the command line, `simsFactor` is overruled.

**Important Note:** It is not recommended to use the `visualise` option beyond testing and development of Petri Nets and performance is significantly affected. Instead, consider using the tools provided by [`mpn_to_dot.py`](https://github.com/MJWootton-Resilience-Projects/Macchiato/blob/master/mpn_to_dot.py) and [`dot_to_image.py`](https://github.com/MJWootton-Resilience-Projects/Macchiato/blob/master/dot_to_image.py) after the simulations are complete. If one is not intending to use `dot_to_image.py`, then it is also recommened to set `dot` to `False`.

#### Places

The places section of the file begins following the line `Places`.  To add a place, simple add a new line with the desired name (spaces are not permitted). By default, a place's initial token count is zero, but a value may be specified after a space on the same line, e.g. `P1 2` will add a place of name *P1* with two tokens at the start of each simulation.

#### Transitions

The transitions section of the file begins following the line `Transitions`. A transition and its properties are specified with a line with the following format (do not include brackets):

```
{Name}:{Timing}:{Parameters} IN {places} OUT {places} VOTE {threshold} RESET {places}
```

`Timing` specifies the duration from the enabling of a transition to its firing, which may be instantaneous, of a fixed length, or generated from a stochastic distribution. Most options require one or multiple parameters, subsequently delimited by `:` and expressed in terms of the parameter `units` where relevant. The following timing options are available:

`instant` — A instant transition will fire on the next simulation step with zero advancement of the system clock. If multiple instant transitions are simultaneously enabled, one will be chosen at random with uniform weight.

`delay:a` — A transition with a fixed delay fired after a set duration `a` once enabled.

`uniform:u` — A transition with a uniform distribution will fire at some time, *t*, in the interval 0 < *t* < `u`.

`cyclic:c:ω` — A cyclic transition fires at the next instance at with the simulation clock is a non-zero integer multiple of `c`. The second parameter `ω` allows one to apply an offset. For instance, if two transitions with the parameters `cyclic:1:0` and `cyclic:1:0.5` are persistently enabled, they will respectively fire at the system times, 1, 2, 3 `units` etc, and 1.5, 2.5, 3.5 `units` etc.

`weibull:<t>:β:σ` — A transition with this option will be characterised by a Weibull distribution<sup>[[2]](#r2)</sup> with mean `<t>` and shape parameter `β`. Its firing time, *t*, is given by <img src="https://render.githubusercontent.com/render/math?math=t = \eta [\ln(X)]^{-\beta}">, where *η* is the scale parameter, such that <img src="https://render.githubusercontent.com/render/math?math=\eta = %3C t %3E [\Gamma(\beta^{-1} %2B 1)]^{-1}">, and *X* is a random variable uniformly distributed in the range 0 < *X* < 1, with *Γ*  being the Gamma Function<sup>[[3]](#r3)</sup>. The parameter `σ` is optional and is used when the mean time has an associated uncertainty, such that the scale parameter used for each firing delay calculated is produced from a normal distribution<sup>[[4]](#r4)</sup> with mean equal to the default *η* and a standard deviation of `σ`.

`lognorm:μ:σ` — A transition with log-normal distribution<sup>[[5]](#54)</sup> timing fires after time, *t*, where <img src="https://render.githubusercontent.com/render/math?math=t = \exp(\mu %2B \sigma X)">, with *X* being a standard normal variable, and `μ` and `σ` respectively being the mean and standard deviation of the natural logarithm of the firing delay.

`rate:r` — A transition of this type fires with a constant rate parameterised by `r`. Firing time, *t*, is exponentially distributed <sup>[[6]](#r6)</sup>, such that <img src="https://render.githubusercontent.com/render/math?math=t = -r^{-1}\ln(X)">, where *X* is a random uniform variable in the range 0 < *X* < 1.

`beta:p:q:k` — A transition with the Beta Distribution<sup>[[6]](#r6)</sup> produces a firing delay, *t*, in the interval 0 < *t* < 1, parameterised by `p` and `q`, which weight the probability density towards the extreme or central regions of the available outcome space. An optional parameter `k` can be added to scale the distribution, such that the range of possible values becomes 0 < *t* < `k`.

Note that a transition must be continuously enabled for the duration from firing time generation until it fires. If its enabled status is interrupted, its scheduled firing time will be discarded.

#### Arc Properties
Any places listed after `IN` and `OUT` will be connected to the transition by incoming and outgoing arcs respectively and places listed should be separated by a single space. The weight of an arc is 1 by default and can be given some other value by appending it, separated by `:`, to the name of the relevant place in the list. for example, `IN P1 P2:3 P3 OUT P4 P5:2` specifies three incoming arcs, the second of which has a weight of 3, and two outgoing arcs, the latter of which has a weight of 2.

An incoming arc may be designated as a place conditional or inhibit arc with the code `:pnc` or `:inh` respectively, placed after the arc weight. The action of an inhibit arc is simple to disable its target transition when its weight is met, regardless of the status of the other arcs. A place conditional arc does not enable or disable its target transition but instead modifies its firing time parameters. The modification factor for a transition with *C* place conditional arcs is a function of the arc weights (which can be non-integer for place conditionals) and the number of tokens on the connected places, such that, <img src="https://render.githubusercontent.com/render/math?math=P = 1 %2B \sum_{i}^{c} W_{i} N_{i}">. The alterations to parameters are then, <img src="https://render.githubusercontent.com/render/math?math=a \rightarrow \frac{a}{P}">, <img src="https://render.githubusercontent.com/render/math?math=u \rightarrow \frac{u}{P}">, <img src="https://render.githubusercontent.com/render/math?math=c \rightarrow \frac{c}{P}">, <img src="https://render.githubusercontent.com/render/math?math=a \rightarrow \frac{a}{P}">, <img src="https://render.githubusercontent.com/render/math?math=%3C t %3E \rightarrow \frac{%3C t %3E}{P}">, <img src="https://render.githubusercontent.com/render/math?math=\mu \rightarrow \frac{\mu}{P}">, <img src="https://render.githubusercontent.com/render/math?math=k \rightarrow \frac{k}{P}">, and <img src="https://render.githubusercontent.com/render/math?math=r \rightarrow r P">.

#### Additional Transition Features
Transitions may also be given the properties `VOTE` and `RESET`. A voting transition does not require all of its incoming arc weights to be met to become enabled. Instead, only a given threshold need be met, placed after `VOTE`, separated by a single space. For example, a transition, `T1` with the place relationship given by `T1:instant IN P1 P2 P3 OUT P4 VOTE 2` would only require two of `P1`, `P2`, and `P3` to hold a token in order to fire. Note that *all* incoming arcs whose weight is satisfied are treated normally for the purposes of removing tokens when the transition fires. A reset transition has an associated list of places, delimited by `:` and following `RESET`, separated by a single space, e.g. `RESET P1:P2:P3`. When the transition fires, the places marked for reset are restored to the token count held at the beginning of the simulation.

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

### Scripting Tools

...

### Analysis

Python scripts are currently available to aid analysis of simulation results. As the data produced by Macchiato is saved `*.csv` format, it is fairly simple to produce new analysis tools and users are encouraged to do so.

#### [`TimingData.py`](https://github.com/MJWootton-Resilience-Projects/Macchiato/blob/master/Analysis/TimingData.py)

This script will provide information on the proportion of simulations ending in particular outcomes and the average durations of those sets, with [standard error](https://en.wikipedia.org/wiki/Standard_error) given. This is achieved by inspected of the final states of a given list of places. This list is specified by column numbers, which count from *zero*, and should be separated by `:`, e.g. `3:8:16`. The script will also produce a histogram to represent the results, with *"Duration"* taking the same units as those specified in the simulated Petri Net. A plain text file and an image are produced in the current working directory.

Example:
```
$ python TimingData.py Results_Folder 3:8:16
```

#### [`TransFireFrequency.py`](https://github.com/MJWootton-Resilience-Projects/Macchiato/blob/master/Analysis/TransFireFrequency.py)

This script produces statistics for transition firings, with [standard error](https://en.wikipedia.org/wiki/Standard_error) given. Simply provide the directory containing the results for inspection and a plain text file will be produced in the current working directory.

Example:
```
$ python TransFireFrequency.py Results_Folder
```

### Visualisation

#### Scripts

##### [`mpn_to_dot.py`](https://github.com/MJWootton-Resilience-Projects/Macchiato/blob/master/mpn_to_dot.py)

...

##### [`dot_to_image.py`](https://github.com/MJWootton-Resilience-Projects/Macchiato/blob/master/dot_to_image.py)

...

#### Visualisation Groupings

To assign a grouping for visualisation to a transition or place add the label `GROUP` to the end of the line on which it is specified followed by a space and an integer, which serves as its group assignment. Object in the same group will be displaced together if visualisation is active. Note that places and transitions have separate groupings, even if the same numbers are used.

## Acknowledgements
Thanks to Dr Robert *"Larus"* Lee for the [MS Visio](https://www.microsoft.com/en/microsoft-365/visio/flowchart-software) graphic tools.

## References

<b id="r1">[1]</b> Carl Adam Petri. *Kommunikation  mit  Automaten* (In  German). PhD thesis, Technical University Darmstadt, 1962.

<b id="r2">[2]</b> Athanasios Papoulis and S. Unnikrishna Pillai. Probability, *Random Variables and Stochastic Processes*.  McGraw Hill, 4<sup>th</sup> edition, 2002

<b id="r3">[3]</b> Eric W. Weisstein. *"Gamma Function." From* MathWorld*--A Wolfram Web Resource*. www.mathworld.wolfram.com/GammaFunction.html *Accessed October 2020*, Last edited: 2005.

<b id="r4">[4]</b> Eric W. Weisstein. *"Normal  Distribution." From* MathWorld*--A Wolfram Web Resource*. www.mathworld.wolfram.com/NormalDistribution.html *Accessed October 2019*, Last edited: 2019.

<b id="r5">[5]</b> Brian Dennis and G. P. Patil. *Lognormal Distributions, Theory and Applications*. Marcel Dekker New York, 1987.

<b id="r6">[6]</b> Eric W. Weisstein. *"Exponential Distribution." From* MathWorld*--A Wolfram Web Resource.* https://mathworld.wolfram.com/ExponentialDistribution.html
