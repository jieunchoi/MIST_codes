"""

A wrapper for Aaron Dotter's fortran routines (https://github.com/dotbot2000/iso) to generate eeps and isochrones
from MESA history files and write MIST and FSPS isochrones.

Args:
    runname: the name of the grid
    
Returns:
    None
    
"""

import glob
import os
import shutil
import subprocess

import make_blend_input_file
import make_iso_input_file

def make_eeps_isos(runname, basic=False, fsps=False):
    
    #Path to the new organized directory
    newdirname = os.path.join(os.environ['MIST_GRID_DIR'],runname)
    
    runname_format = '_'.join(runname.split('/'))
    inputfile = "input."+runname_format
    
    #if basic = True, then only print out a very basic set of columns
    #if basic != True, then print out all of the columns except for things like num_retries, etc.

    #Copy the most recent copy of my_history_columns.list file to the iso directory
    if basic == True:
        shutil.copy(os.path.join(os.environ['MIST_CODE_DIR'], 'mesafiles/my_history_columns_basic.list'), os.path.join(os.environ['ISO_DIR'], 'my_history_columns_basic.list'))
    else:
        shutil.copy(os.path.join(os.environ['MIST_CODE_DIR'], 'mesafiles/my_history_columns_full.list'), os.path.join(os.environ['ISO_DIR'], 'my_history_columns_full.list'))

    #Make the input file for the isochrones code to make eeps
    make_iso_input_file.make_iso_input_file(runname, "eeps", basic)
    
    #cd into the isochrone directory and run the codes
    os.chdir(os.environ['ISO_DIR'])
    os.system("./make_eep " + inputfile)
    
    #Loop through the low and high masses and blend the tracks
    initial_eeps_list_fullname = glob.glob(os.path.join(os.environ['MIST_GRID_DIR'], runname+"/eeps/*.eep"))
    initial_eeps_list = [x.split('eeps/')[1] for x in initial_eeps_list_fullname]
    blend_ind = ['M_' in x for x in initial_eeps_list]
    blend_list = [x for x, y in zip(initial_eeps_list, blend_ind) if y]
    blend_list.sort()
    for i, filename in enumerate(blend_list[::2]):
        os.chdir(os.environ['MIST_CODE_DIR'])
        make_blend_input_file.make_blend_input_file(runname_format, filename, blend_list[i*2+1])
        os.chdir(os.environ['ISO_DIR'])
        os.system("./blend_eeps input.blend_"+ runname_format)
        
    #Make the input file for the isochrones code to make isochrones
    os.chdir(os.environ['MIST_CODE_DIR'])
    make_iso_input_file.make_iso_input_file(runname, "iso", basic)
    
    #Run the isochrone code
    os.chdir(os.environ['ISO_DIR'])
    os.system("./make_iso " + inputfile)

    #Get the path to the home directory for the run (runname)
    with open(inputfile) as f:
        lines=f.readlines()
    tracks_directory = lines[5].replace("\n", "")
    home_run_directory = tracks_directory.split("/tracks")[0]

    #Get the total number of EEPs from input.eep
    #12 lines of header
    with open(os.path.join(os.environ['ISO_DIR'], "input.eep"), "r") as inputf:
        inputeep_data = inputf.readlines()
    #Add 1 to account for the first primary EEP
    lowmass_num_lines = 12 + 1
    intmass_num_lines = 12 + 1
    highmass_num_lines = 12 + 1
    for i_l, line in enumerate(inputeep_data[2:8]):
        #Get the secondary EEP number
        numseceep = int(line.strip('\n').split(' ')[-1])
        #Add one for each primary EEP
        if i_l < 3:
            lowmass_num_lines += numseceep+1
        if i_l < 7:
            highmass_num_lines += numseceep+1 
        intmass_num_lines += numseceep+1

    #Generate a list of incomplete EEPs
    eeps_directory = os.path.join(home_run_directory, "eeps")
    incomplete_eeps_arr = []
    for eepname in glob.glob(eeps_directory + "/*.eep"):
        #Remove the pre-blended EEPs
        if "M_" in eepname:
            os.system("rm -f " + eepname)
            continue        
        #Check the length of each EEP file and identify the ones that are incomplete
        numeeps = int(subprocess.Popen('wc -l '+eepname, stdout=subprocess.PIPE, shell=True).stdout.read().split(' ')[-2])
        mass_val = float(eepname.split('M.track')[0].split('/')[-1])/100.0
        if ((mass_val<=0.7)&(numeeps!=lowmass_num_lines)):
            incomplete_eeps_arr.append(eepname)
        if ((mass_val>0.7)&(mass_val<10.0)&(numeeps!=intmass_num_lines)):
            if ((mass_val>6.0)&(mass_val<10.0)&(numeeps==highmass_num_lines)):
                continue
            else:
                incomplete_eeps_arr.append(eepname)
        if ((mass_val>=10.0)&(numeeps!=highmass_num_lines)):
            incomplete_eeps_arr.append(eepname)

    #Make the input file for the track interpolator consisting of only complete EEP files to interpolate bad EEPs from
    os.chdir(os.environ['MIST_CODE_DIR'])
    min_good_mass, max_good_mass = make_iso_input_file.make_iso_input_file(runname, "interp_eeps", basic, incomplete=incomplete_eeps_arr)
    for incomplete_eeps in incomplete_eeps_arr:
        mass_val = float(incomplete_eeps.split('M.track')[0].split('/')[-1])/100.0
        if (mass_val < min_good_mass) | (mass_val > max_good_mass):
            incomplete_eeps_arr.pop(incomplete_eeps_arr.index(incomplete_eeps))

    #Make the input.track file 
    os.chdir(os.environ['ISO_DIR'])    
    header = ["#input file containing list of EEPs\n", inputfile+"\n", "#number of new tracks to interpolate\n", str(len(incomplete_eeps_arr))+"\n", "#masses and output filenames\n"]
    with open("input.tracks_"+runname_format, "w") as trackinputfile:
        for headerline in header:
            trackinputfile.write(headerline)
        for incomplete_eeps in incomplete_eeps_arr:
            mass_val = float(incomplete_eeps.split('M.track')[0].split('/')[-1])/100.0
            eepline = str(mass_val) + ' ' + incomplete_eeps.split('/')[-1] + "_INTERP\n"
            trackinputfile.write(eepline)

    #Write out a textfile of interpolated EEPs
    incomplete_eeps_arr.sort()
    with open(eeps_directory+"/interpolated_eeps.txt", "w") as list_interp_eeps:
        for incomplete_eeps in incomplete_eeps_arr:
            list_interp_eeps.write(incomplete_eeps+"\n")

    #Interpolate the new tracks
    os.system("./make_track " + "input.tracks_"+runname_format)
    
    #Make the FSPS isochrones
    if fsps==True:
        isoch_directory = os.path.join(home_run_directory, "isochrones")
        isoch_output = glob.glob(isoch_directory + "/*.iso")
        fsps_iso_filename = mist2fsps.write_fsps_iso(isoch_output[0])
        shutil.move(os.path.join(os.environ['ISO_DIR'], fsps_iso_filename), isoch_directory)
    
    
    
    
