#!/usr/bin/env python

"""
This generates the input file to the MIST track blending code
to achieve a smooth transition between the very low mass and
low mass models that use different boundary conditions.
"""

import os
import sys

make_isoch_dir = "/home/jchoi/pfs/iso"
code_dir = "/home/jchoi/pfs/mesawork/MIST_codes"

if __name__ == "__main__":
    
    runname = sys.argv[1]
    file1 = sys.argv[2]
    file2 = sys.argv[3]
    tracks_dir = os.path.join(os.path.join(code_dir,runname), "tracks")
    mass = file1.split('M_')[0]
    blendedfile = mass+'M.track.eep'
    inputfilename = "input.blend_"+runname
    
    content = ["#data directory\n", tracks_dir+"\n", "#number of tracks to blend\n", "2\n", \
    "#names of those tracks; if .eep doesn't exist, then will create them\n", file1+"\n", \
    file2+"\n", "#blend fractions, must sum to 1.0\n", "1.0\n", "1.0\n", "#name of blended track\n", \
    blendedfile]

    with open(inputfilename, "w") as newinputfile:
        for contentline in content:
            newinputfile.write(contentline)
    
    os.system("mv " + inputfilename + " " + make_isoch_dir)
