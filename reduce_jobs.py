#!/usr/bin/env python

"""

Takes MESA grids to create isochrones and organizes all the output files
into a nice directory structure.

The directory structure is as follows:
    top level directory --> MIST_vXX/FIDUCIAL/feh_pX.X_afe_pX.X/
    five subdirectories --> tracks/    eeps/    inlists/    isochrones/    plots/

Args:
    runname: the name of the grid

Keywords:
    doplot: if True, generates plots of EEPs and isochrones

"""

import os
import sys
import subprocess
import glob

from scripts import mesa_plot_grid
from scripts import make_eeps_isos
from scripts import mesa_hist_trim
from scripts import reduce_jobs_utils
    
if __name__ == "__main__":
    
    #Digest the inputs
    if len(sys.argv) == 2:
        runname = sys.argv[1]
        redo = False
        doplot = False
        dobotheeps = False        
    elif ((len(sys.argv) < 2) or (len(sys.argv) != 5)):
        print "Usage: ./reduce_jobs name_of_grid redo* doplot* dobotheeps*"
        print "* redo, doplot, and dobotheeps are optional, but all three must be set at the same time. They default to False."
        sys.exit(0)
    else:
        runname = sys.argv[1]
        redo = sys.argv[2]
        doplot = sys.argv[3]
        dobotheeps = sys.argv[4]
    
    #Rename the run directory XXX as XXX_raw
    rawdirname = runname+"_raw"

    #The XXX directory will contain the organized, reduced information
    newdirname = os.path.join(os.environ['MIST_GRID_DIR'],runname)

    #If the redo flag is set, it will assume that the tracks have been processed and the EEPs/isochrones
    #are ready to be made.
    if not redo:
        
        #Renaming and making the relevant directories
        os.system("mv " + os.path.join(os.environ['MIST_GRID_DIR'],runname) + " " + \
        os.path.join(os.environ['MIST_GRID_DIR'],rawdirname))
        
        os.mkdir(newdirname)
    
        #Make the eeps directory that will be filled in later
        os.mkdir(os.path.join(newdirname, "eeps"))
    
        #Make the isochrones directory that will be filled in later
        os.mkdir(os.path.join(newdirname, "isochrones"))

        print "************************************************************"
        print "****************SORTING THE HISTORY FILES*******************"
        print "************************************************************"
        reduce_jobs_utils.sort_histfiles(rawdirname)
        
        print "************************************************************"
        print "****************GENERATING A SUMMARY FILE*******************"
        print "************************************************************"
        reduce_jobs_utils.gen_summary(rawdirname)
        
        #Copy the summary file
        os.system("mv tracks_summary.txt " + newdirname)
    
        print "************************************************************"
        print "****************SAVING THE ABUNDANCES FILE******************"
        print "************************************************************"
        abunfile = glob.glob(os.path.join(os.path.join(os.environ['MIST_GRID_DIR'],rawdirname),'*dir/input_initial_xa.data'))[0]
        xyzfile = glob.glob(os.path.join(os.path.join(os.environ['MIST_GRID_DIR'],rawdirname),'*dir/input_XYZ'))[0]
        os.system("cp " + abunfile + " " + newdirname)
        os.system("cp " + xyzfile + " " + newdirname) 
        
        print "************************************************************"
        print "****************SORTING THE INLIST FILES********************"
        print "************************************************************"
        reduce_jobs_utils.save_inlists(rawdirname)
        
        print "************************************************************"
        print "***************SORTING THE PHOTOS AND MODELS****************"
        print "************************************************************"
        reduce_jobs_utils.save_lowM_photo_model(rawdirname)
    
    print "************************************************************"
    print "**********************MAKE ISOCHRONES***********************"
    print "************************************************************"
    make_eeps_isos.make_eeps_isos(runname, basic=False)
    if dobotheeps:
        make_eeps_isos.make_eeps_isos(runname, basic=True)

    if doplot:
        print "************************************************************"
        print "******************PLOTTING THE EEPS FILES*******************"
        print "************************************************************"
        os.mkdir(os.path.join(newdirname, "plots"))
        mesa_plot_grid.plot_HRD(runname)
        mesa_plot_grid.plot_combine(runname, iso=False, remove_pdf=False)
        
        print "************************************************************"
        print "******************PLOTTING THE ISOCHRONES*******************"
        print "************************************************************"
        mesa_plot_grid.plot_iso(runname)
        mesa_plot_grid.plot_combine(runname, iso=True, remove_pdf=False)
    
    print "************************************************************"
    print "******COMPRESSING BOTH TRACKS AND REDUCED DIRECTORIES*******"
    print "************************************************************"
    #make a separate tracks directory
    os.system("mv " + os.path.join(newdirname, "tracks") + " " + newdirname + "_tracks")
    os.system("cp " + os.path.join(newdirname, "tracks_summary.txt") + " " + newdirname + "_tracks")

    os.chdir(os.environ['MIST_GRID_DIR'])    
    #When decompressed, this .tar.gz opens a MIST_vXX/feh_XXX_afe_XXX directory
    os.system("tar -zcvf " + '_'.join(runname.split('/')) + ".tar.gz " + runname)
    os.system("tar -zcvf " + '_'.join(runname.split('/')) + "_tracks.tar.gz " + runname+'_tracks')
    
    print "************************************************************"
    print "****************MIGRATING FILES TO STORAGE******************"
    print "************************************************************"
    os.system("rm -rf " + runname)
    os.system("rm -rf " + runname + '_tracks')
    os.system("mv " + rawdirname + " " + os.path.join(os.environ['STORE_DIR'], runname.split('/')[0]))
    os.system("mv " + '_'.join(runname.split('/')) + ".tar.gz " + os.path.join(os.environ['STORE_DIR'], runname.split('/')[0]))
    os.system("mv " + '_'.join(runname.split('/')) + "_tracks.tar.gz " + os.path.join(os.environ['STORE_DIR'], runname.split('/')[0]))

