"""

Outputs a formatted mass string given an float mass.

Args:
    mass: mass in floats or integers
    
Returns:
    mass in a formatted string that is 5 characters in length
    
Example:
    >>> format_mass = reformat_massname(0.5)
    >>> print format_mass
    >>> '00050'

"""

def reformat_massname(mass):

    floatmass = float(mass)
    format_mass = str(int(round(floatmass*100)))
    
    #Add extras zeros to make the length of the string equal to 5
    zero = '0'
    if len(format_mass) < 5:
        while len(format_mass) < 5:
            format_mass = zero + format_mass

    return format_mass
    
