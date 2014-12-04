from __future__ import print_function
from fortranformat import FortranRecordReader as fread
import matplotlib.pyplot as plt
import numpy as np

###AARON DOTTER'S ROUTINE###

class MESA_Isochrones:
    """Holds the contents of a MESA isochrone file."""

    #reads in a file and sets a few basic quantities
    def __init__(self,filename):
        self.filename=filename.strip()
        try:
            self.version, self.data = self.read_iso_file()
            self.ages=np.array([self.data[i]['log_age'][0] for i in range(len(self.data))])
        except IOError:
            print("Failed to open isochrone file: ")
            print(self.filename)

        self.have_mags=[]
        self.BCs=[]
        self.mags=[]

    #this function reads in the text file
    def read_iso_file(self):
        #open file
        f=open(self.filename,mode='r')
        #define some line formats
        first_line=fread('(a25,i5)')
        age_line=fread('(a6,e20.10,a5)')
        eep_line=fread('(a25,2i5)')
        def num_line(cols): return fread('(1x,i4,{:d}i32)'.format(np.int(cols-1)))
        def col_line(cols): return fread('(2x,a3,{:d}a32)'.format(np.int(cols-1)))
        def data_line(cols): return fread('(i5,{:d}e32.16)'.format(np.int(cols-1)))
    
        #read the first two lines
        junk,num_ages = first_line.read(f.readline())
        junk,version = first_line.read(f.readline())
    
        #read one block for each isochrone
        iso_set=[]
        for iage in range(num_ages):
            junk,num_eeps,num_cols = eep_line.read(f.readline())
            cols = num_line(num_cols).read(f.readline())
            names = col_line(num_cols).read(f.readline())
            #remove extra spaces in names
            names = tuple([name.strip() for name in names])
            #adjust column number for python
            formats=tuple([np.int32]+[np.float64 for i in range(num_cols-1)])
            iso=np.zeros((num_eeps),{'names':names,'formats':formats})
            #read through EEPs for each isochrone
            for eep in range(num_eeps):
                x=f.readline().split()
                y=[]
            #this business with x and y is inelegant
                y.append(np.int(x[0]))
                [y.append(z) for z in map(np.float64,x[1:])]
                iso[eep]=tuple(y)
            if iage<num_ages-1:
                f.readline()
                f.readline()
            iso_set.append(iso)
        f.close()
        return version, iso_set

    #assign a bolometric correction table
    def add_BCTable(self,filename):
        self.BCs.append(BCTable(filename))
        self.mags.append(None)
        self.have_mags.append(False)

    def get_mags(self,k):
        self.mags[k]=[]
        for d in self.data:
            Teff=10**d['log_Teff']
            index=np,where(Teff>7e4)
            Teff[index]=7e4
            logg=d['log_g']
            index=np.where(logg>5.5)
            logg[index]=5.5
            logL=d['log_L']
            self.mags[k].append(self.BCs[k].get_mags(Teff,logg,logL))
        self.have_mags[k]=True

    #plot an H-R diagram
    def plot_HRD(self,min_log_age=-99.0,max_log_age=99.0,show_legend=False,fig_num=-1):
        small=1.0e-5
        min_log_age-=small
        max_log_age+=small
        if np.int(fig_num) >= 0:
            plt.figure(num=np.int(fig_num),figsize=(12,10))
        else:
            plt.figure(num=None,figsize=(12,10))
        plt.xlabel('log(Teff) [K]', fontsize=20)
        plt.ylabel('log(L/Lsun)', fontsize=20)
        for i, iso in enumerate(self.data):
            if min_log_age <= self.ages[i] <= max_log_age:
                plt.plot(iso['log_Teff'],iso['log_L'],label='log(Age)={:5.2f}'.format(self.ages[i]), color='FireBrick', linewidth=1.5)
        if show_legend:
            leg = plt.legend(loc='lower left')
            leg.draw_frame(False)
        plt.gca().invert_xaxis()

    #plot a color-magnitude diagram
    def plot_CMD(self,mag1,mag2,mag3,min_log_age=-99.0,max_log_age=99.0,show_legend=False,fig_num=-1):
        if not self.have_mags:
            print("Need to call get_mags() first!")
        small=1.0e-5
        min_log_age-=small
        max_log_age+=small
        fs=18
        if np.int(fig_num) >= 0:
            plt.figure(num=np.int(fig_num),figsize=(8,8))
        else:
            plt.figure(num=None,figsize=(8,8))
        mag_list = self.BCTable.names
        if mag1 in mag_list and mag2 in mag_list and mag3 in mag_list:
            for i, iso in enumerate(self.mags):
                if min_log_age <= self.ages[i] <= max_log_age:
                    plt.plot(iso[mag1]-iso[mag2],iso[mag3],label='log(Age)={:5.2f}'.format(self.ages[i]))
            if show_legend: plt.legend(loc='lower left')
            plt.gca().invert_yaxis()
        else:
            print('supplied mags not in BCTable.')
            print('Supplied:')
            print(mag1,mag2,mag3)
            print('Available:')
            print(self.BCTable.names)
            
    def plot_centerTRho(self,min_log_age=-99.0,max_log_age=99.0,show_legend=False,fig_num=-1):
        small=1.0e-5
        min_log_age-=small
        max_log_age+=small
        fs=20
        if np.int(fig_num) >= 0:
            plt.figure(num=np.int(fig_num),figsize=(8,8))
        else:
            plt.figure(num=None,figsize=(8,8))
        plt.xlabel(r'$\log(T_c)$',fontsize=fs)
        plt.ylabel(r'$\log(\rho_c)$',fontsize=fs)
        plt.xticks(fontsize=fs)
        plt.yticks(fontsize=fs)
        for i, iso in enumerate(self.data):
            if min_log_age <= self.ages[i] <= max_log_age:
                plt.plot(iso['log_center_T'],iso['log_center_Rho']) #,label='log(Age)={:i}'.format((i+5)))
        if show_legend: plt.legend(loc='lower right')

    def check_monotonic(self):
        for d in self.data:
            print(d['log_age'][0])
            bad_region=[]
            eep=d['EEP']
            minit=d['initial_mass']
            for i in range(len(minit)-1):
                if minit[i] > minit[i+1]: 
                    print(eep[i],minit[i],minit[i+1])
                    for j in range(i,len(minit)-1):
                        if minit[j] > minit[i]: break
                    bad_region.append([i,j])
            print("\n")
