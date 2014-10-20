
try:	from netCDF4 import Dataset, default_fillvals
except: from netCDF4 import Dataset, _default_fillvals
from datetime import date
from getpass import getuser
from os.path import exists
from numpy import array, int64
from numpy.ma import array as marray, nonzero,masked_where,compressed,zeros
from pruneNC import todaystr
from operator import itemgetter
"""	This routine takes a netcdf input and creates a new one with only 1 dimension. """

# list of variables to save, assuming some conventions
alwaysInclude = ['time', 'lat','lon', 'latbnd', 'lonbnd','LONGITUDE','LATITUDE','DEPTH','TIME','nav_lat','nav_lon','nav_lev','time_counter','deptht','depth', 'latitude', 'longitude','month','mask'] 
		#'crs',]'lat_bnds','lon_bnds',


def getCoordsToKeep(nc,variables,newMask='',debug = False): 
	"""This routine takes an ncdfView object, a list of varialbes, and tests which coordinates should be saved.
	   A Mask can be applied too.
	"""
	CoordsToKeep={}
	for var in variables:
		if var in alwaysInclude: continue
		arr = nc.variables[var][:]
		if len(newMask):
			out = []
			if newMask.shape != arr.shape:
				if debug:'getCoordsToKeep:\t',var,'Wrong shape'
				continue
			try: # 1D arrays
			  for i,m in enumerate(newMask):
				if not m: continue
				out.append(arr[i])	
			  arr= array(out).squeeze()
			except:
				# multi dimensional arrays
			  arr = masked_where(newMask,array(arr))	
		#nearlyZero = 1.E-6
		nz = nonzero(arr)#+nearlyZero
		#nz = compressed(arr)
		#if debug:print "getCoordsToKeep:\tcompressed array:",len(nz),nz.shape,nz.min(),nz.max(),nz.mean()
		if not len(nz):
			variables.remove(var)
			continue
		nzdims = len(nz)
		for i,a in enumerate(nz[0]):
			if var in ['OBSERVATIONS']:
				coords = tuple([nz[j][i] for j in xrange(nzdims)])
				#if coords not in CoordsToKeep.keys():	
				#	print "NEWS OBSERVATION LOCATION:",i,coords
				try: 
				  if i in CoordsToKeep[coords]:pass
				except:
				  try:	CoordsToKeep[coords].append(i)
				  except: CoordsToKeep[coords] = [i,]
			else:
				coords = tuple([nz[j][i] for j in xrange(nzdims)])
				try: 
				  if i in CoordsToKeep[coords]:pass
				except:
				  try:	CoordsToKeep[coords].append(i)
				  except: CoordsToKeep[coords] = [i,]
		if debug: print "getCoordsToKeep:\t",var,"\tndims:", nzdims, len(nz[0]),"\tNumber of Coords:", len(CoordsToKeep.keys())
	return CoordsToKeep,variables
			
