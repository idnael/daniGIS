photos2shp
Utility to create a shapefile from a collection of photos using gps position. Uses also image direction if available on exif data.

Also creates a QGis layer definition file, to easily add the layer to QGis, showing marks or arrows pointing in the direction the image was taken. This was tested in QGis 3.10.

For more info run:
photos2shp -h

https://github.com/idnael/daniGIS

20200806
Why not store the exif times?
Because shapefile don't support a datetime field, only Date, as discussed here: https://gis.stackexchange.com/questions/267413/storing-datetime-values-in-shapefiles-using-qgis

My default camera app doesn't write the exif direction.
Try OpenCamera instead!
https://opencamera.org.uk/
https://play.google.com/store/apps/details?id=net.sourceforge.opencamera


DEPS
sudo pip3 install pyshp
