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

### Set working directory and folders
main_folder = "/Users/caseymcquillan/Desktop/Research/FZZ"
code_folder = main_folder+"/code"
data_folder = main_folder+"/data"
output_folder = main_folder+"/output/Tables/Analysis by Sex"
os.chdir(code_folder)

### Import calibration class
os.chdir(code_folder)
from fzz_calibration_bySex import calibration_model_bySex


#%%      Establishing Baseline:      %%#

# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data_bySex.csv', index_col=0)

# Parameter assumptions:
year = 2019
tau_baseline = 'tau_baseline'
rho_baseline = 0.3827


#%%      Results by Sex:      %%#

#Initialize strings for tables
tau_string = '\\underline{Fixed Per Worker Cost, $\\tau$:} \n \t'
payroll_tax_string = '\\underline{Payroll Tax Rate, $t$:} \n \t'
delta_w_C_string = '\\ \\ Change in College Wage, $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ Change in Non-college Wage, $\Delta(w_N)$ \n \t'
delta_P_c_string = '\\ \\ Change in College Employment Rate, $\Delta(P_C)$ \n \t'
delta_P_n_string = '\\ \\ Change in Non-college Employment Rate, $\Delta(P_N)$ \n \t'
    
#Define Model
model = calibration_model_bySex(alpha_diff=0,
            rho=rho_baseline,
            tau=df_observed.loc[year, tau_baseline],
            elasticities='common',
            w1_c_m=df_observed.loc[year, 'wage1_c_m'], 
            w1_n_m=df_observed.loc[year, 'wage1_n_m'],
            w1_c_f=df_observed.loc[year, 'wage1_c_f'], 
            w1_n_f=df_observed.loc[year, 'wage1_n_f'],
            P1_c_m=df_observed.loc[year, 'P1_c_m'], 
            P1_n_m=df_observed.loc[year, 'P1_n_m'],
            P1_c_f=df_observed.loc[year, 'P1_c_f'], 
            P1_n_f=df_observed.loc[year, 'P1_n_f'],
            share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
            share_pop_c=df_observed.loc[year, 'share_pop_c'],
            share_workers1_c_m=df_observed.loc[year, 'share_workers1_c_m'],
            share_pop_c_m=df_observed.loc[year, 'share_pop_c_m'],
            share_workers1_n_m=df_observed.loc[year, 'share_workers1_n_m'],
            share_pop_n_m=df_observed.loc[year, 'share_pop_n_m'],
            pop_count=df_observed.loc[year, 'pop_count'])

#Make sure there are no NANs in model before calibration
# Remove elasticities if specified to be common
check = set(list(vars(model).keys())) - set(['elasticities'])
#And now check
if any(np.isnan([vars(model)[x] for x in check])):
    print("NAN value entered into calibration model for:")
    for var in check:
        if np.isnan(vars(model)[var])==True: print("    "+var)
    print("for year: " + str(year))

#Calibrate Model
model.calibrate()


### Add values to strings for aggregate
#Calculate Changes
chg_w_C = model.avg_w2_c-model.avg_w1_c
chg_w_N = model.avg_w2_n-model.avg_w1_n
chg_P_C=100*(model.avg_P2_c-model.avg_P1_c)
chg_P_N=100*(model.avg_P2_n-model.avg_P1_n)
    
#Add to strings
ampersand = '&'
tau_string = tau_string + ampersand + f' \${model.tau:,.0f} '
payroll_tax_string = payroll_tax_string + ampersand + f' {100*((model.t)):,.2f}\\% '
delta_w_C_string = delta_w_C_string + ampersand + f' \${chg_w_C:,.0f} '
delta_w_N_string = delta_w_N_string + ampersand + f' \${chg_w_N:,.0f} '
delta_P_c_string = delta_P_c_string + ampersand + f' {chg_P_C:,.2f} pp '
delta_P_n_string = delta_P_n_string + ampersand + f' {chg_P_N:,.2f} pp '


### Add Values to strings for each sex
for _sex in ['_m', '_f']:

    #Add values to strings for Eq Comparison Tables
    ampersand = ' &&'
    
    #Calculate Changes
    exec(f'chg_w_C = model.w2_c{_sex}-model.w1_c{_sex}')
    exec(f'chg_w_N = model.w2_n{_sex}-model.w1_n{_sex}')
    exec(f'chg_P_C=100*(model.P2_c{_sex}-model.P1_c{_sex})')
    exec(f'chg_P_N=100*(model.P2_n{_sex}-model.P1_n{_sex})')
        
    #Add to strings
    tau_string = tau_string + ampersand + f' -  '
    payroll_tax_string = payroll_tax_string + ampersand + f' - '
    delta_w_C_string = delta_w_C_string + ampersand + f' \${chg_w_C:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' \${chg_w_N:,.0f} '
    delta_P_c_string = delta_P_c_string + ampersand + f' {chg_P_C:,.2f} pp '
    delta_P_n_string = delta_P_n_string + ampersand + f' {chg_P_N:,.2f} pp '


#Output Table
header = ['\\begin{tabular}{lcccccc}', '\n',
          '\\FL', '\n',
          '\t &	 \multicolumn{1}{p{2.7cm}}{\small \centering Aggregate}','\n',
          '\t &&	 \multicolumn{1}{p{2.7cm}}{\small \centering Male}','\n',
          '\t &&	 \multicolumn{1}{p{2.7cm}}{\small \centering Female}','\\\\','\n', 
          '\cmidrule{1-6}', '\n']

table_values=[tau_string, ' \\\\\n',
                '\\\\\n',
                payroll_tax_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wages:}', ' \\\\\n',
                delta_w_C_string, ' \\\\\n',
                delta_w_N_string, ' \\\\\n',
                # pct_chg_cwp_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment Rate:}', ' \\\\\n',
                delta_P_c_string, ' \\\\\n',
                delta_P_n_string, ' \\\\\n',
                # delta_employment_string, ' \\\\\n',
                # delta_employment_C_string, ' \\\\\n',
                # delta_employment_N_string, ' \\\\\n',
                '\\\\\n']
                # '\\underline{Wage Bill:}', ' \\\\\n',
                # delta_cwb_string,' \\\\\n']

closer = ['\\bottomrule','\n', '\end{tabular}']

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder)
file = open("EqComparison_bySex.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()