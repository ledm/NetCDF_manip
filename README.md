NetCDF manipulation toolkit
============

A repository to assist with manipulating netcdf files. Merging, pruning, renaming varaibles, creating 1D profiles from 3D files.

They take fairly simple commands to run, but should be fairly powerful.

changeNC.py: creates a new netcdf file, but simple changes can be made. Ie rename a variable, change the units, add attributes, multiply by 1000, etc.

mergeNC.py: takes a list of netcdf files and merges them into one, provided they use the same grid, and contain the same variables.

pruneNC.py: Copies variables from a netcdf file. Mostly to reduce the total size of the file.

depthProfileNC.py: Creates a 1D profile netcdf at a specified location. Does not yet work for lat long coords, only grid index.

depthManipNC.py: This one is a bit crazy and does some unusual things with depth integration. Unfortunately, this one is the least stable, but it is the one I used to make surface/depth integration data for Jose.


Don't forget to add the path to your PYTHONPATH in ~/.cshrc or ~/.bashrc



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

