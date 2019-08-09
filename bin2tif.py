#!/usr/bin/env python

"""Quick extractor for converting TERRA REF .bin files to
   geoTIFF
"""

import os
import sys
import json
import datetime

import terraref.stereo_rgb
from terrautils.spatial import geojson_to_tuples
from terrautils.formats import create_geotiff
from terrautils.metadata import clean_metadata, get_terraref_metadata
import terrautils.betydb
import terrautils.lemnatec

terrautils.betydb.BETYDB_EXPERIMENTS = {
    "data" : [ {
        "experiment" : {"name": 'Dummy',
        "start_date": datetime.date.today().strftime('%Y-%m-%d'),
        "end_date": datetime.date.today().strftime('%Y-%m-%d'),
        "url": ''
        } } ]
    }

terrautils.lemnatec.SENSOR_METADATA_CACHE = os.getcwd()


def check_parameters():
    """Function to check that the parameters passed in appear to be OK
    Exceptions:
        RuntimeError is raised if there is a problem with the parameters
    """
    argc = len(sys.argv)
    if argc < 4:
        raise RuntimeError("Too few parameters were specified.")

    # Check that the paths are all the same
    base_path = os.path.dirname(sys.argv[1])
    for idx in range(2,4):
        test_path = os.path.dirname(sys.argv[idx])
        if not test_path == base_path:
            raise RuntimeError("All files need to be in the same folder")

    # Check that we have a left and right file name
    left, right, json = (None, None, None)
    for idx in range(1, 4):
        if sys.argv[idx].endswith("_left.bin"):
            left = idx
        if sys.argv[idx].endswith("_right.bin"):
            right = idx
        if sys.argv[idx].endswith(".json"):
            json = idx
    if not left or not right or not json:
        raise RuntimeError("Both left and right BIN files, and their JSON file, must be specified")

    # Make sure they exist
    if not os.path.exists(sys.argv[left]):
        raise RuntimeError("Left file is specified but isn't available")
    if not os.path.exists(sys.argv[right]):
        raise RuntimeError("Right file is specified but isn't available")
    if not os.path.exists(sys.argv[json]):
        raise RuntimeError("JSON file is specified but isn't available")

    # Return the set
    return (sys.argv[left], sys.argv[right], sys.argv[json])

def do_work(left_file, right_file, json_file):
    """Make the calls to convert the files
    Args:
        left_file(str): Path to the left BIN file
        right_file(str): Path to the right BIN file
        json_file(str): Path to the JSON file
    """
    out_left = os.path.splitext(left_file)[0] + ".tif"
    out_right = os.path.splitext(right_file)[0] + ".tif"
    file_name, file_ext = os.path.splitext(json_file)
    out_json = file_name + "_updated" + file_ext

    # Load the JSON
    with open(json_file, "r") as infile:
        metadata = json.load(infile)
        if not metadata:
            raise RuntimeError("JSON file appears to be invalid: " + json_file)
        md_len = len(metadata)
        if md_len <= 0:
            raise RuntimeError("JSON file is empty: " + json_file)

    # Prepare the metadata
    clean_md = get_terraref_metadata(clean_metadata(metadata, 'stereoTop'), 'stereoTop')

    # Pull out the information we need from the JSON
    try:
        left_shape = terraref.stereo_rgb.get_image_shape(clean_md, 'left')
        gps_bounds_left = geojson_to_tuples(clean_md['spatial_metadata']['left']['bounding_box'])
        right_shape = terraref.stereo_rgb.get_image_shape(clean_md, 'right')
        gps_bounds_right = geojson_to_tuples(clean_md['spatial_metadata']['right']['bounding_box'])
    except KeyError:
        print("ERROR: Spatial metadata not properly identified in JSON file")
        return
 
    # Make the conversion calls
    print("creating %s" % out_left)
    left_image = terraref.stereo_rgb.process_raw(left_shape, left_file, None)
    create_geotiff(left_image, gps_bounds_left, out_left, asfloat=False, system_md=clean_md, compress=False)

    print("creating %s" % out_right)
    right_image = terraref.stereo_rgb.process_raw(right_shape, right_file, None)
    create_geotiff(right_image, gps_bounds_right, out_right, asfloat=False, system_md=clean_md, compress=True)

    # Write the metadata
    print("creating %s" % out_json)
    with open(out_json, "w") as outfile:
        json.dump(clean_md, outfile, indent=4)

if __name__ == "__main__":
    os.environ['BETYDB_KEY'] = "0"
    left_file, right_file, json_file = check_parameters()
    do_work(left_file, right_file, json_file)
