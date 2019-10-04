# pyC3D2OSIM 

Using this library you can extract and transform markers from C3D files into the OpenSim format and co-ordinate system

# Installation

Just check out this repository and run

`pip install .`

# Usage

To just extract the markers from a C3D/TRC file, you can run the script as follows:

`python extractMarkers.py input.c3d --output-file=output.trc`

You can also extract and/or rename specific markers using the --markers parameters:

`--markers m1 m2 m3=renamedM3 m4=renamedM4`

To translate all markers relative to another marker:

`--origin_marker m1`

To rotate the co-ordinate system around axes defined by markers you can use the --axes_markers parameter.
The first argument is the letter of the axes you want to rotate around followed by a pair of marker names:

`--axes_markers xy x1 x2 y1 y2`

You can also provide the .osim model file to automatically match the markers for rotation:

`--osim_model model.osim`

To translate between motion capture and OpenSim co-ordinate systems, you can use the --mocap_transform parameter.
For known systems (currently only Qualisys), you can put the following:

`--mocap_transform qualisys`

To define your own translation, put the axes in the order you want them to be swapped as the first parameter followed
by the rotation around each axes in degrees:

`--mocap_transform yxz 90 180 0`

You can also use this library as an imported module in your scripts.

# Issues

In case of any issues, please feel free to open an issue / submit a pull request.