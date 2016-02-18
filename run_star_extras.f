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
      use rates_def
      use net_def
      
      implicit none
      
      real(dp) :: original_diffusion_dt_limit
      real(dp) :: burn_check = 0.0
      
!     these routines are called by the standard run_star check_model
      contains
      
      subroutine extras_controls(id, ierr)
      integer, intent(in) :: id
      integer, intent(out) :: ierr
      type (star_info), pointer :: s
      ierr = 0
      call star_ptr(id, s, ierr)
      if (ierr /= 0) return
      
      original_diffusion_dt_limit = s% diffusion_dt_limit
      !s% other_wind => Reimers_then_VW
      s% other_wind => Reimers_then_Blocker
      
      end subroutine extras_controls
      
      integer function extras_startup(id, restart, ierr)
      integer, intent(in) :: id
      logical, intent(in) :: restart
      integer, intent(out) :: ierr
      type (star_info), pointer :: s
      real(dp) :: core_ov_full_on, core_ov_full_off, frac, rot_full_off, rot_full_on, frac2, vct30, vct100
      ierr = 0
      call star_ptr(id, s, ierr)
      if (ierr /= 0) return
      extras_startup = 0
      if (.not. restart) then
         call alloc_extra_info(s)
      else                      ! it is a restart
         call unpack_extra_info(s)
      end if
      
!     set OPACITIES: Zbase for Type 2 Opacities automatically to the Z for the star
      s% Zbase = 1.0 - (s% job% initial_h1 + s% job% initial_h2 + &
      s% job% initial_he3 + s% job% initial_he4)
      write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
      write(*,*) 'Zbase for Type 2 Opacities: ', s% Zbase
      write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
      
!     set ROTATION: extra param are set in inlist: star_job
      rot_full_off = s% job% extras_rpar(1) !1.2
      rot_full_on = s% job% extras_rpar(2) !1.8
      
      if (s% job% extras_rpar(3) > 0.0) then
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
            s% job% new_omega_div_omega_crit = s% job% extras_rpar(3) * frac2
            write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
            write(*,*) 'new omega_div_omega_crit, fraction', s% job% new_omega_div_omega_crit, frac2
            write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
         else
            frac2 = 1.0
            s% job% set_near_zams_omega_div_omega_crit_steps = 10
            s% job% new_omega_div_omega_crit = s% job% extras_rpar(3) * frac2 !nominally 0.4
            write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
            write(*,*) 'new omega_div_omega_crit, fraction', s% job% new_omega_div_omega_crit, frac2
            write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
         end if
      else
         write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
         write(*,*) 'no rotation'
         write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
      end if
      
      
!     set VARCONTROL: for massive stars, turn up varcontrol gradually to help them evolve
      vct30 = 1e-4
      vct100 = 3e-3
      
      if (s% initial_mass > 30.0) then
         frac = (s% initial_mass-30.0)/(100.0-30.0)
         frac = 0.5d0*(1 - cos(pi*frac))
         s% varcontrol_target = vct30 + (vct100-vct30)*frac
         
         if (s% initial_mass > 100.0) then
            s% varcontrol_target = vct100
         end if
         
         !CONVERGENCE TEST CHANGING C
         s% varcontrol_target = s% varcontrol_target * 1.0 

         write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
         write(*,*) 'varcontrol_target is set to ', s% varcontrol_target
         write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
      end if
      
      end function extras_startup
      
!     returns either keep_going, retry, backup, or terminate.
      integer function extras_check_model(id, id_extra)
      integer, intent(in) :: id, id_extra
      integer :: ierr, r, burn_category
      real(dp) :: envelope_mass_fraction, L_He, L_tot, orig_eta, target_eta, min_center_h1_for_diff, critmass, feh
      real(dp) :: category_factors(num_categories)
      real(dp), parameter :: huge_dt_limit = 3.15d16 ! ~1 Gyr
      real(dp), parameter :: new_varcontrol_target = 1d-3
      real(dp), parameter :: Zsol = 0.0142
      type (star_info), pointer :: s
      type (Net_General_Info), pointer :: g
      character (len=strlen) :: photoname
      
      ierr = 0	 
      call star_ptr(id, s, ierr)
      if (ierr /= 0) return
      extras_check_model = keep_going
      
      ierr = 0
      call get_net_ptr(s% net_handle, g, ierr)
      if (ierr /= 0) stop 'bad handle'	  
      
