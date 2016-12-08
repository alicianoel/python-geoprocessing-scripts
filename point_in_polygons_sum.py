# This script replicates the 'Join Attributes by Location' tool in QGIS
# to sum a specific value in a point layer based on a polygon layer.

from osgeo import ogr

# fill in these variables 
POLY_FILE = '/path/to/poly/file.shp'
POINT_FILE = '/path/to/point/file.shp'
POLY_FIELD_NAME = ""
POINT_FILED_NAME = ""

driver = ogr.GetDriverByName("ESRI Shapefile")

dataSource1 = driver.Open(POLY_FILE, 0)
poly_layer = dataSource1.GetLayer()

dataSource2 = driver.Open(POINT_FILE, 0)
point_layer = dataSource2.GetLayer()

for poly in poly_layer:
  total = 0
  poly_geom = poly.GetGeometryRef()
  point_layer.SetSpatialFilter(poly_geom)
  for point in point_layer:
    total = total + int(point.GetField("POINT_FILED_NAME"))
  point_layer.ResetReading()
  print poly.GetField(POLY_FIELD_NAME), total
