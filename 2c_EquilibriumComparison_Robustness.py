#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 14:39:40 2022
@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np

### Set working directory and folders
exec(open("__set_directory.py").read())

### Import calibration class
os.chdir(code_folder)
from fzz_calibration import calibration_model


#%%      Establishing Baseline:      %%#

# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)

# Parameter assumptions:
alpha_c=1
alpha_n=1
year = 2019

#Baseline Parameters
tau_baseline = 'tau_baseline'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]


#%%      Baseline Estimate      %%#
#Results for Overview Table
baselines_results_string = []

#Define Model
model = calibration_model(alpha_c, alpha_n,
                    rho=rho_baseline,
                    tau=df_observed.loc[year, tau_baseline],
                    elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                    w1_c=df_observed.loc[year, 'wage1_c'], 
                    w1_n=df_observed.loc[year, 'wage1_n'],
                    P1_c=df_observed.loc[year, 'P1_c'], 
                    P1_n=df_observed.loc[year, 'P1_n'],
                    share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
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

#Save Results for Overview
pct_chg_cwp = 100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1)
chg_w_C = (model.w2_c - model.w1_c)
pp_chg_P_C = 100*(model.P2_c - model.P1_c)
pp_chg_P_N = 100*(model.P2_n - model.P1_n)
chg_employment_N = model.employment2_n - model.employment1_n
baselines_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & \\${chg_w_C:,.0f}  & {pp_chg_P_C:,.2f} pp & {pp_chg_P_N:,.2f} pp & {chg_employment_N/1000:,.2f} & {100*((model.t)):,.2f}\\% \\\\ ')


#%%      Construct Results by Varying Labor Supply Elasticities      %%#

# String to save results
elasticity_results_string = []

# Parameter to be varied:
elasticity_values = [['common','common'], [0.15,0.15],[0.3,0.3],[0.45,0.45]]
elasticity2specification_Dict ={str(['common','common']):'Common $\kappa$',
                         str([0.15,0.15]): 'Low (0.15)',
                         str([0.3,0.3]): 'Medium (0.30)',
                         str([0.45,0.45]): 'High (0.45)'}

#Initialize strings for tables
column_header_string = '$(\epsilon^H_C, \epsilon^H_N)$ '
delta_w_C_string = '\\ \\ $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ $\Delta(w_N)$ \n \t'
pct_chg_cwp_string = '\\ \\ $\\%\\Delta(w_C/w_N - 1)$ \n \t'
delta_P_n_string = '\\ \\ $\Delta(P_N)$ \n \t'
delta_P_c_string = '\\ \\ $\Delta(P_C)$ \n \t'
delta_employment_string = '$\Delta$(\\small Total Employment): \n \t'
delta_employment_C_string = '\\ \\ \\small College \n \t'
delta_employment_N_string = '\\ \\ \\small Non-College \n \t'
delta_cwb_string = '$\\Delta$(\\small College Share): \n \t'


# Loop through elasticity pairs in calibration process
i = 0
for elasticity_value in elasticity_values:
    i = i+1
    e_c, e_n, = elasticity_value[0], elasticity_value[1]
    label = elasticity2specification_Dict[str(elasticity_value)]
    
    #Define and calibrate model
    model = calibration_model(alpha_c, alpha_n,
                rho=rho_baseline,
                tau=df_observed.loc[year, tau_baseline],
                elasticity_c=e_c, elasticity_n=e_n,
                w1_c=df_observed.loc[year, 'wage1_c'], 
                w1_n=df_observed.loc[year, 'wage1_n'],
                P1_c=df_observed.loc[year, 'P1_c'], 
                P1_n=df_observed.loc[year, 'P1_n'],
                share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year, 'share_pop_c'],
                pop_count=df_observed.loc[year, 'pop_count'])
    
    #Make sure there are no NANs in model before calibration
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

    #Save Results
    pct_chg_cwp = 100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1)
    chg_w_C = (model.w2_c - model.w1_c)
    pp_chg_P_C = 100*(model.P2_c - model.P1_c)
    pp_chg_P_N = 100*(model.P2_n - model.P1_n)
    chg_employment_N = model.employment2_n - model.employment1_n
    elasticity_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & \\${chg_w_C:,.0f}  & {pp_chg_P_C:,.2f} pp & {pp_chg_P_N:,.2f} pp & {chg_employment_N/1000:,.2f} & {100*((model.t)):,.2f}\\% \\\\ ')

    #Add values to strings for Eq Comparison Tables
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
        
    column_header_string = column_header_string + ampersand + f'\t \\small {label} \n '
    
    delta_w_C_string = delta_w_C_string + ampersand + f' {model.w2_c-model.w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' {model.w2_n-model.w1_n:,.0f} '
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
    
header = [f'\ctable[caption={{Equilibrium Comparison Across Elasticity Assumptions}},', '\n',
          '    label={EqComparison_AcrossElasticity}, pos=h!]', '\n',
          '{lccccccc}{}{\\FL', '\n',
          column_header_string, '\\\\',
          '\cmidrule{1-8}', '\n']            


#%%      Construct Results by Varying Substitutabilitity      %%#

# String to save results
rho_results_string = []

# Parameter to be varied:
rho_values = [1, 0.3827, 0.01]
rho2specification_Dict ={str(1):'Perfect Substitutes',
                         str(0.3827): 'Gross Substitutes',
                         str(0.01): 'Cobb-Douglas'}

