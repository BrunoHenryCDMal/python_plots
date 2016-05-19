''' 
stellar_mass_vs_halo_mass
stellar_mass_function
stellar_mass_vs_halo_mass
redfraction_color_cut
metals_vs_stellarmass
BHBM
SFRF
gas_fraction
HI_MF
sfr_vs_stellar_mass
ur_vs_r
UVJ_colour
morphology_vs_stellarmass
sizes_vs_stellarmass
    
bluck_red_fractions
sat_fraction
BHmass_in_radio

misc_plots()
test_resolution_rings


simple_tree_map
full_tree_map
'''

import numpy as np
import pandas as pd
#import seaborn as sns
#sns.set_style('darkgrid')

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from astropy.table import Table
from astropy.io import fits
from importlib import reload
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LogNorm
import sys
from scipy.ndimage import zoom
import os.path

import procedures
reload (procedures)
from procedures import *
import plots_input
reload (plots_input)
from plots_input import *


def stellar_mass_vs_halo_mass(G_MR, ThisRedshiftList, pdf):

    ylim=[2.0,12.5]
    xlim=[2.5, 15.]
  
    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                         'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})    
    fig = plt.figure(figsize=(10,10))
    subplot=plt.subplot()
    subplot.set_ylim(ylim), subplot.set_xlim(xlim) 

    ylab='$\mathrm{log_{10}}(M_*[h^{-2}M_{\odot}])$'       
    xlab='$\mathrm{log_{10}}(M_{200c}[h^{-2}M_{\odot}])$'
    subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)
                  
    for ii in range (0,len(ThisRedshiftList)):
  
        #MODEL
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)
        
        G0_MR=G_MR[sel] 
        G0_MR=np.random.choice(G0_MR, size=10000.)
        G0_MR=G0_MR[G0_MR['StellarMass']>0.]
        StellarMass=stellar_mass_with_err(G0_MR, Hubble_h, ThisRedshiftList[ii])          
        HaloMass=np.log10(G0_MR['Mvir']*1.e10*Hubble_h) 
        sel=G0_MR['Type']==2
        subplot.scatter(HaloMass[sel],StellarMass[sel],s=5, color='red')        
        sel=G0_MR['Type']==1
        subplot.scatter(HaloMass[sel],StellarMass[sel],s=5, color='green')
        sel=G0_MR['Type']==0
        subplot.scatter(HaloMass[sel],StellarMass[sel],s=5, color='blue')
        
    #endfor
    
    plt.tight_layout()
    plt.savefig('./fig/plots_smhm.pdf')
    pdf.savefig()
    plt.close()
    

def stellar_mass_function(G_MR, Volume_MR, G_MRII, Volume_MRII, ThisRedshiftList, pdf):
           
    xlim=[7.0,12.5]
    ylim=[-6.5, 0.5]
    bin=0.25


    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                         'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})

    fig = plt.figure(figsize=(8,7))
    grid = gridspec.GridSpec(2, 2)
    grid.update(wspace=0.0, hspace=0.0)

    for ii in range(0,len(ThisRedshiftList)):
        
        char_redshift="%0.2f" % ThisRedshiftList[ii]
        
        subplot=plt.subplot(grid[ii])

        subplot.set_ylim(ylim), subplot.set_xlim(xlim)
        if ii==2 or ii == 3: 
            xlab='$\mathrm{log_{10}}(M_*[h^{-2}M_{\odot}])$'
        else:
            xlab=''
        if ii==0 or ii == 2:
            ylab='$\mathrm{log_{10}}(\phi [h^3 \mathrm{Mpc^{-3}} \mathrm{log_{10}}(M^{-1})])$'
        else:
            ylab=''      
        subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)
                
    
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(1))    
        subplot.xaxis.set_minor_locator(MultipleLocator(0.25))      
        subplot.yaxis.set_minor_locator(MultipleLocator(0.25))
    
        if ii==1 or ii == 3:
            plt.tick_params(axis='y', which='both', left='on', labelleft='off')
           
    
        #OBSERVATIONS             
        file = MCMCdir + '/ObsConstraints/StellarMassFunction_z'+char_redshift+'.txt'        
        f = open(file, 'r')     
        line = int(f.readline())     
        obs = Table.read(file, format='ascii', data_start=1, data_end=line+1)
        
        obs_xbin=obs['col1']+(obs['col2']-obs['col1'])/2.
        asy_yerror = [np.log10(obs['col3']/(obs['col3']-obs['col4'])), 
                      np.log10((obs['col3']+obs['col4'])/obs['col3'])]
        subplot.errorbar(obs_xbin, np.log10(obs['col3']),yerr=asy_yerror,
                 fmt='o', markersize=5, ecolor='blue', color='blue')
        #sub = plt.subplot(111)
    
        #PREVIOUS MODELS
        RedshiftList_OldModels=[0.1,1.0,2.0,3.0]
        if do_previous_model1==1:           
            char_old_redshift="%0.2f" % RedshiftList_OldModels[ii]
            file = file_previous_model1+'_smf_z'+char_old_redshift+'.txt' 
            model = Table.read(file, format='ascii')
            subplot.plot(model['col1'],model['col2'],color='red',linestyle=linestyle_previous_model1, linewidth=2)
      
        if do_previous_model2==1:           
            file = file_previous_model2+'_smf_z'+char_redshift+'.txt' 
            model = Table.read(file, format='ascii')
            subplot.plot(model['col1'],model['col2'],color='red',linestyle=linestyle_previous_model2, linewidth=2)
      
    
        #MODEL
        #MR
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)
        
        G0_MR=G_MR[sel]   
        G0_MR=G0_MR[G0_MR['StellarMass']>0.]
        StellarMass=stellar_mass_with_err(G0_MR, Hubble_h, ThisRedshiftList[ii])
        
        bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
        hist_MR=np.histogram(StellarMass, bins=bin_arr, range=(xlim[0],xlim[1]))   
        
        #MRII
        if(MRII==1):
            (sel)=select_current_redshift(G_MRII, ThisRedshiftList, ii, FullSnapshotList_MRII)
        
            G0_MRII=G_MRII[sel]   
            G0_MRII=G0_MRII[G0_MRII['StellarMass']>0.]
            StellarMass=stellar_mass_with_err(G0_MRII, Hubble_h, ThisRedshiftList[ii])
        
            bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
            hist_MRII=np.histogram(StellarMass, bins=bin_arr, range=(xlim[0],xlim[1]))   
           
        
        #join MR+MRII & plot     
        if(MRII==1):
            cut_MR_MRII=9.0
            plot_joint_MR_MRII(hist_MR, hist_MRII, cut_MR_MRII, Volume_MR, Volume_MRII, 
                               bin, subplot, color='red',linewidth=2, linestyle='-')
        else:
            x_axis=hist_MR[1][0:len(hist_MR[1][:])-1]+bin/2.           
            hist_MR=hist_MR[0]       
            y_axis=np.log10(hist_MR/(Volume_MR*bin))
            subplot.plot(x_axis,y_axis, color='red', linewidth=2, linestyle='-') 
    
        
        #MCMC sample
        if opt_plot_MCMC_sample==1:
            file = MCMCSampledir + 'mcmc_plus_obs_StellarMassFunction_z'+char_redshift+'.txt' 
            if os.path.isfile(file):
                obs = Table.read(file, format='ascii')      
                subplot.plot(obs['col1'],np.log10(obs['col4']), color='black', linewidth=2)
            
                if ii==len(ThisRedshiftList)-1:
                    plot_label (subplot, 'label', xlim, ylim, 
                        x_percentage=0.55, y_percentage=0.85, color='black', xlog=0, ylog=0, 
                        label='MCMC sample', fontsize=13, fontweight='normal') 
                    plot_label (subplot, 'line', xlim, ylim,
                        x_percentage=0.44, y_percentage=0.87, color='black', x2_percentage=0.53, 
                        xlog=0, ylog=0, linestyle='-', linewidth=2)
                
                
        #LABELS
        if ii==0:
            plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.91, 
                        color='black', xlog=0, ylog=0, label='Observations used in MCMC', 
                        fontsize=13, fontweight='normal') 
            plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.935, 
                        color='blue', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.15) 
            
        if ii==len(ThisRedshiftList)-1:
            plot_label_three_models (subplot, xlim, ylim, position='bottom_left')
                                  
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.05, y_percentage=0.35, 
                    color='black', xlog=0, ylog=0, label='z='+char_redshift[:-1], 
                    fontsize=14, fontweight='normal')      
        if ii==2:
             plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.075, 
                         color='black', xlog=0, ylog=0, label='SMF evo', 
                         fontsize=16, fontweight='normal') 
           
    #endfor


    plt.tight_layout()
    plt.savefig('./fig/plots_smf_evo.pdf')
    pdf.savefig()
    plt.close()
#endif stellar_mass_function==1:



def redfraction_color_cut(G_MR, ThisRedshiftList, pdf):
           
    xlim=[8.5,11.5]
    ylim=[0., 1.2]   
    bin=[0.1,0.05]
    Nbins=[int((xlim[1]-xlim[0])/bin[0]),int((ylim[1]-ylim[0])/bin[1])]

    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                         'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})

    fig = plt.figure(figsize=(15,4))
    grid = gridspec.GridSpec(1, 5)
    grid.update(wspace=0.0, hspace=0.0)

    for ii in range(0,len(ThisRedshiftList)):
        
        char_redshift="%0.2f" % ThisRedshiftList[ii]
        
        subplot=plt.subplot(grid[ii])
        subplot.set_ylim(ylim), subplot.set_xlim(xlim)
        
        xlab='$\mathrm{log_{10}}(M_*[h^{-2}M_{\odot}])$'      
        if ii==0:
            ylab='Red Fraction'
        else:
            ylab=''      
        subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)
        
        #subplot.text(xlim[0]+0.1,ylim[0]+.875,'z='+char_redshift, fontsize=16, fontweight='normal')
                        
    
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(1))    
        subplot.xaxis.set_minor_locator(MultipleLocator(0.25))      
        subplot.yaxis.set_minor_locator(MultipleLocator(0.1))
    
        if ii>0:
            plt.tick_params(axis='y', which='both', left='on', labelleft='off')
                   
        #OBSERVATIONS             
        file = MCMCdir + '/ObsConstraints/RedFraction_z'+char_redshift+'.txt'        
        f = open(file, 'r')     
        line = int(f.readline())     
        obs = Table.read(file, format='ascii', data_start=1, data_end=line+1)
        
        obs_xbin=obs['col1']+(obs['col2']-obs['col1'])/2.       
        subplot.errorbar(obs_xbin, obs['col3'],obs['col4'],
                 fmt='o', markersize=5, ecolor='blue', color='blue')
        #sub = plt.subplot(111)
        
        #PREVIOUS MODELS 
        RedshiftList_OldModels=[0.1,0.4,1.,2.,3.0]
        old_char_redshift="%0.2f" % RedshiftList_OldModels[ii]
        if do_previous_model1==1: 
            file = file_previous_model1+'_redfrac_colorcut_z'+old_char_redshift+'.txt' 
            model = Table.read(file, format='ascii')
            subplot.plot(model['col1'],model['col2'],color='red',linestyle=linestyle_previous_model1, linewidth=2)           
        if do_previous_model2==1: 
            file = file_previous_model2+'_redfrac_colorcut_z'+char_redshift+'.txt'  
            model = Table.read(file, format='ascii')
            subplot.plot(model['col1'],model['col2'],color='red',linestyle=linestyle_previous_model2, linewidth=2)
        
        #MODEL
        bin=0.25        
        Mass_arr=np.arange(xlim[0],xlim[1],bin)
        RedFraction=np.zeros(len(Mass_arr),dtype=np.float32)
        
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)        
        G0_MR=G_MR[sel]   
        StellarMass=stellar_mass_with_err(G0_MR, Hubble_h, ThisRedshiftList[ii])
        
        #z=0.
        if ThisRedshiftList[ii]==0:
            color_ur=G0_MR['MagDust'][:,15]-G0_MR['MagDust'][:,17]  
            Magr=G0_MR['MagDust'][:,17]
            
            for ll in range(0,len(Mass_arr)):
                sel_red=G0_MR[(color_ur>(offset_red_fraction[ii]-slope_red_fraction[ii]*np.tanh((Magr+18.07)/1.09))) &
                    (StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
                sel_all=G0_MR[(StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
                
                RedFraction[ll]=float(len(sel_red))/float(len(sel_all))
                
        #z>0.
        else:
            color_UV=G0_MR['MagDust'][:,0]-G0_MR['MagDust'][:,2]  
            color_VJ=G0_MR['MagDust'][:,2]-G0_MR['MagDust'][:,7]       
                  
            for ll in range(0,len(Mass_arr)):
                sel_red=G0_MR[(((color_VJ < (minimum_y_red_fraction[ii]-offset_red_fraction[ii])/slope_red_fraction[ii]) &
                               (color_UV > minimum_y_red_fraction[ii])) |                      
                              ((color_VJ > (minimum_y_red_fraction[ii]-offset_red_fraction[ii])/slope_red_fraction[ii]) &
                               (color_UV > (color_VJ*slope_red_fraction[ii] + offset_red_fraction[ii])))) &
                              (StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
                
                sel_all=G0_MR[(StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
                if len(sel_all)>0.:
                    RedFraction[ll]=float(len(sel_red))/float(len(sel_all))
                else:
                    RedFraction[ll]=0.
                    
        subplot.plot(Mass_arr, RedFraction, color='red', linestyle='-', linewidth=2) 
      
    
        #MCMC sample
        if opt_plot_MCMC_sample==1:
            file = MCMCSampledir + 'mcmc_plus_obs_RedFraction_z'+char_redshift+'.txt' 
            if os.path.isfile(file):
                obs = Table.read(file, format='ascii')      
                subplot.plot(obs['col1'],obs['col4'], color='black', linewidth=2)
            
                if ii==len(ThisRedshiftList)-1:
                    plot_label (subplot, 'label', xlim, ylim, 
                        x_percentage=0.55, y_percentage=0.85, color='black', xlog=0, ylog=0, 
                        label='MCMC sample', fontsize=13, fontweight='normal') 
                    plot_label (subplot, 'line', xlim, ylim,
                        x_percentage=0.44, y_percentage=0.87, color='black', x2_percentage=0.53, 
                        xlog=0, ylog=0, linestyle='-', linewidth=2)
    
    
        #LABELS    
        if ii==0:
            plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.91, 
                        color='black', xlog=0, ylog=0, label='Observations used in MCMC', 
                        fontsize=12, fontweight='normal') 
            plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.935, 
                        color='blue', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.03) 
        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.05, y_percentage=0.65, 
                    color='black', xlog=0, ylog=0, label='z='+char_redshift[:-1], 
                    fontsize=14, fontweight='normal') 
            
        if ii==len(ThisRedshiftList)-1:
            plot_label_three_models (subplot, xlim, ylim, position='top_left')
                        
    #endfor
        
    plt.tight_layout()
    plt.savefig('./fig/plots_redfraction_color_cut.pdf')
    pdf.savefig()
    plt.close()
#endif redfraction_color_cut

  
def metals_vs_stellarmass(G_MR, ThisRedshiftList, pdf):
           
    xlim=[9.0,12.0]
    ylim=[-1.5, 0.5]   
    bin=0.2
        
    plot_color=['red','purple']        
    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
    fig = plt.figure(figsize=(5,4))
    subplot=plt.subplot()
    subplot.set_ylim(ylim), subplot.set_xlim(xlim)
    
    #format axis
    majorFormatter = FormatStrFormatter('%d')
    subplot.xaxis.set_major_locator(MultipleLocator(1))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25)) 
    
    xlab='$\mathrm{log_{10}}(M_*[h^{-2}M_{\odot}])$'       
    ylab='$\mathrm{log_{10}}(Z/Z_{\odot})$'         
    subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)    
        
    for ii in range (0,len(ThisRedshiftList)):
        
        char_redshift="%0.2f" % ThisRedshiftList[ii]
        
        #PREVIOUS MODELS    
        if ThisRedshiftList[ii]==0.1:
            char_redshift="%0.2f" % ThisRedshiftList[ii]
            if do_previous_model1==1: 
                file = file_previous_model1+'_metals_median_z'+char_redshift+'.txt' 
                model = Table.read(file, format='ascii')
                subplot.plot(model['col1'],model['col2'],color='red',linestyle=linestyle_previous_model1, linewidth=2)

            if do_previous_model2==1: 
                file = file_previous_model2+'_metals_z'+char_redshift+'.txt' 
                model = Table.read(file, format='ascii')
                subplot.plot(model['col1'],model['col2'],color='red',linestyle=linestyle_previous_model2, linewidth=2)

        if ii==0:        
            #observations from GALLAZI   
            Nbins=16
            obs_bin=0.2
            xmass=np.arange(Nbins)*obs_bin+8.8
            obsp50=[-0.60,-0.61,-0.65,-0.61,-0.52,-0.41,-0.23,-0.11,-0.01,0.04,0.07,0.10,0.12,0.13,0.14,0.15]
            obsp16=[-1.11,-1.07,-1.10,-1.03,-0.97,-0.90,-0.80,-0.65,-0.41,-0.24,-0.14,-0.09,-0.06,-0.04,-0.03,-0.03]
            obsp84=[-0.00,-0.00,-0.05,-0.01,0.05,0.09,0.14,0.17,0.20,0.22,0.24,0.25,0.26,0.28,0.29,0.30]  
            subplot.errorbar(xmass, obsp50, color='blue', fmt='o')       
            subplot.plot(xmass, obsp16,color='blue', linestyle='--')
            subplot.plot(xmass, obsp84,color='blue', linestyle='--')   
            
            #create OBSconstraint file for MCMC           
            '''obs_y=np.zeros(Nbins,dtype=np.float64)
            obs_y_err=np.zeros(Nbins,dtype=np.float64)
            for kk in range (0,len(xmass)):
                print('%0.2f %0.2f %0.2f %0.2f' % ((xmass[kk]-obs_bin/2.),(xmass[kk]+obs_bin/2),
                      (10.**obsp84[kk]+10.**obsp16[kk])/2.,(10.**obsp84[kk]-10.**obsp16[kk])/2.))                           
                obs_y[kk]=(10.**obsp84[kk]+10.**obsp16[kk])/2.
                obs_y_err[kk]=(10.**obsp84[kk]-10.**obsp16[kk])/2.              
            obs_y_err = [np.log10(obs_y/(obs_y-obs_y_err)),np.log10((obs_y+obs_y_err)/obs_y)]
            subplot.errorbar(xmass, np.log10(obs_y), yerr=obs_y_err, color='black', fmt='o')'''  
            
            #LABELS        
            plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.91, 
                        color='black', xlog=0, ylog=0, label='Gallazzi 2005', 
                        fontsize=13, fontweight='normal') 
            plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.935, 
                        color='blue', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.05) 
                               
            plot_label_three_models (subplot, xlim, ylim, position='bottom_left')
            #z=3
            plot_label (subplot, 'label', xlim, ylim, 
                        x_percentage=0.36, y_percentage=0.06, color='black', xlog=0, ylog=0, 
                        label=', z=0            This Work, z=3', fontsize=10, fontweight='normal')             
            plot_label (subplot, 'line', xlim, ylim,
                    x_percentage=0.52, y_percentage=0.08, color=plot_color[1], x2_percentage=0.61, 
                    xlog=0, ylog=0, linestyle='-', linewidth=2)
    
        #Model
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)        
        G0_MR=G_MR[sel]         
        StellarMass=stellar_mass_with_err(G0_MR, Hubble_h, ThisRedshiftList[ii])    
        if(opt_detailed_enrichment==0):                                 
            Metallicity=(G0_MR['MetalsStellarMass'])/((G0_MR['StellarMass'])*0.02)    
        else:
            MassInMetals=G0_MR['MetalsDiskMass'][:,0]+G0_MR['MetalsDiskMass'][:,1]+G0_MR['MetalsDiskMass'][:,2]+\
                         G0_MR['MetalsBulgeMass'][:,0]+G0_MR['MetalsBulgeMass'][:,1]+G0_MR['MetalsBulgeMass'][:,2]            
            Metallicity=MassInMetals/(G0_MR['StellarMass']*0.02) 
            
        StellarMass=StellarMass[Metallicity>0.]    
        Metallicity=np.log10(Metallicity[Metallicity>0.])        
                
        (x_binned, median, mean, pc16, pc84)=median_and_percentiles (bin, xlim[0], xlim[1], StellarMass, Metallicity)    
        subplot.plot(x_binned, median,color=plot_color[ii], linewidth=2)
        if (ii==0):
            subplot.plot(x_binned, pc16,color=plot_color[ii], linewidth=2, linestyle='-')
            subplot.plot(x_binned, pc84,color=plot_color[ii], linewidth=2, linestyle='-')
                   
       
        #MCMC sample
        if opt_plot_MCMC_sample==1:
            file = MCMCSampledir + 'mcmc_plus_obs_StellarMetallicityvsStellarMass_z'+char_redshift+'.txt' 
            if os.path.isfile(file):
                obs = Table.read(file, format='ascii')      
                subplot.plot(obs['col1'],np.log10(obs['col4']), color='black', linewidth=2)
            
                if ii==len(ThisRedshiftList)-1:
                    plot_label (subplot, 'label', xlim, ylim, 
                        x_percentage=0.55, y_percentage=0.85, color='black', xlog=0, ylog=0, 
                        label='MCMC sample', fontsize=13, fontweight='normal') 
                    plot_label (subplot, 'line', xlim, ylim,
                        x_percentage=0.44, y_percentage=0.87, color='black', x2_percentage=0.53, 
                        xlog=0, ylog=0, linestyle='-', linewidth=2)    
    #endfor
        
    plt.tight_layout()
    plt.savefig('./fig/plots_metals_vs_stellarmass.pdf')
    pdf.savefig()
    plt.close()

