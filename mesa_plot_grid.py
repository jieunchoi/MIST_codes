"""

Makes HR diagrams of tracks from MESA grids.

"""

import mesa_plot as mp
import glob
import matplotlib.pyplot as plt
import os

work_dir = os.environ['MESAWORK_DIR']

def plot_HRD(gridname, logg=False):
    
    """
    
    Generates .png files of individual tracks.
    
    Args:
        gridname: the name of the grid

    Keywords:
        logg: make the HR diagram in logg-logTeff space instead of logL-logTeff

    Returns:
        None
        
    """
    
    grid_dir = os.path.join(work_dir, gridname)
    filelist = glob.glob(os.path.join(grid_dir, 'tracks/*.track'))
    for file in filelist:
        starmass = float(file.split('tracks/')[1].split('M')[0])/100.0
        star = mp.Starfile(file)
    	if logg == False:
            star.plot_HR()
            if starmass < 0.8:
                plt.axis([5.5, 3.0, -6, 4])
            elif starmass < 10.0:
                plt.axis([5.5, 3.0, -2, 5.5])
            else:
                plt.axis([5.5, 3.0, 3, 7])
            figname = os.path.join(grid_dir, 'plots/'+gridname+'_'+file.split('tracks/')[1].split('M')[0] +'M'+ file.split('tracks/')[1].split('M')[1].split('.track')[0]+'.png')

        elif logg == True:
            star.plot_HR(logg=True)
            if starmass < 0.8:
                plt.axis([5.5, 3.0, 9, 0])
            elif starmass < 10.0:
                plt.axis([5.5, 3.0, 9, -2])
            else:
                plt.axis([5.5, 3.0, 7, -3])
            figname = os.path.join(grid_dir, 'plots/'+gridname+'_'+file.split('tracks/')[1].split('M')[0] +'M'+ file.split('tracks/')[1].split('M')[1].split('.track')[0]+'_logg.png')
            
    	plt.title(str(starmass))
        plt.savefig(figname)
    	plt.clf()

def mesa_plot_combine(gridname, logg=False, remove_png=True):
    
    """
    
    Combines the .png files from a MESA grid into a single .pdf file.
    
    Args:
        gridname: the name of the grid

    Keywords:
        logg: make the HR diagram in logg-logTeff space instead of logL-logTeff
        remove_png: removes the .png files of individual tracks after the combined .pdf file is created

    Returns:
        None
        
    """
    
    grid_dir = os.path.join(work_dir, gridname)
    if logg == False:
        filelist = glob.glob(os.path.join(grid_dir, 'plots/'+gridname+'_[0-1]*.png'))
        filelist = [x for x in filelist if 'logg' not in x]
    if logg == True:
        filelist = glob.glob(os.path.join(grid_dir, 'plots/'+gridname+'_[0-1]*logg.png'))
        
    command = 'convert '
    for file in filelist:
        command += file + ' '
    
    if logg == False:
        command += gridname + '_alltracks.pdf'
    if logg == True:
        command += gridname + '_alltracks_logg.pdf'
    
    if remove_png == True:    
        os.system("rm " + os.path.join(grid_dir, 'plots/'+gridname+'_[0-1]*.png'))
    os.system(command)