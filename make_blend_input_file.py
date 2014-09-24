"""

Generates the input file to the MIST track blending code
to achieve a smooth transition between the very low mass and
low mass models that use different boundary conditions.

Args:
    runname: the name of the grid
    file1: the name of one of the file to be blended
    file2: the name of the other file to be blended
    
Returns:
    None
    
Example:
    >>> make_blend_input_file('MIST_v0.1', '00030M_tau100.track', '00030M_PT.track')
    
"""

import os
import sys

make_isoch_dir = os.environ['ISO_DIR']
code_dir = os.environ['MIST_CODE_DIR']

def make_blend_input_file(runname, file1, file2):

    #Generate the name of the input file for the blending code
    tracks_dir = os.path.join(os.path.join(code_dir,runname), "tracks")
    mass = file1.split('M_')[0]
    blendedfile = mass+'M.track.eep'
    inputfilename = "input.blend_"+runname
    
    #The blending mass range goes from 0.3 to 0.6, inclusive, +0.01 is there for transition purposes
    blendfrac_PT = min(((float(mass) - 0.3)/(0.6-0.3))+0.01, 1.0)
    blendfrac_tau100 = 1.0 - blendfrac_PT
    
    #Write out the contents of the file
    content = ["#data directory\n", tracks_dir+"\n", "#number of tracks to blend\n", "2\n", \
    "#names of those tracks; if .eep doesn't exist, then will create them\n", file1+"\n", \
    file2+"\n", "#blend fractions, must sum to 1.0\n", str(blendfrac_PT)+"\n", \
    str(blendfrac_tau100)+"\n", "#name of blended track\n", blendedfile]

    with open(inputfilename, "w") as newinputfile:
        for contentline in content:
            newinputfile.write(contentline)
    
    os.system("mv " + inputfilename + " " + make_isoch_dir)
    