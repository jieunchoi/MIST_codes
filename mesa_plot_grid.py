"""

Makes HR diagrams of tracks from MESA grids.

"""

import mesa_plot_eeps as mp
import glob
import matplotlib.pyplot as plt
import os

work_dir = os.environ['MESAWORK_DIR']

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
    grid_dir = os.path.join(work_dir, gridname)
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
            figname = os.path.join(grid_dir, 'plots/'+lowest_dir+'_'+file.split('eeps/')[1].split('M')[0] +'M'+ file.split('eeps/')[1].split('M')[1].split('.track')[0]+'_ind.pdf')

        elif logg == True:
            star.plot_HR(colorname='RoyalBlue', logg=True)
            if starmass < 0.8:
                plt.axis([5.5, 3.0, 9, 0])
            elif starmass < 10.0:
                plt.axis([5.5, 3.0, 9, -2])
            else:
                plt.axis([5.5, 3.0, 7, -3])
            figname = os.path.join(grid_dir, 'plots/'+lowest_dir+'_'+file.split('eeps/')[1].split('M')[0] +'M'+ file.split('eeps/')[1].split('M')[1].split('.track')[0]+'_logg_ind.pdf')
            
    	plt.title(str(starmass))
        plt.savefig(figname)
    	plt.clf()

def plot_combine(gridname, logg=False, remove_pdf=False):
    
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
    grid_dir = os.path.join(work_dir, gridname)
    if logg == False:
        filelist = glob.glob(os.path.join(grid_dir, 'plots/'+lowest_dir+'_[0-1]*.pdf'))
        filelist = [x for x in filelist if 'logg' not in x]
    if logg == True:
        filelist = glob.glob(os.path.join(grid_dir, 'plots/'+lowest_dir+'_[0-1]*logg.pdf'))
        
    command = 'gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile='+os.path.join(grid_dir, 'plots/')
    
    if logg == False:
        command += '_'.join(gridname.split('/')) + '_alltracks.pdf '
    if logg == True:
        command += '_'.join(gridname.split('/')) + '_alltracks_logg.pdf '
 
    for file in filelist:
        command += file + ' '
            
    if remove_pdf == True:    
        os.system("rm " + os.path.join(grid_dir, 'plots/'+lowest_dir+'_[0-1]*ind.pdf'))

    os.system(command)