#end metals_vs_stellarmass


def gasmetals_vs_stellarmass(G_MR, ThisRedshiftList, pdf):
           
    xlim=[9.0,12.0]
    ylim=[8., 9.5]   
    bin=0.2
        
    plot_color=['red','purple']        
    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
    fig = plt.figure(figsize=(5,4))
    subplot=plt.subplot()
    subplot.set_ylim(ylim), subplot.set_xlim(xlim)
    
    #format axis
    majorFormatter = FormatStrFormatter('%d')
    subplot.xaxis.set_major_locator(MultipleLocator(1))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25)) 
    
    xlab='$\mathrm{log_{10}}(M_*[h^{-2}M_{\odot}])$'       
    ylab='$12 + log_{10}$(O/H)$_{gas}$'         
    subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)    
        
    for ii in range (0,len(ThisRedshiftList)):
           
        #Model
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)        
        G0_MR=G_MR[sel]         
        StellarMass=stellar_mass_with_err(G0_MR, Hubble_h, ThisRedshiftList[ii])    
        if(opt_detailed_enrichment==0):                                 
            Metallicity=G0_MR['MetalsColdGas']/G0_MR['ColdGas']/0.02 
        else:
            MassInGasMetals=G0_MR['MetalsColdGas'][:,0]+G0_MR['MetalsColdGas'][:,1]+G0_MR['MetalsColdGas'][:,2]+\
                         G0_MR['MetalsColdGas'][:,0]+G0_MR['MetalsColdGas'][:,1]+G0_MR['MetalsColdGas'][:,2]           
            Metallicity=MassInGasMetals/G0_MR['ColdGas']/0.02
               
        StellarMass=StellarMass[Metallicity>0.]    
        Metallicity=np.log10(Metallicity[Metallicity>0.])+8.69         
                
        (x_binned, median, mean, pc16, pc84)=median_and_percentiles (bin, xlim[0], xlim[1], StellarMass, Metallicity)    
        subplot.plot(x_binned, median,color=plot_color[ii], linewidth=2)
        if (ii==0):
            subplot.plot(x_binned, pc16,color=plot_color[ii], linewidth=2, linestyle='-')
            subplot.plot(x_binned, pc84,color=plot_color[ii], linewidth=2, linestyle='-')
            
            
        #LABELS        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.91, 
                    color='black', xlog=0, ylog=0, label='Gallazzi 2005', 
                    fontsize=13, fontweight='normal') 
        plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.935, 
                    color='blue', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.05) 
                               
        plot_label_three_models (subplot, xlim, ylim, position='bottom_left')
        #z=3
        plot_label (subplot, 'label', xlim, ylim, 
                    x_percentage=0.36, y_percentage=0.06, color='black', xlog=0, ylog=0, 
                    label=', z=0            This Work, z=3', fontsize=10, fontweight='normal')             
        plot_label (subplot, 'line', xlim, ylim,
                    x_percentage=0.52, y_percentage=0.08, color=plot_color[1], x2_percentage=0.61, 
                    xlog=0, ylog=0, linestyle='-', linewidth=2)
       
    #endfor
        
    plt.tight_layout()
    plt.savefig('./fig/plots_metals_vs_stellarmass.pdf')
    pdf.savefig()
    plt.close()

#end gasmetals_vs_stellarmass 

def BHBM(G_MR, ThisRedshiftList, pdf):
   
    for ii in range(0,len(ThisRedshiftList)):        
        
        xlim=[8.5,12.5]
        ylim=[5.0, 10.5]
        bin=[0.1,0.05]
        Nbins=[int((xlim[1]-xlim[0])/bin[0]),int((ylim[1]-ylim[0])/bin[1])]
    
        plot_color=['red','purple']        
        plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
        fig = plt.figure(figsize=(5,4))
        subplot=plt.subplot()
        subplot.set_ylim(ylim), subplot.set_xlim(xlim)    
            
        #format axis
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(1))    
        subplot.xaxis.set_minor_locator(MultipleLocator(0.25)) 
            
        xlab='$\mathrm{log_{10}}(M_{\mathrm{Bulge}}[h^{-2}M_{\odot}])$'       
        ylab='$\mathrm{log_{10}}(M_{\mathrm{BH}}[h^{-1}M_{\odot}])$' 
        subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)   
            
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)        
        G0_MR_unsel=G_MR[sel]   
        G0_MR=G0_MR_unsel[(G0_MR_unsel['BulgeMass'] > 0.) & (G0_MR_unsel['BlackHoleMass'] > 0.)]
        Ngals=len(G0_MR) 
       
        BulgeMass=(np.log10(G0_MR['BulgeMass']*1.e10*Hubble_h)) 
        BHMass=(np.log10(G0_MR['BlackHoleMass']*1.e10)) 
         
        #plt.scatter(BulgeMass, BHMass, s=5, color='black')          
        H, xedges, yedges = np.histogram2d(BulgeMass, BHMass, bins=Nbins)            
        extent = [xedges[0], xedges[-1],yedges[0], yedges[-1]]       
        plt.subplots_adjust(bottom=0.15, left=0.15)        
        mylevels = np.linspace(1., Nbins[0], Nbins[0])*Ngals/(Nbins[0]**2/0.7)        
        H = zoom(H, 20)        
        cont=plt.contourf(H.transpose()[::], origin='lower', cmap='Greys_r', levels=mylevels, extent=extent)        
        plt.colorbar(format='%d') 
        #(ax, cmap=None, norm=None, alpha=None, values=None, boundaries=None, orientation='vertical', 
        #ticklocation='auto', extend='neither', spacing='uniform', ticks=None, format=None, 
        #drawedges=False, filled=True, extendfrac=None, extendrect=False, label='')
       
        file = Datadir + 'mcconnel2012.dat'
        obs = Table.read(file, format='ascii', data_start=20)     
        obs_x = np.log10(obs['col14']*Hubble_h_WMAP7**2)
        obs_y = np.log10(obs['col3']*Hubble_h_WMAP7**2)        
        obs_x_err=np.zeros(len(obs_x),dtype=np.float64)+0.24 
        obs_y_err = [np.log10(obs['col3']/obs['col4']),np.log10(obs['col5']/obs['col3'])]
       
        subplot.errorbar(obs_x, obs_y,xerr= obs_x_err, yerr=obs_y_err,
                 fmt='o', markersize=5, ecolor='blue', color='blue')
        
        #LABELS        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.9, 
                    color='black', xlog=0, ylog=0, label='McConnel 2012', 
                    fontsize=13, fontweight='normal') 
        plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.925, 
                    color='blue', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.15) 
        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.7, y_percentage=0.1, 
                    color='black', xlog=0, ylog=0, label='BHBM', 
                    fontsize=13, fontweight='normal') 
        
    plt.tight_layout()
    plt.savefig('./fig/plots_bhbm.pdf')
    pdf.savefig()
    plt.close()

#end BHBM




def SFRF(G_MR, Volume_MR, G_MRII, Volume_MRII, ThisRedshiftList, pdf):
   
    for ii in range(0,len(ThisRedshiftList)):        
        
        char_redshift="%0.2f" % ThisRedshiftList[ii]
        
        xlim=[-2.0,3.0]
        ylim=[-6.0,0.0]
        bin=0.2
    
        plot_color=['red','purple']        
        plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
        fig = plt.figure(figsize=(5,4))
        subplot=plt.subplot()
        subplot.set_ylim(ylim), subplot.set_xlim(xlim)    
            
        #format axis
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(1))    
        subplot.xaxis.set_minor_locator(MultipleLocator(0.25)) 
            
        xlab='$\mathrm{log_{10}}(\mathrm{SFR}[h^{-2}M_{\odot}yr^{-1}])$'   
        ylab='$\mathrm{log_{10}}(\phi [h^3 \mathrm{Mpc^{-3}} \mathrm{log_{10}}(SFR^{-1})])$'     
        subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)   
            
        #MR
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)         
        G0_MR=G_MR[sel]   
        G0_MR=G0_MR[G0_MR['Sfr']>0.]
        SFR=(np.log10(G0_MR['Sfr']*Hubble_h**2))
                
        bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
        hist_MR=np.histogram(SFR, bins=bin_arr, range=(xlim[0],xlim[1]))   
            
        #MRII    
        if(MRII==1):
            (sel)=select_current_redshift(G_MRII, ThisRedshiftList, ii, FullSnapshotList_MRII)         
            G0_MRII=G_MRII[sel]   
            G0_MRII=G0_MRII[G0_MRII['Sfr']>0.]
            SFR=(np.log10(G0_MRII['Sfr']*Hubble_h**2))
                
            bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
            hist_MRII=np.histogram(SFR, bins=bin_arr, range=(xlim[0],xlim[1]))   
               
     
        #join MR+MRII & plot     
        if(MRII==1):
            cut_MR_MRII=9.0
            plot_joint_MR_MRII(hist_MR, hist_MRII, cut_MR_MRII, Volume_MR, Volume_MRII, 
                               bin, subplot, color='red',linewidth=2, linestyle='-')
        else:
            x_axis=hist_MR[1][0:len(hist_MR[1][:])-1]+bin/2.           
            hist_MR=hist_MR[0]       
            y_axis=np.log10(hist_MR/(Volume_MR*bin))
            subplot.plot(x_axis,y_axis, color='red', linewidth=2, linestyle='-') 
            
    
        file = Datadir + 'gruppioni2015.txt'
        obs = Table.read(file, format='ascii', data_start=0, data_end=7)       
        obs_x = (obs['col1']+obs['col2'])/2.
        obs_y = np.log10(obs['col3'])       
        obs_y_err = np.log10((obs['col3']+obs['col4']))-np.log10((obs['col3']-obs['col4']))
       
        subplot.errorbar(obs_x, obs_y, yerr=obs_y_err,
                 fmt='o', markersize=5, ecolor='blue', color='blue')
                
        #MCMC sample
        if opt_plot_MCMC_sample==1:
            file = MCMCSampledir + 'mcmc_plus_obs_SFRF_z'+char_redshift+'.txt' 
            if os.path.isfile(file):
                obs = Table.read(file, format='ascii')      
                subplot.plot(obs['col1'],np.log10(obs['col4']), color='black', linewidth=2)
            
                if ii==len(ThisRedshiftList)-1:
                    plot_label (subplot, 'label', xlim, ylim, 
                        x_percentage=0.55, y_percentage=0.85, color='black', xlog=0, ylog=0, 
                        label='MCMC sample', fontsize=13, fontweight='normal') 
                    plot_label (subplot, 'line', xlim, ylim,
                        x_percentage=0.44, y_percentage=0.87, color='black', x2_percentage=0.53, 
                        xlog=0, ylog=0, linestyle='-', linewidth=2)    
            
        #LABELS   
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.2, 
                    color='black', xlog=0, ylog=0, label='Gruppioni 2015', 
                    fontsize=13, fontweight='normal') 
        plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.225, 
                    color='blue', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.15) 
           
        plot_label (subplot, 'label', xlim, ylim, 
                x_percentage=0.15, y_percentage=0.1, color='black', xlog=0, ylog=0, 
                label=prefix_this_model, fontsize=13, fontweight='normal') 
        plot_label (subplot, 'line', xlim, ylim,
                x_percentage=0.04, y_percentage=0.12, color='red', x2_percentage=0.13, 
                xlog=0, ylog=0, linestyle='-', linewidth=2)
        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.775, y_percentage=0.85, 
                    color='black', xlog=0, ylog=0, label='SFRF', 
                    fontsize=13, fontweight='normal') 
            
    plt.tight_layout()
    plt.savefig('./fig/plots_sfrf.pdf')
    pdf.savefig()
    plt.close()

