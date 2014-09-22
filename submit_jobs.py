#!/usr/bin/env python 

"""
This calls all the necessary routines to submit a grid of specified name and metallicity.
"""

import os
import sys
import shutil
from make_slurm_sh import make_slurm_sh 

runname = sys.argv[1]
Z = sys.argv[2]

work_dir = os.environ['MESAWORK_DIR']
cleanwork_dir = os.path.join(work_dir,"cleanworkdir")
dirname = os.path.join(work_dir, runname)
codedir = os.path.join(work_dir, "codes")
runbasefile = 'SLURM_MISTgrid.sh'

if __name__ == "__main__":

    #create a working directory
    try:
        os.mkdir(dirname)
    except OSError:
        print "The directory already exists"
        del_or_no = raw_input(dirname +' already exists. Delete? (1 or 0): ')
        if del_or_no == '1':
            print 'Deleting the directory...'
            shutil.rmtree(dirname)
            os.mkdir(dirname)
        elif del_or_no == '0':
            print 'Okay never mind.'
            sys.exit(0)
        else:
            print 'Invalid choice.'
            sys.exit(0)

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
            shutil.copytree(cleanwork_dir, pathtoinlistdir)
            
        except OSError:
            pass

        #take the inlists from the directory "inlists" and copy them to the individual directories & rename as inlist_project
        shutil.copy(os.path.join(orig_inlistdir,inlistname), os.path.join(pathtoinlistdir, 'inlist_project'))

        #create and move the pbs file into the correct directory
        slurmfile = make_slurm_sh(inlistname, pathtoinlistdir, runbasefile)
        shutil.move(slurmfile, pathtoinlistdir)

        #cd into the individual directory and qsub
        os.chdir(pathtoinlistdir)
        print "sbatch " + slurmfile
#        os.system("sbatch "+slurmfile)
        os.chdir(codedir)
    
