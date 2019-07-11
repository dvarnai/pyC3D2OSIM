# Extract marker locations from C3D file and convert them into OpenSim 4.0 TRC format

import argparse
import c3d
from itertools import compress
import numpy as np
import sys
import math
from scipy.spatial.transform import Rotation

# Command-line interface definition
parser = argparse.ArgumentParser(description='Extract marker locations from C3D files and save in TRC format.')
parser.add_argument('input_file', metavar='I', type=argparse.FileType('rb'),
                    help='C3D file to use')
parser.add_argument('--output_file', metavar='O', type=argparse.FileType('w'), default=sys.stdout,
                    help='TRC file to write')
parser.add_argument('--markers', metavar='M', type=lambda kv: kv.split('=', 1), nargs='+', action='append',
                    default=None, help='List of markers to read and optionally renamed')
parser.add_argument('--origin_marker', metavar='R', type=str, default=None,
                    help='Transform markers relative to this marker')
parser.add_argument('--mocap_transform', metavar='M', type=str, nargs='+', default=[],
                    help='MoCap system name or list of rotations in degrees along the axes in the OpenSim coordinate '
                         'system optionally trailed by '
                         'correct axes order eg. yxz 90 180 0.')
# Loads a C3D file and maps variables to TRC variables
def loadC3D(file):
    reader = c3d.Reader(file)
    data = dict()
    data["NumFrames"] = reader.header.last_frame-reader.header.first_frame+1
    data["DataRate"] = reader.header.frame_rate
    data["CameraRate"] = reader.header.frame_rate
    data["NumMarkers"] = len(reader.point_labels)
    data["Units"] = "mm"
    data["OrigDataRate"] = reader.header.frame_rate
    data["OrigDataStartFrame"] = reader.header.first_frame
    data["OrigNumFrames"] = reader.header.last_frame-reader.header.first_frame+1
    data["Labels"] = list(map(lambda x: x.strip(), reader.point_labels))

    data["Data"] = np.empty(shape=(data["NumMarkers"], data["NumFrames"], 3), dtype=np.float)
    for i, points, analog in reader.read_frames():
        for label, frameData in enumerate(points[:,0:3]):
            data["Data"][label][i-reader.header.first_frame] = frameData

    return data

# Translates marker positions relative to another marker
def translateToOrigin(data, origLabel):
    data["Data"] = data["Data"] - data["Data"][data["Labels"].index(origLabel)]
    return data

# Filters unnecessary markers and renames them
def filterMarkers(data, markers):

    # Filter markers
    data["NumMarkers"] = len(markers)
    orig_markers = list(map(lambda x: x[0], markers))
    list_filter = list(map(lambda x: x in orig_markers, data["Labels"]))
    data["Labels"] = list(compress(data["Labels"], list_filter))
    data["Data"] = data["Data"][list_filter]

    # Rename markers
    remap = dict(map(lambda x: (x[0], x[1] if len(x) == 2 else None), markers))
    for i, label in enumerate(data["Labels"]):
        if remap[label] is not None:
            data["Labels"][i] = remap[label]

    return data

# Transform coordinates from lab coordinate system to OpenSim coordinate system
def mocapTransform(data, transform):

    permutation = [0,1,2]
    if len(transform) == 1:
        if transform[0] == 'qualisys':
            rotations = [90, 180, 0]
        else:
            raise ValueError("Unknown mocap system")
    elif len(transform) == 3:
        rotations = transform
    elif len(transform) == 4:
        rotations = transform[1:4]
        for i in range(3):
            permutation[i] = ord(transform[0][i])-ord('x')
            if permutation[i] > 2 or permutation[i] < 0:
                raise ValueError("Incorrect value for axes order")

    else:
        raise ValueError("Transform must be a known mocap system or a list of rotation angles optionally trailed by "
                         "order of axes")

    rot = Rotation.from_euler('XZY', np.array(rotations)[[0,2,1]]*[1,-1,1], degrees=True)

    data["Data"] = rot.apply(data["Data"].reshape(-1,3)[:,permutation]).reshape(data["Data"].shape)
    return data

# Writes the data in a TRC file
def writeTRC(data, file):

    # Write header
    file.write("PathFileType\t4\t(X/Y/Z)\toutput.trc\n")
    file.write("DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames\n")
    file.write("%d\t%d\t%d\t%d\tmm\t%d\t%d\t%d\n" % (data["DataRate"], data["CameraRate"], data["NumFrames"],
                                                     data["NumMarkers"], data["OrigDataRate"],
                                                     data["OrigDataStartFrame"], data["OrigNumFrames"]))

    # Write labels
    file.write("Frame#\tTime\t")
    for i, label in enumerate(data["Labels"]):
        if i != 0:
            file.write("\t")
        file.write("\t\t%s" % (label))
    file.write("\n")
    file.write("\t")
    for i in range(len(data["Labels"]*3)):
        file.write("\t%c%d" % (chr(ord('X')+(i%3)), math.ceil((i+1)/3)))
    file.write("\n")

    # Write data
    for i in range(len(data["Data"][0])):
        file.write("%d\t%f" % (i, 1/data["DataRate"]*i))
        for l in range(len(data["Data"])):
            file.write("\t%f\t%f\t%f" % tuple(data["Data"][l][i]))
        file.write("\n")


if __name__ == '__main__':
    # Parse command line arguments
    args = parser.parse_args()

    # Load C3D file
    data = loadC3D(args.input_file)

    # Translate markers relative to origin marker
    if(args.origin_marker is not None):
        translateToOrigin(data, args.origin_marker)

    # Delete unnecessary markers and rename them
    if(args.markers is not None):
        filterMarkers(data, args.markers[0])

    # MoCap transformation
    if(len(args.mocap_transform) > 0):
        mocapTransform(data, args.mocap_transform)

    # Write the data into the TRC file
    writeTRC(data, args.output_file)

    # Clean up
    args.input_file.close()
    args.output_file.close()