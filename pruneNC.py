
#from ncdfView import ncdfView
try:	from netCDF4 import Dataset, default_fillvals
except: from netCDF4 import Dataset, _default_fillvals
from datetime import date
from getpass import getuser
from os.path import exists
from numpy.ma import array as marray
"""
	this file takes a netcdf in, a netcdf out and a list of variables to save.
	it automatically saves the dimensions, and the header.

	This class takes an input netcdf filename, an output netcdf filename and a list of variables to keep. Usually ['var', 'lat','lon',time','depth'].
	It creates a new netcdf that contains only the variables that you gave it. 
"""


class pruneNC:
  def __init__(self, filenameIn, filenameOut, variables, depthInt = False, timemean=False, debug=False):
	self.fni=filenameIn
	self.fno=filenameOut
	self.vars=variables
	self.depthInt=depthInt
	self.timemean=timemean		#take mean of entire time series. Ideal for turning a daily file into a monthly file.
	self.debug=debug
	self.run()

  def run(self):	
	if not self.vars:
		print 'pruneNC:\tERROR:\tvariables to save are no use:', self.vars
		return
	if not exists(self.fni):
		print 'pruneNC:\tERROR:\tinputfile name does not exists:', self.fni
		return
				
	nci = Dataset(self.fni,'r')#Quiet =True)
	
	if self.depthInt: 
		print 'FAIL: maybe you should look at the depthManip.py class instead. This one only removes variables from a netcdf.'
		return
		
	
	#check that there are some overlap between input vars and nci:
	for v in self.vars:
		if v in nci.variables.keys():continue
		print 'pruneNC:\tERROR:\tvariable,' ,v,', not found in ',self.fni
		return
		
	#create dataset and header.
	if self.debug: print 'pruneNC:\tINFO:\tCreating a new dataset:\t', self.fno
	nco = Dataset(self.fno,'w')
	for a in nci.ncattrs():
		if self.debug: print 'pruneNC:\tINFO:\tcopying attribute: \t\"'+a+'\":\t', nci.getncattr(a)
		nco.setncattr(a,nci.getncattr(a))	
	appendToDesc= 'Reprocessed on '+todaystr()+' by '+getuser()+' using pruneNC.py'
	try: nco.Notes = nci.Notes + '\n\t\t'+appendToDesc
	except: nco.Notes = appendToDesc
	
	# list of variables to save, assuming some conventions
	alwaysInclude = ['time', 'lat','lon', 'latbnd', 'lonbnd']
	save =   list(set(nci.variables.keys()).intersection(set(alwaysInclude) ) ) 
	save = list(set(sorted(save + self.vars)))
	
	# create dimensions:
	for d in nci.dimensions.keys():
	  if d in ['time',]: nco.createDimension(d, None)
	  else:		     nco.createDimension(d, len(nci.dimensions[d]))

	# create Variables:
	for var in save:  nco.createVariable(var, nci.variables[var].dtype, nci.variables[var].dimensions,zlib=True,complevel=5)

	# Long Names:
	for var in save: 
		try:  	long_name=nci.variables[var].long_name
		except:	
		  print 'pruneNC:\tWarning:\tNo long_name for ', var
		  long_name = var
		  
		if self.timemean: long_name.replace('Daily', 'Monthly')	
		nco.variables[var].long_name=long_name
		if self.debug: print 'pruneNC:\t Adding long_name for ', var, long_name
		  
	# Units:
	for var in save: 
		try:  	nco.variables[var].units=nci.variables[var].units
		except: print 'pruneNC:\tWarning:\tNo units for ', var	
		
	# Fill Values:
	for var in save:
		if self.debug: print 'pruneNC:\tINFO:\tCopying ', var, ' ...' 
		arr = nci.variables[var][:]
		
		if self.timemean and len(intersection(['time','t'], nci.variables[var].dimensions)):
			if self.debug: print 'pruneNC:\tInfo:\tSaving time averaged var:',var
			arr = marray([arr.mean(0),])
			while len(arr.shape) < len(nci.variables[var].dimensions): arr = marray(arr[None,:])
			
		if self.debug: print 'pruneNC:\tInfo:\tSaving var:',var, arr.shape, '\tdims:', nci.variables[var].dimensions
		nco.variables[var][:] =arr

	# Close netcdfs:
	nco.close()
	nci.close()
	if self.debug: print 'pruneNC:\tINFO:\tsuccessfully created:\t', self.fno
	return

	
def todaystr():
	# returns string: DD/MM/YYYY on todays date
	return str(date.today().day)+'/'+str(date.today().month)+'/'+str(date.today().year)
	
def intersection(list1,list2):
	"""return the overlap between two lists"""
	return list(set(list1).intersection(set(list2) ) )
