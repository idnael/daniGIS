Utility to create a shapefile from a collection of photos using gps position.
Uses image direction if available on exif data.

The created shapefile can be added as a layer in a QGis project, showing marks or arrows pointing in the direction the image was taken.


20200806
Why not store the exif times?
Because shapefile don't support a datetime field, only Date, as discussed here: https://gis.stackexchange.com/questions/267413/storing-datetime-values-in-shapefiles-using-qgis

