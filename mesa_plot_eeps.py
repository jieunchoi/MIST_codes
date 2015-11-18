import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, rc

class EEPfile:
    
    """
    
    Reads in and plots MESA EEP files.

    
    """
    
    def __init__(self, filename, verbose=True):
    
        """

        Reads in the file.
        
        Args:
            filename: the name of the history or profile file.
        
        Usage:
            >> star = mpE.EEPfile('2M.track.eep')
        
        """
        
        self.filename = filename
        if verbose:
            print 'Reading in: ' + self.filename
            
        self.datafile = np.genfromtxt(self.filename, skip_header=4, names=True)

        f = open(self.filename, 'r')
        unformatted_header_list = f.readlines()[4]
        f.close()
        header_list = '\n'.join(unformatted_header_list.split())
        self.hdr_list = header_list
    
    def read_vars(self, *columnnames):

        """

        Reads in an arbitrary number of columns.

        Args:
            columnnames: the name of the column as listed in history_columns.list or profile_columns.list
    
        Usage:
            >> age, initmass, h1_c = star.read_vars('star_age', 'initial_mass', 'center_h1')
        
        """
        
        all_xvar = []
        
        #read in as many columns as necessary 
        for xvar in columnnames:
            while True:
                try:
                    x = self.datafile[xvar]
                    break
                except (TypeError, NameError, ValueError):
                    print "Ooops! That wasn't a valid column entry. Try again from the following: "
                    print self.hdr_list
                    xvar = raw_input('var: ')
            all_xvar.append(x)
        
        if len(columnnames) == 1:
            all_xvar = all_xvar[0]
            
        return all_xvar

    def plot_vars(self, xvar, yvar, xlabel='', ylabel='', color='black', linewidth=1.5, linestyle='-', label='', loc=1, pltnum = 1, x_inv=0, y_inv=0, saveplot=0, figname='', phase=None):
        
        """

        Plots two columns.

        Args:
            xvar: x-axis variable name as listed in history_columns.list or profile_columns.list
            yvar: y-axis variable name as listed in history_columns.list or profile_columns.list
        
        Keywords:
            regular matplotlib keywords: xlabel, ylabel, color, linewidth, linestyle, label, loc
            mesa_plot_hist keyword: pltnum, x_inv, y_inv, saveplot, figname, phase
    
        Usage:
            >> star.plot_vars('log_center_Rho', 'log_center_T', linewidth=2.0, color='blue', saveplot=1, figname='center_rhoT.pdf')
        
        """
        
        font = {'family' : 'serif',
                'weight' : 'normal',
                'size'   : 18}
        rc('font', **font)
       
        x, y = self.read_vars(xvar, yvar)
        
        fig = plt.figure(pltnum, figsize=(8,8))
        plt.xlabel(xlabel, fontsize=20)
        plt.ylabel(ylabel, fontsize=20)
        
        ax = fig.add_subplot(111)
                
        ax.plot(x, y, color=color, linestyle=linestyle, label=label, linewidth=linewidth)

        if (np.min(x) <= 0 and np.min(y) >= 0):
            x_axmin, x_axmax, y_axmin, y_axmax = min(x)*1.1, max(x)*1.1, min(y)*0.9, max(y)*1.1
        if (np.min(y) <= 0 and np.min(x) >= 0):
        	x_axmin, x_axmax, y_axmin, y_axmax = min(x)*0.9, max(x)*1.1, min(y)*1.1, max(y)*1.1
        if (np.min(y) <= 0 and np.min(x) <= 0):
    		x_axmin, x_axmax, y_axmin, y_axmax = min(x)*1.1, max(x)*1.1, min(y)*1.1, max(y)*1.1
        if (np.min(y) >= 0 and np.min(x) >= 0):
        	x_axmin, x_axmax, y_axmin, y_axmax = min(x)*0.9, max(x)*1.1, min(y)*0.9, max(y)*1.1
            
        if x_inv == 1 and y_inv == 1:
            ax.axis([x_axmax, x_axmin, y_axmax, y_axmin])
        elif x_inv == 1 and y_inv == 0:
            ax.axis([x_axmax, x_axmin, y_axmin, y_axmax])
        elif y_inv == 1 and x_inv == 0:
            ax.axis([x_axmin, x_axmax, y_axmax, y_axmin])
        else:
            ax.axis([x_axmin, x_axmax, y_axmin, y_axmax])
                
        if saveplot == 1:
            fig.savefig(figname)
        if label != '':
            leg = plt.legend(loc=loc)
            leg.draw_frame(False)
        
        if phase != None:
            p = self.read_vars('phase')
            p_ind = np.where(p == phase)
            if len(p_ind) > 0:
                ax.plot(x[p_ind], y[p_ind], color=color, linewidth=4.0, alpha=0.3)
        
        return x, y
                
    def plot_HR(self, color='black', linestyle='-', linewidth=1.5, label='', loc=1, pltnum=2, logg=False, figname='', saveplot=0, phase=None):
        
        """

        Plots the HR diagram.

        Args:
            None.
            
        Keywords:
            regular matplotlib keywords: color, linestyle, linewidth, label, loc
            mesa_plot_hist keyword: pltnum, logg, figname, saveplot, phase
    
        Usage:
            >> star.plot_HR()
        
        """
        
        #plot the HR diagram in logg-logTeff space
        if logg == False:
            logTeff, logL = self.plot_vars('log_Teff','log_L', pltnum=pltnum, color=color, linestyle=linestyle, linewidth=linewidth, label=label, loc=3, xlabel=r'$\log(T_{\rm eff})\;[\rm K]$', ylabel=r'$\log(L/L_{\odot}$)', x_inv=1, saveplot=saveplot, figname=figname, phase=phase)
            return logTeff, logL
            
        #plot the regular HR diagram
        else:
            logTeff, logg = self.plot_vars('log_Teff','log_g', pltnum=pltnum, color=color, linestyle=linestyle, linewidth=linewidth, label=label, loc=3, xlabel=r'$\log(T_{\rm eff})\;[\rm K]$', ylabel=r'$\log(g)\;[\rm g\;cm^{-3}]$', x_inv=1, y_inv=1, saveplot=saveplot, figname=figname, phase=phase)
            return logTeff, logg
        