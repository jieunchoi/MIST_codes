import numpy as np

def read_mist(file):
    
    """
    
    Reads in the contents of the MIST isochrone output file.
    
    Args:
        file: name of the MIST isochrone file
    
    Returns:
        data: the isochrone tables
        colname_list: the names of the columns
    
    """    
    
    #Read header info
    with open(file) as f:
        data = f.readlines()
    header = data[:11]
    print '------------------------------------------------------------'
    print file
    print '------------------------------------------------------------'
    
    #Read the column names
    colname_string1 = data[10]
    colname_string2 = colname_string1.replace("\n", "")
    colname_string3 = colname_string2.replace("#", "")
    colname_list = colname_string3.split()
    
    #Read in the actual data as an array
    data = np.genfromtxt(file)

    return data, colname_list

def write_fsps_iso(file, logage=False):
    
    """
    
    Translates MIST isochrone output file to an FSPS isochrone output.
    
    Args:
        file: name of the MIST isochrone file
    
    Keywords:
        logage: specify the age format in the MIST file. FSPS assumes logage.
    
    Returns:
        name of the FSPS isochrone file
    
    """    
    
    #Specify the column names for FSPS isochrones
    fsps_col_names = '# log(age)     Mini          Mact          logl          logt          logg      Composition      Phase         logMdot'

    data, mist_col_names = read_mist(file)
    numcol = np.shape(data)[1]
    numrow = np.shape(data)[0]
    
    #Format specifications
    fmt = "{:8.3f}{:14.8f}{:14.8f}{:14.8f}{:14.8f}{:14.8f}{:14.8f}{:14.8f}{:14.5e}"
    
    #Identify columns
    if logage == True:
        log_age = data[:, mist_col_names.index('log10_isochrone_age_yr')].T
    else:
        log_age = np.log10(data[:, mist_col_names.index('isochrone_age_yr')].T)
    mini = data[:, mist_col_names.index('initial_mass')].T
    mact = data[:, mist_col_names.index('star_mass')].T
    log_L = data[:, mist_col_names.index('log_L')].T
    log_t = data[:, mist_col_names.index('log_Teff')].T
    log_g = data[:, mist_col_names.index('log_g')].T
    co_rat = data[:, mist_col_names.index('surf_num_c12_div_num_o16')].T
    phase = data[:, mist_col_names.index('phase')].T
    mdot = data[:, mist_col_names.index('star_mdot')].T
    h1 = data[:,mist_col_names.index('surface_h1')].T
    cn_rat = ((data[:,mist_col_names.index('surface_c12')].T/12.0) + (data[:,mist_col_names.index('surface_c13')].T/13.0))/(data[:,mist_col_names.index('surface_n14')].T/14.0)
    
    #use co ratio column and use dummy values to distinguish between WC/WO or WN
    WCind = np.where((phase == 9) & (cn_rat > 1.0))
    co_rat[WCind] = 99
    WNind = np.where((phase == 9) & (cn_rat <= 1.0))
    co_rat[WNind] = 9
    
    #Set up the file to write to  
    runname = file.rstrip('.iso').split("/")[-1]
    fsps_iso_filename = "isoc_"+runname+".dat"
    
    with open(fsps_iso_filename, 'w') as f: 
        for i in range(numrow):
            row = [log_age[i], mini[i], mact[i], log_L[i], log_t[i], log_g[i], co_rat[i], phase[i], np.log10(abs(mdot[i]))]
            fmt_row = fmt.format(*row)
            
            #Print column names every time the age changes
            if log_age[i-1] != log_age[i]:
                f.write(fsps_col_names+"\n")
            
            f.write(fmt_row+"\n")
    
    return fsps_iso_filename
    
    
    
    
    
    
    

    

        

        
	
