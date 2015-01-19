"""

Makes HR diagrams of tracks from MESA grids.

"""

import mesa_plot_eeps as mp
import glob
import matplotlib.pyplot as plt
import os
import Isochrones
import numpy as np

mistgrid_dir = os.environ['MIST_GRID_DIR']

def plot_HRD(gridname, logg=False):
    
    """
    
    Generates .pdf files of individual tracks.
    
    Args:
        gridname: the name of the grid

    Keywords:
        logg: make the HR diagram in logg-logTeff space instead of logL-logTeff

    Returns:
        None
        
    """
    #Assumes gridname has the form MIST_vXX/feh_XXX_afe_XXX
    lowest_dir = gridname.split('/')[-1]
    grid_dir = os.path.join(mistgrid_dir, gridname)
    filelist = glob.glob(os.path.join(grid_dir, 'eeps/*M.track.eep'))
    for file in filelist:
        starmass = float(file.split('eeps/')[1].split('M')[0])/100.0
        star = mp.EEPfile(file)
    	if logg == False:
            star.plot_HR(colorname='RoyalBlue')
            if starmass < 0.8:
                plt.axis([5.5, 3.0, -6, 4])
            elif starmass < 10.0:
                plt.axis([5.5, 3.0, -2, 5.5])
            else:
                plt.axis([5.5, 3.0, 3, 7])
            figname = os.path.join(grid_dir, 'plots/'+lowest_dir+'_'+file.split('eeps/')[1].split('M')[0] +'M'+ file.split('eeps/')[1].split('M')[1].split('.track')[0]+'_track_ind.pdf')

        elif logg == True:
            star.plot_HR(colorname='RoyalBlue', logg=True)
            if starmass < 0.8:
                plt.axis([5.5, 3.0, 9, 0])
            elif starmass < 10.0:
                plt.axis([5.5, 3.0, 9, -2])
            else:
                plt.axis([5.5, 3.0, 7, -3])
            figname = os.path.join(grid_dir, 'plots/'+lowest_dir+'_'+file.split('eeps/')[1].split('M')[0] +'M'+ file.split('eeps/')[1].split('M')[1].split('.track')[0]+'_track_logg_ind.pdf')
            
    	plt.title(str(starmass))
        plt.savefig(figname)
    	plt.clf()

def format_age(age):
    
    if age < 10.0:
        fmtage = '0'+str(int(round(age*100)))
    else:
        fmtage = str(int(round(age*100)))
    
    return fmtage
    
def plot_iso(gridname):
    
    """
    
    Generates .pdf files of isochrones.
    
    Args:
        gridname: the name of the grid

    Keywords:
        None

    Returns:
        None
        
    """
    #Assumes gridname has the form MIST_vXX/feh_XXX_afe_XXX
    grid_dir = os.path.join(mistgrid_dir, gridname)
    lowest_dir = gridname.split('/')[-1]
    iso_dir = glob.glob(os.path.join(grid_dir, 'isochrones/MIST*iso'))[0]
    isochrone = Isochrones.MESA_Isochrones(iso_dir)
    
    age_list = np.linspace(5, 10.3, 107)
    for age in age_list:
        isochrone.plot_HRD(min_log_age=age-0.01,max_log_age=age+0.01, fig_num=1)
        
        if age <= 7.0:
            plt.axis([5.5, 3.2, -3, 7])
        elif ((age > 7.0) & (age <= 9.0)):
            plt.axis([6.0, 2.5, -6, 6])
        elif age > 9.0:
            plt.axis([5.5, 2.0, -8, 4])
            
        plt.title(str(age))
    
        figname = os.path.join(grid_dir, 'plots/'+lowest_dir+'_'+format_age(age)+'_iso_ind.pdf')
        plt.savefig(figname)
        plt.clf()
        
def plot_combine(gridname, logg=False, iso=False, remove_pdf=False):
    
    """
    
    Combines the .pdf files from a MESA grid into a single .pdf file.
    
    Args:
        gridname: the name of the grid

    Keywords:
        logg: make the HR diagram in logg-logTeff space instead of logL-logTeff
        remove_pdf: removes the .pdf files of individual tracks after the combined .pdf file is created

    Returns:
        None
        
    """
    
    lowest_dir = gridname.split('/')[-1]
    grid_dir = os.path.join(mistgrid_dir, gridname)
    command = 'gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile='+os.path.join(grid_dir, 'plots/')
    if not iso:
        if logg == False:
            filelist = glob.glob(os.path.join(grid_dir, 'plots/'+lowest_dir+'_[0-1]*track*.pdf'))
            filelist = [x for x in filelist if 'logg' not in x]
        if logg == True:
            filelist = glob.glob(os.path.join(grid_dir, 'plots/'+lowest_dir+'_[0-1]*track*logg*.pdf'))
        
        if logg == False:
            command += '_'.join(gridname.split('/')) + '_alltracks.pdf '
        if logg == True:
            command += '_'.join(gridname.split('/')) + '_alltracks_logg.pdf '
 
    if iso:
        filelist = glob.glob(os.path.join(grid_dir, 'plots/'+lowest_dir+'_[0-1]*iso*.pdf'))
        command += '_'.join(gridname.split('/')) + '_allages.pdf '
            
    for file in sorted(filelist):
        command += file + ' '
            
    if remove_pdf == True:    
        os.system("rm " + os.path.join(grid_dir, 'plots/'+lowest_dir+'_[0-1]*ind.pdf'))

    os.system(command)
