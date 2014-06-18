#!/usr/bin/env python

"""
This is master code that takes the MESA runs then 
creates isochrones & organizes all the output files
into a nice directory structure.
The directory structure is as follows:

top level directory: MIST_v00/FIDUCIAL/feh_p0.0_afe_p0.0/

four subdirectories: tracks/   eeps/    inlists/    isochrones/
"""

import glob
import os
import sys
import csv
import reformat_massname
import subprocess
import datetime

work_dir = '/home/jchoi/pfs/mesawork/'

def gen_summary(rawdirname):
    
    listerrfiles = glob.glob(work_dir+rawdirname+'/*/*.e*')
    listoutfiles = glob.glob(work_dir+rawdirname+'/*/*.o*')

    #create the dictionary
    stat_summary = {}

    for index, file in enumerate(listerrfiles):
        
        #declare status and also reset each iteration
        status = ''
        #check which format it is. originally assumed a '/*M_dir/*M.e*' format
        if 'M_dir' in file:
            mass = "{:<20}".format(file.split("/")[-2].rstrip('M_dir/'))
        else:
            mass = "{:<20}".format(file.split("/")[-2].split('M_')[0] + '_' + file.split("/")[-2].split('M_')[1].rstrip('_dir'))

        with open(file, 'r') as errfile:
            errcontent = errfile.readlines()
        with open(listoutfiles[index], 'r') as outfile:
            outcontent = outfile.readlines()

        status = ''
        termination_reason = ''

        #check for error messages
        if (len(errcontent) > 1):
            if '=>> PBS: job killed: walltime' in errcontent[1]:
                status = 'FAILED'
                reason = "job killed, hit a walltime limit"
            else:
                status = 'FAILED'
                reason = "Unknown error, please check"
        else:
            for line in outcontent[-30:]:
                if 'termination code' in line:
                    termination_reason = line.split('termination code: ')[1].split('\n')[0]
                    break
                if 'failed in do_relax_num_steps' in line:
                    termination_reason = 'failed during preMS'
                    break
            for line in outcontent[-50:]:  
                if (' stopping because of convergence problems' in line) or \
                           ('terminated evolution: convergence problems' in line):
                    status = 'FAILED'
                    reason = termination_reason
                if (line == outcontent[-1]) & (status == ''):
                    status = 'OK'
                    reason = termination_reason
        
        #get the runtime
        dates = subprocess.Popen('grep [0-9][0-9]:[0-9][0-9]:[0-9][0-9] ' + listoutfiles[index], shell=True, stdout=subprocess.PIPE)
        try:
            startdate, enddate = dates.stdout
            startdatelist = startdate.rstrip('\n').split(' ')
            enddatelist = enddate.rstrip('\n').split(' ')
            start = datetime.timedelta(int(startdatelist[2]), int(startdatelist[3].split(':')[-1]), 0,0,int(startdatelist[3].split(':')[-2]), int(startdatelist[3].split(':')[-3]))
            end = datetime.timedelta(int(enddatelist[2]), int(enddatelist[3].split(':')[-1]), 0,0,int(enddatelist[3].split(':')[-2]), int(enddatelist[3].split(':')[-3]))
            runtime = str(datetime.timedelta(seconds=datetime.timedelta.total_seconds(end-start)))
        #if it only returns starttime
        except:
            runtime = 'exceeded walltime'
            
        #populate the stat_summary dictionary
        stat_summary[mass] = "{:<10}".format(status) + "{:<90}".format(reason) + "{:<20}".format(runtime)

    keys = stat_summary.keys()
    #sort by mass in ascending order
    keys.sort()
    
    #write the file out
    summary_filename = "tracks_summary.txt"
    f = csv.writer(open(summary_filename, 'w'), delimiter='\t')
    f.writerow(["{:<20}".format('#Mass'), "{:<10}".format('Status'), "{:<90}".format('Reason'), 'Runtime'])
    f.writerow(['','',''])
    
    for key in keys:
        f.writerow([key, stat_summary[key]])
        