!     increase VARCONTROL and MDOT: increase varcontrol and Mdot when the model hits the TPAGB phase
      if ((s% initial_mass < 10) .and. (s% center_h1 < 1d-4) .and. (s% center_he4 < 1d-4)) then
         !try turning up Mdot
         feh = log10_cr((1.0 - (s% job% initial_h1 + s% job% initial_h2 + s% job% initial_he3 + s% job% initial_he4))/Zsol)
         if (feh < -0.3) then
            critmass = pow_cr(feh,2d0)*0.3618377 + feh*1.47045658 + 5.69083898
            if (feh < -2.15) then
               critmass = pow_cr(-2.15d0,2d0)*0.3618377 -2.15*1.47045658 + 5.69083898
            end if
         else if ((feh >= -0.3) .and. (feh <= -0.22)) then
            critmass = feh*18.75 + 10.925
         else
            critmass = feh*1.09595794 + 7.0660861
         end if 
         if ((s% initial_mass > critmass) .and. (s% have_done_TP)) then
            if (s% Blocker_wind_eta < 1.0) then
               write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
               write(*,*) 'turning up Blocker'
               write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
            end if
            s% Blocker_wind_eta = 3.0
         end if

         if ((s% have_done_TP) .and. (s% varcontrol_target < new_varcontrol_target)) then !only print the first time
            s% varcontrol_target = new_varcontrol_target
            
!     CONVERGENCE TEST CHANGING C
     s% varcontrol_target = s% varcontrol_target * 1.0
            
            write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
            write(*,*) 'increasing varcontrol to ', s% varcontrol_target
            write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
         end if
      end if
      
!     treat postAGB: suppress late burning by turn off burning post-AGB and also save a model and photo
      envelope_mass_fraction = 1d0 - max(s% he_core_mass, s% c_core_mass, s% o_core_mass)/s% star_mass
      category_factors(:) = 1.0 !turn off burning except for H
      category_factors(3:) = 0.0
      if ((s% initial_mass < 10) .and. (envelope_mass_fraction < 0.1) .and. (s% center_h1 < 1d-4) .and. (s% center_he4 < 1d-4) &
      .and. (s% L_phot > 3.0) .and. (s% Teff > 7000.0)) then
		  if (burn_check == 0.0) then !only print the first time
			  write(*,*) '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
			  write(*,*) 'now at post AGB phase, turning off all burning except for H & saving a model + photo'
			  write(*,*) '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
			  
			  !save a model and photo
			  call star_write_model(id, s% job% save_model_filename, ierr)
			  photoname = 'photos/pAGB_photo'
			  call star_save_for_restart(id, photoname, ierr)
			  
			  !turn off burning
			  do r=1,g% num_reactions
				  burn_category = reaction_categories(g% reaction_id(r))
				  s% rate_factors(r) = category_factors(burn_category)
			  end do
			  burn_check = 1.0
		  end if		  
      end if
      
!     define STOPPING CRITERION: stopping criterion for C burning, massive stars.
      if ((s% center_h1 < 1d-4) .and. (s% center_he4 < 1d-4)) then
         if ((s% center_c12 < 1d-4) .and. (s% initial_mass >= 10.0)) then
            termination_code_str(t_xtra1) = 'central C12 mass fraction below 1e-4'
            s% termination_code = t_xtra1
            extras_check_model = terminate
         else if ((s% center_c12 < 1d-2) .and. (s% initial_mass < 10.0)) then
            termination_code_str(t_xtra2) = 'central C12 mass fraction below 1e-2'
            s% termination_code = t_xtra2
            extras_check_model = terminate
         end if
      end if
      
!     define STOPPING CRITERION: stopping criterion for TAMS, low mass stars.
      if ((s% center_h1 < 1d-4) .and. (s% initial_mass < 0.59)) then
         termination_code_str(t_xtra2) = 'central H1 mass fraction below 1e-4'
         s% termination_code = t_xtra2
         extras_check_model = terminate
      end if
      
