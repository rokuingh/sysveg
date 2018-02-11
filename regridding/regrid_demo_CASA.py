import ESMF
import numpy as np

CASA_grid_file = "/software/co2flux/SurfaceFluxData/CASA/modified_GEE.3hrly.1x1.25.2015.nc"
STEM_grid_file = "/software/co2flux/Saved_WRF_runs/subset_wrfout.nc"
# CASA_grid_file = "data/modified_GEE.3hrly.1x1.25.2015.nc"
# STEM_grid_file = "data/subset_wrfout.nc"

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

        f = nc.Dataset(CASA_grid_file)
        gee = f.variables['GEE']
        gee = np.swapaxes(gee,1,2)
        # import pdb; pdb.set_trace()
        realdata = True
        field.data[:] = gee[0:23,:,:]
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
    fig.suptitle('CASA data regridding to 9km WRF-STEM', fontsize=14, fontweight='bold')

    ax = fig.add_subplot(1, 2, 1)
    im = ax.imshow(srcfield.data.T, cmap='hot', aspect='auto', origin="lower",
                   extent=[np.min(srclons), np.max(srclons), np.min(srclats), np.max(srclats)])
    ax.set_xbound(lower=np.min(srclons), upper=np.max(srclons))
    ax.set_ybound(lower=np.min(srclats), upper=np.max(srclats))
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("CASA GEE CO2 data")

    ax = fig.add_subplot(1, 2, 2)
    im = ax.imshow(interpfield.data.T, cmap='hot', aspect='auto', origin="lower",
                   extent=[np.min(dstlons), np.max(dstlons), np.min(dstlats), np.max(dstlats)])
    ax.set_xbound(lower=np.min(dstlons), upper=np.max(dstlons))
    ax.set_ybound(lower=np.min(dstlats), upper=np.max(dstlats))
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Conservative Regrid Solution on 9km WRF-STEM")

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.9, 0.1, 0.01, 0.8])
    fig.colorbar(im, cax=cbar_ax)

    plt.show()

##########################################################################################

# Start up ESMF, this call is only necessary to enable debug logging
esmpy = ESMF.Manager(debug=True)

# Create a destination grid from a GRIDSPEC formatted file.
srcgrid = ESMF.Grid(filename=CASA_grid_file, filetype=ESMF.FileFormat.GRIDSPEC,
                    add_corner_stagger=True, is_sphere=False)
dstgrid = ESMF.Grid(filename=STEM_grid_file, filetype=ESMF.FileFormat.GRIDSPEC,
                    add_corner_stagger=True, is_sphere=False)

srcfield = ESMF.Field(srcgrid, "srcfield", staggerloc=ESMF.StaggerLoc.CENTER, ndbounds=[24])
dstfield = ESMF.Field(dstgrid, "dstfield", staggerloc=ESMF.StaggerLoc.CENTER, ndbounds=[24])

srcfield = initialize_field(srcfield)

# Regrid from source grid to destination grid.
regridSrc2Dst = ESMF.Regrid(srcfield, dstfield,
                            regrid_method=ESMF.RegridMethod.CONSERVE,
                            unmapped_action=ESMF.UnmappedAction.ERROR)

dstfield = regridSrc2Dst(srcfield, dstfield)

if plot:
    try:
        import netCDF4 as nc
    except:
        raise ImportError('netCDF4 not available on this machine')

    # read longitudes and latitudes from file
    f = nc.Dataset(CASA_grid_file)
    srclons = f.variables['lon'][:]
    srclats = f.variables['lat'][:]

    f = nc.Dataset(STEM_grid_file)
    dstlons = f.variables['XLONG'][:]
    dstlats = f.variables['XLAT'][:]

    plot_sol(srclons, srclats, srcfield, dstlons, dstlats, dstfield)

print '\nregrid demo completed successfully.\n'
