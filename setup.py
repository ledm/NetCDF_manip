from setuptools import setup

MAJOR               = 0
MINOR               = 1
VERSION = '{}.{}'.format(MAJOR, MINOR)

######
# Use pip to install this script:
# pip install -e . --user

setup(name="netcdf_manip",
      version=VERSION,
      description="A repository to assist with manipulating netcdf files. Merging, pruning, renaming varaibles, creating 1D profiles from 3D files.",
      author="Lee de Mora (PML)",
      author_email="ledm@pml.ac.uk",
      url="https://gitlab.ecosystem-modelling.pml.ac.uk/ledm/netcdf_manip",
      license='Revised Berkeley Software Distribution (BSD) 3-clause license.',
      classifiers=[
          'Development Status :: 1 - Alpha',
          'Intended Audience :: Scientific researcher',
          'Topic :: NetCDF editing',
          'License :: OSI Approved :: BSD3 License',
          'Programming Language :: Python :: 2.7',
          'Operating System :: UNIX',
      ],
      install_requires=[
          "numpy",
          "netCDF4", 
          "datetime",
      ],
      )


