#!/usr/bin/python
# Ryan O'Kuinghttons
# April 11, 2018

###############################################################################
#
#  Regrid the HERMES emisiones data onto geo grid, run with:
#
#  python regrid_hermes_geo.py
#
###############################################################################

import ESMF
import numpy as np

geo_file = "/nfs/pic.es/user/r/rokuingh/sandbox/sysveg/data/geo_em.d03.nc"
emi_file = "/nfs/pic.es/user/r/rokuingh/sandbox/sysveg/data/Emisiones_CAT1_2015091_UAB_4.nc"

plot = True
init = True

try:
    import netCDF4 as nc
except:
    init = False
    plot = False

try:
    import matplotlib
    import matplotlib.pyplot as plt
except:
    plot = False

def initialize_field(field):
    if init:
        try:
            import netCDF4 as nc
        except:
            raise ImportError('netCDF4 not available on this machine')

        f = nc.Dataset(emi_file)
        co2 = f.variables['CO2']
        # this should switch from [time,level,lat,lon] to [lon,lat,level,time]
        co2 = np.swapaxes(co2,1,3)
        co2 = np.swapaxes(co2,2,4)
        co2 = np.swapaxes(co2,3,4)        
        # import pdb; pdb.set_trace()
        realdata = True
        field.data[:] = gee[:,:,:,:]
    else:
        field.data[:] = 42.0

    return field

def compute_mass(valuefield, areafield, fracfield, dofrac):
    mass = 0.0
    areafield.get_area()
    if dofrac:
        mass = np.sum(areafield.data[:]*valuefield.data[:]*fracfield.data[:])
    else:
        mass = np.sum(areafield.data[:] * valuefield.data[:])

    return mass

def plot_sol(srclons, srclats, srcfield, dstlons, dstlats, interpfield):

    try:
        import matplotlib
        import matplotlib.pyplot as plt
    except:
        raise ImportError("matplotlib is not available on this machine")

    fig = plt.figure(1, (15, 6))
    fig.suptitle('geo', fontsize=14, fontweight='bold')

    ax = fig.add_subplot(1, 2, 1)
    im = ax.imshow(srcfield.data.T, cmap='hot', aspect='auto', origin="lower",
                   extent=[np.min(srclons), np.max(srclons), np.min(srclats), np.max(srclats)])
    ax.set_xbound(lower=np.min(srclons), upper=np.max(srclons))
    ax.set_ybound(lower=np.min(srclats), upper=np.max(srclats))
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("geo")

    ax = fig.add_subplot(1, 2, 2)
    im = ax.imshow(interpfield.data.T, cmap='hot', aspect='auto', origin="lower",
                   extent=[np.min(dstlons), np.max(dstlons), np.min(dstlats), np.max(dstlats)])
    ax.set_xbound(lower=np.min(dstlons), upper=np.max(dstlons))
    ax.set_ybound(lower=np.min(dstlats), upper=np.max(dstlats))
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("geo")

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.9, 0.1, 0.01, 0.8])
    fig.colorbar(im, cax=cbar_ax)

    plt.show()

##########################################################################################

# Start up ESMF, this call is only necessary to enable debug logging
esmpy = ESMF.Manager(debug=True)

# Create a destination grid from a GRIDSPEC formatted file.
srcgrid = ESMF.Grid(filename=emi_file, filetype=ESMF.FileFormat.GRIDSPEC,
                    add_corner_stagger=False, is_sphere=False,
                    coord_names=[])
dstgrid = ESMF.Grid(filename=geo_file, filetype=ESMF.FileFormat.GRIDSPEC,
                    add_corner_stagger=False, is_sphere=False,
                    coord_names=["XLONG_U", "XLAT_U"])

srcfield = ESMF.Field(srcgrid, "srcfield", staggerloc=ESMF.StaggerLoc.CENTER, ndbounds=[11,24])
dstfield = ESMF.Field(dstgrid, "dstfield", staggerloc=ESMF.StaggerLoc.CENTER, ndbounds=[11,24])

srcfield = initialize_field(srcfield)

# Regrid from source grid to destination grid.
regridSrc2Dst = ESMF.Regrid(srcfield, dstfield,
                            regrid_method=ESMF.RegridMethod.BILINEAR,
                            unmapped_action=ESMF.UnmappedAction.ERROR)

dstfield = regridSrc2Dst(srcfield, dstfield)

print '\nregrid demo completed successfully.\n'
