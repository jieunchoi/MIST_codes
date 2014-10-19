#!/usr/bin/env python 

"""

Calls all of the necessary routines to submit a grid of specified name and metallicity.

Args:
    runname: the name of the grid
    Z: the mass fraction in metals
    
Example:
    To run a Z=0.015 grid called MIST_v0.1
    >>> ./submit_jobs MIST_v0.1 0.015

"""

import os
import sys
import shutil
from make_slurm_sh import make_slurm_sh
from make_inlist_inputs import make_inlist_inputs
from make_replacements import make_replacements

runname = sys.argv[1]
Z = sys.argv[2]

work_dir = os.environ['MESAWORK_DIR']
code_dir = os.environ['MIST_CODE_DIR']
dirname = os.path.join(work_dir, runname)
cleanwork_dir = os.path.join(work_dir, "cleanworkdir")
orig_inlist_dir = os.path.join(work_dir, 'inlists/inlists_'+'_'.join(runname.split('/')))
runbasefile = 'SLURM_MISTgrid.sh'

if __name__ == "__main__":

    #Create a working directory
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
            print 'Do not delete.'
            sys.exit(0)
        else:
            print 'Invalid choice.'
            sys.exit(0)

    #Generate inlists using template inlist files
    new_inlist_name = '<<MASS>>M<<BC_LABEL>>.inlist'
    make_replacements(make_inlist_inputs(runname, Z, 'VeryLow'), new_inlist_name,\
        direc=orig_inlist_dir, file_base=os.path.join(code_dir,'inlist_lowinter'), clear_direc=True)
    make_replacements(make_inlist_inputs(runname, Z, 'LowDiffBC'), new_inlist_name,\
        direc=orig_inlist_dir, file_base=os.path.join(code_dir,'inlist_lowinter'))
    make_replacements(make_inlist_inputs(runname, Z, 'Intermediate'), new_inlist_name,\
        direc=orig_inlist_dir, file_base=os.path.join(code_dir,'inlist_lowinter'))
    make_replacements(make_inlist_inputs(runname, Z, 'HighDiffBC'), new_inlist_name,\
        direc=orig_inlist_dir, file_base=os.path.join(code_dir,'inlist_high'))
    make_replacements(make_inlist_inputs(runname, Z, 'VeryHigh'), new_inlist_name,\
        direc=orig_inlist_dir, file_base=os.path.join(code_dir,'inlist_high'))
        
    inlist_list = os.listdir(orig_inlist_dir)
    inlist_list.sort()

    for inlistname in inlist_list:
        #Make individual directories for each mass
        inlistdir = inlistname.replace('.inlist', '_dir')

        #Define an absolute path to this directory.
        pathtoinlistdir = os.path.join(dirname, inlistdir)

        #Copy over the contents of the template directory and copy over the most recent my_history_columns.list and run_star_extras.f
        try:
            shutil.copytree(cleanwork_dir, pathtoinlistdir)
            shutil.copy(os.path.join(code_dir, 'my_history_columns.list'), os.path.join(cleanwork_dir, 'my_history_columns.list'))
            shutil.copy(os.path.join(code_dir, 'run_star_extras.f'), os.path.join(cleanwork_dir, 'src/run_star_extras.f'))
        except OSError:
            pass

        #Populate each directory with appropriate inlists and rename as inlist_project
        shutil.copy(os.path.join(orig_inlist_dir,inlistname), os.path.join(pathtoinlistdir, 'inlist_project'))

        #Create and move the SLURM file to the correct directory
        slurmfile = make_slurm_sh(inlistname, pathtoinlistdir, runbasefile)
        shutil.move(slurmfile, pathtoinlistdir)

        #cd into the individual directory and submit the job
        os.chdir(pathtoinlistdir)
        print "sbatch " + slurmfile
        os.system("sbatch "+slurmfile)
        os.chdir(code_dir)
    
