from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt

class ISO:
    
    """
    
    Reads in MIST isochrone files.

    
    """
    
    def __init__(self, filename, verbose=True):
    
        """
        
        Args:
            filename: the name of .iso file.
        
        Usage:
            >> iso = read_mist_models.ISO('MIST_v1.0_feh_p0.00_afe_p0.0_vvcrit0.4.iso')
            >> age_ind = iso.age_index(8.0)
            >> logTeff = iso.isos[age_ind]['log_Teff']
            >> logL = iso.isos[age_ind]['log_L']
            >> plt.plot(logTeff, logL) #plot the HR diagram for logage = 8.0
            
        Attributes:
            version     Dictionary containing the MIST and MESA version numbers.
            abun        Dictionary containing Yinit, Zinit, [Fe/H], and [a/Fe] values.
            rot         Rotation in units of surface v/v_crit.
            ages        List of ages.
            num_ages    Number of isochrones.
            hdr_list    List of column headers.
            isos        Data.
            
        """
        
        self.filename = filename
        if verbose:
            print('Reading in: ' + self.filename)
            
        self.version, self.abun, self.rot, self.ages, self.num_ages, self.hdr_list, self.isos = self.read_iso_file()
        
    def read_iso_file(self):

        """

        Reads in the isochrone file.
        
        Args:
            filename: the name of .iso file.
        
        """
        
        #open file and read it in
        with open(self.filename) as f:
            content = [line.split() for line in f]
        version = {'MIST': content[0][-1], 'MESA': content[1][-1]}
        abun = {content[3][i]:float(content[4][i]) for i in range(1,5)}
        rot = float(content[4][-1])
        num_ages = int(content[6][-1])
        
        #read one block for each isochrone
        iso_set = []
        ages = []
        counter = 0
        data = content[8:]
        for i_age in range(num_ages):
            #grab info for each isochrone
            num_eeps = int(data[counter][-2])
            num_cols = int(data[counter][-1])
            hdr_list = data[counter+2][1:]
            formats = tuple([np.int32]+[np.float64 for i in range(num_cols-1)])
            iso = np.zeros((num_eeps),{'names':tuple(hdr_list),'formats':tuple(formats)})
            #read through EEPs for each isochrone
            for eep in range(num_eeps):
                iso_chunk = data[3+counter+eep]
                iso[eep]=tuple(iso_chunk)
            iso_set.append(iso)
            ages.append(iso[0][1])
            counter+= 3+num_eeps+2
        return version, abun, rot, ages, num_ages, hdr_list, iso_set  
        
    def age_index(self, age):
    
        """

        Returns the index for the user-specified age.
    
        Args:
            age: the age of the isochrone.
    
        """
    
        diff_arr = abs(np.array(self.ages) - age)
        age_index = np.where(diff_arr == min(diff_arr))[0][0]
    
        if ((age > max(self.ages)) | (age < min(self.ages))):
            print('The requested age is outside the range. Try between ' + str(min(self.ages)) + ' and ' + str(max(self.ages)))
        
        return age_index
    		
