#!/usr/bin/python
# Ryan O'Kuinghttons
# Feb 26, 2018

###############################################################################
#
#  Rejigger air quality data from csv, run with:
#
#  python airqualitybarcelona.py
#
#  datadir.py file contains the path to the dir with data files of interest
###############################################################################

import pandas as pd
import os, glob
import numpy as np
    
# pull together csv files 
def gather_source_files(datadir):
    
    if not os.path.isdir(datadir):
        raise ValueError("Directory: " + datadir + " was not found.  DING!")

    os.chdir(datadir)
    files = []

    for f in glob.glob("*.csv"):
        files.append(os.path.join(datadir, f))
    files.sort()
    
    return files

def get_station_data(datadir):
    
    if not os.path.isdir(datadir):
        raise ValueError("Directory: " + datadir + " was not found.  DING!")

    os.chdir(datadir)
    files = []

    for f in glob.glob("*.txt"):
        files.append(os.path.join(datadir, f))

    sfile = ""
    for f in files:
        if "Stations" in f:
            sfile = f

    df = pd.read_csv(sfile, sep = ";")
    
    # delete unwanted columns
    df = df.dropna(how='all')
    stations = df["COD_LOCAL"].astype(int).tolist()
    
    return stations

def parse_barcelona_aq():
    
    from datadir import datadirbarcelona as datadir

    files = gather_source_files(datadir)
    
    stations = get_station_data(datadir)

    # create output directory
    subdir = os.path.join(os.path.dirname(files[0]),"BarcelonaAQ-processed")
    if not os.path.exists(subdir):
        os.mkdir(subdir)
        
    # split out tracer names from file names
    tracers = []
    for f in files:
        t = f.split("_")[0]
        tracers.append(t.split("/")[-1])
            
    # numpy array to hold all data
    hours = 24
    days = 366
    statdat = np.zeros([hours*days, len(tracers), len(stations)])
    
    # map a month to correct row position
    date2rowMap = {"1":0,
                   "2":31,
                   "3":31+29,
                   "4":31+29+31,
                   "5":31+29+31+30,
                   "6":31+29+31+30+31,
                   "7":31+29+31+30+31+30,
                   "8":31+29+31+30+31+30+31,
                   "9":31+29+31+30+31+30+31+31,
                   "10":31+29+31+30+31+30+31+31+30,
                   "11":31+29+31+30+31+30+31+31+30+31,
                   "12":31+29+31+30+31+30+31+31+30+31+30,
                   }
    
    # save an index for the tracers dimension of the statdat array
    t_i = -1
    for f in files:        
        # move to the next tracer
        t_i = t_i + 1
        
        # just run one file for testing purposes
        # if t_i > 0: break
        
        # read the tracer file into a dataframe
        df=pd.read_csv(f, sep=';')

        # assert columns are in proper order
        assert(f.split("_")[0].split("/")[-1] == tracers[t_i])
        
        # record the columns of dataframe that hold data values of interest
        keep_col = [c for c in df.columns.values if "H" in c]

        # assert we have the proper number of columns
        assert(len(keep_col) == hours)

        # iterate rows of tracer datafile searching for matching stations
        for index, row in df.iterrows():
            # split off the station id
            pm = row['PUNTO_MUESTREO'].split("_")[0]
            
            # stations of interest
            for i in range(len(stations)):
                station = stations[i]
                # match station of interest with row in tracer data file
                if str(station) in str(pm):
                    # map this month and day to row block of data array
                    r_i = (date2rowMap[str(row["MES"])] + row["DIA"] - 1) * hours
                    # save tracer data in array
                    statdat[r_i:r_i+hours,t_i,i] = row[keep_col].values.copy()

    for i in range(len(stations)):
        # just run one file for testing purposes
        # if i > 0: break

        # create index
        dates = pd.date_range('20160101 00:00', periods=hours*days, freq='H')

        # create dataframe of the station we want to output
        out_df = pd.DataFrame(statdat[:,:,i],  index=dates, columns=tracers)

        # write new csv
        filename = str(stations[i])+".csv"
        out_df.to_csv(os.path.join(subdir, filename))

        print ("Processed {}").format(filename)

def main():

    parse_barcelona_aq()

if __name__ == "__main__":
    main()
