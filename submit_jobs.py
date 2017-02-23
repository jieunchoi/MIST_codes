#!/usr/bin/env python 

"""

Calls all of the necessary routines to submit a grid of specified name and metallicity.

Args:
    runname: the name of the grid
    FeH: metallicity
    aFe: alpha-enhancement
    
Example:
    To run a [Fe/H] = 0, [a/Fe] = 0 grid called MIST_v0.1
    >>> ./submit_jobs MIST_v0.1 0.0 0.0

"""

import os
import sys
import shutil

from scripts import make_slurm_sh
from scripts import make_inlist_inputs
from scripts import make_replacements

if __name__ == "__main__":

    #Digest the inputs
    runname = sys.argv[1]
    FeH = sys.argv[2]
    aFe = sys.argv[3]
    dirname = os.path.join(os.environ['MIST_GRID_DIR'], runname)
    
    #Create a working directory
    try:
        os.mkdir(dirname)
    except OSError:
        print "The directory already exists."
        sys.exit(0)

    ###RUN AARON'S CODE HERE
    ###generate the Zbase_val.txt file and the abundances list file
    
    #Generate inlists using template inlist files
    tempstor_inlist_dir = os.path.join(os.environ['MESAWORK_DIR'], 'inlists/inlists_'+'_'.join(runname.split('/')))
    new_inlist_name = '<<MASS>>M<<BC_LABEL>>.inlist'
    path_to_inlist_lowinter = os.path.join(os.environ['MIST_CODE_DIR'],'mesafiles/inlist_lowinter')
    path_to_inlist_high = os.path.join(os.environ['MIST_CODE_DIR'],'mesafiles/inlist_high')
    
    #The nuclear network must be specified since it is an input to Aaron's code to get the abundances
    net_name = 'mesa_49.net'
    
    #aFe value must be between -0.2 and 0.6 in steps of 0.2 (for opacity table reasons)
    okay_Fe = [-0.2, 0.0, 0.2, 0.4, 0.6]
    if aFe not in okay_Fe:
        print "[a/Fe] must be one of the following: "+(" ").join([str(x) for x in okay_Fe])
        sys.exit(0)
    if aFe < 0:
        afe_fmt = 'afe'+str(aFe)
    else:
        afe_fmt = 'afe+'+str(aFe)
        
    #Zbase needs to be set in MESA for Type II opacity tables. Get this from a file produced by Aaron's code
    with open('Zbase_val.txt') as f:
        Zbase = float(f.read())
    
    #Make the substitutions in the template inlists
    make_replacements.make_replacements(make_inlist_inputs.make_inlist_inputs(runname, 'VeryLow', afe_formatted, zbase, net=net_name),\
        new_inlist_name, direc=tempstor_inlist_dir, file_base=path_to_inlist_lowinter, clear_direc=True)
    make_replacements.make_replacements(make_inlist_inputs.make_inlist_inputs(runname, 'LowDiffBC', afe, zbase, net=net_name),\
        new_inlist_name, direc=tempstor_inlist_dir, file_base=path_to_inlist_lowinter)
    make_replacements.make_replacements(make_inlist_inputs.make_inlist_inputs(runname, 'Intermediate', afe, zbase, net=net_name),\
        new_inlist_name, direc=tempstor_inlist_dir, file_base=path_to_inlist_lowinter)
    make_replacements.make_replacements(make_inlist_inputs.make_inlist_inputs(runname, 'HighDiffBC', afe, zbase, net=net_name),\
        new_inlist_name, direc=tempstor_inlist_dir, file_base=path_to_inlist_high))
    make_replacements.make_replacements(make_inlist_inputs.make_inlist_inputs(runname, 'VeryHigh', afe, zbase, net=net_name),\
        new_inlist_name, direc=tempstor_inlist_dir, file_base=path_to_inlist_high)
        
    inlist_list = os.listdir(tempstor_inlist_dir)
    inlist_list.sort()

    for inlistname in inlist_list:
        #Make individual directories for each mass
        onemassdir = inlistname.replace('.inlist', '_dir')

        #Define an absolute path to this directory.
        path_to_onemassdir = os.path.join(dirname, onemassdir)

        #Copy over the contents of the template directory
        shutil.copytree(os.path.join(os.environ['MESAWORK_DIR'], "cleanworkdir"), path_to_onemassdir)

        #Populate each directory with appropriate inlists and rename as inlist_project
        shutil.copy(os.path.join(tempstor_inlist_dir,inlistname), os.path.join(path_to_onemassdir, 'inlist_project'))
        
        #Populate each directory with the most recent my_history_columns.list and run_star_extras.f
        shutil.copy(os.path.join(os.environ['MIST_CODE_DIR'], 'mesafiles/my_history_columns.list'),\
                os.path.join(path_to_onemassdir, 'my_history_columns.list'))
        shutil.copy(os.path.join(os.environ['MIST_CODE_DIR'], 'mesafiles/run_star_extras.f'),\
                os.path.join(path_to_onemassdir, 'src/run_star_extras.f'))
        
        #Populate each directory with the input abundance file named input_initial_composition.data
        #shutil.move()

        #Create and move the SLURM file to the correct directory
        runbasefile = os.path.join(os.environ['MIST_CODE_DIR'], 'mesafiles/SLURM_MISTgrid.sh')
        slurmfile = make_slurm_sh.make_slurm_sh(inlistname, path_to_onemassdir, runbasefile)
        shutil.move(slurmfile, path_to_onemassdir)
        
        #cd into the individual directory and submit the job
        os.chdir(path_to_onemassdir)
        print "sbatch " + slurmfile
        os.system("sbatch "+slurmfile)
        os.chdir(os.environ['MIST_CODE_DIR'])
    