class ISOCMD:
    
    """
    
    Reads in MIST CMD files.

    
    """
    
    def __init__(self, filename, verbose=True):
    
        """
        
        Args:
            filename: the name of .iso.cmd file.
        
        Usage:
            >> isocmd = read_mist_models.ISOCMD('MIST_v1.0_feh_p0.00_afe_p0.0_vvcrit0.4.iso.cmd')
            >> age_ind = isocmd.age_index(7.0)
            >> B = isocmd.isocmds[age_ind]['Bessell_B']
            >> V = isocmd.isocmds[age_ind]['Bessell_V']
            >> plt.plot(B-V, V) #plot the CMD for logage = 7.0
        
        Attributes:
            version         Dictionary containing the MIST and MESA version numbers.
            photo_sys       Photometric system. 
            abun            Dictionary containing Yinit, Zinit, [Fe/H], and [a/Fe] values.
            Av_extinction   Av for CCM89 extinction.
            rot             Rotation in units of surface v/v_crit.
            ages            List of ages.
            num_ages        Number of ages.
            hdr_list        List of column headers.
            isocmds         Data.
        
        """
        
        self.filename = filename
        if verbose:
            print('Reading in: ' + self.filename)
            
        self.version, self.photo_sys, self.abun, self.Av_extinction, self.rot, self.ages, self.num_ages, self.hdr_list, self.isocmds = self.read_isocmd_file()
    
    def read_isocmd_file(self):

        """

        Reads in the cmd file.
        
        Args:
            filename: the name of .iso.cmd file.
        
        """
        
        #open file and read it in
        with open(self.filename) as f:
            content = [line.split() for line in f]
        version = {'MIST': content[0][-1], 'MESA': content[1][-1]}
        photo_sys = ' '.join(content[2][4:])
        abun = {content[4][i]:float(content[5][i]) for i in range(1,5)}
        rot = float(content[5][-1])
        num_ages = int(content[7][-1])
        Av_extinction = float(content[8][-1])
        
        #read one block for each isochrone
        isocmd_set = []
        ages = []
        counter = 0
        data = content[10:]
        for i_age in range(num_ages):
            #grab info for each isochrone
            num_eeps = int(data[counter][-2])
            num_cols = int(data[counter][-1])
            hdr_list = data[counter+2][1:]
            formats = tuple([np.int32]+[np.float64 for i in range(num_cols-1)])
            isocmd = np.zeros((num_eeps),{'names':tuple(hdr_list),'formats':tuple(formats)})
            #read through EEPs for each isochrone
            for eep in range(num_eeps):
                isocmd_chunk = data[3+counter+eep]
                isocmd[eep]=tuple(isocmd_chunk)
            isocmd_set.append(isocmd)
            ages.append(isocmd[0][1])
            counter+= 3+num_eeps+2
        return version, photo_sys, abun, Av_extinction, rot, ages, num_ages, hdr_list, isocmd_set

    def age_index(self, age):
        
        """

        Returns the index for the user-specified age.
        
        Args:
            age: the age of the isochrone.
        
        """
        
        diff_arr = abs(np.array(self.ages) - age)
        age_index = np.where(diff_arr == min(diff_arr))[0][0]
        
        if ((age > max(self.ages)) | (age < min(self.ages))):
            print('The requested age is outside the range. Try between ' + str(min(self.ages)) + ' and ' + str(max(self.ages)))
            
        return age_index

        
class EEP:
    
    """
    
    Reads in and plots MESA EEP files.

    
    """
    
    def __init__(self, filename, verbose=True):
        
        """
        
        Args:
            filename: the name of .track.eep file.
        
        Usage:
            >> eep = read_mist_models.EEP('00200M.track.eep')
            >> logTeff, center_h1, mdot = eep.eeps['log_Teff'], eep['center_h1'], eep['star_mdot']
            
        Attributes:
            version         Dictionary containing the MIST and MESA version numbers.
            abun            Dictionary containing Yinit, Zinit, [Fe/H], and [a/Fe] values.
            rot             Rotation in units of surface v/v_crit.
            minit           Initial mass in solar masses.
            hdr_list        List of column headers.
            eeps            Data.
            
        """
                        
        self.filename = filename
        if verbose:
            print('Reading in: ' + self.filename)
                        
        self.version, self.abun, self.rot, self.minit, self.hdr_list, self.eeps = self.read_eep_file()
        
    def read_eep_file(self):
        
        """

        Reads in the EEP file.
        
        Args:
            filename: the name of .track.eep file.
                
        """
        
        eeps = np.genfromtxt(self.filename, skip_header=11, names=True)
        
        with open(self.filename) as f:
            content = [line.split() for line in f]

        version = {'MIST': content[0][-1], 'MESA': content[1][-1]}
        abun = {content[3][i]:float(content[4][i]) for i in range(1,5)}
        rot = float(content[4][-1])
        minit = float(content[7][1])
        hdr_list = content[11][1:]
        
        return version, abun, rot, minit, hdr_list, eeps
        		
    def plot_HR(self, fignum=0, phases=[], phasecolor=[], **kwargs):
        
        """

        Plots the HR diagram.

        Args:
            None.
            
        Keywords:
            accepts matplotlib keywords: color, linestyle, linewidth, etc.
            keyword: fignum, phase*, phasecolor
            
            * Following the FSPS notation,
            * PMS:-1 ; MS:0 ; SGB+RGB:2 ; CHeB:3 ; EAGB:4 ; TPAGB:5 ; post-AGB:6 ; WR:9
    
        Usage:
            >> eep.plot_HR(fignum=3)
            >> eep.plot_HR(phase=[0, 2], phasecolor=['Gray', 'Blue']) #highlight the MS and RGB phases in gray and blue.
        
        """
        
        x = self.eeps['log_Teff']
        y = self.eeps['log_L']
        
        fig = plt.figure(fignum)
        plt.xlabel('log(Teff) [K]', fontsize=22)
        plt.ylabel('log(L/Lsun)', fontsize=22)
        
        ax = fig.add_subplot(111)
        ax.plot(x, y, **kwargs)
        ax.axis([max(x)+0.2, min(x)-0.2, min(y)-0.2, max(y)+0.2])

        if len(phases) >= 0:
            if len(phases) != len(phasecolor):
                print('The length of the phase and phasecolor array must be identical.')
                return
            for i_p, phase in enumerate(phases):
                p = self.eeps['phase']
                p_ind = np.where(p == phase)
                if len(p_ind) > 0:
                    if phasecolor == '':
                        ax.plot(x[p_ind], y[p_ind], linewidth=4.0, alpha=0.5)
                    else:
                        ax.plot(x[p_ind], y[p_ind], color=phasecolor[i_p], linewidth=4.0, alpha=0.5)

