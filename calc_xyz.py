"""

Computes H1, H2, He3, He4 (and Z) given an arbitrary Z or Fe/H.
Assumes Asplund+2009 solar abundances and Y_bbn = 0.2484

Args:
    znew: the new mass fraction in metals

Keywords:
    feh: option to provide [Fe/H] instead of Z

Returns: 
    list of ['H1', 'H2', 'He3', 'He4', 'Z']
    
Example:
    >>> calc_xyz(-1.0, feh=True)
    >>> calc_xyz(0.015)
    
"""

import numpy as np

def calc_xyz(znew, feh=False):
    
    #Specify solar abundaces
    solar_h1 = 0.71785675078296
    solar_h2 = 0.0
    solar_he3 = 0.00002673104291
    solar_he4 = 0.26728369805127
    
    solar_x = solar_h1 + solar_h2
    solar_y = solar_he3 + solar_he4
    solar_z = 0.01483282012286
    
    #Input is either Z or [Fe/H]
    if feh == True:
        znew = 10**(znew)*solar_z
    
    #Primordial He abundance and assume linear enrichment to today's solar Y
    yp = 0.2484
    
    slope = (solar_y - yp)/solar_z
    ynew = yp + slope*znew
    he3he4_rat = 1e-4
    
    #Compute X based on user-provided Z and extrapolated Y
    xnew = 1.0-ynew-znew
    
    h1 = xnew
    h2 = 0.0
    he3 = ynew/(1.0+1.0/he3he4_rat)
    he4 = ynew/(1.0+he3he4_rat)
    znew = znew
    
    h1h2he3he4z_float = [h1, h2, he3, he4, znew]
    h1h2he3he4z = [str(abun) for abun in h1h2he3he4z_float]
    
    return h1h2he3he4z
    