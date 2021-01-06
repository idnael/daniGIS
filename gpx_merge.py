#!/usr/bin/python3
# coding: utf-8

# 202010 TODO: aceitar input kml???

from optparse import OptionParser
import os, subprocess, tempfile, sys, re
import shutil

import math, sys, datetime
from PIL import ImageColor

USAGE="Merge several tracks from gpx files into a single kml. Each line will be draw in a color depends on the age of the track "

optparser = OptionParser(usage=USAGE)
optparser.add_option("-o", "--out", help="KML file to create")
optparser.add_option("", "--color0", default="00FF00")
optparser.add_option("", "--color1", default="0000FF")
optparser.add_option("", "--decay_days", default="180")
optparser.add_option("", "--decay", default="0.8")

(options, args) = optparser.parse_args()

def color_decay(date, options):
    COLOR0 = ImageColor.getrgb("#"+options.color0)
    COLOR1 = ImageColor.getrgb("#"+options.color1)
    DAYS1 = int(options.decay_days)
    DECAY1 = float(options.decay)

    now = datetime.datetime.now()

    days = (now - date).days

    A = math.pow(1 - DECAY1, -1/DAYS1)

    f = math.pow(A, - days)

    rgb = [int(c1 + (c0 - c1)* f) for c0,c1 in zip(COLOR0, COLOR1)]
    rgb = [max(0, min(c, 255)) for c in rgb]

    rgb_str = ("%02x%02x%02x" % (rgb[0], rgb[1], rgb[2])).upper()
    return rgb_str

 
if not options.out:
   optparser.error("Tem que dar o output")

tmp_folder = tempfile.mkdtemp()
tmp_shp = os.path.join(tmp_folder, "tmp.shp")

count = 0

# a ordem everia ser importante...
# quero que os percursos mais recentes se sobreponham aos antigos
# isso quer dizer que os mais recentes devem ficar antes ou depois?
for inputfile in args:
   if not os.path.exists(inputfile):
      print("Non existing", inputfile)
      continue

   filename = os.path.basename(inputfile)

   if not re.match(r'^\d{8}', filename):
      print("Wrong filename format date", inputfile)
      continue
      
   # Formato da date que recebe como arg
   DATE_FORMAT = "%Y%m%d"

   print(inputfile, "...")
   
   # vou obter a data do inicio do filename
   ### !!!! OBTER de outra forma???
   # controlar por options? do timestamp? do proprio gpx??? mas o tracks nao tem o campo time (o waypoints é que tem). ha o campo name (String) = 2020-09-14 18:14:07 -- sera standard???
   
   date = datetime.datetime.strptime(filename[0:8], DATE_FORMAT) 

   color = color_decay(date, options)

   style = "PEN(c:#%s,w:5px)" % color

   # se tentar fazer append para um kml, na segunda vez o resultado vai ficar vazio. Por isso estou a criar um shp, e no fim converto para kml!
   cmd = ["ogr2ogr", "-f", "ESRI Shapefile", "-update", "-append", tmp_shp, "-sql", "SELECT '%s' as SOURCE, '%s' AS OGR_STYLE, '%s' as DATE from tracks" % (filename, style, date), inputfile  ]

   # print(cmd)

   if subprocess.Popen(cmd).wait() != 0:
      print("Erro", cmd)
      sys.exit(2)

   count += 1
   


# TEStar se exite...

if count ==0:
   print("Empty")
   sys.exit(2)


# O order by é para garantir que os mais recentes ficam depois e portanto se sobrepoe na visualizcao no oruxmaps(?)
cmd = ["ogr2ogr", "-f", "libkml", "-sql", "SELECT * FROM tmp AS percursos ORDER BY date", options.out, tmp_shp]
if subprocess.Popen(cmd).wait() != 0:
   print("Erro", cmd)
   sys.exit(2)

shutil.rmtree(tmp_folder)
