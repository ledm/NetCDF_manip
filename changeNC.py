# this file takes a netcdf filename in, a netcdf filename out and an AutoVivification dictionary for changes.
# it copies the netcdf, but makes the changes to metadata requrested in a dictionairy.
#
# For a given variable, units, long_name and variable name can be changed here.
# a lambda function can be assigned to a variable for simple conversions.
#
#	To add or change a netcdf attribute:
#	av = AutoVivification()
#	av['att']['Description'] = 'New description'
#
#	to remove an attribute:
#	av['att']['Description'] = ''
#
#	to change a dimension name:
#	av['dim']['oldDimensionName']= 'newDimensionName'
#
#	to change a variable, i.e. change old var,'t', to new var:'time'.
#	av['t']['name']='time'
#	av['t']['units']='day'
#	
#	to remove a variable from the file, set it's name to "False", "Remove", or "Delete"
#	av['t']['name']='False'
#
#	The values in the array can be changed with a lambda function: 
#	av['t']['convert']=lambda t:t/2. # divide time by two.
#
#
# As always, the debug flag just prints more when set to True
# THIS CLASS DOES NOT CHANGE VARIABLE LENGTH, OR DIMENSION SIZE.

#from ncdfView import ncdfView
try:from netCDF4 import Dataset, default_fillvals
except:from netCDF4 import Dataset, _default_fillvals

from datetime import date
from getpass import getuser
from os.path import exists



class changeNC:
  def __init__(self, filenameIn, filenameOut, av, debug=True,datasetFormat='NETCDF4'):
	self.fni=filenameIn
	self.fno=filenameOut
	self.av=av		
	self.debug=debug
	self.datasetFormat = datasetFormat
	self.run()

  def run(self):
  	# starting checks:
	if not self.av:
		print 'changeNC:\tERROR:\tchanges to make are no use:', self.av
		return
	if not exists(self.fni):
		print 'changeNC:\tERROR:\tinputfile name does not exists:', self.fni
		return
		
	if self.debug: print 'changeNC:\tINFO:\tOpening dataset:\t', self.fni
	nci = Dataset(self.fni,'r')#Quiet =True)
		
	# create dataset and netcdf attributes.
	if self.debug: print 'changeNC:\tINFO:\tCreating a new dataset:\t', self.fno
	nco = Dataset(self.fno,'w',format=self.datasetFormat)
	attributes =  nci.ncattrs()
	attributes.extend(list(self.av['att']))
	for att in list(set(attributes)):
		attribute = ''
		if att in self.av['att']: attribute = self.av['att'][att]
		else: attribute= nci.getncattr(att)
		if self.debug: print 'changeNC:\tINFO:\tadding attribute: \t\"',att,'\":\t', attribute	
		nco.setncattr(att,attribute)
		

	# create dimensions:
	dimensions = nci.dimensions.keys()
	for dim in dimensions:
	  newDim = dim
	  dimSize=len(nci.dimensions[dim])
	  if nci.dimensions[dim].isunlimited(): dimSize = None	  
	  if self.av['dim'][dim]['name']: newDim=self.av['dim'][dim]['name']
	  if self.av['dim'][dim]['newSize']: dimSize = self.av['dim'][dim]['newSize']	  
	  nco.createDimension(newDim, dimSize)
	  if self.debug: print 'changeNC:\tINFO:\tadding dimension: ',dim,'-->', newDim, '\t(',dimSize,')'


	# list of variables to save
	keys = nci.variables.keys()
	
	# create Variables:
	for var in keys:
		newname = var
		if self.av[var]['name']:newname = self.av[var]['name']
		if newname.lower() in ['false', 'none','remove', 'delete', 0]:
			if self.debug: print 'changeNC:\tINFO:\tremoving variable: ',var
			continue
		dimensions = list(nci.variables[var].dimensions)
		# for d,dim in enumerate(dimensions):
		#	#if self.av['dim'][dim]: dimensions[d] = self.av['dim'][dim]
		if self.av[var]['newDims']: dimensions = self.av[var]['newDims']
      		nco.createVariable(newname, nci.variables[var].dtype, tuple(dimensions),zlib=True,complevel=5)
	  	if self.debug: print 'changeNC:\tINFO:\tadding variable: ',var,'-->', newname, '\t(',dimensions,')'
	  
	# Long Names:
	for var in keys: 
		long_name = ''
		newname = var	
		if self.av[var]['name']:newname = self.av[var]['name']		
		if newname.lower() in ['false', 'none','remove', 'delete', 0]:continue		
		if self.av[var]['long_name']: long_name= self.av[var]['long_name']
		else: 
		  try:  	long_name=nci.variables[var].long_name
		  except:	print 'changeNC:\tWarning:\tNo long_name for ', var
		if long_name: nco.variables[newname].long_name=long_name
		if self.debug: print 'changeNC:\tINFO:\tadding long_name: ',var,'-->', newname, '\t(',long_name,')'
	# Units:
	for var in keys: 
		units = ''
		newname = var
		if self.av[var]['name']:newname = self.av[var]['name']
		if newname.lower() in ['false', 'none','remove', 'delete', 0]:continue		
		if self.av[var]['units']: units= self.av[var]['units']
		else: 
		  try:  	units=nci.variables[var].units
		  except:	print 'changeNC:\tWarning:\tNo units for ', var
		if units: nco.variables[newname].units=units
		if self.debug: print 'changeNC:\tINFO:\tadding units: ',var,'-->', newname, '\t(',units,')'
						
	# Fill Values:
	for var in keys:
		newname = var
		func = lambda  x: x
		if self.av[var]['name']:newname = self.av[var]['name'] 
		if newname.lower() in ['false', 'none','remove', 'delete', 0]:continue		
		if self.av[var]['convert']:func = self.av[var]['convert'] 		
		if self.debug: print 'changeNC:\tINFO:\tCopying ', var, ' ...' ,newname, nci.variables[var][:].shape,
		nco.variables[newname][:] =func(nci.variables[var][:])
		if self.debug: print '->', nco.variables[newname][:].shape
	# Close netcdfs:
	nco.close()
	nci.close()
	print 'changeNC:\tINFO:\tsuccessfully created:\t', self.fno
	return

	

def todaystr():
	# returns string: DD/MM/YYYY on todays date
	return str(date.today().day)+'/'+str(date.today().month)+'/'+str(date.today().year)


class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try: return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value
# class to auto add objects to dictionaries
# ie:
# a = AutoVivification()
# a['a']['b']='ab'
# a['a']['c']='ac'
# print a['a'],a['a']['b'],a['a']['c']      
