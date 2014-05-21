#!/usr/bin/env python 

"""
This calls all the necessary routines to submit a grid of specified name and metallicity.
"""

import os
import sys
import shutil
from make_pbsfiles import make_pbsfiles 

runname = sys.argv[1]
Z = sys.argv[2]

#Z = 0.016
#r = "MIST_v0.4"

work_dir = "/home/jchoi/pfs/mesawork/"
clean_work_dir = '/home/jchoi/pfs/clean_work_dir/'
dirname = os.path.join(work_dir, runname)
codedir = os.path.join(work_dir, "codes")
pbsbasefile = 'serial.pbs'

if __name__ == "__main__":

    #create a working directory
    try:
        os.mkdir(dirname)
    except OSError:
        print "The directory already exists"

    os.system("./make_inlists.py " + runname + " " + Z)
    orig_inlistdir = os.path.join(work_dir, 'inlists/inlists_'+runname)
    inlist_list = os.listdir(orig_inlistdir)
    inlist_list.sort()

    for inlistname in inlist_list:
        #make individual directories for each model
        inlistdir = inlistname.replace('.inlist', '_dir')

        #define an absolute path to the inlist directory within this working directory (ie. /home/jchoi/pfs/mesawork/V00_Z0.02_abSOLAR/10M_dir)
        pathtoinlistdir = os.path.join(dirname, inlistdir)

        try:
            shutil.copytree(clean_work_dir, pathtoinlistdir)
            
        except OSError:
            pass

        #take the inlists from the directory "inlists" and copy them to the individual directories & rename as inlist_project
        shutil.copy(os.path.join(orig_inlistdir,inlistname), os.path.join(pathtoinlistdir, 'inlist_project'))

        #create and move the pbs file into the correct directory
        pbsfile = make_pbsfiles(inlistname, pathtoinlistdir, pbsbasefile)
        shutil.move(pbsfile, pathtoinlistdir)

        #cd into the individual directory and qsub
        os.chdir(pathtoinlistdir)
        print "qsub " + pbsfile
        os.system("qsub "+pbsfile)
        os.chdir(codedir)
    
