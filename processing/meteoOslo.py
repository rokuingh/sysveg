#!/usr/bin/python
# Ryan O'Kuinghttons
# March 15, 2018

###############################################################################
#
#  Rejigger meteo data from csv, run with:
#
#  python meteoOslo.py
#
#  datadir.py file contains the path to the dir with data files of interest
###############################################################################

import pandas as pd
import os, glob
from cStringIO import StringIO

    
# pull together csv files 
def gather_source_files(datadir):
    
    if not os.path.isdir(datadir):
        raise ValueError("Directory: " + datadir + " was not found.  DING!")

    os.chdir(datadir)
    files = []

    for f in glob.glob("file*.txt"):
        files.append(os.path.join(datadir, f))
    files.sort()
    
    return files

def get_station_data(datafile):

    subfiles = []

    go = False
    with open(datafile) as f:
        for line in f:
            # stop gathering data
            if "Elements" in line:
                go = False
                break
            # gather data if we are in correct part of the file
            if go:
                # continuation of same subfile
                subfiles[-1].write(line)
            # start gathering data
            if "Stations" in line:
                go = True
                # new subfile
                subfiles.append(StringIO())
        
    stations = []
    for subfile in subfiles:
        subfile.seek(0)
        df = pd.read_csv(subfile, sep=";")
        stations = df["Name"].tolist()
    
    return stations

def parse_oslo_meteo():
    
    from datadir import datadiroslometeo as datadir

    files = gather_source_files(datadir)

    # create output directory
    subdir = os.path.join(os.path.dirname(files[0]),"OsloMeteo-processed")
    if not os.path.exists(subdir):
        os.mkdir(subdir)
    
    ind = 0 # for testing
    for datafile in files:
        # for testing, just run one file
        if ind > 0: break
        ind = ind + 1

        stations = get_station_data(datafile)

        for station in stations:
            subfiles = [] # list of subfiles parsed out of megafile
            readline = False # none shall pass
            stat = station.split(" ")[-1] # stat!
            # iterate through datafile
            with open(datafile) as f:
                for line in f:
                    print line
                    # stop gathering data
                    if line.strip() == "": # blank line
                        print "------------------ STOP ---------------------"
                        readline = False
                    # gather data if we are in correct part of the file
                    if readline:
                        # continuation of same subfile
                        subfiles[-1].write(line)
                    # start gathering data
                    if stat in line:
                        print "------------------START---------------------"
                        readline = True
                        # new subfile
                        subfiles.append(StringIO())
            
            frames = []
            print len(subfiles) # station name is found in stations dataframe first..
            import ipdb; ipdb.set_trace()

            for subfile in subfiles:
                subfile.seek(0)
                df = pd.read_csv(subfile, sep=";")
                frames.append(df)
                        
            # concatenate dataframes
            out_df = pd.concat(frames)
            
            # modify date index
            dates = pd.date_range('20160101', periods=days, freq='D')
            out_df["Date"] = dates
            
            # write new csv
            filename = str(stat)+".csv"
            # out_df.to_csv(os.path.join(subdir, filename))

            print ("Processed {}").format(filename)

def main():

    from datadir import datadiroslometeo as datadir
    
    parse_oslo_meteo()

if __name__ == "__main__":
    main()
