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
## Import function to define project folder
from __fmzz import project_folder_plus

## Define project directory folders
main_folder = project_folder_plus('')
code_folder = project_folder_plus("/code")
data_folder = project_folder_plus("/data")
output_folder = project_folder_plus("/output/Tables/")
appendix_output_folder = project_folder_plus("/output/Tables/Appendix")

### Import calibration class
os.chdir(code_folder)
from fzz_calibration import calibration_model 
from fzz_calibration_bySex import calibration_model_bySex


#%%      Establishing Baseline:      %%#

# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data_bySex.csv', index_col=0)

# Parameter assumptions:
year = 2019
tau_baseline = 'tau_baseline'
rho_baseline = 0.3827
elasticity_baseline = ['common', 'common']
e_c_baseline, e_n_baseline = elasticity_baseline[0], elasticity_baseline[1]


#%%      Results by Sex:      %%#

### Initialize strings for tables
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


# Results for Baseline Model
model = calibration_model(alpha_c=1, alpha_n=1,
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
    
# Make sure there are no NANs in model before calibration
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

# Calibrate Model
model.calibrate()

# Add values to strings
ampersand = '&'

#Calculate Changes
chg_w_C = model.w2_c-model.w1_c
chg_w_N = model.w2_n-model.w1_n
chg_cwp = 100*((model.w2_c/model.w2_n)-(model.w1_c/model.w1_n))/(model.w1_c/model.w1_n -1)

chg_P_C=100*(model.P2_c-model.P1_c)
chg_P_N=100*(model.P2_n-model.P1_n)
chg_employment_C = model.employment2_c-model.employment1_c
chg_employment_N = model.employment2_n-model.employment1_n
chg_employment = chg_employment_C+chg_employment_N

chg_cwb = 100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))
              -((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n)))

# Add to strings
ampersand = '&'
tau_string = tau_string + ampersand + f' \${model.tau:,.0f} '
payroll_tax_string = payroll_tax_string + ampersand + f' {100*((model.t)):,.2f}\\% '

delta_w_C_string = delta_w_C_string + ampersand + f' \${chg_w_C:,.0f} '
delta_w_N_string = delta_w_N_string + ampersand + f' \${chg_w_N:,.0f} '
pct_chg_cwp_string = pct_chg_cwp_string + ampersand + f' {chg_cwp:,.2f}\\% '

delta_P_c_string = delta_P_c_string + ampersand + f' {chg_P_C:,.2f} pp '
delta_P_n_string = delta_P_n_string + ampersand + f' {chg_P_N:,.2f} pp '
delta_employment_string = delta_employment_string + ampersand + f' {chg_employment:,.0f} '
delta_employment_C_string = delta_employment_C_string + ampersand + f' {chg_employment_C:,.0f} '
delta_employment_N_string = delta_employment_N_string + ampersand + f' {chg_employment_N:,.0f} '

delta_cwb_string = delta_cwb_string + ampersand + f' {chg_cwb:,.2f} pp'



### Results for Aggregated Model
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

# Calibrate Model
model.calibrate()

# Add values to strings for aggregate
#Calculate Changes
chg_w_C = model.avg_w2_c-model.avg_w1_c
chg_w_N = model.avg_w2_n-model.avg_w1_n
chg_cwp = 100*((model.avg_w2_c/model.avg_w2_n)-(model.avg_w1_c/model.avg_w1_n))/(model.avg_w1_c/model.avg_w1_n -1)

chg_P_C=100*(model.avg_P2_c-model.avg_P1_c)
chg_P_N=100*(model.avg_P2_n-model.avg_P1_n)
chg_employment_C = ((model.employment2_c_m+model.employment2_c_f)-(model.employment1_c_m+model.employment1_c_f))
chg_employment_N = ((model.employment2_n_m+model.employment2_n_f)-(model.employment1_n_m+model.employment1_n_f))
chg_employment = chg_employment_C+chg_employment_N

chg_cwb = 100*((((model.L2_c_m+model.L2_c_f)*model.avg_w2_c)/\
                ((model.L2_c_m+model.L2_c_f)*model.avg_w2_c \
                 + (model.L2_n_m+model.L2_n_f)*model.avg_w2_n))\
               -(((model.L1_c_m+model.L1_c_f)*model.avg_w1_c)/\
                 ((model.L1_c_m+model.L1_c_f)*model.avg_w1_c \
                  + (model.L1_n_m+model.L1_n_f)*model.avg_w1_n)))

# Add to strings
ampersand = '&&'
tau_string = tau_string + ampersand + f' \${model.tau:,.0f} '
payroll_tax_string = payroll_tax_string + ampersand + f' {100*((model.t)):,.2f}\\% '

