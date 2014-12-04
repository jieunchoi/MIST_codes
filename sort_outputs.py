#!/usr/bin/env python

"""

Takes MESA grids to create isochrones and organizes all the output files
into a nice directory structure.

The directory structure is as follows:
    top level directory --> MIST_vXX/FIDUCIAL/feh_pX.X_afe_pX.X/
    five subdirectories --> tracks/    eeps/    inlists/    isochrones/    plots/

Args:
    runname: the name of the grid

"""

import glob
import os
import sys
import csv
import reformat_massname
import subprocess
import datetime
import mesa_plot_grid
import mesa2fsps

work_dir = os.environ['MESAWORK_DIR']
storage_dir = os.environ['STORE_DIR']

def gen_summary(rawdirname):
    
    """

    Retrieves various information about the MESA run and writes to a summary file

    Args:
        rawdirname: the name of the grid with the suffix '_raw'
    
    Returns:
        None

    """
    
    #Outputs from the cluster
    listerrfiles = glob.glob(os.path.join(work_dir, rawdirname) + '/*/*.e')
    listoutfiles = glob.glob(os.path.join(work_dir, rawdirname) + '/*/*.o')
    
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
                    if 'DUE TO TIME LIMIT ***' in line:
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
            startdatelist = startdate.rstrip('\n').split(' ')
            enddatelist = enddate.rstrip('\n').split(' ')
            
            #For single-digit dates
            if '' in startdatelist:
                startdatelist.remove('')
            if '' in enddatelist:
                enddatelist.remove('')
            
            #If not start and finish in the same month:
            if startdatelist[1] != enddatelist[1]:
                if startdatelist[2] == '31':
                    startdatelist[2] = '0'
                elif startdatelist[2] == '30':
                    if startdatelist[1] in ['Jan', 'Mar', 'May', 'Jul', 'Aug', 'Oct', 'Dec']:
                        startdatelist[2] = '0'
                        enddatelist[2] = '2'
            start = datetime.timedelta(int(startdatelist[2]), int(startdatelist[3].split(':')[-1]), 0,0,int(startdatelist[3].split(':')[-2]), int(startdatelist[3].split(':')[-3]))
            end = datetime.timedelta(int(enddatelist[2]), int(enddatelist[3].split(':')[-1]), 0,0,int(enddatelist[3].split(':')[-2]), int(enddatelist[3].split(':')[-3]))
            runtime = str(datetime.timedelta(seconds=datetime.timedelta.total_seconds(end-start)))
                
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

    Organizes the history files.

    Args:
        rawdirname: the name of the grid with the suffix '_raw'
    
    Returns:
        None

    """

    #Get the list of history files (tracks)
    listofhist = glob.glob(os.path.join(work_dir, os.path.join(rawdirname+'/*/LOGS/*.data')))

    #Make the track directory in the new reduced MESA run directory
    new_parentdirname = rawdirname.split("_raw")[0]
    histfiles_dirname = os.path.join(os.path.join(work_dir, new_parentdirname), "tracks")
    os.mkdir(histfiles_dirname)

    #Rename & copy the history files over
    for histfile in listofhist:
        if 'M_history.data' in histfile:
            unformat_mass_string = histfile.split('LOGS/')[1].split('M_history.data')[0]
            newhistfilename = histfile.split('LOGS')[0]+'LOGS/'+reformat_massname.reformat_massname(unformat_mass_string)+'M.track'
        else:
            unformat_mass_string = histfile.split('LOGS/')[1].split('_history.data')[0].split('M_')[0]
            bc_name = histfile.split('LOGS/')[1].split('M_')[1].split('_history.data')[0]
            newhistfilename = histfile.split('LOGS')[0]+'LOGS/'+reformat_massname.reformat_massname(unformat_mass_string)+'M_' + bc_name + '.track'
        os.system("cp " + histfile + " " + newhistfilename)
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
    listofinlist = glob.glob(os.path.join(work_dir, os.path.join(rawdirname+'/*/inlist_project')))

    #Nake the inlist directory in the new reduced MESA run directory
    new_parentdirname = rawdirname.split("_raw")[0]
    inlistfiles_dirname = os.path.join(os.path.join(work_dir, new_parentdirname), "inlists")
    os.mkdir(inlistfiles_dirname)
    
    #Copy the inlist files from the general inlist directory in MESAWORK_DIR to the newly created inlist directory
    for inlistfile in listofinlist:
        format_mass_string = inlistfile.split('/')[-2].split('M_')[0]
        if 'M_dir' in inlistfile:
            newinlistfilename = os.path.join(os.path.join(work_dir, new_parentdirname),'inlists/'+format_mass_string+'M.inlist')
        else:
            bc_name = inlistfile.split('raw/')[1].split('M_')[1].split('_')[0]
            newinlistfilename = os.path.join(os.path.join(work_dir, new_parentdirname),'inlists/'+format_mass_string+'M_'+bc_name+'.inlist')
        os.system("cp " + inlistfile + " " + newinlistfilename)

def do_organize(runname):
    
    """

    Wrapper for the various routines to reduce a directory of MESA runs to
    a MIST directory.

    Args:
        runname: the name of the grid
    
    Returns:
        None

    """
    
    #Rename the run directory XXX as XXX_raw
    rawdirname = runname+"_raw"
    os.system("mv " + os.path.join(work_dir,runname) + " " + os.path.join(work_dir,rawdirname))
    
    #The XXX directory will contain the organized, reduced information
    newdirname = os.path.join(work_dir,runname)
    os.mkdir(newdirname)
    
    #Make the eeps directory that will be filled in later
    os.mkdir(os.path.join(newdirname, "eeps"))
    
    #Make the isochrones directory that will be filled in later
    os.mkdir(os.path.join(newdirname, "isochrones"))

    print "************************************************************"
    print "****************SORTING THE HISTORY FILES*******************"
    print "************************************************************"
    sort_histfiles(rawdirname)
    
    print "************************************************************"
    print "****************GENERATING A SUMMARY FILE*******************"
    print "************************************************************"
    gen_summary(rawdirname)
    
    #Move the summary file to the tracks directory
    os.system("mv tracks_summary.txt " + os.path.join(newdirname, "tracks"))
    
    print "************************************************************"
    print "****************SORTING THE INLIST FILES********************"
    print "************************************************************"
    save_inlists(rawdirname)
    
    print "************************************************************"
    print "**********************MAKE ISOCHRONES***********************"
    print "************************************************************"
    mesa2fsps.mesa2fsps(runname)
    
    print "************************************************************"
    print "****************PLOTTING THE EEPS FILES******************"
    print "************************************************************"
    os.mkdir(os.path.join(newdirname, "plots"))
    mesa_plot_grid.plot_HRD(runname)
    mesa_plot_grid.plot_combine(runname, iso=False)
    
    print "************************************************************"
    print "******************PLOTTING THE ISOCHRONES*******************"
    print "************************************************************"
    mesa_plot_grid.plot_iso(runname)
    mesa_plot_grid.plot_combine(runname, iso=True)
    
    print "************************************************************"
    print "****************COMPRESSING THE DIRECTORY*******************"
    print "************************************************************"
    os.chdir(work_dir)
    #When decompressed, this .tar.gz opens a MIST_vXX/feh_XXX_afe_XXX directory
    os.system("tar -zcvf " + '_'.join(runname.split('/')) + ".tar.gz " + runname)
    
    print "************************************************************"
    print "****************MIGRATING FILES TO STORAGE******************"
    print "************************************************************"
    os.system("rm -rf " + runname)
    os.system("mv " + rawdirname + " " + os.path.join(storage_dir, runname.split('/')[0]))
    os.system("mv " + '_'.join(runname.split('/')) + ".tar.gz " + os.path.join(storage_dir, runname.split('/')[0]))
    
if __name__ == "__main__":
    
    runname = sys.argv[1]
    do_organize(runname)

