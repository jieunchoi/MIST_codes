#!/usr/bin/env python 

"""
This generates EEP files from MESA history files, then
generates MIST and FSPS isochrones.
"""

import glob
import mist2fsps
import os
import sys
import shutil

make_isoch_dir = "/home/jchoi/pfs/make_isoch"
code_dir = "/home/jchoi/pfs/mesawork/codes"

if __name__ == "__main__":
    
    inputfile = sys.argv[1]
    runname = inputfile.split("input.")[1]

    print "************************************************************"
    print "***************MAKING NEW INPUT FILE FOR EEPS***************"
    print "************************************************************"
    #input file for the isochrones code to make eeps
    os.system("./make_mist_input_file.py " + runname + " eeps")
    
    print "************************************************************"
    print "********************MAKING EEPS FILES***********************"
    print "************************************************************"
    #get to the isochrone directory and run the codes
    os.chdir(make_isoch_dir)
    os.system("more " + inputfile)
    os.system("./make_eeps " + inputfile)
    
    print "************************************************************"
    print "******************BLEND THE LOW MASS TRACKS*****************"
    print "************************************************************"
    #loop through the low masses
    initial_eeps_list_fullname = glob.glob(os.path.join(code_dir, runname+"/tracks/*.eep"))
    initial_eeps_list = [x.split('tracks/')[1] for x in initial_eeps_list_fullname]
    blend_ind = ['M_' in x for x in initial_eeps_list]
    blend_list = [x for x, y in zip(initial_eeps_list, blend_ind) if y]
    blend_list.sort()
    for i, filename in enumerate(blend_list[::2]):
        os.chdir(code_dir)
        os.system("./make_blend_input_file.py " + runname + " " + filename +  " " + blend_list[i*2+1])
        os.chdir(make_isoch_dir)
        os.system("./blend_eeps input.blend_"+ runname)
        
    print "************************************************************"
    print "***************MAKING NEW INPUT FILE FOR ISO***************"
    print "************************************************************"
    #input file for the isochrones code to make isochrones, just rewrite the old
    os.chdir(code_dir)
    os.system("./make_mist_input_file.py " + runname + " iso")
    
    print "************************************************************"
    print "********************MAKING ISOCHRONES***********************"
    print "************************************************************"
    os.chdir(make_isoch_dir)
    os.system("./make_iso " + inputfile)
    
    #get the address to the home directory for the run
    with open(inputfile) as f:
        lines=f.readlines()
    tracks_directory = lines[1].replace("\n", "")
    home_run_directory = tracks_directory.split("/tracks")[0]

    print "************************************************************"
    print "*********************MOVING THE EEPS************************"
    print "************************************************************"    
    #move the eeps to the eeps directory
    eeps_directory = os.path.join(home_run_directory, "eeps")
    for data in glob.glob(tracks_directory + "/*.eep"):
        newname = data.replace(".track","")
        os.system("mv " + data + " " + newname)
        try:
            shutil.move(newname, eeps_directory)
        except shutil.Error:
            del_or_no = raw_input(newname + " already exists in " + eeps_directory + \
            ". Delete? (1 or 0):  ")
            if del_or_no == '1':
                print "Deleting the old file..."
                os.remove(os.path.join(eeps_directory, newname.split("tracks/")[1]))
                shutil.move(newname, eeps_directory)
            elif del_or_no == '0':
                print "Never mind."
                pass
            else:
                print "Invalid input!"
                pass
            
    print "************************************************************"
    print "****************MOVING THE MIST ISOCHRONES******************"
    print "************************************************************"
    #move the MIST isochrone into the isochrones directory
    isoch_directory = os.path.join(home_run_directory, "isochrones")
    for data in glob.glob(tracks_directory + "/*.iso"):
        try:
            shutil.move(data, isoch_directory)
        except shutil.Error:
            del_or_no = raw_input(data+ " already exists in " + isoch_directory + \
            ". Delete? (1 or 0):  ")
            if del_or_no == '1':
                print "Deleting the old file..."
                os.remove(os.path.join(isoch_directory, file.split("tracks/")[1]))
                shutil.move(data, isoch_directory)
            elif del_or_no == '0':
                print "Never mind."
                pass
            else:
                print "Invalid input!"
                pass
            
    print "************************************************************"
    print "****************MAKING THE FSPS ISOCHRONES******************"
    print "************************************************************"
    #run the mist2fsps routine
    isoch_output = glob.glob(isoch_directory + "/*.iso")
    fsps_iso_filename = mist2fsps.write_fsps_iso(isoch_output[0])

    try:
        shutil.move(os.path.join(make_isoch_dir, fsps_iso_filename), isoch_directory)
    except shutil.Error:
        del_or_no = raw_input(fsps_iso_filename + " already exists in " + isoch_directory + \
        ". Delete? (1 or 0):  ")
        if del_or_no == '1':
            print "Deleting the old file..."
            os.remove(os.path.join(isoch_directory, fsps_iso_filename))
            shutil.move(os.path.join(make_isoch_dir, fsps_iso_filename), isoch_directory)
        elif del_or_no == '0':
            print "Never mind."
            pass
        else:
            print "Invalid input!"
            pass

    
    
    
    