delta_w_C_string = delta_w_C_string + ampersand + f' \${chg_w_C:,.0f} '
delta_w_N_string = delta_w_N_string + ampersand + f' \${chg_w_N:,.0f} '
pct_chg_cwp_string = pct_chg_cwp_string + ampersand + f' {chg_cwp:,.2f}\\% '

delta_P_c_string = delta_P_c_string + ampersand + f' {chg_P_C:,.2f} pp '
delta_P_n_string = delta_P_n_string + ampersand + f' {chg_P_N:,.2f} pp '
delta_employment_string = delta_employment_string + ampersand + f' {chg_employment:,.0f} '
delta_employment_C_string = delta_employment_C_string + ampersand + f' {chg_employment_C:,.0f} '
delta_employment_N_string = delta_employment_N_string + ampersand + f' {chg_employment_N:,.0f} '

delta_cwb_string = delta_cwb_string + ampersand + f' {chg_cwb:,.2f} pp'



### Results for Each Sex
for _sex in ['_m', '_f']:

    #Add values to strings for Eq Comparison Tables
    ampersand = ' &&'
    
    #Calculate Changes
    exec(f'chg_w_C = model.w2_c{_sex}-model.w1_c{_sex}')
    exec(f'chg_w_N = model.w2_n{_sex}-model.w1_n{_sex}')
    exec(f'chg_P_C=100*(model.P2_c{_sex}-model.P1_c{_sex})')
    exec(f'chg_P_N=100*(model.P2_n{_sex}-model.P1_n{_sex})')
    exec(f'chg_employment_C=model.employment2_c{_sex}-model.employment1_c{_sex}')
    exec(f'chg_employment_N=model.employment2_n{_sex}-model.employment1_n{_sex}')
    chg_employment = chg_employment_C+chg_employment_N
   
    #Add to strings
    tau_string = tau_string + ampersand + f' -  '
    payroll_tax_string = payroll_tax_string + ampersand + f' - '
    
    delta_w_C_string = delta_w_C_string + ampersand + f' \${chg_w_C:,.0f} '
    delta_w_N_string = delta_w_N_string + ampersand + f' \${chg_w_N:,.0f} '
    pct_chg_cwp_string = pct_chg_cwp_string + ampersand + f' - '
    
    delta_P_c_string = delta_P_c_string + ampersand + f' {chg_P_C:,.2f} pp '
    delta_P_n_string = delta_P_n_string + ampersand + f' {chg_P_N:,.2f} pp '
    delta_employment_string = delta_employment_string + ampersand + f' {chg_employment:,.0f} '
    delta_employment_C_string = delta_employment_C_string + ampersand + f' {chg_employment_C:,.0f} '
    delta_employment_N_string = delta_employment_N_string + ampersand + f' {chg_employment_N:,.0f} '
    
    delta_cwb_string = delta_cwb_string + ampersand + f' - '


### Output Table
header = ['\\begin{tabular}{lcccccccc}', '\n',
          '\\FL', '\n',
          '\t &	 \multicolumn{1}{p{2.7cm}}{\small \centering Baseline}','\n',
          '\t &&	 \multicolumn{1}{p{2.7cm}}{\small \centering Aggregate}','\n',
          '\t &&	 \multicolumn{1}{p{2.7cm}}{\small \centering Male}','\n',
          '\t &&	 \multicolumn{1}{p{2.7cm}}{\small \centering Female}','\\\\','\n', 
          '\cmidrule{1-8}', '\n']

table_values=[tau_string, ' \\\\\n',
                '\\\\\n',
                payroll_tax_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wages:}', ' \\\\\n',
                delta_w_C_string, ' \\\\\n',
                delta_w_N_string, ' \\\\\n',
                pct_chg_cwp_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Employment Rate:}', ' \\\\\n',
                delta_P_c_string, ' \\\\\n',
                delta_P_n_string, ' \\\\\n',
                delta_employment_string, ' \\\\\n',
                delta_employment_C_string, ' \\\\\n',
                delta_employment_N_string, ' \\\\\n',
                '\\\\\n',
                '\\underline{Wage Bill:}', ' \\\\\n',
                delta_cwb_string,' \\\\\n']

closer = ['\\bottomrule','\n', '\end{tabular}']

#Adjust dollar signs for negative values in the table
table_values = [x.replace('\\$-', '-\\$') for x in table_values]

#Create, write, and close file
cwd = os.getcwd()
os.chdir(output_folder)
file = open("RC2_EquilibriumComparison_bySex.tex","w")
file.writelines(header) 
file.writelines(table_values)   
file.writelines(closer)   
file.close()
