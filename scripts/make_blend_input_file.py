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
    >>> make_blend_input_file('MIST_v1.0_feh_p0.00_afe_p0.0_vvcrit0.4', '00030M_tau100.track', '00030M_PT.track')
    
"""

import math
import os
import numpy as np

def make_blend_input_file(runname, file1, file2):

    #Convert MIST_vXX_feh_XXX_afe_XXX back to MIST_vXX/feh_XXX_afe_XXX
    runname_original = runname.split('_feh')[0]+'/feh'+runname.split('feh')[1]

    #Generate the name of the input file for the blending code
    eeps_dir = os.path.join(os.path.join(os.environ['MIST_GRID_DIR'], runname_original), "eeps")
    mass = file1.split('M')[0]
    float_mass = float(mass)/100.0

    blendedfile = mass+'M.track.eep'
    inputfilename = "input.blend_"+runname
    
    #The blending mass range goes from >0.3 to <0.6 or >10 to <16
    if float_mass < 5.0:
        min_blend = 0.3
        max_blend = 0.6
        frac = (float_mass - min_blend)/(max_blend - min_blend)
        blendfrac_BC1 = 0.5*(1.0 - np.cos(math.pi*frac))
        blendfrac_BC2 = 1.0 - blendfrac_BC1
    elif float_mass >= 5.0:
        min_blend = 10.0
        max_blend = 16.0
        frac = (float_mass - min_blend)/(max_blend - min_blend)
        blendfrac_BC2 = 0.5*(1.0 - np.cos(math.pi*frac))
        blendfrac_BC1 = 1.0 - blendfrac_BC2
    
    #Write out the contents of the file
    content = ["#data directory\n", eeps_dir+"\n", "#number of tracks to blend\n", "2\n", \
    "#names of those tracks; if .eep doesn't exist, then will create them\n", file1.split('.eep')[0]+"\n", \
    file2.split('.eep')[0]+"\n", "#blend fractions, must sum to 1.0\n", str(blendfrac_BC1)+"\n", \
    str(blendfrac_BC2)+"\n", "#name of blended track\n", blendedfile]

    with open(inputfilename, "w") as newinputfile:
        for contentline in content:
            newinputfile.write(contentline)
    
    os.system("mv " + inputfilename + " " + os.environ['ISO_DIR'])
    