#end SFRF


 

def gas_fraction(G_MR, ThisRedshiftList, pdf):
   
    for ii in range(0,len(ThisRedshiftList)):        
        
        char_redshift="%0.2f" % ThisRedshiftList[ii]
        
        xlim=[8.5,12.0]
        ylim=[-2.,1.0]
       
        bin=0.1
        plot_color=['red','purple']        
        plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
        fig = plt.figure(figsize=(5,4))
        subplot=plt.subplot()
        subplot.set_ylim(ylim), subplot.set_xlim(xlim)    
            
        #format axis
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(1))    
        subplot.xaxis.set_minor_locator(MultipleLocator(0.25))
            
        xlab='$log_{10}(M_*[h^{-2}M_{\odot}])$'
        ylab='$M_{\mathrm{Cold}}/M_*$'     
        subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)   
            
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)        
        G0_MR=G_MR[sel]          
        G0_MR=G0_MR[(G0_MR['StellarMass']>0.) & (G0_MR['ColdGas']>0.)]
        StellarMass=stellar_mass_with_err(G0_MR, Hubble_h, ThisRedshiftList[ii])
        Fraction=np.log10(G0_MR['ColdGas']*1.e10*Hubble_h)-StellarMass 
   
        (x_binned, median, mean, pc16, pc84)=median_and_percentiles (bin, xlim[0], xlim[1], StellarMass, Fraction)          
        sel=(median!=0)        
        subplot.plot(x_binned[sel], median[sel],color=plot_color[ii], linewidth=2)     
        subplot.plot(x_binned[sel], pc16[sel],color=plot_color[ii], linewidth=2, linestyle='--')
        subplot.plot(x_binned[sel], pc84[sel],color=plot_color[ii], linewidth=2, linestyle='--')
    
    
        file = Datadir + 'peeples_2015.txt'
        obs = Table.read(file, format='ascii', data_start=0)       
        obs_x = (obs['col1']+obs['col2'])/2.
        obs_y = np.log10(obs['col3'])       
        obs_y_err = [np.log10(obs['col3']/(obs['col3']-obs['col4'])),np.log10((obs['col3']+obs['col4'])/obs['col3'])]
               
        subplot.errorbar(obs_x, obs_y, yerr=obs_y_err,
                 fmt='o', markersize=5, ecolor='blue', color='blue')
              
        #MCMC sample
        if opt_plot_MCMC_sample==1:
            file = MCMCSampledir + 'mcmc_plus_obs_ColdGasFractionvsStellarMass_z'+char_redshift+'.txt' 
            if os.path.isfile(file):
                obs = Table.read(file, format='ascii')      
                subplot.plot(obs['col1'],np.log10(obs['col4']), color='black', linewidth=2)
                #subplot.errorbar(obs['col1'],obs['col2'], yerr=obs['col3'], 
                #                 fmt='o', markersize=5, ecolor='black', color='black')
            
                if ii==len(ThisRedshiftList)-1:
                    plot_label (subplot, 'label', xlim, ylim, 
                        x_percentage=0.55, y_percentage=0.85, color='black', xlog=0, ylog=0, 
                        label='MCMC sample', fontsize=13, fontweight='normal') 
                    plot_label (subplot, 'line', xlim, ylim,
                        x_percentage=0.44, y_percentage=0.87, color='black', x2_percentage=0.53, 
                        xlog=0, ylog=0, linestyle='-', linewidth=2)
            
        #LABELS        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.2, 
                    color='black', xlog=0, ylog=0, label='Peeples 2015', 
                    fontsize=13, fontweight='normal') 
        plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.225, 
                    color='blue', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.15) 
           
        plot_label (subplot, 'label', xlim, ylim, 
                x_percentage=0.15, y_percentage=0.1, color='black', xlog=0, ylog=0, 
                label=prefix_this_model, fontsize=13, fontweight='normal') 
        plot_label (subplot, 'line', xlim, ylim,
                x_percentage=0.04, y_percentage=0.12, color='red', x2_percentage=0.13, 
                xlog=0, ylog=0, linestyle='-', linewidth=2)
        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.55, y_percentage=0.8, 
                    color='black', xlog=0, ylog=0, label='Gas Fraction', 
                    fontsize=13, fontweight='normal')   
            
    plt.tight_layout()
    plt.savefig('./fig/plots_gas_fraction.pdf')
    pdf.savefig()
    plt.close()

#end gas fraction


def HI_fraction(G_MR, ThisRedshiftList, pdf):
   
    for ii in range(0,len(ThisRedshiftList)):        
        
        char_redshift="%0.2f" % ThisRedshiftList[ii]
        
        xlim=[7.5,11.0]
        ylim=[-1.,1.0]
       
        bin=0.25
        plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
        fig = plt.figure(figsize=(5,4))
        subplot=plt.subplot()
        subplot.set_ylim(ylim), subplot.set_xlim(xlim)    
            
        #format axis
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(1))    
        subplot.xaxis.set_minor_locator(MultipleLocator(0.25))
            
        xlab='$log_{10}(M_{\mathrm{HI}}[h^{-2}M_{\odot}])$'
        ylab='$\mathrm{log_{10}}(M_{\mathrm{HI}}/L_{\mathrm{r}})$'     
        subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)   
            
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)        
        G0_MR=G_MR[sel]          
        G0_MR=G0_MR[(G0_MR['StellarMass']>0.) & (G0_MR['ColdGas']>0.)]        
        if(opt_rings==1):
            HI=(np.log10(G0_MR['ColdGas']*(1.-G0_MR['H2fraction'])*1.e10*Hubble_h))              
        else:            
            HI=(np.log10(G0_MR['ColdGas']*0.54*1.e10*Hubble_h))
           
        Lr=mag_to_lum(G0_MR['MagDust'][:,17])      
        Fraction=np.log10((10**HI/(Hubble_h*Hubble_h))/Lr)
   
        (x_binned, median, mean, pc16, pc84)=median_and_percentiles (bin, xlim[0], xlim[1], HI, Fraction)          
        sel=(median!=0)        
        subplot.plot(x_binned[sel], median[sel],color='red', linewidth=2)     
        subplot.plot(x_binned[sel], pc16[sel],color='red', linewidth=2, linestyle='--')
        subplot.plot(x_binned[sel], pc84[sel],color='red', linewidth=2, linestyle='--')
    
    
        #OBSERVATIONS
        file=Datadir+'Haynes_newfile'
        fits_table=fits.open(file)
        haynes = fits_table[1]
               
        haynes_MHI=haynes.data['HI']
        haynes_Magr=haynes.data['mr']-5*(np.log10(haynes.data['distance']*1.e6)-1)
        haynes_Lr=mag_to_lum(haynes_Magr)
        fraction=np.log10(10**haynes_MHI/haynes_Lr)
        (x_binned, median, mean, pc16, pc84)=median_and_percentiles(bin, xlim[0], xlim[1]-0.25, haynes_MHI, fraction) 
        obs_x = x_binned
        obs_y = (pc84+pc16)/2       
        obs_y_err = (pc84-pc16)/2               
        subplot.errorbar(obs_x, obs_y, yerr=obs_y_err, fmt='o', markersize=5, ecolor='blue', color='blue')
                
        fits_table.close()
            
        #MCMC sample
        if opt_plot_MCMC_sample==1:
            file = MCMCSampledir + 'mcmc_plus_obs_HIFractionvsStellarMass_z'+char_redshift+'.txt' 
            if os.path.isfile(file):
                obs = Table.read(file, format='ascii')      
                subplot.plot(obs['col1'],np.log10(obs['col4']), color='black', linewidth=2)
                #subplot.errorbar(obs['col1'],obs['col2'], yerr=obs['col3'], 
                #                 fmt='o', markersize=5, ecolor='black', color='black')
            
                if ii==len(ThisRedshiftList)-1:
                    plot_label (subplot, 'label', xlim, ylim, 
                        x_percentage=0.55, y_percentage=0.85, color='black', xlog=0, ylog=0, 
                        label='MCMC sample', fontsize=13, fontweight='normal') 
                    plot_label (subplot, 'line', xlim, ylim,
                        x_percentage=0.44, y_percentage=0.87, color='black', x2_percentage=0.53, 
                        xlog=0, ylog=0, linestyle='-', linewidth=2)
            
        #LABELS        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.2, 
                    color='black', xlog=0, ylog=0, label='Haynes 2011', 
                    fontsize=13, fontweight='normal') 
        plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.225, 
                    color='blue', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.15) 
           
        plot_label (subplot, 'label', xlim, ylim, 
                x_percentage=0.15, y_percentage=0.1, color='black', xlog=0, ylog=0, 
                label=prefix_this_model, fontsize=13, fontweight='normal') 
        plot_label (subplot, 'line', xlim, ylim,
                x_percentage=0.04, y_percentage=0.12, color='red', x2_percentage=0.13, 
                xlog=0, ylog=0, linestyle='-', linewidth=2)
        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.55, y_percentage=0.9, 
                    color='black', xlog=0, ylog=0, label='HI/Lr', 
                    fontsize=13, fontweight='normal')   
            
    plt.tight_layout()
    plt.savefig('./fig/plots_gas_fraction.pdf')
    pdf.savefig()
    plt.close()

#end gas fraction



def HI_MF(G_MR, Volume_MR, G_MRII, Volume_MRII, ThisRedshiftList, pdf):
    for ii in range(0,len(ThisRedshiftList)):        
        
        xlim=[8.0,11.5]
        ylim=[-6.0,0.0]
        bin=0.25
    
        plot_color=['red','purple']        
        plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
        fig = plt.figure(figsize=(5,4))
        subplot=plt.subplot()
        subplot.set_ylim(ylim), subplot.set_xlim(xlim)    
            
        #format axis
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(1))    
        subplot.xaxis.set_minor_locator(MultipleLocator(0.25))
            
        xlab='$\mathrm{log_{10}}(\mathrm{M_{\mathrm{HI}}}[h^{-2}M_{\odot}])$'   
        ylab='$\mathrm{log_{10}}(\phi [h^3 \mathrm{Mpc^{-3}} \mathrm{log_{10}}(M_{\mathrm{HI}}^{-1})])$'     
        subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)   
            
        #PREVIOUS MODELS       
        char_redshift="%0.2f" % ThisRedshiftList[ii]
        if do_previous_model1==1: 
            file = file_previous_model1+'_coldgas_MF.txt' 
            model = Table.read(file, format='ascii')
            subplot.plot(model['col1'],model['col2'],color='red',linestyle=linestyle_previous_model1, linewidth=2)
      
        if do_previous_model2==1: 
            file = file_previous_model2+'_coldgas_MF.txt' 
            model = Table.read(file, format='ascii')
            subplot.plot(model['col1'],model['col2'],color='red',linestyle=linestyle_previous_model2, linewidth=2) 
            
        #MODEL
        #MR
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)         
        G0_MR=G_MR[sel]   
        
        if(opt_rings==1):
            G0_MR=G0_MR[(G0_MR['ColdGas']>0.) & (G0_MR['H2fraction']<1.)]
            HI=(np.log10(G0_MR['ColdGas']*(1.-G0_MR['H2fraction'])*1.e10*Hubble_h))  
        else:
            G0_MR=G0_MR[G0_MR['ColdGas']>0.]
            HI=(np.log10(G0_MR['ColdGas']*0.54*1.e10*Hubble_h))  
        
        bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
        hist_MR=np.histogram(HI, bins=bin_arr, range=(xlim[0],xlim[1]))   
       
        #MRII
        if(MRII==1):
            (sel)=select_current_redshift(G_MRII, ThisRedshiftList, ii, FullSnapshotList_MRII)         
            G0_MRII=G_MRII[sel]             
            if(opt_rings==1):
                G0_MRII=G0_MRII[(G0_MRII['ColdGas']>0.) & (G0_MRII['H2fraction']<1.)]
                HI=(np.log10(G0_MRII['ColdGas']*(1.-G0_MRII['H2fraction'])*1.e10*Hubble_h))  
            else:
                G0_MRII=G0_MRII[G0_MRII['ColdGas']>0.]
                HI=(np.log10(G0_MRII['ColdGas']*0.54*1.e10*Hubble_h)) 
        
            bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
            hist_MRII=np.histogram(HI, bins=bin_arr, range=(xlim[0],xlim[1])) 
            
        #join MR+MRII & plot     
        if(MRII==1):
            cut_MR_MRII=9.0
            plot_joint_MR_MRII(hist_MR, hist_MRII, cut_MR_MRII, Volume_MR, Volume_MRII, 
                               bin, subplot, color='red',linewidth=2, linestyle='-')
        else:
            x_axis=hist_MR[1][0:len(hist_MR[1][:])-1]+bin/2.           
            hist_MR=hist_MR[0]       
            y_axis=np.log10(hist_MR/(Volume_MR*bin))
            subplot.plot(x_axis,y_axis, color='red', linewidth=2, linestyle='-') 
        
        #OBSERVATIONS
        h=0.75
        file = Datadir + 'zwaan2005.txt'       
        obs = Table.read(file, format='ascii')      
        obs_x = obs['col1']
        obs_y = obs['col2']-3.*np.log10(h)      
        obs_y_err = [-obs['col3'],obs['col4']]
       
        subplot.errorbar(obs_x, obs_y, yerr=obs_y_err,
                 fmt='o', markersize=5, ecolor='blue', color='blue')
        
        
        file = Datadir + 'haynes2011_gmf.txt'       
        obs = Table.read(file, format='ascii')      
        obs_x = obs['col1']+2.*np.log10(Hubble_h_WMAP7)
        obs_y = obs['col2']-3.*np.log10(Hubble_h_WMAP7)      
        obs_y_err = [-obs['col3'],obs['col4']]
       
        subplot.errorbar(obs_x, obs_y, yerr=obs_y_err,
                 fmt='o', markersize=5, ecolor='limegreen', color='limegreen')
         
        #MCMC sample
        if opt_plot_MCMC_sample==1:
            file = MCMCSampledir + 'mcmc_plus_obs_ColdGasMassFunction_z'+char_redshift+'.txt' 
            if os.path.isfile(file):
                obs = Table.read(file, format='ascii')      
                subplot.plot(obs['col1'],np.log10(obs['col4']), color='black', linewidth=2)
                           
                if ii==len(ThisRedshiftList)-1:
                    plot_label (subplot, 'label', xlim, ylim, 
                        x_percentage=0.55, y_percentage=0.85, color='black', xlog=0, ylog=0, 
                        label='MCMC sample', fontsize=13, fontweight='normal') 
                    plot_label (subplot, 'line', xlim, ylim,
                        x_percentage=0.44, y_percentage=0.87, color='black', x2_percentage=0.53, 
                        xlog=0, ylog=0, linestyle='-', linewidth=2)    
            
        #LABELS        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.5, 
                    color='black', xlog=0, ylog=0, label='Zwaan 2005', 
                    fontsize=13, fontweight='normal') 
        plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.525, 
                    color='blue', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.15) 
        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.4, 
                    color='black', xlog=0, ylog=0, label='Haynes 2011', 
                    fontsize=13, fontweight='normal') 
        plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.425, 
                    color='limegreen', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.15) 
        
        plot_label_three_models (subplot, xlim, ylim, position='bottom_left')
        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.75, y_percentage=0.8, 
                    color='black', xlog=0, ylog=0, label='HI MF', 
                    fontsize=13, fontweight='normal')   
        
    plt.tight_layout()
    plt.savefig('./fig/plots_HI_MF.pdf')
    pdf.savefig()
    plt.close()
   

