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
* Tidied up parsing of command-line arguments added help text
