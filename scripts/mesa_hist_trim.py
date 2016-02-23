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
    
    #prune repeated model numbers due to backups and retries
    arrdata = np.genfromtxt(histfile, skip_header=5, names=True)
    mn = arrdata['model_number']
    diff_mn = mn[1:]-mn[:-1]
    repeated_mn = np.where(diff_mn != 1)[0] #should be strictly monotonic; keep the newest model number
    
    #remove the bad rows
    cleaned_data = list(np.delete(np.array(data), repeated_mn, 0))
    numrow = len(cleaned_data) 
    numhdr = len(hdr)
    
    cleaned_histfile = histfile
    with open(cleaned_histfile, 'w') as f2:
        
        for i in range(numhdr):
            f2.write(hdr[i])
            
        for j in range(numrow):
            f2.write(cleaned_data[j])
    