#end HI_MF




def sfr_vs_stellar_mass(G_MR, ThisRedshiftList, pdf):
           
    xlim=[8.5,11.5]
    ylim=[-2.5, 3]   
    bin=[0.1,0.05]
    Nbins=[int((xlim[1]-xlim[0])/bin[0]),int((ylim[1]-ylim[0])/bin[1])]

    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                         'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})

    fig = plt.figure(figsize=(15,4))
    grid = gridspec.GridSpec(1, 5)
    grid.update(wspace=0.0, hspace=0.0)

    for ii in range(0,len(ThisRedshiftList)):
        
        char_redshift="%0.1f" % ThisRedshiftList[ii]
        
        subplot=plt.subplot(grid[ii])
        subplot.set_ylim(ylim), subplot.set_xlim(xlim)
        
        xlab='$\mathrm{log_{10}}(M_*[h^{-2}M_{\odot}])$'      
        if ii==0:
            ylab='$\mathrm{log_{10}}(\mathrm{SFR}[h^{-2}M_{\odot}yr^{-1}])$'
        else:
            ylab=''      
        subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)
        
        subplot.text(xlim[0]+2.,ylim[0]+.3,'z='+char_redshift, fontsize=16, fontweight='normal')
        
        if ii==2:
            subplot.text(xlim[0]+0.3,ylim[0]+0.5,'MS evo', fontsize=16, fontweight='normal')
        
        
    
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(1))    
        subplot.xaxis.set_minor_locator(MultipleLocator(0.25))      
        subplot.yaxis.set_minor_locator(MultipleLocator(0.25))
    
        if ii>0:
            plt.tick_params(axis='y', which='both', left='on', labelleft='off')
           
        
        #MODEL
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)
        
        G0_MR=G_MR[sel]   
        G0_MR=G0_MR[(G0_MR['StellarMass']>0.) & (G0_MR['Sfr']>0.)]
        StellarMass=stellar_mass_with_err(G0_MR, Hubble_h, ThisRedshiftList[ii])
        SFR=(np.log10(G0_MR['Sfr']*Hubble_h**2))
        Ngals=len(G0_MR)
      
        H, xedges, yedges = np.histogram2d(StellarMass, SFR, bins=Nbins)            
        extent = [xedges[0], xedges[-1],yedges[0], yedges[-1]]       
        plt.subplots_adjust(bottom=0.15, left=0.15)        
        mylevels = np.linspace(1., Nbins[0], Nbins[0])*Ngals/(Nbins[0]**2/0.7)        
        H = zoom(H, 20)        
        cont=plt.contourf(H.transpose()[::], origin='lower', cmap='Greys_r', levels=mylevels, extent=extent)   
        
        if ii==len(ThisRedshiftList)-1:
            plt.colorbar(format='%d') 
            
        #OBSERVATIONS
        #values at all_z
        
        #ELBAZ2007
        obs_slope_elbaz2007 =[0.77, -99.0, 0.9, -99.0, -99.0]
        obs_offset_elbaz2007=[np.log10(8.7)-(0.77*11.), -99.0, np.log10(7.2)-9, -99.0, -99.0]
        obs_offset_low_elbaz2007=[np.log10(5.0)-(0.77*11.), -99.0, np.log10(3.6)-9, -99.0, -99.0]
        obs_offset_high_elbaz2007=[np.log10(16.1)-(0.77*11.), -99.0, np.log10(14.4)-9, -99.0, -99.0]
        
        #KARIM2011
        file = Datadir + 'karim2011_sfr_mass_sf.txt'       
        karim2011 = Table.read(file, format='ascii') 
        karim_low_z_limit        = karim2011['col4']
        karim_medium_mass        = karim2011['col3']
        karim_sfr                = karim2011['col19']
        karim_sfr_error_up   = karim2011['col20']
        karim_sfr_error_down = karim2011['col21']
        log_karim_sfr_error_up=np.log10((karim_sfr+karim_sfr_error_up)/karim_sfr)
        log_karim_sfr_error_down=np.log10(karim_sfr/(karim_sfr-karim_sfr_error_down))
        
        obs_x=np.arange(xlim[0], xlim[1], 0.01)
        
        if ThisRedshiftList[ii]==0.0:  
            #ELBAZ2007
            obs_y=obs_x*obs_slope_elbaz2007[ii] + obs_offset_elbaz2007[ii] + 2.*np.log10(Hubble_h_WMAP7)
            subplot.plot(obs_x+2.*np.log10(Hubble_h_WMAP7), obs_y, color='firebrick', linewidth=2)            
            obs_y=obs_x*obs_slope_elbaz2007[ii] + obs_offset_low_elbaz2007[ii] + 2.*np.log10(Hubble_h_WMAP7)
            subplot.plot(obs_x+2.*np.log10(Hubble_h_WMAP7), obs_y, color='firebrick', linewidth=2, linestyle='--')            
            obs_y=obs_x*obs_slope_elbaz2007[ii] + obs_offset_high_elbaz2007[ii] + 2.*np.log10(Hubble_h_WMAP7)
            subplot.plot(obs_x+2.*np.log10(Hubble_h_WMAP7), obs_y, color='firebrick', linewidth=2, linestyle='--')
            
        if ThisRedshiftList[ii]==0.4: 
            #KARIM2011
            sel=(karim_low_z_limit==0.2) & (karim_medium_mass>8.8)                
            subplot.errorbar(karim_medium_mass[sel]+2.*np.log10(Hubble_h_WMAP7), 
                             np.log10(karim_sfr[sel])+2.*np.log10(Hubble_h_WMAP7), 
                             [log_karim_sfr_error_down[sel], log_karim_sfr_error_up[sel]], 
                             mfc='white', markeredgecolor='limegreen', color='limegreen', fmt='o', markersize=5)
            sel=(karim_low_z_limit==0.4) & (karim_medium_mass>8.9)                
            subplot.errorbar(karim_medium_mass[sel]+2.*np.log10(Hubble_h_WMAP7), 
                             np.log10(karim_sfr[sel])+2.*np.log10(Hubble_h_WMAP7), 
                             [log_karim_sfr_error_down[sel], log_karim_sfr_error_up[sel]], 
                             color='limegreen', fmt='o', markersize=5)
            
        if ThisRedshiftList[ii]==1.0:  
             #ELBAZ2007
            obs_y=obs_x*obs_slope_elbaz2007[ii] + obs_offset_elbaz2007[ii] + 2.*np.log10(Hubble_h_WMAP7)
            subplot.plot(obs_x+2.*np.log10(Hubble_h_WMAP7), obs_y, color='firebrick', linewidth=2)            
            obs_y=obs_x*obs_slope_elbaz2007[ii] + obs_offset_low_elbaz2007[ii] + 2.*np.log10(Hubble_h_WMAP7)
            subplot.plot(obs_x+2.*np.log10(Hubble_h_WMAP7), obs_y, color='firebrick', linewidth=2, linestyle='--')            
            obs_y=obs_x*obs_slope_elbaz2007[ii] + obs_offset_high_elbaz2007[ii] + 2.*np.log10(Hubble_h_WMAP7)
            subplot.plot(obs_x+2.*np.log10(Hubble_h_WMAP7), obs_y, color='firebrick', linewidth=2, linestyle='--')
            
            #KARIM2011
            sel=(karim_low_z_limit==0.8) & (karim_medium_mass>9.1)                
            subplot.errorbar(karim_medium_mass[sel]+2.*np.log10(Hubble_h_WMAP7), 
                             np.log10(karim_sfr[sel])+2.*np.log10(Hubble_h_WMAP7), 
                             [log_karim_sfr_error_down[sel], log_karim_sfr_error_up[sel]],
                             mfc='white', markeredgecolor='limegreen', color='limegreen', fmt='o', markersize=5)
            sel=(karim_low_z_limit==1.0) & (karim_medium_mass>9.3)                
            subplot.errorbar(karim_medium_mass[sel]+2.*np.log10(Hubble_h_WMAP7), 
                             np.log10(karim_sfr[sel])+2.*np.log10(Hubble_h_WMAP7), 
                             [log_karim_sfr_error_down[sel], log_karim_sfr_error_up[sel]],  
                             color='limegreen', fmt='o', markersize=5)
            
            #Whitaker2013
            file = Datadir + 'whitaker2013_mass_vs_sfr_z0.5_1.0.txt'       
            obs = Table.read(file, format='ascii') 
            subplot.errorbar(obs['col1']+2.*np.log10(Hubble_h_WMAP7), obs['col2']+2.*np.log10(Hubble_h_WMAP7),
                             obs['col3'], mfc='white', markeredgecolor='blue', color='blue', fmt='o', markersize=5)
            file = Datadir + 'whitaker2013_mass_vs_sfr_z1.0_1.5.txt'       
            obs = Table.read(file, format='ascii') 
            subplot.errorbar(obs['col1']+2.*np.log10(Hubble_h_WMAP7), obs['col2']+2.*np.log10(Hubble_h_WMAP7),
                             obs['col3'], color='blue', fmt='o', markersize=5)
            
        if ThisRedshiftList[ii]==2.0:  
            #KARIM2011
            sel=(karim_low_z_limit==1.6) & (karim_medium_mass>9.6)                
            subplot.errorbar(karim_medium_mass[sel]+2.*np.log10(Hubble_h_WMAP7), 
                             np.log10(karim_sfr[sel])+2.*np.log10(Hubble_h_WMAP7), 
                             [log_karim_sfr_error_down[sel], log_karim_sfr_error_up[sel]],
                             mfc='white', markeredgecolor='limegreen', color='limegreen', fmt='o', markersize=5)
            sel=(karim_low_z_limit==2.0) & (karim_medium_mass>9.8)                
            subplot.errorbar(karim_medium_mass[sel]+2.*np.log10(Hubble_h_WMAP7), 
                             np.log10(karim_sfr[sel])+2.*np.log10(Hubble_h_WMAP7), 
                             [log_karim_sfr_error_down[sel], log_karim_sfr_error_up[sel]],  
                             color='limegreen', fmt='o', markersize=5)
            
            #Whitaker2013
            file = Datadir + 'whitaker2013_mass_vs_sfr_z1.5_2.0.txt'       
            obs = Table.read(file, format='ascii') 
            subplot.errorbar(obs['col1']+2.*np.log10(Hubble_h_WMAP7), obs['col2']+2.*np.log10(Hubble_h_WMAP7),
                             obs['col3'], mfc='white', markeredgecolor='blue', color='blue', fmt='o', markersize=5)
            file = Datadir + 'whitaker2013_mass_vs_sfr_z2.0_2.5.txt'       
            obs = Table.read(file, format='ascii') 
            subplot.errorbar(obs['col1']+2.*np.log10(Hubble_h_WMAP7), obs['col2']+2.*np.log10(Hubble_h_WMAP7),
                             obs['col3'], color='blue', fmt='o', markersize=5)
            
        if ThisRedshiftList[ii]==3.0:
            #KARIM2011
            sel=(karim_low_z_limit==2.5) & (karim_medium_mass>10.0)                
            subplot.errorbar(karim_medium_mass[sel]+2.*np.log10(Hubble_h_WMAP7), 
                             np.log10(karim_sfr[sel])+2.*np.log10(Hubble_h_WMAP7), 
                             [log_karim_sfr_error_down[sel], log_karim_sfr_error_up[sel]],
                             color='limegreen', fmt='o', markersize=5)
         
        #labels
        if ii==0:
            plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.82, 
                        color='black', xlog=0, ylog=0, label='Karim 2011', 
                        fontsize=13, fontweight='normal') 
            plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.845, 
                        color='limegreen', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.15) 
        
            plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.9, 
                        color='black', xlog=0, ylog=0, label='Whitaker 2013', 
                        fontsize=13, fontweight='normal') 
            plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.925, 
                        color='blue', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.15) 
        
            plot_label (subplot, 'label', xlim, ylim, 
                    x_percentage=0.15, y_percentage=0.74, color='black', xlog=0, ylog=0, 
                    label='Elbaz 2007', fontsize=13, fontweight='normal') 
            plot_label (subplot, 'line', xlim, ylim,
                    x_percentage=0.04, y_percentage=0.76, color='firebrick', x2_percentage=0.13, 
                    xlog=0, ylog=0, linestyle='-', linewidth=2)
    #endfor
        
    plt.tight_layout()
    plt.savefig('./fig/plots_sfr_vs_stellar_mass.pdf')
    pdf.savefig()
    plt.close()
#endif stellar_mass_vs_sfr




