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

from scripts import make_slurm_sh
from scripts import make_inlist_inputs
from scripts import make_replacements
from scripts import calc_xyz

if __name__ == "__main__":

    #Digest the inputs
    runname = sys.argv[1]
    FeH = sys.argv[2]
    Z = calc_xyz.calc_xyz(float(FeH),input_feh=True)[-1]
    dirname = os.path.join(os.environ['MIST_GRID_DIR'], runname)
    
    #Create a working directory
    try:
        os.mkdir(dirname)
    except OSError:
        print "The directory already exists"
        sys.exit(0)

    #Generate inlists using template inlist files
    tempstor_inlist_dir = os.path.join(os.environ['MESAWORK_DIR'], 'inlists/inlists_'+'_'.join(runname.split('/')))
    new_inlist_name = '<<MASS>>M<<BC_LABEL>>.inlist'
    make_replacements.make_replacements(make_inlist_inputs.make_inlist_inputs(runname, Z, 'VeryLow'), new_inlist_name,\
        direc=tempstor_inlist_dir, file_base=os.path.join(os.environ['MIST_CODE_DIR'],'mesafiles/inlist_lowinter'), clear_direc=True)
    make_replacements.make_replacements(make_inlist_inputs.make_inlist_inputs(runname, Z, 'LowDiffBC'), new_inlist_name,\
        direc=tempstor_inlist_dir, file_base=os.path.join(os.environ['MIST_CODE_DIR'],'mesafiles/inlist_lowinter'))
    make_replacements.make_replacements(make_inlist_inputs.make_inlist_inputs(runname, Z, 'Intermediate'), new_inlist_name,\
        direc=tempstor_inlist_dir, file_base=os.path.join(os.environ['MIST_CODE_DIR'],'mesafiles/inlist_lowinter'))
    make_replacements.make_replacements(make_inlist_inputs.make_inlist_inputs(runname, Z, 'HighDiffBC'), new_inlist_name,\
        direc=tempstor_inlist_dir, file_base=os.path.join(os.environ['MIST_CODE_DIR'],'mesafiles/inlist_high'))
    make_replacements.make_replacements(make_inlist_inputs.make_inlist_inputs(runname, Z, 'VeryHigh'), new_inlist_name,\
        direc=tempstor_inlist_dir, file_base=os.path.join(os.environ['MIST_CODE_DIR'],'mesafiles/inlist_high'))
        
    inlist_list = os.listdir(tempstor_inlist_dir)
    inlist_list.sort()

    for inlistname in inlist_list:
        #Make individual directories for each mass
        inlistdir = inlistname.replace('.inlist', '_dir')

        #Define an absolute path to this directory.
        pathtoinlistdir = os.path.join(dirname, inlistdir)

        #Copy over the contents of the template directory and copy over the most recent my_history_columns.list and run_star_extras.f
        try:
            shutil.copytree(os.path.join(os.environ['MESAWORK_DIR'], "cleanworkdir"), pathtoinlistdir)
            shutil.copy(os.path.join(os.environ['MIST_CODE_DIR'], 'mesafiles/my_history_columns.list'), os.path.join(os.path.join(os.environ['MESAWORK_DIR'], "cleanworkdir"), 'my_history_columns.list'))
            shutil.copy(os.path.join(os.environ['MIST_CODE_DIR'], 'mesafiles/run_star_extras.f'), os.path.join(os.path.join(os.environ['MESAWORK_DIR'], "cleanworkdir"), 'src/run_star_extras.f'))
        except OSError:
            pass

        #Populate each directory with appropriate inlists and rename as inlist_project
        shutil.copy(os.path.join(tempstor_inlist_dir,inlistname), os.path.join(pathtoinlistdir, 'inlist_project'))

        #Create and move the SLURM file to the correct directory
        runbasefile = os.path.join(os.environ['MIST_CODE_DIR'], 'mesafiles/SLURM_MISTgrid.sh')
        slurmfile = make_slurm_sh.make_slurm_sh(inlistname, pathtoinlistdir, runbasefile)
        shutil.move(slurmfile, pathtoinlistdir)
        
        #cd into the individual directory and submit the job
        os.chdir(pathtoinlistdir)
        print "sbatch " + slurmfile
        os.system("sbatch "+slurmfile)
        os.chdir(os.environ['MIST_CODE_DIR'])
    
