"""
This generates the Hyades cluster pbs file for each model.
"""

import os
import numpy as np

def make_pbsfiles(inlistname, inlistdir, pbsbasefile):

    runname = inlistname.strip(".inlist")
    massval = int(runname.split('M')[0])/100.0
    
    infile = open(pbsbasefile, 'r')
    infile_contents = infile.read()
    infile.close()

    replaced_contents = infile_contents.replace('<<RUNNAME>>', runname)
    replaced_contents = replaced_contents.replace('<<DIRNAME>>', inlistdir)
    if ((massval > 10) | ((massval > 4) & (massval < 7))):
        replaced_contents = replaced_contents.replace('<<WALLTIME>>', '30:00:00')
    else:
        replaced_contents = replaced_contents.replace('<<WALLTIME>>', '10:00:00')
    pbsfile = runname+'_run.pbs'

    outfile = open(pbsfile, 'w+')
    outfile.write(replaced_contents)
    outfile.close()

    return pbsfile
