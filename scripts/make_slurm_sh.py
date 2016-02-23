"""

Generates the Odyssey cluster SLURM file for each model.

Args:
    inlistname: name of the inlist
    inlistdir: name of the inli
    runbasefile: the name of the template shell script
    
Returns:
    the name of the SLURM file

"""

def make_slurm_sh(inlistname, inlistdir, runbasefile):
    
    #Read the contents of the base file 
    infile = open(runbasefile, 'r')
    infile_contents = infile.read()
    infile.close()

    #Replace the keys with appropriate values
    runname = inlistname.strip(".inlist")
    replaced_contents = infile_contents.replace('<<RUNNAME>>', runname)
    replaced_contents = replaced_contents.replace('<<DIRNAME>>', inlistdir)

    #Find the mass of the model to assign appropriate runtime
    massval = int(runname.split('M')[0])/100.0
    if (massval <= 0.6):
        replaced_contents = replaced_contents.replace('<<RUNTIME>>', '30:00:00')
    else:
        replaced_contents = replaced_contents.replace('<<RUNTIME>>', '120:00:00')
    runfile = runname+'_run.sh'

    #Write the new shell script
    outfile = open(runfile, 'w+')
    outfile.write(replaced_contents)
    outfile.close()

    return runfile
