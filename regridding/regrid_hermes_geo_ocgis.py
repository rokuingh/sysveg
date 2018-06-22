#!/usr/bin/python
# Ryan O'Kuinghttons
# May 23, 2018

###############################################################################
#
#  Regrid the HERMES emisiones data onto geo grid, run with:
#
#  python regrid_hermes_geo_ocgis.py
#
# 
# TODO:
# - change missing values to 0
# - investigate whether there are more than 2 time steps and if so why
# - use a conservative RegridMethod
# - run domain 4 (barcelona)
# 
# 
###############################################################################

import ocgis


emi_file = "/home/ryan/sandbox/sysveg/data/HERMES/Emisiones_CAT1_2015091_UAB_4_grid.nc"
# emi_file = "/nfs/pic.es/user/r/rokuingh/sandbox/sysveg/data/HERMES/Emisiones_CAT1_2015091_UAB_4_grid.nc"
geo_file = "/home/ryan/sandbox/sysveg/data/HERMES/geo_em.d03-2.nc"
# geo_file = "/nfs/pic.es/user/r/rokuingh/sandbox/sysveg/data/HERMES/geo_em.d03-2.nc"

# Regrid using bilinear interpolation (i.e. without corners)

rd_in = ocgis.RequestDataset(uri=emi_file, format_time=False)
rd_out = ocgis.RequestDataset(uri=geo_file, format_time=False)
regrid_options = {'regrid_method': ESMF.RegridMethod.BILINEAR,
                  'split':False}

# import ipdb; ipdb.set_trace()

ops = ocgis.OcgOperations(dataset=rd_in, regrid_destination=rd_out, output_format='nc',
                          regrid_options=regrid_options, prefix='geo_output')
ret = ops.execute()
