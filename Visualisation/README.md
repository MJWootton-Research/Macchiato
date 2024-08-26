# Visualisation

*To produce image files from Macchiato input files and simulation results*

## Dependencies

* [Python 3](https://www.python.org)
* [Graphiz](https://github.com/MJWootton-Research/Macchiato#graphviz)

## Usage

Two scripts are provided for visualisation. Due to the limitations of Graphviz, they are not recommended as tools to produce images for reports etc. For this purpose, a dedicated graphical tool such as Microsoft Visio is better suited, see [Macchiato Petri Net Graphical Construction](https://github.com/MJWootton-Research/Macchiato/tree/main/PetriNetDrawingTools/README.md). By default, Graphviz will attempt to enforce a hierarchical structure on the Petri Net visualisation, but this is unsuitable in many cases, particularly with systems with multiple looping sequences. To compensate for this, one can add a place or transition to a grouping, which will force objects to appear next to those of the same assignment. This is achieved through the addition of the label `GROUP` to the end of the line on which the object is specified followed by a space and an integer, which serves as its group reference. Note that places and transitions have separate groupings, i.e. the places and transitions in `P1 GROUP 1`, `P2 GROUP 1`, `T1:instant IN P1 OUT P2 GROUP 1`, and `T2:instant IN P2 OUT P1 GROUP 1` will be organised as two independent groups.

### [`mpn_to_dot.py`](https://github.com/MJWootton-Research/Macchiato/tree/main/Visualisation/mpn_to_dot.py)

This script will produce a single `*.dot` file (readable by Graphviz) depicting a Petri Net in its initial state, as described in an `*.mpn` file. Replacing `PetriNet.mpn` with the path of the target `*.mpn` , it is invoked with the following command:

```shell
python /path/to/mpn_to_dot.py /path/to/PetriNet.mpn format1 format2 format3
```

If multiple image file formats are supplied a file of each of the given types will also be produced. Formats should be specified by their file extension only, e.g. `svg` or `eps`.

**Note:** For best results, it is highly recommended to use vector image supporting formats (e.g. `svg`, `eps`, `pdf`) instead of raster images (e.g. `png`, `jpg`, `gif`, `bmp`).

### [`dot_to_image.py`](https://github.com/MJWootton-Research/Macchiato/tree/main/Visualisation/dot_to_image.py)

This script will read a `.dot` file, or a directory of `*.dot` files, and produce image files of types from the given list of formats. Substituting `/path/to/target` for the directory or file to be read, the script is executed with the following command, with the desired image formats listed at the end.

```shell
python /path/to/dot_to_image.py /path/to/target format1 format2 format 3
```
