#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 23:23:54 2022

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



#%%      Vary Tau:      %%#
#Results for Overview Table
tau_results_string = []

#Parameters to be varied:
tau_params = ['tau_baseline', 'tau_high']

#Initialize strings for tables
tau_string = '\\underline{Fixed Per Worker Cost, $\\tau$:} \n \t'
payroll_tax_string = '\\underline{Payroll Tax Rate, $t$:} \n \t'
delta_w_C_string = '\\ \\ Change in College Wage, $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ Change in Non-college Wage, $\Delta(w_N)$ \n \t'
pct_chg_cwp_string = '\\ \\ Pct. Change in College Wage Premium, $\\%\\Delta(w_C/w_N - 1)$ \n \t'
delta_P_c_string = '\\ \\ Change in College Employment Rate, $\Delta(P_C)$ \n \t'
delta_P_n_string = '\\ \\ Change in Non-college Employment Rate, $\Delta(P_N)$ \n \t'
delta_employment_string = 'Change in Total Employment, $\Delta(L)$ \n \t'
delta_employment_C_string = '\\ \\ \\small Change in College Employment, $\Delta(L_C)$ \n \t'
delta_employment_N_string = '\\ \\ \\small Change in Non-college Employment, $\Delta(L_N)$ \n \t'
delta_cwb_string = 'Change in College Share of Wage Bill, $\Delta(\\frac{w_C L_C}{w_N L_N+w_C L_C})$: \n \t'


#Loop through
i = 0
for tau_param in tau_params:
    i = i+1
    
    #Define Model
    model = calibration_model_bySex(alpha_diff=0,
                rho=rho_baseline,
                tau=df_observed.loc[year, tau_param],
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
    
    #Add values to strings for Eq Comparison Tables
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
    
    #Long calculations
    chg_employment_C = ((model.employment2_c_m+model.employment2_c_f)-(model.employment1_c_m+model.employment1_c_f))
    chg_employment_N = ((model.employment2_n_m+model.employment2_n_f)-(model.employment1_n_m+model.employment1_n_f))
    chg_employment = chg_employment_C+chg_employment_N
    chg_cwb = 100*((((model.L2_c_m+model.L2_c_f)*model.avg_w2_c)/\
                    ((model.L2_c_m+model.L2_c_f)*model.avg_w2_c \
                     + (model.L2_n_m+model.L2_n_f)*model.avg_w2_n))\
                   -(((model.L1_c_m+model.L1_c_f)*model.avg_w1_c)/\
                     ((model.L1_c_m+model.L1_c_f)*model.avg_w1_c \
                      + (model.L1_n_m+model.L1_n_f)*model.avg_w1_n)))
    
    #Strings
    tau_string = tau_string + ampersand + f' \${model.tau:,.0f} '
    payroll_tax_string = payroll_tax_string + ampersand + f' {100*((model.t)):,.2f}\\% '
    delta_w_C_string = delta_w_C_string + ampersand + f' \${model.avg_w2_c-model.avg_w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' \${model.avg_w2_n-model.avg_w1_n:,.0f} '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
        f' {100*((model.avg_w2_c/model.avg_w2_n)-(model.avg_w1_c/model.avg_w1_n))/(model.avg_w1_c/model.avg_w1_n -1):,.2f}\\% '
    
    delta_P_n_string = delta_P_n_string + ampersand + f' {100*(model.avg_P2_n-model.avg_P1_n):,.2f} pp '
    delta_P_c_string = delta_P_c_string + ampersand + f' {100*(model.avg_P2_c-model.avg_P1_c):,.2f} pp '
    delta_employment_string = delta_employment_string + ampersand + f' {chg_employment:,.0f} '
    delta_employment_C_string = delta_employment_C_string + ampersand + f' {chg_employment_C:,.0f} '
    delta_employment_N_string = delta_employment_N_string + ampersand + f' {chg_employment_N:,.0f} '
    
    delta_cwb_string = delta_cwb_string + ampersand + f' {chg_cwb:,.2f} pp'



header = ['\\begin{tabular}{lcccc}', '\n',
          '\\FL', '\n',
          '\t &	 \multicolumn{1}{p{2.7cm}}{\small \centering \\textbf{(1)} \\\\ {\\bf Baseline}}','\n', 
          '\t &&	 \multicolumn{1}{p{2.7cm}}{\small \centering \\textbf{(2)} \\\\Total Coverage \\\\ FTFY Workers}','\\\\','\n', 
          '\cmidrule{1-4}', '\n']

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

closer = ['\\bottomrule','\n', '\end{tabular}']

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder)
file = open("EqComparison_AcrossTau_bySex_agg.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()



