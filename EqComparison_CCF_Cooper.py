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
output_folder_tables = main_folder+"/output/Tables/Cost Counterfactual"
output_folder_graphs = main_folder+"/output/Graphs/Cost Counterfactual"
os.chdir(code_folder)

### Import calibration class
os.chdir(code_folder)
from fzz_calibration_CCF import calibration_model_CCF


#%%      Establishing Baseline:      %%#

# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data_CCF.csv', index_col=0)

# Parameter assumptions:
year = 2019
tau_baseline = 'tau_baseline'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]


#%%      Model Calculations:      %%#

#Initialize strings for tables
tau_string = '\\underline{Change in Cost, $\\tau$:} \n \t'
delta_w_C_string = '\\ \\ Change in College Wage, $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ Change in Non-college Wage, $\Delta(w_N)$ \n \t'
pct_chg_w_C_string = '\\ \\ Pct. Change in College Wage, $\\%\Delta(w_C)$ \n \t'
pct_chg_w_N_string = '\\ \\ Pct. Change in Non-college Wage, $\\%\Delta(w_N)$ \n \t'
pct_chg_cwp_string = '\\ \\ Pct. Change in College Wage Premium, \n \t'
delta_P_string = '\\ \\ Change in Employment Rate, $\Delta(P)$ \n \t'
delta_P_c_string = '\\ \\ Change in College Employment Rate, $\Delta(P_C)$ \n \t'
delta_P_n_string = '\\ \\ Change in Non-college Employment Rate, $\Delta(P_N)$ \n \t'
delta_employment_string = 'Change in Total Employment, $\Delta(L)$ \n \t'
delta_employment_C_string = '\\ \\ \\small Change in College Employment, $\Delta(L_C)$ \n \t'
delta_employment_N_string = '\\ \\ \\small Change in Non-college Employment, $\Delta(L_N)$ \n \t'
pct_chg_twb_string = 'Percent Change in Total Wage Bill, \n \t'
    
#Parameters to be varied:
CCFs = ['NA', 'NA']
alpha_params = [0, 0.75, 1, 1.25]

#Loop through CCFs
i = 0


tau_CCF=1.10*df_observed.loc[year, tau_baseline]

#Loop through alpha parameters
for alpha in alpha_params:
    i = i+1
    #Define Model
    model = calibration_model_CCF(alpha, alpha,
                    rho=rho_baseline,
                    tau=df_observed.loc[year, tau_baseline],
                    tau_CCF=tau_CCF,
                    elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                    w_c=df_observed.loc[year, 'wage1_c'], 
                    w_n=df_observed.loc[year, 'wage1_n'],
                    P_c=df_observed.loc[year, 'P1_c'], 
                    P_n=df_observed.loc[year, 'P1_n'],
                    share_workers_c=df_observed.loc[year, 'share_workers1_c'],
                    share_pop_c=df_observed.loc[year, 'share_pop_c'],
                    pop_count=df_observed.loc[year, 'pop_count'])
        
    #Make sure there are no NANs in model before calibration
    # Remove elasticities if specified to be common
    if model.elasticity_c == model.elasticity_n == 'common': 
        check = set(list(vars(model).keys())) - set(['elasticity_c', 'elasticity_n'])
    else: check = vars(model).keys()
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
    
    tau_string = tau_string + ampersand + f' \${model.tau_CCF-model.tau:,.0f} '
    
    delta_w_C_string = delta_w_C_string + ampersand + f' \${model.w_c_CCF-model.w_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' \${model.w_n_CCF-model.w_n:,.0f} '
    pct_chg_w_C_string = pct_chg_w_C_string + ampersand + f' {100*(model.w_c_CCF-model.w_c)/model.w_c:,.2f}\\% '
    pct_chg_w_N_string = pct_chg_w_N_string + ampersand + f' {100*(model.w_n_CCF-model.w_n)/model.w_n:,.2f}\\% '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
        f' {100*((model.w_c_CCF/model.w_n_CCF)-(model.w_c/model.w_n))/(model.w_c/model.w_n -1):,.2f}\\% '
    
    delta_P_string = delta_P_string + ampersand + f' {100*((model.L_c_CCF+model.L_n_CCF)-(model.L_c+model.L_n)):,.2f} pp '
    delta_P_n_string = delta_P_n_string + ampersand + f' {100*(model.P_n_CCF-model.P_n):,.2f} pp '
    delta_P_c_string = delta_P_c_string + ampersand + f' {100*(model.P_c_CCF-model.P_c):,.2f} pp '

    pct_chg_twb_string = pct_chg_twb_string + ampersand + \
        f' {100*((model.L_c_CCF*model.w_c_CCF + model.L_n_CCF*model.w_n_CCF)-(model.L_c*model.w_c + model.L_n*model.w_n))/(model.L_c*model.w_c + model.L_n*model.w_n):,.2f} \\%'
   
#%%      Output Latex Tables:      %%#

header = ['\\begin{tabular}{lcccccccc}', '\n',
          '\\FL', '\n',
          '\t &	 $\\alpha=0$','\n', 
          '\t &&	 $\\alpha=0.75$','\n', 
          '\t &&	 $\\alpha=1$','\n',
          '\t &&	 $\\alpha=1.25$', '\\\\','\n', 
          '\cmidrule{1-8}', '\n']

table_values=[tau_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wages:}', ' \\\\\n',
                delta_w_C_string, ' \\\\\n',
                delta_w_N_string, ' \\medskip \\\\\n',
                pct_chg_w_C_string, ' \\\\\n',
                pct_chg_w_N_string, ' \\medskip \\\\\n',
                pct_chg_cwp_string, ' \\\\\n',
                '\\ \\ $\\%\\Delta(w_C/w_N - 1)$', ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment Rate:}', ' \\\\\n',
                delta_P_string, ' \\\\\n',
                delta_P_c_string, ' \\\\\n',
                delta_P_n_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wage Bill:}', ' \\\\\n',
                pct_chg_twb_string,' \\\\\n',
                '\\ \\ $\\%\Delta({w_N L_N+w_C L_C})$', ' \\\\\n']

closer = ['\\bottomrule','\n', '\end{tabular}']

#Adjust dollar signs for negative values in the table
table_values = [x.replace('\\$-', '-\\$') for x in table_values]

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder_tables)
file = open(f"EqComparison_CCF_Cooper.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()