#!/usr/bin/python
# Ryan O'Kuinghttons
# June 8, 2018

###############################################################################
#
# Modify the emissiones metadata for CF compliance and regridding purposes:
#
# python modify_emissiones.py
#
# Status:
# - NOTE below is to remove element_index temporarily to avoid an ocgis bug 
#   with ragged arrays. element_index will be needed in final product.
# - due to the use of shapefile output format, the NetCDF product naturally
#   lends itself to UGRID. There are a few ways this UGRID representation
#   could be converted to CF (structured grid) output if so desired:
#   1. change the disaggregation process to preserve grid info, use NetCDF
#      directly instead of shapefile
#   2. reverse engineer the shapefile generation, using the element index to
#      follow cell connectivity and piece together the grid layout
#   3. create a grid with the same vertices as this mesh and regrid
# - this script only uses a subset of the disaggregated files, the full set
#   is not yet available
# - beware the name changes for the data variables, so far the PMFINE seems
#   to be the only set of files with this issue
# 
# 
###############################################################################

import ocgis
import os
import numpy as np

datadir = "/home/ryan/Dropbox/backup/sandbox/sysveg/data/emissions_100m_shp"
guinea_pig = os.path.join(datadir, "CO_2015091_100m2.nc")
gp_shp = os.path.join(datadir, "CO_2015091_100m2.shp")
PATH_OUT = os.path.join(datadir, "TracerDissaggregate_100m2.nc")

# shapefiles to process
tracers = ["CO", "NO", "NO2", "PMFINE"]
timesteps = 3

# test generate tracers/timestep dependent file names
# for tracer in tracers:
#     var_name = tracer+"_100m2"
#     for timestep in range(timesteps):
#         sf_name = tracer+"_"+"2016"+str(timestep+1).zfill(3)+"_100m2.shp"
#         print (sf_name)
        
# read grid size from one file
field = ocgis.RequestDataset(os.path.join(datadir, gp_shp)).create_field()
ds_size = field.geom.shape[0];

# convert the shapefile geometries to netcdf, this can take several hours
# only do this once, and then add variables to netcdf afterwards
if (not guinea_pig):
    field = ocgis.RequestDataset(gp_shp).create_field()
    gc = field.geom.convert_to()
    field = gc.parent
    field.write(guinea_pig, driver='netcdf')


# test generate tracers/timestep dependent file names
tracer_array = np.zeros([len(tracers), timesteps, ds_size])
print("\nExtracting data from shapefile\n")
for tcr_ind, tracer in enumerate(tracers):
    var_name = tracer+"_100m2"
    # variable is named differently in the PMFINE file for some reason
    if (tracer == "PMFINE"):
        var_name = tracer+"_100"
    for timestep in range(timesteps):
        sf_name = tracer+"_"+"2016"+str(timestep+1).zfill(3)+"_100m2.shp"
        print ("  Processing "+sf_name)
        
        # open file
        field = ocgis.RequestDataset(os.path.join(datadir, sf_name), var_name).create_field()
        
        # extract variable
        tracer_array[tcr_ind, timestep, :] = field.get(var_name).get_value()
        

print ("\nAggregating data by timestep\n"+PATH_OUT)
# create variables from each tracer
var_list = []
for tcr_ind, tracer in enumerate(tracers):
    var_name = tracer+"_100m2"
    # variable is named differently in the PMFINE file for some reason
    if (tracer == "PMFINE"):
        var_name = tracer+"_100"
    var_list.append(ocgis.Variable(name=var_name, value=tracer_array[tcr_ind, :, :], dimensions=['time', 'ngeom']))

# read converted nc file into Field
field = ocgis.RequestDataset(guinea_pig).create_field()

# NOTE: remove element_index for now, to avoid bug with ragged arrays
field.remove_variable('element_index')

# add variables to Field
for var in var_list:
    field.add_variable(var)

# write Field
field.write(PATH_OUT)

print ("Output written to "+PATH_OUT)