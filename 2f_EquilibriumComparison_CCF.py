#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 21:39:02 2022
@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np

### Set working directory
from _set_directory import code_folder
from _set_directory import data_folder
from _set_directory import output_folder

### Import calibration class
from _fmzz_calibration_model_CCF import fmzz_calibration_model_CCF


#%%      Baseline Specifications      %%#
from _baseline_specifications import alpha_diff_baseline
from _baseline_specifications import year_baseline as year
from _baseline_specifications import past_year_baseline
from _baseline_specifications import tau_baseline
from _baseline_specifications import rho_baseline
from _baseline_specifications import elasticities_baseline


#%%      Importing Data:      %%#
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data_CCF.csv', index_col=0)


#%%      Model Calculations:      %%#
#Initialize strings for tables
tau_string = '\\underline{Change in Cost, $\\tau$:} \n \t'
delta_w_C_string = '\\ \\ Change in College Wage, $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ Change in Non-college Wage, $\Delta(w_N)$ \n \t'
pct_chg_cwp_string = '\\ \\ Pct. Change in College Wage Premium, \n \t'
delta_P_c_string = '\\ \\ Change in College Employment Rate, $\Delta(P_C)$ \n \t'
delta_P_n_string = '\\ \\ Change in Non-college Employment Rate, $\Delta(P_N)$ \n \t'
delta_employment_string = 'Change in Total Employment, $\Delta(L)$ \n \t'
delta_employment_C_string = '\\ \\ \\small Change in College Employment, $\Delta(L_C)$ \n \t'
delta_employment_N_string = '\\ \\ \\small Change in Non-college Employment, $\Delta(L_N)$ \n \t'
delta_cwb_string = 'Change in College Share of Wage Bill, \n \t'
    
#Parameters to be varied:
CCFs = ['NoGrowth', 'Canada']
alpha_params = [0, 0.75, 1, 1.25]

#Loop through CCFs
i = 0
for cost_CCF in CCFs:
    tau_param_CCF='tau_CCF_'+cost_CCF

    #Loop through alpha parameters
    for alpha in alpha_params:
        alpha_c, alpha_n = alpha, alpha
        i = i+1
        #Define Model
        model = fmzz_calibration_model_CCF(alpha_c, alpha_n,
                        rho=rho_baseline,
                        tau=df_observed.loc[year, tau_baseline],
                        tau_CCF=df_observed.loc[year, tau_param_CCF],
                        elasticities=elasticities_baseline,
                        w_c=df_observed.loc[year, 'wage1_c'], 
                        w_n=df_observed.loc[year, 'wage1_n'],
                        P_c=df_observed.loc[year, 'P1_c'], 
                        P_n=df_observed.loc[year, 'P1_n'],
                        share_workers_c=df_observed.loc[year, 'share_workers1_c'],
                        share_pop_c=df_observed.loc[year, 'share_pop_c'],
                        pop_count=df_observed.loc[year, 'pop_count'])
        
        #Calibrate Model
        model.calibrate()
            
        #Add values to strings for Eq Comparison Tables
        if i ==1: ampersand = '&'
        if i > 1: ampersand = ' &&'
        
        tau_string = tau_string + ampersand + f' \${model.tau_CCF-model.tau:,.0f} '
        delta_w_C_string = delta_w_C_string + ampersand + f' \${model.w_c_CCF-model.w_c:,.0f} '
        delta_w_N_string = delta_w_N_string + ampersand + f' \${model.w_n_CCF-model.w_n:,.0f} '
        pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
            f' {100*((model.w_c_CCF/model.w_n_CCF)-(model.w_c/model.w_n))/(model.w_c/model.w_n -1):,.2f}\\% '
        
        delta_P_n_string = delta_P_n_string + ampersand + f' {100*(model.P_n_CCF-model.P_n):,.2f} pp '
        delta_P_c_string = delta_P_c_string + ampersand + f' {100*(model.P_c_CCF-model.P_c):,.2f} pp '
        delta_employment_string = delta_employment_string + ampersand + \
            f' {(model.employment_c_CCF+model.employment_n_CCF)-(model.employment_c+model.employment_n):,.0f} '
        delta_employment_C_string = delta_employment_C_string + ampersand + \
            f' {(model.employment_c_CCF)-(model.employment_c):,.0f} '
        delta_employment_N_string = delta_employment_N_string + ampersand + \
            f' {(model.employment_n_CCF)-(model.employment_n):,.0f} '
        
        delta_cwb_string = delta_cwb_string + ampersand + \
            f' {100*(((model.L_c_CCF*model.w_c_CCF)/(model.L_c_CCF*model.w_c_CCF + model.L_n_CCF*model.w_n_CCF))-((model.L_c*model.w_c)/(model.L_c*model.w_c + model.L_n*model.w_n))):,.2f} pp'

   
#%%      Output Latex Tables:      %%#
header = ['\\begin{tabular}{lcccccccccccccccc}', '\n',
          '\\FL', '\n',
          '\t &	\multicolumn{7}{c}{No Growth Counterfactual}','\n', 
          '\t &&	 \multicolumn{7}{c}{Canada Counterfactual}','\n', 
          '\\\\',  '\cmidrule{2-8}', '\cmidrule{10-16}', '\n', 
          '\t &	 $\\alpha=0$','\n', 
          '\t &&	 $\\alpha=0.75$','\n', 
          '\t &&	 $\\alpha=1$','\n',
          '\t &&	 $\\alpha=1.25$','\n', 
          '\t &&	 $\\alpha=0$','\n', 
          '\t &&	 $\\alpha=0.75$','\n', 
          '\t &&	 $\\alpha=1$','\n', 
          '\t &&	 $\\alpha=1.25$', '\\\\','\n', 
          '\cmidrule{1-16}', '\n']

table_values=[tau_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wages:}', ' \\\\\n',
                delta_w_C_string, ' \\\\\n',
                delta_w_N_string, ' \\\\\n',
                pct_chg_cwp_string, ' \\\\\n',
                '\\ \\ $\\%\\Delta(w_C/w_N - 1)$', ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment Rate:}', ' \\\\\n',
                delta_P_c_string, ' \\\\\n',
                delta_P_n_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wage Bill:}', ' \\\\\n',
                delta_cwb_string,' \\\\\n',
                '\\ \\ $\Delta(\\frac{w_C L_C}{w_N L_N+w_C L_C})$', ' \\\\\n']

closer = ['\\bottomrule','\n', '\end{tabular}']

## Adjust dollar signs for negative values in the table
table_values = [x.replace('\\$-', '-\\$') for x in table_values]

## Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder)
file = open(f"EquilibriumComparison_CCF.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()
