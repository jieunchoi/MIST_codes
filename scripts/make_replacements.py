"""

Replaces various 'keys' (such as mass) in the 
template inlist with corresponding values for each model.

Args:
    replist: list of keys and values
    name_str: name of the new inlist

Keywords:
    direc: directory where the new inlist is stored
    file_base: template inlist file
    clear_direc: clear the directory if there are existing files

Returns: 
    None

See Also:
    make_inlist_inputs: generates replist
    
Example:
    >>> make_replacements(make_inlist_inputs(runname, 'VeryLow'), '10M.inlist',\
        direc='/home/project/inlist', file_base='inlist_project_base', clear_direc=True)
        
Acknowledgment: 
    Thanks to Joshua Burkart for providing assistance with and content for earlier versions of this code.
        
"""

import numpy as np
import os

import reformat_massname

def make_replacements(replist, name_str, direc='inlists', file_base='inlist_project_template', clear_direc=False):
    
    #Make sure that the template inlist exists
    if not os.path.isfile(file_base):
        raise Exception("Template inlist file does not exist!")
    
    #Make sure that the inlist directory exists
    if not os.path.isdir(direc):
        os.mkdir(direc)
    
    #Remove existing files in the directory if clear_direc=True
    elif clear_direc and not os.path.abspath(direc) == os.path.abspath('.'):
        print "Removing existing files in " + direc
        for file in os.listdir(direc):
            os.remove(os.path.join(direc, file))
    
    #Separate the keys from values
    keys = [replist[i][0] for i in xrange(len(replist))]
    vals = [replist[i][1] for i in xrange(len(replist))]

    numkey = np.shape(vals)[0]
    nummass = np.shape(vals)[1]
    perms = []
    
    #Generate a list of combinations
    for i in range(nummass):
        combo = tuple(vals[j][i] for j in range(numkey))
        perms.append(combo)
    
    #Read in the template file
    infile = open(file_base, 'r')
    file_base_contents = infile.read()
    infile.close()
    
    #Replace the keys with values and save to a new inlist
    for val_vec in perms:
        file_mod = file_base_contents
        inlist_file = name_str
        for i in xrange(numkey):
            file_mod = file_mod.replace(keys[i], str(val_vec[i]))
            
            #For mass, change the decimal value to a uniform-length string
            #e.g., 0.5 becomes 00500            
            if keys[i] == "<<MASS>>":
                inlist_file = inlist_file.replace(keys[i], reformat_massname.reformat_massname(val_vec[i]))
            else:
                inlist_file = inlist_file.replace(keys[i], str(val_vec[i]))
        
        inlist_file = os.path.join(direc, inlist_file)
        
        outfile = open(inlist_file, 'w')
        outfile.write(file_mod)
        outfile.close()
	
