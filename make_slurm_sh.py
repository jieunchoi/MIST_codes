"""
This generates the Odyssey cluster SLURM file for each model.
"""

import os
import numpy as np

def make_pbsfiles(inlistname, inlistdir, runbasefile):

    runname = inlistname.strip(".inlist")
    massval = int(runname.split('M')[0])/100.0
    
    infile = open(runbasefile, 'r')
    infile_contents = infile.read()
    infile.close()

    replaced_contents = infile_contents.replace('<<RUNNAME>>', runname)
    replaced_contents = replaced_contents.replace('<<DIRNAME>>', inlistdir)
    if ((massval > 10) | ((massval > 4) & (massval < 7))):
        replaced_contents = replaced_contents.replace('<<WALLTIME>>', '24:00:00')
    else:
        replaced_contents = replaced_contents.replace('<<WALLTIME>>', '36:00:00')
    runfile = runname+'_run.sh'

    outfile = open(runfile, 'w+')
    outfile.write(replaced_contents)
    outfile.close()

    return pbsfile
