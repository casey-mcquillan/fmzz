#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 20:33:56 2022

@author: caseymcquillan
"""
#%%  Preamble: Import packages, set directory #%%  
### Import Packages
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")

### Set working directory and folders
code_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/code"
data_folder = "/Users/caseymcquillan/Desktop/Research/FZZ/data"
output_path = '/Users/caseymcquillan/Desktop/Research/FZZ/output/Tables/RC4_zwick'

### Import calibration class
os.chdir(code_folder)

#from fzz_calibration import calibration_model 
from fzz_calibration_RC4_zwick import calibration_model_RC4 


#%% Generating Tables that Vary Elasticties  Across Substitutability #%% 
# Importing Data
os.chdir(data_folder)
df_observed = pd.read_csv('observed_data.csv', index_col=0)

# Parameter assumptions:
alpha_c=1
alpha_n=1
tau_param = 'tau_high'
year = 2019

# Parameter to be varied:
rho_values = [1, 0.3827, 0.01]


# Loop through rho values in calibration process
i = 0
for rho_value in rho_values:
    i = i+1
        
    #Initialize strings for tables
    column_header_string = '$(\epsilon^H_C, \epsilon^H_N)$ '
    delta_w_C_string = '\\ \\ $\Delta(w_C)$ \n \t'
    delta_w_N_string = '\\ \\ $\Delta(w_N)$ \n \t'
    delta_cwp_string = '\\ \\ $\Delta(w_C - w_N)$ \n \t'
    pct_chg_cwp_string = '\\ \\ $\\%\\Delta(w_C - w_N)$ \n \t'
    pct_chg_L_string = '\\ \\ $\\%\\Delta(L_C+L_N)$ \n \t'
    pct_chg_L_C_string = '\\ \\ $\\%\\Delta(L_C)$ \n \t'
    pct_chg_L_B_string = '\\ \\ $\\%\\Delta(L_N)$ \n \t'
    delta_employmentShare_C_string = '$\Delta$(\\small College Share): \n \t'
    delta_employment_string = '$\Delta$(\\small Total Employment): \n \t'
    delta_employment_C_string = '\\ \\ \\small College \n \t'
    delta_employment_N_string = '\\ \\ \\small Non-College \n \t'
    delta_cwb_string = '$\\Delta$(\\small College Share): \n \t'
    
    # Parameter assumptions:
    alpha_c=1
    alpha_n=1
    tau_param = 'tau_high'
    year = 2019
    
    # Parameter to be varied:
    elasticity_values = [['common','common'], [0.15,0.15],[0.3,0.3],[0.45,0.45]]
    
    # Loop through elasticity pairs in calibration process
    j = 0
    for elasticity_value in elasticity_values:
        j = j+1
        e_c, e_n, = elasticity_value[0], elasticity_value[1]
        
        #Define and calibrate model
        model = calibration_model_RC4(alpha_c, alpha_n,
                    rho=rho_value,
                    tau=df_observed.loc[year, tau_param],
                    elasticity_c=e_c, elasticity_n=e_n,
                    w1_c=df_observed.loc[year, 'wage1_c'], 
                    w1_n=df_observed.loc[year, 'wage1_n'],
                    P1_c=df_observed.loc[year, 'P1_c'], 
                    P1_n=df_observed.loc[year, 'P1_n'],
                    share_workers1_c=df_observed.loc[year, 'share_workers1_c'],
                    share_pop_c=df_observed.loc[year, 'share_pop_c'],
                    pop_count=df_observed.loc[year, 'pop_count'])
        
        #Make sure there are no NANs in model before calibration
        # Remove elasticities if specified to be common
        if elasticity_value == ['common','common']: 
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
        
        #Output Summary tables
        model.generate_table(file_name='SummaryTable'+str(year)+f"_RC4_rho{i}_epsilon{j}", year=year, 
                         table_type="equilibrium summary",
                         table_label="SummaryTable"+str(year)+f"_RC4_rho{i}_epsilon{j}", 
                         location=output_path, 
                         subtitle=f" with $\rho = {rho_value}, \epsilon^H_C = {elasticity_value[0]},\epsilon^H_N={elasticity_value[1]}$")
    
        #Add values to strings for Eq Comparison Tables
        if j ==1: ampersand = '&'
        if j > 1: ampersand = ' &&'
            
        column_header_string = column_header_string + ampersand + f'\t \\small {str(elasticity_value)} \n '
        
        delta_w_C_string = delta_w_C_string + ampersand + f' {model.w2_c-model.w1_c:,.0f} '
        delta_w_N_string = delta_w_N_string + ampersand + f' {model.w2_n-model.w1_n:,.0f} '
        delta_cwp_string = delta_cwp_string + ampersand + f' {(model.w2_c-model.w2_n)-(model.w1_c-model.w1_n):,.0f} '
        pct_chg_cwp_string = pct_chg_cwp_string + ampersand + \
            f' {100*((model.w2_c-model.w2_n)-(model.w1_c-model.w1_n))/(model.w1_c-model.w1_n):,.2f}\\% '
        
        pct_chg_L_string = pct_chg_L_string + ampersand +  \
            f' {100*((model.L2_c+model.L2_n)-(model.L1_c+model.L1_n))/(model.L1_c+model.L1_n):,.2f}\\% '
        pct_chg_L_C_string = pct_chg_L_C_string + ampersand + \
            f' {100*((model.L2_c)-(model.L1_c))/(model.L1_c):,.2f}\\% '
        pct_chg_L_B_string = pct_chg_L_B_string + ampersand + \
            f' {100*((model.L2_n)-(model.L1_n))/(model.L1_n):,.2f}\\% '
        
        delta_employmentShare_C_string = delta_employmentShare_C_string + ampersand + \
            f' {100*(((model.L2_c)/(model.L2_c+model.L2_n))-((model.L1_c)/(model.L1_c+model.L1_n))):,.2f} pp '
        delta_employment_string = delta_employment_string + ampersand + \
            f' {(model.employment2_c+model.employment2_n)-(model.employment1_c+model.employment1_n):,.0f} '
        delta_employment_C_string = delta_employment_C_string + ampersand + \
            f' {(model.employment2_c)-(model.employment1_c):,.0f} '
        delta_employment_N_string = delta_employment_N_string + ampersand + \
            f' {(model.employment2_n)-(model.employment1_n):,.0f} '
        
        delta_cwb_string = delta_cwb_string + ampersand + \
            f' {100*(((model.L2_c*model.w2_c)/(model.L2_c*model.w2_c + model.L2_n*model.w2_n))-((model.L1_c*model.w1_c)/(model.L1_c*model.w1_c + model.L1_n*model.w1_n))):,.2f} pp'
        
    
    header = [f'\ctable[caption={{Equilibrium Comparison for {year} Across Elasticities with $\\rho = {rho_value}$ }},', '\n',
              '    label={EqComparison_AcrossElasticity_rho{i}}, pos=h!]', '\n',
              '{lccccccc}{}{\\FL', '\n',
              column_header_string, '\\\\',
              '\cmidrule{1-8}', '\n']            
    
    table_values=['\\underline{Wages:}', ' \\\\\n',
                    delta_w_C_string, ' \\\\\n',
                    delta_w_N_string, ' \\\\\n',
                    delta_cwp_string, ' \\\\\n',
                    pct_chg_cwp_string, ' \\\\\n',
                    '\\\\\n',
                    '\\underline{Labor Supply:}', ' \\\\\n',
                    pct_chg_L_string, ' \\\\\n',
                    pct_chg_L_C_string, ' \\\\\n',
                    pct_chg_L_B_string, ' \\\\\n',
                    '\\\\\n',
                    '\\underline{Employment:}', ' \\\\\n',
                    delta_employmentShare_C_string, ' \\\\\n',
                    delta_employment_string, ' \\\\\n',
                    delta_employment_C_string, ' \\\\\n',
                    delta_employment_N_string, ' \\\\\n',
                    '\\\\\n',
                    '\\underline{Wage Bill:}', ' \\\\\n',
                    delta_cwb_string,' \\\\\n']
    
    closer = ['\\bottomrule}']
    
    #Create, write, and close file
    cwd = os.getcwd()
    os.chdir(output_path)
    file = open(f'EqComparison_AcrossElasticity_rho{i}.tex',"w")
    file.writelines(header) 
    file.writelines(table_values)   
    file.writelines(closer)   
    file.close()
