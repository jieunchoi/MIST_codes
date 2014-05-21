import numpy as np

def calc_xyz(znew, feh=False):
    
    solar_h1 = 0.71785675078296
    solar_h2 = 0.0
    solar_he3 = 0.00002673104291
    solar_he4 = 0.26728369805127
    
    #solar values
    solar_x = solar_h1 + solar_h2
    solar_y = solar_he3 + solar_he4
    solar_z = 0.01483282012286
    
    #input either as Z or [Fe/H]
    if feh == True:
        znew = 10**(znew)*solar_z
    
    #primordial He abundance
    yp = 0.2484
    
    slope = (solar_y - yp)/solar_z
    ynew = yp + slope*znew
    he3he4_rat = 1e-4
    
    xnew = 1.0-ynew-znew
    
    h1 = xnew
    h2 = 0.0
    he3 = ynew/(1.0+1.0/he3he4_rat)
    he4 = ynew/(1.0+he3he4_rat)
    znew = znew
    
    h1h2he3he4z = [h1, h2, he3, he4, znew]
    
    return h1h2he3he4z
    