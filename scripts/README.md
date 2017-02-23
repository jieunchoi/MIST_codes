# scripts

## calc_xyz.py
Computes H1, H2, He3, and He4 for an input metallicity ([Fe/H] or Z). Assumes protosolar abundances from Asplund+2009, Y_BBN from Planck 2015, H2/H1 from Asplund+2009, and He3/He4 from Mahaffy+1998. Can be used as a stand-alone code.

Example Usage: <code>H1, H2, He3, He4, Z = calc_xyz.calc_xyz(-1.0, input_feh=True)</code>

**Deprecated. As of MIST v2.0 we use <code>initial_xa_calculator</code> to get the initial abundances for a given [Fe/H] and [a/Fe].

## make_blend_input_file.py
Generates the input file necessary to run the <code>./blend_eeps</code> executable in the iso package. It has the relevant mass range hard-coded in. In practice, the mass range and the functional form for the blending weights can be modified. Not intended for stand-alone use.

## make_eeps_isos.py
Runs the executables from the iso package (e.g., <code>./make_eep</code>). Creates the necessary input files, makes EEPs, blends the EEPS over the transition mass range, generates a list of incomplete EEPS, and interpolates new tracks for the incomplete EEPS. Not intended for stand-alone use.

## make_iso_input_file.py
Generates the input files necessary to run the <code>./make_eeps</code>, <code>./make_iso</code>, and <code>./eep_interp_met</code> executables in the iso package. For <code>./make_iso</code>, the age spacing is currently hardcoded (log(Age) = 5.0 to 10.3 in steps of 0.05), but this can be changed. Not intended for stand-alone use.

## make_inlist_inputs.py
1. Specifies the grid of masses, which can be modified by the user.

2. Generates the mass-appropriate values to replace the <code><<PLACEHOLDER>></code> input fields in the template MESA inlist files. More input fields, e.g., <code>mixing_length_alpha</code>, can be added as needed.
    
Not intended for stand-alone use.


## make_replacements.py
Takes the dictionary output from <code>make_inlist_inputs.py</code> and modifies the template MESA inlist file for each mass in the grid.

Not intended for stand-alone use.

## make_slurm_sh.py
Generates a SLURM file for each model in the grid using the template <code>mesafiles/SLURM_MISTgrid.sh</code>. The run time is hard-coded in but can be modified. Can be used as a stand-alone code, but the name of the model needs to be specified in the <code>XXXXXM.inlist</code> format.

Example Usage: <code>make_slurm_sh.make_slurm_sh(00100M.inlist, my_first_MIST_grid/00100M_dir, mesafiles/SLURM_MISTgrid.sh)</code>

## mesa_hist_trim.py
Processes the raw output MESA history data files to remove the repeated model steps (this can happen due to retries and backups) and scribbly numerical features in the post-AGB phase. The post-AGB features are selected to be those that have large d(logL)/dt and d(logTeff)/dt, i.e., model points that jump around erratically on very short timescales in the HR diagram. The latter is for cosmetic reasons that help during the EEP and isochrone construction. Can be used as a stand-alone code.

Example Usage: <code>mesa_hist_trim.trim_file('1M_history.data')</code>

## mesa_plot_grid.py
Uses <code>read_mist_models.py</code> to generate pdf files of HRD plots for all of the models in the input grid. Can plot both EEP tracks (<code>plot_HRD</code>) and isochrones (<code>plot_iso</code>). <code>plot_combine</code> can be used to combine the individual pdf files to create a single pdf file for each grid. Can be used as a stand-alone code.

Example Usage: <code>mesa_plot_grid.plot_iso('my_first_MIST_grid')</code>

## mist2fsps.py
Reads in the <code>.iso</code> MIST isochrone file and writes out a file that can be used in Charlie Conroy's [FSPS package](https://github.com/cconroy20/fsps). Can be used as a stand-alone code.

Example Usage: <code>mist2fsps.write_fsps_iso('my_first_MIST_grid_.iso')</code>

## read_mist_models.py
Plots <code>.iso</code>, <code>.iso.cmd</code>, <code>.eep</code>,and <code>.eep.cmd</code> MIST files.

Can be used as a stand-alone code.

See [here](http://waps.cfa.harvard.edu/MIST/read_mist_models_demo.html) for a detailed demo.

## reduce_jobs_utils.py
Contains the helper functions for <code>reduce_jobs.py</code>. Can be used as a stand-alone code.

Example Usage:
* <code>reduce_jobs_utils.gen_summary('my_first_MIST_grid_raw')</code>
Creates a summary file <code>tracks_summary.txt</code> for each mass model in a grid. The columns include status (OK vs. FAILED), the reason for failure, and the run time (to get CPU hours, need to x by number of CPUs).

* <code>reduce_jobs_utils.sort_histfiles('my_first_MIST_grid_raw')</code>
Copies over the raw MESA history files from the individual mass directories (e.g., <code>my_first_MIST_grid_raw/00100M_dir/LOGS/1M_history.data</code>) to the <code>my_first_MIST_grid/tracks</code> directory. Processes the MESA history file by calling <code>mesa_hist_trim.trim_file</code>.

* <code>reduce_jobs_utils.save_inlists</code>
Copies over the MESA inlist files from the individual mass directories (e.g., <code>my_first_MIST_grid_raw/00100M_dir/inlist_project</code>) to the <code>my_first_MIST_grid/inlists</code> directory. Renames the inlist files to e.g., <code>00100M.inlist</code>.

* <code>reduce_jobs_utils.save_lowM_photo_model</code>
Copies over the <code>.mod</code> and <code>.photo</code> files saved at the post-AGB phase from the individual mass directories (e.g., <code>my_first_MIST_grid_raw/00100M_dir/00100M_pAGB.mod</code>) to the <code>my_first_MIST_grid/models_photos</code> directory.


## reformat_mass_name.py
Formats an input float-type mass value to a uniform 5-character-long string. Can be used as a stand-alone code.

Example Usage: string_name = <code>reformat_massname.reformat_massname(0.34)</code>

