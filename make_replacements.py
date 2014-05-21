"""
This replaces various 'keys' (such as mass) in the 
template inlist with corresponding values for each model.
"""

import numpy as np
import os
import itertools
import reformat_massname


def make_replacements(replist, direc='inlists', file_base='inlist_project_base', \
	name_str='', clear_direc=False):
	
	if not os.path.isfile(file_base):
		raise Exception("Base file does not exist!")
		
	if not os.path.isdir(direc):
		os.mkdir(direc)

	elif clear_direc and not os.path.abspath(direc) == os.path.abspath('.'):
		print "Removing existing files in " + direc
		for file in os.listdir(direc):
			os.remove(os.path.join(direc, file))

	keys = [ replist[i][0] for i in xrange(len(replist)) ]
	vals = [ replist[i][1] for i in xrange(len(replist)) ]
	
	perms = zip(vals[0], vals[1], vals[2])
	#perms = list(itertools.product(*vals))

	infile = open(file_base, 'r')
	file_base_contents = infile.read()
	infile.close()
	
	for val_vec in perms:
		file_mod = file_base_contents
		inlist_file = name_str
		for i in xrange(len(keys)):
			file_mod = file_mod.replace(keys[i], str(val_vec[i]))
			if keys[i] == "<<MASS>>":
				inlist_file = inlist_file.replace(keys[i], reformat_massname.reformat_massname(val_vec[i]))
			else:
				inlist_file = inlist_file.replace(keys[i], val_vec[i])
		
		inlist_file = os.path.join(direc, inlist_file)

		outfile = open(inlist_file, 'w')
		outfile.write(file_mod)
		outfile.close()
	
