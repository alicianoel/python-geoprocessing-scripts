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

def sortlayer(l, fd):
	"""Sorts feature stack order in a shapefile. Sorts in ascending order so that greatest values are at
	the bottom of the attribute list and therefore at the top of the stack order.

	Args:
		l: Shapefile to read attributes.
		fd: field to sort by
	"""

	inDataSource = inDriver.Open(l, 1)
	inlayer = inDataSource.GetLayer()
	fids = []
	vals = []

	for f in inlayer:
		fid = f.GetFID()
		fids.append(fid)
		vals.append((f.GetField(fd), fid))
	vals.sort()
	# index as dict: {newfid: oldfid, ...}
	ix = {fids[i]: vals[i][1] for i in xrange(len(fids))}

	# swap features around in groups/rings
	for fidstart in ix.keys():
		if fidstart not in ix: continue
		ftmp = inlayer.GetFeature(fidstart)
		fiddst = fidstart
		while True:
			fidsrc = ix.pop(fiddst)
			if fidsrc == fidstart: break
			f = inlayer.GetFeature(fidsrc)
			f.SetFID(fiddst)
			inlayer.SetFeature(f)
			fiddst = fidsrc
		ftmp.SetFID(fiddst)
		inlayer.SetFeature(ftmp)

l = "input_file.shp" #change "input_file.shp" to the name of your shapefile
fd = "acq_date" #field to filter by
sortlayer(l, fd)
