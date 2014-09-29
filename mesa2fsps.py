"""

A wrapper for various routines to generate eeps and isochrones
from MESA history files and write MIST and FSPS isochrones.

Args:
    runname: the name of the grid
    
Returns:
    None
    
"""

import glob
import os
import sys
import shutil
import mist2fsps
from make_blend_input_file import make_blend_input_file
from make_iso_input_file import make_iso_input_file

work_dir = os.environ['MESAWORK_DIR']
make_isoch_dir = os.environ['ISO_DIR']
code_dir = os.environ['MIST_CODE_DIR']

def mesa2fsps(runname):
    
    #Path to the new organzed directory
    newdirname = os.path.join(work_dir,runname)

    runname_format = '_'.join(runname.split('/'))
    inputfile = "input."+runname_format

    #Make the input file for the isochrones code to make eeps
    make_iso_input_file(runname, "eeps")

    #Copy the most recent copy of my_history_columns.list file to the iso directory
    shutil.copy(os.path.join(code_dir, 'my_history_columns.list'), os.path.join(make_isoch_dir, 'my_history_columns.list'))

    #cd into the isochrone directory and run the codes
    os.chdir(make_isoch_dir)
    os.system("./make_eeps " + inputfile)
    
    #Loop through the low masses and blend the tracks
    initial_eeps_list_fullname = glob.glob(os.path.join(work_dir, runname+"/eeps/*.eep"))
    initial_eeps_list = [x.split('eeps/')[1] for x in initial_eeps_list_fullname]
    blend_ind = ['M_' in x for x in initial_eeps_list]
    blend_list = [x for x, y in zip(initial_eeps_list, blend_ind) if y]
    blend_list.sort()
    for i, filename in enumerate(blend_list[::2]):
        os.chdir(code_dir)
        make_blend_input_file(runname_format, filename, blend_list[i*2+1])
        os.chdir(make_isoch_dir)
        os.system("./blend_eeps input.blend_"+ runname_format)
        
    #Make the input file for the isochrones code to make isochrones
    os.chdir(code_dir)
    make_iso_input_file(runname, "iso")
    
    #Run the isochrone code
    os.chdir(make_isoch_dir)
    os.system("./make_iso " + inputfile)
    
    #Get the path to the home directory for the run (runname)
    with open(inputfile) as f:
        lines=f.readlines()
    tracks_directory = lines[1].replace("\n", "")
    home_run_directory = tracks_directory.split("/tracks")[0]

    #Move the eeps to the eeps directory and rename them
    eeps_directory = os.path.join(home_run_directory, "eeps")
    for data in glob.glob(eeps_directory + "/*.eep"):
        newname = data.replace(".track","")
            
    #Make the FSPS isochrones
    isoch_directory = os.path.join(home_run_directory, "isochrones")
    isoch_output = glob.glob(isoch_directory + "/*.iso")
    fsps_iso_filename = mist2fsps.write_fsps_iso(isoch_output[0])

    shutil.move(os.path.join(make_isoch_dir, fsps_iso_filename), isoch_directory)
    
    
    
    
