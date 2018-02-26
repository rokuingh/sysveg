#!/usr/bin/python
# Ryan O'Kuinghttons
# Feb 16, 2018

###############################################################################
#
#  Rejigger air quality data from csv, run with:
#
#  python airqualityoslo.py
#
#  datadir.py file contains the path to the dir with data files of interest
###############################################################################

# pull together csv files 
def gather_source_files(datadir):
    import os, glob

    if not os.path.isdir(datadir):
        raise ValueError("Directory: " + datadir + " was not found.  DING!")

    os.chdir(datadir)
    files = []

    for f in glob.glob("*.csv"):
        files.append(os.path.join(datadir, f))
    files.sort()
    
    return files


def parse_pandas(files):
    import pandas as pd
    import os

    for f in files:
        # split out the tracer name based on file name
        temp = f.split("-")[0]
        sub = temp.split("/")[-1]
        subdir = os.path.join(os.path.dirname(f),"OsloAQ-processed")
        if not os.path.exists(subdir):
            os.mkdir(subdir)

        # use pandas to rearrange the columns
        f_in=pd.read_csv(f, encoding = 'utf8')

        # delete unwanted columns
        keep_col = [s for s in f_in.columns.values if "|" in s]
        keep_col.insert(0, u"Fra-tid")
        f_out = f_in[keep_col]

        # rename the columns with only tracer values
        i = 0
        newcols = f_out.columns.values
        for col in f_out.columns.values:
            if "|" in col:
                newcol = col.split("|")[1]
                newcol = newcol.strip()
                newcols[i] = newcol
            i = i + 1
        f_out.columns = newcols

        # split first column into two
        # NOTE: throws warning about a copy of a slice, disregard
        f_out['Fra-tid'], f_out['Time'] = f_out['Fra-tid'].str.split(' ', 1).str
        
        # move new time column to second place
        cols = f_out.columns.tolist()
        cols.insert(1, cols.pop(cols.index('Time')))
        f_out = f_out[cols]

        # write new csv
        f_out.to_csv(os.path.join(subdir, sub+".csv"), index=False, encoding = 'utf8')

        print ("Processed {}").format(f)

def main(datadir):

    parse_pandas(gather_source_files(datadir))

if __name__ == "__main__":
    from datadir import datadiroslo as datadir
    main(datadir)
