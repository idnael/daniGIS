#!/usr/bin/python3
# coding: utf-8

# 202007 Daniel

# 20200928 poderia usar o modulo generico osgeo.ogr em vez do shapefile?

# TODO 20201215 how to find the reference def file? when writing it, use unicode?

import codecs, math, shapefile, re, sys, glob, subprocess, os, shutil, random, traceback, datetime
import pyexiv2
from optparse import OptionParser

PROJECTION = '''GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'''

KEY_LAT = "Exif.GPSInfo.GPSLatitude"
KEY_LAT_REF = "Exif.GPSInfo.GPSLatitudeRef"

KEY_LON = "Exif.GPSInfo.GPSLongitude"
KEY_LON_REF = "Exif.GPSInfo.GPSLongitudeRef"

KEY_DIR = "Exif.GPSInfo.GPSImgDirection"
KEY_DIR_REF = "Exif.GPSInfo.GPSImgDirectionRef"

def shapefile_files(name):
    if name.endswith(".shp"):
        name = name[:-4]
    return glob.glob(name+".*")

def dump_metadata(metadata):
    for k in metadata.keys():
        print(" KEY",k)
        try:
            print(" VAL", str(metadata[k].value))
        except:
            print(" VAL", sys.exc_info()[1])

def to_degrees(triple, positive):
    deg = float(triple[0])
    min = float(triple[1])
    sec = float(triple[2])
    return (deg + min/60 + sec / 3600) * (positive and +1 or -1)

class PhotoInfo:
    def __init__(self, direction, point):
        self.direction = direction
        self.point = point

class Photos2Shapefile:
    def __init__(self, shp_file, verbose=False, append=True):
        self.verbose = verbose
        
        prj_file = os.path.splitext(shp_file)[0] + ".prj"

        # hash from path to PhotoInfo
        self.photos = {}
                
        if append and os.path.exists(shp_file):
            reader = shapefile.Reader(shp_file)

            field_names = [field[0] for field in reader.fields[1:]]
            if field_names != ["path", "filename", "direction"]:
                self.error("Wrong format in existing %s" % shp_file)
            
            for i in range(len(reader)):
                element = reader.shapeRecord(i)
                
                if len(element.shape.points) != 1:
                    self.error("Error reading %s" % shp_file)

                file = element.record["path"]
                self.photos[file] = PhotoInfo(element.record["direction"], element.shape.points[0])
                                
            reader.close()

        for f in shapefile_files(shp_file):
            os.remove(f)
            
        with open(prj_file, "w") as f:
            f.write(PROJECTION)

        self.writer = shapefile.Writer(shp_file)
        self.writer.shapeType = shapefile.POINT

        self.writer.field('path', 'C', size=240)
        self.writer.field('filename', 'C', size=240)
        self.writer.field('direction', 'N')

        self.total_points = 0
        self.total_directions = 0
        self.total_errors = 0

    def error(self, msg):
        print(msg)
        sys.exit(1)
        
    def add_photo(self, file):
        try:
            metadata = pyexiv2.ImageMetadata(file)
            
            metadata.read()
            dump_metadata(metadata)

            if KEY_LAT in metadata.keys():
                lat = to_degrees(metadata[KEY_LAT].value, metadata[KEY_LAT_REF].value == "N")        
                lon = to_degrees(metadata[KEY_LON].value, metadata[KEY_LON_REF].value != "W")

                if KEY_DIR in metadata.keys():
                    # I only know "M" which means the ref is magnetic north
                    if KEY_DIR_REF not in metadata.keys() or metadata[KEY_DIR_REF].value != 'M':
                        self.total_errors +=1
                        print("%s: wrong value of %s" % (file, KEY_DIR_REF))
                        return
                    
                    self.total_directions += 1
                    direc = float(metadata[KEY_DIR].value)
                else:
                    direc = -1

                if options.verbose:
                    print("%s: lon=%f, lat=%f, direction=%s" % (file, lon, lat, direc >=0 and str(direc) or "UNKNOWN"))

                self.photos[file] = PhotoInfo(direc, [lon, lat])

                self.total_points +=1
                                
            else:
                print("%s: no coords" % (file))

        except:
            self.total_errors +=1
            # non fatal error

            print("ERRO!!!", traceback.format_exc())
            print("Error reading %s: %s" % (file, sys.exc_info()[1]))

    def save(self):
        last_id = 0
        for file, photo in self.photos.items():
            last_id +=1
            self.writer.record(id=last_id, path=file, filename=os.path.basename(file), direction=photo.direction)
            self.writer.point(* photo.point)
            
        self.writer.close()

        print("Added %i points, %i points with direction, %i errors" % (self.total_points, self.total_directions, self.total_errors))


def create_layer_def(shapefile_path):
    def_path = os.path.splitext(shapefile_path)[0] + ".__LAYER_DEF__.qlr"

    # TODO find relative to __file__ ... but follow symlinks... ???
    ref_file = "/home/daniel/comp/etc/daniGIS/photos2shp_layerreference.qlr"

    with open(ref_file, "r") as fd:
        xml = fd.read()

    NAME = os.path.basename(shapefile_path)
    ID = os.path.splitext(NAME)[0] + "_" + datetime.datetime.now().strftime("%Y%b%d_%H%M%S")
    xml = xml.replace("TESTLAYER_ID", ID).replace("TESTLAYER_NAME", NAME).replace("TESTLAYER_PATH", shapefile_path)

    print("Writing %s" % def_path)
    
    with open(def_path, "w") as fd:
        fd.write(xml)
    
    
    
USAGE = """
Get list of photo files, reads GPS EXIF info from each file, and creates a shapefile with exif info from photos. 
If direction info is present in exif, store it in 'direction' field, degrees from north in clockwise direction, from 0 to 360. If direction is unknown, use -1.

If shapefile already exists, add more photos to it. Existing files will be updates. For this to work you should always use paths relative to the same folder.

Don't do this:
cd MAINFOLDER
photos2shp --out photos.shp otherfolder/1.jpg
cd otherfolder
photos2shp --out photos.shp 1.jpg ## this will create duplicate file!

Requires pyshp and pyexiv2.

Example:
$ photos2shp --out myphotos.shp 20200804-*.jpg
Read files from stdin:
$ find -name "*.jpg" | photos2shp --out morephotos.shp -

You can then add the layer to your QGIS project by just importing the layer definition created
that is the shapefile name with the .__LAYER_DEF__.qlr suffix.

Or the difficult way:
You can then add the created shapefile in QGIS, with arrows showing the image direction:
Add the shapefile as a layer.
In simbology, specify 'Rule Based' and add 2 rules:
If field 'direction' is < 0, which means there is no direction data, use a simple symbol like a circle.
If field 'direction' is >=0, use an arrow (choose from SVG markers...) and in rotation specify the field 'direction'.
See example in photos2shp_qgi3_example.qgs!
"""

optparser = OptionParser(usage=USAGE)
optparser.add_option("", "--out", help="Shapefile to create")
optparser.add_option("-v", "--verbose", action="store_true")
optparser.add_option("-a", "--add", action="store_true")
(options, args) = optparser.parse_args()

if not options.out:
    optparser.error("Missing --out")

if not options.out.lower().endswith(".shp"):
    optparser.error("out should have .shp extension")

p2s = Photos2Shapefile(options.out, verbose=options.verbose, append=options.add)

if args == ["-"]:
    for line in codecs.getwriter('utf-8')(sys.stdin).readlines():
        p2s.add_photo(line.rstrip())
else:
    for file in args:
        p2s.add_photo(file)

p2s.save()

create_layer_def(options.out)
