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
    
    #Specify solar abundaces, protosolar from Asplund+2009
    solar_h1 = 0.7154
    solar_h2 = 1.43e-5
    solar_he3 = 4.49e-5
    solar_he4 = 0.2702551
    
    solar_x = solar_h1 + solar_h2
    solar_y = solar_he3 + solar_he4
    solar_z = 1.0-solar_x-solar_y
    
    #Input is either Z or [Fe/H]
    if feh == True:
        znew = 10**(znew)*solar_z
    
    #Primordial He abundance and assume linear enrichment to today's solar Y
    yp = 0.249 #from Planck 2015 pol, lensing + external data such as BAO
    
    slope = (solar_y - yp)/solar_z
    ynew = yp + slope*znew
    he3he4_rat = 1.66e-4 #from Jupiter, Mahaffy+1998
    
    #Compute X based on user-provided Z and extrapolated Y
    xnew = 1.0-ynew-znew
    h2h1_rat = 2.0e-5 #from Jupiter & solar wind, Asplund 2009
    
    h1 = xnew/(1.0+h2h1_rat)
    h2 = xnew/(1.0+1.0/h2h1_rat)
    he3 = ynew/(1.0+1.0/he3he4_rat)
    he4 = ynew/(1.0+he3he4_rat)
    znew = znew
    
    h1h2he3he4z_float = [h1, h2, he3, he4, znew]
    h1h2he3he4z = [str(abun) for abun in h1h2he3he4z_float]
    
    return h1h2he3he4z
    
