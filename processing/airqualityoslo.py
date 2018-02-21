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

    for f in files:
        # split out the tracer name based on file name
        temp = f.split("-")[0]
        sub = temp.split("/")[-1]

        # use pandas to rearrange the columns
        f_in=pd.read_csv(f, encoding = 'utf8')
        # keep_col = [s for s in f_in.columns.values if sub in s]
        keep_col = [s for s in f_in.columns.values if "|" in s]
        keep_col.insert(0, u"Til-tid")
        keep_col.insert(0, u"Fra-tid")
        f_out = f_in[keep_col]
        f_out.to_csv(sub+".csv", index=False, encoding = 'utf8')

        print ("Processed {}").format(f)

def main(datadir):

    parse_pandas(gather_source_files(datadir))

if __name__ == "__main__":
    from datadir import datadir as datadir
    main(datadir)
