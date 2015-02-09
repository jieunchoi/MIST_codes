import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, rc

class EEPfile:
    
    """
    
    Reads in and plots MISTeep files.
    
    """
    
    def __init__(self, filename):
        
        self.filename = filename
        print 'Reading in: ' + self.filename

        self.datafile = np.genfromtxt(self.filename, skip_header=4, names=True)

        f = open(self.filename, 'r')
        unformatted_header_list = f.readlines()[4]
        f.close()
        header_list = '  |  '.join(unformatted_header_list.split())
        self.hdr_list = header_list
    
    def read_vars(self, *columnnames):

        all_xvar = []
        for xvar in columnnames:
            while True:
                try:
                    x = self.datafile[xvar]
                    break
                except (TypeError, NameError, ValueError):
                    print xvar, " wasn't a valid column entry. Try again from the following: \n"
                    print self.hdr_list
                    print '\n'
                    xvar = raw_input('var: ')
            all_xvar.append(x)
        
        if len(columnnames) == 1:
            all_xvar = all_xvar[0]
            
        return all_xvar

    def plot_vars(self, xvar, yvar, pltnum = 1, leglabel='', legendloc=1, xtitle='', ytitle='', filetit='', linestyle='-', linewidth=1.5, colorname='', x_inv=0, y_inv=0, saveplot=0):
        
        font = {'family' : 'serif',
                'weight' : 'normal',
                'size'   : 18}
        rc('font', **font)
       
        x, y = self.read_vars(xvar, yvar)
        
        fig = plt.figure(pltnum, figsize=(12,10))
        plt.xlabel(xtitle, fontsize=20)
        plt.ylabel(ytitle, fontsize=20)
        
        ax = fig.add_subplot(111)
                
        if colorname != '' and linestyle == '-':
            ax.plot(x, y, color=colorname, label=leglabel, linewidth=linewidth)
        elif colorname != '' and linestyle != '-':
            ax.plot(x, y, color=colorname, linestyle=linestyle, label=leglabel, linewidth=linewidth)
        elif colorname == '' and linestyle == '-':
            ax.plot(x, y, label=leglabel, linewidth=linewidth)
        elif colorname == '' and linestyle != '-':
            ax.plot(x, y, linestyle=linestyle, label=leglabel, linewidth=linewidth)

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
            fig.savefig(filetit)
        
        return x, y
        
    def plot_HR(self, leglabel='', colorname='', linestyle='-', pltnum=111, logg=False):
        
        if logg == False:
            logTeff, logL = self.plot_vars('log_Teff','log_L', pltnum=pltnum, colorname=colorname, linestyle=linestyle, leglabel=leglabel, legendloc=3, xtitle='log(Teff) [K]', ytitle='log(L/Lsun)', x_inv=1)
            return logTeff, logL
        else:
            logTeff, logg = self.plot_vars('log_Teff','log_g', pltnum=pltnum, colorname=colorname, linestyle=linestyle, leglabel=leglabel, legendloc=3, xtitle='log(Teff) [K]', ytitle='log(g) [g/cc]', x_inv=1, y_inv=1)
            return logTeff, logg
        
