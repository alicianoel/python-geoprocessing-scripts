def CalculateArea(geom):
	"""Calculate are in Sqkm for given input geom.

	To calcualte area of polygon which has WGS84 and lat long
	spatail reference by reprojecting in Cylindrical Equal-Area (EPSG:3410)
	projection. Then reverts back to WGS84.

	Args:
	geom: Polygon geometry.

	Returns:
	area: Area of polygon in SQKM.
	"""

	src_sr = osr.SpatialReference()
	src_sr.ImportFromEPSG(_SRS_EPSG)
	dest_sr = osr.SpatialReference()
	dest_sr.ImportFromProj4(_CYLINDRICAL_EQUAL_AREA_PROJ4_DEF)
	sr_trans = osr.CoordinateTransformation(src_sr, dest_sr)
	trs_back = osr.CoordinateTransformation(dest_sr, src_sr)


	geom.Transform(sr_trans)
	area = geom.Area() / (1000 * 1000)  # SQKM

	geom.Transform(trs_back)

	return area



def AddArea(input_shp):
	"""Adds calculated area field and values in Sqkm for given input geom from CalculateArea.

	Returns:
	area: Area of polygon in SQKM.
	"""

	source = ogr.Open(input_shp, 1)
	layer = source.GetLayer()
	layer_defn = layer.GetLayerDefn()

	layer_defn = layer.GetLayerDefn()
	field_names = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]
	if 'area_sqkm' not in field_names:
		# print 'creating area_sqkm field'
		# Add a new field
		area_field = ogr.FieldDefn('area_sqkm', ogr.OFTReal)
		layer.CreateField(area_field)
		
input_shp = "input_file.shp" #change "input_file.shp" to your file name.
AddArea(input_shp)
