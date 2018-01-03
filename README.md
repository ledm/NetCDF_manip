# NetCDF manipulation toolkit
============

A toolkit to assist with the manipulating netcdf files in python. 
They take fairly simple commands to run, but should be fairly powerful.
These tools can be used to 
* Merge several netcdf files along the time axis.
* Prune unneeded variables from a file to reduce file size
* Renaming varaibles
* Creating 1D profiles from 3D data.



## changeNC.py
This tool creates a new netcdf file, but simple changes can be made. Ie rename a variable, change the units, add attributes, multiply by 1000, etc.

## mergeNC.py
This tool  takes a list of netcdf files and merges them into one, provided they use the same grid, and contain the same variables.

## pruneNC.py
This tool  Copies variables from a netcdf file. Mostly to reduce the total size of the file.

## depthProfileNC.py
This tool  Creates a 1D profile netcdf at a specified location. Does not yet work for lat long coords, only grid index.

## depthManipNC.py
This tool is a bit built for a single project and and does some unusual things with depth integration. 
Unfortunately, this tool is the least stable, but it is the one I used to make surface/depth integration data.
It is built for purpose, and may not be suitable for other uses.



# Installation

Use pip to install this script:
```
pip install -e . --user
```

Alternatively, you can use `git clone` to make a local copy of the repository,
but don't forget to add the path of the cloned directory to your PYTHONPATH in ~/.cshrc or ~/.bashrc.

In .bashrc:
```
PYTHONPATH=$PYTHONPATH:$HOME/local/lib/netcdf_manip
```

In .cshrc:
```
setenv PYTHONPATH ${PYTHONPATH}:$HOME/local/lib/netcdf_manip
```



# License

Copyright 2015, Plymouth Marine Laboratory

Address:
Plymouth Marine Laboratory
Prospect Place, The Hoe
Plymouth, PL1 3DH, UK

Email:
ledm@pml.ac.uk

This file is part of the netcdf_manip library.

netcdf_manip is free software: you can redistribute it and/or modify it
under the terms of the Revised Berkeley Software Distribution (BSD) 3-clause license. 

netcdf_manip is distributed in the hope that it will be useful, but
without any warranty; without even the implied warranty of merchantability
or fitness for a particular purpose. See the revised BSD license for more details.
You should have received a copy of the revised BSD license along with netcdf_manip.
If not, see <http://opensource.org/licenses/BSD-3-Clause>.

