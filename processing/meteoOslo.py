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

import os, glob
import pandas as pd
import numpy as np
    
import io # python3
# from cStringIO import StringIO # python2    

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

    readline = False
    with open(datafile, encoding='iso-8859-1') as f:
        for line in f:
            # stop gathering data
            if "Elements" in line:
                readline = False
                break
            # gather data if we are in correct part of the file
            if readline:
                # continuation of same subfile
                subfiles[-1].write(line)
            # start gathering data
            if "Stations" in line:
                readline = True
                # new subfile
                subfiles.append(io.StringIO())
        
    stats = []
    for subfile in subfiles:
        subfile.seek(0)
        df = pd.read_csv(subfile, sep=";")
        station_ids = df["Stnr"].tolist()
        station_names = df["Name"].tolist()
    
    stations = {}
    for idx, station in enumerate(station_names):
        name = station.split("- ")[-1] # stat!
        stations.update({station_ids[idx]:name})
        
    return stations

def parse_oslo_meteo():
    
    from datadir import datadiroslometeo as datadir

    files = gather_source_files(datadir)

    # create output directory
    subdir = os.path.join(os.path.dirname(files[0]),"OsloMeteo-processed")
    if not os.path.exists(subdir):
        os.mkdir(subdir)
    
    # map a month to correct index position
    month2indMap = {"January":0,
                   "February":1,
                   "March":2,
                   "April":3,
                   "May":4,
                   "June":5,
                   "July":6,
                   "August":7,
                   "September":8,
                   "October":9,
                   "November":10,
                   "December":11,
                   }
    # map a month to correct row position
    month2rowMap = {"January":31,
                   "February":29,
                   "March":31,
                   "April":30,
                   "May":31,
                   "June":30,
                   "July":31,
                   "August":31,
                   "September":30,
                   "October":31,
                   "November":30,
                   "December":31,
                   }
    # blank line to fill months with missing data
    blank = "0;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN;NaN\n"
    blank_header = "Date;TA 01;fTA 01;TA 07;fTA 07;TA 13;fTA 13;TA 19;fTA 19;TAM;fTAM;TAX;fTAX;TAN;fTAN;NN 01;fNN 01;NN 07;fNN 07;NN 13;fNN 13;NN 19;fNN 19;RR 01;fRR 01;RR 07;fRR 07;RR 13;fRR 13;RR 19;fRR 19;RR;fRR\n"
    # ind = 0 # for testing
    for datafile in files:
        # for testing, just run one file
        # if ind > 0: break
        # ind = ind + 1

        stations = get_station_data(datafile)

        # for key, value in d.iteritems(): # Python2
        for key, value in stations.items(): # Python3
            subfiles = [] # list of subfiles parsed out of megafile
            for i in range(len(month2indMap)):
                subfiles.append(io.StringIO())
            readline = False # none shall pass
            # iterate through datafile
            with open(datafile, encoding='iso-8859-1') as f:
                month = ""
                for line in f:
                    # stop gathering data
                    if line.strip() == "": # blank line
                        readline = False # stop
                    # gather data if we are in correct part of the file
                    if readline:
                        # continuation of same subfile
                        subfiles[month2indMap[month]].write(line)
                    # start gathering data
                    if str(key) in line:
                        # station lines not IN a table signify headers TO a data table
                        if ";" not in line: # use ; in place of month because of May..
                            readline = True # start
                            temp = line.split(value)[1]
                            month = temp.split(" ")[1]
                            if "No data" in line:
                                # write out blank lines for this month
                                subfiles[month2indMap[month]].write(blank_header)
                                for i in range(month2rowMap[month]):
                                    subfiles[month2indMap[month]].write(blank)
                                readline = False #stop

            frames = []
            drop = ("Number of","Minimum","Date","Maximum","Total","Mean","Normal","Deviation","%")
            # write subfiles to dataframes
            for subfile in subfiles:
                subfile.seek(0)
                df = pd.read_csv(subfile, sep=";")
                # drop some rows with useless info
                df = df[~df["Date"].isin(drop)]
                frames.append(df)
                        
            # concatenate dataframes
            df = pd.concat(frames)

            # set index to Date column
            df.set_index("Date", inplace=True)

            # modify format of index
            dates = pd.date_range('20160101 01', periods=366*4, freq='360min')
            
            # we only want 6 columns
            cols = ["TAM","TAX","TAN","TA","NN","RR"]
            
            # create a buffer to hold the rejiggered data
            out = np.zeros((df.shape[0]*4,len(cols)))
            
            # replace x values with -1000
            df = df.replace('x', -1000)
            
            # TA, NN, RR all have 4 hourly values per day
            out[0::4,3] = df["TA 01"].values
            out[1::4,3] = df["TA 07"].values
            out[2::4,3] = df["TA 13"].values
            out[3::4,3] = df["TA 19"].values
            
            out[0::4,4] = df["NN 01"].values
            out[1::4,4] = df["NN 07"].values
            out[2::4,4] = df["NN 13"].values
            out[3::4,4] = df["NN 19"].values
            
            out[0::4,5] = df["RR 01"].values
            out[1::4,5] = df["RR 07"].values
            out[2::4,5] = df["RR 13"].values
            out[3::4,5] = df["RR 19"].values
            
            # TAM, TAX, TAN all have one hourly value per day
            out[3::4,0] = df["TAM"].values
            out[3::4,1] = df["TAX"].values
            out[3::4,2] = df["TAN"].values

            df_out = pd.DataFrame(out, columns=cols, index=dates)

            # write new csv
            filename = str(value)+".csv"
            df_out.to_csv(os.path.join(subdir, filename))

            print ("Processed {}".format(filename))

def main():

    from datadir import datadiroslometeo as datadir
    
    parse_oslo_meteo()

if __name__ == "__main__":
    main()