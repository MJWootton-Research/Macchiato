# Macchiato Changelog

## Version 1

* Earlier versions of Macchiato were distributed through a private GDrive folder

### Version 1-4

* Created private GitHub repository to manage access to Macchiato

#### Version 1-4-1

* Added new methods to PetriNet object to reveal objects with no connecting arcs
  * disconnectedPlaces 
  * disconnectedTrans

#### Version 1-4-2

* Rewrote in-simulation visualisation to use Graphviz command line tools

#### Version 1-4-3

* Fixed bug where the macro in the MS Visio Petri Net drawing tools gave incorrect output for reset transitions

#### Version 1-4-4

* Removed case sensitivity of Boolean options in *.mpn files

#### Version 1-4-5

* Added optional path selection in write function in Macchiato module

#### Version 1-4-6

* Added support for comments at the end of line in an `*.mpn` file
* Tidied up parsing of command-line arguments and added help text

### Version 1-5

* Merged `PetriNet.py` into `Macchiato.py`
* Miscellaneous bug fixes and small quality of life improvements
* Added `HistogramTime.py`
* Changed verbose mode tag to `-v` instead of `-V`

#### Version 1-5-1

* Changed method for silencing output in non-verbose mode
* Bug fixes for analysis scripts

### Version 1-6

* Added feature to restrict output files to a specific list of places and transitions

#### Version 1-6-1

* Custom calls to `Macchiato.PetriNet.run(...)` now respect verbosity toggle properly