class convertToOneDNC:
  def __init__(self, filenameIn, filenameOut, newMask='', variables=[], debug=False,dictToKeep=''):
	self.fni=filenameIn
	self.fno=filenameOut
	self.vars=variables
	self.newMask=newMask
	self.debug=debug
	self.dictToKeep = dictToKeep
	self.run()
	

  def run(self):
	if not exists(self.fni):
		print 'convertToOneDNC:\tERROR:\tinputfile name does not exists:', self.fni
		assert False
		return
		  
	nci = Dataset(self.fni,'r')
	
	if not self.vars:
		self.vars = nci.variables.keys() # save all


	#check that there are some overlap between input vars and nci:
	for v in self.vars:
		if v in nci.variables.keys():continue
		print 'convertToOneDNC:\tERROR:\tvariable,' ,v,', not found in ',self.fni
		return
		
	#create dataset and header.
	if self.debug: print 'convertToOneDNC:\tINFO:\tCreating a new dataset:\t', self.fno
	nco = Dataset(self.fno,'w')
	for a in nci.ncattrs():
		if self.debug: print 'convertToOneDNC:\tINFO:\tcopying attribute: \t\"'+a+'\":\t', nci.getncattr(a)
		nco.setncattr(a,nci.getncattr(a))
	
	appendToDesc= 'Reprocessed on '+todaystr()+' by '+getuser()+' using convertToOneDNC.py'
	try: nco.Notes = nci.Notes + '\n\t\t'+appendToDesc
	except: nco.Notes = appendToDesc
	


	save =   list(set(nci.variables.keys()).intersection(set(alwaysInclude) ) ) 
	save = sorted(list(set(sorted(save + self.vars))))
	

	# test to find out which coordinates should be saved.	
	if not self.dictToKeep:
		CoordsToKeep,save=getCoordsToKeep(nci,save,newMask=self.newMask,debug = self.debug)
	else:
		CoordsToKeep = self.dictToKeep

	print "convertToOneDNC:\tinfo:\tCoordsToKeep:", save#, self.dictToKeep
	
		
	# create dimensions:
	#for d in nci.dimensions.keys():
	#  if d in ['time',]: nco.createDimension(d, None)
	#  else:		     nco.createDimension(d, len(nci.dimensions[d]))
	nco.createDimension('index', None)

	# create Variables:

	nco.createVariable('index',   int64, ['index',],zlib=True,complevel=5)#,chunksizes=10000)	
	nco.createVariable('index_t', int64, ['index',],zlib=True,complevel=5)#,chunksizes=10000)		
	nco.createVariable('index_z', int64, ['index',],zlib=True,complevel=5)#,chunksizes=10000)		
	nco.createVariable('index_y', int64, ['index',],zlib=True,complevel=5)#,chunksizes=10000)		
	nco.createVariable('index_x', int64, ['index',],zlib=True,complevel=5)#,chunksizes=10000)
	for var in save:
		nco.createVariable(var, nci.variables[var].dtype, ['index',],zlib=True,complevel=5)#,chunksizes=10000)
	
	# Long Names:
	nco.variables['index'].long_name='index'
	nco.variables['index_t'].long_name='index - time'	
	nco.variables['index_z'].long_name='index - depth'
	nco.variables['index_y'].long_name='index - latitude'
	nco.variables['index_x'].long_name='index - longitude'
			
	for var in save: 
		try:  	long_name=nci.variables[var].long_name
		except:	
		  if self.debug: print 'convertToOneDNC:\tWarning:\tNo long_name for ', var
		  long_name = var
		  
		nco.variables[var].long_name=long_name
		if self.debug: print 'convertToOneDNC:\t Adding long_name for ', var, long_name
		  
	# Units:
	nco.variables['index'].units=''
	nco.variables['index_t'].units=''
	nco.variables['index_z'].units=''
	nco.variables['index_y'].units=''
	nco.variables['index_x'].units=''
					
	for var in save: 
		try:  	nco.variables[var].units=nci.variables[var].units
		except: print 'convertToOneDNC:\tWarning:\tNo units for ', var	
		
	# Fill Values:
	def itemsgetter(a):
    		return a[1][0]

	sorted_Coords = sorted(CoordsToKeep.iteritems(), key=itemsgetter)
	print "convertToOneDNC:\tINFO:\tsorted_Coords:",sorted_Coords[0],sorted_Coords[-1]
	data={}
	if self.debug: print 'convertToOneDNC:\tINFO:\tCopying index  ...' , len(sorted_Coords)	
