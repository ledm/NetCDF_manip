
try:	from netCDF4 import Dataset, default_fillvals
except: from netCDF4 import Dataset, _default_fillvals
from datetime import date
from getpass import getuser
from os.path import exists
from numpy import array, int64
from numpy.ma import array as marray, nonzero,masked_where,compressed
from pruneNC import todaystr
"""	This routine takes a netcdf input and creates a new one with only 1 dimension. """

# list of variables to save, assuming some conventions
alwaysInclude = ['time', 'lat','lon', 'latbnd', 'lonbnd','LONGITUDE','LATITUDE','DEPTH','TIME','nav_lat','nav_lon','time_counter','deptht']


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
				if coords not in CoordsToKeep.keys():	
					print "NEWS OBSERVATION LOCATION:",i,coords
				CoordsToKeep[coords] = True							
			else:
				coords = tuple([nz[j][i] for j in xrange(nzdims)])
				CoordsToKeep[coords] = True
		if debug: print "getCoordsToKeep:\t",var,"\tndims:", nzdims, len(nz[0]),"\tNumber of Coords:", len(CoordsToKeep.keys())
	return CoordsToKeep,variables
			
class convertToOneDNC:
  def __init__(self, filenameIn, filenameOut, newMask='', variables=[], debug=False):
	self.fni=filenameIn
	self.fno=filenameOut
	self.vars=variables
	self.newMask=newMask
	self.debug=debug
	self.run()
	

  def run(self):
	if not exists(self.fni):
		print 'convertToOneDNC:\tERROR:\tinputfile name does not exists:', self.fni
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
	save = list(set(sorted(save + self.vars)))
	

	# test to find out which coordinates should be saved.	
	CoordsToKeep,save=getCoordsToKeep(nci,save,newMask=self.newMask,debug = self.debug)


	
		
	# create dimensions:
	#for d in nci.dimensions.keys():
	#  if d in ['time',]: nco.createDimension(d, None)
	#  else:		     nco.createDimension(d, len(nci.dimensions[d]))
	nco.createDimension('index', None)

	# create Variables:

	nco.createVariable('index', int64, ['index',],zlib=True,complevel=5)	
	for var in save:
		nco.createVariable(var, nci.variables[var].dtype, ['index',],zlib=True,complevel=5)
	
	# Long Names:
	nco.variables['index'].long_name='index'
	for var in save: 
		try:  	long_name=nci.variables[var].long_name
		except:	
		  if self.debug: print 'convertToOneDNC:\tWarning:\tNo long_name for ', var
		  long_name = var
		  
		nco.variables[var].long_name=long_name
		if self.debug: print 'convertToOneDNC:\t Adding long_name for ', var, long_name
		  
	# Units:
	nco.variables['index'].units=''
	for var in save: 
		try:  	nco.variables[var].units=nci.variables[var].units
		except: print 'convertToOneDNC:\tWarning:\tNo units for ', var	
		
	# Fill Values:
	data={}
	nco.variables['index'][:] = array([a for a,i in enumerate(CoordsToKeep.keys())])
	for var in save:
		if self.debug: print 'convertToOneDNC:\tINFO:\tCopying ', var, ' ...' 
		arr = nci.variables[var][:]
		outarr = []
		if arr.ndim ==1:
			if var.lower() in ['time','time_counter','t']:	d = 0
			if var.lower() in ['depth','deptht',]:		d = 1
			if var.lower() in ['latbnd','lat','latitude']:	d = 2			
			if var.lower() in ['lonbnd','lonbnd','longitude']:d = 3
			for c in sorted(CoordsToKeep.keys()):	
				outarr.append(arr[c[d]])
		elif arr.ndim ==2:
			if var.lower() in ['nav_lat','nav_lon']:	d = (2,3)
			for c in sorted(CoordsToKeep.keys()):	
				outarr.append(arr[(c[2:])])				
		else:
		    for c in sorted(CoordsToKeep.keys()):
			outarr.append(arr[c])
		outarr= marray(outarr)
		if self.debug: print 'convertToOneDNC:\tINFO:\tSaving var:',var, arr.shape, '->', outarr.shape , 'coords:',len(CoordsToKeep.keys())
		nco.variables[var][:] =outarr

	# Close netcdfs:
	nco.close()
	nci.close()
	if self.debug: print 'convertToOneDNC:\tINFO:\tsuccessfully created:\t', self.fno
	return				


