"""

Computes H1, H2, He3, He4 (and Z) given an arbitrary [Fe/H] or Z.
Assumes Asplund+2009 solar abundances and Y_bbn = 0.249

Args:
    input_met: desired metallicity in Z or [Fe/H]

Keywords:
    input_feh: option to provide [Fe/H] instead of Z

Returns: 
    list of ['H1', 'H2', 'He3', 'He4', 'Z']
    
Example:
    >>> calc_xyz(-1.0, input_feh=True)
    >>> calc_xyz(0.015)
    
"""

import numpy as np

def calc_xyz(input_met, input_feh=True):
    
    #Specify solar abundaces, protosolar from Asplund+2009
    proto_h1 = 0.7154
    proto_h2 = 1.43e-5
    proto_he3 = 4.49e-5
    proto_he4 = 0.2702551
    
    proto_x = proto_h1+proto_h2
    proto_y = proto_he3+proto_he4
    proto_z = 1.0-proto_x-proto_y

    #Primordial He abundance and assume linear enrichment to today's solar Y
    bbn_y = 0.249 #from Planck 2015 pol, lensing + external data such as BAO

    #Compute the protosolar log(Z/X) and dY_dZ
    proto_log_z_div_x = np.log10(proto_z/proto_x)
    slope = (proto_y-bbn_y)/proto_z

    #For solar-scaled abundances,
    #[Fe/H] = log10(Fe/H) - log10(Fe/H)SUN
    #[Fe/H] = log10(Z/X) - log10(Z/X)SUN
    if input_feh == True:
        feh = input_met
        new_z_div_x = 10.0**(feh+proto_log_z_div_x)
        top = 1.0-bbn_y
        bottom = 1.0+new_z_div_x*(1.0+slope)
        
        #Obtain new X, Y, Z values
        xnew = top/bottom
        znew = new_z_div_x*xnew
        ynew = 1.0-xnew-znew

    if input_feh == False:
        znew = input_met
        new_z_div_x = znew/((1.0-bbn_y)-znew*(1.0+slope))
        
        xnew = znew/new_z_div_x
        ynew = 1.0-xnew-znew
        
    h2h1_rat = 2.0e-5 #from Jupiter & solar wind, Asplund 2009
    he3he4_rat = 1.66e-4 #from Jupiter, Mahaffy+1998
    
    h1 = xnew/(1.0+h2h1_rat)
    h2 = xnew/(1.0+1.0/h2h1_rat)
    he3 = ynew/(1.0+1.0/he3he4_rat)
    he4 = ynew/(1.0+he3he4_rat)
    
    h1h2he3he4z_float = [h1, h2, he3, he4, znew]
    h1h2he3he4z = [str(abun) for abun in h1h2he3he4z_float]

    return h1h2he3he4z
    
