import glob
import os
import csv
import subprocess
from datetime import datetime

from scripts import mesa_hist_trim
from scripts import reformat_massname

def gen_summary(rawdirname):
    
    """

    Retrieves various information about the MESA run and writes to a summary file

    Args:
        rawdirname: the name of the grid with the suffix '_raw'
    
    Returns:
        None

    """
    
    #Outputs from the cluster
    listerrfiles = glob.glob(os.path.join(os.environ['MIST_GRID_DIR'], rawdirname) + '/*/*.e')
    listoutfiles = glob.glob(os.path.join(os.environ['MIST_GRID_DIR'], rawdirname) + '/*/*.o')
    
    #Dictionary to store the information about the MESA run
    stat_summary = {}

    #Loop over each model
    for index, file in enumerate(listerrfiles):

        #Declare status and also initialize each iteration
        status = ''

        #Extract the mass of the model
        if 'M_dir' in file:
            mass = file.split("/")[-2].rstrip('M_dir/')
        else:
            mass = file.split("/")[-2].split('M_')[0] + '_' + file.split("/")[-2].split('M_')[1].rstrip('_dir')

        with open(file, 'r') as errfile:
            errcontent = errfile.readlines()
        with open(listoutfiles[index], 'r') as outfile:
            outcontent = outfile.readlines()

        status = ''
        termination_reason = ''
        reason = ''

        #Retrieve the stopping reasons
        for line in outcontent[-30:]:
            if 'termination code' in line:
                termination_reason = line.split('termination code: ')[1].split('\n')[0]
                reason = termination_reason.replace(' ', '_')
                if reason == 'min_timestep_limit':
                    status = 'FAILED'
                else:
                    status = 'OK'
            if 'failed in do_relax_num_steps' in line:
                termination_reason = 'failed_during_preMS'
                reason = termination_reason.replace(' ', '_')
                status = 'FAILED'
        
        if status != 'OK':
            if (len(errcontent) > 0):
                status = 'FAILED'
                reason = 'unknown_error'
                for line in errcontent:
                    if 'DUE TO TIME LIMIT' in line:
                        reason = 'need_more_time'
                        break
                    elif 'exceeded memory limit' in line:
                        reason = 'memory_exceeded'
                        break
                    elif 'Socket timed out on send/recv operation' in line:
                        reason = 'socket_timed_out'
                        
        #Retrieve the run time information
        dates = subprocess.Popen('grep [0-9][0-9]:[0-9][0-9]:[0-9][0-9] ' + listoutfiles[index], shell=True, stdout=subprocess.PIPE)
        try:
            startdate, enddate = dates.stdout
            startdate_fmt = datetime.strptime(startdate.rstrip('\n'), '%a %b %d %H:%M:%S %Z %Y')
            enddate_fmt = datetime.strptime(enddate.rstrip('\n'), '%a %b %d %H:%M:%S %Z %Y')
            
            delta_time = (enddate_fmt - startdate_fmt)
            #Total run time in decimal hours
            runtime = delta_time.total_seconds()/(3600.0)
            
        #If there is no end date
        except ValueError:
            runtime = 'exceeded_req_time'
            
        #Populate the stat_summary dictionary
        stat_summary[mass] = "{:10}".format(status) + "{:50}".format(reason) + "{:25}".format(runtime)

    keys = stat_summary.keys()
    #Sort by mass in ascending order
    keys.sort()
    
    #Write to a file
    summary_filename = "tracks_summary.txt"
    f = csv.writer(open(summary_filename, 'w'), delimiter='\t')
    f.writerow(["{:15}".format('#Mass'), "{:10}".format('Status') + "{:50}".format('Reason') + "{:25}".format('Runtime')])
    f.writerow(['','','',''])
    
    for key in keys:
        f.writerow(["{:15}".format(key), stat_summary[key]])
        