!     check DIFFUSION: to determine whether or not diffusion should happen
!     no diffusion for fully convective, post-MS, and mega-old models 
	  s% diffusion_dt_limit = 3.15d7
      if(abs(s% mass_conv_core - s% star_mass) < 1d-2) then ! => fully convective
         s% diffusion_dt_limit = huge_dt_limit
      end if
      if (s% star_age > 5d10) then !50 Gyr is really old
         s% diffusion_dt_limit = huge_dt_limit
      end if
      min_center_h1_for_diff = 1d-10
      if (s% center_h1 < min_center_h1_for_diff) then
         s% diffusion_dt_limit = huge_dt_limit
      end if
      
	  end function extras_check_model
      
      
      integer function how_many_extra_history_columns(id, id_extra)
      integer, intent(in) :: id, id_extra
      integer :: ierr
      type (star_info), pointer :: s
      ierr = 0
      call star_ptr(id, s, ierr)
      if (ierr /= 0) return
      how_many_extra_history_columns = 0
      end function how_many_extra_history_columns
      
      
      subroutine data_for_extra_history_columns(id, id_extra, n, names, vals, ierr)
      integer, intent(in) :: id, id_extra, n
      character (len=maxlen_history_column_name) :: names(n)
      real(dp) :: vals(n)
      integer, intent(out) :: ierr
      type (star_info), pointer :: s
      ierr = 0
      call star_ptr(id, s, ierr)
      if (ierr /= 0) return
      end subroutine data_for_extra_history_columns
      
      
      integer function how_many_extra_profile_columns(id, id_extra)
      use star_def, only: star_info
      integer, intent(in) :: id, id_extra
      integer :: ierr
      type (star_info), pointer :: s
      ierr = 0
      call star_ptr(id, s, ierr)
      if (ierr /= 0) return
      how_many_extra_profile_columns = 0
      end function how_many_extra_profile_columns
      
      
      subroutine data_for_extra_profile_columns(id, id_extra, n, nz, names, vals, ierr)
      use star_def, only: star_info, maxlen_profile_column_name
      use const_def, only: dp
      integer, intent(in) :: id, id_extra, n, nz
      character (len=maxlen_profile_column_name) :: names(n)
      real(dp) :: vals(nz,n)
      integer, intent(out) :: ierr
      type (star_info), pointer :: s
      integer :: k
      ierr = 0
      call star_ptr(id, s, ierr)
      if (ierr /= 0) return
      end subroutine data_for_extra_profile_columns
      
      
!     returns either keep_going or terminate.
!     note: cannot request retry or backup; extras_check_model can do that.
      integer function extras_finish_step(id, id_extra)
      integer, intent(in) :: id, id_extra
      integer :: ierr
      type (star_info), pointer :: s
      ierr = 0
      call star_ptr(id, s, ierr)
      if (ierr /= 0) return
      extras_finish_step = keep_going
      call store_extra_info(s)
      
!     set BC: change to tables after running on simple photosphere
      if (s% model_number == 100) then
         write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
         write(*,*) 'switching from simple photosphere to ', s% job% extras_cpar(1)
         write(*,*) '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
         s% which_atm_option = s% job% extras_cpar(1)
      endif
      end function extras_finish_step
      
      subroutine Reimers_then_VW(id, Lsurf, Msurf, Rsurf, Tsurf, w, ierr)
      use star_def
	  use chem_def, only: ih1, ihe4
      integer, intent(in) :: id
      real(dp), intent(in) :: Lsurf, Msurf, Rsurf, Tsurf ! surface values (cgs)
!     NOTE: surface is outermost cell. not necessarily at photosphere.
!     NOTE: don't assume that vars are set at this point.
!     so if you want values other than those given as args,
!     you should use values from s% xh(:,:) and s% xa(:,:) only.
!     rather than things like s% Teff or s% lnT(:) which have not been set yet.
      real(dp), intent(out) :: w ! wind in units of Msun/year (value is >= 0)
      integer, intent(out) :: ierr
      real(dp) :: logP, P, reimers_w, pre_superwind_w, superwind_w, vexp, agb_w, center_h1, center_he4
	  integer :: h1, he4
	  type (star_info), pointer :: s
      ierr = 0
      call star_ptr(id, s, ierr)
      if (ierr /= 0) return
	  
