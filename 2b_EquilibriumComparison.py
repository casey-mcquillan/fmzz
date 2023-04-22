#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 14:39:40 2022
@author: caseymcquillan
"""
#%%     Preamble        #%%  
### Import Packages
import os
import pandas as pd

### Set working directory
from _set_directory import code_folder
from _set_directory import data_folder
from _set_directory import output_folder

### Import calibration model
os.chdir(code_folder)
from _fmzz_calibration_model import fmzz_calibration_model 


#%%      Baseline Specifications      %%#
from _baseline_specifications import alpha_diff_baseline
from _baseline_specifications import year_baseline as year
from _baseline_specifications import rho_baseline
from _baseline_specifications import elasticities_baseline

#Parameter(s) to be varied
from _varying_parameters import tau_params, tau2specification_Dict


#%%      Importing Data      %%#
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)


#%%      Construct Results by Varying Tau      %%#

#Initialize strings for tables
tau_string = '\\underline{Fixed Per Worker Cost, $\\tau$:} \n \t'
payroll_tax_string = '\\underline{Payroll Tax Rate, $t$:} \n \t'
delta_w_C_string = '\\ \\ Change in College Wage, $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ Change in Non-college Wage, $\Delta(w_N)$ \n \t'
pct_chg_cwp_string = '\\ \\ Pct. Change in College Wage Premium \n \t'
delta_P_c_string = '\\ \\ Change in College Employment Rate, $\Delta(P_C)$ \n \t'
delta_P_n_string = '\\ \\ Change in Non-college Employment Rate, $\Delta(P_N)$ \n \t'
delta_employment_string = 'Change in Total Employment, $\Delta(L)$ \n \t'
delta_employment_C_string = '\\ \\ \\small Change in College Employment, $\Delta(L_C)$ \n \t'
delta_employment_N_string = '\\ \\ \\small Change in Non-college Employment, $\Delta(L_N)$ \n \t'
delta_cwb_string = 'Change in College Share of Wage Bill, $\Delta(\\frac{w_C L_C}{w_N L_N+w_C L_C})$: \n \t'

#Loop through tau_params
i = 0
for tau_param in tau_params:
    i = i+1
    label = tau2specification_Dict[tau_param]
    
    #Define Model
    model = fmzz_calibration_model(alpha_diff=alpha_diff_baseline,
                        rho=rho_baseline,
                        tau=df_observed.loc[year, tau_param],
                        elasticities=elasticities_baseline,
                        w1_c=df_observed.loc[year, 'wage1_c'], 
                        w1_n=df_observed.loc[year, 'wage1_n'],
                        P1_c=df_observed.loc[year, 'P1_c'], 
                        P1_n=df_observed.loc[year, 'P1_n'],
                        share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                        share_pop_c=df_observed.loc[year, 'share_pop_c'],
                        pop_count=df_observed.loc[year, 'pop_count'])
    
    #Calibrate Model
    model.calibrate()
            
    #Save Results
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
    
    tau_string = tau_string + ampersand + f' \${model.tau:,.0f} '
    payroll_tax_string = payroll_tax_string + ampersand + f' {100*((model.t)):,.2f}\\% '
    delta_w_C_string = delta_w_C_string + ampersand + f' \${model.w2_c-model.w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' \${model.w2_n-model.w1_n:,.0f} '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
        f' {100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1):,.2f}\\% '
    
    delta_P_n_string = delta_P_n_string + ampersand + f' {100*(model.P2_n-model.P1_n):,.2f} pp '
    delta_P_c_string = delta_P_c_string + ampersand + f' {100*(model.P2_c-model.P1_c):,.2f} pp '
    delta_employment_string = delta_employment_string + ampersand + \
        f' {(model.employment2_c+model.employment2_n)-(model.employment1_c+model.employment1_n):,.0f} '
    delta_employment_C_string = delta_employment_C_string + ampersand + \
        f' {(model.employment2_c)-(model.employment1_c):,.0f} '
    delta_employment_N_string = delta_employment_N_string + ampersand + \
        f' {(model.employment2_n)-(model.employment1_n):,.0f} '

    delta_cwb_string = delta_cwb_string + ampersand + \
        f' {100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))-((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))):,.2f} pp'


#%%      Compile and Export LaTeX file:      %%#
## LaTeX code for header
header = ['\\begin{tabular}{lcccc}', '\n',
          '\\FL', '\n',
          '\t &	 \multicolumn{1}{p{2.7cm}}{\small \centering \\textbf{(1)} \\\\ Baseline}','\n', 
          '\t &&	 \multicolumn{1}{p{2.7cm}}{\small \centering \\textbf{(2)} \\\\ Full Coverage}','\\\\','\n', 
          '\cmidrule{1-4}', '\n']

## LaTeX code for table results
table_values=[tau_string, ' \\\\\n',
                '\\\\\n',
                payroll_tax_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wages:}', ' \\\\\n',
                delta_w_C_string, ' \\\\\n',
                delta_w_N_string, ' \\\\\n',
                pct_chg_cwp_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment:}', ' \\\\\n',
                delta_P_c_string, ' \\\\\n',
                delta_P_n_string, ' \\\\\n',
                delta_employment_string, ' \\\\\n',
                delta_employment_C_string, ' \\\\\n',
                delta_employment_N_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wage Bill:}', ' \\\\\n',
                delta_cwb_string,' \\\\\n']

## LaTeX code for closer
closer = ['\\bottomrule','\n', '\end{tabular}']

## Adjust dollar signs for negative values in the table
table_values = [x.replace('\\$-', '-\\$') for x in table_values]

## Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder)
file = open("EquilibriumComparison.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()


#%% Return to code directory #%%
os.chdir(code_folder)