def ur_vs_r(G_MR, ThisRedshiftList, pdf):
           
    xlim=[-23.,-14.]
    ylim=[1.0, 3.2]   
    bin=[0.5,0.025]
    Nbins=[int((xlim[1]-xlim[0])/bin[0]),int((ylim[1]-ylim[0])/bin[1])]

    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                         'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})

    fig = plt.figure(figsize=(5,4))
    subplot=plt.subplot()
    
    subplot.set_ylim(ylim), subplot.set_xlim(xlim)      
    subplot.set_xlabel('r', fontsize=16), subplot.set_ylabel('u-r', fontsize=16) 
    
    majorFormatter = FormatStrFormatter('%2d')
    subplot.xaxis.set_major_locator(MultipleLocator(2))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25))      

    for ii in range(0,len(ThisRedshiftList)):                     
             
        subplot.text(xlim[0]+0.2,ylim[0]+0.25,'z=0', fontsize=16, fontweight='normal')     
        subplot.text(xlim[0]+0.2,ylim[0]+0.05,'r vs u-r cut', fontsize=16, fontweight='normal')
                  
        #MODEL
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)
        
        G0_MR=G_MR[sel]   
        G0_MR=G0_MR[(G0_MR['MagDust'][:,15]<99.) & (G0_MR['MagDust'][:,17]<99.)]        
        color_ur=G0_MR['MagDust'][:,15]-G0_MR['MagDust'][:,17]  
        Magr=G0_MR['MagDust'][:,17]         
        Ngals=len(G0_MR)
      
        H, xedges, yedges = np.histogram2d(Magr, color_ur, bins=Nbins)            
        extent = [xedges[0], xedges[-1],yedges[0], yedges[-1]]       
        plt.subplots_adjust(bottom=0.15, left=0.15)        
        mylevels = np.linspace(1., Nbins[0]*4., Nbins[0]*4.)*Ngals/(Nbins[0]**2/0.2)        
        H = zoom(H, 20)        
        cont=plt.contourf(H.transpose()[::], origin='lower', cmap='Greys_r', levels=mylevels, extent=extent)        
        plt.colorbar(format='%d') 
        
        #BestFit Cut   
        bin=0.01
        x_arr=np.arange(xlim[0],xlim[1]+bin,bin)        
        y_arr=(offset_red_fraction[0]-slope_red_fraction[0]*np.tanh((x_arr+18.07)/1.09))
        subplot.plot(x_arr,y_arr,color='red', linestyle='-', linewidth=2)  
        
        #OBSERVATIONAL CUT 
        Nbin=0.01
        x_arr=np.arange(xlim[0],xlim[1]+Nbin,Nbin)       
        y_arr=2.06-0.244*np.tanh((x_arr+20.07)/1.09)        
        subplot.plot(x_arr,y_arr,color='blue', linestyle='--', linewidth=2) 
        
        #LABELS
        plot_label (subplot, 'label', xlim, ylim, 
                    x_percentage=0.15, y_percentage=0.9, color='black', xlog=0, ylog=0, 
                    label='Baldry 2004', fontsize=13, fontweight='normal') 
        plot_label (subplot, 'line', xlim, ylim,
                    x_percentage=0.04, y_percentage=0.92, color='blue', x2_percentage=0.13, 
                    xlog=0, ylog=0, linestyle='--', linewidth=2)
        
        plot_label (subplot, 'label', xlim, ylim, 
                    x_percentage=0.15, y_percentage=0.82, color='black', xlog=0, ylog=0, 
                    label='Best Fit cut', fontsize=13, fontweight='normal') 
        plot_label (subplot, 'line', xlim, ylim,
                    x_percentage=0.04, y_percentage=0.84, color='red', x2_percentage=0.13, 
                    xlog=0, ylog=0, linestyle='-', linewidth=2)
        
    #endfor
        
    plt.tight_layout()
    plt.savefig('./fig/plots_ur_vs_r.pdf')
    pdf.savefig()
    plt.close()
#endif ur_vs_r






def UVJ_colour(G_MR, ThisRedshiftList, pdf):
           
    xlim=[-0.5,2.5]
    ylim=[-0.5, 2.5]   
    bin=[0.05,0.05]
    Nbins=[int((xlim[1]-xlim[0])/bin[0]),int((ylim[1]-ylim[0])/bin[1])]

    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                         'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})

    fig = plt.figure(figsize=(12,4))
    grid = gridspec.GridSpec(1, 4)
    grid.update(wspace=0.0, hspace=0.0)

    for ii in range(0,len(ThisRedshiftList)):
        
        char_redshift="%0.1f" % ThisRedshiftList[ii]
        
        subplot=plt.subplot(grid[ii])
        subplot.set_ylim(ylim), subplot.set_xlim(xlim)
        if ii==0:
            ylabel='U-V'
        else:
             ylabel=''
        subplot.set_xlabel('V-J', fontsize=16), subplot.set_ylabel(ylabel, fontsize=16)
        
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(1))    
        subplot.xaxis.set_minor_locator(MultipleLocator(0.25))      
        subplot.yaxis.set_minor_locator(MultipleLocator(0.25)) 
        
        if ii>0:
            plt.tick_params(axis='y', which='both', left='on', labelleft='off')
        
        subplot.text(xlim[0]+2.,ylim[0]+.2,'z='+char_redshift, fontsize=16, fontweight='normal')
        
        if ii==2:
            subplot.text(xlim[0]+0.2,ylim[0]+0.2,'UVJ cut', fontsize=16, fontweight='normal')
                  
        #MODEL
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)
        
        G0_MR=G_MR[sel]   
        G0_MR=G0_MR[(G0_MR['MagDust'][:,0]<99.) & (G0_MR['MagDust'][:,2]<99.) & (G0_MR['MagDust'][:,7]<99.)]        
        color_UV=G0_MR['MagDust'][:,0]-G0_MR['MagDust'][:,2]  
        color_VJ=G0_MR['MagDust'][:,2]-G0_MR['MagDust'][:,7]       
        Ngals=len(G0_MR)
      
        H, xedges, yedges = np.histogram2d(color_VJ, color_UV, bins=Nbins)            
        extent = [xedges[0], xedges[-1],yedges[0], yedges[-1]]       
        plt.subplots_adjust(bottom=0.15, left=0.15)        
        mylevels = np.linspace(1., Nbins[0], Nbins[0])*Ngals/(Nbins[0]**2/2.5)        
        H = zoom(H, 20)        
        cont=plt.contourf(H.transpose()[::], origin='lower', cmap='Greys_r', levels=mylevels, extent=extent)        
        
        if ii==len(ThisRedshiftList)-1:
            plt.colorbar(format='%d') 
        
        #BestFit Cut   
        bin=0.01
        slope=slope_red_fraction[ii+1]
        offset=offset_red_fraction[ii+1]
        minimum_y=minimum_y_red_fraction[ii+1]
        
        x_arr=np.arange(xlim[0],xlim[1]+bin,bin)
        cut1=np.zeros(len(x_arr),dtype=np.float32)+minimum_y      
        cut2=x_arr*slope+offset
  
        sel1=x_arr<((minimum_y-offset)/slope)
        subplot.plot(x_arr[sel1],cut1[sel1],color='red', linestyle='-', linewidth=2)  
         
        sel2=x_arr > ((minimum_y-offset)/slope)
        subplot.plot(x_arr[sel2],cut2[sel2],color='red', linestyle='-', linewidth=2)  
        
        #OBSERVATIONAL CUT    
        Nbin=0.01
        slope=0.88
        if(ThisRedshiftList[ii]<1.):
            offset=0.69 
        else: 
            offset=0.59

        x_arr=np.arange(xlim[0],xlim[1]+Nbin,Nbin)
        cut1=np.zeros(len(x_arr),dtype=np.float32)+1.3   
        cut2=x_arr*slope+offset
  
        sel1=x_arr<((1.3-offset)/slope)
        subplot.plot(x_arr[sel1],cut1[sel1],color='blue', linestyle='--', linewidth=2)  
  
        sel2=x_arr>((1.3-offset)/slope) 
        subplot.plot(x_arr[sel2],cut2[sel2],color='blue', linestyle='--', linewidth=2)  
        
        
        #LABELS
        if ii==0:
            plot_label (subplot, 'label', xlim, ylim, 
                        x_percentage=0.15, y_percentage=0.15, color='black', xlog=0, ylog=0, 
                        label='Muzzin 2013', fontsize=13, fontweight='normal') 
            plot_label (subplot, 'line', xlim, ylim,
                        x_percentage=0.04, y_percentage=0.17, color='blue', x2_percentage=0.13, 
                        xlog=0, ylog=0, linestyle='--', linewidth=2)
        
            plot_label (subplot, 'label', xlim, ylim, 
                        x_percentage=0.15, y_percentage=0.07, color='black', xlog=0, ylog=0, 
                        label='Best Fit cut', fontsize=13, fontweight='normal') 
            plot_label (subplot, 'line', xlim, ylim,
                        x_percentage=0.04, y_percentage=0.09, color='red', x2_percentage=0.13, 
                        xlog=0, ylog=0, linestyle='-', linewidth=2)
    #endfor
        
    plt.tight_layout()
    plt.savefig('./fig/plots_UVJ_colour.pdf')
    pdf.savefig()
    plt.close()
#endif UVJ_colour





    