#Initialize strings for tables
column_header_string = ''
delta_w_C_string = '\\ \\ $\Delta(w_C)$ \n \t'
delta_w_N_string = '\\ \\ $\Delta(w_N)$ \n \t'
pct_chg_cwp_string = '\\ \\ $\\%\\Delta(w_C/w_N - 1)$ \n \t'
delta_P_n_string = '\\ \\ $\Delta(P_N)$ \n \t'
delta_P_c_string = '\\ \\ $\Delta(P_C)$ \n \t'
delta_employment_string = '$\Delta$(\\small Total Employment): \n \t'
delta_employment_C_string = '\\ \\ \\small College \n \t'
delta_employment_N_string = '\\ \\ \\small Non-College \n \t'
delta_cwb_string = '$\\Delta$(\\small College Share): \n \t'


# Loop through rho values in calibration process
i = 0
for rho_value in rho_values:
    i = i+1
    label = rho2specification_Dict[str(rho_value)]
    
    #Define and calibrate model    
    model = calibration_model(alpha_c, alpha_n,
                rho=rho_value,
                tau=df_observed.loc[year, tau_baseline],
                elasticity_c=e_c_baseline, elasticity_n=e_n_baseline,
                w1_c=df_observed.loc[year, 'wage1_c'], 
                w1_n=df_observed.loc[year, 'wage1_n'],
                P1_c=df_observed.loc[year, 'P1_c'], 
                P1_n=df_observed.loc[year, 'P1_n'],
                share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                share_pop_c=df_observed.loc[year, 'share_pop_c'],
                pop_count=df_observed.loc[year, 'pop_count'])
    
    #Make sure there are no NANs in model before calibration
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
    
    #Save Results
    pct_chg_cwp = 100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1)
    chg_w_C = (model.w2_c - model.w1_c)
    pp_chg_P_C = 100*(model.P2_c - model.P1_c)
    pp_chg_P_N = 100*(model.P2_n - model.P1_n)
    chg_employment_N = model.employment2_n - model.employment1_n
    rho_results_string.append(f' \t & {pct_chg_cwp:,.2f}\\% & \\${chg_w_C:,.0f}  & {pp_chg_P_C:,.2f} pp & {pp_chg_P_N:,.2f} pp & {chg_employment_N/1000:,.2f} & {100*((model.t)):,.2f}\\% \\\\ ')
    
    #Add values to strings for Eq Comparison Tables
    if i ==1: ampersand = '&'
    if i > 1: ampersand = ' &&'
        
    column_header_string = column_header_string + ampersand + f'\t \\small {label} \n '
    
    delta_w_C_string = delta_w_C_string + ampersand + f' {model.w2_c-model.w1_c:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' {model.w2_n-model.w1_n:,.0f} '
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
header = ['\\begin{tabular}{lcccccc}', ' \n',
            '\\FL', '\n',
            '\t &    \multicolumn{1}{p{2.4cm}}{\\footnotesize \centering Percent Change \\\\ in College \\\\ Wage Premium}', ' \n',
            '\t &	 \multicolumn{1}{p{2.0cm}}{\\footnotesize \centering Change in \\\\ Non-college Wages \\\\ $\Delta(w_N)$}', '\n',
            '\t &	 \multicolumn{1}{p{2.0cm}}{\\footnotesize \centering Change in \\\\ College Employment \\\\ Rate \\\\ $\Delta(P_C)$}', '\n',
            '\t &	 \multicolumn{1}{p{2.0cm}}{\\footnotesize \centering Change in \\\\ Non-College Employment \\\\ Rate \\\\ $\Delta(P_C)$}', '\n',
            '\t &	 \multicolumn{1}{p{2.0cm}}{\\footnotesize \centering Change in \\\\ Non-College \\\\ Employment (Thous.) \\\\ $\Delta(L_N)$}', '\n',
            '\t &	 \multicolumn{1}{p{2.0cm}}{\\footnotesize \centering Payroll \\\\ Tax Rate \\\\ $t$}', '\\\\', '\n',
            '\cmidrule{1-7}', '\n',
            '\\\\' '\n']  

## LaTeX code for table results
# Baseline section
baseline = [r'\underline{Baseline:}', ' \n', 
          baselines_results_string[0], ' \n',
          '\\\\', ' \n'] 
# Elasticity section
acrossElasticity = [r'\underline{Labor Supply Elasticities:} \\', ' \n',
    '\ \small{Derived Group-Specific Elasticities:} \\\\', ' \n ',
    '\ \ \ \small{$\epsilon_C=0.42$ and $\epsilon_N=0.28$ (Baseline)}', 
    '\n', elasticity_results_string[0], ' \n',
    '\ \small{Assumed Common Elasticities:} \\\\', ' \n',
    '\ \ \ \small{$\epsilon_C=\epsilon_N=0.15$}', 
    '\n', elasticity_results_string[1], ' \n',
    '\ \ \ \small{$\epsilon_C=\epsilon_N=0.30$}', 
    '\n', elasticity_results_string[2], ' \n',
    '\ \ \ \small{$\epsilon_C=\epsilon_N=0.45$}',
    '\n', elasticity_results_string[3], ' \n',
    '\\\\', ' \n'] 
# Substitutability section
acrossRho = [r'\underline{Substitutability ($\rho$)} \\', ' \n',
    '\ \ \small{Perfect Substitutes ($\\rho=1$)}', 
    ' \n', rho_results_string[0], ' \n',
    '\ \ \small{Gross Substitutes ($\\rho=0.38$, Baseline)}', 
    '\n', rho_results_string[1], ' \n',
    '\ \ \small{Cobb-Douglas ($\\rho=0$)}', 
    ' \n', rho_results_string[2], ' \n',
    '\\\\', ' \n'] 
# Concatenate table values
table_values = baseline + acrossElasticity + acrossRho 

## LaTeX code for closer
closer = ['\\bottomrule','\n', '\end{tabular}']

## Adjust dollar signs for negative values in the table
table_values = [x.replace('\\$-', '-\\$') for x in table_values]

## Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder)
file = open("EquilibriumComparison_Robustness.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer) 
file.close()