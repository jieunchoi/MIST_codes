import numpy as np

def trim_file(histfile):
    
    """
    
    Trims the repeated model numbers in MESA history files and rewrites the file.
    
    Args:
        histfile: name of the MESA history file
    
    Returns:
        None
    
    """    
    
    #read in the file
    with open(histfile, 'r') as f1:
        content = f1.readlines()
    
    hdr = content[:6]
    data = content[6:]
    arrdata = np.genfromtxt(histfile, skip_header=5, names=True)
    
    #remove postAGB squiggles
    starmass = arrdata['star_mass']
    if ((starmass[0]<10.0) & (starmass[0]>0.6)):
        ccoremass = arrdata['c_core_mass']
        starage = arrdata['star_age']
        envmass = starmass-ccoremass
        logTeff = arrdata['log_Teff']
        logL = arrdata['log_L']
        logLHe = arrdata['log_LHe']
        
        pagbind_tmp = np.where((starmass-ccoremass)/starmass[0] < 0.15)[0]
        if len(pagbind_tmp) > 0:
            pagbind = np.where((logTeff > logTeff[logLHe[pagbind_tmp[0]]]+0.1) & ((starmass-ccoremass)/starmass[0] < 0.15))[0]
            if len(pagbind) > 0:
                xx = starage[pagbind]-starage[pagbind][0]
                yy = logL[pagbind]
                zz = logTeff[pagbind]
                deriv_logL = (yy[1:]-yy[:-1])/(xx[1:]-xx[:-1])
                deriv_logTeff = (zz[1:]-zz[:-1])/(xx[1:]-xx[:-1])
                badpagb = np.where((abs(deriv_logL) > 0.1)|(abs(deriv_logTeff) > 0.01))[0]
                if len(badpagb > 0):
                    print 'Cutting out bad PAGB scribbles...'                    
                    arrdata = (np.delete(np.array(arrdata), np.array(badpagb)+pagbind[0], 0))
                    data = list(np.delete(np.array(data), np.array(badpagb)+pagbind[0], 0))
            
    #prune repeated model numbers due to backups and retries    
    mn = arrdata['model_number']
    diff_mn = mn[1:]-mn[:-1]
    repeated_mn = np.where(diff_mn != 1)[0] #should be strictly monotonic; keep the newest model number
    
    #remove the bad rows
    cleaned_arrdata = (np.delete(np.array(arrdata), repeated_mn, 0))
    cleaned_data = list(np.delete(np.array(data), repeated_mn, 0))
    cleaned_histfile = histfile
    
    numrow = len(cleaned_data) 
    numhdr = len(hdr)
    with open(cleaned_histfile, 'w') as f2:
        
        for i in range(numhdr):
            f2.write(hdr[i])
            
        for j in range(numrow):
            f2.write(cleaned_data[j])
    