def morphology_vs_stellarmass(G_MR, G_MRII, ThisRedshiftList, pdf):
    
    for ii in range(0,len(ThisRedshiftList)):        
        
        char_redshift="%0.2f" % ThisRedshiftList[ii]
        
        xlim=[8.0,12.]
        ylim=[0.0,1.0]
        bin=0.25
    
        plot_color=['red','purple']        
        plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
        fig = plt.figure(figsize=(5,4))
        subplot=plt.subplot()
        subplot.set_ylim(ylim), subplot.set_xlim(xlim)    
            
        #format axis
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(1))    
        subplot.xaxis.set_minor_locator(MultipleLocator(0.25))
            
        xlab='$\mathrm{log_{10}}(\mathrm{M_{\star}}[h^{-2}M_{\odot}])$'   
        ylab='Fraction'     
        subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)   
       
        #MODEL
        #MR
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)         
        G0_MR=G_MR[sel]                   
        StellarMass=stellar_mass_with_err(G0_MR, Hubble_h, ThisRedshiftList[ii])
        BulgeMassRatio=G0_MR['BulgeMass']/G0_MR['StellarMass']
        
        Mass_arr=np.arange(xlim[0],np.amax(StellarMass)+bin/2.,bin)
        BulgeFraction=np.zeros(len(Mass_arr),dtype=np.float32)
        DiskFraction=np.zeros(len(Mass_arr),dtype=np.float32)
        IrrFraction=np.zeros(len(Mass_arr),dtype=np.float32)
                  
        for ll in range(0,len(Mass_arr)):
                sel_bulge=G0_MR[(BulgeMassRatio>0.7) &
                                (StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
                sel_disk=G0_MR[(BulgeMassRatio<0.7) & (BulgeMassRatio>0.01) &
                               (StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
                sel_irr=G0_MR[(BulgeMassRatio<0.01) & 
                              (StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
                #print(len(sel_bulge),len(sel_disk),len(sel_irr))
                if(float(len(sel_bulge))+float(len(sel_disk))+float(len(sel_irr))>0):
                    BulgeFraction[ll]=float(len(sel_bulge))/(float(len(sel_bulge))+float(len(sel_disk))+float(len(sel_irr)))
                    DiskFraction[ll]=float(len(sel_disk))/(float(len(sel_bulge))+float(len(sel_disk))+float(len(sel_irr)))
                    IrrFraction[ll]=float(len(sel_irr))/(float(len(sel_bulge))+float(len(sel_disk))+float(len(sel_irr)))
        
        subplot.plot(Mass_arr, BulgeFraction, color='red', linestyle='--', linewidth=2)
        subplot.plot(Mass_arr, DiskFraction, color='blue', linestyle='--', linewidth=2)
        subplot.plot(Mass_arr, IrrFraction, color='green', linestyle='--', linewidth=2)
        
       
        #MRII
        if(MRII==1):
            (sel)=select_current_redshift(G_MRII, ThisRedshiftList, ii, FullSnapshotList_MRII)         
            G0_MRII=G_MRII[sel]                   
            StellarMass=stellar_mass_with_err(G0_MRII, Hubble_h, ThisRedshiftList[ii])
            BulgeMassRatio=G0_MRII['BulgeMass']/G0_MRII['StellarMass']
        
            Mass_arr=np.arange(xlim[0],np.amax(StellarMass)+bin/2.,bin)
            BulgeFraction=np.zeros(len(Mass_arr),dtype=np.float32)
            DiskFraction=np.zeros(len(Mass_arr),dtype=np.float32)
            IrrFraction=np.zeros(len(Mass_arr),dtype=np.float32)
                  
            for ll in range(0,len(Mass_arr)):
                sel_bulge=G0_MRII[(BulgeMassRatio>0.7) &
                                (StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
                sel_disk=G0_MRII[(BulgeMassRatio<0.7) & (BulgeMassRatio>0.01) &
                               (StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
                sel_irr=G0_MRII[(BulgeMassRatio<0.01) & 
                                (StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
                #print(len(sel_bulge),len(sel_disk),len(sel_irr))
                if(float(len(sel_bulge))+float(len(sel_disk))+float(len(sel_irr))>0):                     
                    BulgeFraction[ll]=float(len(sel_bulge))/(float(len(sel_bulge))+float(len(sel_disk))+float(len(sel_irr)))
                    DiskFraction[ll]=float(len(sel_disk))/(float(len(sel_bulge))+float(len(sel_disk))+float(len(sel_irr)))
                    IrrFraction[ll]=float(len(sel_irr))/(float(len(sel_bulge))+float(len(sel_disk))+float(len(sel_irr)))

            subplot.plot(Mass_arr, BulgeFraction, color='red', linestyle='-', linewidth=2)
            subplot.plot(Mass_arr, DiskFraction, color='blue', linestyle='-', linewidth=2)
            subplot.plot(Mass_arr, IrrFraction, color='green', linestyle='-', linewidth=2)
              
        #OBSERVATIONS
        h=0.7
        file = Datadir + 'conselice2006_bulge_fract.txt'       
        obs = Table.read(file, format='ascii')       
        subplot.errorbar(obs['col1']+2.*np.log10(h), obs['col2'], obs['col3'],
                 fmt='o', markersize=5, ecolor='red', color='red')
        file = Datadir + 'conselice2006_disk_fract.txt'       
        obs = Table.read(file, format='ascii')       
        subplot.errorbar(obs['col1']+2.*np.log10(h), obs['col2'], obs['col3'],
                 fmt='o', markersize=5, ecolor='blue', color='blue')
        file = Datadir + 'conselice2006_irr_fract.txt'       
        obs = Table.read(file, format='ascii')       
        subplot.errorbar(obs['col1']+2.*np.log10(h), obs['col2'], obs['col3'],
                 fmt='o', markersize=5, ecolor='green', color='green')
      
        #MCMC sample
        if opt_plot_MCMC_sample==1:
            file = MCMCSampledir + 'mcmc_plus_obs_BulgeFraction_z'+char_redshift+'.txt' 
            if os.path.isfile(file):
                obs = Table.read(file, format='ascii')      
                subplot.plot(obs['col1'],obs['col4'], color='black', linewidth=2)
                          
                if ii==len(ThisRedshiftList)-1:
                    plot_label (subplot, 'label', xlim, ylim, 
                        x_percentage=0.55, y_percentage=0.85, color='black', xlog=0, ylog=0, 
                        label='MCMC sample', fontsize=13, fontweight='normal') 
                    plot_label (subplot, 'line', xlim, ylim,
                        x_percentage=0.44, y_percentage=0.87, color='black', x2_percentage=0.53, 
                        xlog=0, ylog=0, linestyle='-', linewidth=2)    
            
        #LABELS        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.075, y_percentage=0.9, 
                    color='black', xlog=0, ylog=0, label='Conselice 2006', 
                    fontsize=13, fontweight='normal') 
        plot_label (subplot, 'symbol', xlim, ylim, x_percentage=0.05, y_percentage=0.925, 
                    color='blue', xlog=0, ylog=0, sym='o', sym_size=5, err_size=0.025) 
        
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.75, y_percentage=0.8, 
                    color='black', xlog=0, ylog=0, label='Morphology', 
                    fontsize=13, fontweight='normal')   
        
    plt.tight_layout()
    plt.savefig('./fig/plots_HI_MF.pdf')
    pdf.savefig()
    plt.close()
   

#end morphology_vs_stellarmass   
    
    
def sizes_vs_stellarmass(G_MR, ThisRedshiftList, pdf):
           
    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
    fig = plt.figure(figsize=(10,5))
    grid = gridspec.GridSpec(1, 2)
       
    for ii in range(0,len(ThisRedshiftList)):        
        
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)        
        G0_MR=G_MR[sel]          
                   
        #Disks    
        xlim=[9.5,11.5]
        ylim=[0.,1.]
        bin=0.2
                         
        subplot=plt.subplot(grid[0])    
        subplot.set_ylim(ylim), subplot.set_xlim(xlim)            
        #format axis
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(0.5))    
        subplot.xaxis.set_minor_locator(MultipleLocator(.1))            
        xlab='$\mathrm{log_{10}}(M_*[h^{-2}M_{\odot}])$'       
        ylab='$\mathrm{R_{50}}(\mathrm{Kpc})$'     
        subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)  
        
        Gal=G0_MR[(G0_MR['StellarMass']>0.) & (G0_MR['DiskMass']>0.) &       
                  (G0_MR['DiskMass']/G0_MR['StellarMass']>0.8)]      
        StellarMass=stellar_mass_with_err(Gal, Hubble_h, ThisRedshiftList[ii])
        StellarMass-=np.log10(Hubble_h**2) 
        StellarDiskRadius=Gal['StellarDiskRadius']/2.*1000./Hubble_h #(from Mpc/h -> Kpc)
        
        (x_binned, median, mean, pc16, pc84)=median_and_percentiles (bin, xlim[0], xlim[1], StellarMass, StellarDiskRadius)   
        subplot.plot(x_binned, np.log10(median),color='red', linewidth=2)
        subplot.plot(x_binned, np.log10(pc16),color='red', linewidth=2, linestyle='--')
        subplot.plot(x_binned, np.log10(pc84),color='red', linewidth=2, linestyle='--')
        #subplot.plot(x_binned, median,color='red', linewidth=2) 
    
    
        #Bulge    
        xlim=[9.5,11.5]
        ylim=[-1.,1.]
        bin=0.2
                         
        subplot=plt.subplot(grid[1])    
        subplot.set_ylim(ylim), subplot.set_xlim(xlim)            
        #format axis
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(0.5))    
        subplot.xaxis.set_minor_locator(MultipleLocator(.1))            
        xlab='$\mathrm{log_{10}}(M_*[h^{-2}M_{\odot}])$'       
        ylab='$\mathrm{R_{50}}(\mathrm{Kpc})$'     
        subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16) 
        
        Gal=G0_MR[(G0_MR['StellarMass']>0.) & (G0_MR['BulgeMass']>0.) &       
                  (G0_MR['BulgeMass']/G0_MR['StellarMass']>0.2)]      
        StellarMass=stellar_mass_with_err(Gal, Hubble_h, ThisRedshiftList[ii])
        StellarMass-=np.log10(Hubble_h**2)
        StellarDiskRadius=Gal['BulgeSize']*1000./Hubble_h #(from Mpc/h -> Kpc)
        
        (x_binned, median, mean, pc16, pc84)=median_and_percentiles (bin, xlim[0], xlim[1], StellarMass, StellarDiskRadius)   
        subplot.plot(x_binned, np.log10(median),color='red', linewidth=2)
        subplot.plot(x_binned, np.log10(pc16),color='red', linewidth=2, linestyle='--')
        subplot.plot(x_binned, np.log10(pc84),color='red', linewidth=2, linestyle='--')
        #subplot.plot(x_binned, median,color='red', linewidth=2) 
    
    plt.tight_layout()
    plt.savefig('./fig/plots_sizes_vs_stellarmass.pdf')
    pdf.savefig()
    plt.close() 
        
#end   sizes_vs_stellarmass 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    



def bluck_red_fractions(G_MR, ThisRedshiftList, pdf):
       
    ii=0
    (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)
                 
    G0_MR=G_MR[sel]   
               
    xmin=8.0
    xmax=13.0
    ymin=-12.
    ymax=-8.0
    bin=0.1

    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
    fig = plt.figure(figsize=(9,9))
    grid = gridspec.GridSpec(1, 2)
    #subplot=plt.subplot(grid[ii]) 
    subplot=plt.subplot()
               
        
        
    #FIND PASSIVE CUT
    subplot.set_ylim([ymin, ymax]), subplot.set_xlim([xmin, xmax])         
    xlab='$log_{10}(M_*[h^{-2}M_{\odot}])$'           
    ylab='$log_{10}(\phi [h^3 Mpc^{-3} log_{10}(M^{-1})])$'               
    subplot.set_xlabel(xlab, fontsize=16)
    subplot.set_ylabel(ylab, fontsize=16)     
        
        
    BHMass=np.log10(G0_MR['BlackHoleMass']*1.e10/Hubble_h) 
    StellarMass=np.log10(G0_MR['StellarMass']*1.e10/Hubble_h) 
    SFR=np.log10(G0_MR['Sfr'] ) 
    SSFR=np.log10(G0_MR['Sfr']/(G0_MR['StellarMass']*1.e10/Hubble_h)) 
            
    sel=np.logical_and(SSFR>-100.,StellarMass>-10.)    
    StellarMass=StellarMass[sel]
    SSFR=SSFR[sel]
    #subplot.plot(StellarMass, SSFR, 'o', markersize=2, color='blue')
             
    #subplot.hist2d(StellarMass, SSFR, bins=30, norm=LogNorm())  
    #subplot.hexbin(StellarMass, SSFR, gridsize=200)
    #plt.colorbar()
        
    #plt.tight_layout()
    pdf.savefig()
    plt.close()
        
    #PLOT RED FRACTIONS WITHOUT BINNING    
     
    G0_MR=G0_MR[G0_MR['Type']==0]           
    BHMass=np.log10(G0_MR['BlackHoleMass']*1.e10/Hubble_h)    
    SSFR=np.log10(G0_MR['Sfr']/(G0_MR['StellarMass']*1.e10/Hubble_h)) 
    HaloMass=np.log10(G0_MR['Mvir']*1.e10/Hubble_h)   
    
    
    
    #BH MASS
    xmin=5.0
    xmax=9.0
    ymin=0.0
    ymax=1.0
    bin=0.5
    
    fig = plt.figure(figsize=(12,5))      
    subplot=plt.subplot(grid[0])
    subplot.set_ylim([ymin, ymax]), subplot.set_xlim([xmin, xmax])         
    xlab='$log_{10}(M_{BH}[M_{\odot}])$'           
    ylab='$f_{Quench}$'               
    subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)   
    majorFormatter = FormatStrFormatter('%d')
    subplot.xaxis.set_major_locator(MultipleLocator(1))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25))      
    subplot.yaxis.set_minor_locator(MultipleLocator(0.25))           
    #plt.tick_params(axis='y', which='both', left='on', labelleft='off')
    
    Nbins=int((xmax-xmin)/bin+1)  
    hist=np.array([],dtype=np.float64)
    x_array=np.array([],dtype=np.float64)
    Aindex=np.array(len(G0_MR),dtype=np.float64)
    Aindex=SSFR
    for ii in range(0,Nbins):              
        n_passive  = len(Aindex[(BHMass > (xmin+ii*bin)) & (BHMass < (xmin+(ii+1)*bin)) & (SSFR<-10.5)])
        n_total  = len(Aindex[(BHMass > (xmin+ii*bin)) & (BHMass < (xmin+(ii+1)*bin))])
        if n_total>0. :
            hist=np.append(hist,n_passive/n_total)
        else:
            hist=np.append(hist,0.)
        x_array=np.append(x_array,xmin+ii*bin+bin/2.)
        #endfor             
    subplot.plot(x_array,hist,color='red',linestyle='-', linewidth=2)
    
    
    #HALOMASS
    xmin=10.0
    xmax=16.0
    ymin=0.0
    ymax=1.0
    bin=0.5
    
    subplot=plt.subplot(grid[1])
    subplot.set_ylim([ymin, ymax]), subplot.set_xlim([xmin, xmax])         
    xlab='$log_{10}(M_{200c}[M_{\odot}])$'           
    ylab='$f_{Quench}$'               
    subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)   
    majorFormatter = FormatStrFormatter('%d')
    subplot.xaxis.set_major_locator(MultipleLocator(1))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25))      
    subplot.yaxis.set_minor_locator(MultipleLocator(0.25))           
    #plt.tick_params(axis='y', which='both', left='on', labelleft='off')
    
    Nbins=int((xmax-xmin)/bin+1)  
    hist=np.array([],dtype=np.float64)
    x_array=np.array([],dtype=np.float64)
    Aindex=np.array(len(G0_MR),dtype=np.float64)
    Aindex=SSFR
    for ii in range(0,Nbins):              
        n_passive  = len(Aindex[(HaloMass > (xmin+ii*bin)) & (HaloMass < (xmin+(ii+1)*bin)) & (SSFR<-10.5)])
        n_total  = len(Aindex[(HaloMass > (xmin+ii*bin)) & (HaloMass < (xmin+(ii+1)*bin))])
        if n_total>0. :
            hist=np.append(hist,n_passive/n_total)
        else:
            hist=np.append(hist,0.)
        x_array=np.append(x_array,xmin+ii*bin+bin/2.)
        #endfor             
    subplot.plot(x_array,hist,color='red',linestyle='-', linewidth=2)
            
        
    plt.tight_layout()
    plt.savefig('./fig/plots_bluck_red_fractions_no_binning.pdf')
    pdf.savefig()
    plt.close()
        
    #PLOT RED FRACTIONS
    xmin=5.0
    xmax=9.0
    ymin=0.0
    ymax=1.0
    bin=0.5
        
    fig = plt.figure(figsize=(12,5))      
    subplot=plt.subplot(grid[0])
    subplot.set_ylim([ymin, ymax]), subplot.set_xlim([xmin, xmax])         
    xlab='$log_{10}(M_{BH}[M_{\odot}])$'           
    ylab='$f_{Quench}$'               
    subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)   
    majorFormatter = FormatStrFormatter('%d')
    subplot.xaxis.set_major_locator(MultipleLocator(1))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25))      
    subplot.yaxis.set_minor_locator(MultipleLocator(0.25))           
    #plt.tick_params(axis='y', which='both', left='on', labelleft='off')
         
    BHMass=np.log10(G0_MR['BlackHoleMass']*1.e10/Hubble_h) 
    #BHMass=np.log10(G0_MR['BulgeMass']*1.e10/Hubble_h) 
    #StellarMass=np.log10(G0_MR['StellarMass']*1.e10/Hubble_h)       
    SSFR=np.log10(G0_MR['Sfr']/(G0_MR['StellarMass']*1.e10/Hubble_h)) 
    HaloMass=np.log10(G0_MR['Mvir']*1.e10/Hubble_h) 
        
    sel=G0_MR['Type']==0
    BHMass=BHMass[sel]
    SSFR=SSFR[sel]
    HaloMass=HaloMass[sel]
    Index_arr=HaloMass
        
    plot_colors=['blue','green','yellow','red']
    halo_min_mass=11.
    halo_bin=1.0
    for jj in range (0,4):
        print((halo_min_mass+jj*halo_bin),(halo_min_mass+(jj+1)*halo_bin))
        sel=np.logical_and(HaloMass > (halo_min_mass+jj*halo_bin), HaloMass < (halo_min_mass+(jj+1)*halo_bin))
        Nbins=int((xmax-xmin)/bin+1)  
        hist=np.array([],dtype=np.float64)
        x_array=np.array([],dtype=np.float64)
        ABHMass=BHMass[sel]
        ASSFR=SSFR[sel]
        Aindex=Index_arr[sel]
        for ii in range(0,Nbins):              
            n_passive  = len(Aindex[np.logical_and(np.logical_and(ABHMass > (xmin+ii*bin), ABHMass < (xmin+(ii+1)*bin)), 
                                           ASSFR<-10.5)])
            n_total  = len(Aindex[np.logical_and(ABHMass > (xmin+ii*bin), ABHMass < (xmin+(ii+1)*bin))])
            if n_total>0. :
                hist=np.append(hist,n_passive/n_total)
            else:
                hist=np.append(hist,0.)
            x_array=np.append(x_array,xmin+ii*bin+bin/2.)
        #endfor             
        subplot.plot(x_array,hist,color=plot_colors[jj],linestyle='-', linewidth=2)
            
    #endfor             
        
    #plt.tight_layout()
    #plt.savefig('./fig/plots.pdf')
    #pdf.savefig()
    #plt.close()
            
    #halo mass bins
    xmin=11.0
    xmax=15.0
    ymin=0.0
    ymax=1.0
    bin=0.5
        
    #fig = plt.figure(figsize=(9,9))      
    subplot=plt.subplot(grid[1]) 
    subplot.set_ylim([ymin, ymax]), subplot.set_xlim([xmin, xmax])         
    xlab='$log_{10}(M_{200c}[M_{\odot}])$'           
    ylab='$f_{Quench}$'               
    subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)   
    majorFormatter = FormatStrFormatter('%d')
    subplot.xaxis.set_major_locator(MultipleLocator(1))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25))      
    subplot.yaxis.set_minor_locator(MultipleLocator(0.25))           
    #plt.tick_params(axis='y', which='both', left='on', labelleft='off')
          
    BHMass=np.log10(G0_MR['BlackHoleMass']*1.e10/Hubble_h) 
    #BHMass=np.log10(G0_MR['BulgeMass']*1.e10/Hubble_h) 
    #StellarMass=np.log10(G0_MR['StellarMass']*1.e10/Hubble_h)       
    SSFR=np.log10(G0_MR['Sfr']/(G0_MR['StellarMass']*1.e10/Hubble_h)) 
    HaloMass=np.log10(G0_MR['Mvir']*1.e10/Hubble_h) 
        
    sel=G0_MR['Type']==0
    BHMass=BHMass[sel]
    SSFR=SSFR[sel]
    HaloMass=HaloMass[sel]
    Index_arr=HaloMass
    
    plot_colors=['blue','green','yellow','red']
    bh_min_mass=5.
    bh_bin=1.0
        
    for jj in range (0,4):
            
        print((bh_min_mass+jj*bh_bin),(bh_min_mass+(jj+1)*bh_bin))
        sel=np.logical_and(BHMass > (bh_min_mass+jj*bh_bin), BHMass < (bh_min_mass+(jj+1)*bh_bin))
            
        Nbins=int((xmax-xmin)/bin+1)  
        hist=np.array([],dtype=np.float64)
        x_array=np.array([],dtype=np.float64)
        AHaloMass=HaloMass[sel]
        ASSFR=SSFR[sel]
        Aindex=Index_arr[sel]
        for ii in range(0,Nbins):             
            n_passive  = len(Aindex[np.logical_and(np.logical_and(AHaloMass > (xmin+ii*bin), AHaloMass < (xmin+(ii+1)*bin)),
                                          ASSFR<-10.5)])           
            n_total  = len(Aindex[np.logical_and(AHaloMass > (xmin+ii*bin), AHaloMass < (xmin+(ii+1)*bin))])
            if n_total>0. :
                hist=np.append(hist,n_passive/n_total)
            else:
                hist=np.append(hist,0.)
            x_array=np.append(x_array,xmin+ii*bin+bin/2.)
        #endfor             
        subplot.plot(x_array,hist,color=plot_colors[jj],linestyle='-', linewidth=2)
            
    #endfor             
      
    plt.tight_layout()
    plt.savefig('./fig/plots_bluck_red_fractions.pdf')
    pdf.savefig()
    plt.close()
             
#end bluck_red_fractions


