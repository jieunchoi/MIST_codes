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
            self.ages=np.array([self.data[i][0][1] for i in range(len(self.data))])
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