#	nco.variables['index'][:] = [ int(a[1]) for a in sorted_Coords]	

	nco.variables['index'][:] = array([ a[1][0] for a in sorted_Coords])
	nco.sync()
	
	# 4D coordinates:
	if len(sorted_Coords[0][0]) ==4:
		print "4D:", sorted_Coords[0][0]
		if self.debug: print 'convertToOneDNC:\tINFO:\tCopying index t ...' 	
		nco.variables['index_t'][:] = array([a[0][0] for a in sorted_Coords])
		nco.sync()
		if self.debug: print 'convertToOneDNC:\tINFO:\tCopying index z ...' 			
		nco.variables['index_z'][:] = array([a[0][1] for a in sorted_Coords])
		nco.sync()		
		if self.debug: print 'convertToOneDNC:\tINFO:\tCopying index y ...' 	
		nco.variables['index_y'][:] = array([a[0][2] for a in sorted_Coords])
		nco.sync()		
		if self.debug: print 'convertToOneDNC:\tINFO:\tCopying index x ...' 	
		nco.variables['index_x'][:] = array([a[0][3] for a in sorted_Coords])
		nco.sync()	
		
	if len(sorted_Coords[0][0]) ==3:
		print "3D:", sorted_Coords[0][0]	
		if self.debug: print 'convertToOneDNC:\tINFO:\tCopying index t ...' 	
		nco.variables['index_t'][:] = array([a[0][0] for a in sorted_Coords])
		nco.sync()
		#if self.debug: print 'convertToOneDNC:\tINFO:\tCopying index z ...' 			
		nco.variables['index_z'][:] = zeros(len(sorted_Coords))
		#nco.sync()		
		if self.debug: print 'convertToOneDNC:\tINFO:\tCopying index y ...' 	
		nco.variables['index_y'][:] = array([a[0][1] for a in sorted_Coords])
		nco.sync()		
		if self.debug: print 'convertToOneDNC:\tINFO:\tCopying index x ...'
		#tempArr = []
		#for a in sorted_Coords:
		#	print a[0]
		#	tempArr.append(a[0][2])
			
		nco.variables['index_x'][:] = array([a[0][2] for a in sorted_Coords])
		nco.sync()		
	
	for var in save:
		if self.debug: print 'convertToOneDNC:\tINFO:\tCopying ', var, ' ...' 
		arr = nci.variables[var][:]
		outarr = []
		if arr.ndim ==1 and len(sorted_Coords[0][0]) ==4:
			if var.lower() in ['time','time_counter','t','month']:	d = 0
			if var.lower() in ['depth','deptht',]:		d = 1
			if var.lower() in ['latbnd','lat','latitude']:	d = 2			
			if var.lower() in ['lonbnd','lon','longitude']: d = 3
			#for c in (CoordsToKeep.keys()):	
			for c in sorted_Coords:
				outarr.append(arr[c[0][d]])
			try: print var, d
			except: var, "not found"
		elif arr.ndim ==1 and len(sorted_Coords[0][0]) ==3:
			if var.lower() in ['time','time_counter','t','month']:	d = 0
			#if var.lower() in ['depth','deptht',]:		d = 1
			if var.lower() in ['latbnd','lat','latitude']:	d = 1			
			if var.lower() in ['lonbnd','lon','longitude']: d = 2
			#for c in (CoordsToKeep.keys()):	
			for c in sorted_Coords:
				outarr.append(arr[c[0][d]])
			try: print var, d
			except: var, "not found"
		elif arr.ndim ==2:
			if var.lower() in ['nav_lat','nav_lon']:			d = (2,3)
			if var.lower() in ['deptht','latitude','longitude']:		d = (0,1)
			if var.lower() in ['mask'] and len(sorted_Coords[0][0]) ==3: 	d = (1,2) # because of MLD datasets.
			print var, 'convertToOneDNC:\tINFO:\tndim: 2',var, d
			
			for c in sorted_Coords:			#for c in sorted(CoordsToKeep.keys()):	
				outarr.append(arr[(c[0][d[0]],c[0][d[1]])])	
		elif arr.ndim ==3:
			#if var.lower() in ['fAirSeaC',]:
			#d = (0,2,3)
			#print var, 'lendth : 3'
			for c in sorted_Coords:
				if len(c[0]) == 4: outarr.append(arr[(c[0][0],c[0][2],c[0][3])])
				if len(c[0]) == 3: outarr.append(arr[(c[0][0],c[0][1],c[0][2])])
		elif arr.ndim ==4:
		    #for c in sorted(CoordsToKeep.keys()):
		    	for c in sorted_Coords:
		    		#print c, c[0], arr.shape
		    		#print arr[c[0]]
				outarr.append(arr[ (c[0][0],c[0][1],c[0][2],c[0][3]) ])
		else:
			print "How many dimensions?", arr.ndim
			assert False
		outarr= marray(outarr)
		if self.debug: print 'convertToOneDNC:\tINFO:\tSaving var:',var, arr.shape, '->', outarr.shape , 'coords:',len(sorted_Coords)
		nco.variables[var][:] =outarr
		nco.sync()	
	# Close netcdfs:
	nco.close()
	nci.close()
	if self.debug: print 'convertToOneDNC:\tINFO:\tsuccessfully created:\t', self.fno
	return				


