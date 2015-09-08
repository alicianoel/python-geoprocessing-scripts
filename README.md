# python-geoprocessing-scripts

- calc_feature_area.py<br>
  calculates the area in sqkm for a specified input shapefile.

- sort_features.py<br>
  function to sort shapefile features by a specified attribute. Useful before running 'flatten-shp-geometries.py'.

- flatten-shp-geometries.py<br>
  functions for flattening a shapefile to eliminate overlapping polygons. input shapefile features should be already   sorted in the order of which they will be flattened. this is achieved by rasterizing the vectors (using a unique     id, in this case, 'asset_id') while storing the attribute table in a dictionary, then re-vectorizing the raster and   re-joining the attributes. It is much faster than having to break all the polygons, and with a high resolution the   accuracy is negligable.

- spatial_filter.py<br>
  selects features from 'input_shp' that intersect 'aoi', and places them in 'output_shp'.
