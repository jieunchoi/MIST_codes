"""
This code transforms MIST isochrone output file and
converts to an FSPS isochrone output format.
"""

import numpy as np

def read_mist(file):
    #read header info and isochrone tables

    with open(file) as f:
        data = f.readlines()
        header = data[0:3]
        print '------------------------------------------------------------'
        print header[0].split('\n')[0]
        print header[1].split('\n')[0]
        print header[2].split('\n')[0]
        print '------------------------------------------------------------'
    
    #read the column names to identify the data columns by names
    colname_string1 = data[4]
    colname_string2 = colname_string1.replace("\n", "")
    colname_string3 = colname_string2.replace("#", "")
    colname_list = colname_string3.split()
    
    #read in the actual data as an array
    data = np.genfromtxt(file)

    return data, colname_list

def write_fsps_iso(file):
    
    fsps_col_names = '# log(age)     Mini          Mact          logl          logt          logg      Composition      Phase         Mdot'

    data, mist_col_names = read_mist(file)
    numcol = np.shape(data)[1]
    numrow = np.shape(data)[0]
    
    #format specifications
    fmt = "{:8.2f}{:14.8f}{:14.8f}{:14.8f}{:14.8f}{:14.8f}{:14.8f}{:14.8f}{:14.5e}"
    
    #identify columns to go into fsps isochrone file
    log_age = data[:, mist_col_names.index('log_age')].T    
    mini = data[:, mist_col_names.index('initial_mass')].T
    mact = data[:, mist_col_names.index('star_mass')].T
    log_L = data[:, mist_col_names.index('log_L')].T
    log_t = data[:, mist_col_names.index('log_Teff')].T
    log_g = data[:, mist_col_names.index('log_g')].T
    co_rat = data[:, mist_col_names.index('surf_num_c12_div_num_o16')].T
    phase = data[:, mist_col_names.index('phase')].T
    mdot = data[:, mist_col_names.index('star_mdot')].T
    
    #set up the file to write to  
    runname = file.rstrip('.iso').split("/")[-1]
    fsps_iso_filename = "isoc_"+runname+".dat"
    with open(fsps_iso_filename, 'w') as f: 
        for i in range(numrow):
            row = [log_age[i], mini[i], mact[i], log_L[i], log_t[i], log_g[i], co_rat[i], phase[i], mdot[i]]
            fmt_row = fmt.format(*row)
            
            #write the column names every time we move to a new age (different isochrone file)
            if log_age[i-1] != log_age[i]:
                f.write(fsps_col_names+"\n")
            
            #write the row!    
            f.write(fmt_row+"\n")
    
    return fsps_iso_filename
    
    
    
    
    
    
    

    

        

        
	
