# MIST_codes
Routines to run and process a grid of MIST models on the Odyssey computing cluster at Harvard.

## Prerequisites
### Software
* a customized version of MESA v9691 : http://mesa.sourceforge.net/ (http://waps.cfa.harvard.edu/MIST/data/tarballs_v1.0/MESA_files.tar.gz)
* mesasdk (for MESA installation) : http://www.astro.wisc.edu/~townsend/static.php?ref=mesasdk
* iso : https://github.com/dotbot2000/iso
* initial_xa_calculator : https://github.com/dotbot2000/initial_xa_calculator

### env variables
The following environment variables must be set in your e.g., <code>.bashrc</code>, <code>.bash_profile</code>.

* <code>$ISO_DIR</code> = path to the iso directory.
* <code>$MIST_CODE_DIR</code> = path to this directory.
* <code>$XA_CALC_DIR</code> = path to the abudance calculator directory.
* <code>$MIST_GRID_DIR</code> = path to where the MIST models will be computed.
* <code>$STORE_DIR</code> = path to where the processed tarballs will be stored.
* <code>$MESAWORK_DIR</code> = path to the directory where <code>inlists</code> and <code>cleanworkdir</code> will be stored.

<code>inlists</code> is a directory where the MESA inlists that are generated for each MIST grid are stored. The inlists are then copied to individual mass directories for each MIST grid.
<code>cleanworkdir</code> is copy of the <code>mesa/star/work</code> directory. This serves as the template directory for each mass directory.
	
## Getting Started
The two high-level scripts are <code>submit_jobs.py</code> and <code>reduce_jobs.py</code>. Files related to MESA, such as the template inlists, can be found in the <code>mesafiles</code> directory. <code>scripts</code> contains all the necessary helper functions.

### Submitting a grid of models
<code>./submit_jobs.py my_first_MIST_grid -1.0 0.0</code>
This will run a grid of models with [Fe/H]=-1 and [a/Fe]=0.

It creates a directory named <code>my_first_MIST_grid</code> in <code>$MIST_GRID_DIR</code>. This <code>my_first_MIST_grid</code> directory contains a number of subdirectories <code>XXXXXM_dir</code> for each mass, e.g., <code>00100M_dir</code> for a 1 Msun model. Each subdirectory is populated with everything, e.g., a customized <code>inlist</code>, that is required to run a single model. The <code>initial_xa_calculator</code> generates an input file of initial abundances for the user-supplied value of [Fe/H] and [a/Fe].

The choice of masses is set in <code>scripts/make_inlist_inputs.py</code>, and the input physics can be modified in <code>mesafiles/inlist_XXXXX</code> and <code>mesafiles/run_star_extras.f</code>, though doing so requires familiarity with MESA. The jobs are submitted using <code>SLURM</code>, where the exact choices of queue name, number of nodes, etc. can be set in the template file <code>mesafiles/SLURM_MISTgrid.sh</code> and <code>scripts/make_slurm_sh.py</code>.

The MESA history files are written out to <code>$MIST_GRID_DIR/my_first_MIST_grid/XXXXXM_dir/LOGS</code>. The MESA terminal output, which is useful for checking the computation progress in real-time, is found in <code>$MIST_GRID_DIR/my_first_MIST_grid/XXXXXM_dir/XXXXXM.o</code>. Any error messages are written out to <code>$MIST_GRID_DIR/my_first_MIST_grid/XXXXXM_dir/XXXXXM.e</code>.

### Processing a grid of models
<code>./reduce_jobs.py my_first_MIST_grid</code>
This will process the MESA history files and call Aaron Dotter's iso package to generate EEP tracks and isochrones.

This script goes through multiple steps.

1. It first renames the grid by attaching a <code>_raw</code> suffix, e.g., <code> my_first_MIST_grid_raw</code>. 
2. It creates a <code>my_first_MIST_grid</code>, which contains the subdirectories <code>eeps</code> <code>isochrones</code>, <code>inlists</code>, <code>plots</code>, and <code>models_photos</code>.
3. It copies over the MESA history files and renames them to <code>XXXXXM.track</code>. It cuts out any redundant model steps due to e.g., retries in the MESA computation and removes any features due to numerical noise that may occur during the post-AGB phase.
4. It analyzes the <code>XXXXXM.o</code> and <code>XXXXXM.e</code> files to generate a summary file, <code>tracks_summary.txt</code>, of all the individual MESA runs.
5. It copies over the individual inlists to <code>my_first_MIST_grid/inlists</code> and renames them to <code>XXXXXM.inlist</code>.
6. If there are any MESA photos or models saved during the computation to allow for convenient restarts, they are also saved to <code>models_photos</code> after being renamed <code>XXXXXM.mod</code> and <code>XXXXXM.photo</code>.
7. It calls the <code>iso</code> package to make the EEP files and isochrones. There is an option to choose between <code>basic</code> and <code>full</code>. As the names suggest, <code>full</code> is just more comprehensive and contains more MESA columns. See <code>mesafiles/my_history_columns_basic.list</code> and <code>mesafiles/my_history_columns_full.list</code> for more information.
8. It plots the individual EEPs and isochrones and saves them as pdfs (Optional).
9. It saves the original MESA history data files separately as <code>my_first_MIST_grid_tracks</code>. 
10. <code>my_first_MIST_grid_tracks</code>, <code>my_first_MIST_grid</code>, and  <code>my_first_MIST_grid_raw</code> are compressed and moved over to <code>$STORE_DIR</code> for permanent storage.
11. Everything <code>my_first_MIST_grid</code>-related is removed from <code>$MIST_GRID_DIR</code>.

See <code>scripts/README.md</code> for more information.