class EEPCMD:
    
    """
    
    Reads in and plots MESA EEP CMD files.

    
    """
    
    def __init__(self, filename, verbose=True):
        
        """
        
        Args:
            filename: the name of .track.eep.cmd file.
        
        Usage:
            >> eepcmd = read_mist_models.EEPCMD('00200M.track.eep.cmd')
            >> B, V, mdot = eepcmd.eepcmds['Bessell_B'], eep['Bessell_V'], eep['star_mdot']
            
        Attributes:
            version         Dictionary containing the MIST and MESA version numbers.
            photo_sys       Photometric system.
            abun            Dictionary containing Yinit, Zinit, [Fe/H], and [a/Fe] values.
            rot             Rotation in units of surface v/v_crit.
            minit           Initial mass in solar masses.
            hdr_list        List of column headers.
            Av_extinction   Av for CCM89 extinction.
            eepcmds         Data.
            
        """
                        
        self.filename = filename
        if verbose:
            print('Reading in: ' + self.filename)
                        
        self.version, self.photo_sys, self.abun, self.rot, self.minit, self.Av_extinction, self.hdr_list, self.eepcmds = self.read_eepcmd_file()
        
    def read_eepcmd_file(self):
        
        """

        Reads in the EEP CMD file.
        
        Args:
            filename: the name of .eep.cmd file.
                
        """
        
        eepcmds = np.genfromtxt(self.filename, skip_header=14, names=True)
        
        with open(self.filename) as f:
            content = [line.split() for line in f]

        version = {'MIST': content[0][-1], 'MESA': content[1][-1]}
        photo_sys = ' '.join(content[2][4:])
        abun = {content[4][i]:float(content[5][i]) for i in range(1,5)}
        rot = float(content[5][-1])
        minit = float(content[8][1])
        Av_extinction = float(content[11][-1])
        hdr_list = content[14][1:]
        
        return version, photo_sys, abun, rot, minit, Av_extinction, hdr_list, eepcmds
        		
    def plot_CMD(self, filters, fignum=0, phases=[], phasecolor=[], **kwargs):
        
        """

        Plots the CMD diagram.

        Args:
            filters: a list of three filters, ['filter1', 'filter2', 'filter3']. x-axis: 'filter1'-'filter2', y-axis: 'filter3'
            
        Keywords:
            accepts matplotlib keywords: color, linestyle, linewidth, etc.
            keyword: fignum, phase*, phasecolor
            
            * Following the FSPS notation,
            * PMS:-1 ; MS:0 ; SGB+RGB:2 ; CHeB:3 ; EAGB:4 ; TPAGB:5 ; post-AGB:6 ; WR:9
    
        Usage:
            >> eepcmd.plot_CMD(['Bessell_B', 'Bessell_V', 'Bessell_V'], fignum=3)
        """
        
        try:
            x1 = self.eepcmds[filters[0]]
        except:
            print(filters[0]) + ' does not appear in this file.'
            return
        try:
            x2 = self.eepcmds[filters[1]]
        except:
            print(filters[1]) + ' does not appear in this file.'
            return
        try:
            y = self.eepcmds[filters[2]]
        except:
            print(filters[2]) + ' does not appear in this file.'
            return
        
        fig = plt.figure(fignum)
        plt.xlabel(' '.join(filters[0].split('_')) + '-' + ' '.join(filters[1].split('_')), fontsize=22)
        plt.ylabel(' '.join(filters[2].split('_')), fontsize=22)
        
        ax = fig.add_subplot(111)
        ax.plot(x1-x2, y, **kwargs)
        ax.axis([min(x1-x2)-0.2, max(x1-x2)+0.2, max(y)+0.2, min(y)-0.2])

        if len(phases) >= 0:
            if len(phases) != len(phasecolor):
                print('The length of the phase and phasecolor array must be identical.')
                return
            for i_p, phase in enumerate(phases):
                p = self.eepcmds['phase']
                p_ind = np.where(p == phase)
                if len(p_ind) > 0:
                    if phasecolor == '':
                        ax.plot(x1[p_ind]-x2[p_ind], y[p_ind], linewidth=4.0, alpha=0.5)
                    else:
                        ax.plot(x1[p_ind]-x2[p_ind], y[p_ind], color=phasecolor[i_p], linewidth=4.0, alpha=0.5)

        