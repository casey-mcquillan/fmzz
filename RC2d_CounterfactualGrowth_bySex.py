#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  7 19:14:35 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np

### Set working directory #%%
from _set_directory import code_folder
from _set_directory import data_folder
from _set_directory import appendix_output_folder

### Import calibration class
from _fmzz_calibration_model_bySex import fmzz_calibration_model_bySex


#%%      Baseline Specifications      %%#
from _baseline_specifications import alpha_diff_baseline
from _baseline_specifications import year_baseline as year2
from _baseline_specifications import past_year_baseline as year1
from _baseline_specifications import rho_baseline
from _baseline_specifications import elasticities_baseline

#Parameter(s) to be varied
from _varying_parameters import tau_params, tau2specification_Dict


#%%      Importing Data      %%#
os.chdir(data_folder)
df_observed = pd.read_csv('RC2_observed_data_bySex.csv', index_col=0)


#%%      Calibration while Varying Tau      %%#'
for _sex in ['_m', '_f']:

    #Calculate Observed Change over Time
    chg_w_C_observed = df_observed.loc[year2, 'wage1_c'+_sex]-df_observed.loc[year1, 'wage1_c'+_sex]
    chg_w_N_observed = df_observed.loc[year2, 'wage1_n'+_sex]-df_observed.loc[year1, 'wage1_n'+_sex]
    # chg_cwp_observed = 100*((df_observed.loc[year2, 'wage1_c'+_sex]/df_observed.loc[year2, 'wage1_n'+_sex])\
    #                -(df_observed.loc[year1, 'wage1_c'+_sex]/df_observed.loc[year1, 'wage1_n'+_sex]))
    
    chg_P_C_observed = 100*(df_observed.loc[year2, 'P1_c'+_sex]-df_observed.loc[year1, 'P1_c'+_sex])
    chg_P_N_observed = 100*(df_observed.loc[year2, 'P1_n'+_sex]-df_observed.loc[year1, 'P1_n'+_sex])
    
    chg_employment_C_observed = ((df_observed.loc[year2, 'pop_count']*df_observed.loc[year2,'share_pop_c'+_sex]*df_observed.loc[year2, 'P1_c'+_sex]) - \
                                    (df_observed.loc[year1, 'pop_count']*df_observed.loc[year1,'share_pop_c'+_sex]*df_observed.loc[year1, 'P1_c'+_sex]))\
                                    /1e6
    chg_employment_N_observed = ((df_observed.loc[year2, 'pop_count']*(1-df_observed.loc[year2,'share_pop_c'])*df_observed.loc[year2, 'P1_n'+_sex]) - \
                                    (df_observed.loc[year1, 'pop_count']*(1-df_observed.loc[year1,'share_pop_c'])*df_observed.loc[year1, 'P1_n'+_sex]))\
                                    /1e6
                                    
    ### Initialize strings
    # Growth over Time
    chg_tau_string = '\\ \\ Change in Cost  $(\\tau_{2019}-\\tau_{1977})$ \n \t & - '
    chg_t_string = '\\ \\ Payroll Tax $(t_{2019}-t_{1977})$ \n \t & - '
    chg_w_C_string = '\\ \\ Change in College Wages $w_{C,2019}-w_{C,1977}$ \n \t '+f'& \${chg_w_C_observed:,.0f}'
    chg_w_N_string = '\\ \\ Change in Non-college Wages $w_{N,2019}-w_{N,1977}$ \n \t '+f'& \${chg_w_N_observed:,.0f}'
    chg_P_c_string = '\\ \\ \\small Change in College Employment Rate $P_{C,2019}-P_{C,1977}$ \n \t '+f'& {chg_P_C_observed:,.2f} pp'
    chg_P_n_string = '\\ \\ \\small Change in Non-college Employment Rate $P_{N,2019}-P_{N,1977}$ \n \t '+f'& {chg_P_N_observed:,.2f} pp'
    chg_employment_C_string = f'\\ \\ \\small College \n \t & {chg_employment_C_observed:,.2f}'
    chg_employment_N_string = f'\\ \\ \\small Non-College \n \t & {chg_employment_N_observed:,.2f}'
    
    
    #Loop through different tau parameters
    i = 0
    for tau_param in tau_params:
        i = i+1
        
        #Define Model
        model_year1 = fmzz_calibration_model_bySex(alpha_diff=alpha_diff_baseline,
                        rho=rho_baseline,
                        tau=df_observed.loc[year1, tau_param],
                        elasticities=elasticities_baseline,
                        w1_c_m=df_observed.loc[year1, 'wage1_c_m'], 
                        w1_n_m=df_observed.loc[year1, 'wage1_n_m'],
                        w1_c_f=df_observed.loc[year1, 'wage1_c_f'], 
                        w1_n_f=df_observed.loc[year1, 'wage1_n_f'],
                        P1_c_m=df_observed.loc[year1, 'P1_c_m'], 
                        P1_n_m=df_observed.loc[year1, 'P1_n_m'],
                        P1_c_f=df_observed.loc[year1, 'P1_c_f'], 
                        P1_n_f=df_observed.loc[year1, 'P1_n_f'],
                        share_workers1_c=df_observed.loc[year1, 'share_workers1_c'],
                        share_pop_c=df_observed.loc[year1, 'share_pop_c'],
                        share_workers1_c_m=df_observed.loc[year1, 'share_workers1_c_m'],
                        share_pop_c_m=df_observed.loc[year1, 'share_pop_c_m'],
                        share_workers1_n_m=df_observed.loc[year1, 'share_workers1_n_m'],
                        share_pop_n_m=df_observed.loc[year1, 'share_pop_n_m'],
                        pop_count=df_observed.loc[year1, 'pop_count'])
        
        model_year2 = fmzz_calibration_model_bySex(alpha_diff=alpha_diff_baseline,
                        rho=rho_baseline,
                        tau=df_observed.loc[year2, tau_param],
                        elasticities=elasticities_baseline,
                        w1_c_m=df_observed.loc[year2, 'wage1_c_m'], 
                        w1_n_m=df_observed.loc[year2, 'wage1_n_m'],
                        w1_c_f=df_observed.loc[year2, 'wage1_c_f'], 
                        w1_n_f=df_observed.loc[year2, 'wage1_n_f'],
                        P1_c_m=df_observed.loc[year2, 'P1_c_m'], 
                        P1_n_m=df_observed.loc[year2, 'P1_n_m'],
                        P1_c_f=df_observed.loc[year2, 'P1_c_f'], 
                        P1_n_f=df_observed.loc[year2, 'P1_n_f'],
                        share_workers1_c=df_observed.loc[year2, 'share_workers1_c'],
                        share_pop_c=df_observed.loc[year2, 'share_pop_c'],
                        share_workers1_c_m=df_observed.loc[year2, 'share_workers1_c_m'],
                        share_pop_c_m=df_observed.loc[year2, 'share_pop_c_m'],
                        share_workers1_n_m=df_observed.loc[year2, 'share_workers1_n_m'],
                        share_pop_n_m=df_observed.loc[year2, 'share_pop_n_m'],
                        pop_count=df_observed.loc[year2, 'pop_count'])
                    
        ## Calibrate Models
        model_year1.calibrate()
        model_year2.calibrate()
        
        #Add values to strings for Eq Comparison Table
        if i ==1: ampersand = '&'
        if i > 1: ampersand = ' &&'
    
        #Calculate Change over Time in Payroll Tax counterfactual
        chg_tau = model_year2.tau-model_year1.tau
        chg_t = 100*(model_year2.t-model_year1.t)
        exec(f'chg_w_C = model_year2.w2_c{_sex}-model_year1.w2_c{_sex}')
        exec(f'chg_w_N = model_year2.w2_n{_sex}-model_year1.w2_n{_sex}')
        exec(f'chg_P_C=100*(model_year2.P2_c{_sex}-model_year1.P2_c{_sex})')
        exec(f'chg_P_N=100*(model_year2.P2_n{_sex}-model_year1.P2_n{_sex})')
        exec(f'chg_employment_C = (model_year2.employment2_c{_sex}-model_year1.employment2_c{_sex})/1e6')
        exec(f'chg_employment_N = (model_year2.employment2_n{_sex}-model_year1.employment2_n{_sex})/1e6')
        
        ## Add Values to Strings
        # Change over time
        chg_tau_string = chg_tau_string + f' && \${chg_tau:,.0f} '
        chg_t_string = chg_t_string + f' && {chg_t:,.2f} pp '
        chg_w_C_string = chg_w_C_string + f' && \${chg_w_C:,.0f} '
        chg_w_N_string = chg_w_N_string + f' && \${chg_w_N:,.0f} '
        
        chg_P_c_string = chg_P_c_string + f' && {chg_P_C:,.2f} pp '
        chg_P_n_string = chg_P_n_string + f' && {chg_P_N:,.2f} pp '
        chg_employment_C_string = chg_employment_C_string + f' && {chg_employment_C:,.2f} '
        chg_employment_N_string = chg_employment_N_string + f' && {chg_employment_N:,.2f} '
        
        
    #%%      Creating Tables      %%#'
    
    ## Growth over Time 
    header = ['\\begin{tabular}{lccccc}', '\n',
              '\\FL', '\n',
              '\t & && \multicolumn{3}{c}{Payroll Tax Equilibrium} \\\\', '\n',
              '\cmidrule{4-6} \n',
              '\t &	 \multicolumn{1}{p{2.2cm}}{\centering Head Tax \ Equilibrium}','\n', 
              '\t &&	 \multicolumn{1}{p{2.4cm}}{\centering Baseline}','\n', 
              '\t &&	 \multicolumn{1}{p{2.4cm}}{\centering  Full Coverage}', '\\\\','\n', 
              '\cmidrule{1-6}', '\n']
    
    table_values=['\\underline{Employer-Sponsored Health Insurance:}', ' \\\\\n', 
                  chg_tau_string, ' \\\\\n',
                  chg_t_string, ' \\\\\n',
                  '\\\\\n',
                  '\\underline{Wages:}', ' \\\\\n', 
                  chg_w_C_string, ' \\\\\n',
                  chg_w_N_string, ' \\\\\n',
                  '\\\\\n',
                  '\\underline{Employment Rate:}', ' \\\\\n',
                  chg_P_c_string, ' \\\\\n',
                  chg_P_n_string, ' \\\\\n',
                  '\\\\\n']
    
    closer = ['\\bottomrule','\n', '\end{tabular}']
    
    #Create, write, and close file
    cwd = os.getcwd()
    os.chdir(appendix_output_folder)
    file = open(f"RC2_CounterfactualGrowth{_sex}.tex","w")
    file.writelines(header) 
    file.writelines(table_values)   
    file.writelines(closer)   
    file.close()


#%% Return to code directory #%%
os.chdir(code_folder)