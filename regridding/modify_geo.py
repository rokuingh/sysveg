import ocgis

PATH_IN = "/home/ryan/sandbox/sysveg/data/HERMES/geo_em.d03.nc"
PATH_IN = "/nfs/pic.es/user/r/rokuingh/sandbox/sysveg/data/HERMES/geo_em.d03.nc"
PATH_OUT = "/home/ryan/sandbox/sysveg/data/HERMES/geo_em.d03-2.nc"
PATH_OUT = "/nfs/pic.es/user/r/rokuingh/sandbox/sysveg/data/HERMES/geo_em.d03-2.nc"

rd = ocgis.RequestDataset(PATH_IN)
field = rd.create_field()

# field["lonx"].set_name("bounds_lon")
# field["latx"].set_name("bounds_lat")

lon = field.get('XLONG_M').get_value()
lat = field.get('XLAT_M').get_value()

ydim = field.dimensions["south_north"]
xdim = field.dimensions["west_east"]
# 
lon_notime = lon[0,:,:]
lat_notime = lat[0,:,:]

# import ipdb; ipdb.set_trace()

field.remove_variable('XLONG_M')
field.remove_variable('XLAT_M')

attrs = {"units":"degrees_east",
         "axis":"x"}
var = ocgis.Variable(name='lon', value=lon_notime, dimensions=[ydim, xdim], 
                     attrs=attrs)
field.add_variable(var)


attrs = {"units":"degrees_north",
         "axis":"y"}
var = ocgis.Variable(name='lat', value=lat_notime, dimensions=[ydim, xdim],
                     attrs=attrs)
field.add_variable(var)

# field["lon_center"].set_name("lon")
# field["lat_center"].set_name("lat")

# now create a grid and write bounds
## grid = field.grid
# field["lon"].set_bounds(field.get('bounds_lon').extract(), force=True)
# field["lat"].set_bounds(field.get('bounds_lat').extract(), force=True)
# grid = ocgis.Grid(field["lon"], field['lat'], crs=ocgis.crs.Spherical(), parent=field)

# grid.set_extrapolated_bounds('bounds_lon', 'bounds_lat', 'corners')
# grid.x.bounds.attrs.pop('units')
# grid.y.bounds.attrs.pop('units')

field.remove_variable('Times')
field.remove_variable('XLAT_V')
field.remove_variable('XLONG_V')
field.remove_variable('XLAT_U')
field.remove_variable('XLONG_U')
field.remove_variable('CLAT')
field.remove_variable('CLONG')
field.remove_variable('MAPFAC_M')
field.remove_variable('MAPFAC_V')
field.remove_variable('MAPFAC_U')
field.remove_variable('MAPFAC_MX')
field.remove_variable('MAPFAC_VX')
field.remove_variable('MAPFAC_UX')
field.remove_variable('MAPFAC_MY')
field.remove_variable('MAPFAC_VY')
field.remove_variable('MAPFAC_UY')
field.remove_variable('E')
field.remove_variable('F')
field.remove_variable('SINALPHA')
field.remove_variable('COSALPHA')
field.remove_variable('LANDMASK')
field.remove_variable('LANDUSEF')
field.remove_variable('LU_INDEX')
field.remove_variable('HGT_M')
field.remove_variable('SOILTEMP')
field.remove_variable('SOILCTOP')
field.remove_variable('SCT_DOM')
field.remove_variable('SOILCBOT')
field.remove_variable('SCB_DOM')
field.remove_variable('ALBEDO12M')
field.remove_variable('GREENFRAC')
field.remove_variable('LAI12M')
field.remove_variable('SNOALB')
field.remove_variable('SLOPECAT')
field.remove_variable('CON')
field.remove_variable('VAR')
field.remove_variable('OA1')
field.remove_variable('OA2')
field.remove_variable('OA3')
field.remove_variable('OA4')
field.remove_variable('OL1')
field.remove_variable('OL2')
field.remove_variable('OL3')
field.remove_variable('OL4')
field.remove_variable('VAR_SSO')
field.remove_variable('LAKE_DEPTH')


# write from Field to get the variables
field.write(PATH_OUT)
# need to use grid.parent when using ocgis to calculate bounds
# grid.parent.write(PATH_OUT)
