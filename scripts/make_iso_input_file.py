"""

Generates the input file to the MIST isochrone code.
Use in either the eep or iso mode.

Args:
    runname: the name of the grid
    mode: determine if the the file is to make isochrones or eeps
    
Returns:
    None
    
Example:
    >>> make_iso_input_file('MIST_v0.1', 'eeps')
    
"""

import glob
import os
import numpy as np

def make_iso_input_file(runname, mode, basic, incomplete=[]):
    
    #Convert MIST_vXX/feh_XXX_afe_XXX to MIST_vXX_feh_XXX_afe_XXX
    runname_format = '_'.join(runname.split('/'))

    #Name of the input file
    inputfilename = "input."+runname_format

    #Check if this input file exists already, and if so, remove it.
    if os.path.isfile(os.path.join(os.environ['ISO_DIR'], inputfilename)):
        print "REMOVE OLD ISO INPUT FILE....." + inputfilename
        os.system("rm " + os.path.join(os.environ['ISO_DIR'], inputfilename))

    #Define some paths
    tracks_dir = os.path.join(os.path.join(os.environ['MIST_GRID_DIR'], runname), "tracks")
    eeps_dir = os.path.join(os.path.join(os.environ['MIST_GRID_DIR'], runname), "eeps")
    iso_dir = os.path.join(os.path.join(os.environ['MIST_GRID_DIR'], runname), "isochrones")

    #Get the list of tracks
    if mode == 'eeps':
        tracks_list = sorted(glob.glob(tracks_dir+"/*.track"))
        
    #Generate a list of final track names (i.e., as if low masses have been blended)
    if mode == 'iso':
        initial_tracks_list = glob.glob(eeps_dir+"/*M.track.eep")
        tracks_list = sorted([x.split('.eep')[0] for x in initial_tracks_list])
    
    #Generate a list of track names that are complete only
    if mode == 'interp_eeps':
        initial_tracks_list = glob.glob(eeps_dir+"/*M.track.eep")
        for failed_eep in incomplete:
            failed_eep_ind = np.where(np.array(initial_tracks_list) == failed_eep)[0][0]
            initial_tracks_list.pop(failed_eep_ind)
        tracks_list = sorted([x.split('.eep')[0] for x in initial_tracks_list])
        max_good_mass = float(tracks_list[-1].split('/')[-1].split('M')[0])/100.0
        min_good_mass = float(tracks_list[0].split('/')[-1].split('M')[0])/100.0
        
    #Header and footer in the file
    if basic == True:
        mhc_file = "my_history_columns_basic.list"
        iso_file = runname_format+"_basic.iso\n"
    else:
        mhc_file = "my_history_columns_full.list"
        iso_file = runname_format+"_full.iso\n"
    
    dirname = runname.split('/')[-1]
    dirname_split = dirname.split('_')
    feh = dirname_split[1]
    afe = dirname_split[3]
    vvcrit = dirname_split[4]

    fehval = float(feh[1:])*1.0
    if 'm' in feh:
        fehval *= -1.0
    afeval = float(afe[1:])*1.0
    if 'm' in afe:
        afeval *= -1.0

    with open(os.path.join(os.path.join(os.environ['MIST_GRID_DIR'], runname),'input_XYZ')) as f:
        Xval = float(f.readline())
        Yval = float(f.readline())
        Zval = float(f.readline())
            
    fmt_abun_info = "{:>10.4f}".format(Yval)+"{:>12.5e}".format(Zval)+"{:>7.2f}".format(fehval)+\
        "{:>12.2f}".format(afeval)+"{:>9}".format(vvcrit.split('vvcrit')[-1])+"\n"
    header = ["#version string, max 8 characters\n", "1.0\n", "#initial Y, initial Z, [Fe/H], [alpha/Fe], v/vcrit\n",\
        fmt_abun_info, "#data directories: 1) history files, 2) eeps, 3) isochrones\n", tracks_dir+"\n", eeps_dir+"\n", iso_dir+"\n", \
        "# read history_columns\n", os.path.join(os.environ['ISO_DIR'], mhc_file)+"\n", "# specify tracks\n", str(len(tracks_list))+"\n"]
    footer = ["#specify isochrones\n", iso_file, "min_max\n", "log10\n", "107\n", "5.0\n", "10.3\n", "single\n"]

    #Write the file
    print "**************************************************************************"
    print "WRITE NEW ISO INPUT FILE..... "+os.environ['ISO_DIR']+"/"+inputfilename
    print "**************************************************************************"
    with open(inputfilename, "w") as newinputfile:
        for headerline in header:
            newinputfile.write(headerline)
        for full_trackname in tracks_list:
            trackname = full_trackname.split("/")[-1]
            newinputfile.write(trackname+"\n")
        for footerline in footer:
            newinputfile.write(footerline)
    
    os.system("mv " + inputfilename + " " + os.environ['ISO_DIR'])

    #Used to check which masses can/can't be interpolated in mesa2fsps.py
    if mode == 'interp_eeps':
        return min_good_mass, max_good_mass
