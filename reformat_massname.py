"""
This simply replaces an integer mass with
a formatted mass string.
"""

import numpy as np

def reformat_massname(mass):

    floatmass = float(mass)
    format_mass = str(int(round(floatmass*100)))
    
    zero = '0'
    if len(format_mass) < 5:
        while len(format_mass) < 5:
            format_mass = zero + format_mass

    return format_mass
    
