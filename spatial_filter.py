import datetime
import os

from collections import OrderedDict
import itertools
from operator import itemgetter, attrgetter
import glob
import subprocess
from collections import defaultdict
from pprint import pprint
import datetime

import ogr
import osr
import gdal

def spatialFilter(input_shp,aoi,output_shp):
  """selects features from 'input_shp' that intersect 'aoi', and places them in 'output_shp'.

  Args:
    input_shp: a .shp with features to be selected.
    aoi: a .shp to check for intersection against input_shp.
  Returns:
    output_shp: On success creates a shapefile named output_shp.shp with features from input_shp that intersect aoi.
  """
  inDataSource = driver.Open(input_shp, 0)
  inlayer = inDataSource.GetLayer()

  # create the data source
  outdata_source = driver.CreateDataSource(output_shp)
  # create the spatial reference, WGS84
  srs = osr.SpatialReference()
  srs.ImportFromEPSG(4326)
  # create the layer
  outlayer = outdata_source.CreateLayer("outlayer", srs, ogr.wkbPolygon)

  # Add input Layer Fields to the output Layer if it is the one we want
  inLayerDefn = inlayer.GetLayerDefn()
  for i in range(0, inLayerDefn.GetFieldCount()):
    fieldDefn = inLayerDefn.GetFieldDefn(i)
    fieldName = fieldDefn.GetName()
    outlayer.CreateField(fieldDefn)

  #load spatialfilter
  inspatialfilter = driver.Open(aoi, 0)
  inspatialfilterlayer = inspatialfilter.GetLayer()
  #get geometry for spatialfilter
  for inFeature in inspatialfilterlayer:
    spatialfiltergeom = inFeature.GetGeometryRef()

  inlayer.SetSpatialFilter(spatialfiltergeom)
  # Get the output Layer's Feature Definition
  outLayerDefn = outlayer.GetLayerDefn()
  for inFeature in inlayer:
    # Create output Feature
    outFeature = ogr.Feature(outLayerDefn)
    try:
      # Add field values from input Layer
      for i in range(0, outLayerDefn.GetFieldCount()):
        fieldDefn = outLayerDefn.GetFieldDefn(i)
        fieldName = fieldDefn.GetName()
        outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),inFeature.GetField(i))
      # Set geometry
      geom = inFeature.GetGeometryRef()
      outFeature.SetGeometry(geom.Clone())
      # Add new feature to output Layer
      outlayer.CreateFeature(outFeature)
    except Exception:
      sys.exc_clear()
  inlayer.SetSpatialFilter(None)


spatialFilter('input_file.shp','aoi_dissolve.shp','features_in_aoi.shp')
#'aoi_dissolve.shp' must be dissolved so that there is only one feature.