!     first Reimers for the MS+RGB
      reimers_w = 4d-13*(Lsurf*Rsurf/Msurf)/(Lsun*Rsun/Msun)
      reimers_w = reimers_w * s% Reimers_wind_eta
      
!     Vassiliadis and Wood 1993	 
!     compute pulsation period assuming the fundamental mode
      logP = -2.07 + 1.94*log10_cr(Rsurf/Rsun)-0.9*log10_cr(Msurf/Msun) !in days
      P = pow_cr(10d0, logP)    !in days

!     for periods below ~500-800 days, exponentially increasing mdot
      if (Msurf/Msun < 2.5) then
         pre_superwind_w = pow_cr(10d0, -11.4+0.0123*P)
      else
         pre_superwind_w = pow_cr(10d0, -11.4+0.0125*(P - 100.0*(Msurf/Msun - 2.5)))
      end if
      
!     for periods above ~500-800 days, radiation pressure driven superwind
!     ensure that vexp is not a negative value
      vexp = min(15.0, max(3.0, -13.5+0.056*P))*1e5 !orig formula in km/s
      superwind_w = (Lsurf/(clight*vexp))*(secyer/Msun)
      
!     want the exponential increase in Mdot with P then ~const superwind
      agb_w = min(pre_superwind_w, superwind_w)
      
!     use Reimers for RGB then switch to VW during AGB
      h1 = s% net_iso(ih1)
      he4 = s% net_iso(ihe4)
      center_h1 = s% xa(h1,s% nz)
      center_he4 = s% xa(he4,s% nz)
      if (center_h1 < 0.01d0 .and. center_he4 < s% RGB_to_AGB_wind_switch) then
         w = agb_w
      else
         w = reimers_w
      end if
      end subroutine Reimers_then_VW
	  
	  subroutine Reimers_then_Blocker(id, Lsurf, Msurf, Rsurf, Tsurf, w, ierr)
      use star_def
      use chem_def, only: ih1, ihe4
      integer, intent(in) :: id
      real(dp), intent(in) :: Lsurf, Msurf, Rsurf, Tsurf ! surface values (cgs)
!     NOTE: surface is outermost cell. not necessarily at photosphere.
!     NOTE: don't assume that vars are set at this point.
!     so if you want values other than those given as args,
!     you should use values from s% xh(:,:) and s% xa(:,:) only.
!     rather than things like s% Teff or s% lnT(:) which have not been set yet.
      real(dp), intent(out) :: w ! wind in units of Msun/year (value is >= 0)
      integer, intent(out) :: ierr
      integer :: h1, he4
      real(dp) :: plain_reimers, reimers_w, blocker_w, center_h1, center_he4
	  type (star_info), pointer :: s
	  ierr = 0
      call star_ptr(id, s, ierr)
      if (ierr /= 0) return
	  
	  plain_reimers = 4d-13*(Lsurf*Rsurf/Msurf)/(Lsun*Rsun/Msun)
	  
	  reimers_w = plain_reimers * s% Reimers_wind_eta
	  blocker_w = plain_reimers * s% Blocker_wind_eta * &
               4.83d-9 * pow_cr(Msurf/Msun,-2.1d0) * pow_cr(Lsurf/Lsun,2.7d0)

          h1 = s% net_iso(ih1)
          he4 = s% net_iso(ihe4)
          center_h1 = s% xa(h1,s% nz)
          center_he4 = s% xa(he4,s% nz)

          !prevent the low mass RGBs from using Blocker
          if (center_h1 < 0.01d0 .and. center_he4 > 0.1d0) then
             w = reimers_w
          else 
             w = max(reimers_w, blocker_w)
          end if
	  
	  end subroutine Reimers_then_Blocker
      
      subroutine extras_after_evolve(id, id_extra, ierr)
      integer, intent(in) :: id, id_extra
      integer, intent(out) :: ierr
      type (star_info), pointer :: s
      ierr = 0
      call star_ptr(id, s, ierr)
      if (ierr /= 0) return
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
!     call move_int or move_flg    
      num_ints = i
      
      i = 0
!     call move_dbl       
      
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
