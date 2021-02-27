#!/usr/bin/python3
# coding: utf-8

# 202011 Daniel

import pyexiv2, sys
from optparse import OptionParser

# para testar com as minhas fotos de teste mas sem as apagar:
# cp teste_exifpropagate_comdir.jpg _comdir.jpg
# cp teste_exifpropagate_semdir.jpg _semdir.jpg

# PARA USAR NO GEEQIE
# copiar isto para ~/.config/geeqie/applications/fotos_gps_propagate.desktop
# [Desktop Entry]
# Version=1.0
# Type=Application
# 
# # The name which appears in the menu:
# Name=Foto Exif propagate
# 
# #Name[cs]=
# #Name[fr]=
# #Name[de]=Vorlage
# 
# # Replace "command" with the actual command or script:
# Exec=foto_exif_propagate %F
# 
# 
# 
# # Change the following line to point to an icon of your choosing
# Icon=gtk-file
# 
# 
# # Desktop files that are usable only in Geeqie should be marked like this:
# Categories=X-Geeqie;
# OnlyShowIn=X-Geeqie;


# 20201129 TODO opcao --geeqie_install
# o .desktop podia indicar para abrir num terminal?
# opcao --ask - pergunta antes de mudar jpg

# 20201215
# Ao tirar fotos panoramicas com a app oficial do poocophone
# tem:
# Exif.GPSInfo.GPSLatitude
# Exif.GPSInfo.GPSLatitudeRef
# Exif.GPSInfo.GPSLongitudeRef
# mas nao tem: Exif.GPSInfo.GPSLongitude !

USAGE="Se tenho duas fotos tiradas no mesmo ponto (e direcao) mas uma tem informacao exif GPS (e direcao) e outra nao, uso este tool para propagar a informcao de uma para outra. Util por exemplo se tirar a mesma foto com telemovel e camera, ou ambas com telemovel, mas uma com uma app que nao regista a direcao mas tira fotos melhores nocturnas"
optparser = OptionParser(usage=USAGE)
optparser.add_option("-q", "--quiet", action="store_true")
(options, args) = optparser.parse_args()

#if len(args) < 2:
#    parser.error("Should have 2+ args")

def propagate(wantedkeys, title):
    # collects metadata for each file in args
    metadata = []
    for i in range(len(args)):
        m = pyexiv2.ImageMetadata(args[i])
        m.read()
        metadata.append(m)

    # sees if each file has all the necessary tags
    has = []
    for m in metadata:
        # must have all the wanted keys
        has.append(all([key in m.keys() for key in wantedkeys]))
        
    if sum(has) == 0:
        sys.stderr.write("No %s info\n" % title)
        
    elif sum(has) == len(args):
        sys.stderr.write("All have %s info\n" % title)
        
    elif sum(has) != 1:
        # nao sei decidir qual deve ser o source
        sys.stderr.write("Ambiguidade no %s\n" % title)
        
    else:
        # o source é um que tem has==true
        source = [i for i in range(len(args)) if has[i]] [0]
        
        #sys.stderr.write("Copy %s info from %s? (y/n)" % (title, args[source]))
        #sys.stderr.flush()
        #answear = sys.stdin.readline()
        if True: ###answear.strip().lower() == "y":
            sys.stderr.write("Propagating %s from %s\n" % (title, args[source]))
            if not options.quiet:
                for i in range(len(args)):
                    if i != source:
                        for key in wantedkeys:
                            metadata[i][key] = metadata[source][key].value
                        metadata[i].write()


KEY_LAT = "Exif.GPSInfo.GPSLatitude"
KEY_LAT_REF = "Exif.GPSInfo.GPSLatitudeRef"

KEY_LON = "Exif.GPSInfo.GPSLongitude"
KEY_LON_REF = "Exif.GPSInfo.GPSLongitudeRef"

KEY_DIR = "Exif.GPSInfo.GPSImgDirection"
KEY_DIR_REF = "Exif.GPSInfo.GPSImgDirectionRef"
                    
propagate([KEY_LAT, KEY_LAT_REF, KEY_LON, KEY_LON_REF], "GPS lat/lon")

propagate([KEY_DIR, KEY_DIR_REF], "Direction")
