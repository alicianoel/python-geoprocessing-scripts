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


def FlatLayerFromRasterize(input_shp, output_tif, output_flat_shp,
                             width=70000, height=35000, attribute='asset_id'):
    """Creates flat file by Rasterizing layer.

    Args:
      input_shp: Input shapefile path.
      output_tif: Path to output raster tif.
      output_flat_shp: Output flat shapefile after polygonize the raster.
      width: Width of raster. Default value is 120,000. This is calculated
      to burn (Xmax - Xmin)/120000 this size pixel in width and
      (Ymax -Ymin)/60000 pixel size in height.
      height: Output raster height in pixel.
      attribute: Attribute value to be used in rasterization.

    """

    ds = ogr.Open(input_shp)
    layer = ds.GetLayer()
    xmin, xmax, ymin, ymax = layer.GetExtent()
    driver = gdal.GetDriverByName('GTiff')
    raster_dst = driver.Create(output_tif, width, height,
                               1, gdal.GDT_Int32, options=['COMPRESS=LZW'])
    raster_dst.GetRasterBand(1).Fill(0)
    raster_dst.GetRasterBand(1).SetNoDataValue(0)
    x_res = (xmax - xmin) / width
    y_res = (ymax - ymin) / height
    raster_transform = [xmin, x_res, 0, ymax, 0, -y_res]
    raster_dst.SetGeoTransform(raster_transform)
    srs_info = osr.SpatialReference()
    srs_info.SetWellKnownGeogCS('WGS84')
    raster_dst.SetProjection(srs_info.ExportToWkt())
    # Blendrank value used as pixel value in rasterization. This value is
    # is really high which fits under 32bit.
    result = gdal.RasterizeLayer(raster_dst, [1], layer,
                                 burn_values=[_MAX_VALUE_32BIT],
                                 options=['ATTRIBUTE=%s' % attribute])

    src_band = raster_dst.GetRasterBand(1)
    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    dst_ds = shpdriver.CreateDataSource(output_flat_shp)
    dst_layer1 = dst_ds.CreateLayer('flat_file_intermediate',geom_type=layer.GetLayerDefn().GetGeomType(),srs=layer.GetSpatialRef())
    fd = ogr.FieldDefn(attribute, ogr.OFTInteger)
    fd.SetWidth(15)
    dst_layer1.CreateField(fd)

    gdal.Polygonize(src_band, src_band.GetMaskBand(), dst_layer1, 0,['8CONNECTED=8'])


def GetFlatFileWithAllAttribute(raw_shp, flat_intmd_shp,out_name,shp_data_dict=None,burn_attribute='asset_id'):
	"""Adds attribute to flat file.

	Args:
		raw_shp: Shapefile to read attributes.
		flat_intmd_shp: Path Intermediate shapefile.
		shp_data_dict: A dictionary mapping blendrank to attributes.
			If 'None' read attribute from raw shapefile.
		burn_attribute: Attribute field to be used for rasterize value.
	"""
	dst_raw = ogr.Open(raw_shp)
	dst_layer_raw = dst_raw.GetLayer()

	shpdriver = ogr.GetDriverByName('ESRI Shapefile')

	dst_intmd_flat = ogr.Open(flat_intmd_shp)
	dst_layer_intmd = dst_intmd_flat.GetLayer()

	dst_final_flat = shpdriver.CreateDataSource(out_name)
	dst_layer_flat = dst_final_flat.CreateLayer('flat_file_shp',geom_type=dst_layer_intmd.GetLayerDefn().GetGeomType(),srs=dst_layer_intmd.GetSpatialRef())
	attribute_list = []
	for i in range(dst_layer_raw.GetLayerDefn().GetFieldCount()):
		dst_layer_flat.CreateField(dst_layer_raw.GetLayerDefn().GetFieldDefn(i))
		attribute_list.append(dst_layer_raw.GetLayerDefn().GetFieldDefn(i).GetName())

	attribute_dict = {}
	if shp_data_dict is None:
		for feature in dst_layer_raw:
			asset_id = feature.GetField(burn_attribute)
			value_dict = {}
			for attribute in attribute_list:
				value_dict[attribute] = feature.GetField(attribute)
				attribute_dict[asset_id] = value_dict
		shp_data_dict = attribute_dict
	# print shp_data_dict

	flat_feature = ogr.Feature(dst_layer_flat.GetLayerDefn())
	for feature in dst_layer_intmd:
		geom = feature.GetGeometryRef()
		# Rasterization process could create self intersecting polygons.
		# Self intersecting polygons boundary crosses itself and creates
		# problem in further processing. To fix these self intersecting
		# polygons, call CloseRings on the polygon geometry object.
		geom.CloseRings()
		flat_feature.SetGeometry(geom)
		asset_id = feature.GetField(burn_attribute)
		for attribute in attribute_list:
			try:
				if attribute == 'area':
					poly_wkb = geom.ExportToWkb()
					poly_area = CalculateArea(poly_wkb)
					flat_feature.SetField(attribute,poly_area)
				else:
					flat_feature.SetField(attribute,shp_data_dict[asset_id][attribute])
			except Exception:
				sys.exc_clear()
		dst_layer_flat.CreateFeature(flat_feature)
