# this file takes a list of netcdfs in, a netcdf out and a list of variables to save.


# This class takes a list of input netcdf filenames, an output netcdf filename and a list of variables.
# it automatically saves the dimensions, and the header.
# It creates a new netcdf that contains the variables that you gave it from all the files in the input file list in chronological.
# In combination with pruneNC.py, this scrip can take the 12hourly file,

#from ncdfView import ncdfView
from netCDF4 import Dataset,num2date,date2num
try:	from netCDF4 import default_fillvals
except: from netCDF4 import _default_fillvals as default_fillvals
from datetime import date
from getpass import getuser
from os.path import exists
from numpy.ma import array,masked_all
from numpy import  append,mean
from glob import glob 

class mergeNC:
  def __init__(self, filesIn, filenameOut, variables, timeAverage=False,debug=False,calendar='standard',fullCheck=False):
	self.fnsi=filesIn
	self.fno=filenameOut
	self.vars=variables
	self.cal = calendar
	self.timeAverage = timeAverage
	self.fullCheck = fullCheck
	self.debug = debug
	self.run()

  def run(self):
	if type(self.fnsi) == type('abc'):
		self.fnsi = glob(self.fnsi)
		  
	if not exists(self.fnsi[0]):
		print 'mergeNC:\tERROR:\tinputfile name does not exists:', self.fnsi[0]
		return
	if self.debug: print 'mergeNC:\tINFO:\topening dataset:\t', self.fnsi[0]	
	nci = Dataset(self.fnsi[0],'r')#Quiet =True)
	
	if self.timeAverage:
		print 'mergeNC:\tWARNING:\ttimeAverage is not yet debugged. '# are no use:', self.vars
		#return		
	if not self.vars:
		if self.debug: print 'mergeNC:\tINFO:\tvariables to save are empty, saving all.'
		self.vars = nci.variables.keys()

	if self.vars == 'all':
		if self.debug: print 'mergeNC:\tINFO:\tvariables to save:  \'all\' requested. '
		self.vars = nci.variables.keys()
				
	if self.cal != 'standard':
		if self.debug: print 'mergeNC:\tINFO:\tUsing non-standard calendar:', self.cal
				
	
	#check that there are some overlap between input vars and nci:
	for v in self.vars:
		if v in nci.variables.keys():continue
		print 'mergeNC:\tERROR:\tvariable,' ,v,', not found in ',self.fnsi[0]
		return
		
	#create dataset and header.
	if self.debug: print 'mergeNC:\tINFO:\tCreating a new dataset:\t', self.fno
	nco = Dataset(self.fno,'w')
	for a in nci.ncattrs():
		if self.debug: print 'mergeNC:\tINFO:\tcopying attribute: \t\"'+a+'\":\t', nci.getncattr(a)
		nco.setncattr(a,nci.getncattr(a))	
	appendToDesc= 'Reprocessed on '+todaystr()+' by '+getuser()+' using mergeNC.py'
	try: nco.Notes = nci.Notes + '\n\t\t'+appendToDesc
	except: nco.Notes = appendToDesc
	
	# list of variables to save, assuming some conventions
	alwaysInclude = ['time', 'lat','lon', 'latbnd', 'lonbnd', 'latitude', 'longitude', 't','nav_lat','nav_lon', 'time_counter', 'deptht',]
	alwaysInclude = intersection(nci.variables.keys(),alwaysInclude) 
	save = list(set(sorted(alwaysInclude + self.vars)))
	time = intersection(['time', 't','time_counter',], alwaysInclude)
	if len(time) ==1: tvar=time[0]
	else: tvar = 'time'
	
	missing = {}
	if self.fullCheck:
	    if self.debug: print 'mergeNC:\tINFO:\tPerforming full check for missing entries'
	    for t,fni in enumerate(self.fnsi):
		#if self.debug: print 'mergeNC:\tINFO:\tOpening ', fni, ' ...', t   
		nci = Dataset(fni,'r')
		keys =nci.variables.keys()
		for s in save:
			if s in alwaysInclude:continue
			if s not in keys:
				print 'mergeNC:\tWARNING:\tFull check: ',s,' is missing from ', fni
				try: missing[s].append(fni)
				except:missing[s] = [fni,]
	    	nci.close()

 	    for s in missing.keys():
	        #remove key: 	    
	    	#print 'mergeNC:\tWARNING:\tFull check:\tremoving',s,' from ',save
	    	#save.remove(s)
	        
	        #remove missing files:
	    	for fn in missing[s]: 
		    	print 'mergeNC:\tWARNING:\tFull check:\tremoving',fni,' from files'	    	
	    		try:self.fnsi.remove(fn)
	    		except: print 'mergeNC:\tWARNING:\tFull check:\t',fni,' already removed from files'


  
	
	# create dimensions:
	nci = Dataset(self.fnsi[0],'r')#Quiet =True)	
	for d in nci.dimensions.keys():
	  if nci.dimensions[d].isunlimited(): dimSize = None
	  else:	  dimSize=len(nci.dimensions[d])
	  nco.createDimension(d, dimSize)	
	  

	# create Variables:
	for var in save:  nco.createVariable(var, nci.variables[var].dtype, nci.variables[var].dimensions,zlib=True,complevel=5)

	# Long Names:
	for var in save: 
		try:  	nco.variables[var].long_name=nci.variables[var].long_name
		except:	
			if self.debug: print 'mergeNC:\tWarning:\tNo long_name for ', var
		  
	# Units:
	for var in save:
	    #if var in time and self.timeAverage: nco.variables[var].units='Month'
	    #else:
		try:  	nco.variables[var].units=nci.variables[var].units
		except: 
			if self.debug: print 'mergeNC:\tWarning:\tNo units for ', var	
	
	# Fill Values:
	for var in alwaysInclude:
		if var in time:continue
		if self.debug: print 'mergeNC:\tINFO:\tCopying ', var, ' ...', nci.variables[var][:].shape
		nco.variables[var][:] =nci.variables[var][:]
	nci.close()
	
	a={}
	a[tvar] = []
	for var in save:
		if var in alwaysInclude: continue
		a[var]=[]

	for t,fni in enumerate(self.fnsi):
		if self.debug: print 'mergeNC:\tINFO:\tOpening ', fni, ' ...', t   
		nci = Dataset(fni,'r')
		
		#times:
		tval = num2date(nci.variables[tvar][:],nci.variables[tvar].units,calendar=self.cal)		
		a[tvar].extend( date2num(tval,nco.variables[tvar].units,calendar=self.cal))
		
		if self.debug: print 'mergeNC:\tINFO:\tTIME:',t, tvar, array(a[tvar]).shape

		# not time:
		for var in a.keys():
		  if var in time:continue
		  if var in nci.variables.keys(): arr = nci.variables[var][:]
		  else:
	  	    if self.debug:print 'mergeNC:\tWARNING:', fni,' is missing variable:',var, nco.variables[var][0,:].shape

	  	    arr = masked_all(nco.variables[var][0,:].shape)
		  
		  if not len(a[var]): a[var]=arr
		  else:    a[var] = append(a[var], arr, axis=0) 		  
		  if self.debug: print 'mergeNC:\tINFO\tvar:', t, var, 'len:',len(a[var]), arr.shape,a[var].shape

		nci.close()
	
	if self.timeAverage: 
	    for var in a.keys():
		if self.debug: print "mergeNC:\tINFO\tTime Average:", var 
		if var == tvar:
			nco.variables[tvar][:] = [mean(a[var]),]	
		else:
			nco.variables[var][:] = array(a[var]).mean(0)[None,:] 
			
	else: # No time averaging.
	    for var in a.keys():
		if self.debug: print 'mergeNC:\tINFO:\tsaving ', var, ' ...',nco.variables[var][:].shape,array(a[var]).shape  #, a[var][0]
		nco.variables[var][:] = array(a[var])
		
	# Close output netcdfs:
	nco.close()
	if self.debug: print 'mergeNC:\tINFO:\tsuccessfully created:\t', self.fno
	return

	


def todaystr():
	# returns string: DD/MM/YYYY on todays date
	return str(date.today().day)+'/'+str(date.today().month)+'/'+str(date.today().year)

def intersection(list1,list2): return list(set(list1).intersection(set(list2) ) ) 


