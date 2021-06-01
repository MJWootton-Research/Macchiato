# Macchiato Petri Net Graphical Construction

## Dependencies

* [Macchiato](https://github.com/MJWootton-Resilience-Projects/Macchiato)
* [Microsoft Visio](https://www.microsoft.com/en/microsoft-365/visio/flowchart-software)

## Usage

To begin, make a copy of the the [example file](https://github.com/MJWootton-Resilience-Projects/Macchiato/blob/master/PetriNetDrawingTools/MacchiatoExample.vsdm), which contains the macro that exports the Petri Net as an `*.mpn` file.  A copy of the [stencil file](https://github.com/MJWootton-Resilience-Projects/Macchiato/blob/master/PetriNetDrawingTools/MacchiatoStencil.vssx) must be saved in the same directory or imported from the repository itself. Only objects from this stencil should be used.

When the example file is opened, a small banner will appear, asking the user  whether macros should be enabled. Click *"Enable Content"* as otherwise it will not be possible to export the Petri Net.

<img src="/home/chapelo/MEGA/Research/Macchiato/PetriNetDrawingTools/src/Macro.png" style="zoom: 33%;" />

If the Macchiato stencil is not already visible in the *"Shapes"* panel, import `MacchiatoStencil.vssx` via *"More Shapes"* → *"Open Stencil"*.

![](/home/chapelo/MEGA/Research/Macchiato/PetriNetDrawingTools/src/Shapes.png)

Make sure that *"Shape Data Window"* is enabled in the *"Data"* tab.

![](/home/chapelo/MEGA/Research/Macchiato/PetriNetDrawingTools/src/Data.png)

The *"Shape Data"* panel is used to set the parameters for each object in the model, including the system parameters block.

![](/home/chapelo/MEGA/Research/Macchiato/PetriNetDrawingTools/src/EditShapeData.png)

New objects are added, either by dragging shapes from the stencil, or by copying existing ones. Particularly in the latter case, make sure that every place and transition has a unique name.

Connections must be made using the arc objects and not the default Visio connectors. The arcs are connected by dragging their end points onto the places and transitions, either linked to the centre or to an attachment point.

| ![](/home/chapelo/MEGA/Research/Macchiato/PetriNetDrawingTools/src/Glue.png) | ![](/home/chapelo/MEGA/Research/Macchiato/PetriNetDrawingTools/src/Point.png) |
| ------------------------------------------------------------ | ------------------------------------------------------------ |

Additional points can be added from the *"Home"* tab. However, be certain that the correct object is selected as Visio will allow the user to attach a connection point associated with the currently selected object to any shape in the file, potentially causing failed or erroneous `*.mpn` export.

![](/home/chapelo/MEGA/Research/Macchiato/PetriNetDrawingTools/src/AddPoint.png)

The model is exported to an `*.mpn` file when the key combination *"ctrl*+*e"* is pressed. The output is saved in the same directory as the source file with the name specified in the system parameters object. Existing files will be overwritten, with no warning issued, so be careful not to unintentionally destroy work.

![](/home/chapelo/MEGA/Research/Macchiato/PetriNetDrawingTools/src/Parameters.png)

## Acknowledgements

Thank-you to Dr Robert *"Larus"* Lee for developing the original Macchiato stencil and macro for Microsoft Visio.
