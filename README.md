NetCDF_manip
============

A repository to assist with manipulating netcdf files. Merging, pruning, renaming varaibles, creating 1D profiles from 3D files.

They take fairly simple commands to run, but should be fairly powerful.

changeNC.py: creates a new netcdf file, but simple changes can be made. Ie rename a variable, change the units, add attributes, multiply by 1000, etc.

mergeNC.py: takes a list of netcdf files and merges them into one, provided they use the same grid, and contain the same variables.

pruneNC.py: Copies variables from a netcdf file. Mostly to reduce the total size of the file.

depthProfileNC.py: Creates a 1D profile netcdf at a specified location. Does not yet work for lat long coords, only grid index.

depthManipNC.py: This one is a bit crazy and does some unusual things with depth integration. Unfortunately, this one is the least stable, but it is the one I used to make surface/depth integration data for Jose.