def sort_histfiles(rawdirname):

    #get the list of history files (tracks)
    listofhist = glob.glob(os.path.join(work_dir, os.path.join(rawdirname+'/*/LOGS/*.data')))

    #make the history file directory in the new parent directory
    #i.e. v04_Z0.02_abSOLAR/histfiles
    new_parentdirname = rawdirname.split("_raw")[0]
    os.system("cd " + new_parentdirname)
    histfiles_dirname = os.path.join(new_parentdirname, "tracks")
    os.mkdir(histfiles_dirname)

    #rename & copy the files over
    for histfile in listofhist:
        if 'M_history.data' in histfile:
            unformat_mass_string = histfile.split('LOGS/')[1].split('M_history.data')[0]
            newhistfilename = histfile.split('LOGS')[0]+'LOGS/'+reformat_massname.reformat_massname(unformat_mass_string)+'M.track'
        else:
            unformat_mass_string = histfile.split('LOGS/')[1].split('M_history.data')[0]
            bc_name = histfile.split('LOGS/')[1].split('M_')[1].split('_history.data')[0]
            newhistfilename = histfile.split('LOGS')[0]+'LOGS/'+reformat_massname.reformat_massname(unformat_mass_string)+'M_' + bc_name + '.track'
        os.system("cp " + histfile + " " + newhistfilename)
        os.system("mv " + newhistfilename + " " + histfiles_dirname)
        
def save_inlists(rawdirname):

    #make the inlist file directory
    #inlistfiles_dirname = dirname + '_inlists'
    new_parentdirname = rawdirname.split("_raw")[0]
    os.system("cd " + new_parentdirname)
    inlistfiles_dirname = os.path.join(new_parentdirname, "inlists")
    os.mkdir(inlistfiles_dirname)
    
    #copy the files from the general inlist dir to the inlist dir specific to this run
    os.system("cp " + os.path.join(work_dir, "inlists/inlists_"+new_parentdirname+"/*") + " " + inlistfiles_dirname)

def do_organize(dirname):
    
    #rename the run directory ("v04_Z0.02_abSOLAR") as "v04_Z0.02_abSOLAR_raw"
    rawdirname = dirname+"_raw"
    os.system("mv " + os.path.join(work_dir,dirname) + " " + os.path.join(work_dir,rawdirname))
    #new "v04_Z0.02_abSOLAR" directory that will contain all of the information
    os.mkdir(dirname)
    #make an eeps directory that will be filled in later
    os.mkdir(os.path.join(dirname, "eeps"))
    #make isochrones and eeps directories that will be filled in later
    os.mkdir(os.path.join(dirname, "isochrones"))

    print "************************************************************"
    print "****************SORTING THE HISTORY FILES*******************"
    print "************************************************************"
    sort_histfiles(rawdirname)
    
    print "************************************************************"
    print "****************GENERATING A SUMMARY FILE*******************"
    print "************************************************************"
    gen_summary(rawdirname)
    
    #move the summary file to this tracks directory
    os.system("mv tracks_summary.txt " + os.path.join(dirname, "tracks"))
    print "************************************************************"
    print "****************SORTING THE INLIST FILES********************"
    print "************************************************************"
    save_inlists(rawdirname)
    
    #now make isochrones
    print "************************************************************"
    print "**************NOW IT'S TIME FOR ISOCHRONES******************"
    print "************************************************************"
    os.system("./mesa2fsps.py " + "input."+sys.argv[1])
    
    print "************************************************************"
    print "****************COMPRESSING THE DIRECTORY*******************"
    print "************************************************************"
    os.system("tar -zcvf " + dirname + ".tar.gz " + dirname)
    os.system("mv " + dirname + "* " + work_dir)
    
#do_organize(sys.argv[1])




