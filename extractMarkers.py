# Extract marker locations from C3D file and convert them into OpenSim 4.0 TRC format

import argparse
import c3d
from itertools import compress
import numpy as np
from scipy.spatial.transform import Rotation

# Command-line interface definition
parser = argparse.ArgumentParser(description='Extract marker locations from C3D files and save in TRC format.')
parser.add_argument('input_file', metavar='I', type=argparse.FileType('rb'),
                    help='C3D file to use')
parser.add_argument('output_file', metavar='O', type=argparse.FileType('w'),
                    help='TRC file to write')
parser.add_argument('--markers', metavar='M', type=str, nargs='+', default=None,
                    help='List of markers to read')
parser.add_argument('--origin_marker', metavar='R', type=str, default=None,
                    help='Transform markers relative to this marker')
parser.add_argument('--mocap_transform', metavar='M', type=str, nargs='+', default=[],
                    help='MoCap system name or list of rotations along the axis')

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
            data["Data"][label][i-1] = frameData

    return data

def translateToOrigin(data, origLabel):
    data["Data"] = data["Data"] - data["Data"][data["Labels"].index(origLabel)]
    return data

def filterMarkers(data, markers):
    data["NumMarkers"] = len(markers)
    list_filter = list(map(lambda x: x in markers, data["Labels"]))
    data["Labels"] = list(compress(data["Labels"], list_filter))
    data["Data"] = data["Data"][list_filter]
    return data

def mocapTransform(data, transform):

    rotations = transform
    if len(transform) == 1:
        if transform[0] == 'qualisys':
            rotations = [90, 180, 0]
        else:
            raise ValueError("Unknown mocap system")
    elif len(transform) != 3:
        raise ValueError("Transform must be a known mocap system or a list of rotation angles")

    rot = Rotation.from_euler('xyz', rotations, degrees=True)

    data["Data"] = rot.apply(data["Data"].reshape(-1,3)).reshape(data["Data"].shape)
    return data


def writeTRC(data, file):
    print("Write file")

if __name__ == '__main__':
    # Parse command line arguments
    args = parser.parse_args()

    # Load C3D file
    data = loadC3D(args.input_file)

    # Translate markers relative to origin marker
    if(args.origin_marker is not None):
        translateToOrigin(data, args.origin_marker)

    # Delete unnecessary markers
    if(args.markers is not None):
        filterMarkers(data, args.markers)

    # MoCap transformation
    if(len(args.mocap_transform) > 0):
        mocapTransform(data, args.mocap_transform)

    # Write the data into the TRC file
    writeTRC(c3d, args.output_file)