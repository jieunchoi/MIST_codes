#!/usr/bin/env python

"""
This generates the MESA inlist files for a range of masses and BC conditions.
Future capability will include abundances as well.
"""

import sys
import numpy as np
import os
from make_replacements import make_replacements

runname=sys.argv[1]

work_dir = '/home/jchoi/pfs/mesawork/'
code_dir = '/home/jchoi/pfs/mesawork/MIST_codes/'
inlist_dir = '/home/jchoi/pfs/mesawork/inlists/inlists_'+runname

if __name__ == "__main__":
    
    massgrid = lambda i,f,step: np.linspace(i,f,round(((f-i)/step))+1.0)
    bigmassgrid = np.unique(np.hstack((np.array([0.08]), massgrid(0.1,2.0,0.05), massgrid(2.0,5.0,0.2),\
                                              massgrid(5,12,0.5), massgrid(12,20,1.0),\
                                              massgrid(20,40,2), massgrid(40,60,5), massgrid(60,150,10.0))
                                        ))

    verylow = np.where(bigmassgrid <= 0.25)
    low_diffBC = np.where((bigmassgrid >= 0.3) & (bigmassgrid <= 0.6))
    inter = np.where((bigmassgrid > 0.6) & (bigmassgrid < 10.0))
    high = np.where(bigmassgrid >= 10.0)

    bctablegrid = np.hstack((["grey_and_kap"]*(np.size(verylow)+np.size(low_diffBC)+np.size(inter)+np.size(high))))
    bclabelgrid = np.hstack((['']*(np.size(verylow)+np.size(low_diffBC)+np.size(inter)+np.size(high))))

#    bctablegrid = np.hstack((["tau_100_tables"]*np.size(verylow), ["tau_100_tables"]*np.size(low_diffBC),\
#["photosphere_tables"]*np.size(low_diffBC),["photosphere_tables"]*(np.size(inter)+np.size(high))))
#    bclabelgrid = np.hstack((['']*np.size(verylow), ['_tau100']*np.size(low_diffBC),\
#['_PT']*np.size(low_diffBC), ['']*(np.size(inter)+np.size(high))))

    bcindex = np.arange(0, np.size(bctablegrid))
    i1 = np.size(verylow)
    i2 = i1+np.size(low_diffBC) #*2
    i3 = i2+np.size(inter)
    i4 = i3+np.size(high)
    verylow_index = bcindex[:i1]
    low_diffBC_index = bcindex[i1:i2]
    inter_index = bcindex[i2:i3]
    high_index = bcindex[i3:i4]

    mapfunc = lambda var: np.str(int(var)) if var == int(var) else np.str(var)
    # list of [replacement string, values]s
    verylow_replist = [\
        ["<<MASS>>", map(mapfunc, bigmassgrid[verylow])],\
            ["<<BC_LABEL>>", list(bclabelgrid[verylow_index])],\
            ["<<BC_TABLE>>", list(bctablegrid[verylow_index])],\
        ]

    lowbc_replist = [\
        ["<<MASS>>", map(mapfunc, bigmassgrid[low_diffBC])]*2],\
            ["<<BC_LABEL>>", list(bclabelgrid[low_diffBC_index])],\
            ["<<BC_TABLE>>", list(bctablegrid[low_diffBC_index])],\
        ] 

    inter_replist = [\
        ["<<MASS>>", map(mapfunc, bigmassgrid[inter])],\
            ["<<BC_LABEL>>", list(bclabelgrid[inter_index])],\
            ["<<BC_TABLE>>", list(bctablegrid[inter_index])],\
        ]

    high_replist = [\
        ["<<MASS>>", map(mapfunc, bigmassgrid[high])],\
            ["<<BC_LABEL>>", list(bclabelgrid[high_index])],\
            ["<<BC_TABLE>>", list(bctablegrid[high_index])],\
        ]

    make_replacements(verylow_replist, direc=os.path.join(inlist_dir), file_base=os.path.join(code_dir+'inlist_low'), name_str='<<MASS>>M<<BC_LABEL>>.inlist', clear_direc=True)
    make_replacements(lowbc_replist, direc=os.path.join(inlist_dir), file_base=os.path.join(code_dir+'inlist_inter'), name_str='<<MASS>>M<<BC_LABEL>>.inlist')
    make_replacements(inter_replist, direc=os.path.join(inlist_dir), file_base=os.path.join(code_dir+'inlist_inter'), name_str='<<MASS>>M<<BC_LABEL>>.inlist')
    make_replacements(high_replist, direc=os.path.join(inlist_dir), file_base=os.path.join(code_dir+'inlist_high'), name_str='<<MASS>>M<<BC_LABEL>>.inlist')