def sat_fraction(G_MR, ThisRedshiftList, pdf):
    
    xlim=[8.5,11.5]
    ylim=[0., 1.] 
           
    plot_color=['red','purple']        
    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
    
    fig = plt.figure(figsize=(15,4))
    grid = gridspec.GridSpec(1, 5)
    grid.update(wspace=0.0, hspace=0.0)
    
    for ii in range (0,len(ThisRedshiftList)):
           
        char_redshift="%0.2f" % ThisRedshiftList[ii]
            
        subplot=plt.subplot(grid[ii])
        subplot.set_ylim(ylim), subplot.set_xlim(xlim)
        
        xlab='$\mathrm{log_{10}}(M_*[h^{-2}M_{\odot}])$'      
        if ii==0:
            ylab='Satellite Fraction'
        else:
            ylab=''      
        subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)
        
        majorFormatter = FormatStrFormatter('%d')
        subplot.xaxis.set_major_locator(MultipleLocator(1))    
        subplot.xaxis.set_minor_locator(MultipleLocator(0.25))      
        subplot.yaxis.set_minor_locator(MultipleLocator(0.1))
        
        if ii>0:
            plt.tick_params(axis='y', which='both', left='on', labelleft='off')
        
        bin=0.25        
        Mass_arr=np.arange(xlim[0],xlim[1],bin)
        SatFraction=np.zeros(len(Mass_arr),dtype=np.float32)
        HaloSatFraction=np.zeros(len(Mass_arr),dtype=np.float32)
        
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)        
        G0_MR=G_MR[sel]   
        StellarMass=stellar_mass_with_err(G0_MR, Hubble_h, ThisRedshiftList[ii])
        Type=G0_MR['Type']
        
        for ll in range(0,len(Mass_arr)):
            sel_sat=G0_MR[(Type>0) & (StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
            sel_halosat=G0_MR[(Type==1) & (StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
            sel_all=G0_MR[(StellarMass>Mass_arr[ll]-bin/2.) & (StellarMass<Mass_arr[ll]+bin/2.)]
                
            if len(sel_all)>0.:
                SatFraction[ll]=float(len(sel_sat))/float(len(sel_all))
                HaloSatFraction[ll]=float(len(sel_halosat))/float(len(sel_all))
            else:               
                SatFraction[ll]=0.
                HaloSatFraction[ll]=0.
                      
        subplot.plot(Mass_arr, SatFraction, color='red', linestyle='-', linewidth=2) 
        subplot.plot(Mass_arr, HaloSatFraction, color='green', linestyle='-', linewidth=2) 
       
        #labels
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.05, y_percentage=0.55, 
                    color='black', xlog=0, ylog=0, label='z='+char_redshift[:-1], 
                    fontsize=14, fontweight='normal') 
    
        if(ii==0):
            plot_label (subplot, 'label', xlim, ylim, 
                    x_percentage=0.15, y_percentage=0.90, color='black', xlog=0, ylog=0, 
                    label='galaxies', fontsize=13, fontweight='normal') 
            plot_label (subplot, 'line', xlim, ylim,
                    x_percentage=0.04, y_percentage=0.92, color='red', x2_percentage=0.13, 
                    xlog=0, ylog=0, linestyle='-', linewidth=2)
            plot_label (subplot, 'label', xlim, ylim, 
                    x_percentage=0.15, y_percentage=0.8, color='black', xlog=0, ylog=0, 
                    label='haloes', fontsize=13, fontweight='normal') 
            plot_label (subplot, 'line', xlim, ylim,
                    x_percentage=0.04, y_percentage=0.82, color='green', x2_percentage=0.13, 
                    xlog=0, ylog=0, linestyle='-', linewidth=2)
            
    plt.tight_layout()
    plt.savefig('./fig/plots_sat_fraction.pdf')
    pdf.savefig()
    plt.close()
    

#end sat_fraction




def BHmass_in_radio(G_MR, ThisRedshiftList, pdf):
    
    xlim=[8.0,12.]
    ylim=[-5.0,0.0]
    bin=0.25
    
    plot_color=['red','purple']        
    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
    fig = plt.figure(figsize=(5,4))
    subplot=plt.subplot()
    subplot.set_ylim(ylim), subplot.set_xlim(xlim)    
            
    #format axis
    majorFormatter = FormatStrFormatter('%d')
    subplot.xaxis.set_major_locator(MultipleLocator(1))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25))
           
    xlab='$\mathrm{log_{10}}(M_*[h^{-2}M_{\odot}])$'   
    ylab='$\mathrm{log_{10}}(\mathrm{M_{BHHot}/M_{BH})}$'     
    subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)   
            
    
    
    for ii in range (0,len(ThisRedshiftList)):
           
        char_redshift="%0.2f" % ThisRedshiftList[ii]
              
        
        bin=0.25        
        Mass_arr=np.arange(xlim[0],xlim[1],bin)
        #MassInRadio=np.zeros(len(Mass_arr),dtype=np.float32)
              
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)        
        G0_MR=G_MR[sel]   
        G0_MR=G0_MR[G0_MR['StellarMass']>0.]
        StellarMass=stellar_mass_with_err(G0_MR, Hubble_h, ThisRedshiftList[ii])
        FractioninRadio=G0_MR['MassRadio']/G0_MR['StellarMass']
               
        (x_binned, median, mean, pc16, pc84)=median_and_percentiles (bin, xlim[0], xlim[1], StellarMass, FractioninRadio)    
        subplot.plot(x_binned, np.log10(median),color='red', linewidth=2)
        print(x_binned, median)        
                      
        #subplot.plot(Mass_arr, SatFraction, color='red', linestyle='-', linewidth=2) 
        
        #labels
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.05, y_percentage=0.55, 
                    color='black', xlog=0, ylog=0, label='z='+char_redshift[:-1], 
                    fontsize=14, fontweight='normal') 
    
        #if(ii==0):
        #    plot_label (subplot, 'label', xlim, ylim, 
        #            x_percentage=0.15, y_percentage=0.90, color='black', xlog=0, ylog=0, 
        #            label='galaxies', fontsize=13, fontweight='normal') 
        #    plot_label (subplot, 'line', xlim, ylim,
        #            x_percentage=0.04, y_percentage=0.92, color='red', x2_percentage=0.13, 
        #            xlog=0, ylog=0, linestyle='-', linewidth=2)
          
            
    plt.tight_layout()
    plt.savefig('./fig/plots_BH_radio.pdf')
    pdf.savefig()
    plt.close()

#end BHmass_in_radio



def HotGas_fraction(G_MR, ThisRedshiftList, pdf):
    
    xlim=[10.0,15.]
    ylim=[0.0,0.2]    
    bin=[0.25,0.01]
    Nbins=[int((xlim[1]-xlim[0])/bin[0]),int((ylim[1]-ylim[0])/bin[1])]
    plot_color=['red','purple']  
    
    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
    fig = plt.figure(figsize=(5,4))
    subplot=plt.subplot()
    subplot.set_ylim(ylim), subplot.set_xlim(xlim)    
            
    #format axis
    majorFormatter = FormatStrFormatter('%d')
    subplot.xaxis.set_major_locator(MultipleLocator(1))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25))
           
    xlab='$\mathrm{log_{10}}(M_vir[h^{-1}M_{\odot}])$'   
    ylab='$\mathrm{log_{10}}(\mathrm{M_{Hot}/M_{vir})}$'     
    subplot.set_xlabel(xlab, fontsize=16), subplot.set_ylabel(ylab, fontsize=16)   
            
    
    
    for ii in range (0,len(ThisRedshiftList)):
           
        char_redshift="%0.2f" % ThisRedshiftList[ii]
           
        (sel)=select_current_redshift(G_MR, ThisRedshiftList, ii, FullSnapshotList_MR)        
        G0_MR=G_MR[sel] 
        
        Ngals=len(G0_MR)
        NN=10000.       
        sel= np.random.uniform(0.0,1.0,Ngals) < NN/Ngals 
        G00_MR=G0_MR[sel]
        plt.scatter(np.log10(G00_MR['Mvir']*1.e10), G00_MR['HotGas']/G00_MR['Mvir'], s=5, color='black')   
    
        G0_MR=G0_MR[(G0_MR['Mvir']>0.) & (G0_MR['Type']==0)]
        #G0_MR=G0_MR[(G0_MR['Mvir']>0.)]       
        Mvir=np.log10(G0_MR['Mvir']*1.e10)
        HotFraction=G0_MR['HotGas']/G0_MR['Mvir']
                  
        Ngals=len(G0_MR)    
        H, xedges, yedges = np.histogram2d(Mvir, HotFraction, bins=Nbins)            
        extent = [xedges[0], xedges[-1],yedges[0], yedges[-1]]       
        plt.subplots_adjust(bottom=0.15, left=0.15)        
        mylevels = np.linspace(1., Nbins[0], Nbins[0])*Ngals/(Nbins[0]**2/3.)        
        H = zoom(H, 20)        
        cont=plt.contourf(H.transpose()[::], origin='lower', cmap='Greys_r', levels=mylevels, extent=extent)        
        plt.colorbar(format='%d')    
        
            
        (x_binned, median, mean, pc16, pc84)=median_and_percentiles (bin[0], xlim[0], xlim[1], Mvir, HotFraction)    
        subplot.plot(x_binned, median,color='red', linewidth=2)
        print(x_binned, median)        
                      
        #subplot.plot(Mass_arr, SatFraction, color='red', linestyle='-', linewidth=2) 
        
        #labels
        plot_label (subplot, 'label', xlim, ylim, x_percentage=0.05, y_percentage=0.55, 
                    color='black', xlog=0, ylog=0, label='z='+char_redshift[:-1], 
                    fontsize=14, fontweight='normal') 
    
        #if(ii==0):
        #    plot_label (subplot, 'label', xlim, ylim, 
        #            x_percentage=0.15, y_percentage=0.90, color='black', xlog=0, ylog=0, 
        #            label='galaxies', fontsize=13, fontweight='normal') 
        #    plot_label (subplot, 'line', xlim, ylim,
        #            x_percentage=0.04, y_percentage=0.92, color='red', x2_percentage=0.13, 
        #            xlog=0, ylog=0, linestyle='-', linewidth=2)
          
            
    plt.tight_layout()
    plt.savefig('./fig/plots_HotGas_fraction.pdf')
    pdf.savefig()
    plt.close()

#end HotGas_fraction


def misc_plots(G_MR, FullSnapshotList, pdf):
       
    fig = plt.figure(figsize=(10,10))
        
    sel= np.logical_and(np.logical_and(np.logical_and(G_MR['SnapNum']==FullSnapshotList[0], G_MR['StellarMass']>0.),
          G_MR['BlackHoleMass']>0.), G_MR['DiskMass']>0.) 
    G0_MR=G_MR[sel]   
    Ngals=len(G0_MR['StellarMass']) 
  
    d = {'StellarMass' : pd.Series(np.log10((G0_MR['StellarMass'])*1.e10),index=np.zeros(Ngals,dtype=np.int32)),
         'BulgeMass' : pd.Series(np.log10((G0_MR['BulgeMass'])*1.e10),index=np.zeros(Ngals,dtype=np.int32)),
         'DiskMass' : pd.Series(np.log10((G0_MR['DiskMass'])*1.e10),index=np.zeros(Ngals,dtype=np.int32)),
         'BlackHoleMass' : pd.Series(np.log10((G0_MR['BlackHoleMass'])*1.e10),index=np.zeros(Ngals,dtype=np.int32)),
         'SSFR' : pd.Series(np.log10(G0_MR['Sfr']/G0_MR['StellarMass']),index=np.zeros(Ngals,dtype=np.int32)),
         'Type' : pd.Series(G0_MR['Type'],index=np.zeros(Ngals,dtype=np.int32)),
         'Activity':pd.Series(np.zeros(Ngals,dtype=np.str_),index=np.zeros(Ngals,dtype=np.int32))}       
       
    df = pd.DataFrame(d)    
    #df['SSFR'] = (df.weight/2000).astype(int) 
    
    NN=10000.       
    sel= np.random.uniform(0.0,1.0,Ngals) < NN/Ngals 
    df=df[sel]
    
    df.Activity[:]='Active'
    sel=df.SSFR<-10.5
    df.Activity[sel]='Passive'
    
    #df.Passive.map({1: 'Passive', 0: 'Active'})
       
    #histogram TODO
    #g = sns.FacetGrid(df, col="Activity", size=6, aspect=1)
    #g.map(sns.distplot, "StellarMass")    
          
    #scatter plot
    ##g = sns.FacetGrid(df, col='Activity', size=6, aspect=1)  
    ##g.map(plt.scatter, 'StellarMass', 'BlackHoleMass')     
   
    #linear regretion
    ##g = sns.FacetGrid(df, col='Activity', size=6, aspect=1)  
    ##g.map(sns.regplot, 'StellarMass', 'BlackHoleMass')      
        
    #contour plot    
    #g = sns.FacetGrid(df, col="Activity", row='Type', size=6, aspect=1)
    #g.map(sns.kdeplot, 'StellarMass', 'BlackHoleMass') 
    #plt.xlim(7.0, 12.0), plt.ylim(4.0, 12.0) 
    
    ##g = sns.FacetGrid(df, col="Activity", size=6, aspect=1)
    ##g.map(sns.kdeplot, 'StellarMass', 'BlackHoleMass') 
    ##plt.xlim(7.0, 12.0), plt.ylim(4.0, 10.0)  
    
    #multiple variables
    ##this one just produces scater plots (pairplot) with the option of a hist in the diagonal
    ##g = sns.pairplot(df[["StellarMass", "BlackHoleMass", "Activity"]], hue="Activity", diag_kind="hist")  
    ##for ax in g.axes.flat:  
    ##    plt.setp(ax.get_xticklabels(), rotation=45)
    
    #We were able to control three regions (the diagonal, the lower-left triangle, and the 
    #upper-right triangle) separately. Again, you can pipe in any plotting function that 
    #understands the data it's given.    
    ##g = sns.PairGrid(df[["StellarMass", "BlackHoleMass", "Activity"]], hue="Activity")  
    ##g.map_upper(sns.regplot)  
    ##g.map_lower(sns.residplot)  
    ##g.map_diag(plt.hist)  
    ##for ax in g.axes.flat:  
    ##    plt.setp(ax.get_xticklabels(), rotation=45)
    ##g.add_legend()  
    ##g.set(alpha=0.5)  
    
    ax = sns.kdeplot(df.StellarMass, df.BlackHoleMass,
                  cmap="Reds", shade=True, shade_lowest=False)
    ax = sns.kdeplot(df.StellarMass, df.DiskMass,
                  cmap="Blues", shade=True, shade_lowest=False)
    
    
    #joint plots
    sns.jointplot("StellarMass", "BlackHoleMass", data=df, kind='kde')  
    
    g = sns.JointGrid(x="StellarMass", y="BlackHoleMass", data=df)  
    g.plot_joint(sns.kdeplot, shade=True, n_levels=20, cut=10., bw=0.2, shade_lowest=False)  
    g.plot_marginals(sns.distplot)  
    
    
    #g = sns.JointGrid(x="StellarMass", y="BlackHoleMass", data=df)  
    #g.plot_joint(sns.regplot, order=2)  
    #g.plot_marginals(sns.distplot)  
    
    #pdf.savefig()
    #plt.close()
 
#end misc_plots
     
    
    