def sort_histfiles(rawdirname):
    
    """

    Organizes the history files and creates a separate directory.

    Args:
        rawdirname: the name of the grid with the suffix '_raw'
    
    Returns:
        None

    """

    #Get the list of history files (tracks)
    listofhist = glob.glob(os.path.join(os.environ['MIST_GRID_DIR'], os.path.join(rawdirname+'/*/LOGS/*.data')))

    #Make the track directory in the new reduced MESA run directory
    new_parentdirname = rawdirname.split("_raw")[0]
    histfiles_dirname = os.path.join(os.path.join(os.environ['MIST_GRID_DIR'], new_parentdirname + "/tracks"))
    os.mkdir(histfiles_dirname)


    #Trim repeated model numbers, then rename & copy the history files over
    for histfile in listofhist:
        print 'processing', histfile
        if 'M_history.data' in histfile:
            unformat_mass_string = histfile.split('LOGS/')[1].split('M_history.data')[0]
            newhistfilename = histfile.split('LOGS')[0]+'LOGS/'+reformat_massname.reformat_massname(unformat_mass_string)+'M.track'
        else:
            unformat_mass_string = histfile.split('LOGS/')[1].split('_history.data')[0].split('M_')[0]
            bc_name = histfile.split('LOGS/')[1].split('M_')[1].split('_history.data')[0]
            newhistfilename = histfile.split('LOGS')[0]+'LOGS/'+reformat_massname.reformat_massname(unformat_mass_string)+'M_' + bc_name + '.track'
        os.system("cp " + histfile + " " + newhistfilename)
        mesa_hist_trim.trim_file(newhistfilename)
        os.system("mv " + newhistfilename + " " + histfiles_dirname)
        
def save_inlists(rawdirname):

    """

    Organizes the inlist files.

    Args:
        rawdirname: the name of the grid with the suffix '_raw'
    
    Returns:
        None

    """
    
    #Get the list of inlist files
    listofinlist = glob.glob(os.path.join(os.environ['MIST_GRID_DIR'], os.path.join(rawdirname+'/*/inlist_project')))

    #Nake the inlist directory in the new reduced MESA run directory
    new_parentdirname = rawdirname.split("_raw")[0]
    inlistfiles_dirname = os.path.join(os.path.join(os.environ['MIST_GRID_DIR'], new_parentdirname), "inlists")
    os.mkdir(inlistfiles_dirname)
    
    #Copy the inlist files from the general inlist directory in MESAWORK_DIR to the newly created inlist directory
    for inlistfile in listofinlist:
        format_mass_string = inlistfile.split('/')[-2].split('M_')[0]
        if 'M_dir' in inlistfile:
            newinlistfilename = os.path.join(os.path.join(os.environ['MIST_GRID_DIR'], new_parentdirname),'inlists/'+format_mass_string+'M.inlist')
        else:
            bc_name = inlistfile.split('raw/')[1].split('M_')[1].split('_')[0]
            newinlistfilename = os.path.join(os.path.join(os.environ['MIST_GRID_DIR'], new_parentdirname),'inlists/'+format_mass_string+'M_'+bc_name+'.inlist')
        os.system("cp " + inlistfile + " " + newinlistfilename)

def save_lowM_photo_model(rawdirname):
    
    """

    Saves the .mod and photo saved at postAGB for the low mass stars.

    Args:
        rawdirname: the name of the grid with the suffix '_raw'
    
    Returns:
        None

    """
    
    #Get the list of photos and models
    listofphoto = glob.glob(os.path.join(os.environ['MIST_GRID_DIR'], os.path.join(rawdirname+'/*/photos/pAGB_photo')))
    listofmod = glob.glob(os.path.join(os.environ['MIST_GRID_DIR'], os.path.join(rawdirname+'/*/*pAGB.mod')))

    #Nake the inlist directory in the new reduced MESA run directory
    new_parentdirname = rawdirname.split("_raw")[0]
    models_photos_files_dirname = os.path.join(os.path.join(os.environ['MIST_GRID_DIR'], new_parentdirname), "models_photos")
    os.mkdir(models_photos_files_dirname)
    
    #check first if these files exist in case the grid consists only of high mass stars.
    if len(listofphoto) < 1:
        print "THERE ARE NO PHOTOS OR MODELS SAVED AT THE POST-AGB PHASE."
    else:
        for i in range(len(listofphoto)):
            format_mass_string = listofphoto[i].split('/')[-3].split('M_')[0]
            newphotofilename = os.path.join(os.path.join(os.environ['MIST_GRID_DIR'], new_parentdirname),'models_photos/'+format_mass_string+'M_pAGB.photo')
            newmodfilename = os.path.join(os.path.join(os.environ['MIST_GRID_DIR'], new_parentdirname),'models_photos/'+format_mass_string+'M_pAGB.mod')
            os.system("cp " + listofphoto[i] + " " + newphotofilename)
            os.system("cp " + listofmod[i] + " " + newmodfilename)

