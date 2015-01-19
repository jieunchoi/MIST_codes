! ***********************************************************************
!
!   Copyright (C) 2010  Bill Paxton
!
!   this file is part of mesa.
!
!   mesa is free software; you can redistribute it and/or modify
!   it under the terms of the gnu general library public license as published
!   by the free software foundation; either version 2 of the license, or
!   (at your option) any later version.
!
!   mesa is distributed in the hope that it will be useful, 
!   but without any warranty; without even the implied warranty of
!   merchantability or fitness for a particular purpose.  see the
!   gnu library general public license for more details.
!
!   you should have received a copy of the gnu library general public license
!   along with this software; if not, write to the free software
!   foundation, inc., 59 temple place, suite 330, boston, ma 02111-1307 usa
!
! ***********************************************************************
 
      module run_star_extras

      use star_lib
      use star_def
      use const_def
	  use crlibm_lib
      ! use run_star_support
      
      implicit none
      
	  real(dp) :: original_diffusion_dt_limit
	  
      ! these routines are called by the standard run_star check_model
      contains
    
	      subroutine extras_controls(s, ierr)
	         type (star_info), pointer :: s
	         integer, intent(out) :: ierr
	         ierr = 0
			 
			 original_diffusion_dt_limit = s% diffusion_dt_limit			          
			 s% other_wind => VW_superwind
	      end subroutine extras_controls
            
	      integer function extras_startup(s, id, restart, ierr)

             type (star_info), pointer :: s
	         integer, intent(in) :: id
	         logical, intent(in) :: restart
	         integer, intent(out) :: ierr
		     real(dp) :: core_ov_full_on, core_ov_full_off, frac, rot_full_off, rot_full_on, frac2, vct30, vct100
			 
	         ierr = 0
	         extras_startup = 0
	         if (.not. restart) then
	            call alloc_extra_info(s)
	         else ! it is a restart
	            call unpack_extra_info(s)
	         end if
			 
			 !set OPACITIES: Zbase for Type 2 Opacities automatically to the Z for the star
			 s% Zbase = 1.0 - (s% job% initial_h1 + s% job% initial_h2 + &
			 s% job% initial_he3 + s% job% initial_he4)
			 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
			 write(*,*) 'Zbase for Type 2 Opacities: ', s% Zbase
			 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

			!set CONVECTIVE OVERSHOOT: extra param are set in inlist: star_job
			 !core_ov_full_off = s% job% extras_rpar(1) !1.1
			 !core_ov_full_on = s% job% extras_rpar(2) !1.7
			 !
	         !if (s% star_mass < core_ov_full_off) then
			 !	 frac = 0
	         !else if (s% star_mass >= core_ov_full_off .and. s% star_mass <= core_ov_full_on) then
			 !	 frac = (s% star_mass - core_ov_full_off) / &
	         !           (core_ov_full_on - core_ov_full_off)
	         !    frac = 0.5d0*(1 - cos(pi*frac))
			 !else
			 !    frac = 1d0
	         !end if

             frac = 1d0
	         s% overshoot_f_above_burn_h = frac * s% overshoot_f_above_burn_h
			 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
			 write(*,*) 'core convective overshoot fraction: ', frac
			 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

			 !set ROTATION: extra param are set in inlist: star_job
			 rot_full_off = s% job% extras_rpar(3) !1.2
			 rot_full_on = s% job% extras_rpar(4) !1.8
			 
			 if (s% job% extras_rpar(5) > 0.0) then
	         	if (s% star_mass < rot_full_off) then
			 		 frac2 = 0
			 		 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
			 		 write(*,*) 'no rotation'
			 		 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
	         	else if (s% star_mass >= rot_full_off .and. s% star_mass <= rot_full_on) then
			 		 frac2 = (s% star_mass - rot_full_off) / &
	         	           (rot_full_on - rot_full_off)
	         	    frac2 = 0.5d0*(1 - cos(pi*frac2))
			 		 s% job% set_near_zams_omega_div_omega_crit_steps = 10
			 		 s% job% new_omega_div_omega_crit = s% job% extras_rpar(5) * frac2
			 		 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
			 		 write(*,*) 'new omega_div_omega_crit, fraction', s% job% new_omega_div_omega_crit, frac2
			 		 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
			 	else
			 		 frac2 = 1.0
			 		 s% job% set_near_zams_omega_div_omega_crit_steps = 10
			 		 s% job% new_omega_div_omega_crit = s% job% extras_rpar(5) * frac2 !nominally 0.4
			 		 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
			 		 write(*,*) 'new omega_div_omega_crit, fraction', s% job% new_omega_div_omega_crit, frac2
			 		 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
	         	end if
			else
				write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
				write(*,*) 'no rotation'
				write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
			end if
				

			 !set VARCONTROL: for massive stars, turn up varcontrol gradually to help them evolve
			 vct30 = 2e-4
			 vct100 = 3e-3
			 
			 if (s% initial_mass > 30.0) then
				 frac = (s% initial_mass-30.0)/(100.0-30.0)
				 frac = 0.5d0*(1 - cos(pi*frac))
				 s% varcontrol_target = vct30 + (vct100-vct30)*frac
				 
				 if (s% initial_mass > 100.0) then
					 s% varcontrol_target = vct100
				 end if
				 
				 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
				 write(*,*) 'varcontrol_target is set to ', s% varcontrol_target
				 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
			 end if
			 
	      end function extras_startup
      
	      ! returns either keep_going, retry, backup, or terminate.
	      integer function extras_check_model(s, id, id_extra)
	         type (star_info), pointer :: s
	         integer, intent(in) :: id, id_extra
             real(dp) :: envelope_mass_fraction, L_He, L_tot, orig_eta, target_eta, min_center_h1_for_diff
			 real(dp), parameter :: huge_dt_limit = 3.15d16 ! ~1 Gyr
			 real(dp), parameter :: new_varcontrol_target = 1d-3
	         extras_check_model = keep_going
			 
			 !increase VARCONTROL: increase varcontrol when the model hits the AGB phase
			 if ((s% initial_mass < 10) .and. (s% center_h1 < 1d-4) .and. (s% center_he4 < 1d-4)) then
				 if (s% varcontrol_target < new_varcontrol_target) then !only print the first time
					 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
					 write(*,*) 'increasing varcontrol to', new_varcontrol_target
					 write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
				 s% varcontrol_target = new_varcontrol_target
				 end if
			 end if
			 
			 !suppress LATE BURNING: turn off burning post-AGB			 
			 envelope_mass_fraction = 1d0 - max(s% he_core_mass, s% c_core_mass, s% o_core_mass)/s% star_mass
			 
			 L_He = s% power_he_burn*Lsun
			 L_tot = s% photosphere_L*Lsun
			 if (s% initial_mass < 10) then
				 if ((envelope_mass_fraction < 0.1) .and. (s% center_h1 < 1d-4) .and. (s% center_he4 < 1d-4) .and. (s% L_phot > 3.0)) then
					 if (s% category_factors(3) > 0) then !only print the first time
						 write(*,*) '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
						 write(*,*) 'now at post AGB phase, turning off all burning except for H'
						 write(*,*) '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
					 end if
					 s% category_factors(3:) = 0.0
				 end if
			 end if
			 
			 !define STOPPING CRITERION: stopping criterion for C burning, massive stars.
			 if ((s% center_h1 < 1d-4) .and. (s% center_he4 < 1d-4) .and. (s% center_c12 < 1d-4)) then
			   	 termination_code_str(t_xtra1) = 'central C12 mass fraction below 1e-4'
				 s% termination_code = t_xtra1
			   	 extras_check_model = terminate
			 end if
			 
			 !define STOPPING CRITERION: stopping criterion for TAMS, low mass stars.
			 if ((s% center_h1 < 1d-4) .and. (s% initial_mass < 0.6)) then
				 termination_code_str(t_xtra2) = 'central H1 mass fraction below 1e-4'
				 s% termination_code = t_xtra2
			   	 extras_check_model = terminate
			 end if
			 
			 !check DIFFUSION: to determine whether or not diffusion should happen
			 !no diffusion for fully convective, post-MS, and mega-old models 
             if(abs(s% mass_conv_core - s% star_mass) < 1d-2) then ! => fully convective
 	            s% diffusion_dt_limit = huge_dt_limit
		 		s% do_element_diffusion = .false.
			 else
 	        	s% diffusion_dt_limit = original_diffusion_dt_limit
				s% do_element_diffusion = .true.
			 end if
			 if (s% star_age > 5d10) then !50 Gyr is really old
				s% diffusion_dt_limit = huge_dt_limit
				s% do_element_diffusion = .false.
			 end if
			 min_center_h1_for_diff = 1d-4
     		 if (s% center_h1 < min_center_h1_for_diff) then
				s% do_element_diffusion = .false.
			 end if
				
	      end function extras_check_model
		                                                                                                                                                                      
	      integer function how_many_extra_history_columns(s, id, id_extra)
	         type (star_info), pointer :: s
	         integer, intent(in) :: id, id_extra
	         how_many_extra_history_columns = 0
	      end function how_many_extra_history_columns
      
	      subroutine data_for_extra_history_columns(s, id, id_extra, n, names, vals, ierr)
	         type (star_info), pointer :: s
	         integer, intent(in) :: id, id_extra, n
	         character (len=maxlen_history_column_name) :: names(n)
	         real(dp) :: vals(n)
	         integer, intent(out) :: ierr

	         ierr = 0
	      end subroutine data_for_extra_history_columns
      
	      integer function how_many_extra_profile_columns(s, id, id_extra)
	         type (star_info), pointer :: s
	         integer, intent(in) :: id, id_extra
	         how_many_extra_profile_columns = 0
	      end function how_many_extra_profile_columns
      
	      subroutine data_for_extra_profile_columns(s, id, id_extra, n, nz, names, vals, ierr)
	         type (star_info), pointer :: s
	         integer, intent(in) :: id, id_extra, n, nz
	         character (len=maxlen_profile_column_name) :: names(n)
	         real(dp) :: vals(nz,n)
	         integer, intent(out) :: ierr
	         integer :: k
	         ierr = 0
          end subroutine data_for_extra_profile_columns
      
	      ! returns either keep_going or terminate.
	      ! note: cannot request retry or backup; extras_check_model can do that.
	      integer function extras_finish_step(s, id, id_extra)
	         type (star_info), pointer :: s
	         integer, intent(in) :: id, id_extra
	         integer :: ierr
	         extras_finish_step = keep_going
	         call store_extra_info(s)

			 !set NET: evolve 100 steps then change to approx21_extras net
             if (s% model_number == 100) then
				
				write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
				write(*,*) 'changing net to ', s% job% extras_cpar(1)
                write(*,*) 'switching from simple photosphere to ', s% job% extras_cpar(2)
				write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

                call star_change_to_new_net(id, .true., s% job% extras_cpar(1), ierr)
                s% which_atm_option = s% job% extras_cpar(2)
				
			 endif
	      end function extras_finish_step
      
	      subroutine VW_superwind(id, Lsurf, Msurf, Rsurf, Tsurf, w, ierr)
	         use star_def
	         integer, intent(in) :: id
	         real(dp), intent(in) :: Lsurf, Msurf, Rsurf, Tsurf ! surface values (cgs)
	         ! NOTE: surface is outermost cell. not necessarily at photosphere.
	         ! NOTE: don't assume that vars are set at this point.
	         ! so if you want values other than those given as args,
	         ! you should use values from s% xh(:,:) and s% xa(:,:) only.
	         ! rather than things like s% Teff or s% lnT(:) which have not been set yet.
	         real(dp), intent(out) :: w ! wind in units of Msun/year (value is >= 0)
	         integer, intent(out) :: ierr
			 real(dp) :: logP, P
			 
			 !Vassiliadis and Wood 1993 for superwind
			 
	         logP = -2.07 + 1.94*log10_cr(Rsurf/Rsun)-0.9*log10_cr(Msurf/Msun) !in days
			 P = pow_cr(10d0, logP)
			 w = pow_cr(10d0, -11.4+0.0125*(P - 100.0*(Msurf/Msun - 2.5)))
			 
	         ierr = 0
	      end subroutine VW_superwind
		  
	      subroutine extras_after_evolve(s, id, id_extra, ierr)
	         type (star_info), pointer :: s
	         integer, intent(in) :: id, id_extra
	         integer, intent(out) :: ierr
	         ierr = 0
	      end subroutine extras_after_evolve
            
	      subroutine alloc_extra_info(s)
	         integer, parameter :: extra_info_alloc = 1
	         type (star_info), pointer :: s
	         call move_extra_info(s,extra_info_alloc)
	      end subroutine alloc_extra_info
      
	      subroutine unpack_extra_info(s)
	         integer, parameter :: extra_info_get = 2
	         type (star_info), pointer :: s
	         call move_extra_info(s,extra_info_get)
	      end subroutine unpack_extra_info
            
	      subroutine store_extra_info(s)
	         integer, parameter :: extra_info_put = 3
	         type (star_info), pointer :: s
	         call move_extra_info(s,extra_info_put)
	      end subroutine store_extra_info
      
	      subroutine move_extra_info(s,op)
	         integer, parameter :: extra_info_alloc = 1
	         integer, parameter :: extra_info_get = 2
	         integer, parameter :: extra_info_put = 3
	         type (star_info), pointer :: s
	         integer, intent(in) :: op
         
	         integer :: i, j, num_ints, num_dbls, ierr
         
	         i = 0
	         ! call move_int or move_flg    
	         num_ints = i
         
	         i = 0
	         ! call move_dbl       
         
	         num_dbls = i
         
	         if (op /= extra_info_alloc) return
	         if (num_ints == 0 .and. num_dbls == 0) return
         
	         ierr = 0
	         call star_alloc_extras(s% id, num_ints, num_dbls, ierr)
	         if (ierr /= 0) then
	            write(*,*) 'failed in star_alloc_extras'
	            write(*,*) 'alloc_extras num_ints', num_ints
	            write(*,*) 'alloc_extras num_dbls', num_dbls
	            stop 1
	         end if
         
	         contains
         
	         subroutine move_dbl(dbl)
	            real(dp) :: dbl
	            i = i+1
	            select case (op)
	            case (extra_info_get)
	               dbl = s% extra_work(i)
	            case (extra_info_put)
	               s% extra_work(i) = dbl
	            end select
	         end subroutine move_dbl
         
	         subroutine move_int(int)
	            integer :: int
	            i = i+1
	            select case (op)
	            case (extra_info_get)
	               int = s% extra_iwork(i)
	            case (extra_info_put)
	               s% extra_iwork(i) = int
	            end select
	         end subroutine move_int
         
	         subroutine move_flg(flg)
	            logical :: flg
	            i = i+1
	            select case (op)
	            case (extra_info_get)
	               flg = (s% extra_iwork(i) /= 0)
	            case (extra_info_put)
	               if (flg) then
	                  s% extra_iwork(i) = 1
	               else
	                  s% extra_iwork(i) = 0
	               end if
	            end select
	         end subroutine move_flg
      
	      end subroutine move_extra_info
   	   
      end module run_star_extras