def test_resolution(G_MR, Volume_MR, G_MRII, Volume_MRII, ThisRedshiftList, pdf):
   
   
    plt.rcParams.update({'xtick.major.width': 1.0, 'ytick.major.width': 1.0, 
                             'xtick.minor.width': 1.0, 'ytick.minor.width': 1.0})
    fig = plt.figure(figsize=(7,5))
    grid = gridspec.GridSpec(2, 2)
    grid.update(wspace=0.0, hspace=0.0)
       
        
    #Cold Gas    
    xlim=[7.0,11.5]
    ylim=[-6.0,0.0]
    bin=0.25
    subplot=plt.subplot(grid[0])
    subplot.set_ylim(ylim), subplot.set_xlim(xlim)
    
    #format axis
    majorFormatter = FormatStrFormatter('%d')
    subplot.xaxis.set_major_locator(MultipleLocator(1))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25))
    plt.tick_params(axis='x', which='both', top='on', labeltop='on', bottom='off', labelbottom='off')
       
    #MR  
    (sel)=select_current_redshift(G_MR, ThisRedshiftList, 0, FullSnapshotList_MR)         
    G0_MR=G_MR[sel]   
    G0_MR=G0_MR[(G0_MR['ColdGas']>0.) & (G0_MR['Type']==0)]
    mass=(np.log10(G0_MR['ColdGas']*1.e10*Hubble_h))

    bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
    hist=np.histogram(mass, bins=bin_arr, range=(xlim[0],xlim[1]))   
    subplot.plot(hist[1][0:len(hist[1][:])-1]+bin/2.,np.log10(hist[0][:]/(Volume_MR*bin)),
                 color='red', linewidth=2, linestyle='--')

    #MRII
    (sel)=select_current_redshift(G_MRII, ThisRedshiftList, 0, FullSnapshotList_MRII)         
    G0_MRII=G_MRII[sel]   
    G0_MRII=G0_MRII[(G0_MRII['ColdGas']>0.) & (G0_MRII['Type']==0)]
    mass=(np.log10(G0_MRII['ColdGas']*1.e10*Hubble_h))

    bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
    hist=np.histogram(mass, bins=bin_arr, range=(xlim[0],xlim[1]))   
    subplot.plot(hist[1][0:len(hist[1][:])-1]+bin/2.,np.log10(hist[0][:]/(Volume_MRII*bin)),
                 color='red', linewidth=2)
        
    plot_label (subplot, 'label', xlim, ylim, 
                x_percentage=0.15, y_percentage=0.20, color='black', xlog=0, ylog=0, 
                label='ColdGas', fontsize=15, fontweight='normal')  
    
    plot_label (subplot, 'label', xlim, ylim, 
                x_percentage=0.15, y_percentage=0.5, color='black', xlog=0, ylog=0, 
                label='MR', fontsize=13, fontweight='normal') 
    plot_label (subplot, 'line', xlim, ylim,
                x_percentage=0.04, y_percentage=0.53, color='red', x2_percentage=0.13, 
                xlog=0, ylog=0, linestyle='--', linewidth=2)
    plot_label (subplot, 'label', xlim, ylim, 
                x_percentage=0.15, y_percentage=0.4, color='black', xlog=0, ylog=0, 
                label='MRII', fontsize=13, fontweight='normal') 
    plot_label (subplot, 'line', xlim, ylim,
                x_percentage=0.04, y_percentage=0.43, color='red', x2_percentage=0.13, 
                xlog=0, ylog=0, linestyle='-', linewidth=2)
        
    #SFR  
    xlim=[-3.5,2.]
    ylim=[-6.0,0.0]
    bin=0.25
    subplot=plt.subplot(grid[1])
    subplot.set_ylim(ylim), subplot.set_xlim(xlim)
    
    #format axis
    majorFormatter = FormatStrFormatter('%d')
    subplot.xaxis.set_major_locator(MultipleLocator(1))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25))      
    plt.tick_params(axis='x', which='both', top='on', labeltop='on', bottom='off', labelbottom='off')   
    plt.tick_params(axis='y', which='both', left='on', labelleft='off')
    
    #MR
    (sel)=select_current_redshift(G_MR, ThisRedshiftList, 0, FullSnapshotList_MR)         
    G0_MR=G_MR[sel]   
    G0_MR=G0_MR[G0_MR['Sfr']>0.]
    mass=(np.log10(G0_MR['Sfr']*Hubble_h))

    bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
    hist=np.histogram(mass, bins=bin_arr, range=(xlim[0],xlim[1]))   
    subplot.plot(hist[1][0:len(hist[1][:])-1]+bin/2.,np.log10(hist[0][:]/(Volume_MR*bin)),
                 color='red', linewidth=2, linestyle='--')

    #MRII
    (sel)=select_current_redshift(G_MRII, ThisRedshiftList, 0, FullSnapshotList_MRII)         
    G0_MRII=G_MRII[sel]   
    G0_MRII=G0_MRII[G0_MRII['Sfr']>0.]
    mass=(np.log10(G0_MRII['Sfr']*Hubble_h))

    bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
    hist=np.histogram(mass, bins=bin_arr, range=(xlim[0],xlim[1]))   
    subplot.plot(hist[1][0:len(hist[1][:])-1]+bin/2.,np.log10(hist[0][:]/(Volume_MRII*bin)),
                 color='red', linewidth=2)
    
    plot_label (subplot, 'label', xlim, ylim, 
                x_percentage=0.15, y_percentage=0.20, color='black', xlog=0, ylog=0, 
                label='SFR', fontsize=15, fontweight='normal') 
    
    
    #Stellar Mass   
    xlim=[7.0,12.5]
    ylim=[-6.0,0.0]
    bin=0.25
    subplot=plt.subplot(grid[2])
    subplot.set_ylim(ylim), subplot.set_xlim(xlim)
    
    #format axis
    majorFormatter = FormatStrFormatter('%d')
    subplot.xaxis.set_major_locator(MultipleLocator(1))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25))
    plt.tick_params(axis='x', which='both', top='off', labeltop='off')  
    
    #MR
    (sel)=select_current_redshift(G_MR, ThisRedshiftList, 0, FullSnapshotList_MR)         
    G0_MR=G_MR[sel]   
    G0_MR=G0_MR[G0_MR['StellarMass']>0.]
    mass=(np.log10(G0_MR['StellarMass']*1.e10*Hubble_h))

    bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
    hist=np.histogram(mass, bins=bin_arr, range=(xlim[0],xlim[1]))   
    subplot.plot(hist[1][0:len(hist[1][:])-1]+bin/2.,np.log10(hist[0][:]/(Volume_MR*bin)),
                 color='red', linewidth=2, linestyle='--')

    #MRII
    (sel)=select_current_redshift(G_MRII, ThisRedshiftList, 0, FullSnapshotList_MRII)         
    G0_MRII=G_MRII[sel]   
    G0_MRII=G0_MRII[G0_MRII['StellarMass']>0.]
    mass=(np.log10(G0_MRII['StellarMass']*1.e10*Hubble_h))

    bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
    hist=np.histogram(mass, bins=bin_arr, range=(xlim[0],xlim[1]))   
    subplot.plot(hist[1][0:len(hist[1][:])-1]+bin/2.,np.log10(hist[0][:]/(Volume_MRII*bin)),
                 color='red', linewidth=2)
    
    plot_label (subplot, 'label', xlim, ylim, 
                x_percentage=0.15, y_percentage=0.20, color='black', xlog=0, ylog=0, 
                label='StellarMass', fontsize=15, fontweight='normal') 
           
    #BH Mass    
    xlim=[3.5,10.]
    ylim=[-6.0,0.0]
    bin=0.25
    subplot=plt.subplot(grid[3])
    subplot.set_ylim(ylim), subplot.set_xlim(xlim)
    
    #format axis
    majorFormatter = FormatStrFormatter('%d')
    subplot.xaxis.set_major_locator(MultipleLocator(1))    
    subplot.xaxis.set_minor_locator(MultipleLocator(0.25))
    plt.tick_params(axis='x', which='both', top='off', labeltop='off') 
    plt.tick_params(axis='y', which='both', left='on', labelleft='off')
          
    #MR  
    (sel)=select_current_redshift(G_MR, ThisRedshiftList, 0, FullSnapshotList_MR)         
    G0_MR=G_MR[sel]   
    G0_MR=G0_MR[(G0_MR['BlackHoleMass']>0.) & (G0_MR['Type']==0)]
    mass=(np.log10(G0_MR['BlackHoleMass']*1.e10*Hubble_h))

    bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
    hist=np.histogram(mass, bins=bin_arr, range=(xlim[0],xlim[1]))   
    subplot.plot(hist[1][0:len(hist[1][:])-1]+bin/2.,np.log10(hist[0][:]/(Volume_MR*bin)),
                 color='red', linewidth=2, linestyle='--')

    #MRII
    (sel)=select_current_redshift(G_MRII, ThisRedshiftList, 0, FullSnapshotList_MRII)         
    G0_MRII=G_MRII[sel]   
    G0_MRII=G0_MRII[(G0_MRII['BlackHoleMass']>0.) & (G0_MRII['Type']==0)]
    mass=(np.log10(G0_MRII['BlackHoleMass']*1.e10*Hubble_h))

    bin_arr=np.arange(xlim[0],xlim[1]+bin,bin)
    hist=np.histogram(mass, bins=bin_arr, range=(xlim[0],xlim[1]))   
    subplot.plot(hist[1][0:len(hist[1][:])-1]+bin/2.,np.log10(hist[0][:]/(Volume_MRII*bin)),
                 color='red', linewidth=2)
        
    plot_label (subplot, 'label', xlim, ylim, 
                x_percentage=0.15, y_percentage=0.20, color='black', xlog=0, ylog=0, 
                label='BlackHoleMass', fontsize=15, fontweight='normal') 
    
    
    
    plt.tight_layout()
    plt.savefig('./fig/plots_test_resolution_rings.pdf')
    pdf.savefig()
    plt.close()
    
#end test_resolution_rings
    
    
def simple_tree_map(G_MR, pdf):
    
    fig = plt.figure(figsize=(15,15))
    subplot=plt.subplot()
    subplot.set_xlim([0.0,300.]), subplot.set_ylim([-5.0, 150.]) 
    subplot.set_xlabel('x', fontsize=16), subplot.set_ylabel('y', fontsize=16)
               
    G0_MR=G_MR[(G_MR['SnapNum']==255) & (G_MR['StellarMass']>1.0) & (G_MR['Type']==0)]      
    G0_MR=G_MR[(G_MR['GalID']>=G0_MR['GalID']) & (G_MR['GalID']<=G0_MR['LastProgGal'])]    
      
    print('Ngals in tree=',len(G0_MR))
        
    for jj in range (150,255):
        G_aux=G0_MR[G0_MR['SnapNum']==jj]
        G_desc=G0_MR[G0_MR['SnapNum']==jj+1]
     
        for ii in range (0,len(G_aux)):           
            if(G_aux['Type'][ii]==0):
                plot_color='blue'
            else:
                if(G_aux['Type'][ii]==1):
                    plot_color='green'
                else:
                    plot_color='red'
            mass=G_aux['StellarMass'][ii]*100.
            if(mass==0.):
                mass=1.                
            subplot.scatter(2+ii*10.0,255-jj,s=mass, color=plot_color)
            for kk in range (0,len(G_desc)):
                if(G_desc['GalID'][kk]==G_aux['DescendantGal'][ii]):
                    subplot.plot([2+ii*10.0,2+kk*10.0],[255-jj,255-jj-1],color='black')
            
#simple_tree_map


  
def full_tree_map(G_MR, pdf, object_type):       
    
    print('Doing tree for',object_type)
    
    #G0_MR=G_MR[(G_MR['SnapNum']==255) & (G_MR['StellarMass']>1.0) & (G_MR['Type']==0)]
    #G0_MR=G_MR[(G_MR['SnapNum']==255) & (G_MR['StellarMass']>.35) & (G_MR['Type']==0)]
    #G0_MR=G_MR[(G_MR['SnapNum']==255) & (G_MR['StellarMass']<0.03) & (G_MR['StellarMass']>0.01) & (G_MR['Type']==0)] 
    #print(len(G0_MR))
    G0_MR=G_MR[(G_MR['GalID']==4000000000000)]
    G0_MR=G_MR[(G_MR['GalID']>=G0_MR['GalID']) & (G_MR['GalID']<=G0_MR['LastProgGal'])]    
        
    print('Ngals in tree=',len(G0_MR['GalID']))
    
    done=np.zeros(len(G0_MR),dtype=np.float32)
    pos=np.zeros(len(G0_MR),dtype=np.float32)
    plot_snap=np.zeros(len(G0_MR),dtype=np.float32)
    marker_size=np.zeros(len(G0_MR),dtype=np.float32)
    plot_type=np.zeros(len(G0_MR),dtype=np.float32)
    
    gal=G0_MR[G0_MR['SnapNum']==255]
    prog=gal['FirstProgGal']
 
    print('ID of final gal=',gal['GalID'])
    ii=0
  
    #for ll in range (0,100):
    while(prog>0):     
        sel=G0_MR['GalID']==prog
        G_sel=G0_MR[sel]
        #if gal not done and there is a progenitor, plot galaxy and move to progenitor
        if((done[sel]==0) & (G_sel['FirstProgGal']>0)):           
            plot_type[sel]=G_sel['Type']            
            pos[sel]=ii
            plot_snap[sel]=255-G_sel['SnapNum'] 
            if(object_type=='galaxies'):
                marker_size[sel]=G_sel['StellarMass']      
            else:
                marker_size[sel]=G_sel['Mvir']      
            done[sel]=1
            prog=G_sel['FirstProgGal']
        else:
            #if galaxy not done but there is no progenitor, plot galaxy and move
            #either to the next prog (if it exists) or descendant (if nextprog=-1)
            if(done[sel]==0):
                plot_type[sel]=G_sel['Type']                
                pos[sel]=ii
                plot_snap[sel]=255-G_sel['SnapNum'] 
                if(object_type=='galaxies'):
                    marker_size[sel]=G_sel['StellarMass']      
                else:
                    marker_size[sel]=G_sel['Mvir']                  
                done[sel]=1
                
                if(G_sel['NextProgGal']>0):
                    prog=G_sel['NextProgGal']                     
                    ii+=1                     
                else:
                    prog=G_sel['DescendantGal']
            #if galaxy done move either to the next prog (if it exists) 
            #or descendant (if nextprog=-1)
            else:                                       
                if(G_sel['NextProgGal']>0):
                    prog=G_sel['NextProgGal']                   
                    ii+=1                    
                else:
                    prog=G_sel['DescendantGal']
        
    fig = plt.figure(figsize=(15,15))
    subplot=plt.subplot()
    subplot.set_xlim([-20.0,20.+np.amax(pos)*5.+50.]), subplot.set_ylim([-5.0, 255.]) 
    #subplot.set_xlim([-20.0,3700.]), subplot.set_ylim([40.0, 80.]) 
    subplot.set_xlabel('', fontsize=16), subplot.set_ylabel('Snap', fontsize=16)         
    subplot.xaxis.set_ticklabels([])
    
    if(object_type=='galaxies'):
        marker_scale=100.     
    else:
        marker_scale=5.   
                
    sel=((plot_type==0) & (marker_size>0.))    
    subplot.scatter(20+pos[sel]*5.0,plot_snap[sel],s=marker_size[sel]*marker_scale, color='blue')
    sel=((plot_type==1) & (marker_size>0.))   
    subplot.scatter(20+pos[sel]*5.0,plot_snap[sel],s=marker_size[sel]*marker_scale, color='green')
    sel=((plot_type==2) & (marker_size>0.))   
    subplot.scatter(20+pos[sel]*5.0,plot_snap[sel],s=marker_size[sel]*marker_scale, color='red')    
    sel=(marker_size==0.)  
    subplot.scatter(20+pos[sel]*5.0,plot_snap[sel],s=marker_size[sel]+marker_scale/100., color='black')
    
    print('done tree walk')    
                
    for jjj in range (0,len(G0_MR)):
        prog=G0_MR['FirstProgGal'][jjj] 
        sel=G0_MR['GalID']==prog
        G_sel=G0_MR[sel]
        if(prog>0):          
            subplot.plot([20+pos[jjj]*5.0,20+pos[sel]*5.0],
                         [255-G0_MR['SnapNum'][jjj],255-G_sel['SnapNum']],color='black')
            prog=G_sel['NextProgGal']
            sel=G0_MR['GalID']==prog
            G_sel=G0_MR[sel]
            while(prog>0):
                subplot.plot([20+pos[jjj]*5.0,20+pos[sel]*5.0],
                             [255-G0_MR['SnapNum'][jjj],255-G_sel['SnapNum']],color='black')
                prog=G_sel['NextProgGal']
                sel=G0_MR['GalID']==prog
                G_sel=G0_MR[sel]
               
    print('done second tree walk')      
             
    plt.tight_layout()
    plt.savefig('./fig/plots_full_tree_map.pdf')
    pdf.savefig()
    plt.close()

#full_tree_map   