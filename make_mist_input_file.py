#!/usr/bin/env python

"""
This generates the input file to the MIST isochrone code.
It can be used in either the eep or iso mode.
"""

import glob
import re
import os
import sys

make_isoch_dir = "/home/jchoi/pfs/iso"
code_dir = "/home/jchoi/pfs/mesawork/MIST_codes"

if __name__ == "__main__":

    #name, i.e. feh_p0.0_afe_p0.0_rot
    runname=sys.argv[1]
    inputfilename = "input."+runname

    #need to know if we need the file to make isochrones or eeps
    mode = sys.argv[2]

    #if the file exists already then remove it
    if os.path.isfile(os.path.join(make_isoch_dir, inputfilename)):
        print "removing old input file................" + inputfilename
        os.system("rm " + os.path.join(make_isoch_dir, inputfilename))

    tracks_dir = os.path.join(os.path.join(code_dir, runname), "tracks")
    eeps_dir = os.path.join(os.path.join(code_dir, runname), "eeps")
    iso_dir = os.path.join(os.path.join(code_dir, runname), "isochrones")

    #get the list of tracks
    if mode == 'eeps':
        tracks_list = sorted(glob.glob(tracks_dir+"/*.track"))
    #generate a fake set of final track names (low masses have been blended) to generate a new input file
    if mode == 'iso':
        initial_tracks_list = glob.glob(tracks_dir+"/*.track")
        good_names = ['M_' not in x for x in initial_tracks_list]
        bad_names = ['M_' in x for x in initial_tracks_list]
        good_names_list = [x for x, y in zip(initial_tracks_list, good_names) if y]
        bad_names_list = [x for x, y in zip(initial_tracks_list, bad_names) if y]

        fake_names_list = list(set([x.split('M_')[0]+'M.track' for x in bad_names_list]))
        tracks_list = sorted(good_names_list+fake_names_list)
        
    #header and footer in the file
    hdr = ["#data directories: 1) history files, 2) eeps, 3) isochrones\n", tracks_dir+"\n", eeps_dir+"\n", iso_dir+"\n", \
    "# read history_columns\n", os.path.join(make_isoch_dir, "my_history_columns.list")+"\n", "# specify tracks\n", str(len(tracks_list))+"\n"]

    footer = ["#specify isochrones\n", runname+".iso\n", "min_max\n", "51\n", "5.0\n", "10.3\n", "single\n"]

    print make_isoch_dir+"/"+inputfilename
    with open(inputfilename, "w") as newinputfile:
        for hdrline in hdr:
            newinputfile.write(hdrline)
        for full_trackname in tracks_list:
            trackname = full_trackname.split("/tracks/")[-1]
            newinputfile.write(trackname+"\n")
        for footerline in footer:
            newinputfile.write(footerline)
    
    os.system("mv " + inputfilename + " " + make_isoch_dir)
