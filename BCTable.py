import numpy as np
from scipy.interpolate import griddata

###AARON DOTTER'S ROUTINE###

class BCTable:
    """Holds a table of Teff, logg, and bolometric corrections."""

    def __init__(self,filename):
        f=filename.strip()
        try:
            self.data=np.genfromtxt(f,names=True,dtype=None,skip_header=1)
        except IOError:
            print("Failed to open input file: ")
            print(f)
            return
        grid=[]; mags=[]
        Teff=[]; logg=[]
        for d in self.data:
            Teff.append(d['Teff'])
            logg.append(d['logg'])
            grid.append([d['Teff'],d['logg']])
            dl=list(d)
            mags.append([dl[3:]])
        loc=f.rfind('.')
        self.system=f[loc+1:]
        self.alpha=float(f[loc-2:loc].replace('p','+').replace('m','-'))/10.
        self.Teff=np.array(sorted(set(Teff)))
        self.logg=np.array(sorted(set(logg)))
        self.grid=np.array(grid)
        self.mags=np.array(mags)
        self.FeH=self.data[0]['FeH']
        self.names=self.data.dtype.names[3:]
        self.SolBol = 4.75

    def table_interp(self,Teff,logg):
        return np.squeeze(griddata(self.grid,self.mags,(Teff,logg),method='linear'))

    def get_mags(self,Teff,logg,logL):
        Teff=np.array(Teff,ndmin=1)
        logg=np.array(logg,ndmin=1)
        logL=np.array(logL,ndmin=1)
        formats=[np.float64 for name in self.names]
        BCs=self.table_interp(Teff,logg)
        mags=np.empty(shape(Teff),{'names':self.names,'formats':formats})
        for i in range(len(Teff)):
            mags[i]=self.SolBol - 2.5*np.expand_dims(logL[i],1) - BCs[i]
        return mags

    def table_check(self):
        count=0
        for i in range(1,len(self.grid)):
            Teff1=self.grid[i-1][0]
            Teff2=self.grid[i][0]
            if Teff1 == Teff2:
                logg1=self.grid[i-1][1]
                logg2=self.grid[i][1]
                dg=logg2-logg1
                if logg2 > logg1 and dg == 0.5:
                    pass
                else:
                    print(Teff1, Teff2)
                    print(logg1, logg2)
                    index=np.where((self.logg>logg1)&(self.logg<logg2))
                    gnew=self.logg[index]
                    tnew=Teff1
                    result=self.table_interp(tnew,gnew)[0][0]
                    print(result)
                    count+=1
        return count
